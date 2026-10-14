"""Source-native +14/+174/role-object/registered club GameState atomic save tests."""
from __future__ import annotations
from dataclasses import replace
from datetime import date
from struct import pack_into, unpack_from
import unittest

from game_state import GameCalendar, GameState
from original_native_status_world_state import (
    OriginalNativeWorldStateError,OriginalNativeStatusWorldState,
    OriginalNativePlayerStatusWorld,source_native_registered_key,
    source_native_player_status_world_from_reached,
)
from original_native_4085d0_world_branch import (
    Original4085D0ReachedWorld,
)
from original_native_417340_registered_user_gate import (
    Original417340ReachedUser,
    source_original_417340_registered_user_from_reached,
)
from original_native_41edf0_registered_quota import Original41EDF0Reached


def native_player(pid=123, *, status=0x1020, reserve=3, role=0x16,
                  aux=5, current=2, registered=3, source_ptr=0x3000):
    p=bytearray(0x24c)
    pack_into("<H",p,4,pid)
    pack_into("<h",p,0x10,current)
    pack_into("<h",p,0x72,registered)
    pack_into("<I",p,0x14,status)
    pack_into("<I",p,0x174,reserve)
    pack_into("<I",p,0x248,source_ptr)
    p[0x152]=role
    p[0x153]=aux
    return bytes(p)


SOURCE_ROLE=b"\x00\x00\x00\x13\xa7"


def reached_player(player):
    team=bytearray(8)
    pack_into("<I",team,4,unpack_from("<h",player,0x10)[0])
    team_index=unpack_from("<h",player,0x10)[0]
    return Original4085D0ReachedWorld(
        original_team_owner_pointer=(0x60000 if team_index<0 else
                                     0x50000+680*team_index),
        original_team_owner_record=bytes(team),
        original_player_pointer=0x2000,
        original_player_at_entry=player,
        original_407060_eax=0,
        original_4ea3c0_source_object_pointer=0x3000,
        original_4ea3c0_source_object=SOURCE_ROLE,
        original_406be0_eax=1,
        original_5f0d20_eax=2,
    )


def proof(reached, *, manager_key=99):
    from original_native_418220_role_swap import source_original_418220_role_swap_from_reached
    staged=bytearray(reached.original_player_at_entry)
    old_status=unpack_from("<I",staged,0x14)[0]
    pack_into("<I",staged,0x14,(old_status|0x10)&0xffffffdf)
    reserve=unpack_from("<I",staged,0x174)[0]
    if reserve&1:
        swapped=source_original_418220_role_swap_from_reached(
            original_player_at_418220=bytes(staged),
            original_source_role_object_pointer=0x3000,
            original_source_role_object_at_418220=SOURCE_ROLE)
        staged=bytearray(swapped.original_player_after_418220)
    pack_into("<I",staged,0x174,reserve&0xfffffffc)
    club=bytearray(8);pack_into("<I",club,4,2)
    world=bytearray(0x9d0);pack_into("<I",world,0x9cc,0x1000)
    link=bytearray(8);pack_into("<I",link,0,0x2000)
    user=bytearray(0x5b8);pack_into("<I",user,0x5b4,0x3000)
    context=bytearray(8);pack_into("<I",context,4,manager_key)
    manager=Original417340ReachedUser(
        0x1000,bytes(link),0x2000,bytes(user),0x3000,bytes(context))
    return source_original_417340_registered_user_from_reached(
        original_player_at_call=bytes(staged),
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=None,
        original_reached_club_pointer=0x50000+680*2,
        original_reached_club_record=bytes(club),
        original_global_874c10_record=bytes(world),
        original_reached_manager_links=(manager,),
    )


def quota_reached(proof, *, registered=3, count=3):
    c=bytearray(0x1ac)
    pack_into("<i",c,0x1a8,count)
    return Original41EDF0Reached(
        original_player_at_call=proof.original_native_player_at_call,
        original_874b90_club_array_base=0x50000,
        original_874b94_default_club_pointer=0x60000,
        original_registered_club_pointer=(0x60000 if registered<0 else
                                          0x50000+registered*680),
        original_registered_club_record=bytes(c),
    )


def state_with_world(p):
    state=GameState(calendar=GameCalendar(date(2000,7,1)),players={unpack_from("<H",p,4)[0]:object()})
    record=state.retain_verified_native_status_world(
        original_player_record=p,
        original_role_object_pointer=0x3000,
        original_role_object_record=SOURCE_ROLE,
        mapped_runtime_player_index=unpack_from("<H",p,4)[0],
    )
    return state,record


