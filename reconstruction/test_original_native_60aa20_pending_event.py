"""Original 606540->60AA20 nonhuman event-state prequeue source tests."""
from __future__ import annotations

from dataclasses import replace
from struct import pack_into,unpack_from
from pathlib import Path
import hashlib
import os
import unittest

from original_native_41a5b0_extra_event import source_original_41a5b0_optional_extra_from_reached
from test_original_native_41a5b0_extra_event import staged,manager_proof
from original_native_605f90_dispatch import (
    Original605F90ReachedCall,Original605F90Thresholds,
    Original606540Reached,source_original_605f90_predispatch_from_reached,
    source_original_606540_pre_human_from_reached,
)
from test_original_native_605f90_dispatch import ADD1,INIT1
from original_native_60aa20_pending_event import (
    Original60AA20SourceError,Original60AA20NonhumanReached,
    source_original_60aa20_nonhuman_pending_from_reached,
)


def reached(*,draw=0,rng4=None,first606540=10,source77=60,initial22=254,
            status=0,global_day=100,manager=False):
    original_source=staged(
        registered=False,count=14,source_float=14.0,
        source_77=source77,status=status,threshold=75,
    )
    raw=bytearray(original_source.original_player_after_row_at_call)
    raw[0x22]=initial22
    # A new reached post-row player must be qualified against the corresponding
    # exact player-byte registered-human proof, not against an earlier snapshot.
    original_source=replace(
        original_source,
        original_player_after_row_at_call=bytes(raw),
        original_registered_417340_owner_proof=manager_proof(bytes(raw),registered=False))
    receipt=source_original_41a5b0_optional_extra_from_reached(original_source)
    allocated=bytearray(raw)
    pack_into("<I",allocated,0x24c,0x6000)
    d=bytearray(12)
    pack_into("<I",d,0,0xffffffff)
    d[4]=3;d[5]=4
    prematch=source_original_605f90_predispatch_from_reached(
        Original605F90ReachedCall(
            original_caller=receipt,
            original_allocated_descriptor_pointer=0x6000,
            original_descriptor_after_605f70=bytes(d),
            original_player_after_41a5b0_pointer_store=bytes(allocated),
            original_first_resolved_native_player=bytes(allocated),
            original_second_resolved_native_player=bytes(allocated),
            original_rng100_result=draw,
            original_mutable_thresholds=Original605F90Thresholds(ADD1,INIT1),
        )
    )
    if first606540<50:
        sub=Original606540Reached(
            prematch,first606540,50,original_82232c_short_base=10)
    elif first606540<80:
        sub=Original606540Reached(
            prematch,first606540,50,
            original_822324_second_threshold=80,
            original_second_rng4_result=rng4,
            original_822330_medium_base=35)
    else:
        sub=Original606540Reached(
            prematch,first606540,50,
            original_822324_second_threshold=80,
            original_822328_third_threshold=95,
            original_second_rng4_result=rng4,
            original_822334_long_base=60)
    stage=source_original_606540_pre_human_from_reached(sub)
    proof=manager_proof(bytes(allocated),registered=manager)
    return Original60AA20NonhumanReached(
        original_606540_predispatch=stage,
        original_descriptor_at_60aa20=stage.original_source_descriptor_before_417340,
        original_descriptor_pointer=0x6000,
        original_player_at_60aa20=bytes(allocated),
        original_registered_606540_proof=proof,
        original_registered_60aa20_proof=proof,
        original_raw_global_calendar_day_9847fc=global_day,
    )


