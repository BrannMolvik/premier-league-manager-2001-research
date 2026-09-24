import unittest
from unittest.mock import patch

from match_calculator import PositionRole
from match_events import BoundaryRecord, BoundaryType, ChanceOutcome, ChanceRecord, SubstitutionRecord
from match_orders import TeamOrderPriorities
from match_simulation import (
    PreparedMatchPlayer,
    PreparedMatchSide,
    resolve_attacking_sequence,
    simulate_normal_match,
)
from match_strength import SegmentAttack, TeamStrengthContext


class ScriptedRng:
    def __init__(self, values):
        self.values = list(values)

    def randbelow(self, bound):
        if not self.values:
            raise AssertionError(f"unexpected RNG({bound})")
        value = self.values.pop(0)
        if not 0 <= value < bound:
            raise AssertionError(f"scripted value {value} outside RNG({bound})")
        return value


class MidpointRng:
    def randbelow(self, bound):
        return bound // 2


def raw_skills(value=100):
    return (value,) * 17


def player(
    side,
    idx,
    role,
    value=100,
    *,
    active=True,
    bench=False,
    preferred=None,
    aux=0,
):
    return PreparedMatchPlayer(
        side=side,
        player_index=idx,
        condition=100,
        form_state=2,
        current_position=role,
        balance_position_code=int(role),
        preferred_positions=preferred or (int(role), 0, 0),
        skills=raw_skills(value),
        active=active,
        substitution_available=bench,
        position_aux_code=aux,
    )


def context(user_controlled=True):
    return TeamStrengthContext(
        tactic_style=0,
        match_bias=2,
        user_controlled=user_controlled,
        aggression=5,
    )


def side(side_id, players, taker_index, *, user_controlled=True):
    team_context = context(user_controlled)
    return PreparedMatchSide(
        players=tuple(players),
        attack_context=team_context,
        defence_context=team_context,
        penalty_taker_priority=(taker_index,),
        corner_taker_priority=(taker_index,),
        free_kick_taker_priority=(taker_index,),
    )


def matrix(value=1.0):
    return tuple(
        tuple(
            tuple(float(value) for _ in range(17))
            for _ in range(20)
        )
        for _ in range(4)
    )


class PreparedMatchTests(unittest.TestCase):
    def test_raw_skill_mapping_into_chance_player(self):
        skills = list(range(17))
        subject = PreparedMatchPlayer(
            side=0,
            player_index=4,
            condition=100,
            form_state=2,
            current_position=PositionRole.CENTRE_MIDFIELD,
            balance_position_code=12,
            preferred_positions=(12, 0, 0),
            skills=tuple(skills),
        )
        chance = subject.chance_player()
        self.assertEqual(chance.passing, 5)
        self.assertEqual(chance.shooting, 6)
        self.assertEqual(chance.tackling, 7)
        self.assertEqual(chance.heading, 8)
        self.assertEqual(chance.control, 9)
        self.assertEqual(chance.goalkeeping, 13)
        self.assertEqual(chance.set_piece, 16)

    def test_team_orders_may_reference_inactive_players_for_fallback(self):
        prepared = PreparedMatchSide(
            players=(player(0, 1, PositionRole.CENTRE_MIDFIELD),),
            attack_context=context(),
            defence_context=context(),
            penalty_taker_priority=(99, 1),
            corner_taker_priority=(99, 1),
            free_kick_taker_priority=(99, 1),
        )
        self.assertEqual(prepared.penalty_taker_priority, (99, 1))

    def test_team_order_priorities_bridge_all_four_consumers(self):
        prepared = PreparedMatchSide.from_team_orders(
            players=(player(0, 1, PositionRole.CENTRE_MIDFIELD),),
            attack_context=context(),
            defence_context=context(),
            team_orders=TeamOrderPriorities(
                captain=(8, 1),
                penalty=(9, 1),
                corner=(7, 1),
                free_kick=(6, 1),
            ),
        )

        self.assertEqual(prepared.attack_context.captain_priority, (8, 1))
        self.assertEqual(prepared.defence_context.captain_priority, (8, 1))
        self.assertEqual(prepared.penalty_taker_priority, (9, 1))
        self.assertEqual(prepared.corner_taker_priority, (7, 1))
        self.assertEqual(prepared.free_kick_taker_priority, (6, 1))

    def test_starting_indices_capture_active_players_not_bench(self):
        prepared = side(
            0,
            [
                player(0, 1, PositionRole.CENTRE_MIDFIELD),
                player(
                    0,
                    11,
                    PositionRole.CENTRE_MIDFIELD,
                    active=False,
                    bench=True,
                ),
            ],
            1,
        )
        self.assertEqual(prepared.starting_player_indices, (1,))
        self.assertEqual(
            [item.player_index for item in prepared.active_prepared_players()],
            [1],
        )


