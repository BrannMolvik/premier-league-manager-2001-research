import unittest
from dataclasses import dataclass, FrozenInstanceError
from datetime import date, timedelta

from match_events import (
    ChanceRecord,
    ChanceSource,
    FinishMode,
    IncidentKind,
    IncidentRecord,
    SubstitutionRecord,
)
from match_postmatch import (
    FormTransitionSettings,
    MoraleSettings,
    PlayerTransferRequest,
    apply_player_transfer_request_response,
    apply_signed_contract_finalizer_morale,
    decrease_player_morale,
    increase_player_morale,
    appeared_player_indices,
    apply_league_match_discipline,
    persist_match_performance_and_fastview_form_histories,
    persist_match_performance_history,
    finalize_match_participant_statistics,
    FinalizedParticipantStatistics,
    FinalizedSideParticipantStatistics,
    persist_post_match_form,
    persist_post_match_side,
    persist_premier_league_discipline,
    persist_premier_league_match_incidents,
    persist_premier_league_morale_and_form,
    maybe_queue_player_transfer_request,
    refresh_league_suspension_for_next_fixture,
    sync_post_match_conditions,
    serve_league_suspension_after_fixture,
    update_post_match_form,
)
from match_simulation import (
    NormalMatchResult,
    PreparedMatchPlayer,
    RawPlayerConditionHistory,
    PreparedMatchSide,
    TimedMatchEvent,
)
from match_strength import TeamStrengthContext


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError(f"{value} outside RNG({bound})")
        return value


