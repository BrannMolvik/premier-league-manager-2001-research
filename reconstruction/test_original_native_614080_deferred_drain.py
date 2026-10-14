"""Original 614080 active/deferred drain source and two shipped vtables."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
from struct import pack_into,unpack_from
import hashlib,os,unittest

from original_native_614080_deferred_drain import (
    Original614080Reached, Original614080DrainSourceError,
    source_original_614080_deferred_drain_from_reached,
)


def queue(vtable=0x7d7760, *, active=0, deferred=0, empty=False):
    h=bytearray(0x14)
    pack_into("<I",h,0,1)
    pack_into("<I",h,4,0 if empty else 0x2000)
    pack_into("<I",h,8,0 if empty else 0x2000)
    pack_into("<I",h,0xc,active)
    pack_into("<I",h,0x10,deferred)
    if active or empty:
        return Original614080Reached(bytes(h))
    n=bytearray(12);pack_into("<I",n,0,0x3000)
    ev=bytearray(20);pack_into("<I",ev,0,vtable)
    return Original614080Reached(bytes(h),0x2000,bytes(n),0x3000,bytes(ev))


class Original614080DrainTests(unittest.TestCase):
    def test_reentrant_active_sets_deferred_one_and_skips_dispatch(self):
        x=queue(active=1)
        o=source_original_614080_deferred_drain_from_reached(x)
        self.assertTrue(o.original_deferred_flag_set)
        self.assertEqual(unpack_from("<I",o.original_header_source_after,0x10)[0],1)
        self.assertEqual(unpack_from("<I",o.original_header_source_after,0xc)[0],1)
        self.assertIsNone(o.original_virtual4_source_result_if_called)
        self.assertIsNone(o.original_virtual18_source_result_if_called)
        self.assertFalse(o.original_native_queue_mutated)
        q=replace(x,original_event_pointer=0x3000)
        with self.assertRaisesRegex(Original614080DrainSourceError,"BEFORE scanning"):
            source_original_614080_deferred_drain_from_reached(q)

    def test_known_7d7760_literal1_vft4_and_vft18_retain(self):
        x=queue()
        o=source_original_614080_deferred_drain_from_reached(x)
        self.assertFalse(o.original_deferred_flag_set)
        self.assertTrue(o.original_single_node_retained)
        self.assertEqual((o.original_virtual4_source_result_if_called,
                          o.original_virtual18_source_result_if_called),(1,1))
        self.assertFalse(o.original_4ea190_wrapper_unlink_required)
        self.assertEqual(o.original_header_source_after,x.original_queue_header_before)
        self.assertFalse(o.original_event_virtual4_executed)
        self.assertFalse(o.original_inbox_delivery_verified)

    def test_known_7bd564_dynamic_virtual24_must_be_reached_and_can_remove(self):
        x=queue(0x7bd564)
        with self.assertRaisesRegex(Original614080DrainSourceError,"payload virtual24"):
            source_original_614080_deferred_drain_from_reached(x)
        kept=source_original_614080_deferred_drain_from_reached(replace(
            x,original_7bd564_reached_payload_virtual24_result=1))
        self.assertTrue(kept.original_single_node_retained)
        self.assertEqual((kept.original_virtual4_source_result_if_called,
                          kept.original_virtual18_source_result_if_called),(0,1))
        removed=source_original_614080_deferred_drain_from_reached(replace(
            x,original_7bd564_reached_payload_virtual24_result=0))
        self.assertFalse(removed.original_single_node_retained)
        self.assertTrue(removed.original_4ea190_wrapper_unlink_required)
        self.assertEqual(unpack_from("<I",removed.original_header_source_after,4)[0],0)
        self.assertEqual(unpack_from("<I",removed.original_header_source_after,8)[0],0)
        self.assertFalse(removed.original_native_queue_mutated)
        self.assertFalse(removed.original_inbox_delivery_verified)

    def test_empty_list_retains_header_and_no_event_claim(self):
        q=queue(empty=True)
        x=source_original_614080_deferred_drain_from_reached(q)
        self.assertFalse(x.original_deferred_flag_set)
        self.assertIsNone(x.original_single_node_retained)
        self.assertEqual(x.original_header_source_after,q.original_queue_header_before)

    def test_wrong_queue_owner_type_or_missing_native_branch_fails_closed(self):
        x=queue()
        malformed=bytearray(x.original_single_node_before)
        pack_into("<I",malformed,4,0x100)
        event=bytearray(x.original_event_object_bytes);pack_into("<I",event,0,0x12345678)
        header=bytearray(x.original_queue_header_before)
        pack_into("<I",header,8,0x1000)
        for bad in (
            replace(x,original_single_node_pointer=0x999),
            replace(x,original_single_node_before=bytes(malformed)),
            replace(x,original_event_object_bytes=bytes(event)),
            replace(x,original_queue_header_before=bytes(header)),
            replace(x,original_7bd564_reached_payload_virtual24_result=0),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original614080DrainSourceError):
                    source_original_614080_deferred_drain_from_reached(bad)
        x=queue(0x7bd564)
        with self.assertRaises(Original614080DrainSourceError):
            source_original_614080_deferred_drain_from_reached(replace(
                x,original_7bd564_reached_payload_virtual24_result=True))

    def test_private_original_vtable_and_deferred_drain_exact_bytes(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:self.skipTest("original EXE deliberately private")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        for vt,a,b in ((0x7d7760,0x4093e0,0x4093e0),
                       (0x7bd564,0x40dfb0,0x404610)):
            self.assertEqual(unpack_from("<I",data,vt-0x400000+4)[0],a)
            self.assertEqual(unpack_from("<I",data,vt-0x400000+24)[0],b)
        for va,hx in {
            0x613f37:"8b 43 10",0x613f40:"e8 3b 01 00 00",
            0x614085:"8b 47 0c",0x61408c:"c7 47 10 01 00 00 00",
            0x61409e:"8b 0e",0x6140a5:"ff 50 04",
            0x6140b0:"ff 52 18",0x6140c0:"83 f8 01",
            0x6140c7:"ff 52 18",0x6140d2:"ff 50 18",
            0x6140e0:"e8 ab 60 ed ff",
            0x4093e0:"b8 01 00 00 00 c3",
            0x40dfb0:"33 c0 c3",0x404610:"8b 49 08",
            0x404615:"ff 60 24",
        }.items():
            with self.subTest(va=hex(va)):
                raw=bytes.fromhex(hx)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":unittest.main()
