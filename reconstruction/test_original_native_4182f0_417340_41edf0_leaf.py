"""Original 4182F0 human/41EDF0 role and quota source + GameState tests."""
from __future__ import annotations

from dataclasses import replace
from datetime import date
from struct import pack_into,unpack_from
import unittest

from game_state import GameState,GameCalendar
from original_native_409c90_assignment_status import Original409C90SourceError
from original_native_4182f0_417340_41edf0_leaf import (
    source_original_4182f0_417340_optional_41edf0_leaf,
)
from original_native_417340_registered_user_gate import (
    Original417340ReachedUser,
    source_original_417340_registered_user_from_reached,
)
from original_native_41edf0_registered_quota import Original41EDF0Reached
from test_original_native_status_world_state import native_player


STATUS=b"\x17\x18\x00\xe5\xc3"
POINTER=0x3000


def after_local_stores(p):
    raw=bytearray(p)
    pack_into("<I",raw,0x14,(unpack_from("<I",p,0x14)[0]|0x10)&~0x20)
    flags174=unpack_from("<I",p,0x174)[0]
    if flags174&1:
        raw[0x152]=STATUS[3]&31
        raw[0x153]=STATUS[4]&15
    pack_into("<I",raw,0x174,flags174&~3)
    return bytes(raw)


def qualified_user_receipt(player,matched):
    club=bytearray(8)
    pack_into("<I",club,4,2)
    owner=bytearray(0x9d0)
    links=()
    if matched:
        pack_into("<I",owner,0x9cc,0x1000)
        link=bytearray(8);pack_into("<I",link,0,0x2000)
        user=bytearray(0x5b8);pack_into("<I",user,0x5b4,0x7000)
        context=bytearray(8);pack_into("<I",context,4,2)
        links=(Original417340ReachedUser(
            0x1000,bytes(link),0x2000,bytes(user),0x7000,bytes(context)),)
    return source_original_417340_registered_user_from_reached(
        original_player_at_call=player,
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=None,
        original_reached_club_pointer=0x50000+680*2,
        original_reached_club_record=bytes(club),
        original_global_874c10_record=bytes(owner),
        original_reached_manager_links=links)


def quota_receipt(player,amount=5):
    club=bytearray(0x1ac)
    pack_into("<i",club,0x1a8,amount)
    return Original41EDF0Reached(
        original_player_at_call=player,
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=0x60000,
        original_registered_club_pointer=0x50000+680*3,
        original_registered_club_record=bytes(club))


def stage_args(p,*,matched=False,include_41edf0=False,club_counter=5):
    post=after_local_stores(p)
    return dict(
        original_native_player_pointer=0x9000,
        original_player_before_4182f0=p,
        original_status_before_4182f0=STATUS,
        original_417340_source_receipt=qualified_user_receipt(post,matched),
        original_41edf0_source_if_reached=(
            quota_receipt(post,club_counter) if include_41edf0 and
            (unpack_from("<I",post,0x14)[0]&0x1000) else
            Original41EDF0Reached(original_player_at_call=post)
            if include_41edf0 else None))


def game_state(p):
    pid=unpack_from("<H",p,4)[0]
    state=GameState(calendar=GameCalendar(date(2000,7,1)),players={pid:object()})
    state.retain_verified_native_status_world(
        original_player_record=p,original_role_object_pointer=POINTER,
        original_role_object_record=STATUS,mapped_runtime_player_index=pid)
    state.native_status_world.registered_club_quotas[3]=5
    return state


def world_apply(state,args,pid=123):
    return state.apply_verified_native_4182f0_assignment_leaf(
        **args,original_source_status_pointer=POINTER,
        mapped_runtime_player_index=pid)


