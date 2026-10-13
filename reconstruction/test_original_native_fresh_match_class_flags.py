"""Original new-match +0x44 source initialization and v+0x30 family routing."""
from __future__ import annotations
import os
from pathlib import Path
from dataclasses import replace
from itertools import product
from struct import pack
import unittest

from original_native_schedule_producer_source import (
    source_original_schedule_constructor_for_verified_producer,
)
from original_schedule_event_native_constructor import (
    source_original_schedule_event_constructor_510380,
)
from original_native_fresh_match_class_flags import (
    OriginalFreshMatchFlagsSourceError,
    source_original_fresh_match_event_serial_510380,
    SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS,
    SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS,
    SOURCE_ORIGINAL_INHERITS_CUP_FLAGS_NATIVE_KINDS,
    source_original_fresh_match_flags44_and_collection,
)


def original_fresh(vt, flag_values=None):
    args=dict(original_native_class_vtable=vt)
    if flag_values is not None:
        a,b,c=flag_values
        args.update(original_source_510520_argument_dword_esp18=a,
                    original_source_510520_argument_dword_esp1c=b,
                    original_source_510520_argument_dword_esp20=c)
    return source_original_fresh_match_flags44_and_collection(**args)


class OriginalNativeFreshMatchFlagsTests(unittest.TestCase):
    def test_all_six_saved_match_classes_and_only_themselves_are_qualified(self):
        self.assertEqual(SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS,
                         {0x7C4C24:1,0x7C9D9C:2,0x7C9E80:3,
                          0x7C9EF8:4,0x7C9F70:5,0x7C9E14:6})
        self.assertEqual(SOURCE_ORIGINAL_ZERO_FLAGS_NATIVE_KINDS,{1,4,6})
        self.assertEqual(SOURCE_ORIGINAL_INHERITS_CUP_FLAGS_NATIVE_KINDS,{2,3,5})
        for vt,kind in SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS.items():
            flags=(None if kind in (1,4,6) else
                   (1,1,0) if kind==3 else
                   (0,1,0) if kind==5 else (0,0,0))
            with self.subTest(vt=hex(vt)):
                got=original_fresh(vt,flags)
                self.assertEqual(got.source_native_virtual28_kind,kind)
                self.assertEqual(got.initial_original_flags44,
                                 0 if kind in (1,2,4,6) else 0x6 if kind==3 else 0x4)
                self.assertTrue(got.source_original_event8_is_zero_immediately_after_constructor)
                self.assertFalse(got.original_event_identity_is_known)
                self.assertEqual(got.source_native_date_collection_pointer,
                                 0x947AF0 if kind==2 else 0x947AD8)

    def test_actual_original_three_constructor_arguments_compose_bits_1_2_3(self):
        for a,b,c in product((0,1),repeat=3):
            flags=(a<<1)|(b<<2)|(c<<3)
            for vt,kind in SOURCE_ORIGINAL_KNOWN_FRESH_LEAGUE_MATCH_KINDS.items():
                if kind in (1,4,6):
                    continue
                if kind==3 and (a,b)!=(1,1):
                    continue
                if kind==5 and b!=1:
                    continue
                with self.subTest(kind=kind,args=(a,b,c)):
                    got=original_fresh(vt,(a,b,c))
                    self.assertEqual(got.initial_original_flags44,flags)
                    self.assertEqual(got.source_native_date_collection_pointer,
                                     0x947AF0 if kind==2 and b==0 else 0x947AD8)
                    self.assertEqual(got.initial_original_flags44 & ~0x0E,0)

    def test_actual_native_subclass_constructor_forces_flag_arguments(self):
        self.assertEqual(original_fresh(0x7C9EF8).initial_original_flags44,0)
        for c in (0,1):
            self.assertEqual(original_fresh(0x7C9E80,(1,1,c)).initial_original_flags44,
                             6|(c<<3))
        for a,c in product((0,1),repeat=2):
            self.assertEqual(original_fresh(0x7C9F70,(a,1,c)).initial_original_flags44,
                             4|(a<<1)|(c<<3))
        for flags in ((0,0,0),(0,1,0),(1,0,1)):
            with self.assertRaises(OriginalFreshMatchFlagsSourceError):
                original_fresh(0x7C9E80,flags)

    def test_actual_dword_arguments_only_consume_low_bit(self):
        got=original_fresh(0x7C9D9C,(0xFFFFFFFF,0x100,0xFFFFFFFE))
        self.assertEqual(got.initial_original_flags44,0x2)
        self.assertEqual(got.source_native_date_collection_pointer,0x947AF0)
        got=original_fresh(0x7C9E80,(0x101,0xFFFFFFFF,0xFFFFFFFE))
        self.assertEqual(got.initial_original_flags44,0x6)
        self.assertEqual(got.source_native_date_collection_pointer,0x947AD8)

    def test_unknown_original_initial_values_refuse_fake_flags_or_date_owner(self):
        for vt,args in (
            (0x7C4CE4,None),
            (0xDEADBEEF,None),
            (0x7C9D9C,None),
            (0x7C9D9C,(0,None,0)),
            (0x7C9D9C,(0,True,0)),
            (0x7C9D9C,(0,1,-1)),
            (0x7C9D9C,(0,1,0x100000000)),
            (0x7C4C24,(0,0,0)),
            (0x7C9EF8,(0,0,0)),
            (0x7C9E14,(0,0,0)),
            (0x7C9E80,(0,1,0)),
            (0x7C9E80,(1,0,0)),
            (0x7C9F70,(0,0,0)),
            (True,None),
        ):
            with self.subTest(vtable=vt,inputs=args),self.assertRaises(
                OriginalFreshMatchFlagsSourceError):
                original_fresh(vt,args)

    def test_original_fresh_collection_selected_serial_even_odd_and_increment(self):
        for vt,args in (
            (0x7C4C24,None),
            (0x7C9D9C,(0,0,0)),
            (0x7C9D9C,(0,1,0)),
            (0x7C9EF8,None),
            (0x7C9F70,(1,1,1)),
        ):
            for before in (0,1,0x7FFFFFFF,0xFFFFFFFF):
                with self.subTest(vtable=hex(vt),flags=args,serial=before):
                    source=original_fresh(vt,args)
                    got=source_original_fresh_match_event_serial_510380(
                        qualified_fresh_source_match=source,
                        original_selected_collection_counter_before=before)
                    direct=source_original_schedule_event_constructor_510380(
                        original_uninitialized_event_record=bytes(0x14),
                        original_collection_pointer=source.source_native_date_collection_pointer,
                        original_collection_serial_counter_before=before)
                    self.assertEqual(got.source_original_event_id_dword_0c,
                                     direct.source_event_id_dword_0c)
                    self.assertEqual(got.original_selected_collection_counter_after,
                                     direct.source_collection_counter_after_constructor)
                    self.assertEqual(got.source_original_event8_immediately_after_constructor,0)
                    self.assertFalse(got.original_live_registry_pointer_is_known)

    def test_forged_or_unqualified_initial_flags_and_owner_refuse_event_id(self):
        valid=original_fresh(0x7C9D9C,(0,1,0))
        forged=(
            replace(valid,initial_original_flags44=0x20),
            replace(valid,initial_original_flags44=True),
            replace(valid,source_native_date_collection_pointer=0x947AF0),
            replace(valid,source_native_date_collection_pointer=0xDEADBEEF),
            replace(valid,source_original_event8_is_zero_immediately_after_constructor=False),
            replace(valid,original_event_identity_is_known=True),
            replace(valid,source_native_virtual28_kind=1),
            replace(valid,original_native_class_vtable=0x7C4CE4),
            replace(original_fresh(0x7C4C24),initial_original_flags44=4),
        )
        for item in forged:
            with self.subTest(forged=item),self.assertRaises(
                OriginalFreshMatchFlagsSourceError):
                source_original_fresh_match_event_serial_510380(
                    qualified_fresh_source_match=item,
                    original_selected_collection_counter_before=3)
        for bad in (None,True,False,-1,0x100000000,"5",2.0):
            with self.subTest(counter=bad),self.assertRaises(
                OriginalFreshMatchFlagsSourceError):
                source_original_fresh_match_event_serial_510380(
                    qualified_fresh_source_match=valid,
                    original_selected_collection_counter_before=bad)
        with self.assertRaises(OriginalFreshMatchFlagsSourceError):
            source_original_fresh_match_event_serial_510380(
                qualified_fresh_source_match=None,
                original_selected_collection_counter_before=0)

    def test_real_startup_producer_class_is_not_a_cup_flag_argument(self):
        generic=source_original_schedule_constructor_for_verified_producer(
            source_emission_kind="league_match",
            original_source_producer_va=0x616FC0,
            original_native_constructor_callsite_va=0x617047)
        got=source_original_fresh_match_flags44_and_collection(
            original_native_class_vtable=generic.original_native_vtable_va)
        self.assertEqual(got.initial_original_flags44,0)
        self.assertEqual(got.source_native_date_collection_pointer,0x947AD8)
        cup=source_original_schedule_constructor_for_verified_producer(
            source_emission_kind="cup_match",
            original_source_producer_va=0x4F64D0,
            original_native_constructor_callsite_va=0x4F66C9)
        with self.assertRaises(OriginalFreshMatchFlagsSourceError):
            source_original_fresh_match_flags44_and_collection(
                original_native_class_vtable=cup.original_native_vtable_va)
        # A Cup class does not prove its constructor's three native flag args.
        self.assertFalse(generic.is_live_original_event)
        self.assertFalse(cup.is_live_original_event)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "private canonical original PE is not present in hosted CI")
    def test_exact_original_native_source_fields_and_kind_callback_opcode(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x5104CF:"89 46 44",
            0x51061D:"6a 01",
            0x51061F:"6a 01",
            0x510654:"6a 00",
            0x510656:"6a 00",
            0x510658:"6a 00",
            0x51069D:"6a 01",
            0x510567:"8b 54 24 20",
            0x51056B:"8b 44 24 1c",
            0x51056F:"8b 4c 24 18",
            0x510573:"83 e2 01",
            0x510576:"d1 e2",
            0x510580:"8b 46 44",
            0x510587:"24 f1",
            0x510589:"d1 e2",
            0x51058F:"89 56 44",
            0x651E20:"b8 01 00 00 00 c3",
            0x6CE1E0:"b8 02 00 00 00 c3",
            0x6CE1F0:"b8 03 00 00 00 c3",
            0x6CECB0:"b8 04 00 00 00 c3",
            0x650010:"b8 05 00 00 00 c3",
            0x650250:"b8 06 00 00 00 c3",
            0x651980:"32 c0 c3",
            0x5112C8:"83 f8 02",
            0x5112CD:"f6 46 44 04",
            0x5112D3:"b0 01",
        }
        for va,hx in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))
        # Actual source virtual+0x28 method ownership, not a Python name map.
        virtual28={0x7C4C24:0x651E20,0x7C9D9C:0x6CE1E0,
                   0x7C9E80:0x6CE1F0,0x7C9EF8:0x6CECB0,
                   0x7C9F70:0x650010,0x7C9E14:0x650250}
        for vt,fun in virtual28.items():
            self.assertEqual(pe.read(vt+0x28,4),pack("<I",fun))


if __name__ == "__main__":
    unittest.main()
