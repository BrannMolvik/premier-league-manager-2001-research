"""Original 409C90 preselection/4181B0 reset, atomic native shadow + Save/Load."""
from __future__ import annotations

from dataclasses import replace
from datetime import date
from struct import unpack_from
import unittest

from game_state import GameCalendar, GameState
from original_native_409c90_assignment_status import (
    SourceOriginal409C90PreSelectionPlayerReset,
    source_original_409c90_reached_41fa50_then_optional_4181b0,
)
from test_original_native_status_world_state import native_player


STATUS=b"\x17\x18\x00\xe5\xc3"
POINTER=0x3000


def qualified_plan(player: bytes, status: bytes | None = STATUS, *,
                   team_club: int = 2, global_club: int = 5):
    return source_original_409c90_reached_41fa50_then_optional_4181b0(
        original_native_player_pointer=0x2000,
        original_player_record_before_41fa50=player,
        original_global_8755d0_dword=global_club,
        original_team_club_key_dword=team_club,
        original_reached_status_record_for_4181b0_if_called=status,
    )


def seeded_state(player: bytes, status: bytes = STATUS):
    pid=unpack_from("<H",player,4)[0]
    state=GameState(calendar=GameCalendar(date(2000,7,1)),players={pid:object()})
    initial=state.retain_verified_native_status_world(
        original_player_record=player,
        original_role_object_pointer=POINTER,
        original_role_object_record=status,
        mapped_runtime_player_index=pid)
    state.native_status_world.registered_club_quotas[3]=9
    return state,initial


class Original409C90NativeShadowIntegrationTests(unittest.TestCase):
    def test_both_418180_paths_and_higher_flags_preserve_native_owner_only(self):
        for flag174 in (2,3,0x80000001):
            with self.subTest(flag174=flag174):
                player=native_player(status=0xFFFFFFFF,reserve=flag174,
                                     role=0xA6,aux=0xB9)
                state,initial=seeded_state(player)
                other=state.players[123]
                before_generic=state.native_player_discipline.copy()
                reset=qualified_plan(player)
                self.assertIsNotNone(reset.original_4181b0_reset_if_reached)
                outcome=state.apply_verified_native_409c90_preselection_reset(
                    original_reached=reset,
                    original_source_status_pointer=POINTER,
                    mapped_runtime_player_index=123)
                self.assertEqual(outcome,state.native_status_world.players[123])
                self.assertEqual(outcome.original_status_14,0xFFFFFFCF)
                self.assertEqual(outcome.original_reserve_selection_174,flag174&~3)
                self.assertEqual((outcome.original_reserve_role_152,
                                  outcome.original_reserve_aux_153),
                                 (5,3) if flag174&1 else (0xA6,0xB9))
                self.assertEqual((outcome.original_role_object_byte_3,
                                  outcome.original_role_object_byte_4),(0xF7,0xC0))
                self.assertEqual((outcome.original_current_club_index_10,
                                  outcome.original_registered_club_index_72),(2,3))
                self.assertEqual(state.native_status_world.registered_club_quotas,{3:9})
                self.assertIs(state.players[123],other)
                self.assertEqual(state.native_player_discipline,before_generic)
                self.assertNotEqual(initial,outcome)
                self.assertFalse(reset.native_original_409c90_executed)
                self.assertFalse(reset.original_mutable_roster_world_completed)

    def test_stale_replay_wrong_owner_unreached_and_forged_projection_fail_atomically(self):
        player=native_player(status=0xFFFFFFFF,reserve=3,role=0xA6,aux=0xB9)
        state,_=seeded_state(player)
        plan=qualified_plan(player)
        pristine=state.native_status_world.snapshot()
        valid=dict(original_reached=plan,
                   original_source_status_pointer=POINTER,
                   mapped_runtime_player_index=123)
        tampered=replace(
            plan,original_4181b0_reset_if_reached=replace(
                plan.original_4181b0_reset_if_reached,
                source_status_after_reset=STATUS))
        for name,args in (
            ("wrong_status_pointer",{"original_source_status_pointer":POINTER+1}),
            ("missing_mapping",{"mapped_runtime_player_index":124}),
            ("wrong_mapped_type",{"mapped_runtime_player_index":True}),
            ("forged_reset_output",{"original_reached":tampered}),
            ("unverified_receipt",{"original_reached":object()}),
            ("unreached",{"original_reached":replace(
                plan,original_4181b0_reset_if_reached=None)}),
        ):
            with self.subTest(name=name),self.assertRaises(ValueError):
                state.apply_verified_native_409c90_preselection_reset(
                    **(valid|args))
            self.assertEqual(state.native_status_world.snapshot(),pristine)
        # The real original 41FA50-positive path skips 4181B0.
        skip_player=native_player(current=4,registered=3)
        skip=qualified_plan(skip_player,None,team_club=3,global_club=5)
        self.assertEqual(skip.original_41fa50_source_decision.source_original_return_eax,1)
        with self.assertRaisesRegex(ValueError,"did not reach"):
            state.apply_verified_native_409c90_preselection_reset(
                original_reached=skip,
                original_source_status_pointer=POINTER,
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_status_world.snapshot(),pristine)

        state.apply_verified_native_409c90_preselection_reset(**valid)
        accepted=state.native_status_world.snapshot()
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            state.apply_verified_native_409c90_preselection_reset(**valid)
        self.assertEqual(state.native_status_world.snapshot(),accepted)

        unseeded=GameState(calendar=GameCalendar(date(2000,7,1)),
                           players={123:object()})
        with self.assertRaisesRegex(ValueError,"absent or stale"):
            unseeded.apply_verified_native_409c90_preselection_reset(**valid)
        self.assertEqual(unseeded.native_status_world.players,{})

    def test_full_controller_save_load_roundtrip_does_not_change_generic_player(self):
        from test_internal_save import InternalSaveTests
        from test_human_gameplay import Database,coefficient_matrix
        from internal_save import snapshot_human_gameplay,restore_human_gameplay

        controller=InternalSaveTests().build_controller()
        generic=controller.squad()[0]
        baseline=(generic.suspended,generic.reserve_active,
                  generic.saved_reserve_role_152,
                  generic.suspension_matches_remaining)
        player=native_player(pid=generic.index,status=0xFFFFFFFF,
                             reserve=3,role=0xA6,aux=0xB9)
        controller.state.retain_verified_native_status_world(
            original_player_record=player,
            original_role_object_pointer=POINTER,
            original_role_object_record=STATUS,
            mapped_runtime_player_index=generic.index)
        controller.state.native_status_world.registered_club_quotas[3]=9
        plan=qualified_plan(player)
        result=controller.state.apply_verified_native_409c90_preselection_reset(
            original_reached=plan,
            original_source_status_pointer=POINTER,
            mapped_runtime_player_index=generic.index)
        snapshot=snapshot_human_gameplay(controller)
        self.assertEqual(snapshot["schema_version"],48)
        restored=restore_human_gameplay(
            Database(),coefficient_matrix(),coefficient_matrix(),snapshot)
        self.assertEqual(restored.state.native_status_world,
                         controller.state.native_status_world)
        self.assertEqual(restored.state.native_status_world.players[generic.index],
                         result)
        self.assertEqual(restored.state.native_status_world.registered_club_quotas,
                         {3:9})
        generic_after=restored.state.players[generic.index]
        self.assertEqual((generic_after.suspended,generic_after.reserve_active,
                          generic_after.saved_reserve_role_152,
                          generic_after.suspension_matches_remaining),baseline)


if __name__=="__main__":
    unittest.main()
