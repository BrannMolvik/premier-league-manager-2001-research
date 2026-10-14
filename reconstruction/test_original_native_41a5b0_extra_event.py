"""Original 41A5B0 optional per-row event source reachability regressions."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_417340_registered_user_gate import (
    Original417340ReachedUser,source_original_417340_registered_user_from_reached,
)
from original_native_41a5b0_extra_event import (
    Original41A5B0Reached, Original41A5B0SourceError,
    source_original_41a5b0_optional_extra_from_reached,
)


def player(pid=123,*,status=0,source_77=60,club_index=2):
    raw=bytearray(0x250)
    pack_into("<H",raw,4,pid)
    pack_into("<h",raw,0x10,club_index)
    pack_into("<I",raw,0x14,status)
    raw[0x77]=source_77
    return bytes(raw)


def manager_proof(source,*,registered=True):
    team=bytearray(8); pack_into("<I",team,4,2)
    global_owner=bytearray(0x9d0); pack_into("<I",global_owner,0x9cc,0x1000)
    link=bytearray(8);pack_into("<I",link,0,0x2000)
    user=bytearray(0x5b8);pack_into("<I",user,0x5b4,0x3000)
    context=bytearray(8);pack_into("<I",context,4,2 if registered else 9)
    reached=Original417340ReachedUser(
        0x1000,bytes(link),0x2000,bytes(user),0x3000,bytes(context))
    return source_original_417340_registered_user_from_reached(
        original_player_at_call=source,
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=None,
        original_reached_club_pointer=0x50000+2*680,
        original_reached_club_record=bytes(team),
        original_global_874c10_record=bytes(global_owner),
        original_reached_manager_links=(reached,),
    )


def staged(*,registered=True,status=0,source_77=60,count=None,
           threshold=75,source_float=None,source=None):
    p=player(status=status,source_77=source_77) if source is None else source
    proof=manager_proof(p,registered=registered)
    if not registered:
        if source_float is None:
            source_float=14.0
        if count is None:
            count=13
    will_allocate=(registered or count>=source_float) and not (p[0x14]&1)
    return Original41A5B0Reached(
        original_player_after_row_at_call=p,
        original_registered_417340_owner_proof=proof,
        original_405080_current_club_pointer=(
            None if registered else proof.original_source_club_pointer),
        original_405080_eligible_count=None if registered else count,
        original_822228_reached_threshold_float=None if registered else source_float,
        original_global_821814_player77_threshold=threshold if will_allocate else None,
    )


class Original41A5B0ExtraEventTests(unittest.TestCase):
    def test_registered_manager_skips_405080_and_exposes_event_type_one(self):
        x=source_original_41a5b0_optional_extra_from_reached(staged())
        self.assertEqual(x.original_player_id,123)
        self.assertEqual(x.original_registered_human_al,1)
        self.assertIsNone(x.original_405080_eligible_count_reached)
        self.assertIsNone(x.original_822228_source_threshold_reached)
        self.assertTrue(x.original_417ff0_low_status_bit_checked)
        self.assertEqual(x.original_417ff0_return_al,0)
        self.assertTrue(x.original_would_allocate_605f70_and_store_player24c)
        self.assertEqual(x.original_605f90_subtype_if_allocated,1)
        self.assertFalse(x.source_branch_complete_without_world_effects)
        self.assertFalse(x.original_native_callback_executed)
        self.assertFalse(x.live_game_state_updated)

    def test_original_age_byte_gte_global_sends_subtype_zero_not_one(self):
        x=source_original_41a5b0_optional_extra_from_reached(
            staged(source_77=90,threshold=75))
        self.assertEqual(x.original_605f90_subtype_if_allocated,0)

    def test_nonhuman_source_count_below_actual_fpu_threshold_early_exits(self):
        x=source_original_41a5b0_optional_extra_from_reached(
            staged(registered=False,count=13))
        self.assertEqual(x.original_405080_eligible_count_reached,13)
        self.assertEqual(x.original_822228_source_threshold_reached,14.0)
        self.assertFalse(x.original_417ff0_low_status_bit_checked)
        self.assertTrue(x.source_branch_complete_without_world_effects)
        self.assertIsNone(x.original_605f90_subtype_if_allocated)

    def test_nonhuman_threshold_reached_but_native_status_bit0_blocks(self):
        x=source_original_41a5b0_optional_extra_from_reached(
            staged(registered=False,count=14,status=1))
        self.assertTrue(x.original_417ff0_low_status_bit_checked)
        self.assertEqual(x.original_417ff0_return_al,1)
        self.assertFalse(x.original_would_allocate_605f70_and_store_player24c)
        self.assertTrue(x.source_branch_complete_without_world_effects)

    def test_nonhuman_count_at_float_threshold_reaches_event_allocation(self):
        x=source_original_41a5b0_optional_extra_from_reached(
            staged(registered=False,count=14,source_float=14.0,source_77=90))
        self.assertTrue(x.original_would_allocate_605f70_and_store_player24c)
        self.assertEqual(x.original_605f90_subtype_if_allocated,0)
        # The threshold global is a runtime data item, not a fixed
        # literal14 comparison. An actual 15.0 must change the decision.
        y=source_original_41a5b0_optional_extra_from_reached(
            staged(registered=False,count=14,source_float=15.0,source_77=90))
        self.assertTrue(y.source_branch_complete_without_world_effects)

    def test_skipped_or_forged_native_reached_inputs_failclosed(self):
        with self.assertRaisesRegex(Original41A5B0SourceError,"skips"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(),original_405080_eligible_count=13))
        with self.assertRaisesRegex(Original41A5B0SourceError,"405080 count"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(registered=False),original_405080_eligible_count=None))
        with self.assertRaisesRegex(Original41A5B0SourceError,"405080 count"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(registered=False),original_822228_reached_threshold_float=None))
        with self.assertRaisesRegex(Original41A5B0SourceError,"405080 count"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(registered=False),original_822228_reached_threshold_float=float("nan")))
        with self.assertRaisesRegex(Original41A5B0SourceError,"threshold skipped"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(registered=False),original_global_821814_player77_threshold=75))
        with self.assertRaisesRegex(Original41A5B0SourceError,"821814"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(),original_global_821814_player77_threshold=None))
        with self.assertRaisesRegex(Original41A5B0SourceError,"proof"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(),original_player_after_row_at_call=player(pid=100)))
        with self.assertRaisesRegex(Original41A5B0SourceError,"through"):
            source_original_41a5b0_optional_extra_from_reached(
                replace(staged(),original_player_after_row_at_call=b""))

    def test_optional_original_binary_opcode_and_initial_mutable_data_proof(self):
        p=os.getenv("FM2001_ORIGINAL_EXE")
        if not p:
            self.skipTest("private original EXE not supplied to CI runner")
        data=Path(p).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x41a5c9:"e8 72 cd ff ff",
            0x41a5ce:"84 c0 75 23",
            0x41a5d2:"8b ce e8 97 cc ff ff",
            0x41a5d9:"8b c8 e8 a0 aa fe ff",
            0x41a5e4:"db 44 24 04",
            0x41a5e8:"d8 1d 28 22 82 00",
            0x41a5ee:"df e0 f6 c4 01",
            0x41a5f5:"8b ce e8 f4 d9 ff ff",
            0x41a600:"6a 0c",
            0x41a61c:"e8 4f b9 1e 00",
            0x41a629:"89 8e 4c 02 00 00",
            0x41a62f:"8a 46 77",
            0x41a632:"8b 15 14 18 82 00",
            0x41a642:"7d 0b",
            0x41a658:"e8 33 b9 1e 00",
            0x417ff0:"8a 41 14 24 01 c3",
            0x605f70:"8b c1 c7 00 ff ff ff ff",
        }
        for va,text in signatures.items():
            with self.subTest(va=hex(va)):
                src=bytes.fromhex(text)
                self.assertEqual(data[va-0x400000:va-0x400000+len(src)],src)
        import struct
        self.assertEqual(struct.unpack_from("<f",data,0x822228-0x400000)[0],14.0)
        self.assertEqual(struct.unpack_from("<i",data,0x821814-0x400000)[0],75)


if __name__=="__main__":
    unittest.main()