class SequenceIntegrationTests(unittest.TestCase):
    def test_recovered_open_play_path_scores_goal(self):
        attack = side(
            0,
            [player(0, 1, PositionRole.CENTRE_MIDFIELD)],
            1,
        )
        defend = side(
            1,
            [
                player(1, 0, PositionRole.GOALKEEPER),
                player(1, 2, PositionRole.CENTRE_BACK),
            ],
            0,
        )
        scores = [0, 0]
        rng = ScriptedRng([50, 0, 0, 80, 0, 0, 0, 0, 255, 0, 1, 50])

        events = resolve_attacking_sequence(25, attack, defend, scores, rng)

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].minute, 25)
        self.assertIsInstance(events[0].event, ChanceRecord)
        self.assertEqual(events[0].event.outcome, ChanceOutcome.GOAL)
        self.assertEqual(scores, [1, 0])


class FullNormalMatchTests(unittest.TestCase):
    def lineup(self, side_id):
        roles = (
            PositionRole.GOALKEEPER,
            PositionRole.RIGHT_BACK,
            PositionRole.LEFT_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.DEFENSIVE_MIDFIELD,
            PositionRole.RIGHT_MIDFIELD,
            PositionRole.LEFT_MIDFIELD,
            PositionRole.CENTRE_MIDFIELD,
            PositionRole.CENTRE_FORWARD,
            PositionRole.STRIKER,
        )
        return [
            player(side_id, index, role, value=50)
            for index, role in enumerate(roles)
        ]

    def test_scheduler_rng7_zero_attempts_ai_sub_for_opposite_side(self):
        home = side(0, self.lineup(0), 10, user_controlled=True)

        away_roles = (
            PositionRole.GOALKEEPER,
            PositionRole.RIGHT_BACK,
            PositionRole.LEFT_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.SWEEPER,
            PositionRole.RIGHT_WING_BACK,
            PositionRole.LEFT_WING_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.CENTRE_BACK,
            PositionRole.CENTRE_MIDFIELD,
        )
        away_players = [
            player(1, index, role, value=50)
            for index, role in enumerate(away_roles)
        ]
        away_players.append(
            player(
                1,
                11,
                PositionRole.CENTRE_MIDFIELD,
                value=250,
                active=False,
                bench=True,
            )
        )
        away = side(1, away_players, 10, user_controlled=False)

        class Rng7Gate:
            def randbelow(self, bound):
                return 0 if bound == 7 else bound - 1

        def one_home_attack_at_sixty(segment_start, weights, rng):
            if segment_start == 60:
                return (SegmentAttack(0, 61),)
            return ()

        with patch(
            "match_simulation.schedule_segment_attacks",
            side_effect=one_home_attack_at_sixty,
        ), patch(
            "match_simulation.resolve_attacking_sequence",
            return_value=(),
        ):
            result = simulate_normal_match(
                home,
                away,
                matrix(),
                matrix(),
                Rng7Gate(),
            )

        substitutions = [
            timed
            for timed in result.events
            if isinstance(timed.event, SubstitutionRecord)
        ]
        self.assertEqual(len(substitutions), 1)
        self.assertEqual(substitutions[0].minute, 61)
        self.assertEqual(substitutions[0].event.player_side, 1)
        self.assertEqual(substitutions[0].event.outgoing_player_index, 10)
        self.assertEqual(substitutions[0].event.incoming_player_index, 11)
        self.assertFalse(away_players[10].active)
        self.assertTrue(away_players[11].active)

    def test_normal_match_runs_all_16_segments_and_boundaries(self):
        home = side(0, self.lineup(0), 10)
        away = side(1, self.lineup(1), 10)

        result = simulate_normal_match(
            home,
            away,
            matrix(),
            matrix(),
            MidpointRng(),
        )

        boundaries = [
            timed for timed in result.events
            if isinstance(timed.event, BoundaryRecord)
        ]
        self.assertEqual(
            [(item.minute, item.event.kind) for item in boundaries],
            [
                (45, BoundaryType.HALF_TIME),
                (90, BoundaryType.FULL_TIME),
            ],
        )
        self.assertEqual(result.score, (0, 0))
        self.assertEqual(len(result.possession_segments), 16)
        self.assertEqual(
            [slot.calculation_minute for slot in result.possession_segments],
            [5, 10, 15, 20, 25, 30, 35, 40, 50, 55, 60, 65, 70, 75, 80, 85],
        )


if __name__ == "__main__":
    unittest.main()
