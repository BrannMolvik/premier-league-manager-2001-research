import unittest
from original_fixture_report_capture import (
    NATIVE_CAPTURE_SCALAR_COPIES, capture_gate_report_scalars, copy_native_capture_scalars,
    NATIVE_CAPTURE_HELPER_SCALAR_COPIES, copy_native_capture_helper_scalars,
    copy_native_capture_possession,
    capture_completed_possession_rows,
)


class NativeFixtureCaptureTests(unittest.TestCase):
    def test_gate_scalar_fragment_uses_retained_d84_d88_d8c_d90_only(self):
        from gate_receipts import GateAttendanceCell, GateReceiptResult

        receipt = GateReceiptResult(
            home_seating=GateAttendanceCell(0.0, 1.0, 1, 900),
            visiting_seating=GateAttendanceCell(0.0, 1.0, 1, 250),
            home_terrace=GateAttendanceCell(0.0, 1.0, 1, 700),
            visiting_terrace=GateAttendanceCell(0.0, 1.0, 1, 150),
            home_revenue=0,
            visiting_revenue=0,
            season_ticket_quantity=80,
            report_seating_price=37,
        )

        scalars = capture_gate_report_scalars(receipt)

        self.assertEqual(
            tuple((item.report_offset, item.calculator_offset) for item in scalars),
            ((0x30, 0xD84), (0x34, 0xD88), (0x38, 0xD8C), (0x3C, 0xD90)),
        )
        self.assertEqual(
            tuple(int.from_bytes(item.value, "little") for item in scalars),
            (2080, 37, 1680, 400),
        )
        self.assertNotIn(0xD9C, tuple(item.calculator_offset for item in scalars))

    def test_gate_scalar_fragment_fails_closed_without_retained_d88(self):
        from gate_receipts import GateAttendanceCell, GateReceiptResult

        cell = GateAttendanceCell(0.0, 1.0, 1, 1)
        with self.assertRaisesRegex(ValueError, "D88"):
            capture_gate_report_scalars(
                GateReceiptResult(cell, cell, cell, cell, 0, 0)
            )

    def test_live_calendar_and_accumulators_are_explicit_not_semantic_scores(self):
        from datetime import date
        from original_fixture_report_capture import LiveReportCompletionScalars
        output = LiveReportCompletionScalars.from_calculation(date(2000, 2, 29), (17, 34))
        self.assertEqual(output.calendar, (100, 2, 29))
        self.assertEqual(output.scores, (17, 34))
        self.assertEqual(output.native_score_nibbles, 0x21)
        self.assertEqual(LiveReportCompletionScalars.from_calculation(date(1904, 1, 1), (0, 0)).calendar,
                         (4, 1, 1))
        self.assertEqual(LiveReportCompletionScalars.from_calculation(date(2100, 3, 1), (0, 0)).calendar,
                         (200, 2, 29))
        for calendar, scores in (((100, 2, 30), (0, 0)), ((8100, 1, 1), (0, 0)),
                                 ((100, True, 1), (0, 0)), ((100, 1, 1), (-1, 0)),
                                 ((100, 1, 1), (True, 0)), ((100, 1, 1), [0, 0])):
            with self.assertRaises(ValueError):
                LiveReportCompletionScalars(calendar, scores)

    def test_live_rows_match_calibrated_snapshot_projection_for_normal_and_extra(self):
        minutes = tuple(range(5, 45, 5)) + tuple(range(50, 90, 5))
        for extra in (False, True):
            selected = minutes + ((95, 100, 110, 115) if extra else ())
            rows = tuple((minute, bytes((10 + i, 30 + i, 5)))
                         for i, minute in enumerate(selected))
            native = bytearray(0x112C)
            native[0xFF8:0xFFC] = (24 if extra else 18).to_bytes(4, 'little')
            for minute, triplet in rows:
                for component, base in enumerate((0x100C, 0x106C, 0x10CC)):
                    offset = base + (minute // 5) * 4
                    native[offset:offset + 4] = triplet[component].to_bytes(4, 'little')
            self.assertEqual(capture_completed_possession_rows(rows),
                             copy_native_capture_possession(bytes(native)))

    def test_live_rows_reject_partial_reordered_duplicate_or_boundary_data(self):
        minutes = tuple(range(5, 45, 5)) + tuple(range(50, 90, 5))
        rows = tuple((minute, bytes((10, 30, 5))) for minute in minutes)
        for invalid in ((), rows[:-1], rows[::-1], rows + rows[:1],
                        ((0, bytes(3)),) + rows, list(rows),
                        ((5, bytearray(3)),) + rows[1:]):
            with self.assertRaises(ValueError):
                capture_completed_possession_rows(invalid)

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

    def test_resolved_helper_fields_are_exact_copies_not_default_values(self):
        native = bytearray(0x1158)
        for index, (_, offset, width) in enumerate(NATIVE_CAPTURE_HELPER_SCALAR_COPIES):
            native[offset:offset + width] = (0xABC001 + index).to_bytes(width, 'little')
        copies = copy_native_capture_helper_scalars(bytes(native))
        self.assertEqual(tuple((c.report_offset, c.calculator_offset, len(c.value))
                               for c in copies), NATIVE_CAPTURE_HELPER_SCALAR_COPIES)
        self.assertEqual(tuple(int.from_bytes(c.value, 'little') for c in copies),
                         tuple(0xABC001 + index for index in range(4)))
        for invalid in (None, bytes(0x1157), bytearray(0x1158)):
            with self.assertRaises(ValueError):
                copy_native_capture_helper_scalars(invalid)

    def test_report_possession_uses_two_or_four_groups_not_segment_count(self):
        native = bytearray(0x1158)
        groups = ((1, 8), (10, 8), (19, 2), (22, 2))
        for base, initial in ((0x100C, 10), (0x106C, 20), (0x10CC, 30)):
            # Poison excluded boundary entries so including them is visible.
            for index in (0, 9, 18, 21):
                native[base + 4 * index:base + 4 * index + 4] = (999).to_bytes(4, 'little')
            for group, (start, length) in enumerate(groups):
                for index in range(start, start + length):
                    native[base + 4 * index:base + 4 * index + 4] = (
                        initial + 10 * group).to_bytes(4, 'little')
        native[0xFF8:0xFFC] = (18).to_bytes(4, 'little')
        ordinary = copy_native_capture_possession(bytes(native))
        self.assertEqual(ordinary.triplets, bytes((10, 20, 30, 20, 30, 40)))
        self.assertEqual(ordinary.averages, bytes((25, 35, 40)))
        for count in (0, 24, 0xFFFFFFFF):
            native[0xFF8:0xFFC] = count.to_bytes(4, 'little')
            extra = copy_native_capture_possession(bytes(native))
            self.assertEqual(extra.triplets,
                             bytes((10, 20, 30, 20, 30, 40, 30, 40, 50, 40, 50, 60)))
            self.assertEqual(extra.averages, bytes((35, 45, 20)))

    def test_possession_preserves_dword_wrap_byte_truncation_and_remainder(self):
        native = bytearray(0x112C)
        native[0xFF8:0xFFC] = (18).to_bytes(4, 'little')
        for base in (0x100C, 0x106C, 0x10CC):
            for start in (1, 10):
                for index in range(start, start + 8):
                    native[base + index * 4:base + index * 4 + 4] = b'\xff' * 4
        result = copy_native_capture_possession(bytes(native))
        self.assertEqual(result.triplets, b'\xff' * 6)
        self.assertEqual(result.averages, bytes((255, 255, 102)))
        for invalid in (None, bytes(0x112B), bytearray(0x112C)):
            with self.assertRaises(ValueError):
                copy_native_capture_possession(invalid)
