"""Original League v+0x3C pair → actual 0x616FC0 native event producer."""
from __future__ import annotations
import os
from pathlib import Path
import unittest

from original_native_procedural_event_emitter import (
    OriginalProceduralEventEmitterSourceError,
    source_original_procedural_event_emitter_616fc0,
)


class OriginalNativeProceduralEventEmitterTests(unittest.TestCase):
    def test_actual_generic_emitter_produces_class1_and_native_date_index(self):
        for teams,cycle,round_index,date_index in (
            (4,0,0,0),(4,1,1,4),(4,2,2,8),
            (12,0,10,10),(12,2,5,27),
        ):
            with self.subTest(teams=teams,cycle=cycle,round_index=round_index):
                got=source_original_procedural_event_emitter_616fc0(
                    original_team_count_plus_3c=teams,
                    original_cycle_index=cycle,
                    original_pair_round_index=round_index,
                    original_scottish_override_active=False)
                self.assertEqual(got.original_date_array_index,date_index)
                self.assertEqual(got.original_native_constructor_class.original_native_serialized_type_code,1)
                self.assertEqual(got.original_native_constructor_class.original_native_vtable_va,0x7C4C24)
                self.assertEqual(got.original_native_constructor_class.original_native_constructor_callsite_va,0x617047)
                self.assertTrue(got.source_match_constructor_called)
                self.assertEqual(got.source_date_owner_lookup_va,0x4F3B50)
                self.assertEqual(got.source_date_bucket_insertion_va,0x615950)
                self.assertFalse(got.source_defers_scottish_final_cycle_to_pair_buffer)
                self.assertFalse(got.original_native_constructor_class.is_live_original_event)

    def test_scottish_source_vtable_3c_final_cycle_buffers_pairs(self):
        for teams in (12,14):
            for cycle in (0,1,2):
                got=source_original_procedural_event_emitter_616fc0(
                    original_team_count_plus_3c=teams,
                    original_cycle_index=cycle,
                    original_pair_round_index=1,
                    original_scottish_override_active=True,
                    original_scottish_616f40_reported_cycle_count=3)
                self.assertEqual(got.source_defers_scottish_final_cycle_to_pair_buffer,cycle==2)
                self.assertEqual(got.source_match_constructor_called,cycle!=2)
                if cycle==2:
                    self.assertIsNone(got.original_date_array_index)
                    self.assertIsNone(got.original_native_constructor_class)
                    self.assertIsNone(got.source_date_bucket_insertion_va)
                else:
                    self.assertEqual(got.original_date_array_index,(teams-1)*cycle+1)

    def test_unqualified_virtual_owner_index_and_overflow_fail_closed(self):
        base=dict(
            original_team_count_plus_3c=4,
            original_cycle_index=1,
            original_pair_round_index=1,
            original_scottish_override_active=False,
            original_scottish_616f40_reported_cycle_count=None,
        )
        cases=(
            dict(original_team_count_plus_3c=True),
            dict(original_team_count_plus_3c=1),
            dict(original_team_count_plus_3c=-1),
            dict(original_cycle_index=-1),
            dict(original_cycle_index=True),
            dict(original_pair_round_index=3),
            dict(original_pair_round_index=None),
            dict(original_cycle_index=0x100000000),
            dict(original_scottish_override_active=None),
            dict(original_scottish_616f40_reported_cycle_count=2),
            dict(original_scottish_override_active=True),
            dict(original_scottish_override_active=True,
                 original_scottish_616f40_reported_cycle_count=0),
            dict(original_scottish_override_active=True,
                 original_scottish_616f40_reported_cycle_count=True),
            dict(original_team_count_plus_3c=0x7FFFFFFF,
                 original_cycle_index=2,original_pair_round_index=2),
        )
        for changes in cases:
            with self.subTest(change=str(changes)),self.assertRaises(
                OriginalProceduralEventEmitterSourceError):
                source_original_procedural_event_emitter_616fc0(**(base|changes))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner private original executable is absent from hosted CI")
    def test_native_private_emitter_and_3c_dispatch_bytes(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x617310:"ff 52 3c",
            0x617047:"e8 a4 94 ef ff",
            0x617071:"e8 da ca ed ff",
            0x617078:"e8 d3 e8 ff ff",
            0x617057:"49",
            0x617059:"0f af 4c 24 20",
            0x617063:"03 cf",
            0x6170A3:"e8 98 fe ff ff",
            0x6170AF:"3b c1",
            0x6170B1:"75 22",
            0x6170E7:"e8 d4 fe ff ff",
            0x6170D2:"c2 10 00",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__ == "__main__":
    unittest.main()
