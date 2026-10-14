"""Strict original 0x5127A0 second team and 0x615D10 signed index tests."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into
import unittest

from original_native_v3c_reschedule_gate import (
    OriginalV3CRescheduleGateError,
    source_original_v3c_511429_reschedule_gate,
    source_original_5127a0_first_calendar_request,
)
from original_native_v3c_calendar_second_pass import (
    source_original_5127a0_second_calendar_request,
    source_original_615d10_calendar_date_window,
)


def match(*, bit=0, vtable=0x7C9D9C):
    raw=bytearray(0x50)
    pack_into("<I",raw,0,vtable)
    pack_into("<I",raw,0x0C,bit)
    pack_into("<I",raw,0x44,1)
    pack_into("<I",raw,0x4C,0x12340000)
    return bytes(raw)


def processing(*, first=0x01020304, second=0x05060708,count=5):
    result=bytearray(0xB58)
    pack_into("<I",result,0,first)
    pack_into("<I",result,0x5B0,second)
    pack_into("<I",result,0xB54,count)
    return bytes(result)


def staged(*, bit=0, date=100):
    native=match(bit=bit)
    gate=source_original_v3c_511429_reschedule_gate(
        original_native_match_at_gate=native,
        original_first_5112e0_virtual30_eax=0,
        original_second_5112e0_virtual30_eax=0)
    first=source_original_5127a0_first_calendar_request(
        original_gate=gate,
        original_processing_owner_at_reschedule=processing(),
        original_reached_global_date_index_9847fc=date)
    return gate,first,native


def native_calendar(*,head=0x31000000,count=10,base=100):
    raw=bytearray(12)
    pack_into("<III",raw,0,head,count,base)
    return bytes(raw)


class NativeV3CSecondCalendarTests(unittest.TestCase):
    def test_two_pass_second_native_owner_is_offset_5b0_not_first(self):
        gate,first,original_match=staged()
        q=source_original_5127a0_second_calendar_request(
            original_gate=gate,
            original_first_calendar_lookup=first,
            original_match_record_at_second_pass=original_match,
            original_processing_owner_at_second_pass=processing(count=19),
            original_reached_second_pass=True,
            original_reached_global_date_index_9847fc=101)
        self.assertEqual(q.source_original_second_team_pointer,0x05060708)
        self.assertEqual(q.source_original_first_team_pointer,0x01020304)
        self.assertEqual(q.source_second_side_slots_offset,0x5B4)
        self.assertEqual(q.source_second_side_flags_offset,0x5FC)
        self.assertEqual(q.source_second_side_count,19)
        self.assertEqual(q.second_requested_date_index,102)
        self.assertEqual(q.original_date_global_index,101)
        self.assertEqual(q.native_calendar_registry_va,0x947AD8)
        self.assertFalse(q.original_615d10_return_known)
        self.assertFalse(q.later_5127a0_world_callbacks_proven)
        self.assertFalse(q.native_match_completion_proven)

    def test_unchanged_same_native_registry_identity_on_second_pass(self):
        for bit,expect in ((0,0x947AD8),(1,0x947AF0),
                           (2,0x947AD8),(3,0x947AF0)):
            with self.subTest(bit=bit):
                gate,first,native=staged(bit=bit)
                second=source_original_5127a0_second_calendar_request(
                    original_gate=gate,
                    original_first_calendar_lookup=first,
                    original_match_record_at_second_pass=native,
                    original_processing_owner_at_second_pass=processing(),
                    original_reached_second_pass=True,
                    original_reached_global_date_index_9847fc=200)
                self.assertEqual(first.native_calendar_registry_va,expect)
                self.assertEqual(second.native_calendar_registry_va,expect)
                # Source reloads the global date for EACH pass; no
                # unsupported assumption that first and second days equal.
                self.assertEqual(first.first_requested_date_index,101)
                self.assertEqual(second.second_requested_date_index,201)

    def test_second_pass_world_must_be_actual_reached_after_first_iteration(self):
        gate,first,native=staged()
        bad=(
            {"original_gate":object()},
            {"original_reached_second_pass":False},
            {"original_reached_second_pass":1},
            {"original_first_calendar_lookup":object()},
            {"original_match_record_at_second_pass":match(vtable=0x7C4C24)},
            {"original_match_record_at_second_pass":bytes(0x0F)},
            {"original_match_record_at_second_pass":bytearray(native)},
            {"original_processing_owner_at_second_pass":bytes(0xB57)},
            {"original_processing_owner_at_second_pass":processing(second=0)},
            {"original_processing_owner_at_second_pass":processing(first=0)},
            {"original_processing_owner_at_second_pass":bytearray(processing())},
            {"original_reached_global_date_index_9847fc":None},
            {"original_reached_global_date_index_9847fc":True},
            {"original_reached_global_date_index_9847fc":0x100000000},
        )
        kwargs=dict(
            original_gate=gate,
            original_first_calendar_lookup=first,
            original_match_record_at_second_pass=native,
            original_processing_owner_at_second_pass=processing(),
            original_reached_second_pass=True,
            original_reached_global_date_index_9847fc=102)
        for replacement in bad:
            with self.subTest(keys=tuple(replacement)):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_5127a0_second_calendar_request(
                        **(kwargs|replacement))

    def test_615d10_signed_date_delta_in_range_and_first_candidate_slot(self):
        for collection in (0x947AD8,0x947AF0):
            with self.subTest(collection=collection):
                q=source_original_615d10_calendar_date_window(
                    original_calendar_registry_va=collection,
                    original_registry_record=native_calendar(),
                    original_requested_date_index=105)
                self.assertEqual(q.source_calendar_date_base_raw,100)
                self.assertEqual(q.source_calendar_slot_count_raw,10)
                self.assertEqual(q.source_date_delta_signed,5)
                self.assertEqual(q.source_calendar_capacity_signed,10)
                self.assertTrue(q.source_would_enter_615c50_search)
                self.assertEqual(q.first_candidate_slot_pointer,0x31000014)
                self.assertFalse(q.negative_source_slot_index_unqualified)
                self.assertFalse(q.null_original_slot_vector_unqualified)
                self.assertFalse(q.native_search_result_proven)

    def test_615d10_end_is_exclusive_and_skips_iterator(self):
        for offset in (10, 11, 100):
            with self.subTest(offset=offset):
                q=source_original_615d10_calendar_date_window(
                    original_calendar_registry_va=0x947AF0,
                    original_registry_record=native_calendar(),
                    original_requested_date_index=100+offset)
                self.assertFalse(q.source_would_enter_615c50_search)
                self.assertIsNone(q.first_candidate_slot_pointer)
                self.assertFalse(q.native_search_result_proven)

    def test_original_negative_index_is_not_silently_normalized(self):
        q=source_original_615d10_calendar_date_window(
            original_calendar_registry_va=0x947AD8,
            original_registry_record=native_calendar(),
            original_requested_date_index=99)
        self.assertTrue(q.source_would_enter_615c50_search)
        self.assertEqual(q.source_date_delta_signed,-1)
        self.assertEqual(q.first_candidate_slot_pointer,0x30FFFFFC)
        self.assertTrue(q.negative_source_slot_index_unqualified)
        self.assertFalse(q.native_search_result_proven)

    def test_native_signed_comparison_uint32_wrap_and_null_vector(self):
        q=source_original_615d10_calendar_date_window(
            original_calendar_registry_va=0x947AF0,
            original_registry_record=native_calendar(head=0,count=2,base=0xFFFFFFFF),
            original_requested_date_index=0)
        self.assertEqual(q.source_date_delta_signed,1)
        self.assertTrue(q.source_would_enter_615c50_search)
        self.assertEqual(q.first_candidate_slot_pointer,4)
        self.assertTrue(q.null_original_slot_vector_unqualified)

    def test_source_negative_capacity_is_signed(self):
        q=source_original_615d10_calendar_date_window(
            original_calendar_registry_va=0x947AD8,
            original_registry_record=native_calendar(count=0xFFFFFFFF,base=100),
            original_requested_date_index=101)
        self.assertEqual(q.source_calendar_capacity_signed,-1)
        self.assertFalse(q.source_would_enter_615c50_search)

    def test_invalid_original_collection_and_date_fail_closed(self):
        for coll in (0,0x947AF1,False,None,"0x947AD8"):
            with self.subTest(coll=coll):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615d10_calendar_date_window(
                        original_calendar_registry_va=coll,
                        original_registry_record=native_calendar(),
                        original_requested_date_index=100)
        for record in (None,bytearray(12),bytes(11)):
            with self.subTest(record_type=type(record)):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615d10_calendar_date_window(
                        original_calendar_registry_va=0x947AD8,
                        original_registry_record=record,
                        original_requested_date_index=100)
        for date in (None,True,-1,0x100000000):
            with self.subTest(date=date):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615d10_calendar_date_window(
                        original_calendar_registry_va=0x947AD8,
                        original_registry_record=native_calendar(),
                        original_requested_date_index=date)

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_original_pe_second_pass_and_615d10_signed_window(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        signatures=(
            (0x5127BB,"8b a8 b0 05 00 00"),
            (0x5127C1,"83 fb 01 75 2d"),
            (0x5127D2,"8d 88 b4 05 00 00"),
            (0x51280E,"8d 88 fc 05 00 00"),
            (0x512814,"8b 80 54 0b 00 00"),
            (0x51292A,"43 83 fb 02"),
            (0x512932,"0f 85 77 fe ff ff"),
            (0x615D10,"53 55 56 8b 74 24 14"),
            (0x615D1A,"8b 4f 08 8b 47 04"),
            (0x615D20,"2b f1 3b f0 7d 26"),
            (0x615D38,"8d 0c b0 e8 10 ff ff ff"),
            (0x615D44,"8b 47 04 46 3b f0 7c e2"),
            (0x615D4C,"33 c0"),
        )
        for addr,hexbytes in signatures:
            with self.subTest(va=hex(addr)):
                expected=bytes.fromhex(hexbytes)
                self.assertEqual(pe.read(addr,len(expected)),expected)


if __name__=="__main__":
    unittest.main()
