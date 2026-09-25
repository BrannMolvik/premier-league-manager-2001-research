import unittest
from dataclasses import dataclass
from datetime import date, timedelta

from match_events import IncidentKind, IncidentRecord, SubstitutionRecord
from match_postmatch import (
    FormTransitionSettings,
    appeared_player_indices,
    apply_league_match_discipline,
    persist_post_match_form,
    persist_post_match_side,
    persist_premier_league_discipline,
    persist_premier_league_match_incidents,
    refresh_league_suspension_for_next_fixture,
    sync_post_match_conditions,
    serve_league_suspension_after_fixture,
    update_post_match_form,
)
from match_simulation import (
    NormalMatchResult,
    PreparedMatchPlayer,
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
            2,  # participant 0 injury category -> broken toe
            1,  # broken-toe RNG(4) -> four weeks
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

        self.assertEqual(rng.calls, [100, 4, 3])
        self.assertEqual(summary.injured_player_indices, frozenset((0,)))
        self.assertEqual(
            summary.discipline.sent_off_player_indices,
            frozenset((1,)),
        )
        self.assertTrue(participants[0].injured)
        self.assertEqual(participants[0].injury_return_date, date(2000, 9, 16))
        self.assertEqual(participants[0].condition, 34)
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
