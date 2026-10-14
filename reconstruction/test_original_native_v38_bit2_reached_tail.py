"""Source-exact 0x513659 match v38 bit2 reached callback gating."""
from __future__ import annotations

import unittest
from dataclasses import replace
from struct import pack_into

from original_native_v38_score_stage import (
    source_original_513570_pre_rng_score_stage,
)
from original_native_v38_bit2_reached_tail import (
    OriginalV38Bit2TailError,
    source_original_513570_bit2_reached_tail,
)


def native_match(*, bit2=True, linked_ptr=0):
    raw=bytearray(0x5C)
    pack_into("<I",raw,0,0x7C9D9C)
    pack_into("<I",raw,0x44,4 if bit2 else 0)
    pack_into("<I",raw,0x54,linked_ptr)
    return bytes(raw)


def original_context(*,primary=1,secondary=0,head=0,d14=0):
    raw=bytearray(0xD52)
    pack_into("<I",raw,0xD0C,primary)
    pack_into("<I",raw,0xD10,secondary)
    pack_into("<I",raw,0xB60,head)
    pack_into("<I",raw,0xD14,d14)
    return bytes(raw)


def prepare(*,bit2=True,primary=1,secondary=0,d14=0,linked_ptr=0):
    context=original_context(primary=primary,secondary=secondary,d14=d14)
    stage=source_original_513570_pre_rng_score_stage(
        original_match_record=native_match(bit2=bit2,linked_ptr=linked_ptr),
        original_context=context,original_linked_events={})
    return stage,context