class Original4182F0LeafTests(unittest.TestCase):
    def test_complete_human_skip_and_nonhuman_bit13_skip_with_swap(self):
        for flags,matched in ((0x1000,True),(0x2000,False),(0x0,True)):
            with self.subTest(flags=flags,matched=matched):
                p=native_player(status=flags,reserve=3,role=0xA6,aux=0xB9)
                args=stage_args(p,matched=matched)
                state=game_state(p)
                generic=state.players[123]
                out=world_apply(state,args)
                after=state.native_status_world.players[123]
                self.assertFalse(out.original_41edf0_was_reached)
                self.assertIsNone(out.original_41edf0_quota_if_reached)
                self.assertEqual(after.original_status_14,(flags|0x10)&~0x20)
                self.assertEqual(after.original_reserve_selection_174,0)
                self.assertEqual((after.original_reserve_role_152,after.original_reserve_aux_153),(5,3))
                self.assertEqual((after.original_role_object_byte_3,after.original_role_object_byte_4),
                                 (0xE6,0xC9))
                self.assertEqual(state.native_status_world.registered_club_quotas[3],5)
                self.assertIs(state.players[123],generic)

    def test_41edf0_reached_unset_bit12_skips_quota_and_set_bit12_decrements(self):
        for flags,expected_flags,quota_changed in (
            (0,0x10,False),
            (0x1000,0x10,True),
            (0x1000|0x20,0x10,True),
        ):
            with self.subTest(flags=flags):
                p=native_player(status=flags,reserve=2,role=0xA6,aux=0xB9)
                args=stage_args(p,include_41edf0=True)
                state=game_state(p)
                out=world_apply(state,args)
                after=state.native_status_world.players[123]
                self.assertTrue(out.original_41edf0_was_reached)
                self.assertEqual(after.original_status_14,expected_flags)
                self.assertEqual(after.original_reserve_selection_174,0)
                self.assertEqual((after.original_reserve_role_152,after.original_reserve_aux_153),
                                 (0xA6,0xB9))
                self.assertEqual((after.original_role_object_byte_3,after.original_role_object_byte_4),
                                 (0xE5,0xC3))
                self.assertEqual(state.native_status_world.registered_club_quotas[3],
                                 4 if quota_changed else 5)

    def test_wrong_user_skip_wrong_quota_and_stale_source_are_atomic(self):
        p=native_player(status=0x1000,reserve=3,role=0xA6,aux=0xB9)
        args=stage_args(p,include_41edf0=True)
        state=game_state(p)
        baseline=state.native_status_world.snapshot()
        for name,changed in (
            ("skipped_quota",{"original_41edf0_source_if_reached":None}),
            ("bad_original_player_ptr",{"original_native_player_pointer":0}),
            ("bad_manager_source",{"original_417340_source_receipt":
                replace(args["original_417340_source_receipt"],original_417340_return_al=1)}),
            ("wrong_callback_input",{"original_41edf0_source_if_reached":
                replace(args["original_41edf0_source_if_reached"],
                        original_player_at_call=p)}),
        ):
            with self.subTest(name=name),self.assertRaises(ValueError):
                world_apply(state,args|changed)
            self.assertEqual(state.native_status_world.snapshot(),baseline)
        with self.assertRaises(ValueError):
            world_apply(state,args,pid=999)
        self.assertEqual(state.native_status_world.snapshot(),baseline)
        bad_quota=game_state(p)
        bad_quota.native_status_world.registered_club_quotas[3]=4
        old=bad_quota.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"quota absent or stale"):
            world_apply(bad_quota,args)
        self.assertEqual(bad_quota.native_status_world.snapshot(),old)
        wrong_ptr=game_state(p)
        with self.assertRaises(ValueError):
            wrong_ptr.apply_verified_native_4182f0_assignment_leaf(
                **args,original_source_status_pointer=0x3001,
                mapped_runtime_player_index=123)
        self.assertEqual(wrong_ptr.native_status_world.snapshot(),baseline)
        world_apply(state,args)
        committed=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            world_apply(state,args)
        self.assertEqual(state.native_status_world.snapshot(),committed)

        human=stage_args(p,matched=True)
        with self.assertRaisesRegex(Original409C90SourceError,"unreached"):
            source_original_4182f0_417340_optional_41edf0_leaf(
                **(human|{"original_41edf0_source_if_reached":
                    args["original_41edf0_source_if_reached"]}))

    def test_full_controller_roundtrip_after_native_registered_quota(self):
        from test_internal_save import InternalSaveTests
        from test_human_gameplay import Database,coefficient_matrix
        from internal_save import snapshot_human_gameplay,restore_human_gameplay
        controller=InternalSaveTests().build_controller()
        generic=controller.squad()[0]
        generic_before=(generic.suspended,generic.reserve_active,
                        generic.saved_reserve_role_152,generic.suspension_matches_remaining)
        p=native_player(pid=generic.index,status=0x1000,reserve=3,role=0xA6,aux=0xB9)
        controller.state.retain_verified_native_status_world(
            original_player_record=p,original_role_object_pointer=POINTER,
            original_role_object_record=STATUS,mapped_runtime_player_index=generic.index)
        controller.state.native_status_world.registered_club_quotas[3]=5
        stage=controller.state.apply_verified_native_4182f0_assignment_leaf(
            **stage_args(p,include_41edf0=True),
            original_source_status_pointer=POINTER,
            mapped_runtime_player_index=generic.index)
        self.assertEqual(stage.original_41edf0_quota_if_reached.original_registered_club_counter_after,4)
        snapshot=snapshot_human_gameplay(controller)
        self.assertEqual(snapshot["schema_version"],48)
        restored=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),snapshot)
        self.assertEqual(restored.state.native_status_world,controller.state.native_status_world)
        generic_after=restored.state.players[generic.index]
        self.assertEqual((generic_after.suspended,generic_after.reserve_active,
                          generic_after.saved_reserve_role_152,
                          generic_after.suspension_matches_remaining),generic_before)


if __name__=="__main__":
    unittest.main()
