"""Original 409C90 single-player reset real GameState native sidecar persistence.

Source-authenticated 41FA50→4181B0 transaction only. Not a claim of
complete native 409C90, original match or Windows11 GUI acceptance.
"""
from datetime import date
from struct import pack_into
from unittest import TestCase

from game_state import GameCalendar, GameState
from original_native_status_world_state import OriginalNativeStatusWorldState


def native_player(pid=123,*,club=2,registered=3,flags14=0x30,
                  flags174=3,saved_role=0x16,saved_position=5,
                  status_pointer=0x40000):
    b=bytearray(0x24c)
    pack_into("<H",b,4,pid)
    pack_into("<h",b,0x10,club)
    pack_into("<h",b,0x72,registered)
    pack_into("<I",b,0x14,flags14)
    pack_into("<I",b,0x174,flags174)
    pack_into("<I",b,0x248,status_pointer)
    b[0x152]=saved_role
    b[0x153]=saved_position
    return bytes(b)


SOURCE_ROLE=b"\x01\x00\x00\x13\xa7"


class Original409C90PersistentNativeWorldTests(TestCase):
    def case(self,*,pid=123,flags174=3,role=SOURCE_ROLE):
        native=native_player(pid=pid,flags174=flags174)
        s=GameState(calendar=GameCalendar(date(2000,7,1)),
                    players={123:object(),124:object()})
        s.retain_verified_native_status_world(
            original_player_record=native,
            original_role_object_pointer=0x40000,
            original_role_object_record=role,
            mapped_runtime_player_index=pid)
        return s,native

    def apply(self,s,source,**changed):
        values=dict(mapped_runtime_player_index=123,
                    original_native_player_pointer=0x500000,
                    original_player_record_before_41fa50=source,
                    original_role_object_record_before_4181b0=SOURCE_ROLE,
                    original_global_8755d0_dword=99,
                    original_team_club_key_dword=2)
        values.update(changed)
        return s.apply_verified_native_409c90_preselection_player_reset(**values)

    def test_original_418220_exchange_and_4ea370_status_reset_commit_atomically(self):
        state,source=self.case()
        state.native_status_world.registered_club_quotas[3]=7
        before=state.native_status_world.snapshot()
        projected=self.apply(state,source)
        self.assertEqual(projected.original_41fa50_source_decision.source_original_return_eax,0)
        reset=projected.original_4181b0_reset_if_reached
        self.assertIsNotNone(reset)
        self.assertTrue(reset.original_418220_was_reached)
        self.assertFalse(reset.native_original_4181b0_executed)
        current=state.native_status_world.players[123]
        self.assertEqual(current.original_status_14,0)
        self.assertEqual(current.original_reserve_selection_174,0)
        self.assertEqual((current.original_reserve_role_152,current.original_reserve_aux_153),
                         (0x13,7))
        self.assertEqual((current.original_role_object_byte_3,current.original_role_object_byte_4),
                         (1,0xa0))
        self.assertEqual((current.original_current_club_index_10,current.original_registered_club_index_72),
                         (2,3))
        self.assertNotEqual(state.native_status_world.snapshot(),before)
        self.assertEqual(state.native_status_world.registered_club_quotas,{3:7})
        self.assertEqual(OriginalNativeStatusWorldState.restore(
                         state.native_status_world.snapshot(),{123,124}),
                         state.native_status_world)
        # This native sidecar is the existing internal-save schema payload.
        self.assertIn("players",state.native_status_world.snapshot())

    def test_original_4181b0_bit0_clear_does_not_swap_saved_roles(self):
        state,source=self.case(flags174=2)
        result=self.apply(state,source)
        self.assertFalse(result.original_4181b0_reset_if_reached.original_418220_was_reached)
        current=state.native_status_world.players[123]
        self.assertEqual((current.original_reserve_role_152,current.original_reserve_aux_153),
                         (0x16,5))
        self.assertEqual((current.original_role_object_byte_3,current.original_role_object_byte_4),
                         (1,0xa0))
        self.assertEqual(current.original_reserve_selection_174,0)

    def test_original_41fa50_true_never_reaches_4181b0_and_does_not_modify_state(self):
        state,source=self.case()
        before=state.native_status_world.snapshot()
        with self.assertRaises(ValueError):
            self.apply(state,source,original_global_8755d0_dword=99,
                       original_team_club_key_dword=3)
        self.assertEqual(state.native_status_world.snapshot(),before)

    def test_reject_stale_unseeded_wrong_player_and_source_pointer_without_any_changes(self):
        state,source=self.case()
        before=state.native_status_world.snapshot()
        bad=bytearray(source)
        pack_into("<I",bad,0x14,0)
        cases=[
            {"original_player_record_before_41fa50":bytes(bad)},
            {"original_native_player_pointer":True},
            {"original_native_player_pointer":0},
            {"mapped_runtime_player_index":124},
            {"mapped_runtime_player_index":456},
            {"original_player_record_before_41fa50":native_player(status_pointer=0)},
            {"original_role_object_record_before_4181b0":bytes(4)},
            {"original_global_8755d0_dword":True},
            {"original_team_club_key_dword":None},
        ]
        for changed in cases:
            with self.subTest(change=str(changed)[:85]),self.assertRaises(ValueError):
                self.apply(state,source,**changed)
            self.assertEqual(state.native_status_world.snapshot(),before)
        del state.native_status_world.players[123]
        with self.assertRaises(ValueError):
            self.apply(state,source)
        self.assertEqual(state.native_status_world.players,{})

    def test_second_original_player_and_existing_quota_unaffected(self):
        state,source=self.case()
        another=native_player(pid=124,flags14=0x10,flags174=0)
        state.retain_verified_native_status_world(
            original_player_record=another,
            original_role_object_pointer=0x40000,
            original_role_object_record=SOURCE_ROLE,
            mapped_runtime_player_index=124)
        state.native_status_world.registered_club_quotas[-1]=9
        other_before=state.native_status_world.players[124]
        self.apply(state,source)
        self.assertEqual(state.native_status_world.players[124],other_before)
        self.assertEqual(state.native_status_world.registered_club_quotas,{-1:9})
        snap=state.native_status_world.snapshot()
        restored=OriginalNativeStatusWorldState.restore(snap,{123,124})
        self.assertEqual(restored.snapshot(),snap)
