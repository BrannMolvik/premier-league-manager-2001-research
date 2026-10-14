"""Original post-row 419680 current manager status availability, full source guards."""
from __future__ import annotations
from dataclasses import replace
from datetime import date
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from game_state import GameState,GameCalendar
from original_native_419680_availability import (
    Original419680Reached,Original419680SourceError,
    source_original_419680_availability_from_reached,
)
from original_native_417340_registered_user_gate import (
    Original417340ReachedUser,
    source_original_417340_registered_user_from_reached,
)


ROLE=b"\x00\x00\x00\x13\xa7"


def player(*,id=123,fa=3,uefa=2,flags=0x20,
           current=2,registered=3,raw_date=5):
    p=bytearray(0x24c)
    pack_into("<H",p,4,id)
    pack_into("<h",p,0x10,current)
    pack_into("<h",p,0x72,registered)
    pack_into("<I",p,0x14,flags)
    pack_into("<I",p,0x174,2)
    pack_into("<I",p,0x248,0x3000)
    p[0x13b]=fa
    p[0x13e]=uefa
    p[0x152]=0x13
    p[0x153]=7
    pack_into("<I",p,0x160,raw_date)
    return bytes(p)


def manager_proof(p, *,matching=True):
    club=bytearray(8)
    team_idx=unpack_from("<h",p,0x10)[0]
    pack_into("<I",club,4,team_idx)
    owner=bytearray(0x9d0)
    pack_into("<I",owner,0x9cc,0x1000)
    node=bytearray(8)
    pack_into("<I",node,0,0x2000)
    user=bytearray(0x5b8)
    pack_into("<I",user,0x5b4,0x3000)
    ctx=bytearray(8)
    pack_into("<I",ctx,4,team_idx if matching else team_idx+1)
    link=Original417340ReachedUser(
        0x1000,bytes(node),0x2000,bytes(user),0x3000,bytes(ctx))
    return source_original_417340_registered_user_from_reached(
        original_player_at_call=p,
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=None,
        original_reached_club_pointer=0x50000+680*team_idx,
        original_reached_club_record=bytes(club),
        original_global_874c10_record=bytes(owner),
        original_reached_manager_links=(link,),
    )


def reached(*,p=None,lookup=0,v18=None,cat=None,date_raw=None,user=None):
    return Original419680Reached(
        original_player_at_entry=player() if p is None else p,
        original_calendar_lookup_pointer=lookup,
        original_competition_v18_eax=v18,
        original_second_competition_34=cat,
        original_510a20_reached_date_raw=date_raw,
        original_417340_registered_owner_proof=user,
    )


def state_for_player(p):
    s=GameState(calendar=GameCalendar(date(2000,7,1)),
                players={unpack_from("<H",p,4)[0]:object()})
    idx=unpack_from("<H",p,4)[0]
    s.retain_verified_native_player_discipline(
        original_player_record=p,mapped_runtime_player_index=idx)
    s.retain_verified_native_status_world(
        original_player_record=p,
        original_role_object_pointer=0x3000,
        original_role_object_record=ROLE,
        mapped_runtime_player_index=idx)
    return s


