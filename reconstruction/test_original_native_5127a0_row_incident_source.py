"""Original 5127A0 row byte order and native 41A490 effect regressions."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from struct import pack_into
import hashlib
import os
import unittest
from original_native_5127a0_row_incident_source import (
    OriginalRowIncidentSourceError,
    source_original_5127a0_row_from_reached,
    source_original_41a490_accumulator_at_callback_boundary,
)


def owner(*, first=2, second=2):
    o=bytearray(0xb58)
    pack_into("<I",o,0,0x10000)
    pack_into("<I",o,0x5b0,0x20000)
    pack_into("<i",o,0x5a4,first)
    pack_into("<i",o,0xb54,second)
    for side,count,vectors,rows in (
        (0,first,0x4,0x4c), (1,second,0x5b4,0x5fc)
    ):
        for i in range(count):
            pack_into("<I",o,vectors+4*i,0x40000+side*0x1000+i*4)
            o[rows+i*0x4c+0x48] = 1+i
            o[rows+i*0x4c+0x49] = 2+i
            o[rows+i*0x4c+0x4a] = 1 if (i%2)==0 else 0
    return bytes(o)


def player(value):
    p=bytearray(0x148)
    p[0x144]=value
    return bytes(p)


def row(side=0,index=0, raw=None):
    return source_original_5127a0_row_from_reached(
        original_processing_owner_record=owner() if raw is None else raw,
        original_pass_index=side,original_row_index=index,
    )


def stage(r, old=0):
    return source_original_41a490_accumulator_at_callback_boundary(
        original_reached_row=r,original_player_at_41a490=player(old),
        original_41a490_reached=True,
    )


class OriginalNativeRowIncidentTests(unittest.TestCase):
    def test_both_passes_have_distinct_own_and_opponent_pointers(self):
        a=row(0,0)
        b=row(1,0)
        self.assertEqual((a.source_current_team_pointer,a.source_opponent_team_pointer),
                         (0x10000,0x20000))
        self.assertEqual((b.source_current_team_pointer,b.source_opponent_team_pointer),
                         (0x20000,0x10000))
        self.assertEqual((a.source_4197c0_arg1,a.source_4197c0_arg2,a.source_4197c0_arg3),
                         (1,2,0x20000))
        self.assertEqual((b.source_4197c0_arg1,b.source_4197c0_arg2,b.source_4197c0_arg3),
                         (1,2,0x10000))
        self.assertTrue(a.source_41a5b0_called_after_row)
        self.assertFalse(a.original_4197c0_world_callback_executed)

    def test_each_row_uses_4c_stride_and_independent_41a5b0_flag(self):
        for side in (0,1):
            r=row(side,1)
            self.assertEqual((r.source_4197c0_arg1,r.source_4197c0_arg2), (2,3))
            self.assertFalse(r.source_41a5b0_called_after_row)
            self.assertEqual(r.source_player_pointer,0x40000+side*0x1000+4)

    def test_source_guard_invalid_row_and_pointers(self):
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"pass"):
            row(2,0)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"row index"):
            row(0,-1)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"row index"):
            row(0,2)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"18-row"):
            row(0,0,owner(first=0))
        broken=bytearray(owner())
        pack_into("<I",broken,0x4,0)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"row player"):
            row(0,0,bytes(broken))
        pack_into("<I",broken,0x4,0x50000)
        pack_into("<I",broken,0,0)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"team-owner"):
            row(0,0,bytes(broken))
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"through"):
            row(0,0,b"")

    def test_native_41a490_increment_caps_at_two(self):
        r=stage(row(),old=0)
        self.assertEqual((r.source_increment_capped,r.original_player_144_at_417340_or_return),
                         (2,2))
        self.assertTrue(r.native_417340_callback_outstanding)
        self.assertFalse(r.live_game_state_updated)
        self.assertEqual(r.projected_player_record_at_417340_or_return[0x144],2)

    def test_zero_one_and_two_post_result_call_gate(self):
        r=row()
        for args,old,increment,after,called in (
            ((0,0),0,0,0,False), ((1,0),0,1,1,False),
            ((0,1),0,2,2,True), ((1,1),1,2,3,True)
        ):
            x=replace(r,source_4197c0_arg1=args[0],source_4197c0_arg2=args[1])
            y=stage(x,old=old)
            self.assertEqual((y.source_increment_capped,
                              y.original_player_144_at_417340_or_return,
                              y.native_417340_callback_outstanding),
                             (increment,after,called))

    def test_unsigned_byte_wrap_precedes_417340_gate(self):
        r=stage(row(),old=255)
        self.assertEqual(r.original_player_144_at_417340_or_return,1)
        self.assertFalse(r.native_417340_callback_outstanding)
        r=stage(row(),old=254)
        self.assertEqual(r.original_player_144_at_417340_or_return,0)
        self.assertFalse(r.native_417340_callback_outstanding)

    def test_unreached_leaf_not_assumed_from_source_row(self):
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"reached"):
            source_original_41a490_accumulator_at_callback_boundary(
                original_reached_row=row(),original_player_at_41a490=player(0),
                original_41a490_reached=False)
        with self.assertRaisesRegex(OriginalRowIncidentSourceError,"player bytes"):
            source_original_41a490_accumulator_at_callback_boundary(
                original_reached_row=row(),original_player_at_41a490=b"",
                original_41a490_reached=True)

    def test_actual_private_original_opcodes_when_supplied(self):
        p=os.environ.get("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("private original EXE not supplied to test runner")
        source=Path(p).read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        opcodes={
            0x5128b2:"57 52 50 51 8b cb",
            0x5128b8:"e8 03 6f f0 ff",
            0x5128c1:"84 c0 74 08",
            0x5127af:"8b 44 24 30 85 db 75 04",
            0x5127d2:"8d 88 b4 05 00 00",
            0x51280e:"8d 88 fc 05 00 00",
            0x41a490:"8b 44 24 08 8b 54 24 04",
            0x41a498:"8d 04 42 83 f8 02 7e 05",
            0x41a4a0:"b8 02 00 00 00",
            0x41a4a5:"8a 91 44 01 00 00",
            0x41a4af:"88 91 44 01 00 00",
            0x41a4b5:"3c 01 76 05 e8 82 ce ff ff",
        }
        for va,expected in opcodes.items():
            with self.subTest(original_source_va=hex(va)):
                raw=bytes.fromhex(expected)
                self.assertEqual(source[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":
    unittest.main()
