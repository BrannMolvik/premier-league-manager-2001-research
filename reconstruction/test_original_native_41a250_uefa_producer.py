"""Original UEFA 0x41A250 per-row incident, two event families and safe leaf."""
from __future__ import annotations
from dataclasses import replace
from datetime import date
from struct import pack_into
from pathlib import Path
import hashlib
import os
import unittest

from game_state import GameState, GameCalendar
from original_native_5127a0_row_incident_source import Original5127A0RowCall
from original_native_41a250_uefa_producer import (
    Original41A250Reached, Original41A250SourceError,
    source_original_41a250_uefa_incident_from_reached,
)


def row(arg1=2,arg2=0):
    return Original5127A0RowCall(
        pass_index=0,row_index=0,
        source_current_team_pointer=0x1000,
        source_opponent_team_pointer=0x2000,
        source_player_pointer=0x3000,
        source_4197c0_arg1=arg1,source_4197c0_arg2=arg2,
        source_4197c0_arg3=0x2000,
        source_41a5b0_called_after_row=False,
    )


def player(incident=0,uefa=0,identity=123):
    p=bytearray(0x164)
    pack_into("<H",p,4,identity)
    p[0x13d]=incident
    p[0x13e]=uefa
    pack_into("<I",p,0x160,0xfffffffe)
    return bytes(p)


def reached(*,arg1=2,arg2=0,incident=0,uefa=0,
            first=None,after=None,second=None,entry=None):
    return Original41A250Reached(
        original_row=row(arg1,arg2),
        original_native_player_at_entry=player(incident,uefa) if entry is None else entry,
        original_41a250_reached=True,
        original_first_reached_417340_eax=first,
        original_player_after_first_branch=after,
        original_second_reached_417340_eax=second,
    )


