"""Original 4085D0 read-only exits and mutating-world gate source tests."""
from __future__ import annotations
from dataclasses import replace
from struct import pack_into, unpack_from
from pathlib import Path
import hashlib
import os
import unittest

from original_native_4085d0_world_branch import (
    Original4085D0ReachedWorld,
    Original4085D0SourceError,
    source_original_4085d0_world_branch_from_reached,
    source_original_4085d0_qualified_mutating_leaf,
)


def native_player(*,team=2,flags=0,category_ptr=0x3000):
    p=bytearray(0x24c)
    pack_into("<H",p,4,123)
    pack_into("<h",p,0x10,team)
    pack_into("<I",p,0x14,flags)
    pack_into("<I",p,0x248,category_ptr)
    return bytes(p)


def native_team(key=2):
    t=bytearray(8)
    pack_into("<i",t,4,key)
    return bytes(t)


def reached(*,team=2,flags=0,key=2,n=0,peer=0,capacity=2,
            obj=b"\x00\x00\x00\xef\x00",pointer=0x3000,player=None):
    return Original4085D0ReachedWorld(
        (0x60000 if team<0 else 0x50000+680*team),native_team(key),0x2000,
        native_player(team=team,flags=flags) if player is None else player,
        n,pointer,obj,peer,capacity,
    )


def project(source):
    return source_original_4085d0_world_branch_from_reached(source)


