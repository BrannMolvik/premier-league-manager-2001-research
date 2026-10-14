"""Native original two-side FastView stage tests; source-only, NOT GUI."""
from __future__ import annotations

import os
import struct
import unittest
from pathlib import Path

from original_fastview_two_sided_live_writeback import (
    OriginalFastViewTwoSideWritebackError,
    SOURCE_FASTVIEW_FULL_SIDE_BYTES,
    SOURCE_FASTVIEW_TACTICAL_SIDE_BYTES,
    SOURCE_FASTVIEW_SAFE_NATIVE_PLAYER_MAX,
    source_fastview_native_tactical_280_init_6c1d30,
    source_fastview_native_two_side_setup_533270,
    source_fastview_original_pre_modal_two_flag_reset_6c1cf0,
    source_fastview_native_raw_tactical_280_from_packed_533b70,
)


def make_stage(count=12, initial_available=2, positions=None, flagged=()):
    full=bytearray(SOURCE_FASTVIEW_FULL_SIDE_BYTES)
    raw=bytearray(SOURCE_FASTVIEW_TACTICAL_SIDE_BYTES)
    struct.pack_into("<I",full,0xFC,count)
    struct.pack_into("<I",raw,0x14,count)
    full[0x100]=initial_available
    for i in range(min(count,11)):
        struct.pack_into("<I",raw,0x18+4*i,
                         positions[i] if positions is not None else 1)
    for i in flagged:
        full[0x13C+0x48*i]=1
    return bytes(full),bytes(raw)


