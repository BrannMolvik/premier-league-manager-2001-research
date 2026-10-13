"""Native 0x510380 original two-container event serialization and provenance."""
from __future__ import annotations

import os
from pathlib import Path
from struct import unpack_from,pack
import unittest

from original_schedule_event_native_constructor import (
    OriginalScheduleEventConstructorSourceError,
    source_original_schedule_event_constructor_510380,
)


class OriginalScheduleEventConstructorTests(unittest.TestCase):
    def test_two_original_date_containers_have_distinct_even_odd_serial_ids(self):
        ids=[]
        for container in (0x947AD8,0x947AF0):
            for before in (0,1,2,0x7FFFFFFF):
                initial=b"\xA5"*0x24
                got=source_original_schedule_event_constructor_510380(
                    original_uninitialized_event_record=initial,
                    original_collection_pointer=container,
                    original_collection_serial_counter_before=before)
                tag=((before<<1)&0xFFFFFFFF)|int(container==0x947AF0)
                self.assertEqual(got.source_event_id_dword_0c,tag)
                self.assertEqual(got.source_collection_counter_after_constructor,
                                 (before+1)&0xFFFFFFFF)
                self.assertEqual(unpack_from("<I",got.source_native_event_record_after_constructor,0)[0],0x7C4D70)
                self.assertEqual(unpack_from("<I",got.source_native_event_record_after_constructor,8)[0],0)
                self.assertEqual(unpack_from("<I",got.source_native_event_record_after_constructor,0xC)[0],tag)
                self.assertEqual(unpack_from("<I",got.source_native_event_record_after_constructor,0x10)[0],0xFFFFFFFF)
                self.assertEqual(got.source_native_event_record_after_constructor[4:8],b"\xA5"*4)
                self.assertEqual(got.source_native_event_record_after_constructor[0x14:],b"\xA5"*0x10)
                self.assertEqual(initial,b"\xA5"*0x24)
                ids.append(tag)
        self.assertEqual(ids[:4],[0,2,4,0xFFFFFFFE])
        self.assertEqual(ids[4:],[1,3,5,0xFFFFFFFF])

    def test_native_dword_serial_counter_wraps_and_stays_collection_specific(self):
        a=source_original_schedule_event_constructor_510380(
            original_uninitialized_event_record=bytes(0x14),
            original_collection_pointer=0x947AD8,
            original_collection_serial_counter_before=0xFFFFFFFF)
        b=source_original_schedule_event_constructor_510380(
            original_uninitialized_event_record=bytes(0x14),
            original_collection_pointer=0x947AF0,
            original_collection_serial_counter_before=0xFFFFFFFF)
        self.assertEqual((a.source_event_id_dword_0c,b.source_event_id_dword_0c),
                         (0xFFFFFFFE,0xFFFFFFFF))
        self.assertEqual(a.source_collection_counter_after_constructor,0)
        self.assertEqual(b.source_collection_counter_after_constructor,0)

    def test_unproven_loaded_source_event_and_wrong_collection_rejected(self):
        valid=dict(original_uninitialized_event_record=bytes(0x20),
                   original_collection_pointer=0x947AD8,
                   original_collection_serial_counter_before=1)
        for change in (
            {'original_uninitialized_event_record':bytes(0x13)},
            {'original_uninitialized_event_record':bytearray(0x20)},
            {'original_collection_pointer':0x947AE0},
            {'original_collection_pointer':True},
            {'original_collection_pointer':None},
            {'original_collection_serial_counter_before':True},
            {'original_collection_serial_counter_before':-1},
            {'original_collection_serial_counter_before':0x100000000},
        ):
            with self.subTest(change=str(change)),self.assertRaises(OriginalScheduleEventConstructorSourceError):
                source_original_schedule_event_constructor_510380(**(valid|change))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),"owner original private source not mounted")
    def test_original_510380_native_source_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x510380:"8b 54 24 04",
            0x510386:"33 c9",
            0x510388:"81 fa f0 7a 94 00",
            0x51038e:"0f 94 c1",
            0x510391:"83 e1 01",
            0x510395:"c7 40 08 00 00 00 00",
            0x51039c:"c7 40 10 ff ff ff ff",
            0x5103a3:"c7 00 70 4d 7c 00",
            0x5103a9:"89 48 0c",
            0x5103ac:"8b 72 0c",
            0x5103b2:"d1 e6",
            0x5103b4:"0b ce",
            0x5103b7:"89 48 0c",
            0x5103bd:"41",
            0x5103be:"89 4a 0c",
            0x5103c1:"c2 04 00",
        }
        for addr,hx in sites.items():
            with self.subTest(address=hex(addr)):
                self.assertEqual(pe.read(addr,len(bytes.fromhex(hx))),bytes.fromhex(hx))
