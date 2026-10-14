"""Native 615D10 caller -> one source-615C50 event node candidate."""
from __future__ import annotations

import os
from pathlib import Path
from struct import pack_into
import unittest

from original_native_v3c_calendar_second_pass import (
    source_original_615d10_calendar_date_window,
)
from original_native_v3c_reschedule_gate import OriginalV3CRescheduleGateError
from original_native_615c50_reached_candidate import (
    source_original_615c50_reached_node_candidate,
)


def window(*,date=102,head=0x30000000,count=10,base=100):
    reg=bytearray(0x0C)
    pack_into("<III",reg,0,head,count,base)
    return source_original_615d10_calendar_date_window(
        original_calendar_registry_va=0x947AD8,
        original_registry_record=bytes(reg),
        original_requested_date_index=date)


def node(*,node_state=0,nextptr=0,vt=0x7C4D70):
    raw=bytearray(0x0C)
    pack_into("<I",raw,0,vt)
    pack_into("<I",raw,4,nextptr)
    pack_into("<I",raw,8,node_state)
    return bytes(raw)


def event(*,flags=0):
    raw=bytearray(0x48)
    pack_into("<I",raw,0x44,flags)
    return bytes(raw)


def candidate(*,win=None,head=0x12340000,v18=0x22220000,
              flags=0,v4=1,initial_state=0,after_state=0,**kwargs):
    if win is None: win=window()
    return source_original_615c50_reached_node_candidate(
        original_reached_date_window=win,
        original_slot_head_node_pointer=head,
        original_node_record_at_virtual18=node(node_state=initial_state),
        original_reached_virtual18_event_pointer=v18,
        original_event_record_after_virtual18=event(flags=flags),
        original_reached_virtual4_comparison_eax=v4,
        original_node_record_after_virtual4=node(node_state=initial_state),
        original_reached_node_state_after_514520=after_state,
        **kwargs,
    )


