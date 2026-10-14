"""Original 0x4F2830 SideRef direct returned get-v0/cached equality."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from original_native_side_ref_comparison import (
    OriginalNativeSideRefCompareSourceError,
    source_original_reached_side_ref_compare_4f2830,
)
from original_leaguematch_native_process_owners import SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS


def native_side(*,cache=0,owner=0,type_code=0,selector=0):
    raw=bytearray(0x10)
    pack_into("<I",raw,4,cache)
    pack_into("<I",raw,8,owner)
    pack_into("<H",raw,0x0C,type_code)
    pack_into("<H",raw,0x0E,selector)
    return bytes(raw)


def compared(**change):
    args=dict(
        original_left_side_after_reached_getter=native_side(cache=0x1010),
        original_right_side_after_reached_getter=native_side(cache=0x1010),
        original_reached_left_virtual0_eax=0x1010,
        original_reached_right_virtual0_eax=0x1010,
    )
    return source_original_reached_side_ref_compare_4f2830(**(args|change))


class OriginalNativeSideRefComparisonTests(unittest.TestCase):
    def test_native_resolved_branch_uses_left_after_cache_not_return_eax(self):
        got=compared(
            original_left_side_after_reached_getter=native_side(cache=0x3030),
            original_reached_left_virtual0_eax=0x1010,
            original_reached_right_virtual0_eax=0x3030)
        self.assertTrue(got.source_original_v4_or_v0_comparison_result)
        self.assertTrue(got.source_compared_resolved_cache_pointer)
        self.assertTrue(got.source_right_getter_was_called)
        self.assertFalse(compared(
            original_left_side_after_reached_getter=native_side(cache=0x3030),
            original_reached_left_virtual0_eax=0x3030,
            original_reached_right_virtual0_eax=0x1010
        ).source_original_v4_or_v0_comparison_result)

    def test_left_resolved_right_null_can_compare_cache_to_zero(self):
        # Original bytecode does not demand right nonzero in its first branch:
        # it compares cache DWORD+4 against actual right returned EAX.
        self.assertFalse(compared(original_reached_right_virtual0_eax=0)
                         .source_original_v4_or_v0_comparison_result)
        self.assertTrue(compared(
            original_left_side_after_reached_getter=native_side(cache=0),
            original_reached_right_virtual0_eax=0)
            .source_original_v4_or_v0_comparison_result)

    def test_original_left_unresolved_right_resolved_is_false_without_identity_comparison(self):
        got=compared(original_reached_left_virtual0_eax=0)
        self.assertFalse(got.source_original_v4_or_v0_comparison_result)
        self.assertFalse(got.source_compared_resolved_cache_pointer)

    def test_both_original_virtual_getters_unresolved_compare_three_native_identity_fields(self):
        for change,expected in (
            (dict(),True),
            (dict(original_right_side_after_reached_getter=native_side(
                owner=0x7777,type_code=2,selector=4)),False),
            (dict(original_right_side_after_reached_getter=native_side(
                owner=0x7777,type_code=2,selector=3)),False),
            (dict(original_right_side_after_reached_getter=native_side(
                owner=0x7778,type_code=2,selector=4)),False),
        ):
            left=native_side(owner=0x7777,type_code=2,selector=4)
            args=dict(original_left_side_after_reached_getter=left,
                      original_right_side_after_reached_getter=left,
                      original_reached_left_virtual0_eax=0,
                      original_reached_right_virtual0_eax=0)
            args.update(change)
            with self.subTest(change=change):
                got=source_original_reached_side_ref_compare_4f2830(**args)
                self.assertEqual(got.source_original_v4_or_v0_comparison_result,expected)
                self.assertFalse(got.source_compared_resolved_cache_pointer)
                self.assertTrue(got.source_right_getter_was_called)

    def test_actual_getter_eax_and_after_bytes_must_be_present(self):
        for change in (
            dict(original_left_side_after_reached_getter=None),
            dict(original_left_side_after_reached_getter=bytearray(0x10)),
            dict(original_left_side_after_reached_getter=bytes(0x0F)),
            dict(original_right_side_after_reached_getter=b""),
            dict(original_reached_left_virtual0_eax=None),
            dict(original_reached_right_virtual0_eax=True),
            dict(original_reached_right_virtual0_eax=-1),
            dict(original_reached_left_virtual0_eax=0x100000000),
            dict(original_reached_left_virtual0_eax="0"),
        ):
            with self.subTest(change=str(change)[:90]),self.assertRaises(
                OriginalNativeSideRefCompareSourceError):
                compared(**change)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner original private PE not accessible in hosted CI")
    def test_original_private_pe_4f2830_callback_branches_and_native_vtables(self):
        from gate13_button_source_trace import OriginalPE32
        original=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x4F2836:"ff 10",
            0x4F2842:"ff 12",
            0x4F2844:"8b 56 04",
            0x4F2849:"3b d0",
            0x4F285D:"ff 12",
            0x4F286A:"66 8b 46 0c",
            0x4F286E:"66 3b 47 0c",
            0x4F287B:"8b 4e 08",
            0x4F287E:"8b 47 08",
            0x4F288C:"66 8b 56 0e",
            0x4F2892:"66 3b 57 0e",
            0x510A4C:"e8 df 1d fe ff",
            0x510A63:"e8 c8 1d fe ff",
            0x510A90:"ff 50 04",
            0x510A9F:"ff 52 04",
        }
        for address,opcode in sites.items():
            with self.subTest(va=hex(address)):
                self.assertEqual(original.read(address,len(bytes.fromhex(opcode))),
                                 bytes.fromhex(opcode))
        for vtable in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            self.assertEqual(original.read(vtable,4),pack("<I",0x510A80))
            self.assertEqual(original.read(vtable+4,4),pack("<I",0x510A40))


if __name__=="__main__":
    unittest.main()