class OriginalFastViewTactical280NativeSourceTests(unittest.TestCase):
    def test_source_orders_starters_and_subs_and_sets_available_flag(self):
        full,raw=make_stage(12,2,flagged=(0,5))
        result=source_fastview_native_tactical_280_init_6c1d30(
            native_full_side_1556=full,native_raw_tactical_280=raw)
        self.assertEqual(len(result),280)
        self.assertEqual(struct.unpack_from("<I",result,0x14)[0],12)
        self.assertEqual(struct.unpack_from("<11I",result,0x60),
                         tuple(range(11)))
        self.assertEqual(result[0xF0],3)
        self.assertEqual(result[0xF1],0)
        self.assertEqual(result[0xF2:0xF2+12],bytes(range(12)))
        self.assertEqual(result[0x104:0x104+12],b"\x00"*11+b"\x01")
        self.assertEqual(result[:0x14],raw[:0x14])
        self.assertEqual(full[0x100],2)

    def test_original_byte_decrement_wraps_exactly_like_x86_dec(self):
        full,raw=make_stage(11,0,flagged=(2,))
        got=source_fastview_native_tactical_280_init_6c1d30(
            native_full_side_1556=full,native_raw_tactical_280=raw)
        self.assertEqual(got[0xF1],255)

    def test_original_compatibility_has_18_19_aliases_and_rewrites_rank_twice(self):
        positions=[18,19]+[1]*9
        full,raw=make_stage(11,1,positions=positions)
        out=source_fastview_native_tactical_280_init_6c1d30(
            native_full_side_1556=full,native_raw_tactical_280=raw)
        ranks=struct.unpack_from("<11I",out,0x60)
        self.assertEqual(ranks[:2],(11,12))
        self.assertEqual(ranks[2:],tuple(range(9)))

    def test_original_three_way_and_pair_position_compatibility(self):
        # Position 9 matches rank 9,12,15, repeatedly overwriting its
        # rank; 4/8, 2/6 and 3/7 are separate symmetric aliases.
        positions=[9,4,2,3,1,1,1,1,1,1,1]
        full,raw=make_stage(11,0,positions=positions)
        out=source_fastview_native_tactical_280_init_6c1d30(
            native_full_side_1556=full,native_raw_tactical_280=raw)
        ranks=struct.unpack_from("<11I",out,0x60)
        self.assertEqual(ranks[4:],tuple(range(7)))
        self.assertGreater(ranks[0],ranks[2])
        self.assertGreater(ranks[0],ranks[1])
        self.assertGreater(ranks[0],ranks[3])

    def test_unmatched_position_preserves_original_value_not_invented_rank(self):
        positions=[255]+[1]*10
        full,raw=make_stage(11,0,positions=positions)
        rawbyte=bytearray(raw)
        struct.pack_into("<I",rawbyte,0x60,0x12345678)
        out=source_fastview_native_tactical_280_init_6c1d30(
            native_full_side_1556=full,native_raw_tactical_280=bytes(rawbyte))
        self.assertEqual(struct.unpack_from("<I",out,0x60)[0],0x12345678)

    def test_two_side_stage_preserves_order_and_entire_original_owner_bytes(self):
        left,raw_l=make_stage(11,5,flagged=(0,))
        right,raw_r=make_stage(18,1,flagged=(0,1))
        stage=source_fastview_native_two_side_setup_533270(
            native_full_side0_1556=left,native_full_side1_1556=right,
            native_raw_tactics_side0_280=raw_l,
            native_raw_tactics_side1_280=raw_r)
        self.assertEqual(stage.original_full_side_global_memory,left+right)
        self.assertEqual(len(stage.original_full_side_global_memory),3112)
        self.assertEqual(stage.original_tactics_side0[0xF1],4)
        self.assertEqual(stage.original_tactics_side1[0xF1],255)
        self.assertEqual(stage.original_tactics_side1[0x104:0x104+18],
                         b"\x00"*11+b"\x01"*7)
        self.assertEqual(stage.original_tactics_side1[0xF2:0xF2+18],
                         bytes(range(18)))

    def test_missing_owner_and_mismatched_count_fail_before_any_side_return(self):
        good,raw=make_stage(12)
        for native_side,native_tactics in (
            (good[:-1],raw),(good,raw[:-1]),
            (bytearray(good),raw),(good,bytearray(raw)),
        ):
            with self.assertRaises(OriginalFastViewTwoSideWritebackError):
                source_fastview_native_tactical_280_init_6c1d30(
                    native_full_side_1556=native_side,
                    native_raw_tactical_280=native_tactics)
        unmatched=bytearray(raw)
        struct.pack_into("<I",unmatched,0x14,13)
        with self.assertRaises(OriginalFastViewTwoSideWritebackError):
            source_fastview_native_tactical_280_init_6c1d30(
                native_full_side_1556=good,
                native_raw_tactical_280=bytes(unmatched))

    def test_fail_closed_outside_11_to_18_native_player_owner_capacity(self):
        for count in (0,1,10,19,20,255,0xFFFFFFFF):
            full=bytearray(1556);raw=bytearray(280)
            struct.pack_into("<I",full,0xFC,count)
            struct.pack_into("<I",raw,0x14,count)
            with self.subTest(count=count),self.assertRaises(
                OriginalFastViewTwoSideWritebackError):
                source_fastview_native_tactical_280_init_6c1d30(
                    native_full_side_1556=bytes(full),
                    native_raw_tactical_280=bytes(raw))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "private original exe not mounted")
    def test_native_two_side_init_copy_ranking_and_reserve_bytes_original_pe(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x53328B:"e8 e0 00 00 00",
            0x533299:"e8 62 ea 18 00",
            0x5332A5:"e8 76 08 00 00",
            0x5332B0:"e8 7b ea 18 00",
            0x5332B9:"83 fe 02",
            0x6C1D15:"b9 85 01 00 00",
            0x6C1D1A:"8d 3c 95 d0 4a a1 00",
            0x6C1D21:"f3 a5",
            0x6C1D5B:"b9 46 00 00 00",
            0x6C1D64:"8d 1c c5 98 48 a1 00",
            0x6C1D6F:"f3 a5",
            0x6C1D7B:"88 84 03 f2 00 00 00",
            0x6C1DA9:"e8 a2 00 00 00",
            0x6C1DB9:"89 44 b3 60",
            0x6C1DC3:"83 ff 0b",
            0x6C1DC9:"83 fd 14",
            0x6C1DD2:"c6 83 f0 00 00 00 03",
            0x6C1DD9:"8a 81 00 01 00 00",
            0x6C1DE5:"8b 91 fc 00 00 00",
            0x6C1E0C:"83 f8 0b",
            0x6C1E12:"88 04 2e",
            0x6C1E18:"88 16",
            0x6C1E20:"80 3a 00",
            0x6C1E25:"fe 8b f1 00 00 00",
            0x6C1E36:"83 c6 48",
            0x6C1E58:"3b c1",
            0x6C1E62:"83 f8 12",
            0x6C1E7E:"83 f8 09",
            0x6C1EAE:"83 f8 04",
            0x6C1ECA:"83 f8 02",
            0x6C1EE6:"83 f8 03",
        }
        for va,source in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(source))),
                                 bytes.fromhex(source))