@dataclass
class RuntimePlayer:
    index: int = 0
    morale: int = 50
    date_of_birth: date | None = date(1980, 1, 1)
    current_raw: tuple[int, ...] = (20,) * 17
    condition: int = 80
    form_state: int = 2
    injured: bool = False
    suspended: bool = False
    discipline_yellow_total: int = 0
    discipline_yellow_cycle: int = 0
    suspension_matches_remaining: int = 0
    suspension_effective_date: date | None = None
    selection_excluded: bool = False
    injury_return_date: date | None = None
    injury_source_mode: int | None = None
    injury_severity_code: int | None = None
    injury_history_weight: int = 0
    match_performance_history: list[int] = None
    match_performance_history_count: int = 0
    match_performance_history_write_index: int = 0
    contract_renewal_suggestion_pending: bool = True
    transfer_listed: bool = False
    loan_club_id: int | None = None
    wanted: bool = False

    @property
    def selling_squad_count_excluded(self) -> bool:
        return bool(
            self.transfer_listed
            or self.injured
            or self.loan_club_id is not None
            or self.suspended
        )

    def __post_init__(self):
        if self.match_performance_history is None:
            self.match_performance_history = [0] * 6

    def age(self, on_date):
        if self.date_of_birth is None:
            return None
        return on_date.year - self.date_of_birth.year - (
            (on_date.month, on_date.day)
            < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def latest_match_performance(self):
        if self.match_performance_history_count <= 0:
            return 0
        return self.match_performance_history[
            (self.match_performance_history_write_index - 1) % 6
        ]

    def append_match_performance(self, value):
        index = self.match_performance_history_write_index
        self.match_performance_history[index] = int(value) & 0xFF
        self.match_performance_history_count = min(
            6, self.match_performance_history_count + 1
        )
        self.match_performance_history_write_index = (index + 1) % 6
        return int(value)


def prepared_player(index, *, active=True, bench=False, condition=80):
    return PreparedMatchPlayer(
        side=0,
        player_index=index,
        condition=condition,
        form_state=2,
        current_position=12,
        balance_position_code=10,
        preferred_positions=(12, 0, 0),
        skills=(100,) * 17,
        active=active,
        substitution_available=bench,
    )


def prepared_side():
    context = TeamStrengthContext(
        tactic_style=0,
        match_bias=2,
        user_controlled=False,
        aggression=5,
    )
    return PreparedMatchSide(
        players=(
            prepared_player(0, condition=74),
            prepared_player(1, condition=73),
            prepared_player(2, active=False, bench=True, condition=79),
            prepared_player(3, active=False, bench=True, condition=80),
        ),
        attack_context=context,
        defence_context=context,
        penalty_taker_priority=(),
        corner_taker_priority=(),
        free_kick_taker_priority=(),
        starting_player_indices=(0, 1),
    )


class MoraleTransitionTests(unittest.TestCase):
    def test_shipped_settings_match_original_tuning_bytes(self):
        self.assertEqual(
            MoraleSettings(),
            MoraleSettings(
                good_leadership=25,
                lost_match=7,
                won_match=10,
                not_played=8,
                maximum=100,
                loan=10,
                signed_new_contract=30,
            ),
        )

    def test_decrease_uses_leadership_age_and_one_rng2(self):
        low = ScriptedRng([1])
        high = ScriptedRng([1])
        self.assertEqual(decrease_player_morale(80, 7, 20, 20, low), 74)
        self.assertEqual(decrease_player_morale(80, 7, 20, 30, high), 76)
        self.assertEqual(low.calls, [2])
        self.assertEqual(high.calls, [2])

    def test_increase_uses_leadership_age_and_caps_at_maximum(self):
        low = ScriptedRng([1])
        high = ScriptedRng([1])
        # 0x41BB10 adds an explicit final +1 after the base amount,
        # RNG(2), leadership, and age modifiers.
        self.assertEqual(increase_player_morale(80, 10, 20, 20, low), 93)
        self.assertEqual(increase_player_morale(80, 10, 20, 30, high), 95)
        self.assertEqual(
            increase_player_morale(99, 10, 20, 30, ScriptedRng([0])),
            100,
        )

    def test_signed_contract_finalizer_draw_precedes_latch_clear(self):
        player = RuntimePlayer(contract_renewal_suggestion_pending=True)

        class ObservingRng:
            def __init__(self):
                self.calls = []

            def randbelow(self, bound):
                self.calls.append(int(bound))
                self.assert_latch()
                return 0

            def assert_latch(self):
                if not player.contract_renewal_suggestion_pending:
                    raise AssertionError("0x164 latch cleared before morale RNG(2)")

        rng = ObservingRng()
        result = apply_signed_contract_finalizer_morale(
            player,
            date(2000, 7, 1),
            rng,
        )

        self.assertEqual(result, 82)
        self.assertEqual(player.morale, 82)
        self.assertFalse(player.contract_renewal_suggestion_pending)
        self.assertEqual(rng.calls, [2])

    def test_roster_pass_interleaves_morale_form_and_not_played_rng(self):
        side = prepared_side()
        result = NormalMatchResult(
            events=(
                TimedMatchEvent(
                    10,
                    ChanceRecord(
                        ChanceSource.OPEN_PLAY,
                        0,
                        0,
                        0,
                        finish_mode=FinishMode.SHOOTING,
                    ),
                ),
            )
        )
        participants = [
            RuntimePlayer(index=10),
            RuntimePlayer(index=11),
            RuntimePlayer(index=12),
            RuntimePlayer(index=13),
        ]
        unavailable = RuntimePlayer(index=15, injured=True)
        roster = (
            participants[0],
            RuntimePlayer(index=14),
            participants[1],
            unavailable,
        )
        rng = ScriptedRng([0, 99, 0, 1, 1, 99])

        appeared = persist_premier_league_morale_and_form(
            roster,
            side,
            participants,
            result,
            date(2000, 7, 1),
            rng,
        )

        self.assertEqual(appeared, frozenset((10, 11)))
        self.assertEqual([player.morale for player in roster], [62, 43, 63, 50])
        self.assertEqual([player.form_state for player in roster], [2, 2, 2, 2])
        self.assertEqual(rng.calls, [2, 100, 10, 2, 2, 100])


    def test_danger_morale_trigger_queues_next_day_mail(self):
        player = RuntimePlayer(index=77, morale=14)
        rng = ScriptedRng([2])
        queued = []

        self.assertTrue(
            maybe_queue_player_transfer_request(
                player,
                date(2000, 8, 20),
                rng,
                club_user_controlled=True,
                active_club_user_controlled=True,
                request_sink=queued.append,
            )
        )

        self.assertEqual(rng.calls, [30])
        self.assertEqual(
            queued,
            [
                PlayerTransferRequest(
                    player_id=77,
                    queued_on=date(2000, 8, 20),
                    due_on=date(2000, 8, 21),
                )
            ],
        )

    def test_danger_morale_status_gate_is_after_rng30(self):
        player = RuntimePlayer(index=77, morale=14, transfer_listed=True)
        rng = ScriptedRng([2])
        queued = []

        self.assertFalse(
            maybe_queue_player_transfer_request(
                player,
                date(2000, 8, 20),
                rng,
                club_user_controlled=True,
                active_club_user_controlled=True,
                request_sink=queued.append,
            )
        )
        self.assertEqual(rng.calls, [30])
        self.assertEqual(queued, [])

        player.transfer_listed = False
        player.wanted = True
        rng = ScriptedRng([2])
        self.assertFalse(
            maybe_queue_player_transfer_request(
                player,
                date(2000, 8, 20),
                rng,
                club_user_controlled=True,
                active_club_user_controlled=True,
                request_sink=queued.append,
            )
        )
        self.assertEqual(rng.calls, [30])

    def test_danger_morale_draw_follows_same_player_form_draw(self):
        side = prepared_side()
        participants = [
            RuntimePlayer(index=10, morale=14),
            RuntimePlayer(index=11, morale=50),
            RuntimePlayer(index=12, morale=50),
            RuntimePlayer(index=13, morale=50),
        ]
        roster = (participants[0],)
        rng = ScriptedRng([99, 2])
        queued = []

        persist_premier_league_morale_and_form(
            roster,
            side,
            participants,
            NormalMatchResult(events=()),
            date(2000, 8, 20),
            rng,
            club_user_controlled=True,
            active_club_user_controlled=lambda player: True,
            transfer_request_sink=queued.append,
        )

        self.assertEqual(rng.calls, [100, 30])
        self.assertEqual([value.player_id for value in queued], [10])

    def test_transfer_request_response_accept_sets_status_refuse_does_not(self):
        accepted = RuntimePlayer(index=1, morale=10)
        refused = RuntimePlayer(index=2, morale=10)

        apply_player_transfer_request_response(accepted, accept=True)
        apply_player_transfer_request_response(refused, accept=False)

        self.assertTrue(accepted.transfer_listed)
        self.assertTrue(accepted.wanted)
        self.assertFalse(refused.transfer_listed)
        self.assertFalse(refused.wanted)


class FormTransitionTests(unittest.TestCase):
    def test_failed_trigger_consumes_only_one_rng_draw(self):
        rng = ScriptedRng([5])
        self.assertEqual(update_post_match_form(2, rng), 2)
        self.assertEqual(rng.calls, [100])

    def test_neutral_form_can_increase_or_decrease(self):
        self.assertEqual(
            update_post_match_form(2, ScriptedRng([0, 49])),
            3,
        )
        self.assertEqual(
            update_post_match_form(2, ScriptedRng([0, 50])),
            1,
        )

    def test_out_of_form_and_in_form_use_their_exact_trigger_probabilities(self):
        settings = FormTransitionSettings(
            form_change_prob=5,
            in_form_change_prob=20,
            out_of_form_change_prob=20,
            form_increase_prob=50,
        )
        self.assertEqual(
            update_post_match_form(1, ScriptedRng([19, 0]), settings),
            2,
        )
        self.assertEqual(
            update_post_match_form(1, ScriptedRng([20]), settings),
            1,
        )
        self.assertEqual(
            update_post_match_form(3, ScriptedRng([19, 99]), settings),
            2,
        )
        self.assertEqual(
            update_post_match_form(3, ScriptedRng([20]), settings),
            3,
        )

    def test_boundary_states_clamp_exactly(self):
        self.assertEqual(update_post_match_form(0, ScriptedRng([0, 99])), 0)
        self.assertEqual(update_post_match_form(4, ScriptedRng([0, 0])), 4)
        self.assertEqual(update_post_match_form(0, ScriptedRng([0, 0])), 1)
        self.assertEqual(update_post_match_form(4, ScriptedRng([0, 99])), 3)


class LeagueSuspensionTests(unittest.TestCase):
    def test_fifth_yellow_creates_one_match_ban_effective_in_seven_days(self):
        player = RuntimePlayer(
            discipline_yellow_total=4,
            discipline_yellow_cycle=4,
        )
        fixture_date = date(2000, 8, 19)

        apply_league_match_discipline(
            player,
            bookings=1,
            dismissals=0,
            fixture_date=fixture_date,
            rng=ScriptedRng([]),
        )

        self.assertEqual(player.discipline_yellow_total, 5)
        self.assertEqual(player.discipline_yellow_cycle, 0)
        self.assertEqual(player.suspension_matches_remaining, 1)
        self.assertEqual(
            player.suspension_effective_date,
            fixture_date + timedelta(days=7),
        )

    def test_preincrement_modulo_13_branch_adds_three_matches(self):
        player = RuntimePlayer(
            discipline_yellow_total=12,
            discipline_yellow_cycle=2,
        )
        fixture_date = date(2000, 8, 19)

        apply_league_match_discipline(
            player,
            bookings=1,
            dismissals=0,
            fixture_date=fixture_date,
            rng=ScriptedRng([]),
        )

        self.assertEqual(player.discipline_yellow_total, 13)
        self.assertEqual(player.discipline_yellow_cycle, 3)
        self.assertEqual(player.suspension_matches_remaining, 3)
        self.assertEqual(
            player.suspension_effective_date,
            fixture_date + timedelta(days=7),
        )

    def test_red_card_rng_zero_adds_three_matches_nonzero_adds_one(self):
        fixture_date = date(2000, 8, 19)

        three_match = RuntimePlayer()
        rng = ScriptedRng([0])
        apply_league_match_discipline(
            three_match,
            bookings=0,
            dismissals=1,
            fixture_date=fixture_date,
            rng=rng,
        )
        self.assertEqual(three_match.suspension_matches_remaining, 3)
        self.assertEqual(rng.calls, [3])

        one_match = RuntimePlayer()
        rng = ScriptedRng([2])
        apply_league_match_discipline(
            one_match,
            bookings=0,
            dismissals=1,
            fixture_date=fixture_date,
            rng=rng,
        )
        self.assertEqual(one_match.suspension_matches_remaining, 1)
        self.assertEqual(rng.calls, [3])

    def test_existing_effective_date_is_not_reset_when_more_ban_is_added(self):
        fixture_date = date(2000, 8, 19)
        existing = date(2000, 8, 23)
        player = RuntimePlayer(
            suspension_matches_remaining=1,
            suspension_effective_date=existing,
        )

        apply_league_match_discipline(
            player,
            bookings=1,
            dismissals=1,
            fixture_date=fixture_date,
            rng=ScriptedRng([1]),
        )

        self.assertEqual(player.suspension_effective_date, existing)
        self.assertEqual(player.suspension_matches_remaining, 2)

    def test_seven_day_gate_can_allow_an_intervening_fixture(self):
        player = RuntimePlayer(
            suspension_matches_remaining=1,
            suspension_effective_date=date(2000, 8, 26),
            suspended=True,
        )

        # The just-played Aug 23 fixture is still before the activation date.
        self.assertFalse(
            serve_league_suspension_after_fixture(
                player,
                date(2000, 8, 23),
            )
        )
        self.assertEqual(player.suspension_matches_remaining, 1)

        # A next fixture on Aug 25 is also before activation, so availability
        # remains clear. A fixture on/after Aug 26 activates the ban.
        self.assertFalse(
            refresh_league_suspension_for_next_fixture(
                player,
                date(2000, 8, 25),
            )
        )
        self.assertFalse(player.suspended)

        self.assertTrue(
            refresh_league_suspension_for_next_fixture(
                player,
                date(2000, 8, 26),
            )
        )
        self.assertTrue(player.suspended)

    def test_active_ban_serves_one_match_then_expires(self):
        player = RuntimePlayer(
            suspended=True,
            suspension_matches_remaining=1,
            suspension_effective_date=date(2000, 8, 26),
        )

        self.assertTrue(
            serve_league_suspension_after_fixture(
                player,
                date(2000, 9, 2),
            )
        )
        self.assertFalse(player.suspended)
        self.assertEqual(player.suspension_matches_remaining, 0)
        self.assertFalse(
            refresh_league_suspension_for_next_fixture(
                player,
                date(2000, 9, 9),
            )
        )

    def test_full_side_order_serves_then_adds_cards_then_refreshes(self):
        roster = [RuntimePlayer() for _ in range(4)]
        roster[3].suspended = True
        roster[3].suspension_matches_remaining = 1
        roster[3].suspension_effective_date = date(2000, 8, 19)

        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(20, IncidentRecord(IncidentKind.BOOKED, 0, 0)),
            TimedMatchEvent(70, IncidentRecord(IncidentKind.SENT_OFF, 0, 1)),
        ))
        roster[0].discipline_yellow_cycle = 4

        summary = persist_premier_league_discipline(
            roster,
            roster,
            0,
            result,
            date(2000, 8, 19),
            date(2000, 8, 26),
            ScriptedRng([1]),
        )

        self.assertEqual(summary.served_player_count, 1)
        self.assertEqual(summary.booked_player_indices, frozenset((0,)))
        self.assertEqual(summary.sent_off_player_indices, frozenset((1,)))
        self.assertEqual(roster[0].suspension_matches_remaining, 1)
        self.assertTrue(roster[0].suspended)
        self.assertEqual(roster[1].suspension_matches_remaining, 1)
        self.assertTrue(roster[1].suspended)
        self.assertEqual(roster[3].suspension_matches_remaining, 0)
        self.assertFalse(roster[3].suspended)


