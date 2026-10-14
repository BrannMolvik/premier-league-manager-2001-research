"""Original 613EC0 append and 613EE0/4EA190 due queue source tests."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into, unpack_from
import hashlib
import os
import unittest

from original_native_613ee0_pending_list import (
    Original613EC0InsertReached, Original613EE0SingleNodeReached,
    Original613EE0SourceError, source_original_613ec0_insert_from_reached,
    source_original_613ee0_single_due_from_reached,
)
from test_original_native_7d7760_due_cleanup import due as due_callback


def initial_header(*,destructor_enabled=0,active=0,cursor=0):
    b=bytearray(0x14)
    pack_into('<I',b,0,destructor_enabled)
    pack_into('<I',b,0xc,active)
    pack_into('<I',b,0x10,cursor)
    return bytes(b)


def queued(*,day=110,source_day=100,flag=1,header_enabled=1):
    c=due_callback(raw_day=day,producer_day=source_day)
    ins=source_original_613ec0_insert_from_reached(Original613EC0InsertReached(
        initial_header(destructor_enabled=header_enabled,active=97,cursor=62),
        0x20000,0x30000))
    reach=Original613EE0SingleNodeReached(
        ins.original_queue_header_after_source,
        0x20000,ins.original_new_wrapper_source_bytes,0x30000,
        c.original_source_producer.original_pending_event_candidate.original_due_day_raw,
        day,flag,
        c if (c.original_source_producer.original_pending_event_candidate.original_due_day_raw<=day) else None,
    )
    return reach


class Original613EE0PendingSourceTests(unittest.TestCase):
    def test_empty_queue_tail_append_and_one_node_due_removal(self):
        x=queued()
        self.assertEqual(unpack_from('<I',x.original_queue_header_before,4)[0],0x20000)
        self.assertEqual(unpack_from('<I',x.original_queue_header_before,8)[0],0x20000)
        self.assertEqual(unpack_from('<III',x.original_queue_wrapper_before), (0x30000,0,0))
        out=source_original_613ee0_single_due_from_reached(x)
        self.assertTrue(out.original_signed_due)
        self.assertTrue(out.original_due_virtual_dispatch_source_reached)
        self.assertEqual(out.original_source_header_after_scan_before_delivery,
                         initial_header(destructor_enabled=1))
        self.assertIsNone(out.original_source_wrapper_retained)
        self.assertTrue(out.original_event_virtual_zero_destructor_if_removed)
        self.assertTrue(out.original_wrapper_heap_free_if_removed)
        p=out.original_7d7760_player_cleanup_source_receipt.original_player_after_source_cleanup
        self.assertEqual(unpack_from('<I',p,0x24c)[0],0)
        self.assertEqual(unpack_from('<I',p,0x14)[0]&1,0)
        self.assertTrue(out.original_postloop_registered_user_5cf990_unresolved)
        self.assertFalse(out.original_native_queue_callback_executed)
        self.assertFalse(out.original_native_queue_mutated)
        self.assertFalse(out.live_game_state_updated)

    def test_future_item_is_retained_and_header_cursor_reset(self):
        x=queued(day=106)
        self.assertIsNone(x.original_due_nonhuman_player_callback_if_reached)
        o=source_original_613ee0_single_due_from_reached(x)
        self.assertFalse(o.original_signed_due)
        self.assertEqual(o.original_source_wrapper_retained,x.original_queue_wrapper_before)
        self.assertEqual(unpack_from('<I',o.original_source_header_after_scan_before_delivery,4)[0],0x20000)
        self.assertEqual(unpack_from('<I',o.original_source_header_after_scan_before_delivery,8)[0],0x20000)
        self.assertEqual(unpack_from('<I',o.original_source_header_after_scan_before_delivery,0xc)[0],0)
        self.assertEqual(unpack_from('<I',o.original_source_header_after_scan_before_delivery,0x10)[0],0)
        self.assertFalse(o.original_wrapper_heap_free_if_removed)

    def test_flag_zero_runs_due_virtual_without_unlink_as_native_source_branch(self):
        x=queued(flag=0,header_enabled=0)
        out=source_original_613ee0_single_due_from_reached(x)
        self.assertTrue(out.original_due_virtual_dispatch_source_reached)
        self.assertEqual(unpack_from('<I',out.original_source_header_after_scan_before_delivery,4)[0],0x20000)
        self.assertFalse(out.original_wrapper_heap_free_if_removed)
        self.assertFalse(out.original_event_virtual_zero_destructor_if_removed)

    def test_due_queue_removal_calls_conditional_destructor_only_when_enabled(self):
        x=queued(header_enabled=0)
        o=source_original_613ee0_single_due_from_reached(x)
        self.assertFalse(o.original_event_virtual_zero_destructor_if_removed)
        self.assertTrue(o.original_wrapper_heap_free_if_removed)

    def test_insertion_into_nonempty_queue_updates_previous_tail_and_new_prev(self):
        h=bytearray(initial_header())
        pack_into('<I',h,4,0x20000)
        pack_into('<I',h,8,0x20000)
        old=bytearray(12);pack_into('<I',old,0,0x30000)
        x=source_original_613ec0_insert_from_reached(Original613EC0InsertReached(
            bytes(h),0x25000,0x35000,0x20000,bytes(old)))
        self.assertEqual(unpack_from('<I',x.original_queue_header_after_source,4)[0],0x20000)
        self.assertEqual(unpack_from('<I',x.original_queue_header_after_source,8)[0],0x25000)
        self.assertEqual(unpack_from('<III',x.original_new_wrapper_source_bytes),(0x35000,0,0x20000))
        self.assertEqual(unpack_from('<III',x.original_last_wrapper_after_source),(0x30000,0x25000,0))
        self.assertFalse(x.original_native_queue_insert_executed)

    def test_wrong_node_owner_link_and_flag_fail_closed(self):
        q=queued()
        broken=bytearray(q.original_queue_wrapper_before)
        pack_into('<I',broken,4,0x3333)
        for bad in (
            replace(q,original_queue_wrapper_before=bytes(broken)),
            replace(q,original_queue_wrapper_pointer=0x25000),
            replace(q,original_event_pointer=0x35000),
            replace(q,original_remove_after_callback_flag=True),
            replace(q,original_event_date_raw_dword=0xffffffff),
            replace(q,original_target_date_raw_dword=0x100000000),
            replace(q,original_due_nonhuman_player_callback_if_reached=None),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original613EE0SourceError):
                    source_original_613ee0_single_due_from_reached(bad)
        x=Original613EC0InsertReached(initial_header(),0x20000,0x30000,
                                     original_last_wrapper_pointer_before=0x10000)
        with self.assertRaises(Original613EE0SourceError):
            source_original_613ec0_insert_from_reached(x)

    def test_exact_original_executable_queue_opcode_and_callers_if_private(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("original executable private")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        signatures={
            0x613ec0:"56 8b f1",0x613ec3:"6a 0c",
            0x613ece:"89 08",0x613ed6:"e8 95 3e 00 00",
            0x617d70:"8b 51 08",0x617d7b:"89 42 04",0x617d8b:"89 41 08",
            0x617d91:"89 41 08",0x613ee0:"53 8b d9",
            0x613f03:"7f 24",0x613f07:"ff 52 10",0x613f0a:"8b 44 24 14",
            0x613f1c:"e8 6f 62 ed ff",0x4ea190:"56 8b f1",
            0x4ea19d:"e8 4e 2a f4 ff",0x42cbf0:"8b 44 24 04",
            0x42cc08:"89 51 04",0x42cc1e:"89 51 08",
            0x41a35c:"6a 01",0x41a46d:"6a 01",
            0x432164:"6a 01",0x4a807c:"6a 01",0x5e332d:"6a 01",
        }
        for va,signature in signatures.items():
            with self.subTest(original_va=hex(va)):
                s=bytes.fromhex(signature)
                self.assertEqual(data[va-0x400000:va-0x400000+len(s)],s)


if __name__=="__main__":
    unittest.main()
