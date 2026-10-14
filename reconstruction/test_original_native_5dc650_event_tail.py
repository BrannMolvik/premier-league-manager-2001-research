"""Bounded 5DC650 two-branch source record tests, not game execution."""
from unittest import TestCase,main
from struct import unpack_from
from original_native_5dc650_event_tail import (
    Original5DC650EventTailError,source_original_5dc650_reached_record_and_fifo,
)
from test_original_native_5dc510_event_tail import source

def fixture(pointer=0):
    s=source()
    return dict(
        original_edi_pointer_at_5dc672=pointer,
        original_reached_event_conversion_5e43b0_bytes=bytes(range(16)),
        original_reached_esp50_word=0x1234,
        original_reached_esp58_dword=0x11112222,
        original_reached_esp5c_dword=0x33334444,
        original_reached_esp60_dword=0x55556666,
        original_owner_pointer_at_5dc854=s['original_owner_pointer'],
        original_owner_at_5dc854=s['original_owner_at_5dc5d9'],
        original_payload_pointer_allocated=s['original_payload_pointer_allocated'],
        original_payload_20_bytes_before_stores=s['original_payload_20_bytes_before_stores'],
        original_wrapper_pointer_allocated=s['original_wrapper_pointer_allocated'],
        original_wrapper_0c_bytes_before_stores=s['original_wrapper_0c_bytes_before_stores'],
        original_old_tail_wrapper_if_nonempty=None,
        original_old_tail_pointer_if_nonempty=None,
    )

class Native5DC650ReachedTests(TestCase):
    def test_both_paths_preserve_actual_converted_bytes_and_heap_padding(self):
        for ptr,route in ((0,'edi-null-5dc7f5'),(0x30000,'edi-nonnull-5dc707')):
            with self.subTest(route=route):
                result=source_original_5dc650_reached_record_and_fifo(**fixture(ptr))
                payload=result.original_source_fifo_projection.new_native_payload_after_stores
                self.assertEqual(result.original_5dc650_path,route)
                self.assertEqual(payload[:16],bytes(range(16)))
                self.assertEqual(unpack_from('<H',payload,16)[0],0x1234)
                self.assertEqual(payload[18:20],bytes([0xca,0xca]))
                self.assertEqual([unpack_from('<I',payload,i)[0] for i in (20,24,28)],
                                 [0x11112222,0x33334444,0x55556666])
                self.assertFalse(result.original_live_world_committed)

    def test_missing_source_receipt_or_heap_pointers_fail_closed(self):
        good=fixture()
        for change in (
            {'original_edi_pointer_at_5dc672':True},
            {'original_reached_event_conversion_5e43b0_bytes':b''},
            {'original_reached_esp50_word':0x10000},
            {'original_payload_pointer_allocated':0},
            {'original_wrapper_pointer_allocated':0},
            {'original_wrapper_pointer_allocated':0x50000},
        ):
            with self.subTest(change=change):
                with self.assertRaises(Original5DC650EventTailError):
                    source_original_5dc650_reached_record_and_fifo(**(good|change))
if __name__=='__main__':main()
