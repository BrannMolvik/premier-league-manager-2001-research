import unittest

from match_calculator import PositionRole
from match_events import BoundaryRecord, BoundaryType, ChanceOutcome, ChanceRecord
from match_simulation import (
    PreparedMatchPlayer,
    PreparedMatchSide,
    resolve_attacking_sequence,
    simulate_normal_match,
)
from match_strength import TeamStrengthContext


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


def player(side, idx, role, value=100):
    return PreparedMatchPlayer(
        side=side,
        player_index=idx,
        condition=100,
        form_state=2,
        current_position=role,
        balance_position_code=int(role),
        preferred_positions=(int(role), 0, 0),
        skills=raw_skills(value),
    )


def context():
    return TeamStrengthContext(
        tactic_style=0,
        match_bias=2,
        user_controlled=True,
        aggression=5,
    )


def side(side_id, players, taker_index):
    return PreparedMatchSide(
        players=tuple(players),
        attack_context=context(),
        defence_context=context(),
        penalty_taker_index=taker_index,
        corner_taker_index=taker_index,
        free_kick_taker_index=taker_index,
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

    def test_takers_must_be_active(self):
        with self.assertRaises(ValueError):
            PreparedMatchSide(
                players=(player(0, 1, PositionRole.STRIKER),),
                attack_context=context(),
                defence_context=context(),
                penalty_taker_index=99,
                corner_taker_index=1,
                free_kick_taker_index=1,
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