class Original41A250UEFATests(unittest.TestCase):
    def test_zero_second_arg_small_incident_is_truly_callback_free(self):
        a=source_original_41a250_uefa_incident_from_reached(reached())
        self.assertEqual(a.original_player_id,123)
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13d],2)
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13e],0)
        self.assertFalse(a.first_417340_original_callback_reached)
        self.assertFalse(a.second_417340_original_callback_reached)
        self.assertTrue(a.source_callback_free_leaf_complete)
        self.assertIsNone(a.first_original_event_constructor_if_allocated)
        self.assertIsNone(a.second_original_event_constructor_if_allocated)
        self.assertFalse(a.native_pending_queue_mutated)

    def test_unsigned_byte_overflow_can_skip_second_callback(self):
        a=source_original_41a250_uefa_incident_from_reached(
            reached(arg1=2,incident=255))
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13d],1)
        self.assertTrue(a.source_callback_free_leaf_complete)

    def test_three_threshold_subtracts_once_then_requires_417340(self):
        a=source_original_41a250_uefa_incident_from_reached(
            reached(arg1=7,incident=0,second=1))
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13d],4)
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13e],1)
        self.assertTrue(a.second_417340_original_callback_reached)
        self.assertEqual(a.second_original_event_constructor_if_allocated,0x585ad0)
        self.assertFalse(a.source_callback_free_leaf_complete)
        self.assertFalse(a.native_pending_queue_mutated)

    def test_first_and_second_original_event_classes_both_can_be_reached(self):
        after=bytearray(player(incident=2,uefa=1))
        after[0x139]=19  # actual post-first event callback may change unrelated fields
        a=source_original_41a250_uefa_incident_from_reached(
            reached(arg1=2,arg2=1,first=1,after=bytes(after),second=1))
        self.assertEqual(a.first_original_event_constructor_if_allocated,0x585750)
        self.assertEqual(a.second_original_event_constructor_if_allocated,0x585ad0)
        self.assertEqual(a.original_first_417340_entry_player[0x13e],1)
        self.assertEqual(a.original_source_player_at_second_gate_or_return[0x13d],1)
        self.assertTrue(a.first_417340_original_callback_reached)
        self.assertTrue(a.second_417340_original_callback_reached)
        self.assertFalse(a.native_pending_queue_mutated)

    def test_first_callback_false_and_no_second_uses_post_callback_player(self):
        after=player(incident=0,uefa=1)
        a=source_original_41a250_uefa_incident_from_reached(
            reached(arg1=0,arg2=1,first=0,after=after))
        self.assertIsNone(a.first_original_event_constructor_if_allocated)
        self.assertTrue(a.first_417340_original_callback_reached)
        self.assertFalse(a.second_417340_original_callback_reached)
        self.assertFalse(a.source_callback_free_leaf_complete)
        self.assertEqual(a.original_source_player_at_second_gate_or_return,after)

    def test_missing_and_extra_reached_callbacks_failclosed(self):
        with self.assertRaisesRegex(Original41A250SourceError,"first 417340"):
            source_original_41a250_uefa_incident_from_reached(reached(arg2=1))
        with self.assertRaisesRegex(Original41A250SourceError,"AFTER first"):
            source_original_41a250_uefa_incident_from_reached(
                reached(arg2=1,first=0))
        with self.assertRaisesRegex(Original41A250SourceError,"second 417340"):
            source_original_41a250_uefa_incident_from_reached(reached(arg1=3))
        with self.assertRaisesRegex(Original41A250SourceError,"skipped"):
            source_original_41a250_uefa_incident_from_reached(
                reached(arg1=1,first=0))
        with self.assertRaisesRegex(Original41A250SourceError,"skipped"):
            source_original_41a250_uefa_incident_from_reached(
                reached(arg1=1,second=0))
        with self.assertRaisesRegex(Original41A250SourceError,"player snapshot"):
            source_original_41a250_uefa_incident_from_reached(
                reached(arg1=1,arg2=1,first=0,after=player(identity=124)))
        with self.assertRaisesRegex(Original41A250SourceError,"reached"):
            source_original_41a250_uefa_incident_from_reached(
                replace(reached(),original_41a250_reached=False))

    def test_live_qualified_leaf_atomic_and_no_generic_suspend_or_mail(self):
        state=GameState(calendar=GameCalendar(date(2000,7,1)),players={123:object()})
        native=player(incident=0,uefa=0)
        state.retain_verified_native_player_discipline(
            original_player_record=native,mapped_runtime_player_index=123)
        before=state.native_player_discipline[123]
        result=state.retain_verified_uefa_incident_callback_free_leaf(
            original_reached=reached(arg1=2,arg2=0,entry=native),
            mapped_runtime_player_index=123,
        )
        self.assertEqual(result.native_13d,2)
        self.assertEqual(result.native_uefa_counter_13e,0)
        self.assertNotEqual(result,before)
        self.assertEqual(state.native_player_discipline[123],result)
        self.assertFalse(state.original_pending_transfer_eam.entries)
        self.assertFalse(state.original_delivered_mailboxes.mailboxes)

    def test_live_rejects_callback_while_preserving_previous_native_state(self):
        state=GameState(calendar=GameCalendar(date(2000,7,1)),players={123:object()})
        native=player()
        state.retain_verified_native_player_discipline(
            original_player_record=native,mapped_runtime_player_index=123)
        before=state.native_player_discipline[123]
        with self.assertRaisesRegex(ValueError,"outstanding"):
            state.retain_verified_uefa_incident_callback_free_leaf(
                original_reached=reached(arg1=3,arg2=0,second=1,entry=native),
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_player_discipline[123],before)
        with self.assertRaisesRegex(ValueError,"differs"):
            state.retain_verified_uefa_incident_callback_free_leaf(
                original_reached=reached(entry=player(incident=1)),
                mapped_runtime_player_index=123)
        self.assertEqual(state.native_player_discipline[123],before)

    def test_live_replay_stale_original_entry_failsclosed(self):
        state=GameState(calendar=GameCalendar(date(2000,7,1)),players={123:object()})
        native=player()
        state.retain_verified_native_player_discipline(
            original_player_record=native,mapped_runtime_player_index=123)
        task=reached(arg1=1,entry=native)
        state.retain_verified_uefa_incident_callback_free_leaf(
            original_reached=task,mapped_runtime_player_index=123)
        with self.assertRaisesRegex(ValueError,"differs"):
            state.retain_verified_uefa_incident_callback_free_leaf(
                original_reached=task,mapped_runtime_player_index=123)


    def test_source_417340_owner_proof_qualifies_both_distinct_uefa_event_types(self):
        from original_native_417340_registered_user_gate import (
            Original417340ReachedUser,
            source_original_417340_registered_user_from_reached,
        )
        def prove(at_call, *, registered_club=77):
            club=bytearray(8)
            pack_into("<I",club,4,77)
            world=bytearray(0x9d0)
            pack_into("<I",world,0x9cc,0x1000)
            node=bytearray(8)
            pack_into("<I",node,0,0x2000)
            user=bytearray(0x5b8)
            pack_into("<I",user,0x5b4,0x3000)
            context=bytearray(8)
            pack_into("<I",context,4,registered_club)
            link=Original417340ReachedUser(
                0x1000,bytes(node),0x2000,bytes(user),0x3000,bytes(context))
            return source_original_417340_registered_user_from_reached(
                original_player_at_call=at_call,
                original_874b90_club_array_base=0x50000,
                original_874b94_default_club_pointer=None,
                original_reached_club_pointer=0x50000,
                original_reached_club_record=bytes(club),
                original_global_874c10_record=bytes(world),
                original_reached_manager_links=(link,),
            )
        entry=player(incident=2,uefa=0)
        at_first=bytearray(entry)
        at_first[0x13e]=1
        after_first=bytes(at_first)
        at_second=bytearray(after_first)
        at_second[0x13d]=1
        positive_first=prove(bytes(at_first))
        positive_second=prove(bytes(at_second))
        r=source_original_41a250_uefa_incident_from_reached(
            replace(
                reached(arg1=2,arg2=1,entry=entry,after=after_first),
                original_first_417340_registered_owner_proof=positive_first,
                original_second_417340_registered_owner_proof=positive_second,
            )
        )
        self.assertEqual(
            (r.first_original_event_constructor_if_allocated,
             r.second_original_event_constructor_if_allocated),
            (0x585750,0x585ad0),
        )
        self.assertFalse(r.native_pending_queue_mutated)
        negative_second=prove(bytes(at_second),registered_club=4)
        r2=source_original_41a250_uefa_incident_from_reached(
            replace(
                reached(arg1=2,arg2=1,entry=entry,after=after_first),
                original_first_417340_registered_owner_proof=positive_first,
                original_second_417340_registered_owner_proof=negative_second,
            )
        )
        self.assertEqual(r2.first_original_event_constructor_if_allocated,0x585750)
        self.assertIsNone(r2.second_original_event_constructor_if_allocated)
        with self.assertRaisesRegex(Original41A250SourceError,"disagrees"):
            source_original_41a250_uefa_incident_from_reached(
                replace(
                    reached(arg1=2,arg2=1,first=0,entry=entry,after=after_first),
                    original_first_417340_registered_owner_proof=positive_first,
                    original_second_417340_registered_owner_proof=positive_second,
                )
            )
        with self.assertRaisesRegex(Original41A250SourceError,"proof mismatch"):
            source_original_41a250_uefa_incident_from_reached(
                replace(
                    reached(arg1=2,arg2=1,entry=entry,after=after_first),
                    original_first_417340_registered_owner_proof=positive_second,
                    original_second_417340_registered_owner_proof=positive_second,
                )
            )

    def test_optional_private_original_opcode_proof(self):
        source=os.getenv("FM2001_ORIGINAL_EXE")
        if not source:
            self.skipTest("original executable remains private outside GitHub")
        data=Path(source).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        opcodes={
            0x41a26c:"85 c0",0x41a278:"0f 8e eb 00 00 00",
            0x41a27e:"c6 85 3e 01 00 00 01",
            0x41a285:"e8 b6 d0 ff ff",
            0x41a321:"e8 2a b4 16 00",
            0x41a344:"56",
            0x41a34a:"c7 44 24 44 ff ff ff ff",
            0x41a352:"e8 69 9b 1f 00",
            0x41a369:"8a 4c 24 48",
            0x41a36d:"8a 95 3d 01 00 00",
            0x41a373:"02 d1",
            0x41a377:"88 95 3d 01 00 00",
            0x41a37d:"3c 02",
            0x41a385:"2c 03",
            0x41a38f:"c6 85 3e 01 00 00 01",
            0x41a396:"e8 a5 cf ff ff",
            0x41a432:"e8 99 b6 16 00",
            0x41a463:"e8 58 9a 1f 00",
            0x41a475:"e8 66 9a 1f 00",
        }
        for va,expected in opcodes.items():
            with self.subTest(va=hex(va)):
                raw=bytes.fromhex(expected)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":
    unittest.main()
