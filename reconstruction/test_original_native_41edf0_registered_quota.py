"""Original 41EDF0 registered club+1A8 quota and bit12 source tests."""
from __future__ import annotations
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest
from original_native_41edf0_registered_quota import (
    Original41EDF0Reached,Original41EDF0SourceError,
    source_original_41edf0_registered_quota_from_reached,
)


def native_player(index=3, flags=0x1000):
    p=bytearray(0x80)
    pack_into("<H",p,4,123)
    pack_into("<h",p,0x10,2)
    pack_into("<h",p,0x72,index)
    pack_into("<I",p,0x14,flags)
    return bytes(p)


def native_club(counter=3):
    c=bytearray(0x1ac)
    pack_into("<i",c,0x1a8,counter)
    return bytes(c)


def qualify(index=3,flags=0x1000,counter=3):
    if flags&0x1000:
        return Original41EDF0Reached(
            native_player(index,flags),
            0x50000,0x60000,
            0x60000 if index<0 else 0x50000+680*index,
            native_club(counter),
        )
    return Original41EDF0Reached(native_player(index,flags))


class Original41EDF0RegisteredQuotaTests(unittest.TestCase):
    def test_registered_index_is_plus72_not_current_plus10(self):
        r=source_original_41edf0_registered_quota_from_reached(qualify())
        self.assertEqual(r.original_source_registered_club_index_signed,3)
        self.assertEqual(r.original_source_registered_club_pointer,0x50000+680*3)
        self.assertEqual(r.original_registered_club_counter_before,3)
        self.assertEqual(r.original_registered_club_counter_after,2)
        self.assertEqual(unpack_from("<I",r.original_player_after_41edf0,0x14)[0],0)
        self.assertTrue(r.original_status_bit12_cleared)
        self.assertTrue(r.original_registered_club_counter_decremented)
        self.assertFalse(r.native_callback_executed)
        self.assertFalse(r.live_game_state_updated)

    def test_negative_registered_club_uses_original_default_pointer(self):
        r=source_original_41edf0_registered_quota_from_reached(
            qualify(index=-1,counter=1))
        self.assertEqual(r.original_source_registered_club_pointer,0x60000)
        self.assertEqual(r.original_registered_club_counter_after,0)

    def test_zero_negative_counter_does_not_decrement_but_status_still_clears(self):
        for old in (0,-2):
            with self.subTest(old=old):
                r=source_original_41edf0_registered_quota_from_reached(qualify(counter=old))
                self.assertEqual(r.original_registered_club_counter_after,old)
                self.assertTrue(r.original_status_bit12_cleared)
                self.assertFalse(r.original_registered_club_counter_decremented)

    def test_status_bit12_missing_skips_all_source_club_reads(self):
        r=source_original_41edf0_registered_quota_from_reached(qualify(flags=0x20))
        self.assertFalse(r.original_status_bit12_cleared)
        self.assertIsNone(r.original_registered_club_after_41edf0)
        self.assertEqual(unpack_from("<I",r.original_player_after_41edf0,0x14)[0],0x20)
        with self.assertRaisesRegex(Original41EDF0SourceError,"skips"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(native_player(flags=0),0x50000))

    def test_false_identity_truncation_and_invalid_reached_world_fail_closed(self):
        good=qualify()
        with self.assertRaisesRegex(Original41EDF0SourceError,"identity mismatch"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(good.original_player_at_call,0x50000,0x60000,
                                     0xdead,good.original_registered_club_record))
        with self.assertRaisesRegex(Original41EDF0SourceError,"through"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(b""))
        with self.assertRaisesRegex(Original41EDF0SourceError,"through registered"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(native_player()[:0x20],
                                       0x50000,0x60000,0x50000,native_club()))
        with self.assertRaisesRegex(Original41EDF0SourceError,"through"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(good.original_player_at_call,
                                       0x50000,0x60000,good.original_registered_club_pointer,b""))
        with self.assertRaisesRegex(Original41EDF0SourceError,"874B90"):
            source_original_41edf0_registered_quota_from_reached(
                Original41EDF0Reached(good.original_player_at_call,
                                       None,0x60000,good.original_registered_club_pointer,native_club()))

    def test_optional_original_pe_opcode_sha_verification(self):
        file=os.getenv("FM2001_ORIGINAL_EXE")
        if not file:
            self.skipTest("private original binary intentionally outside GitHub")
        data=Path(file).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        patterns={
            0x41edf0:"8b 41 14 56 c1 e8 0c a8 01",
            0x41edfb:"8b 51 14 80 e6 ef",
            0x41ee04:"8b 15 90 4b 87 00",
            0x41ee0a:"0f bf 41 72",
            0x41ee0e:"8b 35 94 4b 87 00",
            0x41ee14:"85 c0 7d 04",
            0x41ee2a:"8b b9 a8 01 00 00",
            0x41ee30:"85 ff 5f 7e 29",
            0x41ee3c:"ff 88 a8 01 00 00",
            0x41ee4d:"8b 8c c2 a8 01 00 00",
            0x41ee54:"49",
            0x41ee58:"89 88 a8 01 00 00",
        }
        for va,h in patterns.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(h)
                self.assertEqual(data[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
