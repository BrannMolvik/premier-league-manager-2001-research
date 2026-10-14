"""Original native 7D7760 pending event due, nonhuman cleanup source tests."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from struct import pack_into, unpack_from
import hashlib
import os
import unittest

from original_native_418ad0_cleanup import source_original_418ad0_cleanup,Original418AD0SourceError
from original_native_7d7760_due_cleanup import (
    Original7D7760DueNonhumanReached,Original7D7760DueSourceError,
    source_original_7d7760_due_nonhuman_cleanup,
)
from original_native_60aa20_pending_event import source_original_60aa20_nonhuman_pending_from_reached
from test_original_native_60aa20_pending_event import reached as source_producer
from test_original_native_41a5b0_extra_event import manager_proof


def due(*,raw_day=110,producer_day=100,source77=60,source_status=0):
    r=source_producer(global_day=producer_day,source77=source77,first606540=10)
    output=source_original_60aa20_nonhuman_pending_from_reached(r)
    event=bytearray(20)
    pack_into("<I",event,0,0x7d7760)
    pack_into("<I",event,4,output.original_pending_event_candidate.original_due_day_raw)
    pack_into("<I",event,8,1)
    pack_into("<I",event,12,0x40000)
    event[0x10]=output.original_pending_event_candidate.original_subtype_status_5
    wrapper=bytearray(12);pack_into("<I",wrapper,0,0x30000)
    return Original7D7760DueNonhumanReached(
        original_source_producer=output,
        original_613ee0_queue_node_pointer=0x20000,
        original_613ee0_queue_node_bytes=bytes(wrapper),
        original_native_event_object_pointer=0x30000,
        original_native_event_object_bytes=bytes(event),
        original_native_player_id_allocation_pointer=0x40000,
        original_native_player_id_allocation_bytes=(123).to_bytes(4,'little'),
        original_613ee0_target_day_raw_dword=raw_day,
        original_player_before_due_handler=output.original_player_after_41a860_and_60aa20,
        original_5d7b40_4139e0_manager_proof=manager_proof(
            output.original_player_after_41a860_and_60aa20,registered=False),
    )


class Original7D7760DueCleanupTests(unittest.TestCase):
    def test_native_due_nonhuman_clears_descriptor_and_bit0(self):
        x=due()
        out=source_original_7d7760_due_nonhuman_cleanup(x)
        self.assertEqual((out.original_event_due_signed32,out.original_target_day_signed32),(107,110))
        self.assertEqual(out.original_7d7760_dispatch_handler,0x5d7b40)
        self.assertTrue(out.original_5d7b40_nonhuman_skips_notification)
        self.assertEqual(out.original_player_24c_descriptor_pointer_before,0x6000)
        self.assertTrue(out.original_418ad0_calls_686fe3_if_nonnull)
        a=x.original_player_before_due_handler
        b=out.original_player_after_source_cleanup
        self.assertEqual(unpack_from("<I",b,0x24c)[0],0)
        self.assertEqual(unpack_from("<I",b,0x14)[0],unpack_from("<I",a,0x14)[0]&~1)
        self.assertEqual(b[:0x14],a[:0x14])
        self.assertEqual(b[0x18:0x24c],a[0x18:0x24c])
        self.assertFalse(out.original_original_event_queue_mutated)
        self.assertFalse(out.original_native_event_handler_executed)
        self.assertFalse(out.original_player_heap_freed)
        self.assertFalse(out.original_notice_delivered)
        self.assertFalse(out.live_game_state_updated)

    def test_418ad0_leaf_null_pointer_still_clears_source_bit0(self):
        q=due()
        a=bytearray(q.original_player_before_due_handler)
        pack_into("<I",a,0x24c,0)
        before=bytes(a)
        out=source_original_418ad0_cleanup(player_id=123,player_before=before)
        self.assertEqual(out.original_descriptor_pointer_before,0)
        self.assertFalse(out.original_native_calls_noop_667e20_if_nonzero)
        self.assertFalse(out.original_native_requests_686fe3_free_if_nonzero)
        self.assertEqual(unpack_from("<I",out.original_player_after_source,0x14)[0]&1,0)
        self.assertFalse(out.original_heap_freed)

    def test_due_date_signed_and_future_skip(self):
        q=due(raw_day=107)
        self.assertEqual(source_original_7d7760_due_nonhuman_cleanup(q).original_target_day_signed32,107)
        with self.assertRaisesRegex(Original7D7760DueSourceError,"not-due"):
            source_original_7d7760_due_nonhuman_cleanup(replace(q,original_613ee0_target_day_raw_dword=106))
        q=due(raw_day=6,producer_day=0xfffffffe)
        self.assertEqual(source_original_7d7760_due_nonhuman_cleanup(q).original_event_due_signed32,5)
        q=due(raw_day=0xfffffffe,producer_day=100)
        with self.assertRaisesRegex(Original7D7760DueSourceError,"not-due"):
            source_original_7d7760_due_nonhuman_cleanup(q)

    def test_original_incorrect_owners_and_user_branch_fail_closed(self):
        base=due()
        event=bytearray(base.original_native_event_object_bytes)
        pack_into("<I",event,0,0x7bd564)
        wrong=bytearray(base.original_player_before_due_handler);pack_into("<H",wrong,4,999)
        wrong_payload=(456).to_bytes(4,"little")
        for bad in (
            replace(base,original_native_event_object_bytes=bytes(event)),
            replace(base,original_native_event_object_pointer=0x12345),
            replace(base,original_native_player_id_allocation_bytes=wrong_payload),
            replace(base,original_player_before_due_handler=bytes(wrong)),
            replace(base,original_5d7b40_4139e0_manager_proof=manager_proof(
                base.original_player_before_due_handler,registered=True)),
            replace(base,original_613ee0_queue_node_pointer=0),
            replace(base,original_native_player_id_allocation_bytes=b"\x7b\x00"),
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(Original7D7760DueSourceError):
                    source_original_7d7760_due_nonhuman_cleanup(bad)
        with self.assertRaises(Original418AD0SourceError):
            source_original_418ad0_cleanup(player_id=456,player_before=base.original_player_before_due_handler)

    def test_private_original_due_vtable_and_cleanup_opcodes(self):
        path=os.environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("original binary private")
        data=Path(path).read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(),
            "833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3")
        self.assertEqual(unpack_from("<I",data,0x7d7760-0x400000+16)[0],0x5d7b40)
        signatures={
            0x613ef3:"8b 73 04",
            0x613f00:"39 41 04",
            0x613f03:"7f 24",
            0x613f07:"ff 52 10",
            0x5d7b5c:"8b 46 08",
            0x5d7baa:"84 c0",
            0x5d7bac:"0f 84 19 05 00 00",
            0x5d80cb:"8b 46 0c",
            0x5d80e2:"e8 e9 09 e4 ff",
            0x418ad4:"8b be 4c 02 00 00",
            0x418adc:"74 10",
            0x418ae0:"e8 3b f3 24 00",
            0x418ae6:"e8 f8 e4 26 00",
            0x418aee:"c7 86 4c 02 00 00 00 00 00 00",
            0x418afb:"24 fe",
            0x418afe:"89 46 14",
            0x667e20:"c3",
            0x686fe3:"ff 74 24 04",
        }
        for va,hexes in signatures.items():
            with self.subTest(original_va=hex(va)):
                raw=bytes.fromhex(hexes)
                self.assertEqual(data[va-0x400000:va-0x400000+len(raw)],raw)


if __name__=="__main__":
    unittest.main()
