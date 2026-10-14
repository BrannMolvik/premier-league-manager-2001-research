"""Original 606540 15 injury notice classes through 5CF990 user retention.

Source-focused opt-in read stage, not actual native gameplay or visible Inbox.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib
import os
import unittest

from original_native_606540_user_retention import (
    Original606540UserQueueReached, Original606540UserRetentionSourceError,
    source_original_606540_user_notice_retention,
)
from original_native_606540_human_mail_route import source_original_606540_human_notice_due_to_user
from test_original_native_606540_human_mail_route import source


def reached(family=0,status=0,subtype=1,now=363):
    x=source(family=family,status=status,subtype=subtype)
    due=source_original_606540_human_notice_due_to_user(x)
    queue=bytearray(12)
    pack_into("<I",queue,0,1)
    pack_into("<II",queue,4,0x40000,0x40000)
    wrapper=bytearray(12)
    pack_into("<III",wrapper,0,x.original_constructed_notice_pointer,0,0)
    return Original606540UserQueueReached(
        original_human_due_source=x,
        original_registered_user_queue_pointer=due.original_413020_candidate_user_queue_pointer,
        original_registered_user_queue_before=bytes(queue),
        original_per_user_wrapper_pointer=0x40000,
        original_per_user_wrapper_before=bytes(wrapper),
        original_source_current_day_9847fc=now,
    )


class Original606540UserRetentionTests(unittest.TestCase):
    def test_all_fifteen_source_classes_retained_in_original_first_user_queue(self):
        constructors=set()
        for fam in (0,1,2):
            for subtype in (0,1,2):
                for status in (0,1,2,3):
                    if subtype==2 and status>=2:
                        continue
                    with self.subTest(family=fam,subtype=subtype,status=status):
                        x=reached(fam,status,subtype)
                        out=source_original_606540_user_notice_retention(x)
                        constructors.add(out.original_notice_class_vtable)
                        self.assertTrue(out.original_source_keeps_user_notice)
                        self.assertFalse(out.original_source_calls_667d30_and_42cc30_on_expiry)
                        self.assertEqual(out.original_source_node_retained,x.original_per_user_wrapper_before)
                        self.assertEqual(out.original_user_queue_after_source,x.original_registered_user_queue_before)
                        self.assertEqual(out.original_registered_user_pointer,0x2000)
                        self.assertEqual(out.original_per_user_queue_pointer,0x92000)
                        self.assertEqual(out.original_event_date_raw_u32,0xfffffffe)
                        self.assertEqual(out.original_expiry_date_raw_u32,363)
                        self.assertFalse(out.original_native_user_queue_mutated)
                        self.assertFalse(out.original_native_5cf990_executed)
                        self.assertFalse(out.original_inbox_rendered)
                        self.assertFalse(out.live_game_state_updated)
        self.assertEqual(len(constructors),15)

    def test_expiry_inclusive_and_strict_signed_native_int32_wrap(self):
        x=reached(now=363)
        keep=source_original_606540_user_notice_retention(x)
        self.assertTrue(keep.original_source_keeps_user_notice)
        self.assertEqual(keep.original_expiry_date_raw_u32,363)
        x=replace(x,original_source_current_day_9847fc=364)
        remove=source_original_606540_user_notice_retention(x)
        self.assertFalse(remove.original_source_keeps_user_notice)
        self.assertTrue(remove.original_source_calls_667d30_and_42cc30_on_expiry)
        self.assertIsNone(remove.original_source_node_retained)
        self.assertEqual(unpack_from("<II",remove.original_user_queue_after_source,4),(0,0))
        self.assertEqual(unpack_from("<I",remove.original_user_queue_after_source,0)[0],1)
        # Current native signed -1 is before the wrapped positive expiry.
        x=replace(x,original_source_current_day_9847fc=0xffffffff)
        self.assertTrue(source_original_606540_user_notice_retention(x).original_source_keeps_user_notice)

    def test_no_user_or_due_lookup_now_false_never_creates_user_queue(self):
        for family in (0,1,2):
            x=reached(family=family)
            if family<2:
                changed=replace(x.original_human_due_source,
                    original_413020_type_lookup_nonnull_if_reached=False)
            else:
                from struct import pack_into
                globalowner=bytearray(x.original_human_due_source.original_global_874c10_record_at_due)
                pack_into("<I",globalowner,0x9cc,0)
                changed=replace(x.original_human_due_source,
                    original_global_874c10_record_at_due=bytes(globalowner),
                    original_413020_reached_manager_nodes=())
            with self.subTest(family=family):
                with self.assertRaises(Original606540UserRetentionSourceError):
                    source_original_606540_user_notice_retention(replace(
                        x,original_human_due_source=changed))

    def test_mismatched_owner_node_event_and_date_are_refused(self):
        x=reached()
        hdr=bytearray(x.original_registered_user_queue_before)
        pack_into("<I",hdr,8,0x55555)
        node=bytearray(x.original_per_user_wrapper_before)
        pack_into("<I",node,0,0x99999)
        for bad in (
            replace(x,original_registered_user_queue_pointer=0x90000),
            replace(x,original_registered_user_queue_before=bytes(hdr)),
            replace(x,original_per_user_wrapper_pointer=0),
            replace(x,original_per_user_wrapper_before=bytes(node)),
            replace(x,original_per_user_wrapper_before=b"\x00"*11),
            replace(x,original_source_current_day_9847fc=True),
            replace(x,original_source_current_day_9847fc=0x100000000),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original606540UserRetentionSourceError):
                    source_original_606540_user_notice_retention(bad)

    def test_optional_original_470ce0_and_5cf990_retention_byte_contract(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("private source EXE optional")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        originals={
            0x470ce0:"8b 41 04", 0x470ce3:"8b 15 fc 47 98 00",
            0x470ce9:"05 6d 01 00 00",0x470cf0:"3b d0",
            0x470cf2:"0f 9e c1", 0x470cf7:"c3",
            0x5cf995:"8b 73 04",0x5cf99e:"8b 7e 04",
            0x5cf9a3:"ff 50 40",0x5cf9ae:"ff 52 44",
            0x5cf9b8:"e8 73 d2 e5 ff",
            0x42cc30:"56 8b f1",0x42cc3d:"e8 ae ff ff ff",
        }
        for va,hx in originals.items():
            with self.subTest(original_va=hex(va)):
                raw=bytes.fromhex(hx)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":
    unittest.main()