class ExactIncidentOrderingTests(unittest.TestCase):
    def test_injury_rng_for_earlier_participant_precedes_later_red_rng(self):
        side = prepared_side()
        participants = [RuntimePlayer() for _ in range(4)]
        roster = participants + [RuntimePlayer() for _ in range(10)]
        result = NormalMatchResult(events=(
            TimedMatchEvent(30, IncidentRecord(IncidentKind.INJURED, 0, 0)),
            TimedMatchEvent(70, IncidentRecord(IncidentKind.SENT_OFF, 0, 1)),
        ))

        # MatchCalculator Condition already exists on PreparedMatchSide. Sync it
        # before the original 0x5127A0 card/injury loop.
        sync_post_match_conditions(side, participants)
        rng = ScriptedRng([
            2,  # Condition 74 -> mode-1 category roll -> ankle
            1,  # ankle severity roll -> minor one-week injury
            1,  # participant 1 red RNG(3) -> one-match suspension
        ])
        summary = persist_premier_league_match_incidents(
            roster,
            participants,
            0,
            result,
            date(2000, 8, 19),
            date(2000, 8, 26),
            rng,
        )

        self.assertEqual(rng.calls, [100, 100, 3])
        self.assertEqual(summary.injured_player_indices, frozenset((0,)))
        self.assertEqual(
            summary.discipline.sent_off_player_indices,
            frozenset((1,)),
        )
        self.assertTrue(participants[0].injured)
        self.assertEqual(participants[0].injury_return_date, date(2000, 8, 26))
        self.assertEqual(participants[0].condition, 64)
        self.assertEqual(participants[1].suspension_matches_remaining, 1)

    def test_condition_sync_happens_before_persistent_injury_drop(self):
        side = prepared_side()
        participants = [RuntimePlayer(condition=80) for _ in range(4)]
        roster = participants + [RuntimePlayer() for _ in range(10)]
        result = NormalMatchResult(events=(
            TimedMatchEvent(40, IncidentRecord(IncidentKind.INJURED, 0, 0)),
        ))

        self.assertEqual(side.players[0].condition, 74)
        sync_post_match_conditions(side, participants)
        self.assertEqual(participants[0].condition, 74)

        # Condition 74 selects low-Condition mode 1. Ankle/minor drops 10.
        rng = ScriptedRng([0, 49])
        persist_premier_league_match_incidents(
            roster,
            participants,
            0,
            result,
            date(2000, 8, 19),
            date(2000, 8, 26),
            rng,
        )
        self.assertEqual(participants[0].injury_source_mode, 1)
        self.assertEqual(participants[0].condition, 64)

        # The later Form pass must not copy PreparedMatchPlayer.condition back.
        form_rng = ScriptedRng([99, 99])
        persist_post_match_form(side, participants, result, form_rng)
        self.assertEqual(participants[0].condition, 64)


