"""Original bounded child constructor RNG accounting, not real gameplay."""
import itertools
import unittest

from original_first_human_nested_random import (
    CHILD_CONSTRUCTOR_SITES,
    NESTED_BOUNDED_RNG_SITE,
    NESTED_BOUNDED_RNG_BOUND,
    ORIGINAL_RAW_RAND_SITE,
    OriginalNestedRandomSourceError,
    project_original_first_human_nested_random,
)


class OriginalFirstHumanNestedRandomTests(unittest.TestCase):
    def test_three_successful_nested_allocations_require_three_source_crt_draws(self):
        receipt = project_original_first_human_nested_random(
            outer_allocation_succeeded=True,
            child_allocations_succeeded=(True, True, True),
        )
        self.assertEqual(receipt.reached_child_constructor_sites, CHILD_CONSTRUCTOR_SITES)
        self.assertEqual(receipt.bounded_rng_calls, 3)
        self.assertEqual(receipt.raw_shared_crt_rand_calls, 3)
        self.assertFalse(receipt.live_crt_checkpoint_verified)
        self.assertEqual(NESTED_BOUNDED_RNG_SITE, 0x60CE38)
        self.assertEqual(NESTED_BOUNDED_RNG_BOUND, 20)
        self.assertEqual(ORIGINAL_RAW_RAND_SITE, 0x66951C)

    def test_each_allocation_branch_is_counted_without_guessing_outcome(self):
        for bits in itertools.product((False, True), repeat=3):
            with self.subTest(allocations=bits):
                receipt = project_original_first_human_nested_random(
                    outer_allocation_succeeded=True, child_allocations_succeeded=bits
                )
                selected = tuple(site for site, flag in zip(CHILD_CONSTRUCTOR_SITES, bits) if flag)
                self.assertEqual(receipt.reached_child_constructor_sites, selected)
                self.assertEqual(receipt.raw_shared_crt_rand_calls, sum(bits))
                self.assertFalse(receipt.live_crt_checkpoint_verified)

    def test_failed_outer_source_allocation_skips_nested_constructor(self):
        receipt = project_original_first_human_nested_random(
            outer_allocation_succeeded=False,
            child_allocations_succeeded=(False, False, False),
        )
        self.assertEqual(receipt.reached_child_constructor_sites, ())
        self.assertEqual(receipt.bounded_rng_calls, 0)
        self.assertEqual(receipt.raw_shared_crt_rand_calls, 0)

    def test_malformed_or_contradictory_flags_fail_closed(self):
        for outer in (None, 1, 0, "yes"):
            with self.subTest(outer=outer), self.assertRaises(OriginalNestedRandomSourceError):
                project_original_first_human_nested_random(
                    outer_allocation_succeeded=outer,
                    child_allocations_succeeded=(True, True, True),
                )
        for children in (None, [True]*3, (), (True, False), (True, False, 1),
                         (True, False, True, False), (True, False, "yes")):
            with self.subTest(children=children), self.assertRaises(OriginalNestedRandomSourceError):
                project_original_first_human_nested_random(
                    outer_allocation_succeeded=True, child_allocations_succeeded=children
                )
        with self.assertRaises(OriginalNestedRandomSourceError):
            project_original_first_human_nested_random(
                outer_allocation_succeeded=False,
                child_allocations_succeeded=(False, True, False),
            )


if __name__ == "__main__":
    unittest.main()
