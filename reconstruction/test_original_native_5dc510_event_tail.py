"""Source-only 5DC510 original record, append and negative queue tests."""
from hashlib import sha256
from os import environ
from pathlib import Path
from struct import pack_into,unpack_from
from unittest import TestCase,main

from original_native_5dc510_event_tail import (
    Original5DC510EventTailError,source_original_5dc510_record_tail_append,
)


def source(empty=True):
    owner=bytearray(0x14)
    if not empty:
        pack_into("<II",owner,4,0x70000,0x70000)
    record=bytes([0xCA]*32)
    wrapper=bytes([0xDC]*12)
    args=bytearray(0x24)
    for offset,value in ((0,11),(4,22),(8,33),(12,44),
                         (16,55),(20,66),(24,77),(28,88),(32,99)):
        pack_into("<I",args,offset,value)
    return dict(
        original_owner_pointer=0x40000,
        original_owner_at_5dc5d9=bytes(owner),
        original_payload_pointer_allocated=0x50000,
        original_payload_20_bytes_before_stores=record,
        original_wrapper_pointer_allocated=0x60000,
        original_wrapper_0c_bytes_before_stores=wrapper,
        original_original_args_ebp8_to_ebp28=bytes(args),
        original_old_tail_wrapper_if_nonempty=(bytes(12) if not empty else None),
        original_old_tail_pointer_if_nonempty=(0x70000 if not empty else None),
    )


def dw(record,offset):
    return unpack_from("<I",record,offset)[0]


class SourceOriginal5DC510EventTailTests(TestCase):
    def test_native_empty_fifo_appends_allocated_payload_and_keeps_heap_padding(self):
        inputs=source()
        result=source_original_5dc510_record_tail_append(**inputs)
        self.assertEqual((dw(result.owner_after_append,4),dw(result.owner_after_append,8)),
                         (0x60000,0x60000))
        self.assertEqual(tuple(dw(result.new_native_payload_after_stores,n)
                               for n in (0,4,8,12,20,24,28)),
                         (11,22,33,44,66,77,88))
        self.assertEqual(unpack_from("<H",result.new_native_payload_after_stores,16)[0],55)
        self.assertEqual(result.new_native_payload_after_stores[18:20],b"\xca\xca")
        self.assertEqual(tuple(dw(result.new_native_wrapper_after_append,n)
                               for n in (0,4,8)),(0x50000,0,0))
        self.assertFalse(result.original_live_queue_mutated)
        self.assertFalse(result.original_native_allocation_executed)
        self.assertFalse(result.original_5dc650_executed)
        self.assertEqual(inputs["original_payload_20_bytes_before_stores"],bytes([0xca]*32))

    def test_nonempty_original_fifo_keeps_head_and_updates_previous_tail_next(self):
        inputs=source(empty=False)
        previous=bytearray(inputs["original_old_tail_wrapper_if_nonempty"])
        pack_into("<I",previous,0,0x80000)
        inputs["original_old_tail_wrapper_if_nonempty"]=bytes(previous)
        result=source_original_5dc510_record_tail_append(**inputs)
        self.assertEqual((dw(result.owner_after_append,4),dw(result.owner_after_append,8)),
                         (0x70000,0x60000))
        self.assertEqual(dw(result.old_tail_after_append_if_reached,4),0x60000)
        self.assertEqual(dw(result.new_native_wrapper_after_append,8),0x70000)

    def test_missing_allocation_partial_chain_or_wrong_owner_pointer_fail_closed(self):
        inputs=source()
        cases=(
            {"original_payload_pointer_allocated":0},
            {"original_wrapper_pointer_allocated":0},
            {"original_wrapper_pointer_allocated":0x50000},
            {"original_owner_at_5dc5d9":b""},
            {"original_payload_20_bytes_before_stores":b""},
            {"original_wrapper_0c_bytes_before_stores":b""},
            {"original_original_args_ebp8_to_ebp28":b""},
            {"original_old_tail_wrapper_if_nonempty":bytes(12)},
            {"original_old_tail_pointer_if_nonempty":0x70000},
        )
        for change in cases:
            with self.subTest(change=change):
                with self.assertRaises(Original5DC510EventTailError):
                    source_original_5dc510_record_tail_append(**(inputs|change))
        nonempty=source(empty=False)
        with self.assertRaisesRegex(Original5DC510EventTailError,"identity drift"):
            source_original_5dc510_record_tail_append(**(nonempty|{
                "original_old_tail_pointer_if_nonempty":0x90000}))
        previous=bytearray(12)
        pack_into("<I",previous,4,0x12345)
        with self.assertRaisesRegex(Original5DC510EventTailError,"terminal"):
            source_original_5dc510_record_tail_append(**(nonempty|{
                "original_old_tail_wrapper_if_nonempty":bytes(previous)}))

    def test_optional_exact_original_pe_malloc_fields_fifo_opcodes(self):
        path=environ.get("FM2001_ORIGINAL_EXE")
        if not path:
            self.skipTest("proprietary original executable intentionally omitted from CI")
        exe=Path(path).read_bytes()
        self.assertEqual((len(exe),sha256(exe).hexdigest()),(
            4714541,"833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3"))
        sites={
            0x5dc5d9:"6a 20",0x5dc5db:"e8 60 bb 08 00",
            0x5dc5e3:"85 c0",0x5dc5e5:"74 42",0x5dc5f9:"89 0b",
            0x5dc5ff:"89 53 04",0x5dc606:"66 89 50 10",
            0x5dc60d:"89 7b 08",0x5dc612:"89 4b 0c",
            0x5dc618:"89 50 14",0x5dc61e:"89 51 04",
            0x5dc624:"89 51 08",0x5dc62b:"6a 0c",
            0x5dc634:"89 38",0x5dc63a:"e8 31 b7 03 00",
            0x617d70:"8b 51 08",0x617d7b:"89 42 04",
            0x617d7e:"c7 40 04 00 00 00 00",
            0x617d8b:"89 41 08",0x617d91:"89 41 08",
            0x617d94:"89 41 04",0x617d9e:"c7 40 08 00 00 00 00",
        }
        for address,payload in sites.items():
            with self.subTest(original_va=hex(address)):
                sig=bytes.fromhex(payload)
                self.assertEqual(exe[address-0x400000:address-0x400000+len(sig)],sig)


if __name__=="__main__":
    main()
