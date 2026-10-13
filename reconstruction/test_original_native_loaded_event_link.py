"""Original loaded-event +8 saved registry reference and source reachability."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack,pack_into,unpack_from
import unittest

from original_native_loaded_event_link import (
    OriginalLoadedEventLinkSourceError,
    SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE,
    source_original_loaded_event_base_link_510900,
    source_original_loaded_leaguematch_saved_fields_510970_5109d0,
)


def native_event(vtable, ident):
    r=bytearray(0x60)
    pack_into("<I",r,0,vtable)
    pack_into("<I",r,0x0C,ident)
    pack_into("<I",r,0x08,0)
    pack_into("<I",r,0x10,0xFFFFFFFF)
    return bytes(r)


def restored(**change):
    base=dict(
        original_native_post_constructor_record=native_event(0x7C9D9C,9),
        original_saved_event_dword_10=0x12345678,
        original_saved_link_registry_index=1,
        original_source_selected_registry_pointer_entries=(0x11110000,0x22220000),
    )
    return source_original_loaded_event_base_link_510900(**(base|change))


class OriginalNativeLoadedEventLinkTests(unittest.TestCase):
    def test_native_type0_and_every_loaded_leaguematch_reach_the_exact_base_loader(self):
        expected={
            0x7C9FE8:0x510960,0x7C4C24:0x510970,
            0x7C9D9C:0x5109D0,0x7C9E80:0x5109D0,
            0x7C9EF8:0x5109D0,0x7C9F70:0x5109D0,
            0x7C9E14:0x510970,
        }
        self.assertEqual(SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE,expected)
        for vt,method in expected.items():
            with self.subTest(vt=hex(vt)):
                got=restored(original_native_post_constructor_record=native_event(vt,2))
                self.assertEqual(got.source_virtual24_load_va,method)
                self.assertEqual(got.source_event_registry_collection_va,0x947AD8)
                self.assertEqual(got.source_resolved_link_pointer_dword_08,0x22220000)

    def test_event_id_selects_its_own_original_source_registry_bit(self):
        for ident,selected in ((0,0x947AD8),(1,0x947AF0),
                               (0xFFFFFFFE,0x947AD8),(0xFFFFFFFF,0x947AF0)):
            with self.subTest(ident=hex(ident)):
                original=native_event(0x7C9D9C,ident)
                got=restored(original_native_post_constructor_record=original)
                self.assertEqual(got.source_event_id_dword_0c,ident)
                self.assertEqual(got.source_event_registry_collection_va,selected)
                self.assertEqual(got.source_saved_link_registry_index,1)
                record=got.source_after_base_load_event_record
                self.assertEqual(unpack_from("<I",record,8)[0],0x22220000)
                self.assertEqual(unpack_from("<I",record,0x10)[0],0x12345678)
                self.assertEqual(record[:8],original[:8])
                self.assertEqual(record[0x14:],original[0x14:])

    def test_original_ffffffff_sentinel_skips_entire_registry_access(self):
        for ident in (0,1):
            r=restored(original_native_post_constructor_record=native_event(0x7C9E80,ident),
                       original_saved_link_registry_index=0xFFFFFFFF,
                       original_source_selected_registry_pointer_entries=None)
            self.assertIsNone(r.source_event_registry_collection_va)
            self.assertEqual(r.source_resolved_link_pointer_dword_08,0)
            self.assertEqual(unpack_from("<I",r.source_after_base_load_event_record,8)[0],0)
        with self.assertRaises(OriginalLoadedEventLinkSourceError):
            restored(original_saved_link_registry_index=0xFFFFFFFF)

    def test_dereferenced_registry_pointer_may_be_exact_original_zero(self):
        r=restored(original_saved_link_registry_index=0,
                   original_source_selected_registry_pointer_entries=(0,))
        self.assertEqual(r.source_resolved_link_pointer_dword_08,0)
        self.assertEqual(r.source_event_registry_collection_va,0x947AF0)

    def test_unknown_source_record_and_unreached_values_fail_closed(self):
        cases=(
            dict(original_native_post_constructor_record=bytes(0x13)),
            dict(original_native_post_constructor_record=bytearray(native_event(0x7C9D9C,0))),
            dict(original_native_post_constructor_record=native_event(0xDEADBEEF,0)),
            dict(original_saved_event_dword_10=True),
            dict(original_saved_link_registry_index=None),
            dict(original_saved_link_registry_index=-1),
            dict(original_saved_link_registry_index=0x100000000),
            dict(original_source_selected_registry_pointer_entries=None),
            dict(original_source_selected_registry_pointer_entries=[0x110,0x220]),
            dict(original_source_selected_registry_pointer_entries=(0x110,)),
            dict(original_source_selected_registry_pointer_entries=(0x110,True)),
        )
        for change in cases:
            with self.subTest(change=str(change)[:85]),self.assertRaises(
                OriginalLoadedEventLinkSourceError):
                restored(**change)

    def test_original_restore_510970_preserves_actual_saved_match_flags(self):
        base=restored(original_native_post_constructor_record=native_event(0x7C4C24,0))
        first=base.source_after_base_load_event_record
        got=source_original_loaded_leaguematch_saved_fields_510970_5109d0(
            original_native_record_after_base_load=first,
            original_saved_match_flags44_dword=0xFFFFFFFF,
            original_saved_halfword_3c=0x1234,
            original_saved_halfword_3e=0,
            original_saved_halfword_40=0xABCD,
            original_saved_dword_48=0x00123456)
        after=got.source_native_match_after_field_load
        self.assertEqual(got.original_source_virtual24_load_va,0x510970)
        self.assertEqual(got.source_saved_match_flags44_dword,0xFFFFFFFF)
        self.assertEqual(unpack_from("<I",after,0x44)[0],0xFFFFFFFF)
        self.assertEqual([unpack_from("<H",after,a)[0] for a in (0x3C,0x3E,0x40)],
                         [0x1234,0,0xABCD])
        self.assertEqual(unpack_from("<I",after,0x48)[0],0x00123456)
        self.assertEqual(after[8:0x14],first[8:0x14])
        self.assertEqual(after[0x58:],first[0x58:])
        self.assertEqual(first[0x44:0x4C],bytes(8))

    def test_original_restore_5109d0_restores_four_extended_saved_bytes(self):
        for vt in (0x7C9D9C,0x7C9E80,0x7C9EF8,0x7C9F70):
            base=restored(original_native_post_constructor_record=native_event(vt,1))
            got=source_original_loaded_leaguematch_saved_fields_510970_5109d0(
                original_native_record_after_base_load=base.source_after_base_load_event_record,
                original_saved_match_flags44_dword=0x40,
                original_saved_halfword_3c=65535,
                original_saved_halfword_3e=12,
                original_saved_halfword_40=0,
                original_saved_dword_48=0x87654321,
                original_saved_extended_four_bytes_58_to_5b=bytes((0,0x42,0xFF,0x80)))
            after=got.source_native_match_after_field_load
            self.assertEqual(got.original_source_virtual24_load_va,0x5109D0)
            self.assertEqual(after[0x58:0x5C],bytes((0,0x42,0xFF,0x80)))
            self.assertEqual(unpack_from("<I",after,0x44)[0],0x40)
            self.assertEqual(unpack_from("<I",after,8)[0],0x22220000)

    def test_original_saved_field_loader_fails_closed_on_unreached_reads(self):
        valid=dict(
            original_native_record_after_base_load=native_event(0x7C9D9C,1),
            original_saved_match_flags44_dword=0,
            original_saved_halfword_3c=0,
            original_saved_halfword_3e=0,
            original_saved_halfword_40=0,
            original_saved_dword_48=0,
            original_saved_extended_four_bytes_58_to_5b=b"abcd")
        for change in (
            {"original_native_record_after_base_load":native_event(0x7C9FE8,0)},
            {"original_native_record_after_base_load":bytearray(native_event(0x7C9D9C,1))},
            {"original_native_record_after_base_load":bytes(0x13)},
            {"original_native_record_after_base_load":native_event(0x7C9D9C,1)[:0x5B]},
            {"original_saved_match_flags44_dword":True},
            {"original_saved_halfword_3c":-1},
            {"original_saved_halfword_3e":65536},
            {"original_saved_halfword_40":False},
            {"original_saved_dword_48":0x100000000},
            {"original_saved_extended_four_bytes_58_to_5b":None},
            {"original_saved_extended_four_bytes_58_to_5b":b"abc"},
            {"original_saved_extended_four_bytes_58_to_5b":bytearray(b"abcd")},
        ):
            with self.subTest(change=str(change)[:90]),self.assertRaises(
                OriginalLoadedEventLinkSourceError):
                source_original_loaded_leaguematch_saved_fields_510970_5109d0(**(valid|change))
        valid["original_native_record_after_base_load"]=native_event(0x7C4C24,0)
        with self.assertRaises(OriginalLoadedEventLinkSourceError):
            source_original_loaded_leaguematch_saved_fields_510970_5109d0(**valid)
        valid["original_saved_extended_four_bytes_58_to_5b"]=None
        source_original_loaded_leaguematch_saved_fields_510970_5109d0(**valid)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "private original PE not mounted for hosted CI")
    def test_private_original_load_vtables_and_exact_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt,method in SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE.items():
            with self.subTest(vtable=hex(vt)):
                self.assertEqual(pe.read(vt+0x24,4),pack("<I",method))
        sites={
            0x510300:"f6 41 0c 01",
            0x510304:"b8 f0 7a 94 00",
            0x51030B:"b8 d8 7a 94 00",
            0x510900:"56 57",
            0x51090B:"8d 46 10",
            0x510911:"e8 7a 75 15 00",
            0x51092C:"83 f8 ff",
            0x510934:"89 46 08",
            0x51093F:"e8 bc f9 ff ff",
            0x510944:"8b 50 10",
            0x510947:"8b 3c ba",
            0x51094A:"89 7e 08",
            0x510965:"e8 96 ff ff ff",
            0x510979:"e8 82 ff ff ff",
            0x510981:"8d 46 44",
            0x510987:"e8 04 75 15 00",
            0x5109D9:"e8 92 ff ff ff",
            0x5109E1:"8d 46 58",
        }
        for addr,hx in sites.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
