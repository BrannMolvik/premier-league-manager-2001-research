import unittest

from match_schedule import MsvcCrtRng
from support_staff_startup import (
    generate_fresh_support_staff_pool,
    rebuild_support_staff_candidates,
)


class FreshSupportStaffStartupTests(unittest.TestCase):
    def test_canonical_pool_and_two_initial_candidate_rebuilds(self):
        rng = MsvcCrtRng(0x61D6DFA2)

        pool = generate_fresh_support_staff_pool(rng)
        self.assertEqual(len(pool), 200)
        self.assertEqual(rng.state, 0x2992DEFA)
        self.assertTrue(all(1 <= staff.staff_type <= 16 for staff in pool))

        first = rebuild_support_staff_candidates(rng, pool)
        self.assertEqual(first.draw_count, 8)
        self.assertEqual(first.attempt_count, 7)
        self.assertEqual(
            first.selected_pool_indices,
            (110, 106, 5, 39, 74, 65, 192),
        )
        self.assertEqual(first.pruned_pool_indices, ())
        self.assertEqual(first.candidate_pool_indices, first.selected_pool_indices)
        self.assertEqual(first.state_after, 0x7B3EA402)

        second = rebuild_support_staff_candidates(
            rng,
            pool,
            first.candidate_pool_indices,
        )
        self.assertEqual(second.draw_count, 17)
        self.assertEqual(second.attempt_count, 11)
        self.assertEqual(second.pruned_pool_indices, (110, 5))
        self.assertEqual(
            second.selected_pool_indices,
            (125, 172, 172, 69, 20, 133, 129, 140, 2, 139, 45),
        )
        self.assertEqual(
            second.candidate_pool_indices,
            (106, 39, 74, 65, 192, 125, 172, 69, 20, 133, 129, 140, 2, 139, 45),
        )
        self.assertEqual(second.state_after, 0x1D1A278D)


if __name__ == "__main__":
    unittest.main()