class OriginalV38Bit2ReachedTailTests(unittest.TestCase):
    def run_stage(self,stage,context,**kwargs):
        return source_original_513570_bit2_reached_tail(
            original_stage=stage,original_context=context,**kwargs)

    def test_no_bit2_never_calls_virtual_or_rng(self):
        stage,ctx=prepare(bit2=False)
        result=self.run_stage(stage,ctx)
        self.assertFalse(result.bit2_branch_entered)
        self.assertFalse(result.original_rng_called)
        self.assertIsNone(result.original_composite_getters_equal)
        self.assertEqual(result.projected_match_record_after_bit2,
                         stage.projected_match_record)
        self.assertFalse(result.native_match_completion_proven)
        with self.assertRaises(OriginalV38Bit2TailError):
            self.run_stage(stage,ctx,original_reached_513f00_eax=0)

    def test_zero_counters_skip_bit2_even_when_flag_set(self):
        stage,ctx=prepare(primary=0,secondary=0)
        result=self.run_stage(stage,ctx)
        self.assertFalse(result.bit2_branch_entered)
        self.assertFalse(result.original_rng_called)

    def test_composite_mismatch_skips_optional_getters_and_rng(self):
        stage,ctx=prepare()
        result=self.run_stage(stage,ctx,
            original_reached_513f00_eax=5,original_reached_513ed0_eax=6)
        self.assertTrue(result.bit2_branch_entered)
        self.assertFalse(result.original_composite_getters_equal)
        self.assertFalse(result.original_rng_called)
        self.assertEqual(result.projected_match_record_after_bit2,
                         stage.projected_match_record)
        with self.assertRaisesRegex(OriginalV38Bit2TailError,"skips linked"):
            self.run_stage(stage,ctx,original_reached_513f00_eax=5,
                original_reached_513ed0_eax=6,
                original_reached_64d540_2_eax=1)

    def test_no_d14_equal_helpers_rng_zero_increments_second_counter(self):
        stage,ctx=prepare()
        result=self.run_stage(stage,ctx,
            original_reached_513f00_eax=0xffffffff,
            original_reached_513ed0_eax=0xffffffff,
            original_reached_64d540_2_eax=0)
        self.assertTrue(result.original_composite_getters_equal)
        self.assertIsNone(result.optional_linked_owner_getters_equal)
        self.assertTrue(result.original_rng_called)
        self.assertEqual(result.projected_match_record_after_bit2[0x5A:0x5C],
                         b"\x00\x01")

    def test_no_d14_equal_helpers_rng_nonzero_increments_first_counter(self):
        stage,ctx=prepare()
        result=self.run_stage(stage,ctx,
            original_reached_513f00_eax=3,
            original_reached_513ed0_eax=3,
            original_reached_64d540_2_eax=1)
        self.assertTrue(result.original_rng_called)
        self.assertEqual(result.projected_match_record_after_bit2[0x5A:0x5C],
                         b"\x01\x00")

    def test_optional_v4c_owner_gate_mismatch_skips_rng(self):
        stage,ctx=prepare(d14=7,linked_ptr=0x1234)
        result=self.run_stage(stage,ctx,
            original_reached_513f00_eax=0,
            original_reached_513ed0_eax=0,
            original_reached_linked_v4c_eax=9,
            original_reached_self_v4c_eax=10)
        self.assertFalse(result.optional_linked_owner_getters_equal)
        self.assertFalse(result.original_rng_called)
        with self.assertRaisesRegex(OriginalV38Bit2TailError,"skips RNG"):
            self.run_stage(stage,ctx,
                original_reached_513f00_eax=0,
                original_reached_513ed0_eax=0,
                original_reached_linked_v4c_eax=9,
                original_reached_self_v4c_eax=10,
                original_reached_64d540_2_eax=1)

    def test_optional_v4c_owner_gate_equal_calls_rng(self):
        stage,ctx=prepare(d14=1,linked_ptr=0x1111)
        result=self.run_stage(stage,ctx,
            original_reached_513f00_eax=0xFFFFFFFE,
            original_reached_513ed0_eax=0xFFFFFFFE,
            original_reached_linked_v4c_eax=8,
            original_reached_self_v4c_eax=8,
            original_reached_64d540_2_eax=0)
        self.assertTrue(result.optional_linked_owner_getters_equal)
        self.assertTrue(result.original_rng_called)
        self.assertEqual(result.projected_match_record_after_bit2[0x5B],1)

    def test_optional_owner_null_fails_before_virtual_method(self):
        stage,ctx=prepare(d14=1,linked_ptr=0)
        with self.assertRaisesRegex(OriginalV38Bit2TailError,"pointer is null"):
            self.run_stage(stage,ctx,
                original_reached_513f00_eax=0,original_reached_513ed0_eax=0)

    def test_reached_callback_inputs_must_match_executed_branches(self):
        stage,ctx=prepare()
        invalid=(
            {},
            {"original_reached_513f00_eax":False,
             "original_reached_513ed0_eax":0},
            {"original_reached_513f00_eax":0,
             "original_reached_513ed0_eax":0},
            {"original_reached_513f00_eax":0,
             "original_reached_513ed0_eax":0,
             "original_reached_64d540_2_eax":True},
            {"original_reached_513f00_eax":0,
             "original_reached_513ed0_eax":0,
             "original_reached_linked_v4c_eax":0,
             "original_reached_self_v4c_eax":0,
             "original_reached_64d540_2_eax":1},
        )
        for row in invalid:
            with self.subTest(row=row):
                with self.assertRaises(OriginalV38Bit2TailError):
                    self.run_stage(stage,ctx,**row)

    def test_original_context_mismatch_and_forged_gate_fail(self):
        stage,ctx=prepare()
        moved=bytearray(ctx)
        pack_into("<I",moved,0xD0C,2)
        with self.assertRaisesRegex(OriginalV38Bit2TailError,"counts changed"):
            self.run_stage(stage,bytes(moved))
        with self.assertRaises(OriginalV38Bit2TailError):
            self.run_stage(replace(stage,
                requires_513659_bit2_resolution=False),ctx)
        with self.assertRaises(OriginalV38Bit2TailError):
            self.run_stage(stage,bytes(0xD51))
        with self.assertRaises(OriginalV38Bit2TailError):
            self.run_stage(stage,bytearray(ctx))
        with self.assertRaises(OriginalV38Bit2TailError):
            source_original_513570_bit2_reached_tail(
                original_stage=object(),original_context=ctx)


if __name__=="__main__":
    unittest.main()
