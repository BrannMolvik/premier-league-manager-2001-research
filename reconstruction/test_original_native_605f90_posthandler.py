"""Static original 605F90 third/fourth getter + 417380 user-record route."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_605f90_posthandler import (
    Original605F90PostReached, Original605F90PostSourceError,
    source_original_605f90_posthandler_from_reached,
)
from test_original_native_605f90_dispatch import predispatched,qualified
from test_original_native_41a5b0_extra_event import manager_proof


def native_post(*, human=True, index=2):
    prior=predispatched(subtype=1,draw=0)
    getter=bytearray(qualified(subtype=1,draw=0).original_player_after_41a5b0_pointer_store)
    getter[0x70]=index
    getter[0x76]=77
    p=bytes(getter)
    proof=manager_proof(p,registered=human)
    base=Original605F90PostReached(
        original_predispatch=prior,
        original_third_resolved_player_pointer=0x50000,
        original_third_resolved_player=p,
        original_posthandler_417340_owner_proof=proof,
    )
    if not human:
        return base
    user=bytearray(0x6bc)
    pack_into("<I",user,0x6b8,0x80000)
    t=bytearray(200); t[0x24]=0x9f
    return replace(base,
        original_fourth_resolved_player_pointer=0x50000,
        original_fourth_resolved_player=p,
        original_4172d0_403850_returned_user_pointer=0x2000,
        original_413b40_reached_user_record=bytes(user),
        original_417380_user_table_pointer=0x80000,
        original_417380_target_record_pointer=0x80000+200*(index-1),
        original_417380_target_record_before=bytes(t),
    )


class Original605F90PostHandlerTests(unittest.TestCase):
    def test_nonhuman_branch_skips_fourth_getter_and_all_record_writes(self):
        r=source_original_605f90_posthandler_from_reached(native_post(human=False))
        self.assertEqual(r.original_player_id,123)
        self.assertEqual(r.original_registered_human_al,0)
        self.assertFalse(r.original_417380_branch_reached)
        self.assertIsNone(r.original_target_record_source_after_if_reached)
        self.assertFalse(r.original_descriptor_freed_or_detached)
        self.assertEqual(r.original_605f90_source_return_al,1)
        self.assertFalse(r.original_native_posthandler_executed)
        self.assertFalse(r.live_game_state_updated)

    def test_registered_human_clears_user_owned_indexed_record_byte_24_only(self):
        x=native_post()
        r=source_original_605f90_posthandler_from_reached(x)
        self.assertTrue(r.original_417380_branch_reached)
        self.assertEqual(r.original_41e3d0_selector_from_player70_if_reached,2)
        self.assertEqual(r.original_registered_user_pointer_if_reached,0x2000)
        self.assertEqual(r.original_target_pointer_if_reached,0x800c8)
        self.assertEqual(r.original_fourth_getter_player_pointer_if_reached,0x50000)
        after=r.original_target_record_source_after_if_reached
        self.assertEqual(after[0x24],0)
        self.assertEqual(after[:0x24],x.original_417380_target_record_before[:0x24])
        self.assertEqual(after[0x25:],x.original_417380_target_record_before[0x25:])
        self.assertEqual(x.original_417380_target_record_before[0x24],0x9f)
        self.assertFalse(r.original_417380_target_write_executed)
        self.assertFalse(r.original_pending_event_delivered)
        self.assertFalse(r.original_descriptor_freed_or_detached)

    def test_selector_uses_player70_not_player76_even_if_different(self):
        x=native_post(index=1)
        out=source_original_605f90_posthandler_from_reached(x)
        self.assertEqual(out.original_target_pointer_if_reached,0x80000)
        self.assertNotEqual(x.original_fourth_resolved_player[0x76],1)

    def test_source_417340_and_4172d0_413b40_owner_fails_closed(self):
        good=native_post()
        user=bytearray(good.original_413b40_reached_user_record)
        pack_into("<I",user,0x6b8,0x90000)
        fourth=bytearray(good.original_fourth_resolved_player)
        pack_into("<h",fourth,0x10,3)
        third=bytearray(good.original_third_resolved_player)
        pack_into("<H",third,4,456)
        for bad in (
            replace(good,original_third_resolved_player=bytes(third)),
            replace(good,original_posthandler_417340_owner_proof=replace(
                good.original_posthandler_417340_owner_proof,
                original_matching_user_pointer=0x3000)),
            replace(good,original_4172d0_403850_returned_user_pointer=0x3000),
            replace(good,original_413b40_reached_user_record=bytes(user)),
            replace(good,original_fourth_resolved_player=bytes(fourth)),
            replace(good,original_417380_user_table_pointer=0x90000),
            replace(good,original_417380_target_record_pointer=0x80000),
            replace(good,original_417380_target_record_before=bytes(199)),
            replace(good,original_fourth_resolved_player_pointer=0),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original605F90PostSourceError):
                    source_original_605f90_posthandler_from_reached(bad)
        nonhuman=native_post(human=False)
        with self.assertRaisesRegex(Original605F90PostSourceError,"skips fourth getter"):
            source_original_605f90_posthandler_from_reached(replace(
                nonhuman,original_fourth_resolved_player_pointer=0x50000))

    def test_zero_source_selector_unsafe_and_u32_target_overflow_fail_closed(self):
        with self.assertRaisesRegex(Original605F90PostSourceError,"before table"):
            source_original_605f90_posthandler_from_reached(native_post(index=0))
        q=native_post(index=255)
        u=bytearray(q.original_413b40_reached_user_record)
        pack_into("<I",u,0x6b8,0xffffff00)
        with self.assertRaisesRegex(Original605F90PostSourceError,"overflows"):
            source_original_605f90_posthandler_from_reached(replace(
                q,original_413b40_reached_user_record=bytes(u),
                original_417380_user_table_pointer=0xffffff00))

    def test_actual_private_original_605f90_to_user_record_x86_if_supplied(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("original executable private, never in public CI")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        source={
            0x605fee:"8b 0d 44 56 87 00",
            0x605ffb:"e8 40 13 e1 ff",
            0x606002:"74 16",
            0x606004:"8b 0d 44 56 87 00",
            0x606011:"e8 6a 13 e1 ff",
            0x606016:"c6 40 24 00",
            0x60601c:"b0 01",
            0x4172d0:"e8 9b ff ff ff",
            0x403853:"e8 58 ff ff ff",
            0x403865:"e8 d6 02 01 00",
            0x413b40:"8b 81 cc 09 00 00",
            0x413b56:"8b 92 b4 05 00 00",
            0x413b6d:"8b 00",
            0x417380:"56 57 8b f1",
            0x417384:"e8 47 ff ff ff",
            0x417389:"8b b8 b8 06 00 00",
            0x417395:"50",
            0x417396:"e8 35 70 00 00",
            0x41739b:"25 ff 00 00 00",
            0x4173a6:"8d 84 cf 38 ff ff ff",
            0x41e3d0:"0f bf 41 10",
            0x41e3d8:"75 06",
            0x41e3da:"8a 41 70",
            0x41e3e0:"8a 41 76",
        }
        for va,hx in source.items():
            with self.subTest(original_va=hex(va)):
                raw=bytes.fromhex(hx)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":
    unittest.main()
