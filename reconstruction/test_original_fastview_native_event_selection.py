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
            {'original_zero_event_base_947ae0':None},
            {'original_zero_event_base_947ae0':-1},
            {'original_zero_events_by_native_index':(0x2000,)},
            {'original_zero_events_by_native_index':(0,0x2010)},
            {'original_zero_events_by_native_index':[0x2000,0x2010]},
            {'original_zero_events_by_native_index':(0x2000,True)},
            {'original_zero_events_by_native_index':(0x2000,None)},
        )
        for change in changes:
            with self.subTest(change=repr(change)),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                source_fastview_original_current_event_51f9f0(**(a|change))
        self.assertEqual(source_fastview_original_current_event_51f9f0(
            **a).original_source_event_record_pointer,0x2010)
        # Original only dereferences the mode-selected native array/base.
        skipped=source_fastview_original_current_event_51f9f0(**(a|{
            'original_nonzero_event_base_947af8':None,
            'original_nonzero_events_by_native_index':None}))
        self.assertEqual(skipped.original_source_event_record_pointer,0x2010)
        self.assertEqual(source_fastview_original_current_event_51f9f0(**(a|{
            'original_5112e0_virtual30_return_byte':1,
            'original_zero_event_base_947ae0':None,
            'original_zero_events_by_native_index':None
        })).original_source_event_record_pointer,0x1040)
        for change in (
            {'original_5112e0_virtual30_return_byte':1,'original_nonzero_event_base_947af8':None},
            {'original_5112e0_virtual30_return_byte':1,'original_nonzero_events_by_native_index':None}):
            with self.subTest(change=repr(change)),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                source_fastview_original_current_event_51f9f0(**(a|change))


    def test_native_51f3c0_unsigned_event_names_sort_without_normalization(self):
        from original_fastview_native_event_selection import source_fastview_original_event_order_swap_51f3c0
        cmp=source_fastview_original_event_order_swap_51f3c0
        def less(a,b):
            return cmp(first_event_virtual14_returned_name_nul=a,
                       second_event_virtual14_returned_name_nul=b)
        self.assertFalse(less(b"A\0",b"Ab\0"))
        self.assertTrue(less(b"Ab\0",b"A\0"))
        self.assertFalse(less(b"A\0",b"A\0ignored"))
        self.assertFalse(less(b"ABC\0",b"ABD\0"))
        self.assertFalse(less(b"HELLO\0",b"hello\0"))
        self.assertFalse(less(b"\x7f\0",b"\x80\0"))
        self.assertTrue(less(b"\x80\0",b"\x7f\0"))
        self.assertFalse(less(b"\0",b"A\0"))
        self.assertFalse(less(b"\0",b"\0"))
        for a,b in ((b"A",b"B\0"),(b"A\0",b"B"),
                    (None,b"A\0"),(b"A\0",bytearray(b"B\0"))):
            with self.subTest(a=a,b=b),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                less(a,b)

    def test_native_51fa70_original_source_filtered_pointers_are_name_sorted(self):
        from original_fastview_native_event_selection import source_fastview_original_unique_named_event_sort_51fa70
        original=((0x3333,b"Zulu\0"),(0x5555,b"Alpha\0"),(0x7777,b"Yankee\0"))
        sorted_source=source_fastview_original_unique_named_event_sort_51fa70(
            original_selected_event_pointer=0x3333,
            original_51fa70_filtered_candidate_pointers_and_indirect_names=original)
        self.assertEqual(sorted_source.original_sorted_source_event_pointers,
                         (0x5555,0x7777,0x3333))
        self.assertEqual(sorted_source.original_selected_event_sorted_ordinal,2)
        self.assertEqual(original,((0x3333,b"Zulu\0"),(0x5555,b"Alpha\0"),(0x7777,b"Yankee\0")))
        singleton=source_fastview_original_unique_named_event_sort_51fa70(
            original_selected_event_pointer=1,
            original_51fa70_filtered_candidate_pointers_and_indirect_names=((1,b"\0"),))
        self.assertEqual(singleton.original_sorted_source_event_pointers,(1,))
        self.assertEqual(singleton.original_selected_event_sorted_ordinal,0)

    def test_original_sort_filters_and_duplicate_ties_fail_not_invented(self):
        from original_fastview_native_event_selection import source_fastview_original_unique_named_event_sort_51fa70 as sort
        good=dict(original_selected_event_pointer=5,
                  original_51fa70_filtered_candidate_pointers_and_indirect_names=((5,b"A\0"),(7,b"B\0")))
        for bad in (
            {'original_selected_event_pointer':0},
            {'original_selected_event_pointer':True},
            {'original_selected_event_pointer':9},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':()},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':[(5,b"A\0")]},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((7,b"B\0"),(5,b"A\0"))},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((5,b"A\0"),(7,b"A\0"))},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((5,b"A\0"),(5,b"B\0"))},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((5,b"A"),(7,b"B\0"))},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((5,b"A\0"),(7,bytearray(b"B\0")))},
            {'original_51fa70_filtered_candidate_pointers_and_indirect_names':((5,b"A\0"),(7,b"B\0"))*65},
        ):
            with self.subTest(bad=repr(bad)[:100]),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                sort(**(good|bad))

    def test_original_51fa70_linked_filter_then_native_name_sort(self):
        from struct import pack_into
        from original_fastview_native_event_selection import (
            OriginalFastViewNativeLinkedEventCandidate,
            source_fastview_original_standard_event_members_51fa70,
            source_fastview_original_unique_named_event_sort_51fa70,
        )
        def record(*,value8=0,value44=0,owner=123,code40=4):
            b=bytearray(0x50)
            pack_into("<I",b,0x08,value8)
            pack_into("<I",b,0x44,value44)
            pack_into("<I",b,0x4C,owner)
            pack_into("<H",b,0x40,code40)
            return bytes(b)
        def candidate(pointer,name="Candidate",callback=None,**kw):
            return OriginalFastViewNativeLinkedEventCandidate(
                pointer,record(**kw),name.encode()+b"\0",callback)
        members=source_fastview_original_standard_event_members_51fa70(
            original_selected_event_pointer=100,
            original_selected_event_owner_pointer_plus4c=123,
            original_selected_event_indirect_name_nul=b"Zulu\0",
            original_linked_candidate_events=(
                candidate(100),candidate(201,"Red",None,value8=1),
                candidate(202,"Blue",None,value44=0x40),
                candidate(203,"Different",None,owner=444),
                candidate(205,"Callback true",True),
                candidate(206,"Alpha",False),
                candidate(207,"Yankee",False),
            ))
        self.assertEqual(members,((100,b"Zulu\0"),(206,b"Alpha\0"),(207,b"Yankee\0")))
        sorted_result=source_fastview_original_unique_named_event_sort_51fa70(
            original_selected_event_pointer=100,
            original_51fa70_filtered_candidate_pointers_and_indirect_names=members)
        self.assertEqual(sorted_result.original_sorted_source_event_pointers,(206,207,100))
        self.assertEqual(sorted_result.original_selected_event_sorted_ordinal,2)

    def test_original_51fa70_callback_required_only_if_source_reached(self):
        from struct import pack_into
        from original_fastview_native_event_selection import (
            OriginalFastViewNativeLinkedEventCandidate,
            source_fastview_original_standard_event_members_51fa70 as filt,
        )
        def c(pointer,owner=5,callback=None,status=0):
            b=bytearray(0x50)
            pack_into("<I",b,0x4c,owner)
            pack_into("<I",b,0x08,status)
            return OriginalFastViewNativeLinkedEventCandidate(pointer,bytes(b),b"E\0",callback)
        base=dict(original_selected_event_pointer=3,
                  original_selected_event_owner_pointer_plus4c=5,
                  original_selected_event_indirect_name_nul=b"S\0")
        self.assertEqual(filt(**(base|{'original_linked_candidate_events':(c(4,owner=6),)})),
                         ((3,b"S\0"),))
        from dataclasses import replace
        # Native source never dereferences a filtered-out record's name.
        filtered=replace(c(4,owner=6),original_event_indirect_name_nul=None)
        self.assertEqual(filt(**(base|{'original_linked_candidate_events':(filtered,)})),
                         ((3,b"S\0"),))
        # The same source name must exist if the branch actually appends it.
        reached=replace(c(4,callback=False),original_event_indirect_name_nul=None)
        with self.assertRaises(OriginalFastViewEventCollectionSourceError):
            filt(**(base|{'original_linked_candidate_events':(reached,)}))

        for variants in (
            (c(4),), # Original callback 510C30 was reached; cannot invent result.
            (c(4,callback=True,status=1),), # Callback not reached.
            (c(3,callback=True),), # Selected never takes callback.
            (c(4,callback=False),c(4,callback=False)), # Duplicate appended.
        ):
            with self.subTest(variant=repr(variants)[:70]),self.assertRaises(OriginalFastViewEventCollectionSourceError):
                filt(**(base|{'original_linked_candidate_events':variants}))
        self.assertEqual(filt(**(base|{'original_linked_candidate_events':()})),
                         ((3,b"S\0"),))
        # Original 0x51FB65 jumps out into special title/return, never
        # reaches the rest of the ordinary iterator or name sort.
        special=bytearray(0x50)
        pack_into("<I",special,0x4C,5)
        pack_into("<H",special,0x40,0xFFFF)
        with self.assertRaises(OriginalFastViewEventCollectionSourceError):
            filt(**(base|{'original_linked_candidate_events':(
                OriginalFastViewNativeLinkedEventCandidate(4,bytes(special),b"Special\0",False),
                c(8,callback=False))}))

        with self.assertRaises(OriginalFastViewEventCollectionSourceError):
            filt(**(base|{'original_linked_candidate_events':[c(4,callback=False)]}))

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
            0x51fab2:"e8 de 8e 14 00",
            0x51fac9:"89 bd a4 00 00 00",
            0x51fada:"41",
            0x51fb71:"89 9c 8d a4 00 00 00",
            0x51fb7e:"40",
            0x51fbd5:"39 38",
            0x51fbe4:"2d a4 00 00 00",
            0x51fbe9:"c1 f8 02",
            0x51fbec:"89 85 a4 02 00 00",
            0x51fb06:"8b 43 08",
            0x51fb0d:"8b 4b 44",
            0x51fb10:"c1 e9 06",
            0x51fb13:"f6 c1 01",
            0x51fb18:"3b df",
            0x51fb49:"39 73 4c",
            0x51fb50:"e8 db 10 ff ff",
            0x51fb55:"84 c0",
            0x51fb60:"66 83 7b 40 ff",
            0x51fc37:"8d 4b 14",
        }
        for va,hex_bytes in sites.items():
            with self.subTest(va=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hex_bytes))),
                                 bytes.fromhex(hex_bytes))
