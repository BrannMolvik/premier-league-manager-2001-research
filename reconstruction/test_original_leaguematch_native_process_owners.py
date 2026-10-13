"""Seven original LeagueMatch process callback vtables and bounded +0x34 wrapper."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack, pack_into
import unittest

from original_leaguematch_native_process_owners import (
    OriginalLeagueMatchProcessOwnerError,
    SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS,
    source_original_leaguematch_process_owners_for_native_record,
    source_original_wrapped_prepare_511120_post_base,
    source_original_leaguematch_native_virtual30_low_byte,
    source_original_match_owned_event_collection_4f3b50,
)


def native_match(vtable, *, special_owner=0x12345000, dword50=0xAABBCCDD):
    r=bytearray(0x58)
    pack_into("<I",r,0,vtable)
    pack_into("<I",r,0x50,dword50)
    pack_into("<I",r,0x54,special_owner)
    return bytes(r)


class LeagueMatchNativeProcessingOwnersTests(unittest.TestCase):
    def test_all_seven_original_vtables_have_distinct_source_callback_owners(self):
        self.assertEqual(len(SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS),7)
        wrapped=[]
        for vt, expected in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                got=source_original_leaguematch_process_owners_for_native_record(
                    original_match_record=native_match(vt))
                self.assertEqual((
                    got.virtual28_kind_va,got.virtual30_owner_va,
                    got.virtual34_prepare_va,got.virtual38_cleanup_va,
                    got.virtual3c_cleanup_va,got.virtual44_owner_va), expected)
                self.assertEqual(got.source_wrapped_prepare,expected[2]==0x511120)
                if got.source_wrapped_prepare: wrapped.append(vt)
        self.assertEqual(set(wrapped),{0x7C9D9C,0x7C9E80,0x7C9EF8,0x7C9F70})

    def test_source_wrapper_writes_special_owner_before_conditioned_d24(self):
        original=native_match(0x7C9F70,dword50=0x1234ACDC)
        true=source_original_wrapped_prepare_511120_post_base(
            original_match_record=original,
            original_base_510d60_al_nonzero=True,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=0xDEADBEEF,
            original_reached_513e70_result=0xFFFFFFFF,
        )
        self.assertEqual(true.original_written_context_dwords,
                         ((0xD28,0xDEADBEEF),(0xD2C,0xFFFFFFFF),
                          (0xD24,0x1234ACDC)))
        self.assertTrue(true.returned_al_nonzero)
        false=source_original_wrapped_prepare_511120_post_base(
            original_match_record=original,
            original_base_510d60_al_nonzero=False,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=0,
            original_reached_513e70_result=1)
        self.assertEqual(false.original_written_context_dwords,
                         ((0xD28,0),(0xD2C,1)))
        self.assertFalse(false.returned_al_nonzero)

    def test_non5_kind_skips_special_owner_even_with_nonzero_source_pointer(self):
        for kind in (0,1,2,3,4,6,0xFFFFFFFF):
            for base_result in (False,True):
                got=source_original_wrapped_prepare_511120_post_base(
                    original_match_record=native_match(0x7C9D9C,dword50=0),
                    original_base_510d60_al_nonzero=base_result,
                    original_native_kind_from_virtual28=kind)
                self.assertEqual(got.original_written_context_dwords,
                                 ((0xD24,0),) if base_result else ())
                self.assertEqual(got.returned_al_nonzero,base_result)

    def test_native_virtual30_distinguishes_unconditional_zero_and_source_kind2(self):
        primary={0x7C4C24,0x7C4CE4,0x7C9E14}
        special=set(SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS)-primary
        for vt in primary:
            with self.subTest(vtable=hex(vt)):
                record=native_match(vt)
                self.assertEqual(source_original_leaguematch_native_virtual30_low_byte(
                    original_match_record=record),0)
                self.assertEqual(source_original_match_owned_event_collection_4f3b50(
                    original_match_record=record),0x947AD8)
                with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                    source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=record,original_reached_virtual28_kind=2)
        for vt in special:
            for kind,flag,al in ((2,0,1),(2,4,0),(2,0x100,1),(3,0,0),(0,0,0)):
                with self.subTest(vtable=hex(vt),kind=kind,flag=flag):
                    record=bytearray(native_match(vt))
                    pack_into("<I",record,0x44,flag)
                    got=source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=bytes(record),
                        original_reached_virtual28_kind=kind)
                    self.assertEqual(got,al)
                    self.assertEqual(source_original_match_owned_event_collection_4f3b50(
                        original_match_record=bytes(record),
                        original_reached_virtual28_kind=kind),
                        0x947AF0 if al else 0x947AD8)
            for kind in (None,True,-1,0x100000000,"2"):
                with self.subTest(vtable=hex(vt),kind=kind),self.assertRaises(
                    OriginalLeagueMatchProcessOwnerError):
                    source_original_leaguematch_native_virtual30_low_byte(
                        original_match_record=native_match(vt),
                        original_reached_virtual28_kind=kind)
            with self.assertRaises(OriginalLeagueMatchProcessOwnerError):
                source_original_leaguematch_native_virtual30_low_byte(
                    original_match_record=native_match(vt)[:0x44],
                    original_reached_virtual28_kind=2)

    def test_original_native_unknown_inputs_are_not_inferred_or_defaulted(self):
        for record in (b"",bytes(3),bytearray(native_match(0x7C9D9C)),
                       native_match(0xDEADBEEF)):
            with self.subTest(record=str(record)[:30]),self.assertRaises(
                OriginalLeagueMatchProcessOwnerError):
                source_original_leaguematch_process_owners_for_native_record(
                    original_match_record=record)
        good=dict(
            original_match_record=native_match(0x7C9D9C),
            original_base_510d60_al_nonzero=True,
            original_native_kind_from_virtual28=5,
            original_reached_513e80_result=1,
            original_reached_513e70_result=2)
        for changes in (
            {"original_match_record":native_match(0x7C4C24)},
            {"original_match_record":native_match(0x7C9D9C,special_owner=0)},
            {"original_match_record":bytes(0x57)},
            {"original_native_kind_from_virtual28":None},
            {"original_native_kind_from_virtual28":True},
            {"original_native_kind_from_virtual28":-1},
            {"original_native_kind_from_virtual28":0x100000000},
            {"original_base_510d60_al_nonzero":1},
            {"original_reached_513e80_result":None},
            {"original_reached_513e70_result":True},
            {"original_reached_513e70_result":-1},
            {"original_native_kind_from_virtual28":4},
        ):
            with self.subTest(changes=str(changes)[:80]),self.assertRaises(
                OriginalLeagueMatchProcessOwnerError):
                source_original_wrapped_prepare_511120_post_base(**(good|changes))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "private original executable not mounted in hosted CI")
    def test_all_native_virtual_slots_and_wrapper_opcodes_match_original(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt, members in SOURCE_LEAGUEMATCH_NATIVE_METHOD_OWNERS.items():
            with self.subTest(vtable=hex(vt)):
                self.assertEqual(pe.read(vt+0x10,4),pack("<I",0x513010))
                self.assertEqual(pe.read(vt+0x18,4),pack("<I",0x6559A0))
                for off,value in zip((0x28,0x30,0x34,0x38,0x3C,0x44),members):
                    self.assertEqual(pe.read(vt+off,4),pack("<I",value))
        sites={
            0x651980:"32 c0 c3",
            0x5112C0:"56",0x5112C5:"ff 50 28",
            0x5112C8:"83 f8 02",0x5112CD:"f6 46 44 04",
            0x5112D3:"b0 01",0x5112D7:"32 c0",
            0x5130B7:"c7 84 24 6c 11 00 00 00 00 00 00",
            0x5130C2:"ff 50 34",0x5130C5:"84 c0",
            0x5130C9:"8d 54 24 08",
            0x511120:"53 56 57",0x51112A:"e8 31 fc ff ff",
            0x51112F:"8a d8",0x511135:"ff 50 28",
            0x511138:"83 f8 05",0x51113D:"8b 4e 54",
            0x511140:"e8 3b 2d 00 00",0x511145:"89 87 28 0d 00 00",
            0x51114B:"8b 4e 54",0x51114E:"e8 1d 2d 00 00",
            0x511153:"89 87 2c 0d 00 00",0x511159:"84 db",
            0x51115D:"8b 4e 50",0x511160:"89 8f 24 0d 00 00",
            0x511167:"8a c3",0x51116B:"c2 04 00",
            0x510D60:"51",0x510D73:"e8 d8 17 12 00",
            0x510D95:"8b 0d 30 75 87 00",
            0x510D9B:"89 8e 3c 0d 00 00",
        }
        for addr,hx in sites.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
