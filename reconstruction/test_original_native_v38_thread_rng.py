"""Original source 0x66951C/0x64D540(2) native TLS RNG tests."""
from __future__ import annotations

import unittest
from struct import pack_into

from original_native_v38_thread_rng import (
    OriginalMatchNativeRngError,
    ORIGINAL_RANDOM_FACTOR_DOUBLE,
    source_original_v38_random_two_from_reached_tls_seed,
)
from original_native_v38_bit2_reached_tail import (
    source_original_513570_bit2_reached_tail,
)
from original_native_v38_score_stage import (
    source_original_513570_pre_rng_score_stage,
)


class NativeThreadRngTwoTests(unittest.TestCase):
    def test_verified_native_lcg_seeds_and_zero_one_return(self):
        cases=(
            (0, 0x00269EC3, 38, 0),
            (0x000186A0, 0xFBC48AE3, 31684, 1),
            (0xDEADBEEF, 0xC7A1DDF6, 18337, 1),
            (0xFFFFFFFF, 0x00235AC6, 35, 0),
        )
        for seed,new,rand15,eax in cases:
            with self.subTest(seed=seed):
                r=source_original_v38_random_two_from_reached_tls_seed(
                    original_reached_tls_seed_at_offset_14=seed)
                self.assertEqual(
                    (r.original_thread_seed_after_66951c,
                     r.original_rand15_result,
                     r.original_64d540_2_return_eax),
                    (new,rand15,eax))
                self.assertFalse(r.original_thread_tls_mutated)
                self.assertFalse(r.reconstructed_match_rng_mutated)

    def test_second_random_call_uses_only_explicit_new_seed(self):
        first=source_original_v38_random_two_from_reached_tls_seed(
            original_reached_tls_seed_at_offset_14=0)
        second=source_original_v38_random_two_from_reached_tls_seed(
            original_reached_tls_seed_at_offset_14=first.original_thread_seed_after_66951c)
        self.assertEqual(second.original_thread_seed_before_66951c,
                         first.original_thread_seed_after_66951c)
        self.assertNotEqual(second.original_thread_seed_after_66951c,
                            first.original_thread_seed_after_66951c)
        self.assertEqual(ORIGINAL_RANDOM_FACTOR_DOUBLE,2**-15)

    def test_invalid_or_unmaterialized_thread_state_fails_closed(self):
        for bad in (None,True,-1,0x100000000,"0",0.0):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalMatchNativeRngError):
                    source_original_v38_random_two_from_reached_tls_seed(
                        original_reached_tls_seed_at_offset_14=bad)

    def test_native_reached_tls_result_routes_original_bit2_counter(self):
        context=bytearray(0xD52)
        pack_into("<I",context,0xD0C,1)
        match=bytearray(0x5C)
        pack_into("<I",match,0,0x7C9D9C)
        pack_into("<I",match,0x44,4)
        stage=source_original_513570_pre_rng_score_stage(
            original_match_record=bytes(match),
            original_context=bytes(context),
            original_linked_events={})
        for seed,expected in ((0,b"\x00\x01"),(100000,b"\x01\x00")):
            with self.subTest(seed=seed):
                native=source_original_v38_random_two_from_reached_tls_seed(
                    original_reached_tls_seed_at_offset_14=seed)
                tail=source_original_513570_bit2_reached_tail(
                    original_stage=stage,
                    original_context=bytes(context),
                    original_reached_513f00_eax=0,
                    original_reached_513ed0_eax=0,
                    original_reached_64d540_2_eax=native.original_64d540_2_return_eax,
                )
                self.assertEqual(
                    tail.projected_match_record_after_bit2[0x5A:0x5C],
                    expected)
                self.assertTrue(tail.original_rng_called)
                self.assertFalse(tail.native_match_completion_proven)


if __name__=="__main__":
    unittest.main()