class Original419680AvailabilityTests(unittest.TestCase):
    def test_null_calendar_lookup_sets_fa_bit1_without_any_other_callback(self):
        p=player(fa=2,uefa=0,flags=0x20)
        out=source_original_419680_availability_from_reached(reached(p=p))
        self.assertEqual(unpack_from("<I",out.original_player_after,0x14)[0],0x22)
        self.assertTrue(out.original_status_bit1_source_or_branch)
        self.assertFalse(out.original_calendar_lookup_nonnull)
        self.assertFalse(out.original_fa_due_date_checked)
        self.assertFalse(out.original_417340_eligibility_callback_reached)
        self.assertFalse(out.original_competition_virtual_world_effects_unverified)
        self.assertFalse(out.original_510a20_world_effects_unverified)
        self.assertFalse(out.original_419680_native_callback_executed)

    def test_null_lookup_has_no_uefa_fallback_and_preserves_other_bits(self):
        p=player(fa=0,uefa=7,flags=0x80)
        out=source_original_419680_availability_from_reached(reached(p=p))
        self.assertEqual(out.original_player_after,p)
        self.assertFalse(out.original_status_bit1_source_or_branch)
        with self.assertRaisesRegex(Original419680SourceError,"NULL original calendar"):
            source_original_419680_availability_from_reached(
                reached(p=p,date_raw=10))

    def test_nonnull_uefa_status_selection_returns_without_fa_even_when_due(self):
        p=player(fa=4,uefa=0,flags=0x20,raw_date=0)
        none=source_original_419680_availability_from_reached(
            reached(p=p,lookup=0x8000,v18=1,cat=1))
        self.assertEqual(none.original_player_after,p)
        self.assertTrue(none.original_league_uefa_source_owner_34_one)
        self.assertFalse(none.original_fa_due_date_checked)
        qualified=source_original_419680_availability_from_reached(
            reached(p=player(fa=0,uefa=1),lookup=0x8000,v18=5,cat=1))
        self.assertTrue(qualified.original_status_bit1_source_or_branch)
        self.assertEqual(unpack_from("<I",qualified.original_player_after,0x14)[0],0x22)
        self.assertTrue(qualified.original_competition_virtual_world_effects_unverified)
        with self.assertRaisesRegex(Original419680SourceError,"before FA"):
            source_original_419680_availability_from_reached(
                reached(p=p,lookup=0x8000,v18=1,cat=1,date_raw=10))

    def test_nonnull_fa_due_signed_date_sets_bit_even_manager_al_zero(self):
        p=player(fa=2,uefa=0,raw_date=0xfffffffe)
        user=manager_proof(p,matching=False)
        self.assertEqual(user.original_417340_return_al,0)
        r=source_original_419680_availability_from_reached(
            reached(p=p,lookup=0x8000,v18=0,date_raw=0,user=user))
        self.assertEqual(unpack_from("<I",r.original_player_after,0x14)[0],0x22)
        self.assertTrue(r.original_fa_due_date_checked)
        self.assertTrue(r.original_417340_eligibility_callback_reached)
        self.assertTrue(r.original_510a20_world_effects_unverified)
        self.assertFalse(r.original_419680_native_callback_executed)

    def test_not_due_fa_and_no_fa_skip_registered_user_lookup(self):
        p=player(fa=2,uefa=1,raw_date=11)
        not_yet=source_original_419680_availability_from_reached(
            reached(p=p,lookup=0x8000,v18=1,cat=2,date_raw=10))
        self.assertFalse(not_yet.original_status_bit1_source_or_branch)
        self.assertTrue(not_yet.original_fa_due_date_checked)
        with self.assertRaisesRegex(Original419680SourceError,"not-yet-due"):
            source_original_419680_availability_from_reached(
                reached(p=p,lookup=0x8000,v18=0,date_raw=10,
                        user=manager_proof(p)))
        zero=source_original_419680_availability_from_reached(
            reached(p=player(fa=0),lookup=0x8000,v18=0))
        self.assertFalse(zero.original_fa_due_date_checked)

    def test_wrong_source_callback_order_and_unverified_owner_fails_closed(self):
        p=player()
        bad=[
            (reached(p=p,lookup=0x8000),"virtual"),
            (reached(p=p,lookup=0x8000,v18=0,cat=1),"skips second"),
            (reached(p=p,lookup=0x8000,v18=1),"second competition"),
            (reached(p=p,lookup=0x8000,v18=0),"510A20"),
            (reached(p=p,lookup=0x8000,v18=0,date_raw=10),"417340 user"),
            (reached(p=p,lookup=0x8000,v18=0,date_raw=10,
                     user=manager_proof(player(fa=0))),"exact at-call"),
            (reached(p=b""),"through"),
        ]
        for item,expression in bad:
            with self.subTest(pattern=expression),self.assertRaisesRegex(
                Original419680SourceError,expression):
                source_original_419680_availability_from_reached(item)

    def test_live_state_bit1_saved_only_after_source_current_world_verification(self):
        p=player(fa=3,uefa=1,flags=0x20)
        state=state_for_player(p)
        before_discipline=state.native_player_discipline.copy()
        before_roles=state.native_status_world.players[123]
        status=state.apply_verified_native_419680_availability(
            original_reached=reached(p=p),mapped_runtime_player_index=123)
        self.assertTrue(status.original_status_bit1_source_or_branch)
        after=state.native_status_world.players[123]
        self.assertEqual(after.original_status_14,0x22)
        self.assertEqual(after.original_role_object_byte_3,before_roles.original_role_object_byte_3)
        self.assertEqual(after.original_role_object_byte_4,before_roles.original_role_object_byte_4)
        self.assertEqual(state.native_player_discipline,before_discipline)
        self.assertEqual(state.native_status_world.registered_club_quotas,{})
        self.assertFalse(state.original_pending_transfer_eam.entries)
        self.assertFalse(state.original_delivered_mailboxes.mailboxes)
        copy=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_419680_availability(
                original_reached=reached(p=p),mapped_runtime_player_index=123)
        self.assertEqual(state.native_status_world.snapshot(),copy)

    def test_live_status_not_mutated_when_417340_callback_proof_fails(self):
        p=player(fa=2,raw_date=2)
        state=state_for_player(p)
        before=state.native_status_world.snapshot()
        with self.assertRaisesRegex(Original419680SourceError,"417340"):
            state.apply_verified_native_419680_availability(
                original_reached=reached(p=p,lookup=0x9000,v18=0,
                                         date_raw=5),
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_status_world.snapshot(),before)
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            changed=player(fa=0,raw_date=2)
            state.apply_verified_native_419680_availability(
                original_reached=reached(p=changed),
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_status_world.snapshot(),before)

    def test_gameplay_internal_save_roundtrip_and_generic_status_unchanged(self):
        from test_internal_save import InternalSaveTests
        from test_human_gameplay import Database,coefficient_matrix
        from internal_save import snapshot_human_gameplay,restore_human_gameplay
        controller=InternalSaveTests().build_controller()
        runtime=controller.squad()[0]
        generic_before=(runtime.suspended,
                        runtime.suspension_matches_remaining,
                        runtime.reserve_active)
        p=player(id=runtime.index,fa=2,flags=0x20)
        controller.state.retain_verified_native_player_discipline(
            original_player_record=p,mapped_runtime_player_index=runtime.index)
        controller.state.retain_verified_native_status_world(
            original_player_record=p,
            original_role_object_pointer=0x3000,
            original_role_object_record=ROLE,
            mapped_runtime_player_index=runtime.index)
        controller.state.apply_verified_native_419680_availability(
            original_reached=reached(p=p),mapped_runtime_player_index=runtime.index)
        saved=snapshot_human_gameplay(controller)
        self.assertEqual(saved["schema_version"],48)
        restored=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),saved)
        self.assertEqual(restored.state.native_status_world.players[runtime.index].original_status_14,
                         0x22)
        self.assertEqual(restored.state.native_player_discipline[runtime.index].native_fa_counter_13b,2)
        runtime_after=restored.state.players[runtime.index]
        self.assertEqual(
            (runtime_after.suspended,runtime_after.suspension_matches_remaining,
             runtime_after.reserve_active),generic_before)

    def test_canonical_private_original_pe_opcode_signatures(self):
        file=os.getenv("FM2001_ORIGINAL_EXE")
        if not file:
            self.skipTest("private source executable intentionally absent from CI")
        pe=Path(file).read_bytes()
        self.assertEqual(hashlib.sha256(pe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        patterns={
            0x419681:"8b 74 24 08",0x419688:"85 f6 74 7c",
            0x419690:"ff 50 18",0x41969f:"ff 52 18",
            0x4196b5:"83 78 34 01",0x4196bb:"8a 87 3e 01 00 00",
            0x4196c5:"8b 47 14 0c 02",0x4196d2:"8a 87 3b 01 00 00",
            0x4196e3:"e8 38 73 0f 00",0x4196ea:"8b 8f 60 01 00 00",
            0x4196f0:"3b c8 7f 26",0x4196f6:"e8 45 dc ff ff",
            0x4196fb:"8b 47 14 0c 02",0x419708:"8a 87 3b 01 00 00",
            0x419715:"0c 02",0x5128f0:"33 f6 85 c0 74 34",
            0x512910:"51 8b c8 e8 68 6d f0 ff",
        }
        for va,source in patterns.items():
            with self.subTest(native_va=hex(va)):
                v=bytes.fromhex(source)
                self.assertEqual(pe[va-0x400000:va-0x400000+len(v)],v)


if __name__=="__main__":
    unittest.main()
