"""Native original 4197C0 qualifying player-row source and GameState regressions."""
from __future__ import annotations
from dataclasses import replace
from datetime import date
from pathlib import Path
from struct import pack_into
import hashlib
import os
import unittest

from game_state import GameCalendar,GameState
from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_4197c0_callbackfree_player_row import (
    Original4197C0SafeRowReached,Original4197C0SafeRowError,
    source_original_4197c0_callbackfree_player_row,
)


def row(a=1,b=0,extra=False):
    return Original5127A0RowCall(
        pass_index=0,row_index=0,
        source_current_team_pointer=0x1000,
        source_opponent_team_pointer=0x2000,
        source_player_pointer=0x3000,
        source_4197c0_arg1=a,
        source_4197c0_arg2=b,
        source_4197c0_arg3=0x2000,
        source_41a5b0_called_after_row=extra,
    )


def player(*,pid=123,card=0,cycle=0,fa=3,uefa=0,
           fa_marker=7,accumulator=0,uefa_progress=0,date_raw=555):
    p=bytearray(0x164)
    pack_into("<H",p,4,pid)
    p[0x139]=card
    p[0x13a]=cycle
    p[0x13b]=fa
    p[0x13c]=fa_marker
    p[0x13d]=uefa_progress
    p[0x13e]=uefa
    p[0x144]=accumulator
    pack_into("<I",p,0x160,date_raw)
    return bytes(p)


def reached(*,a=1,b=0,extra=False,src=None,
            first=0,first_category=None,second=0,second_category=None,
            third=None,v30=0,post=None):
    p=player() if src is None else src
    match=bytearray(0x50)
    pack_into("<I",match,0x4c,0x6000)
    return Original4197C0SafeRowReached(
        original_row=row(a,b,extra),
        original_player_at_entry=p,
        original_player_after_competition_callbacks=p if post is None else post,
        original_match_pointer=0x7000,original_match_record=bytes(match),
        original_competition_owner_pointer=0x6000,
        first_competition_v18_eax=first,
        first_reached_category_34=first_category,
        second_competition_v18_eax=second,
        second_reached_category_34=second_category,
        third_reached_uefa_owner_context_14=third,
        original_5112e0_v30_eax=v30,
    )


def state_for_source(p):
    s=GameState(calendar=GameCalendar(date(2000,7,1)),players={123:object()})
    s.retain_verified_native_player_discipline(
        original_player_record=p,mapped_runtime_player_index=123)
    return s