class OriginalFastViewPackedMatchSide533B70Tests(unittest.TestCase):
    def test_original_packed_fields_and_three_disjoint_byte_arrays(self):
        packed=bytearray(0x28+18)
        struct.pack_into("<I",packed,0,0x1234ABCD)
        for i in range(18):
            packed[4+i]=21+i
            packed[0x16+i]=i+1
            packed[0x28+i]=200+i
        original=b"\xCE"*280
        out=source_fastview_native_raw_tactical_280_from_packed_533b70(
            original_raw_stack_280=original,
            original_packed_side=bytes(packed),
            native_player_count=18)
        self.assertEqual(len(out),280)
        self.assertEqual(struct.unpack_from("<6I",out,0),(
            0xCD,(0x1234ABCD>>8)&3,(0x1234ABCD>>14)&3,
            (0x1234ABCD>>16)&3,(0x1234ABCD>>12)&3,18
        ))
        self.assertEqual(struct.unpack_from("<18I",out,0x18),
                         tuple(range(1,19)))
        self.assertEqual(struct.unpack_from("<18I",out,0x60),
                         tuple(range(200,218)))
        self.assertEqual(struct.unpack_from("<18I",out,0xA8),
                         tuple(range(21,39)))
        self.assertEqual(out[0xF0:],original[0xF0:])
        self.assertEqual(original,b"\xCE"*280)

    def test_native_setup_accepts_authenticated_raw_builder_for_both_sides(self):
        def packed(n,position):
            payload=bytearray(0x28+n)
            for i in range(n):payload[0x16+i]=position
            return bytes(payload)
        owner_l,_=make_stage(11,2)
        owner_r,_=make_stage(18,4)
        l=source_fastview_native_raw_tactical_280_from_packed_533b70(
            original_raw_stack_280=b"\x00"*280,
            original_packed_side=packed(11,1),native_player_count=11)
        rr=source_fastview_native_raw_tactical_280_from_packed_533b70(
            original_raw_stack_280=b"\x00"*280,
            original_packed_side=packed(18,2),native_player_count=18)
        both=source_fastview_native_two_side_setup_533270(
            native_full_side0_1556=owner_l,native_full_side1_1556=owner_r,
            native_raw_tactics_side0_280=l,native_raw_tactics_side1_280=rr)
        self.assertEqual(struct.unpack_from("<I",both.original_tactics_side0,0x14)[0],11)
        self.assertEqual(struct.unpack_from("<I",both.original_tactics_side1,0x14)[0],18)
        self.assertEqual(both.original_tactics_side0[0xF2:0xF2+11],bytes(range(11)))
        self.assertEqual(both.original_tactics_side1[0xF2:0xF2+18],bytes(range(18)))
        self.assertEqual(both.original_full_side_global_memory,owner_l+owner_r)

    def test_native_packed_source_must_preserve_unwritten_stack_bytes(self):
        src=bytearray(0x28+11)
        for i in range(11):src[0x16+i]=1
        out=source_fastview_native_raw_tactical_280_from_packed_533b70(
            original_raw_stack_280=b"\xAB"*280,
            original_packed_side=bytes(src),
            native_player_count=11)
        # 0x533B70 writes through +0xD4 for 11 players; unknown
        # scratch trailing bytes are retained until 0x6C1D30 edits.
        self.assertEqual(out[0xF0:],b"\xAB"*(280-0xF0))

    def test_short_or_malformed_packed_source_cannot_invent_live_tactics(self):
        src=b"\x00"*(0x28+11)
        for changes in (
            {"original_raw_stack_280":b"\x00"*279},
            {"original_raw_stack_280":bytearray(b"\x00"*280)},
            {"original_packed_side":src[:-1]},
            {"original_packed_side":bytearray(src)},
            {"native_player_count":10},
            {"native_player_count":19},
            {"native_player_count":True},
        ):
            params=dict(original_raw_stack_280=b"\x00"*280,
                        original_packed_side=src,
                        native_player_count=11)
            with self.subTest(changes=changes),self.assertRaises(
                OriginalFastViewTwoSideWritebackError):
                source_fastview_native_raw_tactical_280_from_packed_533b70(
                    **(params | changes))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original private executable not mounted")
    def test_native_533b70_source_caller_and_packed_field_opcodes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples={
            0x533B20:"8b 4c 24 0c",
            0x533B2D:"8b 81 a4 05 00 00",
            0x533B35:"8b 81 54 0b 00 00",
            0x533B41:"89 42 14",
            0x533B47:"8b 81 a8 05 00 00",
            0x533B58:"8b 81 58 0b 00 00",
            0x533B79:"8b 02",
            0x533B7B:"c1 e8 08",
            0x533B7E:"83 e0 03",
            0x533B8C:"89 0e",
            0x533B90:"c1 e8 0e",
            0x533B9B:"c1 e9 10",
            0x533BA6:"c1 e8 0c",
            0x533BAF:"8b 46 14",
            0x533BCA:"8a 50 ee",
            0x533BCD:"89 51 b4",
            0x533BD2:"8a 10",
            0x533BD4:"89 51 fc",
            0x533BD9:"8a 50 dc",
            0x533BDD:"89 51 44",
            0x533BE3:"8d 14 07",
        }
        for va,hx in samples.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


