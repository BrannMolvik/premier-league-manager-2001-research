"""Source native 613EE0 pending one human 7BD564 -> 5CFA20 -> 413020.

This does not assert the original queue was allocated or a visible Inbox row
ever existed. Only exact structural source route from separately reached bytes.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib,os,unittest

from original_native_613ee0_human_due import (
    Original613EE0HumanReached, Original613EE0HumanSourceError,
    source_original_613ee0_human_one_due,
)
from test_original_native_606540_human_mail_route import source


def global_due(*,family=0,recipient=True,lookup=True,day=0,caller=0x41a364,
               header_flag=1,deferred=0):
    notice=source(family=family,recipient=recipient,lookup=lookup,now=day)
    header=bytearray(0x14)
    pack_into("<I",header,0,header_flag)
    pack_into("<II",header,4,0x60000,0x60000)
    wrapper=bytearray(12)
    pack_into("<III",wrapper,0,notice.original_7bd564_wrapper_pointer,0,0)
    return Original613EE0HumanReached(
        original_global_947aa8_queue_header_before=bytes(header),
        original_global_947aa8_wrapper_node_pointer=0x60000,
        original_global_947aa8_wrapper_node_before=bytes(wrapper),
        original_human_due_source=notice,
        original_native_613ee0_caller_va=caller,
        original_native_9847fc_raw_date_at_caller=day,
        original_613ee0_post_callback_deferred_614080_flag=deferred,
    )


class Original613EE0HumanDueTests(unittest.TestCase):
    def test_all_five_source_callers_human_due_unlink_without_claimed_execution(self):
        for caller in (0x41a364,0x41a475,0x43216c,0x4a8084,0x5e3335):
            for family in (0,1,2):
                with self.subTest(caller=hex(caller),family=family):
                    x=global_due(family=family,caller=caller)
                    o=source_original_613ee0_human_one_due(x)
                    self.assertTrue(o.original_source_global_node_unlinked)
                    self.assertEqual(unpack_from("<II",o.original_source_global_queue_after,4),(0,0))
                    self.assertEqual(unpack_from("<II",o.original_source_global_queue_after,0xc),(0,0))
                    self.assertTrue(o.original_source_4ea190_calls_virtual_destructor)
                    self.assertEqual(o.original_source_human_due.original_413020_qualified_recipient_user_pointer,0x2000)
                    self.assertFalse(o.original_actual_global_node_free)
                    self.assertFalse(o.original_actual_notice_constructor_executed)
                    self.assertFalse(o.original_actual_5cfa20_callback_executed)
                    self.assertFalse(o.original_actual_413020_per_user_append)
                    self.assertFalse(o.original_visible_inbox_delivered)
                    self.assertFalse(o.live_game_state_updated)

    def test_no_recipient_and_rechecked_lookup_false_still_consume_due_global_node(self):
        for family in (0,1,2):
            q=global_due(family=family,recipient=False)
            o=source_original_613ee0_human_one_due(q)
            self.assertTrue(o.original_source_global_node_unlinked)
            self.assertIsNone(o.original_source_human_due.original_413020_qualified_recipient_user_pointer)
            if family in (0,1):
                q=global_due(family=family,lookup=False)
                o=source_original_613ee0_human_one_due(q)
                self.assertTrue(o.original_source_human_due.original_413020_deferred_lookup_gated_out)
                self.assertIsNone(o.original_source_human_due.original_413020_candidate_user_queue_pointer)

    def test_queue_policy_zero_skips_vft0_destructor_not_due_callback(self):
        x=global_due(header_flag=0)
        o=source_original_613ee0_human_one_due(x)
        self.assertTrue(o.original_source_global_node_unlinked)
        self.assertFalse(o.original_source_4ea190_calls_virtual_destructor)
        self.assertTrue(o.original_source_human_due.original_413020_qualified_recipient_user_pointer)

    def test_false_owner_future_day_or_reentrant_deferred_fail_closed(self):
        q=global_due()
        header=bytearray(q.original_global_947aa8_queue_header_before)
        pack_into("<I",header,8,0x67000)
        active=bytearray(q.original_global_947aa8_queue_header_before)
        pack_into("<I",active,0xc,1)
        node=bytearray(q.original_global_947aa8_wrapper_node_before)
        pack_into("<I",node,0,0x88888)
        for bad in (
            replace(q,original_global_947aa8_queue_header_before=bytes(header)),
            replace(q,original_global_947aa8_queue_header_before=bytes(active)),
            replace(q,original_global_947aa8_wrapper_node_before=bytes(node)),
            replace(q,original_global_947aa8_wrapper_node_pointer=0),
            replace(q,original_native_613ee0_caller_va=0x613ec0),
            replace(q,original_native_9847fc_raw_date_at_caller=1),
            replace(q,original_native_9847fc_raw_date_at_caller=0xfffffffd),
            replace(q,original_613ee0_post_callback_deferred_614080_flag=1),
            replace(q,original_613ee0_post_callback_deferred_614080_flag=True),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises((Original613EE0HumanSourceError,ValueError)):
                    source_original_613ee0_human_one_due(bad)

    def test_private_native_613ee0_queue_and_user_append_source_if_supplied(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("private source executable not distributed")
        exe=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(exe).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        sig={
            0x613ee5:"c7 43 0c 01 00 00 00",
            0x613eec:"c7 43 10 00 00 00 00",
            0x613f00:"39 41 04",
            0x613f03:"7f 24",
            0x613f07:"ff 52 10",
            0x613f1c:"e8 6f 62 ed ff",
            0x613f37:"8b 43 10",
            0x613f40:"e8 3b 01 00 00",
            0x5cfa20:"56 8b f1",
            0x4134ed:"8b 07 6a 0c",
        }
        for va,s in sig.items():
            with self.subTest(va=hex(va)):
                value=bytes.fromhex(s)
                self.assertEqual(exe[va-0x400000:va-0x400000+len(value)],value)


if __name__=="__main__":unittest.main()
