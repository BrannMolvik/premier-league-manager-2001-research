"""Original v3C 0x615D10 outer calendar slot scan with reached callbacks."""
from __future__ import annotations

from struct import pack_into
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

    def test_pointer_arithmetic_fails_closed_before_wrap(self):
        with self.assertRaisesRegex(Original615D10SlotWalkError,"overflow"):
            scan((step(before=reg(base=0xFFFFFFFC),head=0x1000,eax=0x2000),),
                 win=window(raw=reg(base=0xFFFFFFFC)))

if __name__=="__main__":
    unittest.main()
