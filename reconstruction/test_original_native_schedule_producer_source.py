"""Original source-qualified startup emitters, not live match instances."""
from __future__ import annotations

import os
from pathlib import Path
import unittest

from original_native_schedule_producer_source import (
    OriginalScheduleProducerSourceError,
    SOURCE_NATIVE_STARTUP_MATCH_PRODUCERS,
    SOURCE_SCOTTISH_SPLIT_CLASS_CALLSITES,
    source_original_schedule_constructor_for_verified_producer,
)


class OriginalNativeStartupScheduleProducerTests(unittest.TestCase):
    def test_exact_original_producer_constructor_and_loaded_class_families(self):
        expected={
            "fixed_league_match":(0x6173D0,0x617490,0x5104F0,1,0x7C4C24),
            "cup_match":(0x4F64D0,0x4F66C9,0x510520,2,0x7C9D9C),
            "first_leg_match":(0x4F6820,0x4F6A02,0x510640,4,0x7C9EF8),
            "second_leg_match":(0x4F6820,0x4F6A64,0x510680,5,0x7C9F70),
            "scot_split_league_match":(0x4FAC60,None,0x5104F0,1,0x7C4C24),
        }
        self.assertEqual(tuple(SOURCE_NATIVE_STARTUP_MATCH_PRODUCERS),tuple(expected))
        for kind,(producer,callsite,ctor,serialized,vt) in expected.items():
            with self.subTest(kind=kind):
                actual=source_original_schedule_constructor_for_verified_producer(
                    source_emission_kind=kind,
                    original_source_producer_va=producer,
                    original_native_constructor_callsite_va=callsite)
                self.assertEqual((
                    actual.original_source_producer_va,
                    actual.original_native_constructor_callsite_va,
                    actual.original_native_constructor_va,
                    actual.original_native_serialized_type_code,
                    actual.original_native_vtable_va
                ), (producer,callsite,ctor,serialized,vt))
                self.assertFalse(actual.is_live_original_event)

    def test_split_native_callsite_ambiguous_but_both_branches_same_constructor(self):
        self.assertEqual(SOURCE_SCOTTISH_SPLIT_CLASS_CALLSITES,(0x4FADBE,0x4FAE30))
        for site in (None,0x4FADBE,0x4FAE30):
            with self.subTest(site=site):
                got=source_original_schedule_constructor_for_verified_producer(
                    source_emission_kind="scot_split_league_match",
                    original_source_producer_va=0x4FAC60,
                    original_native_constructor_callsite_va=site)
                self.assertEqual(got.original_native_constructor_va,0x5104F0)
                self.assertEqual(got.original_native_serialized_type_code,1)

    def test_procedural_pair_generation_not_assumed_to_be_native_constructor(self):
        cases=[
            ("league_match",0x6170F0,None),
            ("league_match",0x6173D0,0x617490),
            ("fixed_league_match",0x6170F0,0x617490),
            ("fixed_league_match",0x6173D0,None),
            ("cup_match",0x4F6820,0x4F66C9),
            ("cup_match",0x4F64D0,0x4F6A02),
            ("first_leg_match",0x4F6820,0x4F6A64),
            ("second_leg_match",0x4F6820,0x4F6A02),
            ("scot_split_league_match",0x4FAC60,0x617490),
            ("fixed_league_match",True,0x617490),
            ("cup_match",0x4F64D0,True),
            ("cup_match",0x4F64D0,None),
            (None,0x4F64D0,0x4F66C9),
        ]
        for kind,producer,site in cases:
            with self.subTest(kind=kind,producer=producer,site=site):
                with self.assertRaises(OriginalScheduleProducerSourceError):
                    source_original_schedule_constructor_for_verified_producer(
                        source_emission_kind=kind,original_source_producer_va=producer,
                        original_native_constructor_callsite_va=site)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "owner-private original PE not mounted in hosted CI")
    def test_original_producer_sites_and_class_vtables_match_private_exe(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        source_sites={
            0x617490:"e8 5b 90 ef ff",
            0x4F66C9:"e8 52 9e 01 00",
            0x4F6A02:"e8 39 9c 01 00",
            0x4F6A64:"e8 17 9c 01 00",
            0x4FADBE:"e8 2d 57 01 00",
            0x4FAE30:"e8 bb 56 01 00",
            0x51050E:"c7 06 24 4c 7c 00",
            0x51054D:"c7 06 9c 9d 7c 00",
            0x51066B:"c7 06 f8 9e 7c 00",
            0x5106B3:"c7 06 70 9f 7c 00",
        }
        for va,hx in source_sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__ == "__main__":
    unittest.main()
