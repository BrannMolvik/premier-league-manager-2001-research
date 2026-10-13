"""Original PResults 0x4A7210/0x6168C0 dated work, not match totals."""
from __future__ import annotations
import os
from pathlib import Path
import unittest

from original_presults_native_event_work import (
    OriginalPResultsEventSourceError,
    OriginalPResultsNativePreCountNode,
    OriginalPResultsNativeDateBucket,
    OriginalPResultsNativeQueuedEvent,
    source_original_presults_native_current_date_two_pass_6168c0,
    source_original_presults_precount_4a7210,
)


def execution(pointer,**kwargs):
    return OriginalPResultsNativeQueuedEvent(**(
        dict(original_event_pointer=pointer,
             source_virtual_0c_nonzero=True,
             before_event8=0,before_payload44=0) | kwargs))


class OriginalPResultsSourceEventTests(unittest.TestCase):
    def test_original_precount_only_first_container_and_virtual_short_circuit(self):
        def n(pointer,eligible,field8=None,flags=None):
            return OriginalPResultsNativePreCountNode(
                pointer,eligible,field8,flags)
        dates=(
            OriginalPResultsNativeDateBucket(101,(
                n(0x1000,True,0,0),  # yes
                n(0x1004,True,0,1),  # bit0 still counts!
                n(0x1008,True,0,0x40), # bit6 excludes
                n(0x100C,False),  # original virtual+0x0C returns zero, nothing dereferenced
                n(0x1010,True,1), # original +8 excludes, payload getter unvisited
            )),
            OriginalPResultsNativeDateBucket(102,(
                n(0x2000,True,0,0x80), # bit7 not the bit6 source filter
                n(0x2004,True,0,0),
            )),
            OriginalPResultsNativeDateBucket(103,()),
        )
        self.assertEqual(source_original_presults_precount_4a7210(
            original_current_date_global_9847fc=100,
            original_inclusive_upper_date=103,
            original_947ad8_date_buckets=dates,
            original_already_processed_64=3),7)
        self.assertEqual(source_original_presults_precount_4a7210(
            original_current_date_global_9847fc=100,
            original_inclusive_upper_date=100,
            original_947ad8_date_buckets=(),
            original_already_processed_64=9),9)

    def test_original_first_pass_country_human_skips_then_second_pass_processes(self):
        inputs=(
            execution(101,first_pass_616990_human_owned=False,
                      first_pass_510c90_country_member=False,
                      after_first_callback_event8=1,
                      after_first_callback_payload44=0x01),
            execution(102,first_pass_616990_human_owned=True),
            execution(103,first_pass_616990_human_owned=False,
                      first_pass_510c90_country_member=True),
            # original bit0/bit6 and +8 skip both native loops
            execution(104,before_payload44=0x40),
            execution(105,before_payload44=0x01),
            execution(106,before_event8=2),
        )
        got=source_original_presults_native_current_date_two_pass_6168c0(
            original_ordered_date_nodes=inputs)
        self.assertEqual(tuple((x.original_event_pointer,x.source_pass)
                               for x in got.original_progress_callbacks),
                         ((101,1),(102,2),(103,2)))
        self.assertEqual(got.source_progress_tick_count,3)
        self.assertTrue(got.original_6168c0_return_al_nonzero)
        self.assertEqual(tuple(x.native_progress_callback_va
                               for x in got.original_progress_callbacks),
                         (0x4A71F0,)*3)
        self.assertEqual(tuple(x.native_event_virtual_method_offset
                               for x in got.original_progress_callbacks),
                         (0x10,)*3)

    def test_first_pass_event_can_be_processed_twice_if_original_callback_does_not_mark(self):
        native=execution(100,first_pass_616990_human_owned=False,
                         first_pass_510c90_country_member=False,
                         after_first_callback_event8=0,
                         after_first_callback_payload44=0)
        got=source_original_presults_native_current_date_two_pass_6168c0(
            original_ordered_date_nodes=(native,))
        self.assertEqual(tuple(x.source_pass for x in got.original_progress_callbacks),
                         (1,2))
        self.assertEqual(got.source_progress_tick_count,2)
        # Unlike a single match result, the original source may tick more
        # than once if v+0x10 does not set the filter bits before pass two.

    def test_original_first_only_returns_zero_even_when_tick_count_is_positive(self):
        got=source_original_presults_native_current_date_two_pass_6168c0(
            original_ordered_date_nodes=(execution(
                7,first_pass_616990_human_owned=False,
                first_pass_510c90_country_member=False,
                after_first_callback_event8=0,
                after_first_callback_payload44=0x40),))
        self.assertEqual(got.source_progress_tick_count,1)
        self.assertFalse(got.original_6168c0_return_al_nonzero)

    def test_precount_and_live_ticks_have_no_invented_equivalence(self):
        e=OriginalPResultsNativePreCountNode(44,False)
        self.assertEqual(source_original_presults_precount_4a7210(
            original_current_date_global_9847fc=100,
            original_inclusive_upper_date=101,
            original_947ad8_date_buckets=(OriginalPResultsNativeDateBucket(101,(e,)),),
            original_already_processed_64=0),0)
        # Its source runtime execution v+0x0C is irrelevant to 6168C0.
        got=source_original_presults_native_current_date_two_pass_6168c0(
            original_ordered_date_nodes=(
                OriginalPResultsNativeQueuedEvent(44,False,0,0,
                    first_pass_616990_human_owned=True),))
        self.assertEqual(got.source_progress_tick_count,1)

    def test_source_precount_rejects_missing_date_and_unreached_native_fields(self):
        with self.assertRaises(OriginalPResultsEventSourceError):
            OriginalPResultsNativePreCountNode(1,False,0,None)
        with self.assertRaises(OriginalPResultsEventSourceError):
            OriginalPResultsNativePreCountNode(1,True,2,0)
        with self.assertRaises(OriginalPResultsEventSourceError):
            OriginalPResultsNativePreCountNode(1,True,0,None)
        with self.assertRaises(OriginalPResultsEventSourceError):
            OriginalPResultsNativePreCountNode(True,True,0,0)
        for invalid in (
            (1,3,()),
            (1,3,(OriginalPResultsNativeDateBucket(2,()),)),
            (1,3,(OriginalPResultsNativeDateBucket(3,()),OriginalPResultsNativeDateBucket(2,()))),
        ):
            with self.subTest(invalid=str(invalid)),self.assertRaises(OriginalPResultsEventSourceError):
                source_original_presults_precount_4a7210(
                    original_current_date_global_9847fc=invalid[0],
                    original_inclusive_upper_date=invalid[1],
                    original_947ad8_date_buckets=invalid[2],
                    original_already_processed_64=0)

    def test_original_reached_callbacks_and_after_mutation_fail_closed(self):
        base=execution(100,first_pass_616990_human_owned=False,
                       first_pass_510c90_country_member=False,
                       after_first_callback_event8=1,
                       after_first_callback_payload44=1)
        from dataclasses import replace
        invalid=(
            replace(base,first_pass_616990_human_owned=None),
            replace(base,first_pass_510c90_country_member=None),
            replace(base,after_first_callback_event8=None),
            replace(base,after_first_callback_payload44=None),
            replace(base,before_event8=1),
            replace(base,before_payload44=0x40),
            replace(base,first_pass_616990_human_owned=True),
            replace(base,first_pass_510c90_country_member=True),
        )
        for e in invalid:
            with self.subTest(e=str(e)[:95]),self.assertRaises(OriginalPResultsEventSourceError):
                source_original_presults_native_current_date_two_pass_6168c0(
                    original_ordered_date_nodes=(e,))
        with self.assertRaises(OriginalPResultsEventSourceError):
            source_original_presults_native_current_date_two_pass_6168c0(
                original_ordered_date_nodes=[base])


    def test_original_human_pointer_and_country_gate_callbacks_do_not_use_names(self):
        from original_presults_native_event_work import (
            source_original_presults_human_event_616990,
            source_original_presults_country_event_510c90,
        )
        from struct import pack_into
        users=(0x1000,0x2000,0x3000)
        self.assertTrue(source_original_presults_human_event_616990(
            original_human_count_global_8755e4=3,
            original_manager_club_pointers_by_413b10_index=users,
            original_event_first_club_pointer=0x3000,
            original_event_second_club_pointer=0x4000))
        self.assertFalse(source_original_presults_human_event_616990(
            original_human_count_global_8755e4=3,
            original_manager_club_pointers_by_413b10_index=users,
            original_event_first_club_pointer=0x3333,
            original_event_second_club_pointer=0x4444))
        self.assertTrue(source_original_presults_human_event_616990(
            original_human_count_global_8755e4=1,
            original_manager_club_pointers_by_413b10_index=users[:1],
            original_event_first_club_pointer=0x1000,
            original_event_second_club_pointer=None))
        a=bytearray(0x86)
        b=bytearray(0x86)
        pack_into("<H",a,0x84,1);pack_into("<H",b,0x84,1)
        pack_into("<I",a,0x14,42);pack_into("<I",b,0x14,11)
        country=(7,11,13)
        self.assertTrue(source_original_presults_country_event_510c90(
            original_event_first_club_record=bytes(a),
            original_event_second_club_record=bytes(b),
            original_533830_country_indexes_germany_france_england=country))
        pack_into("<I",a,0x14,7)
        self.assertTrue(source_original_presults_country_event_510c90(
            original_event_first_club_record=bytes(a),
            original_event_second_club_record=None,
            original_533830_country_indexes_germany_france_england=country))
        with self.assertRaises(OriginalPResultsEventSourceError):
            source_original_presults_country_event_510c90(
                original_event_first_club_record=bytes(a),
                original_event_second_club_record=bytes(b),
                original_533830_country_indexes_germany_france_england=country)
        pack_into("<H",a,0x84,0)
        pack_into("<I",b,0x14,42)
        self.assertFalse(source_original_presults_country_event_510c90(
            original_event_first_club_record=bytes(a),
            original_event_second_club_record=bytes(b),
            original_533830_country_indexes_germany_france_england=country))
        with self.assertRaises(OriginalPResultsEventSourceError):
            source_original_presults_country_event_510c90(
                original_event_first_club_record=bytes(a),
                original_event_second_club_record=None,
                original_533830_country_indexes_germany_france_england=country)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),"owner original PE unavailable")
    def test_private_original_event_producer_opcode_gate(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        sites={
            0x4A7210:"53",0x4A7217:"8b 3d fc 47 98 00",
            0x4A722a:"47",0x4A7235:"8b 34 81",
            0x4A7240:"ff 52 0c",0x4A7247:"8b 46 08",
            0x4A7252:"ff 50 18",0x4A7255:"8b 48 44",
            0x4A7258:"c1 e9 06",0x4A725e:"75 01",0x4A7260:"43",
            0x6168c0:"a1 fc 47 98 00",
            0x6168de:"8b 06",0x6168e2:"ff 50 18",
            0x6168e7:"8b 46 08",0x6168ee:"8b 47 44",
            0x6168f1:"a8 01",0x6168f5:"c1 e8 06",
            0x6168fd:"e8 8e 00 00 00",
            0x616909:"8b cf",0x61690b:"e8 80 a3 ef ff",
            0x616918:"ff 52 10",0x61691b:"8b 0d 60 68 87 00",
            0x616921:"e8 ca 08 e9 ff",
            0x616946:"8b 16",0x61694a:"ff 52 18",
            0x61694d:"8b 4e 08",0x616954:"8b 48 44",
            0x616959:"c1 ea 06",0x616961:"f6 c1 01",
            0x61696a:"ff 52 10",0x61696d:"8b 0d 60 68 87 00",
            0x616973:"e8 78 08 e9 ff",0x616978:"b3 01",
            0x616985:"5e",0x616986:"8a c3",
            0x616990:"a1 e4 55 87 00",
            0x6169b7:"8b 07",0x6169bd:"3b c6",0x6169c1:"8b 55 28",
            0x6169c7:"ff 12",0x6169c9:"3b c6",
            0x510c90:"56",0x510c93:"8b 46 14",
            0x510c99:"ff 10",0x510c9d:"e8 1e 2b ef ff",
            0x510ca6:"8b 56 28",0x510cac:"ff 12",
            0x510cb0:"e8 0b 2b ef ff",
        }
        for va,hx in sites.items():
            with self.subTest(address=hex(va)):
                self.assertEqual(pe.read(va,len(bytes.fromhex(hx))),bytes.fromhex(hx))


if __name__=="__main__":
    unittest.main()