class OriginalFastViewIntermediateGlobalResetSourceTests(unittest.TestCase):
    def test_both_global_dwords_zero_before_premodal_record_copier(self):
        for before in (bytes(8),bytes(range(8)),bytes([255])*8):
            with self.subTest(before=before):
                result=source_fastview_original_pre_modal_two_flag_reset_6c1cf0(
                    original_a145f0_a145f4_eight_bytes_before=before)
                self.assertEqual(result, bytes(8))
                self.assertEqual(len(result),8)
                self.assertEqual(len(before),8)

    def test_reset_requires_exact_original_two_global_dwords(self):
        for malformed in (None,bytearray(8),"abc",bytes(7),bytes(9),True):
            with self.subTest(malformed=malformed):
                with self.assertRaises(OriginalFastViewTwoSideWritebackError):
                    source_fastview_original_pre_modal_two_flag_reset_6c1cf0(
                        original_a145f0_a145f4_eight_bytes_before=malformed)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "original private executable not mounted")
    def test_original_native_fastview_reset_call_and_two_exact_dword_stores(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        samples=(
            (0x533203,"e8 e8 ea 18 00"),
            (0x6C1CF0,"33 c0 a3 f0 45 a1 00 a3 f4 45 a1 00 c3"),
        )
        for addr,hx in samples:
            with self.subTest(addr=hex(addr)):
                expected=bytes.fromhex(hx)
                self.assertEqual(pe.read(addr,len(expected)),expected)


if __name__ == "__main__":
    unittest.main()