class Native615C50ReachedNodeTests(unittest.TestCase):
    def test_source_empty_slot_returns_zero_before_any_original_virtuals(self):
        r=source_original_615c50_reached_node_candidate(
            original_reached_date_window=window(),
            original_slot_head_node_pointer=0)
        self.assertEqual(r.source_candidate_decision,"empty_slot_returns_zero")
        self.assertEqual(r.reached_node_pointer,0)
        self.assertIsNone(r.original_returned_slot_node_pointer)
        self.assertFalse(r.original_node_link_traversal_outstanding)
        self.assertFalse(r.source_mutable_virtuals_may_have_executed)
        self.assertFalse(r.native_615d10_complete)
        with self.assertRaises(OriginalV3CRescheduleGateError):
            source_original_615c50_reached_node_candidate(
                original_reached_date_window=window(),
                original_slot_head_node_pointer=0,
                original_node_record_at_virtual18=node())

    def test_virtual18_null_enters_next_original_node_and_not_world_result(self):
        r=source_original_615c50_reached_node_candidate(
            original_reached_date_window=window(),
            original_slot_head_node_pointer=0x1111,
            original_node_record_at_virtual18=node(nextptr=0x2222),
            original_reached_virtual18_event_pointer=0)
        self.assertEqual(r.source_candidate_decision,
                         "null_event_virtual18_advance_node")
        self.assertTrue(r.original_node_link_traversal_outstanding)
        self.assertTrue(r.source_mutable_virtuals_may_have_executed)
        self.assertFalse(r.source_virtual_side_effects_proven)
        self.assertIsNone(r.original_returned_slot_node_pointer)

    def test_native_bit5_excludes_615d10_caller_before_side_comparison(self):
        r=source_original_615c50_reached_node_candidate(
            original_reached_date_window=window(),
            original_slot_head_node_pointer=0x1111,
            original_node_record_at_virtual18=node(),
            original_reached_virtual18_event_pointer=0x2222,
            original_event_record_after_virtual18=event(flags=0x20))
        self.assertEqual(r.source_candidate_decision,
                         "event_flag_bit5_excludes_source_calendar_search")
        self.assertTrue(r.original_node_link_traversal_outstanding)
        with self.assertRaises(OriginalV3CRescheduleGateError):
            source_original_615c50_reached_node_candidate(
                original_reached_date_window=window(),
                original_slot_head_node_pointer=0x1111,
                original_node_record_at_virtual18=node(),
                original_reached_virtual18_event_pointer=0x2222,
                original_event_record_after_virtual18=event(flags=0x20),
                original_reached_virtual4_comparison_eax=1)

    def test_native_v4_side_rejection_never_runs_514520(self):
        r=source_original_615c50_reached_node_candidate(
            original_reached_date_window=window(),
            original_slot_head_node_pointer=0x1111,
            original_node_record_at_virtual18=node(),
            original_reached_virtual18_event_pointer=0x2222,
            original_event_record_after_virtual18=event(),
            original_reached_virtual4_comparison_eax=0)
        self.assertEqual(r.source_candidate_decision,
                         "event_virtual4_side_mismatch_advance_node")
        self.assertIsNone(r.original_returned_slot_node_pointer)
        with self.assertRaises(OriginalV3CRescheduleGateError):
            source_original_615c50_reached_node_candidate(
                original_reached_date_window=window(),
                original_slot_head_node_pointer=0x1111,
                original_node_record_at_virtual18=node(),
                original_reached_virtual18_event_pointer=0x2222,
                original_event_record_after_virtual18=event(),
                original_reached_virtual4_comparison_eax=0,
                original_node_record_after_virtual4=node())

    def test_reached_node_plus8_and_bit6_or_bit0_skip_without_514520(self):
        cases=(
            (0,1,"original_node_plus8_already_nonzero_advance"),
            (0x40,0,"event_flag_bit6_excludes_candidate"),
            (1,0,"event_flag_bit0_excludes_615d10_caller"),
        )
        for flags,state,reason in cases:
            with self.subTest(flags=flags,node_state=state):
                r=source_original_615c50_reached_node_candidate(
                    original_reached_date_window=window(),
                    original_slot_head_node_pointer=0x1111,
                    original_node_record_at_virtual18=node(),
                    original_reached_virtual18_event_pointer=0x2222,
                    original_event_record_after_virtual18=event(flags=flags),
                    original_reached_virtual4_comparison_eax=1,
                    original_node_record_after_virtual4=node(node_state=state))
                self.assertEqual(r.source_candidate_decision,reason)
                self.assertTrue(r.original_node_link_traversal_outstanding)
                self.assertIsNone(r.original_returned_slot_node_pointer)
                self.assertFalse(r.native_event_world_complete)

    def test_mutating_514520_actual_reached_node_state_controls_result(self):
        for post,expected_reason,result_ptr in (
            (0,"original_514520_returned_candidate",0x1111),
            (1,"original_514520_mutated_node_plus8_advance",None),
            (0xFFFFFFFF,"original_514520_mutated_node_plus8_advance",None),
        ):
            with self.subTest(post=post):
                r=source_original_615c50_reached_node_candidate(
                    original_reached_date_window=window(),
                    original_slot_head_node_pointer=0x1111,
                    original_node_record_at_virtual18=node(),
                    original_reached_virtual18_event_pointer=0x2222,
                    original_event_record_after_virtual18=event(),
                    original_reached_virtual4_comparison_eax=1,
                    original_node_record_after_virtual4=node(),
                    original_reached_node_state_after_514520=post)
                self.assertEqual(r.source_candidate_decision,expected_reason)
                self.assertEqual(r.original_returned_slot_node_pointer,result_ptr)
                self.assertFalse(r.native_615d10_complete)
                self.assertFalse(r.native_event_world_complete)

    def test_514520_reached_result_is_required_and_typed(self):
        base=dict(original_reached_date_window=window(),
                  original_slot_head_node_pointer=0x1111,
                  original_node_record_at_virtual18=node(),
                  original_reached_virtual18_event_pointer=0x2222,
                  original_event_record_after_virtual18=event(),
                  original_reached_virtual4_comparison_eax=1,
                  original_node_record_after_virtual4=node())
        for bad in (None,True,-1,0x100000000):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615c50_reached_node_candidate(
                        **base,original_reached_node_state_after_514520=bad)

    def test_original_calendar_window_unsafe_or_unreached_fails_before_slot(self):
        for unsafe in (
            window(date=99),
            window(date=110),
            window(head=0),
        ):
            with self.subTest(unsafe=unsafe.source_date_delta_signed):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615c50_reached_node_candidate(
                        original_reached_date_window=unsafe,
                        original_slot_head_node_pointer=0)

    def test_malformed_virtual_nodes_and_returns_fail_closed(self):
        cases=(
            dict(original_node_record_at_virtual18=None),
            dict(original_node_record_at_virtual18=bytes(11)),
            dict(original_node_record_at_virtual18=bytearray(node())),
            dict(original_node_record_at_virtual18=node(vt=0)),
            dict(original_reached_virtual18_event_pointer=None),
            dict(original_reached_virtual18_event_pointer=True),
            dict(original_reached_virtual18_event_pointer=-1),
            dict(original_reached_virtual18_event_pointer=0x100000000),
            dict(original_event_record_after_virtual18=None),
            dict(original_event_record_after_virtual18=bytes(0x47)),
            dict(original_reached_virtual4_comparison_eax=None),
            dict(original_reached_virtual4_comparison_eax=True),
        )
        base=dict(original_reached_date_window=window(),
                  original_slot_head_node_pointer=0x1111,
                  original_node_record_at_virtual18=node(),
                  original_reached_virtual18_event_pointer=0x2222,
                  original_event_record_after_virtual18=event(),
                  original_reached_virtual4_comparison_eax=1,
                  original_node_record_after_virtual4=node(),
                  original_reached_node_state_after_514520=0)
        for replacement in cases:
            with self.subTest(case=replacement):
                with self.assertRaises(OriginalV3CRescheduleGateError):
                    source_original_615c50_reached_node_candidate(
                        **(base|replacement))

    @unittest.skipUnless(os.environ.get("FM2001_ORIGINAL_EXE"),
                         "owner-private original executable not mounted")
    def test_source_pe_615c50_native_callbacks_and_event_flag_predicates(self):
        from gate13_button_source_trace import OriginalPE32
        pe=OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        checks=(
            (0x615C50,"83 ec 10 53 55 56 57"),
            (0x615C57,"8b 39 85 ff"),
            (0x615C65,"8b 07"),
            (0x615C6D,"ff 50 18"),
            (0x615C76,"8b 4e 44"),
            (0x615C7D,"c1 e9 05 83 e1 01"),
            (0x615CAC,"8b ce ff 55 04"),
            (0x615CC1,"8b 47 08 85 c0"),
            (0x615CCD,"c1 e9 06 f6 c1 01"),
            (0x615CD5,"a8 01"),
            (0x615CE1,"e8 3a e8 ef ff"),
            (0x615CED,"8b 7f 04"),
            (0x615CF8,"8b c7"),
            (0x514520,"56 57 8b f9"),
        )
        for addr,h in checks:
            with self.subTest(va=hex(addr)):
                actual=pe.read(addr,len(bytes.fromhex(h)))
                self.assertEqual(actual,bytes.fromhex(h))


if __name__=="__main__":
    unittest.main()
