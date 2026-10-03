import unittest
from original_fixture_report_capture import (
    NATIVE_CAPTURE_SCALAR_COPIES, copy_native_capture_scalars,
)


class NativeFixtureCaptureTests(unittest.TestCase):
    def test_direct_copy_offsets_widths_and_low_words(self):
        native = bytearray(0xFE8)
        for index, (_, offset, width) in enumerate(NATIVE_CAPTURE_SCALAR_COPIES):
            native[offset:offset + width] = bytes((index + 1,)) * width
        native[0xFE0:0xFE8] = bytes.fromhex('3412aabb7856ccdd')
        fields = copy_native_capture_scalars(bytes(native))
        self.assertEqual(tuple((f.report_offset, f.calculator_offset, len(f.value))
                               for f in fields), NATIVE_CAPTURE_SCALAR_COPIES)
        by_offset = {f.report_offset: f.value for f in fields}
        self.assertEqual(by_offset[0x98], bytes.fromhex('3412'))
        self.assertEqual(by_offset[0x9A], bytes.fromhex('7856'))
        self.assertNotIn(0x41, by_offset)  # helper-generated caption is NOT invented
        self.assertNotIn(0x84, by_offset)  # participant array is NOT zero-filled
        self.assertNotIn(0xB8, by_offset)  # variable statistics are NOT invented

    def test_truncated_or_mutable_native_memory_is_rejected(self):
        for value in (b'', bytes(0xFE5), bytearray(0xFE8), None):
            with self.assertRaises(ValueError):
                copy_native_capture_scalars(value)

    def test_scalar_projection_does_not_allocate_a_report_link(self):
        from original_fixture_match_info_link import resolve_source_match_info_link
        scalars = copy_native_capture_scalars(bytes(0xFE8))
        # The API exposes scalar copies only; it neither appends a report nor
        # supplies a native +0x40 link. No score/completion argument exists.
        self.assertEqual(len(scalars), 11)
        self.assertIsNone(resolve_source_match_info_link(0xFFFF, ()))
