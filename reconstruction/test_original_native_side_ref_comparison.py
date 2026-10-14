"""Original 0x4F2830 SideRef direct returned get-v0/cached equality."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from original_native_side_ref_comparison import (
    OriginalNativeSideRefCompareSourceError,
    source_original_reached_side_ref_compare_4f2830,
    source_original_leaguematch_virtual04_510a40_from_reached_comparisons,
    source_original_leaguematch_virtual00_510a80_from_reached_v4,
    source_original_sidereference_virtual0_dispatch_4f28a0,
    SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_SUBTYPE_BRANCHES,
    SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_JUMPTABLE_VA,
    source_original_no_mutating_sidereference_pair_compare_4f2830,
    source_original_match_embedded_sidereference_virtual0_510320,
    SOURCE_ORIGINAL_MATCH_EMBEDDED_SIDEREF_VTABLE_VA,
)
from original_leaguematch_native_process_owners import SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS


def native_side(*,cache=0,owner=0,type_code=0,selector=0,embedded_vtable=0x7C4D50):
    raw=bytearray(0x14)
    pack_into("<I",raw,0,embedded_vtable)
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

    def test_native_leaguematch_v4_short_circuits_side_1_after_side_0_match(self):
        import struct
        for vtable in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            native=struct.pack("<I",vtable)
            yes=compared()
            no=compared(original_reached_left_virtual0_eax=0)
            with self.subTest(vtable=hex(vtable)):
                r=source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
                    original_native_match_record=native,
                    original_first_reached_4f2830_receipt=yes,
                    original_second_reached_4f2830_receipt=None)
                self.assertEqual(r.source_original_method_eax,1)
                self.assertFalse(r.source_second_side_comparison_was_reached)
                with self.assertRaises(OriginalNativeSideRefCompareSourceError):
                    source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
                        original_native_match_record=native,
                        original_first_reached_4f2830_receipt=yes,
                        original_second_reached_4f2830_receipt=no)
                second=source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
                    original_native_match_record=native,
                    original_first_reached_4f2830_receipt=no,
                    original_second_reached_4f2830_receipt=yes)
                self.assertEqual(second.source_original_method_eax,1)
                self.assertTrue(second.source_second_side_comparison_was_reached)
                none=source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
                    original_native_match_record=native,
                    original_first_reached_4f2830_receipt=no,
                    original_second_reached_4f2830_receipt=no)
                self.assertEqual(none.source_original_method_eax,0)

    def test_native_v0_two_comparison_v4_calls_respect_actual_return_order(self):
        for vtable in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            native=pack("<I",vtable)
            for first,second,wanted in ((1,None,1),(0,1,1),(0,0,0),
                                        (0,0xFFFFFFFF,1),(123,None,1)):
                with self.subTest(vtable=hex(vtable),first=first,second=second):
                    self.assertEqual(source_original_leaguematch_virtual00_510a80_from_reached_v4(
                        original_native_match_record=native,
                        original_first_reached_comparison_v4_eax=first,
                        original_second_reached_comparison_v4_eax=second),wanted)
            for first,second in ((1,1),(0,None),(True,0),(-1,0),(0,True)):
                with self.subTest(vtable=hex(vtable),first=first,second=second):
                    with self.assertRaises(OriginalNativeSideRefCompareSourceError):
                        source_original_leaguematch_virtual00_510a80_from_reached_v4(
                            original_native_match_record=native,
                            original_first_reached_comparison_v4_eax=first,
                            original_second_reached_comparison_v4_eax=second)
        yes=compared()
        no=compared(original_reached_left_virtual0_eax=0)
        for change in (
            {"original_native_match_record":pack("<I",0xDEADBEEF)},
            {"original_native_match_record":bytearray(pack("<I",0x7C4C24))},
            {"original_first_reached_4f2830_receipt":None},
            {"original_second_reached_4f2830_receipt":None},
        ):
            original=dict(original_native_match_record=pack("<I",0x7C4C24),
                          original_first_reached_4f2830_receipt=no,
                          original_second_reached_4f2830_receipt=yes)
            with self.subTest(change=str(change)),self.assertRaises(
                OriginalNativeSideRefCompareSourceError):
                source_original_leaguematch_virtual04_510a40_from_reached_comparisons(
                    **(original|change))


    def test_original_sidereference_cached_result_bypasses_type_callbacks(self):
        for kind in (0,1,2,3,4,5,0xFFFF):
            with self.subTest(kind=kind):
                r=source_original_sidereference_virtual0_dispatch_4f28a0(
                    original_native_side_record_before_getter=native_side(
                        cache=0xCAFEBABE,type_code=kind,owner=0xDEADBEEF))
                self.assertEqual(r.source_return_without_mutating_getter,0xCAFEBABE)
                self.assertIsNone(r.source_dispatch_branch_va)
                self.assertFalse(r.source_unresolved_callback_required)

    def test_original_sidereference_zero_cache_4_way_type_handler_or_zero_return(self):
        expected={1:0x4F28E0,2:0x4F290B,3:0x4F2992,4:0x4F2A78}
        self.assertEqual(SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_SUBTYPE_BRANCHES,expected)
        for kind in (0,1,2,3,4,5,0xFFFF):
            with self.subTest(kind=kind):
                r=source_original_sidereference_virtual0_dispatch_4f28a0(
                    original_native_side_record_before_getter=native_side(
                        cache=0,owner=0x11220000,type_code=kind,selector=3))
                self.assertEqual(r.source_dispatch_branch_va,expected.get(kind))
                self.assertEqual(r.source_unresolved_callback_required,kind in expected)
                self.assertEqual(r.source_return_without_mutating_getter,
                                 None if kind in expected else 0)

    def test_original_sidereference_getter_disallows_incomplete_or_mutable_native_input(self):
        for bad in (None,bytes(15),bytearray(16),"native",{"type":1}):
            with self.subTest(bad=str(bad)[:80]),self.assertRaises(
                OriginalNativeSideRefCompareSourceError):
                source_original_sidereference_virtual0_dispatch_4f28a0(
                    original_native_side_record_before_getter=bad)


    def test_source_exact_cached_side_pair_without_unreached_mutating_getter(self):
        # These original SideRef records contain real source-typed cached
        # native pointers, NOT Python club IDs.
        for left,right,want in (
            (native_side(cache=0x1111,type_code=0),native_side(cache=0x1111,type_code=0),True),
            (native_side(cache=0x1111,type_code=1),native_side(cache=0x2222,type_code=4),False),
            (native_side(cache=0x1111,type_code=1),native_side(cache=0,type_code=0),False),
            (native_side(cache=0,type_code=0),native_side(cache=0,type_code=0),True),
            (native_side(cache=0,type_code=5),native_side(cache=0,type_code=5),True),
            (native_side(cache=0,type_code=5),native_side(cache=0,type_code=0),False),
            (native_side(cache=0,type_code=0,owner=0x2121,selector=2),
             native_side(cache=0,type_code=0,owner=0x2121,selector=2),True),
            (native_side(cache=0,type_code=0,owner=0x2121,selector=2),
             native_side(cache=0,type_code=0,owner=0x2121,selector=3),False),
        ):
            with self.subTest(left=left.hex(),right=right.hex()):
                r=source_original_no_mutating_sidereference_pair_compare_4f2830(
                    original_left_side_record=left,original_right_side_record=right)
                self.assertEqual(r.source_original_v4_or_v0_comparison_result,want)

    def test_original_unresolved_mutating_getter_is_not_fake_direct_cache(self):
        for subtype in (1,2,3,4):
            for cache_other in (0,0x1111):
                with self.subTest(type=subtype,other=cache_other):
                    with self.assertRaises(OriginalNativeSideRefCompareSourceError):
                        source_original_no_mutating_sidereference_pair_compare_4f2830(
                            original_left_side_record=native_side(cache=0,type_code=subtype),
                            original_right_side_record=native_side(cache=cache_other,type_code=0))
                    with self.assertRaises(OriginalNativeSideRefCompareSourceError):
                        source_original_no_mutating_sidereference_pair_compare_4f2830(
                            original_left_side_record=native_side(cache=cache_other,type_code=0),
                            original_right_side_record=native_side(cache=0,type_code=subtype))


    def test_original_match_embedded_getter_510320_caches_or_delegates_exactly(self):
        self.assertEqual(SOURCE_ORIGINAL_MATCH_EMBEDDED_SIDEREF_VTABLE_VA,0x7C4D50)
        for kind in (0,1,2,3,4,0xFFFF):
            got=source_original_match_embedded_sidereference_virtual0_510320(
                original_match_embedded_sidereference_record=native_side(
                    type_code=kind,cache=0xABC000))
            with self.subTest(kind=kind):
                self.assertEqual(got.source_original_virtual0_method_va,0x510320)
                self.assertEqual(got.source_return_without_mutating_getter,0xABC000)
                self.assertFalse(got.source_delegated_to_4f28a0)
                self.assertFalse(got.source_original_registration_path_unresolved)
        for kind in (0,1,2,3,4,5,0xFFFF):
            got=source_original_match_embedded_sidereference_virtual0_510320(
                original_match_embedded_sidereference_record=native_side(
                    type_code=kind,cache=0))
            with self.subTest(kind=kind):
                self.assertTrue(got.source_delegated_to_4f28a0)
                self.assertEqual(got.source_original_subtype_callback_owner,
                                 {1:0x4F28E0,2:0x4F290B,3:0x4F2992,4:0x4F2A78}.get(kind))
                self.assertEqual(got.source_original_registration_path_unresolved,
                                 kind in (1,2,3,4))
                self.assertEqual(got.source_return_without_mutating_getter,
                                 None if kind in (1,2,3,4) else 0)

    def test_original_match_embedded_getter_rejects_wrong_vtable_and_incomplete_record(self):
        for bad in (native_side(embedded_vtable=0x7C4D60),
                    native_side(embedded_vtable=0), bytes(0x13),
                    bytearray(native_side()), None):
            with self.subTest(bad=str(bad)[:50]),self.assertRaises(
                OriginalNativeSideRefCompareSourceError):
                source_original_match_embedded_sidereference_virtual0_510320(
                    original_match_embedded_sidereference_record=bad)
        with self.assertRaises(OriginalNativeSideRefCompareSourceError):
            source_original_no_mutating_sidereference_pair_compare_4f2830(
                original_left_side_record=native_side(embedded_vtable=0x7C4D60),
                original_right_side_record=native_side())


    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner original private PE not accessible in hosted CI")
    def test_original_private_pe_4f2830_callback_branches_and_native_vtables(self):
        from gate13_button_source_trace import OriginalPE32
        original=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x510440:"89 76 24",
            0x510446:"c7 46 14 50 4d 7c 00",
            0x5104AB:"89 76 38",
            0x5104B1:"c7 46 28 50 4d 7c 00",
            0x510323:"8b 46 04",
            0x51032A:"e8 71 25 fe ff",
            0x510333:"8b 46 10",
            0x510337:"e8 a4 3c 00 00",
            0x51034E:"e8 ad ff ff ff",
            0x510355:"e8 e6 5b 10 00",
            0x51035D:"e8 ee 0f 00 00",
            0x510373:"89 81 b0 01 00 00",
            0x510379:"8b 46 04",
            0x4F28BE:"8b 46 04",
            0x4F28C3:"0f 85 64 02 00 00",
            0x4F28CB:"66 8b 46 0c",
            0x4F28D0:"83 f8 03",
            0x4F28D9:"ff 24 85 44 2b 4f 00",
            0x4F28E5:"ff 50 44",
            0x4F290E:"e8 ad 74 00 00",
            0x4F299B:"e8 20 74 00 00",
            0x4F2A7B:"e8 20 84 00 00",
            0x4F2B2A:"89 46 04",
            0x4F2B2D:"8b 46 04",
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
        self.assertEqual(original.read(0x7C4D50,4),pack("<I",0x510320))
        self.assertEqual(original.read(0x7C4D60,4),pack("<I",0x4F28A0))
        self.assertEqual(SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_JUMPTABLE_VA,0x4F2B44)
        for subtype,va in SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_SUBTYPE_BRANCHES.items():
            self.assertEqual(original.read(SOURCE_ORIGINAL_SIDEREF_VIRTUAL0_JUMPTABLE_VA+4*(subtype-1),4),pack("<I",va))
        for vtable in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS:
            self.assertEqual(original.read(vtable,4),pack("<I",0x510A80))
            self.assertEqual(original.read(vtable+4,4),pack("<I",0x510A40))


if __name__=="__main__":
    unittest.main()
