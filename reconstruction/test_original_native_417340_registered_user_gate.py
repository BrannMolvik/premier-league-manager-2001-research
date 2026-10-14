"""Original native 417340 registered human club-context lookup regressions."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into
import hashlib
import os
import unittest

from original_native_417340_registered_user_gate import (
    Original417340ReachedUser,Original417340SourceError,
    source_original_417340_registered_user_from_reached,
)


def player(pid=12, club_index=3):
    raw=bytearray(0x164)
    pack_into("<H",raw,4,pid)
    pack_into("<h",raw,0x10,club_index)
    return bytes(raw)


def club(key):
    raw=bytearray(8)
    pack_into("<I",raw,4,key)
    return bytes(raw)


def world(head):
    raw=bytearray(0x9d0)
    pack_into("<I",raw,0x9cc,head)
    return bytes(raw)


def manager(*,link=0x1000,user=0x2000,context=0x3000,key=77,next_link=0):
    node=bytearray(8)
    pack_into("<I",node,0,user)
    pack_into("<I",node,4,next_link)
    record=bytearray(0x5b8)
    pack_into("<I",record,0x5b4,context)
    context_record=bytearray(8)
    pack_into("<I",context_record,4,key)
    return Original417340ReachedUser(
        link,bytes(node),user,bytes(record),context,bytes(context_record))


def project(links=(),*,club_index=3,key=77,head=None,source=None,
            club_pointer=None,club_record=None,world_record=None,
            default=None,base=None):
    if head is None:
        head=links[0].original_manager_link_pointer if links else 0
    if base is None and club_index>=0:
        base=0x50000
    if default is None and club_index<0:
        default=0x60000
    if club_pointer is None:
        club_pointer=default if club_index<0 else base+680*club_index
    return source_original_417340_registered_user_from_reached(
        original_player_at_call=player(club_index=club_index) if source is None else source,
        original_874b90_club_array_base=base,
        original_874b94_default_club_pointer=default,
        original_reached_club_pointer=club_pointer,
        original_reached_club_record=club(key) if club_record is None else club_record,
        original_global_874c10_record=world(head) if world_record is None else world_record,
        original_reached_manager_links=links,
    )


class Original417340RegisteredUserTests(unittest.TestCase):
    def test_current_club_index_times_exact_680_and_first_user_match(self):
        a=project((manager(key=77),))
        self.assertEqual(a.original_source_club_pointer,0x50000+680*3)
        self.assertEqual(a.original_current_club_index_signed,3)
        self.assertEqual(a.original_source_club_owner_key,77)
        self.assertEqual(a.original_visited_manager_link_pointers,(0x1000,))
        self.assertEqual(a.original_matching_user_pointer,0x2000)
        self.assertEqual(a.original_417340_return_al,1)
        self.assertFalse(a.native_callback_executed)
        self.assertFalse(a.live_game_state_updated)

    def test_first_miss_second_hit_stops_without_more_nodes(self):
        m1=manager(key=4,next_link=0x1100)
        m2=manager(link=0x1100,user=0x2100,context=0x3100,key=77)
        r=project((m1,m2))
        self.assertEqual(r.original_visited_manager_link_pointers,(0x1000,0x1100))
        self.assertEqual(r.original_matching_user_pointer,0x2100)
        with self.assertRaisesRegex(Original417340SourceError,"extra"):
            project((m1,m2,manager(link=0x1200)))

    def test_userless_and_no_owner_match_return_zero_not_generic_inbox(self):
        a=project(())
        self.assertEqual(a.original_417340_return_al,0)
        self.assertIsNone(a.original_matching_user_pointer)
        no_match=project((manager(key=7),))
        self.assertEqual(no_match.original_417340_return_al,0)
        self.assertFalse(no_match.live_game_state_updated)

    def test_negative_club_index_uses_distinct_874b94_fallback(self):
        a=project((manager(),),club_index=-1)
        self.assertEqual(a.original_current_club_index_signed,-1)
        self.assertEqual(a.original_source_club_pointer,0x60000)
        self.assertEqual(a.original_417340_return_al,1)
        with self.assertRaisesRegex(Original417340SourceError,"skips 874B90"):
            project((),club_index=-1,base=0x50000)
        with self.assertRaisesRegex(Original417340SourceError,"skips 874B94"):
            project((),default=0x60000)

    def test_source_pointer_and_embedded_object_mismatches_fail_closed(self):
        with self.assertRaisesRegex(Original417340SourceError,"identity mismatch"):
            project((),club_pointer=0x90000)
        with self.assertRaisesRegex(Original417340SourceError,"bytes through"):
            project((),source=b"")
        with self.assertRaisesRegex(Original417340SourceError,"source bytes"):
            project((),club_record=b"")
        with self.assertRaisesRegex(Original417340SourceError,"owner bytes"):
            project((),world_record=b"")
        m=manager()
        with self.assertRaisesRegex(Original417340SourceError,"user pointer identity"):
            project((replace(m,original_user_pointer=0xdead),))
        with self.assertRaisesRegex(Original417340SourceError,"context pointer identity"):
            project((replace(m,original_user_context_pointer=0xdead),))

    def test_native_manager_link_cycle_missing_and_source_order_fail_closed(self):
        m=manager(key=7,next_link=0x1000)
        with self.assertRaisesRegex(Original417340SourceError,"cyclic"):
            project((m,m))
        with self.assertRaisesRegex(Original417340SourceError,"stopped"):
            project((manager(key=7,next_link=0x1100),))
        with self.assertRaisesRegex(Original417340SourceError,"manager link pointer mismatch"):
            project((manager(link=0x1100),),head=0x1000)
        with self.assertRaisesRegex(Original417340SourceError,"extra"):
            project((manager(),),head=0)

    def test_exact_original_pe_opcodes_if_private_file_available(self):
        file=os.getenv("FM2001_ORIGINAL_EXE")
        if not file:
            self.skipTest("original private executable not committed to Git")
        content=Path(file).read_bytes()
        self.assertEqual(hashlib.sha256(content).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        patterns={
            0x417270:"0f bf 49 10 85 c9",
            0x417278:"a1 94 4b 87 00 c3",
            0x41727e:"8b c1 c1 e0 04 03 c1",
            0x417285:"8b 0d 90 4b 87 00 8d 04 80 8d 04 c1",
            0x41728e:"8d 04 c1 c3",
            0x417340:"e8 2b ff ff ff 8b c8 e9 64 c4 fe ff",
            0x4037b0:"51 b9 10 4c 87 00 e8 25 02 01 00 c3",
            0x4139e0:"8b 44 24 04 8b 40 04 50 e8 03 00 00 00",
            0x4139f0:"8b 81 cc 09 00 00 85 c0 74 18",
            0x4139fa:"8b 4c 24 04 8b 10",
            0x413a00:"8b 92 b4 05 00 00 39 4a 04 74 0c",
            0x413a0b:"8b 40 04 85 c0 75 ec 32 c0",
            0x413a12:"32 c0 c2 04 00 b0 01 c2",
        }
        for va,text_bytes in patterns.items():
            with self.subTest(native_va=hex(va)):
                expected=bytes.fromhex(text_bytes)
                self.assertEqual(content[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