class Original4085D0BranchTests(unittest.TestCase):
    def test_existing_status_bit4_with_matching_team_exits_without_mutation(self):
        item=replace(reached(flags=0x10),
            original_407060_eax=None,
            original_4ea3c0_source_object_pointer=None,
            original_4ea3c0_source_object=None,
            original_406be0_eax=None,
            original_5f0d20_eax=None)
        r=project(item)
        self.assertEqual((r.original_417ee0_return_eax,r.original_4085d0_return_if_no_mutation),(1,1))
        self.assertTrue(r.source_read_only_branch_complete)
        self.assertFalse(r.original_would_reach_mutating_4182f0_then_4ea350)
        self.assertFalse(r.native_callbacks_invoked)
        self.assertFalse(r.live_game_state_updated)
        with self.assertRaisesRegex(Original4085D0SourceError,"skips"):
            project(reached(flags=0x10))

    def test_mismatch_of_signed_current_team_vs_source_team_ignores_bit4(self):
        r=project(reached(team=-1,key=2,flags=0x10,n=11,peer=None,capacity=None,obj=None,pointer=None))
        self.assertEqual(r.original_417ee0_return_eax,0)
        self.assertEqual(r.original_407060_teammate_count,11)
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)

    def test_full_teammate_count_skips_category_callback(self):
        r=project(reached(n=11,peer=None,capacity=None,obj=None,pointer=None))
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)
        self.assertIsNone(r.original_4ea3c0_source_category)
        with self.assertRaisesRegex(Original4085D0SourceError,"skips"):
            project(reached(n=11))

    def test_source_peer_count_at_least_category_capacity_is_readonly(self):
        r=project(reached(n=10,peer=2,capacity=2))
        self.assertEqual(r.original_4ea3c0_source_category,0x0f)
        self.assertEqual((r.original_406be0_teammate_count,r.original_5f0d20_category_capacity_floor),(2,2))
        self.assertEqual(r.original_4085d0_return_if_no_mutation,0)
        self.assertTrue(r.source_read_only_branch_complete)

    def test_source_peer_below_capacity_requires_mutating_world_not_fabricated(self):
        r=project(reached(n=0,peer=1,capacity=2))
        self.assertTrue(r.original_would_reach_mutating_4182f0_then_4ea350)
        self.assertFalse(r.source_read_only_branch_complete)
        self.assertIsNone(r.original_4085d0_return_if_no_mutation)
        self.assertFalse(r.live_game_state_updated)
        self.assertFalse(r.native_callbacks_invoked)

    def test_failclosed_missing_actual_reached_data_and_forged_pointer(self):
        with self.assertRaisesRegex(Original4085D0SourceError,"407060"):
            project(replace(reached(),original_407060_eax=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"pointer mismatch"):
            project(reached(pointer=0x7777))
        with self.assertRaisesRegex(Original4085D0SourceError,"source-category"):
            project(replace(reached(),original_player_at_entry=b"\x00"*0x18))
        with self.assertRaisesRegex(Original4085D0SourceError,"source category"):
            project(reached(obj=b""))
        with self.assertRaisesRegex(Original4085D0SourceError,"406BE0"):
            project(reached(peer=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"5F0D20"):
            project(reached(capacity=None))
        with self.assertRaisesRegex(Original4085D0SourceError,"source count"):
            project(reached(n=-1))
        with self.assertRaisesRegex(Original4085D0SourceError,"source count"):
            project(reached(capacity=0))


    def test_source_complete_mutating_leaf_writes_original_player_and_category_only(self):
        from original_native_417340_registered_user_gate import (
            Original417340ReachedUser,source_original_417340_registered_user_from_reached,
        )
        def owner_proof(reached_world,registered=2):
            at_call=bytearray(reached_world.original_player_at_entry)
            old=unpack_from("<I",at_call,0x14)[0]
            pack_into("<I",at_call,0x14,(old|0x10)&0xffffffdf)
            old_reserve=unpack_from("<I",at_call,0x174)[0]
            if old_reserve&1:
                from original_native_418220_role_swap import source_original_418220_role_swap_from_reached
                swapped=source_original_418220_role_swap_from_reached(
                    original_player_at_418220=bytes(at_call),
                    original_source_role_object_pointer=unpack_from("<I",at_call,0x248)[0],
                    original_source_role_object_at_418220=reached_world.original_4ea3c0_source_object)
                at_call=bytearray(swapped.original_player_after_418220)
            pack_into("<I",at_call,0x174,old_reserve&0xfffffffc)
            club=bytearray(8);pack_into("<I",club,4,2)
            global_world=bytearray(0x9d0);pack_into("<I",global_world,0x9cc,0x1000)
            node=bytearray(8);pack_into("<I",node,0,0x2000)
            user=bytearray(0x5b8);pack_into("<I",user,0x5b4,0x3000)
            context=bytearray(8);pack_into("<I",context,4,registered)
            m=Original417340ReachedUser(0x1000,bytes(node),0x2000,bytes(user),
                                         0x3000,bytes(context))
            team=unpack_from("<h",at_call,0x10)[0]
            return source_original_417340_registered_user_from_reached(
                original_player_at_call=bytes(at_call),
                original_874b90_club_array_base=0x50000,
                original_874b94_default_club_pointer=None,
                original_reached_club_pointer=0x50000+680*team,
                original_reached_club_record=bytes(club),
                original_global_874c10_record=bytes(global_world),
                original_reached_manager_links=(m,),
            )
        entry=bytearray(native_player(flags=0x20))
        pack_into("<I",entry,0x174,2)
        w=reached(peer=1,capacity=2,obj=b"\x00\x00\x00\x13\xa7",
                  player=bytes(entry))
        proof=owner_proof(w)
        self.assertEqual(proof.original_417340_return_al,1)
        result=source_original_4085d0_qualified_mutating_leaf(w,proof)
        self.assertEqual(unpack_from("<I",result.original_player_at_exit,0x14)[0],0x10)
        self.assertEqual(unpack_from("<I",result.original_player_at_exit,0x174)[0],0)
        self.assertEqual(result.original_category_object_after_4ea350[4],0xa1)
        self.assertFalse(result.live_game_state_updated)
        self.assertFalse(result.native_4085d0_executed)
        with self.assertRaisesRegex(Original4085D0SourceError,"predicate mismatch"):
            source_original_4085d0_qualified_mutating_leaf(
                w,replace(proof,original_native_player_at_call=w.original_player_at_entry))
        with self.assertRaisesRegex(Original4085D0SourceError,"did not reach"):
            source_original_4085d0_qualified_mutating_leaf(
                replace(w,original_406be0_eax=2),proof)
        swap=bytearray(entry);pack_into("<I",swap,0x174,3)
        swap[0x152]=0x16; swap[0x153]=0x05
        ws=replace(w,original_player_at_entry=bytes(swap))
        swapped=source_original_4085d0_qualified_mutating_leaf(ws,owner_proof(ws))
        self.assertTrue(swapped.original_native_418220_role_swap_projected)
        self.assertFalse(swapped.original_native_4182f0_role_swap_executed)
        self.assertEqual(unpack_from("<I",swapped.original_player_at_exit,0x174)[0],0)
        self.assertEqual(swapped.original_player_at_exit[0x152:0x154],bytes((0x13,0x07)))
        self.assertEqual(swapped.original_category_object_after_4ea350[3:5],bytes((0x16,0xa1)))
        false_proof=owner_proof(w,registered=4)
        with self.assertRaisesRegex(Original4085D0SourceError,"41EDF0"):
            source_original_4085d0_qualified_mutating_leaf(w,false_proof)
        from original_native_41edf0_registered_quota import Original41EDF0Reached
        # Native 41EDF0 gets called even when bit12 is unset: then it
        # returns before reading registered club globals and no quota moves.
        no_quota=source_original_4085d0_qualified_mutating_leaf(
            w,false_proof,Original41EDF0Reached(
                original_player_at_call=false_proof.original_native_player_at_call))
        self.assertTrue(no_quota.original_41edf0_quota_callback_projected)
        self.assertIsNone(no_quota.original_registered_club_after_41edf0)
        self.assertEqual(unpack_from("<I",no_quota.original_player_at_exit,0x14)[0],0x10)
        # Registered owner is +72 (club 3), while current team +10 is 2.
        quota_player=bytearray(entry)
        pack_into("<I",quota_player,0x14,0x1020)
        pack_into("<h",quota_player,0x72,3)
        wquota=replace(w,original_player_at_entry=bytes(quota_player))
        proof=owner_proof(wquota,registered=4)
        club=bytearray(0x1ac)
        pack_into("<i",club,0x1a8,3)
        qualified=Original41EDF0Reached(
            original_player_at_call=proof.original_native_player_at_call,
            original_874b90_club_array_base=0x50000,
            original_874b94_default_club_pointer=0x60000,
            original_registered_club_pointer=0x50000+680*3,
            original_registered_club_record=bytes(club))
        combo=source_original_4085d0_qualified_mutating_leaf(wquota,proof,qualified)
        self.assertEqual(unpack_from("<I",combo.original_player_at_exit,0x14)[0],0x10)
        self.assertEqual(unpack_from("<i",combo.original_registered_club_after_41edf0,0x1a8)[0],2)
        self.assertTrue(combo.original_41edf0_quota_callback_projected)
        self.assertFalse(combo.live_game_state_updated)
        with self.assertRaisesRegex(Original4085D0SourceError,"41EDF0 source"):
            source_original_4085d0_qualified_mutating_leaf(
                wquota,proof,replace(qualified,original_player_at_call=wquota.original_player_at_entry))
        with self.assertRaisesRegex(Original4085D0SourceError,"skipped"):
            source_original_4085d0_qualified_mutating_leaf(w,owner_proof(w),qualified)
        exempt=bytearray(entry);pack_into("<I",exempt,0x14,0x2020)
        we=replace(w,original_player_at_entry=bytes(exempt))
        ok=source_original_4085d0_qualified_mutating_leaf(
            we,owner_proof(we,registered=4))
        self.assertEqual(unpack_from("<I",ok.original_player_at_exit,0x14)[0],0x2010)

    def test_private_original_opcode_signatures_if_original_supplied(self):
        src=os.getenv("FM2001_ORIGINAL_EXE")
        if not src:
            self.skipTest("original executable must remain private outside GitHub")
        exe=Path(src).read_bytes()
        self.assertEqual(hashlib.sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        opcodes={
            0x4085d0:"53 56 8b 74 24 0c 57 8b f9",
            0x4085df:"e8 fc f8 00 00",
            0x4085e8:"5f 5e b8 01 00 00 00",
            0x4085fc:"e8 5f ea ff ff",
            0x408601:"83 f8 0b",
            0x408606:"8b 8e 48 02 00 00",
            0x40860d:"e8 ae 1d 0e 00",
            0x408615:"e8 c6 e5 ff ff",
            0x408622:"e8 99 1d 0e 00",
            0x408628:"b9 64 ae 87 00",
            0x40862d:"e8 ee 86 1e 00",
            0x408632:"3b f8",
            0x408636:"8b ce e8 b3 fc 00 00",
            0x408644:"e8 07 1d 0e 00",
            0x417ee0:"0f bf 41 10 39 44 24 04",
            0x417eef:"8b 41 14 c1 e8 04 83 e0 01",
            0x4ea3c0:"8a 41 03 83 e0 1f c3",
            0x4ea350:"8a 41 04 53 8a 5c 24 08",
            0x418160:"8b 41 14 24 df 89 41 14 c3",
            0x418170:"8b 81 74 01 00 00 24 fd 89 81 74 01 00 00",
            0x418180:"56 8b f1 f6 86 74 01 00 00 01 74 13",
            0x41818c:"e8 8f 00 00 00",
            0x418191:"8b 86 74 01 00 00 24 fe 89 86 74 01 00 00",
            0x41830c:"e8 2f f0 ff ff 84 c0 75 11 8b 46 14 c1 e8 0d a8 01",
            0x41edf0:"8b 41 14 56 c1 e8 0c a8 01 74 63 8b 51 14",
            0x5f0d20:"8b 09 33 d2 8b 01 3d e8 03 00 00 74 26",
            0x4182f0:"56 8b f1 83 4e 14 10",
        }
        for va,pattern in opcodes.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(pattern)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],expected)


if __name__=="__main__":
    unittest.main()