class MatchPerformancePersistenceTests(unittest.TestCase):
    def test_live_finalizer_retains_ordered_output_including_unused_player_zero(self):
        side = prepared_side()
        # All eight flag writes also occur on the non-appeared branch.
        side.players[3].skills = (255,) * 17
        runtime = [RuntimePlayer() for _ in range(4)]
        shared = ScriptedRng([])
        engine = ScriptedRng([])
        output = finalize_match_participant_statistics(
            side, runtime, NormalMatchResult(events=()), shared, engine,
        )
        self.assertEqual(tuple(item.player_index for item in output), (0, 1, 2, 3))
        self.assertEqual(tuple(item.rating for item in output), (6, 6, 0, 0))
        self.assertEqual(output[3].skill_flags, bytes((1,) * 8))
        self.assertEqual(output[0].skill_flags, bytes(8))
        self.assertEqual(shared.calls, [])
        self.assertEqual(engine.calls, [])
        self.assertEqual([p.match_performance_history_count for p in runtime], [1, 1, 0, 0])
        with self.assertRaises(FrozenInstanceError):
            output[0].rating = 8

    def test_invalid_complete_side_rejected_before_rng_and_history_mutation(self):
        side = prepared_side()
        side.players[3].player_index = 17
        runtime = [RuntimePlayer() for _ in range(4)]
        shared, engine = ScriptedRng([]), ScriptedRng([])
        with self.assertRaises(ValueError):
            finalize_match_participant_statistics(
                side, runtime, NormalMatchResult(events=()), shared, engine,
            )
        self.assertEqual(shared.calls, [])
        self.assertEqual([p.match_performance_history_count for p in runtime], [0] * 4)

    def test_partial_or_mutable_statistics_cannot_be_finalized_output(self):
        for rating, flags in ((None, bytes(8)), (2, bytes(8)),
                              (7, bytearray(8)), (7, bytes(7)), (7, bytes((2,) * 8))):
            with self.assertRaises(ValueError):
                FinalizedParticipantStatistics(0, rating, flags)

    def test_identity_container_rejects_missing_duplicate_or_reordered_players(self):
        output = (FinalizedParticipantStatistics(0, 7, bytes(8)),
                  FinalizedParticipantStatistics(1, 0, bytes(8)))
        for identities, statistics in (((), ()), ((100,), output),
                                       ((100, 100), output), ((True, 101), output),
                                       ((100, 101), output[::-1])):
            with self.assertRaises(ValueError):
                FinalizedSideParticipantStatistics(identities, statistics)

    def test_exact_history_finalizer_uses_goal_attribution_cards_and_two_rng_streams(self):
        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(
                10,
                ChanceRecord(
                    ChanceSource.OPEN_PLAY,
                    0,
                    0,
                    0,
                    finish_mode=FinishMode.SHOOTING,
                    secondary_player_side=0,
                    secondary_player_index=1,
                ),
            ),
            TimedMatchEvent(20, IncidentRecord(IncidentKind.BOOKED, 0, 1)),
            TimedMatchEvent(60, SubstitutionRecord(0, 1, 2)),
            TimedMatchEvent(75, IncidentRecord(IncidentKind.SENT_OFF, 0, 2)),
        ))
        runtime = [RuntimePlayer() for _ in range(4)]
        runtime[0].match_performance_history[0] = 10
        runtime[0].match_performance_history_count = 1
        runtime[0].match_performance_history_write_index = 1

        shared = ScriptedRng([1, 1, 0, 0])
        engine = ScriptedRng([1])
        ratings = persist_match_performance_history(
            side,
            runtime,
            result,
            shared,
            engine,
        )

        self.assertEqual(ratings, (9, 8, 6))
        self.assertEqual(shared.calls, [2, 2, 2, 2])
        self.assertEqual(engine.calls, [2])
        self.assertEqual(runtime[0].match_performance_history[:2], [10, 9])
        self.assertEqual(runtime[1].match_performance_history[0], 8)
        self.assertEqual(runtime[2].match_performance_history[0], 6)
        self.assertEqual(runtime[3].match_performance_history_count, 0)

    def test_completed_finalizer_preserves_side_local_target_then_trajectory_rng_order(self):
        context = TeamStrengthContext(
            tactic_style=0,
            match_bias=2,
            user_controlled=False,
            aggression=5,
        )

        def finalizer_side(side_id):
            prepared = PreparedMatchPlayer(
                side=side_id,
                player_index=0,
                condition=80,
                form_state=2,
                current_position=12,
                balance_position_code=10,
                preferred_positions=(12, 0, 0),
                skills=(100,) * 17,
                active=False,
                substitution_available=False,
            )
            return PreparedMatchSide(
                players=(prepared,),
                attack_context=context,
                defence_context=context,
                penalty_taker_priority=(),
                corner_taker_priority=(),
                free_kick_taker_priority=(),
                starting_player_indices=(0,),
            )

        result = NormalMatchResult(
            events=(
                TimedMatchEvent(20, IncidentRecord(IncidentKind.SENT_OFF, 0, 0)),
                TimedMatchEvent(30, IncidentRecord(IncidentKind.SENT_OFF, 1, 0)),
            ),
            raw_condition_history_prefixes=(
                RawPlayerConditionHistory(0, 0, (70,) * 18),
                RawPlayerConditionHistory(1, 0, (60,) * 18),
            ),
            condition_history_sample_count=18,
        )
        side0 = finalizer_side(0)
        side1 = finalizer_side(1)
        runtime0 = [RuntimePlayer(form_state=0)]
        runtime1 = [RuntimePlayer(form_state=0)]
        shared = ScriptedRng([])
        engine = ScriptedRng(
            [0] + [1] * 17
            + [0] + [1] * 17
        )
        captured_statistics = []

        finalized = persist_match_performance_and_fastview_form_histories(
            side0,
            runtime0,
            side1,
            runtime1,
            result,
            shared,
            engine,
            statistics_sink=captured_statistics.append,
        )

        self.assertEqual(len(captured_statistics), 2)
        self.assertEqual(tuple(s[0].rating for s in captured_statistics), (4, 4))
        self.assertEqual(tuple(s[0].player_index for s in captured_statistics), (0, 0))
        self.assertEqual(shared.calls, [])
        self.assertEqual(
            engine.calls,
            [3] + [2] * 17 + [3] + [2] * 17,
        )
        self.assertEqual(
            [
                (item.side_index, item.player_index, item.target_rating)
                for item in finalized.fastview_form_histories
            ],
            [(0, 0, 4), (1, 0, 4)],
        )
        self.assertEqual(
            [
                (item.side_index, item.player_index)
                for item in finalized.fastview_condition_histories
            ],
            [(0, 0), (1, 0)],
        )
        self.assertEqual(
            finalized.fastview_condition_histories[0].samples,
            (70,) * 18 + (80,) * 6,
        )
        self.assertEqual(
            finalized.fastview_condition_histories[1].samples,
            (60,) * 18 + (80,) * 6,
        )
        self.assertEqual(
            finalized.fastview_form_histories[0].samples,
            (5,) + (4,) * 23,
        )
        self.assertEqual(
            finalized.fastview_form_histories[1].samples,
            (5,) + (4,) * 23,
        )
        self.assertEqual(runtime0[0].match_performance_history[0], 4)
        self.assertEqual(runtime1[0].match_performance_history[0], 4)

    def test_completed_finalizer_keeps_human_match_condition_history_raw_only(self):
        ai_context = TeamStrengthContext(
            tactic_style=0,
            match_bias=2,
            user_controlled=False,
            aggression=5,
        )
        human_context = TeamStrengthContext(
            tactic_style=0,
            match_bias=2,
            user_controlled=True,
            aggression=5,
        )

        def side(side_id, context):
            return PreparedMatchSide(
                players=(PreparedMatchPlayer(
                    side=side_id,
                    player_index=0,
                    condition=80,
                    form_state=2,
                    current_position=12,
                    balance_position_code=10,
                    preferred_positions=(12, 0, 0),
                    skills=(100,) * 17,
                    active=False,
                    substitution_available=False,
                ),),
                attack_context=context,
                defence_context=context,
                penalty_taker_priority=(),
                corner_taker_priority=(),
                free_kick_taker_priority=(),
                starting_player_indices=(0,),
            )

        result = NormalMatchResult(
            events=(
                TimedMatchEvent(20, IncidentRecord(IncidentKind.SENT_OFF, 0, 0)),
                TimedMatchEvent(30, IncidentRecord(IncidentKind.SENT_OFF, 1, 0)),
            ),
            raw_condition_history_prefixes=(
                RawPlayerConditionHistory(0, 0, (70,) * 18),
                RawPlayerConditionHistory(1, 0, (60,) * 18),
            ),
            condition_history_sample_count=18,
        )
        finalized = persist_match_performance_and_fastview_form_histories(
            side(0, human_context),
            [RuntimePlayer(form_state=0)],
            side(1, ai_context),
            [RuntimePlayer(form_state=0)],
            result,
            ScriptedRng([]),
            ScriptedRng([0] + [1] * 17 + [0] + [1] * 17),
        )

        self.assertEqual(finalized.fastview_condition_histories, ())
        self.assertEqual(
            finalized.raw_condition_history_prefixes,
            result.raw_condition_history_prefixes,
        )
        self.assertEqual(len(finalized.fastview_form_histories), 2)

    def test_completed_finalizer_fails_closed_without_live_history_sample_count(self):
        context = TeamStrengthContext(
            tactic_style=0,
            match_bias=2,
            user_controlled=False,
            aggression=5,
        )
        side0 = PreparedMatchSide(
            players=(PreparedMatchPlayer(
                side=0,
                player_index=0,
                condition=80,
                form_state=2,
                current_position=12,
                balance_position_code=10,
                preferred_positions=(12, 0, 0),
                skills=(100,) * 17,
            ),),
            attack_context=context,
            defence_context=context,
            penalty_taker_priority=(),
            corner_taker_priority=(),
            free_kick_taker_priority=(),
            starting_player_indices=(0,),
        )
        side1 = PreparedMatchSide(
            players=(PreparedMatchPlayer(
                side=1,
                player_index=0,
                condition=80,
                form_state=2,
                current_position=12,
                balance_position_code=10,
                preferred_positions=(12, 0, 0),
                skills=(100,) * 17,
            ),),
            attack_context=context,
            defence_context=context,
            penalty_taker_priority=(),
            corner_taker_priority=(),
            free_kick_taker_priority=(),
            starting_player_indices=(0,),
        )
        with self.assertRaisesRegex(ValueError, "sample count 18 or 24"):
            persist_match_performance_and_fastview_form_histories(
                side0,
                [RuntimePlayer()],
                side1,
                [RuntimePlayer()],
                NormalMatchResult(events=()),
                ScriptedRng([]),
                ScriptedRng([]),
            )


