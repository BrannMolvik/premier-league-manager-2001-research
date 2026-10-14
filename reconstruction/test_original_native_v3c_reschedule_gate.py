"""Native v3C 0x511429 source reschedule gate/5127A0 registry routing tests."""
from __future__ import annotations

from dataclasses import replace
from struct import pack_into
import unittest

from original_native_v3c_reschedule_gate import (
    OriginalV3CRescheduleGateError,
    source_original_v3c_511429_reschedule_gate,
    source_original_5127a0_first_calendar_request,
)


def match(*, vtable=0x7C9D9C, flags=1, owner=0x12510000,
          calendar_bit=0):
    raw=bytearray(0x50)
    pack_into("<I",raw,0,vtable)
    pack_into("<I",raw,0x0C,calendar_bit)
    pack_into("<I",raw,0x44,flags)
    pack_into("<I",raw,0x4C,owner)
    return bytes(raw)


def gate(*, first=0, second=0, flags=1, calendar_bit=0, vtable=0x7C9D9C):
    return source_original_v3c_511429_reschedule_gate(
        original_native_match_at_gate=match(
            vtable=vtable, flags=flags,calendar_bit=calendar_bit),
        original_first_5112e0_virtual30_eax=first,
        original_second_5112e0_virtual30_eax=second,
    )


def owner(*, first=0xDEADBC00):
    raw=bytearray(8)
    pack_into("<I",raw,0,first)
    return bytes(raw)


class OriginalV3CCalendarGateTests(unittest.TestCase):
    def test_second_competition_v30_zero_calls_original_rescheduler(self):
        for vtable in (0x7C9D9C,0x7C4C24,0x7C4CE4):
            for first in (0,1,0x100,0x101):
                with self.subTest(vtable=vtable,first=first):
                    receipt=gate(vtable=vtable,first=first,second=0)
                    self.assertTrue(receipt.original_5127a0_called)
                    self.assertEqual(receipt.first_5112e0_return_al,first & 0xFF)
                    self.assertEqual(receipt.second_5112e0_return_al,0)
                    self.assertEqual(
                        receipt.source_prior_side_world_branch_may_have_executed,
                        bool(first & 0xFF))
                    self.assertFalse(receipt.prior_world_effects_proven)
                    self.assertFalse(receipt.native_match_completion_proven)
                    self.assertEqual(receipt.subsequent_source_callbacks,
                                     (0x512710,0x512230))

    def test_second_competition_v30_nonzero_skips_reschedule_only(self):
        result=gate(first=1,second=0x101)
        self.assertFalse(result.original_5127a0_called)
        self.assertEqual(result.second_5112e0_return_al,1)
        self.assertTrue(result.source_prior_side_world_branch_may_have_executed)
        self.assertEqual(result.subsequent_source_callbacks,(0x512710,0x512230))
        self.assertFalse(result.native_match_completion_proven)

    def test_match_bit5_skips_second_virtual_call_and_rescheduler(self):
        for original_first in (0,1,0xFF000001):
            with self.subTest(first=original_first):
                receipt=source_original_v3c_511429_reschedule_gate(
                    original_native_match_at_gate=match(flags=0x21),
                    original_first_5112e0_virtual30_eax=original_first,
                )
                self.assertTrue(receipt.native_flag_bit5_skipped_second_call)
                self.assertFalse(receipt.original_5127a0_called)
                self.assertIsNone(receipt.second_5112e0_return_al)
        with self.assertRaisesRegex(OriginalV3CRescheduleGateError,
                                    "skips second"):
            gate(flags=0x21,first=0,second=0)

    def test_source_reached_gate_rejects_invalid_owner_vtable_and_first_bit(self):
        for record in (
            match(flags=0), match(owner=0),
            match(vtable=0xFFFFFFFF),
            bytes(0x4F), bytearray(match()), None,
        ):
            with self.subTest(record=str(record)[:25]):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_v3c_511429_reschedule_gate(
                        original_native_match_at_gate=record,
                        original_first_5112e0_virtual30_eax=0,
                        original_second_5112e0_virtual30_eax=0)

    def test_both_virtual_returns_must_be_actual_uint32_not_assumptions(self):
        for bad in (None,True,-1,"0",0x100000000):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    gate(first=bad)
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    gate(second=bad)
        with self.assertRaises(OriginalV3CRescheduleGateError):
            source_original_v3c_511429_reschedule_gate(
                original_native_match_at_gate=match(),
                original_first_5112e0_virtual30_eax=0)

    def test_first_reschedule_calendar_registry_source_bit0(self):
        for bit,registry in ((0,0x947AD8),(1,0x947AF0),
                             (2,0x947AD8),(3,0x947AF0)):
            with self.subTest(bit=bit):
                original_gate=gate(calendar_bit=bit)
                q=source_original_5127a0_first_calendar_request(
                    original_gate=original_gate,
                    original_processing_owner_at_reschedule=owner(),
                    original_reached_global_date_index_9847fc=42)
                self.assertEqual(q.native_calendar_registry_va,registry)
                self.assertEqual(q.original_date_global_index,42)
                self.assertEqual(q.first_requested_date_index,43)
                self.assertEqual(q.native_processing_owner_first_pointer,0xDEADBC00)
                self.assertEqual(q.native_615d10_argument_3,1)
                self.assertTrue(q.native_615d10_reached)
                self.assertFalse(q.native_615d10_return_value_known)
                self.assertFalse(q.event_inserted_or_rescheduled_proven)

    def test_native_date_plus_one_uses_exact_uint32_wrap(self):
        q=source_original_5127a0_first_calendar_request(
            original_gate=gate(),
            original_processing_owner_at_reschedule=owner(),
            original_reached_global_date_index_9847fc=0xFFFFFFFF)
        self.assertEqual(q.first_requested_date_index,0)
        self.assertFalse(q.event_inserted_or_rescheduled_proven)

    def test_original_calendar_lookup_requires_reached_reschedule_gate(self):
        options=dict(original_processing_owner_at_reschedule=owner(),
                     original_reached_global_date_index_9847fc=42)
        for original_gate in (object(),gate(second=1),
                              replace(gate(),original_5127a0_called=False)):
            with self.subTest(original_gate=type(original_gate)):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_5127a0_first_calendar_request(
                        original_gate=original_gate,**options)

    def test_original_calendar_lookup_fails_closed_on_missing_reached_world(self):
        cases=(
            (None,42),(bytes(3),42),(bytearray(owner()),42),
            (owner(first=0),42),(owner(),None),(owner(),True),
            (owner(),-1),(owner(),0x100000000),
        )
        for ptr,date in cases:
            with self.subTest(ptr_type=type(ptr),date=date):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_5127a0_first_calendar_request(
                        original_gate=gate(),
                        original_processing_owner_at_reschedule=ptr,
                        original_reached_global_date_index_9847fc=date)


if __name__=="__main__":
    unittest.main()
