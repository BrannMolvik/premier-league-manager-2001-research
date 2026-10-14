"""Original v3C 0x615D10 outer calendar slot scan with reached callbacks."""
from __future__ import annotations

from struct import pack_into
from pathlib import Path
import os
import unittest

from original_native_v3c_calendar_second_pass import (
    source_original_615d10_calendar_date_window,
)
from original_native_615d10_linked_slot_walk import (
    Original615D10ReachedStep,
    Original615D10SlotWalkError,
    source_original_615d10_linked_slot_walk_from_reached,
)


def reg(base=0x2000,count=4,datebase=100):
    raw=bytearray(12)
    pack_into("<III",raw,0,base,count&0xFFFFFFFF,datebase)
    return bytes(raw)


def window(*,raw=None,day=101):
    return source_original_615d10_calendar_date_window(
        original_calendar_registry_va=0x947AD8,
        original_registry_record=reg() if raw is None else raw,
        original_requested_date_index=day,
    )


def step(*,before=None,head=0,eax=0,after=None):
    return Original615D10ReachedStep(
        original_registry_at_slot_call=reg() if before is None else before,
        original_slot_head_pointer=head,
        original_reached_615c50_eax=eax,
        original_registry_after_zero_result=after,
    )


def scan(calls,win=None,**kwargs):
    return source_original_615d10_linked_slot_walk_from_reached(
        original_date_window=window() if win is None else win,
        original_reached_slot_calls=tuple(calls),**kwargs)


