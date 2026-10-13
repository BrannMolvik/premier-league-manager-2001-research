"""Original save writer's v+0x20 index and both global calendar owners."""
from __future__ import annotations
import os
from pathlib import Path
from struct import pack,pack_into
import unittest

from original_native_saved_event_link_writer import (
    OriginalSavedEventLinkSourceError,
    SOURCE_ORIGINAL_BOTH_CALENDAR_SAVE_CALLS,
    SOURCE_ORIGINAL_BOTH_CALENDAR_LOAD_CALLS,
    SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE,
    source_original_saved_event_link_index_5107f0,
)
from original_native_loaded_event_link import SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE


def native(vtable,ident=0,own_field10=0x12345678,link_pointer=0):
    r=bytearray(0x5C)
    pack_into("<I",r,0,vtable)
    pack_into("<I",r,0x0C,ident)
    pack_into("<I",r,8,link_pointer)
    pack_into("<I",r,0x10,own_field10)
    return bytes(r)


class NativeSavedEventLinkWriterTests(unittest.TestCase):
    def test_original_separate_save_and_load_calls_cover_both_event_calendars(self):
        self.assertEqual(SOURCE_ORIGINAL_BOTH_CALENDAR_SAVE_CALLS,
                         ((0x50DC6E,0x947AD8),(0x50DCA9,0x947AF0)))
        self.assertEqual(SOURCE_ORIGINAL_BOTH_CALENDAR_LOAD_CALLS,
                         ((0x50E0A4,0x947AD8),(0x50E0C1,0x947AF0)))
        self.assertEqual(SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE,
                         {0x7C9FE8:0x510840,0x7C4C24:0x510850,
                          0x7C9D9C:0x5108B0,0x7C9E80:0x5108B0,
                          0x7C9EF8:0x5108B0,0x7C9F70:0x5108B0,
                          0x7C9E14:0x510850})
        self.assertEqual(set(SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE),
                         set(SOURCE_ORIGINAL_EVENT_LOAD_V24_BY_VTABLE))

    def test_source_null_link_serializes_as_ffffffff_without_target_lookup(self):
        for vt,method in SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE.items():
            with self.subTest(vt=hex(vt)):
                receipt=source_original_saved_event_link_index_5107f0(
                    original_native_source_event_record=native(vt,0,0xFFEEDDCC),
                    original_native_link_target_address=None,
                    original_native_link_target_event_record=None)
                self.assertEqual(receipt.original_source_virtual20_write_va,method)
                self.assertEqual(receipt.original_serialized_event_dword_10,0xFFEEDDCC)
                self.assertEqual(receipt.original_serialized_link_reference_index,0xFFFFFFFF)
                self.assertFalse(receipt.original_link_target_present)
                self.assertFalse(receipt.source_index_collides_with_null_sentinel)

    def test_original_sar_target_index_is_signed_not_python_unsigned_shift(self):
        for ident,expected,collides in (
            (0,0,False),(1,0,False),(2,1,False),
            (0x7FFFFFFE,0x3FFFFFFF,False),
            (0x80000000,0xC0000000,False),
            (0xFFFFFFFF,0xFFFFFFFF,True),
        ):
            with self.subTest(ident=hex(ident)):
                r=source_original_saved_event_link_index_5107f0(
                    original_native_source_event_record=native(0x7C9D9C,3,link_pointer=0xABCD0000),
                    original_native_link_target_address=0xABCD0000,
                    original_native_link_target_event_record=native(0x7C9FE8,ident))
                self.assertEqual(r.original_serialized_link_reference_index,expected)
                self.assertEqual(r.source_index_collides_with_null_sentinel,collides)
                self.assertTrue(r.original_link_target_present)

    def test_invalid_native_source_or_target_is_never_inferred(self):
        good=dict(original_native_source_event_record=native(0x7C9D9C,link_pointer=0xABCD0000),
                  original_native_link_target_address=0xABCD0000,
                  original_native_link_target_event_record=native(0x7C9FE8,2))
        for change in (
            {'original_native_source_event_record':None},
            {'original_native_source_event_record':native(0xDEADBEEF)},
            {'original_native_source_event_record':native(0x7C9D9C)[:0x13]},
            {'original_native_source_event_record':bytearray(native(0x7C9D9C))},
            {'original_native_link_target_address':None},
            {'original_native_link_target_address':0},
            {'original_native_link_target_address':True},
            {'original_native_link_target_address':0xDEADBEEF},
            {'original_native_source_event_record':native(0x7C9D9C)},
            {'original_native_link_target_event_record':None},
            {'original_native_link_target_event_record':native(0xDEADBEEF)},
            {'original_native_link_target_event_record':native(0x7C9FE8)[:0x0F]},
            {'original_native_link_target_event_record':bytearray(native(0x7C9FE8))},
        ):
            with self.subTest(change=str(change)[:80]),self.assertRaises(
                OriginalSavedEventLinkSourceError):
                source_original_saved_event_link_index_5107f0(**(good|change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                          "original private original PE missing in hosted CI")
    def test_exact_private_source_save_writer_and_both_calendar_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for vt,method in SOURCE_ORIGINAL_EVENT_WRITE_V20_BY_VTABLE.items():
            with self.subTest(vt=hex(vt)):
                self.assertEqual(pe.read(vt+0x20,4),pack("<I",method))
        sites={
            0x5107F0:"56 57",0x5107FB:"8d 46 10",
            0x510806:"8b 76 08",0x51080C:"85 f6",
            0x510810:"8b 4e 0c",0x510813:"d1 f9",
            0x510815:"89 4c 24 0c",
            0x51081B:"c7 44 24 0c ff ff ff ff",
            0x51082D:"e8 75 77 15 00",
            0x50DC69:"b9 d8 7a 94 00",
            0x50DC6E:"e8 fd 87 10 00",
            0x50DCA4:"b9 f0 7a 94 00",
            0x50DCA9:"e8 c2 87 10 00",
            0x50E09E:"b9 d8 7a 94 00",
            0x50E0A4:"e8 57 84 10 00",
            0x50E0BB:"b9 f0 7a 94 00",
            0x50E0C1:"e8 3a 84 10 00",
            0x6164B6:"e8 c5 fb ff ff",
            0x6164D2:"e8 09 fc ff ff",
            0x61657D:"e8 5e fe ff ff",
            0x616599:"e8 b2 fe ff ff",
            0x616461:"ff 50 24",
        }
        for addr,hx in sites.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
