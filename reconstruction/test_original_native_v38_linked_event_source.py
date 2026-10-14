"""Fail-closed 0x513570 nonzero linked-event source tests."""
from __future__ import annotations

from struct import pack_into
import unittest

from original_native_v38_linked_event_source import (
    NativeV38LinkedEventSourceError,
    source_native_513570_nonzero_event_entry,
)


def context(a=0, b=0, ptr=0):
    raw = bytearray(0xD14)
    pack_into("<I", raw, 0xD0C, a)
    pack_into("<I", raw, 0xD10, b)
    pack_into("<I", raw, 0xB60, ptr)
    return bytes(raw)


class NativeV38LinkedEntryTests(unittest.TestCase):
    def test_both_counters_zero_returns_without_head_dereference(self):
        x = source_native_513570_nonzero_event_entry(
            original_context=context(ptr=0x1234))
        self.assertEqual(x.first_dispatch, "zero_event_fast_return")
        self.assertEqual(x.initial_event_pointer, 0)
        self.assertFalse(x.needs_original_event_callback_resolution)
        self.assertFalse(x.native_completion_proven)

    def test_primary_nonzero_calls_filter_first(self):
        x = source_native_513570_nonzero_event_entry(
            original_context=context(a=1, b=0, ptr=0x1234))
        self.assertEqual(
            x.first_dispatch, "original_6326b0_and_linked_event_callbacks")
        self.assertTrue(x.needs_original_event_callback_resolution)
        self.assertFalse(x.native_completion_proven)

    def test_secondary_only_uses_different_filter(self):
        x = source_native_513570_nonzero_event_entry(
            original_context=context(a=0, b=9, ptr=0x1234))
        self.assertEqual(
            x.first_dispatch, "original_6326e0_and_linked_event_callbacks")
        self.assertFalse(x.native_completion_proven)

    def test_null_head_does_not_invent_callback(self):
        for a, b, expected in (
            (1, 0, "no_head_primary_score_subtract_then_secondary_gate"),
            (0, 1, "no_head_secondary_gate"),
            (1, 1, "no_head_primary_score_subtract_then_secondary_gate"),
        ):
            with self.subTest(a=a, b=b):
                x = source_native_513570_nonzero_event_entry(
                    original_context=context(a, b))
                self.assertEqual(x.first_dispatch, expected)
                self.assertTrue(x.needs_original_event_callback_resolution)

    def test_only_original_full_context_bytes_accepted(self):
        for bad in (None, bytearray(0xD14), b"", bytes(0xD13)):
            with self.subTest(bad_type=type(bad)):
                with self.assertRaises(NativeV38LinkedEventSourceError):
                    source_native_513570_nonzero_event_entry(
                        original_context=bad)


if __name__ == "__main__":
    unittest.main()
