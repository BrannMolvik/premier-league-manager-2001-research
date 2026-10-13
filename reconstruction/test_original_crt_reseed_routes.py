"""Source-only explicit CRT reseeding, no original game runtime witness."""
import unittest
from match_schedule import MsvcCrtRng
from original_crt_reseed_routes import (
    APPLICATION_CLOCK_SEED,WORLDGEN_XOR_SEED,SAVE_RAND_THEN_SEED,
    RESTORE_SERIALIZED_SEED,OriginalCrtReseedError,
    project_original_application_clock_seed,project_original_worldgen_xor_seed,
    project_original_save_rand_then_seed,project_original_restore_serialized_seed,
)

class OriginalCrtReseedTests(unittest.TestCase):
    def test_actual_source_save_path_consumes_one_raw_rand_then_reseeds(self):
        original = MsvcCrtRng(42)
        reference = MsvcCrtRng(42)
        expected = reference.rand15()
        receipt = project_original_save_rand_then_seed(original)
        self.assertEqual(receipt.native_srand_callsite,SAVE_RAND_THEN_SEED)
        self.assertEqual((receipt.state_before,receipt.seed_argument,receipt.state_after,
                          receipt.direct_raw_draws_before_seed),(42,expected,expected,1))
        self.assertFalse(receipt.actual_native_route_verified)
        reference.seed(expected)
        self.assertEqual(original.rand15(),reference.rand15())

    def test_source_worldgen_xor_supplied_seed_changes_same_owner(self):
        rng = MsvcCrtRng(500)
        receipt = project_original_worldgen_xor_seed(rng,observed_xor_seed=0xdeadbeef)
        self.assertEqual(receipt.native_srand_callsite,WORLDGEN_XOR_SEED)
        self.assertEqual((receipt.state_after,receipt.direct_raw_draws_before_seed),
                         (0xdeadbeef,0))
        self.assertEqual(rng.state,0xdeadbeef)

    def test_source_restore_read_dword_reseeds_without_extra_direct_draw(self):
        rng = MsvcCrtRng(125)
        receipt = project_original_restore_serialized_seed(
            rng,observed_serialized_seed=0xffffff00)
        self.assertEqual(receipt.native_srand_callsite,RESTORE_SERIALIZED_SEED)
        self.assertEqual(receipt.direct_raw_draws_before_seed,0)
        self.assertEqual(rng.state,0xffffff00)

    def test_original_startup_clock_seed_must_be_observed_not_guessed(self):
        rng = MsvcCrtRng(1)
        receipt = project_original_application_clock_seed(
            rng,observed_time32_seconds=1760000000)
        self.assertEqual(receipt.native_srand_callsite,APPLICATION_CLOCK_SEED)
        self.assertEqual(rng.state,1760000000)
        self.assertFalse(receipt.actual_native_route_verified)
        for invalid in (-1,0x80000000,True,None,1.0):
            with self.subTest(invalid=invalid):
                state=rng.state
                with self.assertRaises(OriginalCrtReseedError):
                    project_original_application_clock_seed(
                        rng,observed_time32_seconds=invalid)
                self.assertEqual(rng.state,state)

    def test_bad_source_values_and_wrong_crt_owners_fail_without_mutation(self):
        for bad in (None,True,-1,0x100000000,1.2,"123"):
            rng=MsvcCrtRng(123)
            with self.subTest(bad=bad),self.assertRaises(OriginalCrtReseedError):
                project_original_worldgen_xor_seed(rng,observed_xor_seed=bad)
            self.assertEqual(rng.state,123)
            with self.assertRaises(OriginalCrtReseedError):
                project_original_restore_serialized_seed(
                    rng,observed_serialized_seed=bad)
            self.assertEqual(rng.state,123)
        for fake in (True,None,123,object()):
            with self.assertRaises(OriginalCrtReseedError):
                project_original_save_rand_then_seed(fake)

if __name__ == "__main__":
    unittest.main()
