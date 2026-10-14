"""Regression: source 0x613EE0 due date -> 0x5CFA20 non-Inbox transfer."""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
from struct import pack_into, unpack_from
import unittest

from original_native_5cfa20_due_event_transfer import (
    OriginalQueuedEventTransferError,
    SOURCE_CURRENT_DAY_REMOVE_CALL_SITES,
    source_original_5cfa20_reached_due_transfer,
)

CANONICAL_SHA256 = "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"


def event(*, date=900, owner=0x3000, vtable=0x7BD564):
    b = bytearray(12)
    pack_into("<III", b, 0, vtable, date & 0xffffffff, owner)
    return bytes(b)


def referenced(vtable=0x7D1514, date=25):
    b = bytearray(0x48)
    pack_into("<II", b, 0, vtable, date & 0xffffffff)
    return bytes(b)


def run(*, site=0x41A364, date=900, e=None, ref=None,
        event_ptr=0x2000, obj_ptr=0x3000):
    return source_original_5cfa20_reached_due_transfer(
        original_613ee0_caller_va=site,
        original_613ee0_processing_date=date,
        original_queue_event_pointer=event_ptr,
        original_queue_event_record=event() if e is None else e,
        original_referenced_pointer=obj_ptr,
        original_referenced_object_record=referenced() if ref is None else ref,
    )


class OriginalPendingEventTransferTests(unittest.TestCase):
    def test_actual_five_source_call_sites_all_remove_one_and_use_global_date(self):
        self.assertEqual(SOURCE_CURRENT_DAY_REMOVE_CALL_SITES,
                         (0x41A364, 0x41A475, 0x43216C, 0x4A8084, 0x5E3335))
        for site in SOURCE_CURRENT_DAY_REMOVE_CALL_SITES:
            with self.subTest(site=hex(site)):
                result = run(site=site)
                self.assertEqual(unpack_from("<I", result.original_event_after_5cfa20, 8)[0], 0)
                self.assertEqual(unpack_from("<I", result.original_referenced_after_5cfa20, 4)[0], 900)
                self.assertFalse(result.player_visible_inbox_delivered)
                self.assertFalse(result.native_613ee0_wrapper_deleted)
                self.assertFalse(result.native_413020_executed)
                self.assertFalse(result.live_game_state_updated)

    def test_both_real_referenced_concrete_vtables_have_same_true_virtual3c(self):
        for v in (0x7D1514, 0x7D1568):
            with self.subTest(v=hex(v)):
                result = run(ref=referenced(v))
                self.assertEqual(result.original_event_due_date_signed, 900)
                self.assertEqual(result.original_referenced_pointer, 0x3000)

    def test_source_future_date_skips_all_virtual_and_world_writeback(self):
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "future"):
            run(date=899)
        result=run(date=900)
        self.assertEqual(result.original_processing_date_signed, 900)

    def test_negative_signed_event_date_and_processing_date_use_jg(self):
        result=run(date=-1, e=event(date=-2), ref=referenced(date=0))
        self.assertEqual(result.original_event_due_date_signed, -2)
        self.assertEqual(unpack_from("<i", result.original_referenced_after_5cfa20, 4)[0], -2)
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "future"):
            run(date=-3, e=event(date=-2))

    def test_forged_original_event_vtable_or_reference_object_rejected(self):
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "7BD564"):
            run(e=event(vtable=0x7BD560))
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "referenced object pointer"):
            run(e=event(owner=0x4000))
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "two native classes"):
            run(ref=referenced(0x7D1570))

    def test_skipped_original_caller_or_invalid_pointer_fail_closed(self):
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "five verified"):
            run(site=0x12345678)
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "signed reached"):
            run(date=1 << 31)
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "valid original"):
            run(event_ptr=0)
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "valid original"):
            run(obj_ptr=0x3001)
        with self.assertRaisesRegex(OriginalQueuedEventTransferError, "through"):
            run(e=b"abc")

    def test_native_static_vtables_if_explicit_private_source_supplied(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("private original executable not present in public CI")
        binary=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(binary).hexdigest(), CANONICAL_SHA256)
        # Canonical PE imagebase=0x400000. Image offsets match mapped RVA
        # for these .rdata entries. These tests do not execute the PE.
        def dword(va): return unpack_from("<I", binary, va-0x400000)[0]
        self.assertEqual(dword(0x7BD564+0x10), 0x5CFA20)
        self.assertEqual(dword(0x7D1514+0x3C), 0x4093E0)
        self.assertEqual(dword(0x7D1568+0x3C), 0x4093E0)
        self.assertEqual(binary[0x4093E0-0x400000:0x4093E6-0x400000],
                         bytes.fromhex("B8 01 00 00 00 C3"))


if __name__ == "__main__":
    unittest.main()
