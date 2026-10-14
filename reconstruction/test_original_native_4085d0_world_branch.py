"""Original 4085D0 read-only exits and mutating-world gate source tests."""
from __future__ import annotations
from dataclasses import replace
from struct import pack_into
from pathlib import Path
import hashlib
import os
import unittest

from original_native_4085d0_world_branch import (
    Original4085D0ReachedWorld,
    Original4085D0SourceError,
    source_original_4085d0_world_branch_from_reached,
)


def native_player(*,team=2,flags=0,category_ptr=0x3000):
    p=bytearray(0x24c)
    pack_into("<H",p,4,123)
    pack_into("<h",p,0x10,team)
    pack_into("<I",p,0x14,flags)
    pack_into("<I",p,0x248,category_ptr)
    return bytes(p)


def native_team(key=2):
    t=bytearray(8)
    pack_into("<i",t,4,key)
    return bytes(t)


def reached(*,team=2,flags=0,key=2,n=0,peer=0,capacity=2,
            obj=b"\x00\x00\x00\xef\x00",pointer=0x3000,player=None):
    return Original4085D0ReachedWorld(
        0x1000,native_team(key),0x2000,
        native_player(team=team,flags=flags) if player is None else player,
        n,pointer,obj,peer,capacity,
    )


def project(source):
    return source_original_4085d0_world_branch_from_reached(source)


class Original4085D0BranchTests(unittest.TestCase):
    def test_existing_status_bit4_with_matching_team_exits_without_mutation(self):
        item=replace(reached(flags=0x10),
            original_407060_eax=None,
            original_4ea3c0_source_object_pointer=None,
            original_4ea3c0_source_object=None,
            original_406be0_eax=None,
            original_5f0d20_eax=None)
        r=project(item)
        self.assertEqual((r.original_417ee0_return_eax,r.original_4085d0_return_if_no_mutation),(1,1))
        self.assertTrue(r.source_read_only_branch_complete)
        self.assertFalse(r.original_would_reach_mutating_4182f0_then_4ea350)
        self.assertFalse(r.native_callbacks_invoked)
        self.assertFalse(r.live_game_state_updated)
        with self.assertRaisesRegex(Original4085D0SourceError,"skips"):
            project(reached(flags=0x10))

    def test_mismatch_of_signed_current_team_vs_source_team_ignores_bit4(self):
        r=project(reached(team=-1,key=2,flags=0x10,n=11,peer=None,capacity=None,obj=None,pointer=None))
        self.assertEqual(r.original_417ee0_return_eax,0)
        self.assertEqual(r.original_407060_teammate_count,11)
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)

    def test_full_teammate_count_skips_category_callback(self):
        r=project(reached(n=11,peer=None,capacity=None,obj=None,pointer=None))
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)
        self.assertIsNone(r.original_4ea3c0_source_category)
        with self.assertRaisesRegex(Original4085D0SourceError,"skips"):
            project(reached(n=11))

    def test_source_peer_count_at_least_category_capacity_is_readonly(self):
        r=project(reached(n=10,peer=2,capacity=2))
        self.assertEqual(r.original_4ea3c0_source_category,0x0f)
        self.assertEqual((r.original_406be0_teammate_count,r.original_5f0d20_category_capacity_floor),(2,2))
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)
        self.assertTrue(r.source_read_only_branch_complete)

    def test_source_peer_below_capacity_requires_mutating_world_not_fabricated(self):
        r=project(reached(n=0,peer=1,capacity=2))
        self.assertTrue(r.original_would_reach_mutating_4182f0_then_4ea350)
        self.assertFalse(r.source_read_only_branch_complete)
        self.assertIsNone(r.original_4085d0_return_if_no_mutation)
        self.assertFalse(r.live_game_state_updated)
        self.assertFalse(r.native_callbacks_invoked)

    def test_failclosed_missing_actual_reached_data_and_forged_pointer(self):
        with self.assertRaisesRegex(Original4085D0SourceError,"407060"):
            project(replace(reached(),original_407060_eax=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"pointer mismatch"):
            project(reached(pointer=0x7777))
        with self.assertRaisesRegex(Original4085D0SourceError,"source-category"):
            project(replace(reached(),original_player_at_entry=b"\x00"*0x18))
        with self.assertRaisesRegex(Original4085D0SourceError,"source category"):
            project(reached(obj=b""))
        with self.assertRaisesRegex(Original4085D0SourceError,"406BE0"):
            project(reached(peer=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"5F0D20"):
            project(reached(capacity=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"source count"):
            project(reached(n=-1))
        with self.assertRaisesRegex(Original4085D0SourceError,"source count"):
            project(reached(capacity=0))

    def test_private_original_opcode_signatures_if_original_supplied(self):
        src=os.getenv("FM2001_ORIGINAL_EXE")
        if not src:
            self.skipTest("original executable must remain private outside GitHub")
        exe=Path(src).read_bytes()
        self.assertEqual(hashlib.sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        opcodes={
            0x4085d0:"53 56 8b 74 24 0c 57 8b f9",
            0x4085df:"e8 fc f8 00 00",
            0x4085e8:"5f 5e b8 01 00 00 00",
            0x4085fc:"e8 5f ea ff ff",
            0x408601:"83 f8 0b",
            0x408606:"8b 8e 48 02 00 00",
            0x40860d:"e8 ae 1d 0e 00",
            0x408615:"e8 c6 e5 ff ff",
            0x408622:"e8 99 1d 0e 00",
            0x408628:"b9 64 ae 87 00",
            0x40862d:"e8 ee 86 1e 00",
            0x408632:"3b f8",
            0x408636:"8b ce e8 b3 fc 00 00",
            0x408644:"e8 07 1d 0e 00",
            0x417ee0:"0f bf 41 10 39 44 24 04",
            0x417eef:"8b 41 14 c1 e8 04 83 e0 01",
            0x4ea3c0:"8a 41 03 83 e0 1f c3",
            0x4ea350:"8a 41 04 53 8a 5c 24 08",
            0x4182f0:"56 8b f1 83 4e 14 10",
        }
        for va,pattern in opcodes.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(pattern)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