class Original4197C0SafeRowTests(unittest.TestCase):
    def test_non_uefa_v30_positive_one_card_and_one_accumulator(self):
        source=reached(a=1,v30=1,src=player(fa_marker=8))
        result=source_original_4197c0_callbackfree_player_row(source)
        after=result.original_player_after
        self.assertEqual((after[0x139],after[0x13a],after[0x13c],after[0x144]),
                         (1,1,0,1))
        self.assertEqual((after[0x13b],after[0x13e]),(3,0))
        self.assertEqual(result.original_5112e0_masked_al,1)
        self.assertEqual(result.source_branch,"NON_UEFA_41A490")
        self.assertFalse(result.native_4197c0_executed)
        self.assertTrue(result.external_competition_virtual_world_effects_unverified)

    def test_non_uefa_v30_zero_preserves_accumulator(self):
        result=source_original_4197c0_callbackfree_player_row(
            reached(a=1,v30=0,src=player(accumulator=2)))
        self.assertEqual((result.original_player_after[0x144],
                          result.original_player_after[0x139],
                          result.original_player_after[0x13a]),(2,1,1))
        self.assertEqual(result.source_branch,"NON_UEFA_NO_41A490")
        self.assertFalse(result.source_41a490_accumulator_reached)
        self.assertTrue(result.source_419916_discipline_continuation_reached)

    def test_two_competition_virtuals_distinct_and_uefa_returns_before_card_path(self):
        source=reached(
            a=2,src=player(card=9,cycle=4,uefa_progress=0),
            first=1,first_category=1,second=42,second_category=1,
            third=0x8000,v30=None,
        )
        r=source_original_4197c0_callbackfree_player_row(source)
        self.assertEqual(r.source_branch,"UEFA_41A250")
        self.assertEqual(r.original_player_after[0x13d],2)
        self.assertEqual((r.original_player_after[0x139],
                          r.original_player_after[0x13a]),(9,4))
        self.assertTrue(r.source_41a250_uefa_reached)
        self.assertFalse(r.source_419916_discipline_continuation_reached)
        self.assertIsNone(r.original_5112e0_masked_al)

    def test_full_parent_no_arg1_no_arg2_nonuefa_no_aux_calls(self):
        r=source_original_4197c0_callbackfree_player_row(
            reached(a=0,src=player(cycle=0,card=1),v30=0))
        self.assertEqual(r.original_player_after[0x139:0x13f],
                         player(cycle=0,card=1)[0x139:0x13f])
        self.assertFalse(r.source_419916_discipline_continuation_reached)

    def test_partial_world_and_native_subhandler_cases_fail_closed(self):
        bads=(
            (reached(b=1),"arg2=0"),
            (reached(extra=True),"41A5B0"),
            (reached(a=1,src=player(card=12)),"card threshold"),
            (reached(a=1,src=player(cycle=4)),"13A carry"),
            (reached(a=1,v30=1,src=player(accumulator=1)),"417340"),
            (reached(a=0,src=player(cycle=2)),"early 417EE0"),
            (reached(a=1,second=1,second_category=1,third=0x8000,v30=None),
             "extra"), # staged below with actual UEFA counter example
        )
        for rec,msg in bads[:-1]:
            with self.subTest(message=msg),self.assertRaisesRegex(Original4197C0SafeRowError,msg):
                source_original_4197c0_callbackfree_player_row(rec)
        with self.assertRaisesRegex(Original4197C0SafeRowError,"41A250"):
            source_original_4197c0_callbackfree_player_row(
                reached(a=3,second=1,second_category=1,third=0x8000,v30=None))

    def test_wrong_reached_getter_order_and_player_identity_fail_closed(self):
        bads=(
            (replace(reached(),first_reached_category_34=1),"first competition"),
            (replace(reached(),second_reached_category_34=1),"second competition"),
            (replace(reached(),third_reached_uefa_owner_context_14=0x9000),
             "non-UEFA"),
            (replace(reached(),original_5112e0_v30_eax=None),"5112E0"),
            (replace(reached(),original_5112e0_v30_eax=0x101),"already masked"),
            (replace(reached(),original_match_record=b""),r"match\+4C"),
            (replace(reached(),original_competition_owner_pointer=0x9999),
             "pointer mismatch"),
            (replace(reached(),original_player_after_competition_callbacks=player(card=1)),
             "must match"),
            (replace(reached(),original_match_pointer=0),"match pointer"),
        )
        for rec,msg in bads:
            with self.subTest(message=msg),self.assertRaisesRegex(Original4197C0SafeRowError,msg):
                source_original_4197c0_callbackfree_player_row(rec)

    def test_live_atomic_native_state_update_without_generic_fields(self):
        p=player(fa=2,fa_marker=7,accumulator=0)
        state=state_for_source(p)
        before=state.native_player_discipline[123]
        matched=reached(a=1,src=p,v30=1)
        after=state.apply_verified_native_4197c0_callbackfree_player_row(
            original_reached=matched,mapped_runtime_player_index=123)
        self.assertEqual((after.native_139,after.native_13a,
                          after.native_13c,after.native_incident_accumulator_144),
                         (1,1,0,1))
        self.assertEqual(after.native_fa_counter_13b,2)
        self.assertNotEqual(after,before)
        self.assertEqual(state.native_player_discipline[123],after)
        self.assertEqual(state.native_status_world.players,{})
        self.assertFalse(state.original_pending_transfer_eam.entries)
        self.assertFalse(state.original_delivered_mailboxes.mailboxes)
        current=state.native_player_discipline.copy()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_4197c0_callbackfree_player_row(
                original_reached=matched,mapped_runtime_player_index=123)
        self.assertEqual(state.native_player_discipline,current)

    def test_live_callback_unsafe_parent_does_not_partially_update(self):
        p=player(accumulator=1)
        state=state_for_source(p)
        before=state.native_player_discipline.copy()
        with self.assertRaisesRegex(Original4197C0SafeRowError,"417340"):
            state.apply_verified_native_4197c0_callbackfree_player_row(
                original_reached=reached(a=1,src=p,v30=1),
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_player_discipline,before)

    def test_internal_save_roundtrip_and_old_source_records_remain_optional(self):
        from internal_save import snapshot_human_gameplay,restore_human_gameplay
        from test_internal_save import InternalSaveTests
        from test_human_gameplay import Database,coefficient_matrix
        ctrl=InternalSaveTests().build_controller()
        runtime=ctrl.squad()[0]
        p=player(pid=runtime.index)
        ctrl.state.retain_verified_native_player_discipline(
            original_player_record=p,mapped_runtime_player_index=runtime.index)
        # Existing game state save remains the same schema and sparse
        # original-native record serialization after a reached source row.
        task=reached(src=p,v30=1)
        ctrl.state.apply_verified_native_4197c0_callbackfree_player_row(
            original_reached=task,mapped_runtime_player_index=runtime.index)
        before=ctrl.state.native_player_discipline[runtime.index]
        data=snapshot_human_gameplay(ctrl)
        self.assertEqual(data["schema_version"],48)
        restored=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),data)
        self.assertEqual(restored.state.native_player_discipline[runtime.index],before)
        self.assertEqual(restored.state.native_status_world.players,{})

    def test_private_original_source_opcode_signatures_when_available(self):
        source=os.getenv("FM2001_ORIGINAL_EXE")
        if not source:
            self.skipTest("private native original executable not available in CI")
        pe=Path(source).read_bytes()
        self.assertEqual(hashlib.sha256(pe).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x4197c2:"8b 6c 24 10",
            0x4197cc:"74 37",
            0x419805:"8b 7c 24 20 8b 4f 4c",
            0x419815:"ff 52 18",
            0x41984c:"8b 4f 4c e8 6c a5 0d 00",
            0x41985b:"85 c0 74 2a",
            0x41987d:"e8 ce 09 00 00",
            0x419889:"8b cf e8 50 7a 0f 00",
            0x419898:"55 53 8b ce e8 ef 0b 00 00",
            0x4198a3:"85 ed 74 6f",
            0x419916:"85 db 0f 84 b1 00 00 00",
            0x419925:"8a 86 39 01 00 00",
            0x419933:"f7 f9 83 fa 0c",
            0x419970:"8a 86 39 01 00 00",
            0x41997c:"02 c3 02 d3",
            0x419988:"3c 05",
            0x5112e0:"8b 49 4c 8b 01 ff 50 30 25 ff 00 00 00",
        }
        for addr,hex_bytes in signatures.items():
            with self.subTest(native_va=hex(addr)):
                pat=bytes.fromhex(hex_bytes)
                self.assertEqual(pe[addr-0x400000:addr-0x400000+len(pat)],pat)


if __name__=="__main__":
    unittest.main()