class PostMatchPersistenceTests(unittest.TestCase):
    def test_appeared_set_is_starters_plus_incoming_substitutes(self):
        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(60, SubstitutionRecord(0, 1, 2)),
        ))
        self.assertEqual(
            appeared_player_indices(side, result),
            frozenset((0, 1, 2)),
        )

    def test_condition_injury_and_form_persist_in_participant_order(self):
        side = prepared_side()
        result = NormalMatchResult(events=(
            TimedMatchEvent(55, IncidentRecord(IncidentKind.INJURED, 0, 1)),
            TimedMatchEvent(55, SubstitutionRecord(0, 1, 2)),
        ))
        runtime = [
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=2),
            RuntimePlayer(condition=80, form_state=4),
        ]
        # Three appeared players. Every trigger succeeds and every transition
        # chooses the increase branch: two RNG(100) draws per appeared player.
        rng = ScriptedRng([0, 0, 0, 0, 0, 0])
        settings = FormTransitionSettings(
            form_change_prob=100,
            in_form_change_prob=100,
            out_of_form_change_prob=100,
            form_increase_prob=100,
        )

        summary = persist_post_match_side(
            side,
            runtime,
            result,
            rng,
            form_settings=settings,
        )

        self.assertEqual([p.condition for p in runtime], [74, 73, 79, 80])
        self.assertEqual([p.form_state for p in runtime], [3, 3, 3, 4])
        self.assertFalse(runtime[0].injured)
        self.assertTrue(runtime[1].injured)
        self.assertFalse(runtime[2].injured)
        self.assertEqual(summary.appeared_player_indices, frozenset((0, 1, 2)))
        self.assertEqual(summary.injured_player_indices, frozenset((1,)))
        self.assertEqual(rng.calls, [100] * 6)

    def test_wrong_participant_count_is_rejected(self):
        with self.assertRaises(ValueError):
            persist_post_match_side(
                prepared_side(),
                [RuntimePlayer()],
                NormalMatchResult(events=()),
                ScriptedRng([]),
            )


if __name__ == "__main__":
    unittest.main()
