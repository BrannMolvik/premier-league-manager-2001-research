"""Source 5127A0 row native pointers versus roster player IDs."""
from __future__ import annotations

from dataclasses import replace
from struct import pack_into
import unittest

from original_native_5127a0_order_guard import Original5127A0OrderedSide
from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_5127a0_player_identity import (
    Original5127A0ReachedPlayer,
    Original5127A0IdentityError,
    source_original_5127a0_player_pointer_identity,
)


def native_player(pid):
    result=bytearray(0x250)
    pack_into("<H",result,4,pid)
    return bytes(result)


def side(passindex=0, rowpointer=0x4000):
    row=Original5127A0RowCall(
        pass_index=passindex,row_index=0,
        source_current_team_pointer=0x1000,
        source_opponent_team_pointer=0x2000,
        source_player_pointer=rowpointer,
        source_4197c0_arg1=1,source_4197c0_arg2=0,
        source_4197c0_arg3=0x2000,
        source_41a5b0_called_after_row=False,
    )
    return Original5127A0OrderedSide(
        passindex,(123,124),(row,),0,())


def reached(first=0x4000,second=0x4500):
    return (Original5127A0ReachedPlayer(first,native_player(123)),
            Original5127A0ReachedPlayer(second,native_player(124)))


class Original5127A0PlayerIdentityTests(unittest.TestCase):
    def test_source_row_pointer_resolves_same_native_id_as_roster(self):
        receipt=source_original_5127a0_player_pointer_identity(
            source_side=side(),original_reached_players=reached())
        self.assertEqual(receipt.native_roster_ids,(123,124))
        self.assertEqual(receipt.native_roster_pointers,(0x4000,0x4500))
        self.assertEqual(receipt.native_row_ids,(123,))
        self.assertEqual(receipt.native_row_pointers,(0x4000,))
        self.assertFalse(receipt.native_callbacks_executed)
        self.assertFalse(receipt.live_game_state_updated)

    def test_second_owner_and_second_roster_player(self):
        receipt=source_original_5127a0_player_pointer_identity(
            source_side=side(passindex=1,rowpointer=0x4500),
            original_reached_players=reached())
        self.assertEqual(receipt.side_index,1)
        self.assertEqual(receipt.native_row_ids,(124,))

    def test_forged_row_pointer_missing_roster_and_identity_failclosed(self):
        with self.assertRaisesRegex(Original5127A0IdentityError,"row player pointer"):
            source_original_5127a0_player_pointer_identity(
                source_side=side(rowpointer=0x7777),
                original_reached_players=reached())
        wrong=(Original5127A0ReachedPlayer(0x4000,native_player(99)),reached()[1])
        with self.assertRaisesRegex(Original5127A0IdentityError,"DBRPlayer"):
            source_original_5127a0_player_pointer_identity(
                source_side=side(),original_reached_players=wrong)
        with self.assertRaisesRegex(Original5127A0IdentityError,"coverage"):
            source_original_5127a0_player_pointer_identity(
                source_side=side(),original_reached_players=reached()[:1])
        with self.assertRaisesRegex(Original5127A0IdentityError,"repeated"):
            source_original_5127a0_player_pointer_identity(
                source_side=side(),original_reached_players=reached(first=0x4000,second=0x4000))
        with self.assertRaisesRegex(Original5127A0IdentityError,"bytes"):
            source_original_5127a0_player_pointer_identity(
                source_side=side(),
                original_reached_players=(Original5127A0ReachedPlayer(0x4000,b""),reached()[1]))

    def test_mismatched_side_row_index_rejected_before_player_world(self):
        original=side()
        row=replace(original.source_rows[0],pass_index=1)
        with self.assertRaisesRegex(Original5127A0IdentityError,"side/index"):
            source_original_5127a0_player_pointer_identity(
                source_side=replace(original,source_rows=(row,)),
                original_reached_players=reached())


if __name__=="__main__":
    unittest.main()
