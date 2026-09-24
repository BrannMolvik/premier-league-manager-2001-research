import unittest
from dataclasses import dataclass

from match_lineup import (
    AI_FORMATIONS,
    BENCH_GROUP_ORDER,
    lineup_group_for_role,
    select_ai_lineup_core,
)


@dataclass(frozen=True)
class Player:
    player_index: int
    skills: tuple[int, ...]
    preferred_positions: tuple[int, int, int]
    form_state: int = 2


def player(index: int, role: int, value: int = 100) -> Player:
    return Player(
        player_index=index,
        skills=(value,) * 17,
        preferred_positions=(role, 0, 0),
    )


def formation_zero_starters(value: int = 255) -> list[Player]:
    return [
        player(index, slot.role, value)
        for index, slot in enumerate(AI_FORMATIONS[0])
    ]


class FormationTableTests(unittest.TestCase):
    def test_exact_shape_and_known_auxiliary_slots(self):
        self.assertEqual(len(AI_FORMATIONS), 21)
        self.assertTrue(all(len(formation) == 11 for formation in AI_FORMATIONS))
        self.assertEqual(
            [(slot.role, slot.auxiliary_code) for slot in AI_FORMATIONS[0]],
            [
                (19, 1), (19, 0), (11, 0), (10, 0), (12, 1), (12, 0),
                (4, 1), (4, 0), (3, 0), (2, 0), (1, 0),
            ],
        )

    def test_exact_runtime_role_groups(self):
        self.assertEqual(lineup_group_for_role(1), 3)
        for role in range(2, 8):
            self.assertEqual(lineup_group_for_role(role), 0)
        for role in range(8, 16):
            self.assertEqual(lineup_group_for_role(role), 1)
        self.assertEqual(lineup_group_for_role(16), 255)
        self.assertEqual(lineup_group_for_role(17), 255)
        self.assertEqual(lineup_group_for_role(18), 2)
        self.assertEqual(lineup_group_for_role(19), 2)
        self.assertEqual(BENCH_GROUP_ORDER, (1, 2, 0, 3))


class StarterSelectionTests(unittest.TestCase):
    def test_preferred_match_pass_beats_stronger_out_of_position_player(self):
        weak_natural = player(1, 19, 40)
        strong_midfielder = player(2, 12, 255)

        result = select_ai_lineup_core(
            [weak_natural, strong_midfielder],
            formation_id=0,
            substitute_quota=0,
        )

        self.assertEqual(result.starters[0].player_index, 1)
        self.assertEqual(result.starters[0].role, 19)
        self.assertEqual(result.starters[0].auxiliary_code, 1)

    def test_second_pass_fills_slot_from_out_of_position_player(self):
        subject = player(7, 16, 180)

        result = select_ai_lineup_core(
            [subject],
            formation_id=0,
            substitute_quota=0,
        )

        self.assertEqual(len(result.starters), 1)
        self.assertEqual(result.starters[0].player_index, 7)
        self.assertEqual(result.starters[0].role, 19)
        self.assertNotIn(0, result.unfilled_slot_indices)

    def test_strict_greater_tie_keeps_earlier_roster_player(self):
        first = player(10, 19, 120)
        second = player(11, 19, 120)

        result = select_ai_lineup_core(
            [first, second],
            formation_id=0,
            substitute_quota=0,
        )

        self.assertEqual(result.starters[0].player_index, 10)
        self.assertEqual(result.starters[1].player_index, 11)

    def test_external_eligibility_boundary_is_respected(self):
        unavailable = player(1, 19, 255)
        available = player(2, 19, 80)

        result = select_ai_lineup_core(
            [unavailable, available],
            formation_id=0,
            substitute_quota=0,
            eligible=lambda candidate: candidate.player_index != 1,
        )

        self.assertEqual(result.starters[0].player_index, 2)

    def test_external_stateful_restriction_boundary_is_respected(self):
        first = player(1, 19, 200)
        blocked = player(2, 19, 255)

        def allow(candidate, selected):
            return candidate.player_index != 2 or len(selected) >= 1

        result = select_ai_lineup_core(
            [first, blocked],
            formation_id=0,
            substitute_quota=0,
            starter_allowed=allow,
        )

        self.assertEqual(result.starters[0].player_index, 1)
        self.assertEqual(result.starters[1].player_index, 2)


class BenchSelectionTests(unittest.TestCase):
    def test_ranked_bench_categories_use_original_order(self):
        starters = formation_zero_starters()
        base = len(starters)
        goalkeeper = player(base + 0, 1, 100)
        defender = player(base + 1, 4, 100)
        forward = player(base + 2, 19, 100)
        midfielder = player(base + 3, 12, 100)

        result = select_ai_lineup_core(
            starters + [goalkeeper, defender, forward, midfielder],
            formation_id=0,
            substitute_quota=4,
        )

        self.assertEqual(
            result.substitutes,
            (
                midfielder.player_index,
                forward.player_index,
                defender.player_index,
                goalkeeper.player_index,
            ),
        )

    def test_overflow_is_roster_order_and_excludes_extra_goalkeepers(self):
        starters = formation_zero_starters()
        base = len(starters)

        # One candidate per ranked category. The stronger goalkeeper wins the
        # category-3 pass; the other goalkeeper must not be used by overflow.
        extra_goalkeeper = player(base + 0, 1, 80)
        overflow_first = player(base + 1, 16, 70)
        ranked_midfielder = player(base + 2, 12, 100)
        ranked_forward = player(base + 3, 19, 100)
        ranked_defender = player(base + 4, 4, 100)
        ranked_goalkeeper = player(base + 5, 1, 120)
        overflow_second = player(base + 6, 17, 70)

        result = select_ai_lineup_core(
            starters + [
                extra_goalkeeper,
                overflow_first,
                ranked_midfielder,
                ranked_forward,
                ranked_defender,
                ranked_goalkeeper,
                overflow_second,
            ],
            formation_id=0,
            substitute_quota=6,
        )

        self.assertEqual(
            result.substitutes[:4],
            (
                ranked_midfielder.player_index,
                ranked_forward.player_index,
                ranked_defender.player_index,
                ranked_goalkeeper.player_index,
            ),
        )
        self.assertEqual(
            result.substitutes[4:],
            (overflow_first.player_index, overflow_second.player_index),
        )
        self.assertNotIn(extra_goalkeeper.player_index, result.substitutes)

    def test_bench_ranking_uses_best_preferred_role_not_roster_order(self):
        starters = formation_zero_starters()
        base = len(starters)
        weaker = player(base, 12, 70)
        stronger = player(base + 1, 12, 180)

        result = select_ai_lineup_core(
            starters + [weaker, stronger],
            formation_id=0,
            substitute_quota=1,
        )

        self.assertEqual(result.substitutes, (stronger.player_index,))


if __name__ == "__main__":
    unittest.main()
