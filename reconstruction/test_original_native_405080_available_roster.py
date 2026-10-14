"""Original 405080 eligible club roster count from source pool and status bits."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_405080_available_roster import (
    Original405080ReachedPlayer,Original405080SourceError,
    source_original_405080_available_roster_from_reached,
)
from original_native_41a5b0_extra_event import (
    Original41A5B0SourceError,source_original_41a5b0_optional_extra_from_reached,
)
from test_original_native_41a5b0_extra_event import staged,player


def team(ids):
    t=bytearray(0x298)
    pack_into("<i",t,0x294,len(ids))
    for i,pid in enumerate(ids):
        pack_into("<H",t,0x244+2*i,pid)
    return bytes(t)


def player_raw(pid,flags):
    b=bytearray(0x250)
    pack_into("<H",b,4,pid)
    pack_into("<I",b,0x14,flags)
    return bytes(b)


def source(ids=tuple(range(123,137)),*,statuses=(),owner=None):
    if owner is None:
        owner=0x50000+680*2
    status_by_id=dict(statuses)
    base=0x600000
    return source_original_405080_available_roster_from_reached(
        original_team_pointer=owner,
        original_team_record=team(ids),
        original_875640_pool_base_if_reached=base if ids else None,
        original_reached_roster_player_records=tuple(
            Original405080ReachedPlayer(
                base+592*pid,player_raw(pid,status_by_id.get(pid,0)))
            for pid in ids),
    )


class Original405080AvailableRosterTests(unittest.TestCase):
    def test_exact_original_592_stride_and_four_blocking_status_bits(self):
        ids=tuple(range(123,139))
        flags=((123,1),(124,2),(125,64),(126,256),(127,8))
        result=source(ids,statuses=flags)
        self.assertEqual(result.original_405080_eligible_count,12)
        self.assertEqual(result.original_405080_excluded_count,4)
        self.assertEqual(result.original_roster_ids,ids)
        self.assertEqual(result.original_player_status_14_by_id[0],(123,1))
        self.assertFalse(result.original_native_callback_executed)
        self.assertFalse(result.live_game_state_updated)

    def test_original_team_zero_roster_returns_zero_without_pool_lookup(self):
        x=source(())
        self.assertEqual(x.original_405080_eligible_count,0)
        self.assertIsNone(x.original_875640_pool_base_if_reached)
        with self.assertRaisesRegex(Original405080SourceError,"skips"):
            source_original_405080_available_roster_from_reached(
                original_team_pointer=0x50000,original_team_record=team(()),
                original_875640_pool_base_if_reached=0x600000,
                original_reached_roster_player_records=())

    def test_405080_proof_qualifies_actual_original_41a5b0_threshold(self):
        p=player(pid=123,status=0)
        reached=staged(registered=False,source=p,count=None)
        self.assertEqual(reached.original_405080_eligible_count,14)
        qualified=replace(reached,
            original_405080_eligible_count=None,
            original_405080_source_proof=source())
        decision=source_original_41a5b0_optional_extra_from_reached(qualified)
        self.assertTrue(decision.original_would_allocate_605f70_and_store_player24c)
        self.assertEqual(decision.original_405080_eligible_count_reached,14)
        self.assertFalse(decision.live_game_state_updated)

    def test_wrong_qualified_count_owner_or_player_status_fails_closed(self):
        reached=staged(registered=False,count=14)
        proof=source()
        with self.assertRaisesRegex(Original41A5B0SourceError,"disagrees"):
            source_original_41a5b0_optional_extra_from_reached(replace(
                reached,original_405080_eligible_count=13,
                original_405080_source_proof=proof,
                original_global_821814_player77_threshold=None))
        with self.assertRaisesRegex(Original41A5B0SourceError,"forged"):
            source_original_41a5b0_optional_extra_from_reached(replace(
                reached,original_405080_source_proof=replace(
                    proof,original_team_pointer=0x9999)))
        bad_status=source(statuses=((123,1),))
        with self.assertRaisesRegex(Original41A5B0SourceError,"flags differ"):
            source_original_41a5b0_optional_extra_from_reached(replace(
                reached,original_405080_source_proof=bad_status))

    def test_invalid_reached_native_405080_pool_record_fails_closed(self):
        ids=(123,)
        native=Original405080ReachedPlayer(0x600000+592*123,player_raw(123,0))
        for bad,regex in (
            ((replace(native,original_player_pointer=0xdead),),"pointer mismatch"),
            ((replace(native,original_player_record_at_count=b""),),"status required"),
            ((replace(native,original_player_record_at_count=player_raw(124,0)),),"identity mismatch"),
        ):
            with self.subTest(bad=bad),self.assertRaisesRegex(Original405080SourceError,regex):
                source_original_405080_available_roster_from_reached(
                    original_team_pointer=0x50000,
                    original_team_record=team(ids),
                    original_875640_pool_base_if_reached=0x600000,
                    original_reached_roster_player_records=bad)
        with self.assertRaisesRegex(Original405080SourceError,"duplicate"):
            source((123,123))
        with self.assertRaisesRegex(Original405080SourceError,"incomplete"):
            source_original_405080_available_roster_from_reached(
                original_team_pointer=0x50000,
                original_team_record=team(ids),
                original_875640_pool_base_if_reached=0x600000,
                original_reached_roster_player_records=())

    def test_private_original_exe_native_opcode_signatures_when_supplied(self):
        p=os.getenv("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("original binary private outside GitHub")
        raw=Path(p).read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x405080:"51 55 8b a9 94 02 00 00",
            0x40508f:"8b 3d 40 56 87 00",
            0x405095:"8d b1 44 02 00 00",
            0x4050a3:"66 8b 0e 8d 14 c9",
            0x4050a9:"8d 0c 91 c1 e1 04 03 cf",
            0x4050b1:"8b 51 14 8b da c1 eb 08",
            0x4050b9:"84 d8 75 15",
            0x4050bf:"84 d8 75 0f",
            0x4050c3:"8b ca c1 e9 06",
            0x4050ce:"84 d0 74 01",
            0x4050d2:"4d",
            0x4050e3:"8b c5 5b 5d 59 c3",
        }
        for va,code in signatures.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(code)
                self.assertEqual(raw[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
