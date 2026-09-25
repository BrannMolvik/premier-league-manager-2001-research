import unittest
from dataclasses import dataclass

from match_lineup import AI_FORMATIONS
from match_orders import TeamOrderPriorities
from match_preparation import (
    build_prepared_match_side_from_selection,
    prepare_ai_match_selection,
    prepare_premier_league_ai_match_side,
    prepare_premier_league_ai_selection,
)
from match_team_setup import TeamTacticalState


@dataclass
class Player:
    player_index: int
    club_id: int
    skills: tuple[int, ...]
    preferred_positions: tuple[int, int, int]
    form_state: int = 2
    current_position: int = 0
    position_aux_code: int = 0
    match_active: bool = False
    match_substitute_available: bool = False
    injured: bool = False
    suspended: bool = False
    selection_excluded: bool = False
    non_eu: bool = False
    condition: int = 80
    balance_position_code: int = 10

    def assign_match_position(self, role, auxiliary_code):
        self.current_position = int(role)
        self.position_aux_code = int(auxiliary_code)

    def reset_match_position(self):
        self.current_position = int(self.preferred_positions[0])
        self.position_aux_code = 0

    def set_match_active(self):
        self.match_active = True
        self.match_substitute_available = False

    def set_match_substitute_available(self):
        self.match_active = False
        self.match_substitute_available = True

    def clear_match_selection(self, *, reset_position=False):
        self.match_active = False
        self.match_substitute_available = False
        if reset_position:
            self.reset_match_position()


def player(index, club, role, value=180, **kwargs):
    return Player(
        player_index=index,
        club_id=club,
        skills=(value,) * 17,
        preferred_positions=(int(role), 0, 0),
        current_position=int(role),
        **kwargs,
    )


class MidpointRng:
    def __init__(self):
        self.calls = []

    def randbelow(self, bound):
        self.calls.append(bound)
        return bound // 2


def formation_zero_roster(club=7):
    return [
        player(index, club, slot.role, 180)
        for index, slot in enumerate(AI_FORMATIONS[0])
    ]


