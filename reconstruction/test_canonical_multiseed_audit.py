"""Tests for the canonical Gate-16 multi-seed orchestration wrapper."""
import unittest

from canonical_multiseed_audit import (
    CanonicalMultiSeedAuditError,
    DEFAULT_CANONICAL_SEEDS,
    run_canonical_multiseed_audit,
)


def fake_report(seed: int, rollovers: int) -> dict:
    return {
        "player_seed": int(seed),
        "rollover_count": int(rollovers),
        "snapshots": [{"cycle": cycle} for cycle in range(int(rollovers))],
        "fresh_state_shapes": [[380, 380, 10, 10, 1, 1, 1, 1]]
        * int(rollovers),
    }


class CanonicalMultiSeedAuditTests(unittest.TestCase):
    def test_runs_requested_seeds_in_order_with_one_canonical_runner_per_seed(self):
        calls = []

        def runner(game_dir, *, player_seed, rollover_count, max_days_per_season):
            calls.append(
                (
                    str(game_dir),
                    player_seed,
                    rollover_count,
                    max_days_per_season,
                )
            )
            return fake_report(player_seed, rollover_count)

        report = run_canonical_multiseed_audit(
            "/canonical",
            player_seeds=(1, 2, 0x12345678),
            rollover_count=3,
            max_days_per_season=420,
            canonical_runner=runner,
        )

        self.assertEqual(report["player_seeds"], [1, 2, 0x12345678])
        self.assertEqual(report["seed_count"], 3)
        self.assertTrue(report["all_seeds_passed"])
        self.assertEqual(len(report["reports"]), 3)
        self.assertEqual(
            calls,
            [
                ("/canonical", 1, 3, 420),
                ("/canonical", 2, 3, 420),
                ("/canonical", 0x12345678, 3, 420),
            ],
        )

    def test_default_seed_set_extends_existing_seed_one_evidence(self):
        self.assertEqual(DEFAULT_CANONICAL_SEEDS, (1, 2, 0x12345678))

    def test_signed_seed_inputs_are_normalized_to_uint32(self):
        seen = []

        def runner(_game_dir, *, player_seed, rollover_count, **_kwargs):
            seen.append(player_seed)
            return fake_report(player_seed, rollover_count)

        report = run_canonical_multiseed_audit(
            "/canonical",
            player_seeds=(-1, 1),
            canonical_runner=runner,
        )

        self.assertEqual(seen, [0xFFFFFFFF, 1])
        self.assertEqual(report["player_seeds"], [0xFFFFFFFF, 1])

    def test_duplicate_or_single_seed_requests_fail_before_execution(self):
        calls = []

        def runner(*_args, **_kwargs):
            calls.append(True)
            raise AssertionError("runner must not be called")

        with self.assertRaisesRegex(ValueError, "at least two seeds"):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1,),
                canonical_runner=runner,
            )
        with self.assertRaisesRegex(ValueError, "must be unique"):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 1),
                canonical_runner=runner,
            )
        self.assertEqual(calls, [])

    def test_first_failing_seed_aborts_without_false_combined_success(self):
        calls = []

        def runner(_game_dir, *, player_seed, rollover_count, **_kwargs):
            calls.append(player_seed)
            if player_seed == 2:
                raise RuntimeError("canonical failure")
            return fake_report(player_seed, rollover_count)

        with self.assertRaisesRegex(
            CanonicalMultiSeedAuditError,
            "0x00000002",
        ):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 2, 3),
                canonical_runner=runner,
            )

        self.assertEqual(calls, [1, 2])

    def test_mismatched_seed_or_incomplete_snapshots_fail_closed(self):
        def wrong_seed(_game_dir, *, player_seed, rollover_count, **_kwargs):
            return fake_report(player_seed + 1, rollover_count)

        with self.assertRaisesRegex(
            CanonicalMultiSeedAuditError,
            "mismatched player seed",
        ):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 2),
                canonical_runner=wrong_seed,
            )

        def short_report(_game_dir, *, player_seed, rollover_count, **_kwargs):
            report = fake_report(player_seed, rollover_count)
            report["snapshots"] = report["snapshots"][:-1]
            return report

        with self.assertRaisesRegex(
            CanonicalMultiSeedAuditError,
            "incomplete snapshots",
        ):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 2),
                canonical_runner=short_report,
            )

    def test_invalid_rollover_and_day_bounds_fail_before_execution(self):
        with self.assertRaisesRegex(ValueError, "at least two rollovers"):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 2),
                rollover_count=1,
            )
        with self.assertRaisesRegex(ValueError, "must be positive"):
            run_canonical_multiseed_audit(
                "/canonical",
                player_seeds=(1, 2),
                max_days_per_season=0,
            )


if __name__ == "__main__":
    unittest.main()
