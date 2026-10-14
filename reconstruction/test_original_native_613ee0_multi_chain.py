"""Native 613EE0 full linked pending-list order before due callbacks.

No test in this file asserts that an original native callback, global queue
unlink, user+6B4 append or PEAMail render actually occurred.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into
from unittest import TestCase, main

from original_native_613ee0_multi_chain import (
    Original613EE0LinkedEvent,
    Original613EE0MultiChainReached,
    Original613EE0MultiChainSourceError,
    source_original_613ee0_multi_chain_pre_callback,
)


def queue(*items, today=0, caller=0x41A364):
    """Independent little-endian original wrapper/header fixture bytes."""
    raw_header = bytearray(0x14)
    raw_nodes = []
    for i, (vtable, due) in enumerate(items):
        ptr, event_ptr = 0x10000 + 0x100*i, 0x50000 + 0x100*i
        next_ptr = 0x10000 + 0x100*(i+1) if i+1 < len(items) else 0
        previous_ptr = 0x10000 + 0x100*(i-1) if i > 0 else 0
        raw_node = bytearray(12)
        pack_into("<III", raw_node, 0, event_ptr, next_ptr, previous_ptr)
        size = 12 if vtable == 0x7BD564 else 20
        event = bytearray(size)
        pack_into("<II", event, 0, vtable, due)
        pack_into("<I", event, 8 if vtable == 0x7BD564 else 12, 0xA0000+i)
        raw_nodes.append(Original613EE0LinkedEvent(
            ptr, bytes(raw_node), event_ptr, bytes(event)))
    if raw_nodes:
        pack_into("<II", raw_header, 4,
                  raw_nodes[0].wrapper_pointer, raw_nodes[-1].wrapper_pointer)
    pack_into("<I", raw_header, 0, 1)
    return Original613EE0MultiChainReached(
        bytes(raw_header), tuple(raw_nodes), today, caller)


class SourceOriginal613EE0MultiChainTests(TestCase):
    def test_empty_source_queue_is_not_a_due_inbox(self):
        source = queue()
        result = source_original_613ee0_multi_chain_pre_callback(source)
        self.assertTrue(result.original_full_input_chain_validated)
        self.assertEqual(result.source_decisions_in_native_order, ())
        self.assertFalse(result.live_game_state_updated)
        self.assertFalse(result.original_inbox_rendered)

    def test_mixed_human_notice_and_player_expiry_follow_native_fifo_order(self):
        source = queue(
            (0x7BD564, 0xFFFFFFFF),  # signed due=-1
            (0x7D7760, 0),
            (0x7BD564, 1),
            (0x7D7760, 0xFFFFFFFF),
            today=0)
        result = source_original_613ee0_multi_chain_pre_callback(source)
        items = result.source_decisions_in_native_order
        self.assertEqual(len(items), 4)
        self.assertEqual(tuple(item.event_vtable for item in items),
                         (0x7BD564,0x7D7760,0x7BD564,0x7D7760))
        self.assertEqual(tuple(item.source_virtual10_would_be_called for item in items),
                         (True, True, False, True))
        self.assertEqual(tuple(item.source_4ea190_would_follow_callback for item in items),
                         (True, True, False, True))
        self.assertEqual(tuple(item.original_cached_next_wrapper_pointer for item in items),
                         (0x10100, 0x10200, 0x10300, 0))
        self.assertEqual((result.original_first_wrapper_pointer,
                          result.original_last_wrapper_pointer), (0x10000, 0x10300))
        self.assertFalse(result.original_native_callbacks_executed)
        self.assertFalse(result.original_native_global_queue_mutated)
        self.assertFalse(result.original_user_mailbox_retention_executed)

    def test_signed_native_calendar_boundaries_and_no_early_delivery(self):
        for day, due, expected in (
            (0x7FFFFFFF,0x80000000,True),
            (0x80000000,0x7FFFFFFF,False),
            (0xFFFFFFFE,0xFFFFFFFF,False),
            (0xFFFFFFFF,0xFFFFFFFE,True),
            (0,0,True),
            (0,1,False),
        ):
            with self.subTest(day=day,due=due):
                result = source_original_613ee0_multi_chain_pre_callback(
                    queue((0x7BD564,due),today=day))
                self.assertEqual(result.source_decisions_in_native_order[0]
                                 .source_virtual10_would_be_called,expected)

    def test_all_five_original_flag1_callers_share_same_native_scan(self):
        for caller in (0x41A364,0x41A475,0x43216C,0x4A8084,0x5E3335):
            with self.subTest(caller=hex(caller)):
                result = source_original_613ee0_multi_chain_pre_callback(
                    queue((0x7D7760, 0), caller=caller))
                self.assertTrue(result.source_decisions_in_native_order[0]
                                .source_4ea190_would_follow_callback)

    def test_bad_links_aliases_missing_nodes_and_unverified_event_fail_closed(self):
        source=queue((0x7BD564,0),(0x7D7760,1))
        a,b=source.ordered_source_nodes
        wrong_next=bytearray(a.wrapper_before)
        pack_into("<I",wrong_next,4,0)
        wrong_previous=bytearray(b.wrapper_before)
        pack_into("<I",wrong_previous,8,0)
        bad_event=bytearray(a.event_before)
        pack_into("<I",bad_event,0,0x7BDB1C)  # transfer class is not 7BD564 wrapper
        bad_payload=bytearray(a.event_before)
        pack_into("<I",bad_payload,8,0)
        bad_header=bytearray(source.global_947aa8_header_before)
        pack_into("<I",bad_header,8,0x99999)
        active_header=bytearray(source.global_947aa8_header_before)
        pack_into("<I",active_header,0xC,1)
        deferred_header=bytearray(source.global_947aa8_header_before)
        pack_into("<I",deferred_header,0x10,1)
        examples=(
            replace(source,ordered_source_nodes=(a,)),
            replace(source,ordered_source_nodes=(b,a)),
            replace(source,ordered_source_nodes=(a,a)),
            replace(source,ordered_source_nodes=(replace(a,wrapper_before=bytes(wrong_next)),b)),
            replace(source,ordered_source_nodes=(a,replace(b,wrapper_before=bytes(wrong_previous)))),
            replace(source,ordered_source_nodes=(replace(a,event_before=bytes(bad_event)),b)),
            replace(source,ordered_source_nodes=(replace(a,event_before=bytes(bad_payload)),b)),
            replace(source,global_947aa8_header_before=bytes(bad_header)),
            replace(source,global_947aa8_header_before=bytes(active_header)),
            replace(source,global_947aa8_header_before=bytes(deferred_header)),
            replace(source,native_caller_address=0x613EC0),
            replace(source,native_remove_flag=0),
            replace(source,native_remove_flag=True),
            replace(source,raw_current_date_9847fc=-1),
        )
        for candidate in examples:
            with self.subTest(bad=candidate):
                with self.assertRaises(Original613EE0MultiChainSourceError):
                    source_original_613ee0_multi_chain_pre_callback(candidate)

    def test_optional_exact_private_native_queue_loop_opcodes(self):
        import os
        from hashlib import sha256
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("Original executable deliberately not distributed in CI")
        exe=Path(path).read_bytes()
        self.assertEqual(sha256(exe).hexdigest(),
                         "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x613EF3:"8b 73 04",  # global head
            0x613F00:"39 41 04",  # native signed compare
            0x613F03:"7f 24",     # future branch
            0x613F07:"ff 52 10", # due virtual callback
            0x613F12:"8b 7e 04", # cache NEXT before 4EA190
            0x613F1C:"e8 6f 62 ed ff",
            0x613F29:"8b 76 04", # future/nonremoval advances next
            0x613F30:"c7 43 0c 00 00 00 00", # active cleared
            0x613F37:"8b 43 10", # deferred flag
        }
        for va,hexdump in signatures.items():
            with self.subTest(va=hex(va)):
                expected=bytes.fromhex(hexdump)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(expected)],
                                 expected)


if __name__ == "__main__":
    main()