class OriginalNative615D10WalkTests(unittest.TestCase):
    def test_outer_scan_skips_empty_slot_then_returns_reached_source_node(self):
        r=scan((
            step(head=0,eax=0,after=reg()),
            step(head=0xA000,eax=0xB000),
        ))
        self.assertEqual(r.original_reached_slot_indices,(1,2))
        self.assertEqual(r.original_reached_slot_addresses,(0x2004,0x2008))
        self.assertEqual(r.original_returned_native_node_pointer,0xB000)
        self.assertTrue(r.source_outer_scan_complete)
        self.assertFalse(r.original_615c50_mutating_callbacks_reconstructed)
        self.assertFalse(r.native_match_world_updated)

    def test_callback_can_change_registry_count_and_end_scan(self):
        r=scan((step(head=0xA000,eax=0,after=reg(count=2)),))
        self.assertEqual(r.original_reached_slot_indices,(1,))
        self.assertEqual(r.original_returned_native_node_pointer,0)

    def test_original_reloads_pointer_base_after_mutating_callback(self):
        r=scan((
            step(head=0xA000,eax=0,after=reg(base=0x3000)),
            step(before=reg(base=0x3000),head=0xB000,eax=0xC000),
        ))
        self.assertEqual(r.original_reached_slot_addresses,
                         (0x2004,0x3008))
        self.assertEqual(r.original_returned_native_node_pointer,0xC000)


    def test_actual_v3c_to_5127a0_to_615d10_first_lookup_source_route(self):
        from original_native_v3c_reschedule_gate import (
            source_original_v3c_511429_reschedule_gate,
            source_original_5127a0_first_calendar_request,
        )
        from original_native_v3c_calendar_second_pass import (
            source_original_615d10_reached_request_date_window,
        )
        match=bytearray(0x50)
        pack_into("<I",match,0,0x7C9D9C)
        pack_into("<I",match,0x44,1)
        pack_into("<I",match,0x4C,0xA000)
        gated=source_original_v3c_511429_reschedule_gate(
            original_native_match_at_gate=bytes(match),
            original_first_5112e0_virtual30_eax=0,
            original_second_5112e0_virtual30_eax=0)
        processing_owner=bytearray(4)
        pack_into("<I",processing_owner,0,0xB000)
        first=source_original_5127a0_first_calendar_request(
            original_gate=gated,
            original_processing_owner_at_reschedule=bytes(processing_owner),
            original_reached_global_date_index_9847fc=101)
        w=source_original_615d10_reached_request_date_window(
            original_native_lookup_request=first,
            original_registry_record_at_lookup=reg(base=0x2000,count=10,datebase=100))
        result=scan((
            step(before=reg(base=0x2000,count=10,datebase=100),
                 head=0xD000,eax=0xE000),
        ),win=w)
        self.assertEqual(first.native_calendar_registry_va,0x947AD8)
        self.assertEqual(first.first_requested_date_index,102)
        self.assertEqual(result.original_reached_slot_indices,(2,))
        self.assertEqual(result.original_returned_native_node_pointer,0xE000)
        self.assertFalse(result.native_match_world_updated)

    def test_original_skips_615c50_when_calendar_date_out_of_window(self):
        r=scan((),win=window(day=200))
        self.assertEqual(r.original_reached_slot_indices,())
        self.assertEqual(r.original_returned_native_node_pointer,0)
        with self.assertRaises(Original615D10SlotWalkError):
            scan((step(),),win=window(day=200))

    def test_negative_native_slot_or_missing_vector_fail_closed(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"negative"):
            scan((step(),),win=window(day=99))
        with self.assertRaisesRegex(Original615D10SlotWalkError,"null"):
            scan((step(before=reg(base=0)),),
                 win=window(raw=reg(base=0)))

    def test_wrong_first_registry_or_unsupported_date_result(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"first reached"):
            scan((step(before=reg(base=0x3000),head=0xA000,eax=0xA000),))
        with self.assertRaises(Original615D10SlotWalkError):
            source_original_615d10_linked_slot_walk_from_reached(
                original_date_window=object(),
                original_reached_slot_calls=())

    def test_no_reached_node_results_after_source_stop(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"surplus"):
            scan((
                step(head=0x1000,eax=0x2000),
                step(head=0x3000,eax=0x4000),
            ))
        with self.assertRaisesRegex(Original615D10SlotWalkError,"missing"):
            scan((step(head=0,eax=0,after=reg()),))

    def test_zero_callback_must_supply_after_source_count_snapshot(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"rereads"):
            scan((step(head=0x1000,eax=0),))
        with self.assertRaisesRegex(Original615D10SlotWalkError,"without reading"):
            scan((step(head=0x1000,eax=0x1000,after=reg()),))
        with self.assertRaisesRegex(Original615D10SlotWalkError,"cannot return"):
            scan((step(head=0,eax=0xABCD),))

    def test_exact_after_snapshot_must_match_next_reached_registry(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"between"):
            scan((
                step(head=0,eax=0,after=reg(base=0x3000)),
                step(head=0xA000,eax=0xB000),
            ))

    def test_native_slot_walk_requires_uint32_pointers_and_bounded_length(self):
        bad=(
            step(head=True,eax=0),
            step(head=-1,eax=0),
            step(head=0x100000000,eax=0),
            step(head=0x1000,eax=True),
            step(head=0x1000,eax=-1),
            step(before=bytes(11),head=0x1000,eax=0),
        )
        for row in bad:
            with self.subTest(row=row):
                with self.assertRaises(Original615D10SlotWalkError):
                    scan((row,))
        with self.assertRaises(Original615D10SlotWalkError):
            scan((step(head=0x1000,eax=0x2000),),max_slots=0)
        with self.assertRaises(Original615D10SlotWalkError):
            scan((step(head=0x1000,eax=0x2000),),max_slots=True)
        with self.assertRaises(Original615D10SlotWalkError):
            scan((step(head=0x1000,eax=0x2000),),max_slots=0x1000001)


    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_exact_original_pe_615d10_reloads_registry_and_returns_first_hit(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        checks=(
            (0x615D10,"53 55 56 8b 74 24 14"),
            (0x615D1A,"8b 4f 08 8b 47 04 2b f1 3b f0 7d 26"),
            (0x615D2E,"8b 07 6a 00 6a 00 53 6a 00 55"),
            (0x615D38,"8d 0c b0 e8 10 ff ff ff"),
            (0x615D40,"85 c0 75 0a"),
            (0x615D44,"8b 47 04 46 3b f0 7c e2"),
            (0x615D4C,"33 c0"),
        )
        for addr,h in checks:
            with self.subTest(va=hex(addr)):
                raw=bytes.fromhex(h)
                self.assertEqual(pe.read(addr,len(raw)),raw)

    def test_pointer_arithmetic_fails_closed_before_wrap(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"overflow"):
            scan((step(before=reg(base=0xFFFFFFFC),head=0x1000,eax=0x2000),),
                 win=window(raw=reg(base=0xFFFFFFFC)))

if __name__=="__main__":
    unittest.main()
