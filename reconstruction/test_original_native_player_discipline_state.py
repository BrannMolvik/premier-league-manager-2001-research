"""Source original disciplinary byte sidecar, snapshots and negative guards."""
from __future__ import annotations
from dataclasses import replace
from struct import pack_into
import unittest
from original_native_player_discipline_state import (
    OriginalNativeDisciplineError,OriginalNativePlayerDiscipline,
    source_original_native_discipline_from_reached_player,
    snapshot_original_native_discipline,restore_original_native_discipline,
)


def player(pid=123,fa=3,uefa=2,due=0xfffffffe):
    p=bytearray(0x164)
    pack_into("<H",p,4,pid)
    for off,val in (
        (0x139,8),(0x13a,4),(0x13b,fa),(0x13c,0),
        (0x13d,1),(0x13e,uefa),(0x144,6)
    ):
        p[off]=val
    pack_into("<I",p,0x160,due)
    return bytes(p)


def read(pid=123,**kwargs):
    return source_original_native_discipline_from_reached_player(
        original_native_player_record=player(pid,**kwargs),
        original_mapped_runtime_player_index=pid,
    )


class OriginalNativeDisciplinePreservationTests(unittest.TestCase):
    def test_source_all_native_bytes_retained_distinct_from_generic_suspension(self):
        r=read()
        self.assertEqual((r.native_139,r.native_13a,r.native_fa_counter_13b,
            r.native_13c,r.native_13d,r.native_uefa_counter_13e,
            r.native_incident_accumulator_144,r.native_fa_due_date_raw_160),
            (8,4,3,0,1,2,6,0xfffffffe))
        self.assertNotIn("suspension_matches_remaining",r.__dataclass_fields__)

    def test_sparse_two_player_snapshot_sorted_and_roundtrips(self):
        a,b=read(pid=123),read(pid=42,fa=0,uefa=1,due=0)
        rows=snapshot_original_native_discipline({123:a,42:b})
        self.assertEqual([r[0] for r in rows],[42,123])
        self.assertEqual(restore_original_native_discipline(rows,{42,123}),{42:b,123:a})

    def test_old_saves_do_not_create_zero_native_record_by_default(self):
        self.assertEqual(restore_original_native_discipline(None,{123}),{})
        self.assertEqual(restore_original_native_discipline([],{123}),{})

    def test_source_player_id_must_match_explicit_runtime_mapping(self):
        with self.assertRaisesRegex(OriginalNativeDisciplineError,"identity"):
            source_original_native_discipline_from_reached_player(
                original_native_player_record=player(2),
                original_mapped_runtime_player_index=123)
        with self.assertRaisesRegex(OriginalNativeDisciplineError,"through"):
            source_original_native_discipline_from_reached_player(
                original_native_player_record=b"",
                original_mapped_runtime_player_index=123)
        with self.assertRaises(OriginalNativeDisciplineError):
            source_original_native_discipline_from_reached_player(
                original_native_player_record=player(),original_mapped_runtime_player_index=True)

    def test_duplicate_unknown_and_out_of_order_save_rejected(self):
        a=read(pid=123).array()
        b=read(pid=42).array()
        for source,ids in (([a,a],{123}),([a,b],{42,123}),([a],{42})):
            with self.subTest(source=source):
                with self.assertRaises(OriginalNativeDisciplineError):
                    restore_original_native_discipline(source,ids)
        with self.assertRaisesRegex(OriginalNativeDisciplineError,"tuple"):
            restore_original_native_discipline([a[:7]],{123})

    def test_values_are_raw_bytes_and_unsigned_date_not_guessed(self):
        a=read()
        with self.assertRaises(OriginalNativeDisciplineError):
            replace(a,native_fa_counter_13b=256)
        with self.assertRaises(OriginalNativeDisciplineError):
            replace(a,native_uefa_counter_13e=-1)
        with self.assertRaises(OriginalNativeDisciplineError):
            replace(a,native_fa_due_date_raw_160=1<<32)
        with self.assertRaisesRegex(OriginalNativeDisciplineError,"identity"):
            snapshot_original_native_discipline({44:a})


if __name__=="__main__":
    unittest.main()
