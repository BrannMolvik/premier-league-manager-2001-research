"""Native 5DB7D0 first-side source projection regressions; no original execution."""
from __future__ import annotations
from copy import deepcopy
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into, unpack_from
from unittest import TestCase, main

from original_match_first_side_world_write import (
    OriginalFirstSideWorldWriteError, source_original_5db7d0_first_side_world_tail,
)


def native_bytes(count=10,total=50,firstpart=7,flags=0,mean=20,mean_n=3):
    club=bytearray(0x178)
    context=bytearray(0xDA0)
    pack_into("<I",context,0xD84,total)
    pack_into("<I",context,0xD8C,firstpart)
    pack_into("<I",context,0xD90,(total-firstpart)&0xffffffff)
    for off,val in ((0x144,count),(0xE8,flags),(0x124,20),
                    (0x128,60),(0x12c,mean)):
        pack_into("<I",club,off,val)
    club[0x130]=mean_n
    for off,val in ((0x148,18),(0x14c,12),(0x150,9),(0x154,20),
                    (0x158,15),(0x15c,13),(0x160,22),(0x164,21),
                    (0x168,30),(0x16c,31),(0x170,32),(0x174,33)):
        pack_into("<I",club,off,val)
    return dict(original_first_side_before_tail=bytes(club),
                original_processing_context_at_tail=bytes(context),
                original_local_flag_at_5db7d0=0,
                original_stack_cap_div10_input_if_reached=4000)


def dw(b,off):
    return unpack_from("<I",b,off)[0]


