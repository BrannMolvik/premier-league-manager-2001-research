"""Native 419490 conditional FA/UEFA suspension countdown regressions."""
from __future__ import annotations
from struct import pack_into, unpack_from
import unittest
from original_native_419490_suspension_return_source import (
    Original419490ReachedCalls,Original419490SourceError,
    source_original_419490_suspension_return_from_reached,
)


def player(*,fa=0,uefa=0,scheduled=70,flags=0xffffffff):
    out=bytearray(0x164)
    pack_into("<H",out,4,125)
    pack_into("<h",out,0x10,2)
    pack_into("<I",out,0x14,flags)
    out[0x13b]=fa
    out[0x13e]=uefa
    pack_into("<i",out,0x160,scheduled)
    return bytes(out)


def match():
    out=bytearray(0x50)
    pack_into("<I",out,0x4c,0xa000)
    return bytes(out)


def project(*,fa=0,uefa=0,scheduled=70,date=70,first=0,second=None,
            prior=None,v18=0,category=None,club=None,flags=0xffffffff):
    return source_original_419490_suspension_return_from_reached(
        original_player_at_entry=player(fa=fa,uefa=uefa,scheduled=scheduled,flags=flags),
        original_match_at_entry=match(),
        reached=Original419490ReachedCalls(first,second,prior,v18,category,club),
        original_date_9847fc=date,
    )


