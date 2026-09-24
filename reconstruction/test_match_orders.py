import unittest

from match_calculator import MatchSkillPlayer, PositionRole
from match_orders import (
    TeamOrderCategory,
    first_active_priority,
    select_set_piece_taker,
)


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


def player(index, role, set_piece=100):
    return MatchSkillPlayer(
        side=0,
        player_index=index,
        condition=100,
        form_state=2,
        current_position=role,
        preferred_positions=(int(role), 0, 0),
        passing=100,
        shooting=100,
        tackling=100,
        heading=100,
        control=100,
        goalkeeping=100,
        set_piece=set_piece,
    )


class TeamOrderSelectionTests(unittest.TestCase):
    def test_human_priority_skips_missing_entries(self):
        players = [
            player(3, PositionRole.CENTRE_MIDFIELD),
            player(7, PositionRole.STRIKER),
        ]
        selected = first_active_priority(players, (9, 7, 3))
        self.assertEqual(selected.player_index, 7)

    def test_human_set_piece_falls_back_to_62b780_carrier(self):
        players = [
            player(3, PositionRole.CENTRE_MIDFIELD),
            player(7, PositionRole.ATTACKING_MIDFIELD),
        ]
        rng = ScriptedRng([0])
        selected = select_set_piece_taker(
            players,
            TeamOrderCategory.FREE_KICK,
            True,
            (99,),
            rng,
        )
        self.assertEqual(selected.player_index, 3)
        self.assertEqual(rng.calls, [1])

    def test_ai_penalty_uses_carrier_fallback_directly(self):
        players = [
            player(1, PositionRole.CENTRE_MIDFIELD, set_piece=1),
            player(2, PositionRole.ATTACKING_MIDFIELD, set_piece=255),
        ]
        rng = ScriptedRng([0])
        selected = select_set_piece_taker(
            players,
            TeamOrderCategory.PENALTY,
            False,
            (),
            rng,
        )
        self.assertEqual(selected.player_index, 1)
        self.assertEqual(rng.calls, [1])

    def test_ai_corner_and_free_kick_choose_highest_effective_set_piece_non_gk(self):
        players = [
            player(1, PositionRole.GOALKEEPER, set_piece=255),
            player(2, PositionRole.CENTRE_BACK, set_piece=120),
            player(3, PositionRole.CENTRE_MIDFIELD, set_piece=180),
            player(4, PositionRole.STRIKER, set_piece=180),
        ]
        for category in (TeamOrderCategory.CORNER, TeamOrderCategory.FREE_KICK):
            selected = select_set_piece_taker(
                players,
                category,
                False,
                (),
                ScriptedRng([]),
            )
            self.assertEqual(selected.player_index, 3)


if __name__ == "__main__":
    unittest.main()
