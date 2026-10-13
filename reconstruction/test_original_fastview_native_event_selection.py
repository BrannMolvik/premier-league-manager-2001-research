"""Native FastView second vtable event-source routing, no fake results."""
import os
from pathlib import Path
import unittest
from original_fastview_native_event_selection import (
    OriginalFastViewEventCollectionSourceError,
    source_fastview_original_current_event_51f9f0,
)


class OriginalFastViewEventOwnerSourceTests(unittest.TestCase):
    @staticmethod
    def args():
        return dict(
            original_5112e0_virtual30_return_byte=0,
            original_native_event_current_9847fc=104,
            original_nonzero_event_base_947af8=100,
            original_zero_event_base_947ae0=103,
            original_nonzero_events_by_native_index=(
                0x1000,0x1010,0x1020,0x1030,0x1040),
            original_zero_events_by_native_index=(
                0x2000,0x2010,0x2020),
        )

    def test_mode_zero_selects_947ad8_and_actual_native_cursor_delta(self):
        a=self.args()
        x=source_fastview_original_current_event_51f9f0(**a)
        self.assertEqual(x.mode_5112e0_byte,0)
        self.assertEqual(x.chosen_source_event_array_global_va,0x947ad8)
        self.assertEqual(x.chosen_source_event_base_global_va,0x947ae0)
        self.assertEqual(x.original_offset_from_source_base,1)
        self.assertEqual(x.original_source_event_record_pointer,0x2010)

    def test_nonzero_virtual_byte_selects_distinct_947af0_source(self):
        a=self.args()
        for v in (1,7,255):
            x=source_fastview_original_current_event_51f9f0(
                **(a|{'original_5112e0_virtual30_return_byte':v}))
            self.assertEqual(x.chosen_source_event_array_global_va,0x947af0)
            self.assertEqual(x.chosen_source_event_base_global_va,0x947af8)
            self.assertEqual(x.original_offset_from_source_base,4)
            self.assertEqual(x.original_source_event_record_pointer,0x1040)
        self.assertNotEqual(source_fastview_original_current_event_51f9f0(
            **a).original_source_event_record_pointer,0x1040)

    def test_original_cursor_offset_can_be_zero_but_unverified_negative_fails(self):
        a=self.args()
        out=source_fastview_original_current_event_51f9f0(**(a|{
            'original_native_event_current_9847fc':103}))
        self.assertEqual(out.original_offset_from_source_base,0)
        self.assertEqual(out.original_source_event_record_pointer,0x2000)
        for value in (0,102):
            with self.subTest(value=value),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                source_fastview_original_current_event_51f9f0(**(a|{
                    'original_native_event_current_9847fc':value}))

    def test_no_source_qualified_record_or_array_must_refuse_render(self):
        a=self.args()
        changes=(
            {'original_5112e0_virtual30_return_byte':True},
            {'original_5112e0_virtual30_return_byte':256},
            {'original_5112e0_virtual30_return_byte':-1},
            {'original_native_event_current_9847fc':True},
            {'original_native_event_current_9847fc':0x100000000},
            {'original_nonzero_event_base_947af8':None},
            {'original_zero_event_base_947ae0':-1},
            {'original_zero_events_by_native_index':(0x2000,)},
            {'original_zero_events_by_native_index':(0,0x2010)},
            {'original_zero_events_by_native_index':[0x2000,0x2010]},
            {'original_zero_events_by_native_index':(0x2000,True)},
            {'original_nonzero_events_by_native_index':(0x1000,None)},
        )
        for change in changes:
            with self.subTest(change=repr(change)),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                source_fastview_original_current_event_51f9f0(**(a|change))
        self.assertEqual(source_fastview_original_current_event_51f9f0(
            **a).original_source_event_record_pointer,0x2010)

    def test_native_51f3c0_unsigned_event_names_sort_without_normalization(self):
        from original_fastview_native_event_selection import source_fastview_original_event_name_less_51f3c0
        cmp=source_fastview_original_event_name_less_51f3c0
        def less(a,b):
            return cmp(first_event_virtual14_returned_name_nul=a,
                       second_event_virtual14_returned_name_nul=b)
        self.assertTrue(less(b"A\0",b"Ab\0"))
        self.assertFalse(less(b"Ab\0",b"A\0"))
        self.assertFalse(less(b"A\0",b"A\0ignored"))
        self.assertTrue(less(b"ABC\0",b"ABD\0"))
        self.assertTrue(less(b"HELLO\0",b"hello\0"))
        self.assertTrue(less(b"\x7f\0",b"\x80\0"))
        self.assertFalse(less(b"\x80\0",b"\x7f\0"))
        self.assertTrue(less(b"\0",b"A\0"))
        self.assertFalse(less(b"\0",b"\0"))
        for a,b in ((b"A",b"B\0"),(b"A\0",b"B"),
                    (None,b"A\0"),(b"A\0",bytearray(b"B\0"))):
            with self.subTest(a=a,b=b),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                less(a,b)

    @unittest.skipUnless(os.environ.get('FM2001_ORIGINAL_EXE'),'private owner original executable not mounted')
    def test_original_5112e0_vft30_and_native_51f9f0_source_opcode_sites(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        sites={
            0x7ca590:"f0 f9 51 00",
            0x5112e0:"8b 49 4c",0x5112e3:"8b 01",
            0x5112e5:"ff 50 30",0x5112e8:"25 ff 00 00 00",
            0x51f9f0:"51",0x51f9f5:"8b 8e a8 02 00 00",
            0x51f9fb:"e8 80 b2 10 00",
            0x51fa04:"e8 d7 18 ff ff",0x51fa09:"85 c0",
            0x51fa0d:"a1 fc 47 98 00",0x51fa12:"8b 0d f8 7a 94 00",
            0x51fa18:"2b c1",0x51fa1a:"8b 0d f0 7a 94 00",
            0x51fa21:"8b 14 81",0x51fa2f:"e8 3c 00 00 00",
            0x51fa38:"8b 0d fc 47 98 00",0x51fa3e:"8b 15 e0 7a 94 00",
            0x51fa44:"2b ca",0x51fa46:"8b 15 d8 7a 94 00",
            0x51fa4d:"8b 04 8a",0x51fa5b:"e8 10 00 00 00",
            0x51fa9e:"8b 77 4c",
            0x51f3c0:"8b 44 24 08",
            0x51f3c6:"8b 50 14",
            0x51f3cc:"ff 12",
            0x51f3d2:"8b 40 0c",
            0x51f3e3:"8a 10",
            0x51f3e9:"3a d3",
            0x51f3f9:"3a d3",
            0x51f403:"84 c9",
            0x51f407:"33 c0",
            0x51f415:"1b c0",
            0x51f422:"8a c1",
            0x51fbba:"e8 31 72 00 00",
        }
        for va,hex_bytes in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hex_bytes))),
                                 bytes.fromhex(hex_bytes))