class Original419490CountdownTests(unittest.TestCase):
    def test_uefa_counter_to_zero_may_generate_real_uefa_return_class(self):
        r=project(uefa=1,fa=3,v18=1,category=1,club=1)
        self.assertEqual(r.original_uefa_counter_after,0)
        self.assertEqual(r.original_fa_counter_after,3)
        self.assertEqual(r.original_event_class_if_allocation_succeeds,
                         "EAMReturnFromUEFASuspension")
        self.assertEqual(r.original_constructor_va_if_allocation_succeeds,0x5853f0)
        self.assertEqual(unpack_from("<I",r.original_source_native_player_after,0x14)[0],
                         0xfffffffd)
        self.assertFalse(r.original_recipient_manager_key_resolved)
        self.assertFalse(r.original_native_613ec0_enqueued)
        self.assertFalse(r.live_game_state_updated)

    def test_fa_counter_to_zero_requires_signed_date_and_club_reached_true(self):
        r=project(fa=1,uefa=8,scheduled=72,date=72,v18=0,club=1)
        self.assertEqual(r.original_fa_counter_after,0)
        self.assertEqual(r.original_uefa_counter_after,8)
        self.assertEqual(r.original_event_class_if_allocation_succeeds,
                         "EAMReturnFromFASuspension")
        self.assertEqual(r.original_constructor_va_if_allocation_succeeds,0x585000)

    def test_one_or_two_remaining_not_premature_return(self):
        r=project(uefa=2,fa=4,v18=1,category=1)
        self.assertEqual(r.original_uefa_counter_after,1)
        self.assertIsNone(r.original_event_class_if_allocation_succeeds)
        r=project(fa=2,uefa=4,v18=1,category=0)
        self.assertEqual(r.original_fa_counter_after,1)
        self.assertIsNone(r.original_event_class_if_allocation_succeeds)
        with self.assertRaisesRegex(Original419490SourceError,"skips 417340"):
            project(fa=2,club=1)

    def test_fa_future_schedule_prevents_decrement_until_date(self):
        r=project(fa=1,scheduled=100,date=99)
        self.assertEqual(r.original_fa_counter_after,1)
        self.assertIsNone(r.original_event_class_if_allocation_succeeds)
        with self.assertRaisesRegex(Original419490SourceError,"not due"):
            project(fa=1,scheduled=100,date=99,club=1)

    def test_club_selector_zero_decrements_without_enqueuing(self):
        self.assertIsNone(project(fa=1,club=0).original_event_class_if_allocation_succeeds)
        self.assertIsNone(project(uefa=1,v18=1,category=1,club=0).original_event_class_if_allocation_succeeds)

    def test_initial_4f8e40_early_exit_preserves_all_player_flags_and_countdowns(self):
        r=project(fa=1,uefa=2,first=1,second=0x3333,prior=1,flags=0x22)
        self.assertEqual(unpack_from("<I",r.original_source_native_player_after,0x14)[0],0x22)
        self.assertEqual(r.original_fa_counter_after,1)
        self.assertEqual(r.original_uefa_counter_after,2)
        with self.assertRaisesRegex(Original419490SourceError,"skips downstream"):
            project(fa=1,first=1,second=3,prior=1,v18=0)

    def test_nonzero_initial_and_secondary_false_reach_countdown(self):
        r=project(fa=1,first=1,second=123,prior=0,v18=0,club=1)
        self.assertEqual(r.original_constructor_va_if_allocation_succeeds,0x585000)

    def test_signed_fa_scheduled_date_boundary(self):
        r=project(fa=1,scheduled=-2,date=0xfffffffe,club=1)
        self.assertEqual(r.original_fa_counter_after,0)
        self.assertEqual(r.original_event_class_if_allocation_succeeds,
                         "EAMReturnFromFASuspension")
        r=project(fa=1,scheduled=-1,date=0xfffffffe)
        self.assertEqual(r.original_fa_counter_after,1)

    def test_wrong_reached_return_order_and_missing_source_failsclosed(self):
        with self.assertRaisesRegex(Original419490SourceError,"secondary"):
            project(first=0,second=1,prior=0)
        with self.assertRaisesRegex(Original419490SourceError,"virtual18"):
            project(v18=None)
        with self.assertRaisesRegex(Original419490SourceError,"competition\\+34"):
            project(v18=0,category=1)
        with self.assertRaisesRegex(Original419490SourceError,"competition\\+34"):
            project(v18=1,category=None)
        with self.assertRaisesRegex(Original419490SourceError,"417340"):
            project(uefa=0,v18=1,category=1,club=1)
        with self.assertRaisesRegex(Original419490SourceError,"date"):
            project(date=-1)

    def test_private_canonical_pe_16_native_opcodes_if_available(self):
        import hashlib
        import os
        from pathlib import Path
        p=os.environ.get("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("original source private, no original binary in GitHub")
        binary=Path(p).read_bytes()
        self.assertEqual(hashlib.sha256(binary).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        source={
          0x4194da:"8b 56 14 83 e2 fd 89 56 14",
          0x419517:"8a 86 3e 01 00 00",
          0x419525:"fe c8 88 86 3e 01 00 00",
          0x41959d:"8a 86 3b 01 00 00",
          0x4195ab:"8b 8e 60 01 00 00 8b 15 fc 47 98 00",
          0x4195bf:"fe c8 88 86 3b 01 00 00",
          0x419591:"e8 5a be 16 00",
          0x419627:"e8 d4 b9 16 00",
          0x419654:"c7 00 64 d5 7b 00",
          0x419663:"b9 a8 7a 94 00",
          0x41795b:"88 9e 3b 01 00 00",
          0x41796d:"88 9e 3e 01 00 00",
          0x41a27e:"c6 85 3e 01 00 00 01",
          0x4198b8:"a1 fc 47 98 00 83 c0 07",
          0x4198c0:"89 86 60 01 00 00",
          0x4198c6:"6a 03 e8 73 3c 23 00",
        }
        for va,hexdump in source.items():
            with self.subTest(original_va=hex(va)):
                expected=bytes.fromhex(hexdump)
                self.assertEqual(binary[va-0x400000:va-0x400000+len(expected)], expected)

    def test_native_player_and_competition_owner_required(self):
        with self.assertRaisesRegex(Original419490SourceError,"DBRPlayer"):
            source_original_419490_suspension_return_from_reached(
                original_player_at_entry=b"",original_match_at_entry=match(),
                reached=Original419490ReachedCalls(0,original_competition_v18_eax=0),
                original_date_9847fc=72)
        broken=bytearray(match())
        pack_into("<I",broken,0x4c,0)
        with self.assertRaisesRegex(Original419490SourceError,"nonnull"):
            source_original_419490_suspension_return_from_reached(
                original_player_at_entry=player(),original_match_at_entry=bytes(broken),
                reached=Original419490ReachedCalls(0,original_competition_v18_eax=0),
                original_date_9847fc=72)


if __name__ == "__main__":
    unittest.main()