class AiMatchPreparationTests(unittest.TestCase):
    def test_commits_roles_flags_and_participants(self):
        roster = formation_zero_roster()
        bench_mid = player(11, 7, 12, 160)
        bench_forward = player(12, 7, 19, 160)
        bench_defender = player(13, 7, 4, 160)
        bench_goalkeeper = player(14, 7, 1, 160)
        roster.extend((bench_mid, bench_forward, bench_defender, bench_goalkeeper))

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=4,
        )

        self.assertEqual(len(prepared.lineup.starters), 11)
        for slot_index, assignment in enumerate(prepared.lineup.starters):
            selected = next(
                item for item in roster
                if item.player_index == assignment.player_index
            )
            self.assertTrue(selected.match_active)
            self.assertFalse(selected.match_substitute_available)
            self.assertEqual(selected.current_position, AI_FORMATIONS[0][slot_index].role)
            self.assertEqual(
                selected.position_aux_code,
                AI_FORMATIONS[0][slot_index].auxiliary_code,
            )

        self.assertEqual(
            prepared.lineup.substitutes,
            (11, 12, 13, 14),
        )
        self.assertTrue(all(roster[i].match_substitute_available for i in range(11, 15)))
        self.assertEqual(
            [item.player_index for item in prepared.participants],
            list(range(15)),
        )

    def test_participant_collection_preserves_roster_not_formation_order(self):
        roster = formation_zero_roster()
        roster = list(reversed(roster))

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
        )

        self.assertEqual(
            [item.player_index for item in prepared.participants],
            [item.player_index for item in roster],
        )

    def test_base_unavailable_player_is_excluded_from_selection(self):
        roster = formation_zero_roster()
        injured = player(20, 7, 19, 255, injured=True)
        healthy = player(21, 7, 19, 20)
        # Replace the two natural strikers so one strong injured candidate and
        # one weak healthy candidate compete for a slot.
        roster[0] = injured
        roster[1] = healthy

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
        )

        starter_ids = {item.player_index for item in prepared.lineup.starters}
        self.assertNotIn(20, starter_ids)
        self.assertIn(21, starter_ids)

    def test_additional_competition_eligibility_is_composed(self):
        roster = formation_zero_roster()
        blocked = roster[0]

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
            additional_eligible=lambda candidate: candidate is not blocked,
        )

        self.assertNotIn(
            blocked.player_index,
            {item.player_index for item in prepared.lineup.starters},
        )

    def test_ai_retries_once_with_non_eu_counter_disabled(self):
        roster = formation_zero_roster()
        for subject in roster:
            subject.non_eu = True

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
            non_eu_limit=3,
        )

        self.assertEqual(len(prepared.lineup.starters), 11)
        self.assertTrue(prepared.non_eu_restriction_relaxed)
        self.assertTrue(all(subject.match_active for subject in roster))

    def test_zero_non_eu_limit_still_blocks_players_after_retry(self):
        roster = formation_zero_roster()
        for subject in roster:
            subject.non_eu = True

        with self.assertRaises(ValueError):
            prepare_ai_match_selection(
                7,
                roster,
                formation_id=0,
                substitute_quota=0,
                non_eu_limit=0,
            )

        self.assertTrue(all(not subject.match_active for subject in roster))
        self.assertTrue(
            all(not subject.match_substitute_available for subject in roster)
        )

    def test_disabled_restriction_flag_uses_no_counting_without_retry_marker(self):
        roster = formation_zero_roster()
        for subject in roster:
            subject.non_eu = True

        prepared = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
            non_eu_limit=3,
            enforce_non_eu_restriction=False,
        )

        self.assertEqual(len(prepared.lineup.starters), 11)
        self.assertFalse(prepared.non_eu_restriction_relaxed)

    def test_selected_runtime_state_bridges_to_side_local_match_indices(self):
        roster = list(reversed(formation_zero_roster()))
        selected = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
        )

        prepared = build_prepared_match_side_from_selection(
            selected,
            side=0,
            tactical_state=TeamTacticalState(
                play_style=0,
                without_ball_style=3,
                with_ball_style=2,
                aggression=7,
            ),
            user_controlled=True,
            team_orders=TeamOrderPriorities(
                captain=(10,),
                penalty=(9,),
                corner=(8,),
                free_kick=(7,),
            ),
        )

        # Participant order, not persistent player ID, defines match identity.
        self.assertEqual(
            [item.player_index for item in prepared.players],
            list(range(11)),
        )
        self.assertEqual(
            [item.preferred_positions[0] for item in prepared.players],
            [item.preferred_positions[0] for item in selected.participants],
        )

        persistent_to_local = {
            subject.player_index: local
            for local, subject in enumerate(selected.participants)
        }
        self.assertEqual(
            prepared.attack_context.captain_priority,
            (persistent_to_local[10],),
        )
        self.assertEqual(
            prepared.penalty_taker_priority,
            (persistent_to_local[9],),
        )
        self.assertEqual(
            prepared.corner_taker_priority,
            (persistent_to_local[8],),
        )
        self.assertEqual(
            prepared.free_kick_taker_priority,
            (persistent_to_local[7],),
        )

        self.assertEqual(prepared.attack_context.tactic_style, 2)
        self.assertEqual(prepared.defence_context.tactic_style, 3)
        self.assertEqual(prepared.attack_context.match_bias, 3)
        self.assertEqual(prepared.defence_context.match_bias, 3)
        self.assertEqual(prepared.attack_context.aggression, 7)
        self.assertEqual(prepared.defence_context.aggression, 7)

        expected_starters = tuple(
            persistent_to_local[assignment.player_index]
            for assignment in selected.lineup.starters
        )
        self.assertEqual(prepared.starting_player_indices, expected_starters)
        self.assertTrue(all(item.condition == 80 for item in prepared.players))
        self.assertTrue(
            all(item.balance_position_code == 10 for item in prepared.players)
        )

    def test_missing_priority_player_id_is_omitted_from_match_priority(self):
        roster = formation_zero_roster()
        selected = prepare_ai_match_selection(
            7,
            roster,
            formation_id=0,
            substitute_quota=0,
        )
        prepared = build_prepared_match_side_from_selection(
            selected,
            side=0,
            tactical_state=TeamTacticalState(),
            user_controlled=True,
            team_orders=TeamOrderPriorities(captain=(999, 0)),
        )
        self.assertEqual(prepared.attack_context.captain_priority, (0,))

    def test_premier_league_ai_selection_derives_formation_quota_and_non_eu_limit(self):
        @dataclass(frozen=True)
        class Manager:
            formation_default: int = 0
            formation_class3: int = 2
            formation_class1: int = 1

        @dataclass(frozen=True)
        class Competition:
            substitute_quota: int = 5
            max_non_eu_players: int = 3

        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        roster = formation_zero_roster(club=7)
        roster.extend(
            (
                player(11, 7, 12, 160),
                player(12, 7, 19, 160),
                player(13, 7, 4, 160),
                player(14, 7, 1, 160),
                player(15, 7, 10, 150),
            )
        )
        opponent = formation_zero_roster(club=8)

        # With four matches remaining, club 7 is four points below the safe
        # relegation cut. League pressure +2 plus home value +1 reaches the
        # exact GSAttPerc threshold and selects the attacking alternate.
        table = [
            Row(1, 34, 80),
            Row(2, 34, 70),
            Row(3, 34, 65),
            Row(4, 34, 60),
            Row(5, 34, 55),
            Row(6, 34, 50),
            Row(9, 34, 40),
            Row(10, 34, 35),
            Row(11, 34, 30),
            Row(12, 34, 28),
            Row(13, 34, 27),
            Row(14, 34, 26),
            Row(15, 34, 25),
            Row(16, 34, 24),
            Row(17, 34, 23),
            Row(18, 34, 22),
            Row(19, 34, 21),
            Row(20, 34, 20),
            Row(7, 34, 18),
            Row(8, 34, 16),
        ]

        result = prepare_premier_league_ai_selection(
            7,
            roster,
            opponent,
            Manager(),
            Competition(),
            table,
            is_home=True,
        )

        self.assertEqual(result.strategy_score, 3)
        self.assertEqual(int(result.selection_class), 1)
        self.assertEqual(result.formation_id, 1)
        self.assertEqual(result.substitute_quota, 5)
        self.assertEqual(len(result.selection.lineup.starters), 11)
        self.assertEqual(len(result.selection.lineup.substitutes), 5)

    def test_premier_league_ai_selection_uses_normal_formation_early_season(self):
        @dataclass(frozen=True)
        class Manager:
            formation_default: int = 0
            formation_class3: int = 2
            formation_class1: int = 1

        @dataclass(frozen=True)
        class Competition:
            substitute_quota: int = 5
            max_non_eu_players: int = 3

        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        roster = formation_zero_roster(club=7)
        roster.extend(
            player(11 + i, 7, role, 150)
            for i, role in enumerate((12, 19, 4, 1, 10))
        )
        opponent = formation_zero_roster(club=8)
        table = [Row(club_id, 10, 20) for club_id in range(1, 21)]

        result = prepare_premier_league_ai_selection(
            7,
            roster,
            opponent,
            Manager(),
            Competition(),
            table,
            is_home=False,
        )

        self.assertEqual(result.strategy_score, -1)
        self.assertEqual(int(result.selection_class), 2)
        self.assertEqual(result.formation_id, 0)
        self.assertEqual(result.substitute_quota, 5)

    def test_autonomous_ai_match_side_uses_exact_fresh_backend_defaults(self):
        @dataclass(frozen=True)
        class Manager:
            formation_default: int = 0
            formation_class3: int = 2
            formation_class1: int = 1

        @dataclass(frozen=True)
        class Competition:
            substitute_quota: int = 5
            max_non_eu_players: int = 3

        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        roster = formation_zero_roster(club=7)
        roster.extend(
            player(11 + i, 7, role, 150)
            for i, role in enumerate((12, 19, 4, 1, 10))
        )
        opponent = formation_zero_roster(club=8)
        table = [Row(club_id, 10, 20) for club_id in range(1, 21)]

        result = prepare_premier_league_ai_match_side(
            7,
            roster,
            opponent,
            Manager(),
            Competition(),
            table,
            side=0,
            is_home=True,
            rng=MidpointRng(),
        )

        self.assertEqual(result.tactical_state, TeamTacticalState())
        self.assertFalse(result.match_side.attack_context.user_controlled)
        self.assertFalse(result.match_side.defence_context.user_controlled)
        self.assertEqual(result.match_side.attack_context.tactic_style, 0)
        self.assertEqual(result.match_side.defence_context.tactic_style, 0)
        self.assertEqual(result.match_side.attack_context.match_bias, 2)
        self.assertEqual(result.match_side.defence_context.match_bias, 2)
        self.assertEqual(result.match_side.attack_context.aggression, 5)
        self.assertEqual(len(result.match_side.starting_player_indices), 11)
        self.assertEqual(len(result.match_side.players), 16)
        self.assertTrue(all(subject.condition == 95 for subject in roster))
        self.assertTrue(all(subject.condition == 95 for subject in result.match_side.players))

    def test_autonomous_ai_match_side_preserves_supplied_live_tactics(self):
        @dataclass(frozen=True)
        class Manager:
            formation_default: int = 0
            formation_class3: int = 2
            formation_class1: int = 1

        @dataclass(frozen=True)
        class Competition:
            substitute_quota: int = 5
            max_non_eu_players: int = 3

        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        roster = formation_zero_roster(club=7)
        roster.extend(
            player(11 + i, 7, role, 150)
            for i, role in enumerate((12, 19, 4, 1, 10))
        )
        opponent = formation_zero_roster(club=8)
        table = [Row(club_id, 10, 20) for club_id in range(1, 21)]
        live = TeamTacticalState(
            play_style=2,
            without_ball_style=3,
            with_ball_style=2,
            aggression=8,
        )

        result = prepare_premier_league_ai_match_side(
            7,
            roster,
            opponent,
            Manager(),
            Competition(),
            table,
            side=1,
            is_home=False,
            rng=MidpointRng(),
            tactical_state=live,
        )

        self.assertIs(result.tactical_state, live)
        self.assertEqual(result.match_side.side, 1)
        self.assertEqual(result.match_side.attack_context.tactic_style, 2)
        self.assertEqual(result.match_side.defence_context.tactic_style, 3)
        self.assertEqual(result.match_side.attack_context.match_bias, 1)
        self.assertEqual(result.match_side.attack_context.aggression, 8)
    def test_incomplete_xi_raises_before_mutating_existing_state(self):
        subject = player(
            1,
            7,
            19,
            100,
            match_active=True,
            position_aux_code=3,
        )

        with self.assertRaises(ValueError):
            prepare_ai_match_selection(
                7,
                [subject],
                formation_id=0,
                substitute_quota=0,
            )

        self.assertTrue(subject.match_active)
        self.assertEqual(subject.position_aux_code, 3)


if __name__ == "__main__":
    unittest.main()