class OriginalNativeStatusWorldTests(unittest.TestCase):
    def test_distinct_current_and_registered_indices_raw_source_and_snapshot(self):
        p=native_player()
        r=source_native_player_status_world_from_reached(
            original_player_record=p,original_source_role_object_pointer=0x3000,
            original_source_role_object_record=SOURCE_ROLE,
            original_mapped_player_id=123)
        self.assertEqual((r.original_current_club_index_10,r.original_registered_club_index_72),(2,3))
        self.assertEqual((r.original_status_14,r.original_reserve_selection_174),(0x1020,3))
        self.assertEqual((r.original_reserve_role_152,r.original_reserve_aux_153),(0x16,5))
        self.assertEqual((r.original_role_object_byte_3,r.original_role_object_byte_4),(0x13,0xa7))
        world=OriginalNativeStatusWorldState({123:r},{3:5,-1:-2})
        snapshot=world.snapshot()
        self.assertEqual(snapshot["registered_club_quotas"],[[-1,-2],[3,5]])
        self.assertEqual(OriginalNativeStatusWorldState.restore(snapshot,{123}),world)
        self.assertEqual(source_native_registered_key(-32768),-1)
        self.assertEqual(source_native_registered_key(-1),-1)
        self.assertEqual(source_native_registered_key(3),3)
        self.assertEqual(OriginalNativeStatusWorldState.restore(None,{123}),
                         OriginalNativeStatusWorldState())

    def test_source_requires_real_matching_native_identity_and_role_pointer(self):
        for params,message in (
            ({"original_source_role_object_pointer":0x4444},"pointer mismatch"),
            ({"original_mapped_player_id":124},"player ID mismatch"),
            ({"original_source_role_object_record":b""},"through"),
            ({"original_player_record":b""},"through"),
        ):
            inputs={
                "original_player_record":native_player(),
                "original_source_role_object_pointer":0x3000,
                "original_source_role_object_record":SOURCE_ROLE,
                "original_mapped_player_id":123,
            }
            inputs.update(params)
            with self.subTest(params=params),self.assertRaisesRegex(OriginalNativeWorldStateError,message):
                source_native_player_status_world_from_reached(**inputs)
        with self.assertRaises(OriginalNativeWorldStateError):
            source_native_player_status_world_from_reached(
                original_player_record=native_player(),
                original_source_role_object_pointer=True,
                original_source_role_object_record=SOURCE_ROLE,
                original_mapped_player_id=123)

    def test_saved_status_player_and_registered_quota_reject_forgery(self):
        state,r=state_with_world(native_player())
        raw=state.native_status_world.snapshot()
        for mutated in (
            {"players":[raw["players"][0],raw["players"][0]],"registered_club_quotas":[]},
            {"players":[raw["players"][0][:7]],"registered_club_quotas":[]},
            {"players":[raw["players"][0]],"registered_club_quotas":[[3,3],[3,4]]},
            {"players":[raw["players"][0]],"registered_club_quotas":[[4,3],[3,4]]},
            {"players":[raw["players"][0]],"registered_club_quotas":[[3,True]]},
        ):
            with self.subTest(raw=mutated),self.assertRaises(OriginalNativeWorldStateError):
                OriginalNativeStatusWorldState.restore(mutated,{123})
        with self.assertRaises(OriginalNativeWorldStateError):
            OriginalNativeStatusWorldState.restore(raw,{456})
        with self.assertRaises(OriginalNativeWorldStateError):
            replace(r,original_status_14=True)
        with self.assertRaises(OriginalNativeWorldStateError):
            OriginalNativeStatusWorldState.restore({}, {123})

    def test_original_player_role_registered_club_world_applies_atomically(self):
        p=native_player()
        state,before=state_with_world(p)
        event=reached_player(p)
        gate=proof(event,manager_key=99)
        self.assertEqual(gate.original_417340_return_al,0)
        registered=quota_reached(gate)
        key,quantity=state.retain_verified_native_registered_club_quota(registered)
        self.assertEqual((key,quantity),(3,3))
        result=state.apply_verified_native_4085d0_world(
            original_reached=event,original_registered_417340=gate,
            mapped_runtime_player_index=123,original_41edf0_reached=registered)
        self.assertFalse(result.live_game_state_updated)
        self.assertTrue(result.original_native_418220_role_swap_projected)
        self.assertTrue(result.original_41edf0_quota_callback_projected)
        after=state.native_status_world.players[123]
        self.assertNotEqual(after,before)
        self.assertEqual((after.original_status_14,after.original_reserve_selection_174),(0x10,0))
        self.assertEqual((after.original_reserve_role_152,after.original_reserve_aux_153),(0x13,7))
        self.assertEqual((after.original_role_object_byte_3,after.original_role_object_byte_4),(0x16,0xa1))
        self.assertEqual(state.native_status_world.registered_club_quotas,{3:2})
        self.assertEqual((after.original_current_club_index_10,after.original_registered_club_index_72),(2,3))
        self.assertEqual(state.native_player_discipline,{})
        self.assertFalse(state.original_pending_transfer_eam.entries)
        self.assertFalse(state.original_delivered_mailboxes.mailboxes)

    def test_unguarded_replay_and_bad_quota_never_partially_mutate(self):
        p=native_player()
        state,before=state_with_world(p)
        event=reached_player(p)
        gate=proof(event,manager_key=99)
        registered=quota_reached(gate)
        original=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_4085d0_world(
                original_reached=event,original_registered_417340=gate,
                mapped_runtime_player_index=123,original_41edf0_reached=registered)
        self.assertEqual(state.native_status_world.snapshot(),original)
        state.retain_verified_native_registered_club_quota(registered)
        original=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"source entry is absent or stale"):
            state.apply_verified_native_4085d0_world(
                original_reached=replace(event,original_player_at_entry=native_player(role=13)),
                original_registered_417340=gate,
                mapped_runtime_player_index=123,original_41edf0_reached=registered)
        self.assertEqual(state.native_status_world.snapshot(),original)
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_4085d0_world(
                original_reached=event,original_registered_417340=gate,
                mapped_runtime_player_index=123,
                original_41edf0_reached=quota_reached(gate,count=5))
        self.assertEqual(state.native_status_world.snapshot(),original)
        state.apply_verified_native_4085d0_world(
            original_reached=event,original_registered_417340=gate,
            mapped_runtime_player_index=123,original_41edf0_reached=registered)
        committed=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_4085d0_world(
                original_reached=event,original_registered_417340=gate,
                mapped_runtime_player_index=123,original_41edf0_reached=registered)
        self.assertEqual(state.native_status_world.snapshot(),committed)

    def test_registered_human_source_skips_quota_and_generic_fields(self):
        p=native_player(status=0x20,reserve=2)
        state,_=state_with_world(p)
        event=reached_player(p)
        matched=proof(event,manager_key=2)
        self.assertEqual(matched.original_417340_return_al,1)
        out=state.apply_verified_native_4085d0_world(
            original_reached=event,original_registered_417340=matched,
            mapped_runtime_player_index=123)
        self.assertFalse(out.original_41edf0_quota_callback_projected)
        self.assertEqual(state.native_status_world.players[123].original_status_14,0x10)
        self.assertEqual(state.native_status_world.registered_club_quotas,{})
        with self.assertRaisesRegex(ValueError,"already initialized differently"):
            state.retain_verified_native_status_world(
                original_player_record=native_player(status=0x21),
                original_role_object_pointer=0x3000,
                original_role_object_record=SOURCE_ROLE,
                mapped_runtime_player_index=123)

    def test_full_human_controller_save_restore_without_generic_field_conflation(self):
        from test_internal_save import InternalSaveTests
        from test_human_gameplay import Database,coefficient_matrix
        from internal_save import snapshot_human_gameplay,restore_human_gameplay
        controller=InternalSaveTests().build_controller()
        runtime=controller.squad()[0]
        generic_before=(runtime.suspended,runtime.reserve_active,
                        runtime.saved_reserve_role_152,
                        runtime.suspension_matches_remaining)
        native=native_player(pid=runtime.index,role=27,aux=8,registered=3)
        controller.state.retain_verified_native_status_world(
            original_player_record=native,original_role_object_pointer=0x3000,
            original_role_object_record=SOURCE_ROLE,
            mapped_runtime_player_index=runtime.index)
        world=controller.state.native_status_world
        world.registered_club_quotas[3]=5
        snapshot=snapshot_human_gameplay(controller)
        self.assertEqual(snapshot["game_state"]["original_native_status_world"],world.snapshot())
        self.assertEqual(snapshot["schema_version"],48)
        restored=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),snapshot)
        self.assertEqual(restored.state.native_status_world,world)
        after=restored.state.players[runtime.index]
        self.assertEqual((after.suspended,after.reserve_active,
                          after.saved_reserve_role_152,
                          after.suspension_matches_remaining),generic_before)
        legacy=snapshot_human_gameplay(controller)
        legacy["game_state"].pop("original_native_status_world")
        restored_old=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),legacy)
        self.assertEqual(restored_old.state.native_status_world,OriginalNativeStatusWorldState())
        bad=snapshot_human_gameplay(controller)
        bad["game_state"]["original_native_status_world"]["players"][0][1]=1<<32
        with self.assertRaises(OriginalNativeWorldStateError):
            restore_human_gameplay(
                Database(),coefficient_matrix(),coefficient_matrix(),bad)


if __name__ == "__main__":
    unittest.main()