class Original60AA20NonhumanTests(unittest.TestCase):
    def test_606540_short_source_sets_bit0_age_score_and_separate_pending(self):
        r=source_original_60aa20_nonhuman_pending_from_reached(reached())
        p=r.original_player_after_41a860_and_60aa20
        desc=r.original_descriptor_after_60aa20
        self.assertEqual(unpack_from("<I",p,0x14)[0],1)
        self.assertEqual(p[0x22],255)
        self.assertEqual(p[0x77],50)   # 60 - short original base 10
        self.assertEqual(unpack_from("<I",desc,0)[0],107)
        self.assertEqual(desc[5],0)
        self.assertEqual(r.original_pending_event_candidate.original_event_vtable,0x7d7760)
        self.assertEqual(r.original_pending_event_candidate.original_due_day_raw,107)
        self.assertEqual(r.original_pending_event_candidate.original_player_id,123)
        self.assertFalse(r.original_pending_event_candidate.original_delivery_verified)
        self.assertFalse(r.original_pending_event_candidate.original_947aa8_pending_queue_changed)
        self.assertEqual(r.original_native_rng5_draws,0)
        self.assertFalse(r.native_41a860_callback_executed)
        self.assertFalse(r.live_game_state_updated)

    def test_medium_source_uses_rng4_duration_and_byte22_plus_four(self):
        x=reached(first606540=65,rng4=0,initial22=254,source77=60)
        r=source_original_60aa20_nonhuman_pending_from_reached(x)
        p=r.original_player_after_41a860_and_60aa20
        self.assertEqual(r.original_duration_after_native_mitigation,3)
        self.assertEqual(unpack_from("<I",r.original_descriptor_after_60aa20,0)[0],121)
        self.assertEqual(p[0x77],25)
        self.assertEqual(p[0x22],2)
        self.assertEqual(r.original_pending_event_candidate.original_subtype_status_5,1)

    def test_long_source_byte22_plus_eight_and_age_clamps_to_one(self):
        for draw,cat in ((85,2),(97,3)):
            x=reached(first606540=draw,rng4=2,initial22=253,source77=60)
            r=source_original_60aa20_nonhuman_pending_from_reached(x)
            self.assertEqual(r.original_duration_after_native_mitigation,13)
            self.assertEqual(r.original_player_after_41a860_and_60aa20[0x77],1)
            self.assertEqual(r.original_player_after_41a860_and_60aa20[0x22],5)
            self.assertEqual(r.original_pending_event_candidate.original_subtype_status_5,cat)
            self.assertEqual(unpack_from("<I",r.original_descriptor_after_60aa20,0)[0],191)

    def test_original_date_is_raw_dword_and_wraps_without_guessed_epoch(self):
        x=reached(global_day=0xfffffffe)
        r=source_original_60aa20_nonhuman_pending_from_reached(x)
        self.assertEqual(r.original_pending_event_candidate.original_due_day_raw,5)

    def test_human_owner_must_not_skip_native_rng5_and_manager_callbacks(self):
        x=reached(manager=True)
        with self.assertRaisesRegex(Original60AA20SourceError,"nonhuman predicate"):
            source_original_60aa20_nonhuman_pending_from_reached(x)
        x=reached()
        with self.assertRaisesRegex(Original60AA20SourceError,"nonhuman predicate"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_registered_60aa20_proof=manager_proof(x.original_player_at_60aa20,registered=True)))

    def test_forged_source_descriptor_player_and_day_fail_without_writes(self):
        x=reached()
        with self.assertRaisesRegex(Original60AA20SourceError,"descriptor changed"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_descriptor_at_60aa20=bytes(12)))
        with self.assertRaisesRegex(Original60AA20SourceError,"pointer identity"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_descriptor_pointer=0x5000))
        with self.assertRaisesRegex(Original60AA20SourceError,"calendar DWORD"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_raw_global_calendar_day_9847fc=-1))
        source=bytearray(x.original_player_at_60aa20)
        pack_into("<H",source,4,999)
        with self.assertRaisesRegex(Original60AA20SourceError,"identity"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_player_at_60aa20=bytes(source)))
        with self.assertRaisesRegex(Original60AA20SourceError,"nonhuman predicate"):
            source_original_60aa20_nonhuman_pending_from_reached(
                replace(x,original_registered_606540_proof=manager_proof(bytes(source),registered=False)))

    def test_native_sha_source_opcodes_and_pending_event_vtable(self):
        filename=os.getenv("FM2001_ORIGINAL_EXE")
        if not filename:
            self.skipTest("original EXE not stored in repository")
        exe=Path(filename).read_bytes()
        self.assertEqual(hashlib.sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x60aa20:"51 53 8b d9 8b 0d 44 56 87 00",
            0x60aa3c:"e8 ff c8 e0 ff",
            0x60aa41:"84 c0",
            0x60aacd:"8d 34 ed 00 00 00 00",
            0x60aad9:"e8 82 fd e0 ff",
            0x60aae5:"8d 04 0e",
            0x60aae8:"89 03",
            0x60aafd:"3b cb",
            0x60ab21:"8b 5c 24 10",
            0x60ab2a:"83 f8 03",
            0x60ab75:"88 08",
            0x60ab77:"6a 14",
            0x60ab9b:"c7 00 60 77 7d 00",
            0x60aba7:"6a 04",
            0x60abdd:"e8 de 92 00 00",
            0x41a860:"8b 41 14 0c 01 89 41 14",
        }
        for va,hexes in signatures.items():
            with self.subTest(va=hex(va)):
                signature=bytes.fromhex(hexes)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(signature)],signature)
        self.assertEqual(unpack_from("<I",exe,0x7d7760-0x400000+16)[0],0x5d7b40)


if __name__ == "__main__":
    unittest.main()
