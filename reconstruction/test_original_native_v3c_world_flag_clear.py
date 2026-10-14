"""Original 511370→50EA40→418030 bounded native world effect regression."""
from __future__ import annotations
from struct import pack_into, unpack_from
import unittest
from original_native_v3c_world_flag_clear import (
    OriginalV3CWorldClearError, OriginalV3CReachedPlayer, OriginalV3CReachedSide,
    source_original_511370_first_side_world_clears,
)


def native_match(value=8, flags=1):
    b = bytearray(0x50)
    pack_into("<i", b, 0x0c, value)
    pack_into("<I", b, 0x44, flags)
    return bytes(b)


def native_world(value):
    b = bytearray(0x6c)
    pack_into("<i", b, 0x68, value)
    return bytes(b)


def native_roster(ids=(101, 202)):
    b = bytearray(0x298)
    pack_into("<i", b, 0x294, len(ids))
    for i, ident in enumerate(ids):
        pack_into("<H", b, 0x244 + 2*i, ident)
    return bytes(b)


def native_player(flags=0xffff):
    b = bytearray(0x14c)
    pack_into("<I", b, 0x14, flags)
    pack_into("<I", b, 0x148, flags)
    return bytes(b)


def native_side(offset, value=4, ids=(101, 202), category=4):
    reached = value == category
    return OriginalV3CReachedSide(
        original_side_ref_offset=offset,
        original_side_object_pointer=0x1000+offset,
        original_side_record_at_50ea40=native_roster(ids),
        original_world_object_pointer_at_compare=0x9000+offset,
        original_world_record_at_compare=native_world(value),
        original_world_object_pointer_at_final_store=0x9000+offset if reached else None,
        original_world_record_at_final_store=native_world(value) if reached else None,
        original_player_records_at_418030=(
            tuple(OriginalV3CReachedPlayer(x, native_player()) for x in ids)
            if reached else ()
        ),
    )


def project(sides=None, *, eax=1, match=None):
    if sides is None:
        sides = (native_side(0x14), native_side(0x28))
    return source_original_511370_first_side_world_clears(
        original_match_at_511381=native_match() if match is None else match,
        original_first_competition_virtual30_eax=eax,
        original_reached_sides=sides,
    )


class OriginalV3CSideWorldTests(unittest.TestCase):
    def test_both_reached_sides_clear_two_flags_and_world_owner(self):
        r = project()
        self.assertEqual(r.original_match_day_category_signed, 4)
        self.assertEqual(tuple(x.original_side_ref_offset for x in r.original_side_results), (0x14, 0x28))
        for side in r.original_side_results:
            self.assertTrue(side.original_side_world_equal)
            self.assertEqual(unpack_from("<I", side.original_world_record_after, 0x68)[0], 0xffffffff)
            for p in side.original_player_flags_after:
                self.assertEqual(unpack_from("<I", p.original_player_record_at_418030, 0x14)[0], 0xfffb)
                self.assertEqual(unpack_from("<I", p.original_player_record_at_418030, 0x148)[0], 0xfffb)
        self.assertFalse(r.native_side_callbacks_invoked)
        self.assertFalse(r.live_game_state_updated)

    def test_zero_first_competition_virtual_skips_all_sides(self):
        self.assertEqual(project((), eax=0).original_side_results, ())
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "skips"):
            project(eax=0)

    def test_world_marker_mismatch_skips_second_side_effects(self):
        r = project((native_side(0x14), native_side(0x28, value=9)))
        self.assertEqual(tuple(s.original_side_world_equal for s in r.original_side_results), (True, False))
        self.assertIsNone(r.original_side_results[1].original_world_record_after)

    def test_signed_sar_match_category(self):
        r = project((native_side(0x14, value=-2, category=-2),
                     native_side(0x28, value=-2, category=-2)), match=native_match(value=-3))
        self.assertEqual(r.original_match_day_category_signed, -2)
        self.assertTrue(all(s.original_side_world_equal for s in r.original_side_results))

    def test_qualified_empty_roster_still_resets_owner(self):
        r = project((native_side(0x14, ids=()), native_side(0x28, ids=())))
        self.assertEqual(r.original_side_results[0].original_player_flags_after, ())
        self.assertEqual(unpack_from("<I", r.original_side_results[0].original_world_record_after, 0x68)[0], 0xffffffff)

    def test_failclosed_wrong_player_id_and_post_world_owner(self):
        s = native_side(0x14)
        bad = OriginalV3CReachedSide(0x14, s.original_side_object_pointer,
            s.original_side_record_at_50ea40, s.original_world_object_pointer_at_compare,
            s.original_world_record_at_compare, s.original_world_object_pointer_at_final_store,
            s.original_world_record_at_final_store,
            (OriginalV3CReachedPlayer(999, native_player()), OriginalV3CReachedPlayer(202, native_player())))
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "ID mismatch"):
            project((bad, native_side(0x28)))
        bad_world = OriginalV3CReachedSide(0x14, s.original_side_object_pointer,
            s.original_side_record_at_50ea40, s.original_world_object_pointer_at_compare,
            s.original_world_record_at_compare, 0xdead, s.original_world_record_at_final_store,
            s.original_player_records_at_418030)
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "world owner changed"):
            project((bad_world, native_side(0x28)))

    def test_failclosed_skipped_roster_getters_and_invalid_order(self):
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "SideRef"):
            project((native_side(0x28), native_side(0x14)))
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "bit0"):
            project(match=native_match(flags=0))
        s = native_side(0x14)
        missed = OriginalV3CReachedSide(0x14, s.original_side_object_pointer,
            s.original_side_record_at_50ea40, s.original_world_object_pointer_at_compare,
            s.original_world_record_at_compare, s.original_world_object_pointer_at_final_store,
            s.original_world_record_at_final_store, ())
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "reached player"):
            project((missed, native_side(0x28)))
        s2 = native_side(0x28, value=99)
        forged = OriginalV3CReachedSide(0x28, s2.original_side_object_pointer,
            s2.original_side_record_at_50ea40, s2.original_world_object_pointer_at_compare,
            s2.original_world_record_at_compare,
            original_player_records_at_418030=(OriginalV3CReachedPlayer(101, native_player()),))
        with self.assertRaisesRegex(OriginalV3CWorldClearError, "skips"):
            project((native_side(0x14), forged))


if __name__ == "__main__":
    unittest.main()
