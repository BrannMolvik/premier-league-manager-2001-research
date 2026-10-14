"""Regression: native 5CF990->470CE0 signed +365 event lifetime."""
from __future__ import annotations
from dataclasses import replace
from struct import pack_into
import unittest

from original_native_5cfa20_due_event_transfer import (
    source_original_5cfa20_reached_due_transfer,
)
from original_native_413020_type12_human_route import (
    Original413020ReachedManager, source_original_413020_first_human_owner_for_type12,
)
from original_native_5cf990_type12_retention import (
    OriginalType12RetentionError, source_original_5cf990_type12_retention,
)


def source_event(*, event_day=950, vtable=0x7D1514):
    pending=bytearray(12)
    pack_into("<III",pending,0,0x7BD564,event_day & 0xffffffff,0x9000)
    obj=bytearray(0x48)
    pack_into("<I",obj,0,vtable)
    pack_into("<I",obj,0x10,1)
    pack_into("<I",obj,0x14,77)
    pack_into("<I",obj,0x1c,12)
    return source_original_5cfa20_reached_due_transfer(
        original_613ee0_caller_va=0x43216C,
        original_613ee0_processing_date=event_day,
        original_queue_event_pointer=0x8000,
        original_queue_event_record=bytes(pending),
        original_referenced_pointer=0x9000,
        original_referenced_object_record=bytes(obj),
    )


def selected_user(transfer):
    global_world=bytearray(0x9d0)
    pack_into("<I",global_world,0x9cc,0x1000)
    node=bytearray(8)
    pack_into("<II",node,0,0x2000,0)
    user=bytearray(0x6b8)
    pack_into("<I",user,0x5b4,0x3000)
    pack_into("<I",user,0x6b4,0x5000)
    context=bytearray(0x44)
    pack_into("<I",context,0x40,77)
    step=Original413020ReachedManager(0x1000,bytes(node),0x2000,
                                          bytes(user),0x3000,bytes(context))
    return source_original_413020_first_human_owner_for_type12(
        original_due_transfer=transfer,
        original_global_world_874c10_record=bytes(global_world),
        original_reached_manager_nodes=(step,),
    )


def retain(day, *, event_day=950, vtable=0x7D1514, no_route=False):
    t=source_event(event_day=event_day,vtable=vtable)
    route=selected_user(t)
    if no_route:
        route=replace(route,original_selected_user_event_queue_pointer=None)
    return source_original_5cf990_type12_retention(
        original_due_transfer=t,original_selected_user_route=route,
        original_global_current_day_9847fc=day,
    )


class OriginalType12RetentionTests(unittest.TestCase):
    def test_exact_one_year_end_inclusive_then_cleanup(self):
        r=retain(950+365)
        self.assertEqual(r.original_expiry_day_signed,1315)
        self.assertTrue(r.source_5cf990_keeps_event)
        self.assertFalse(r.source_5cf990_would_call_event_virtual44_and_42cc30)
        r=retain(950+366)
        self.assertFalse(r.source_5cf990_keeps_event)
        self.assertTrue(r.source_5cf990_would_call_event_virtual44_and_42cc30)
        self.assertFalse(r.native_event_deleted)
        self.assertFalse(r.visible_inbox_lifecycle_proven)

    def test_both_original_player_event_classes_share_expiry(self):
        for v in (0x7D1514,0x7D1568):
            with self.subTest(v=hex(v)):
                self.assertTrue(retain(1315,vtable=v).source_5cf990_keeps_event)
                self.assertFalse(retain(1316,vtable=v).source_5cf990_keeps_event)

    def test_signed_date_overflow_is_native_not_python_arithmetic(self):
        r=retain(0x7ffffffe,event_day=0x7ffffffe)
        self.assertEqual(r.original_expiry_day_signed, -0x80000000+363)
        self.assertFalse(r.source_5cf990_keeps_event)
        self.assertTrue(r.source_5cf990_would_call_event_virtual44_and_42cc30)

    def test_source_user_ownership_is_required_before_cleanup(self):
        with self.assertRaisesRegex(OriginalType12RetentionError,"source selected"):
            retain(1316,no_route=True)

    def test_wrong_current_date_or_forged_source_record_failsclosed(self):
        t=source_event()
        route=selected_user(t)
        with self.assertRaisesRegex(OriginalType12RetentionError,"uint32"):
            source_original_5cf990_type12_retention(
                original_due_transfer=t,original_selected_user_route=route,
                original_global_current_day_9847fc=-1,
            )
        with self.assertRaisesRegex(OriginalType12RetentionError,"pointer identity"):
            source_original_5cf990_type12_retention(
                original_due_transfer=t,
                original_selected_user_route=replace(route,original_event_object_pointer=0x9999),
                original_global_current_day_9847fc=1316,
            )


if __name__ == "__main__":
    unittest.main()