class SourceOriginalFirstSideWorldTailTests(TestCase):
    def test_original_history_fifo_and_full_stats_tail(self):
        inp=native_bytes()
        before=deepcopy(inp)
        receipt=source_original_5db7d0_first_side_world_tail(**inp)
        after=receipt.original_first_side_after_bounded_tail
        self.assertFalse(receipt.original_5da2f0_callback_executed)
        self.assertFalse(receipt.live_game_state_updated)
        self.assertFalse(receipt.original_match_completed)
        self.assertEqual(tuple(dw(after,n) for n in
                         (0x148,0x14c,0x150,0x154,0x158,0x15c,
                          0x160,0x164,0x168,0x16c,0x170,0x174)),
                         (7,18,12,9,20,15,50,22,21,30,31,32))
        # Signed five-term weights: -15 + 80 + 40 - 30 + 500 = 575.
        self.assertEqual(dw(after,0x144),585)
        self.assertEqual((dw(after,0x124),dw(after,0x128)),(50,50))
        self.assertEqual((dw(after,0x12c),after[0x130]),(50,1))
        self.assertEqual(dw(after,0xE8)&0x380,0x380)
        self.assertEqual(inp,before)

    def test_original_lower_bound_is_not_upper_cap(self):
        inp=native_bytes()
        inp["original_stack_cap_div10_input_if_reached"]=8000
        out=source_original_5db7d0_first_side_world_tail(**inp)
        self.assertEqual(dw(out.original_first_side_after_bounded_tail,0x144),800)
        self.assertEqual(dw(out.original_first_side_after_bounded_tail,0x160),50)

    def test_zero_count_initializes_one_then_weighted_native_division(self):
        inp=native_bytes(count=0)
        out=source_original_5db7d0_first_side_world_tail(**inp)
        self.assertEqual(dw(out.original_first_side_after_bounded_tail,0x144),16101)

    def test_existing_extreme_flags_use_unsigned_comparison(self):
        inp=native_bytes(flags=0x180)
        club=bytearray(inp["original_first_side_before_tail"])
        pack_into("<I",club,0x124,60)
        pack_into("<I",club,0x128,40)
        inp["original_first_side_before_tail"]=bytes(club)
        out=source_original_5db7d0_first_side_world_tail(**inp)
        self.assertEqual((dw(out.original_first_side_after_bounded_tail,0x124),
                          dw(out.original_first_side_after_bounded_tail,0x128)),
                         (60,40))
        self.assertNotIn(0x124,out.updated_first_side_offsets)
        self.assertNotIn(0x128,out.updated_first_side_offsets)

    def test_native_668350_running_mean_and_counter(self):
        inp=native_bytes(flags=0x380,total=10,mean=20,mean_n=3)
        out=source_original_5db7d0_first_side_world_tail(**inp).original_first_side_after_bounded_tail
        self.assertEqual((dw(out,0x12c),out[0x130]),(17,4))
        self.assertEqual((dw(out,0x124),dw(out,0x128)),(20,10))

    def test_flag_one_is_native_no_write_path_without_reached_cap(self):
        inp=native_bytes()
        inp["original_local_flag_at_5db7d0"]=1
        inp["original_stack_cap_div10_input_if_reached"]=None
        result=source_original_5db7d0_first_side_world_tail(**inp)
        self.assertTrue(result.source_first_side_writes_skipped)
        self.assertEqual(result.original_first_side_after_bounded_tail,
                         inp["original_first_side_before_tail"])
        self.assertEqual(result.updated_first_side_offsets,())
        inp["original_stack_cap_div10_input_if_reached"]=10
        with self.assertRaisesRegex(OriginalFirstSideWorldWriteError,"unreachable"):
            source_original_5db7d0_first_side_world_tail(**inp)

    def test_flagged_mean_byte_255_divide_by_zero_fails_closed(self):
        with self.assertRaisesRegex(OriginalFirstSideWorldWriteError,"division"):
            source_original_5db7d0_first_side_world_tail(
                **native_bytes(flags=0x200,mean_n=255))

    def test_inconsistent_native_owner_components_cannot_commit(self):
        inp=native_bytes()
        context=bytearray(inp["original_processing_context_at_tail"])
        pack_into("<I",context,0xD90,999)
        inp["original_processing_context_at_tail"]=bytes(context)
        with self.assertRaisesRegex(OriginalFirstSideWorldWriteError,"owner components"):
            source_original_5db7d0_first_side_world_tail(**inp)

    def test_invalid_reached_source_type_and_missing_records_fail_closed(self):
        inp=native_bytes()
        for override in (
            {"original_first_side_before_tail":b""},
            {"original_processing_context_at_tail":b""},
            {"original_local_flag_at_5db7d0":True},
            {"original_local_flag_at_5db7d0":2},
            {"original_stack_cap_div10_input_if_reached":None},
            {"original_stack_cap_div10_input_if_reached":True},
            {"original_stack_cap_div10_input_if_reached":-1},
            {"original_stack_cap_div10_input_if_reached":0x100000000},
        ):
            with self.subTest(override=override):
                with self.assertRaises(OriginalFirstSideWorldWriteError):
                    source_original_5db7d0_first_side_world_tail(**(inp|override))

    def test_private_original_opcode_and_coefficient_identity_if_available(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("original executable intentionally absent from hosted CI")
        exe=Path(path).read_bytes()
        self.assertEqual((len(exe),sha256(exe).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        source={
            0x5db7d0:"84 c0",0x5db7d2:"0f 85 1a 02 00 00",
            0x5db7d8:"8d 86 74 01 00 00",0x5db7de:"b9 05 00 00 00",
            0x5db7e3:"8b 50 fc",0x5db7e6:"89 10",
            0x5db7e8:"8b 50 e4",0x5db7eb:"89 50 e8",
            0x5db7f8:"89 9e 48 01 00 00",0x5db7fe:"89 86 60 01 00 00",
            0x5db80e:"c7 86 44 01 00 00 01 00 00 00",
            0x5db822:"0f af 0d 00 11 82 00",0x5db84a:"0f af 0d 04 11 82 00",
            0x5db872:"0f af 0d 08 11 82 00",0x5db89a:"0f af 0d 0c 11 82 00",
            0x5db8c2:"0f af 0d 10 11 82 00",0x5db8ec:"b8 cd cc cc cc",
            0x5db8f1:"f7 64 24 10",0x5db8f5:"c1 ea 03",
            0x5db904:"89 96 44 01 00 00",
            0x5db92b:"89 86 24 01 00 00",
            0x5db95d:"89 86 28 01 00 00",
            0x5db97f:"c6 86 30 01 00 00 01",
            0x5db9aa:"0f af 96 2c 01 00 00",
            0x5db9b5:"fe c0",0x5db9d4:"d8 f9",
            0x5db9d6:"e8 75 c9 08 00",0x5db9dd:"89 86 2c 01 00 00",
            0x5db9e9:"80 cc 02",0x5db9ec:"89 86 e8 00 00 00",
            0x66835f:"80 cc 0c",
            0x821100:"32 00 00 00 64 00 00 00 c8 00 00 00 2c 01 00 00 f4 01 00 00",
        }
        for va,hexdump in source.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(hexdump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__": main()
