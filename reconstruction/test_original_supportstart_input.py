"""Source-routine tests; no original Win11 GUI or mouse-input claim."""
import unittest

from original_supportstart_input import (
    ORIGINAL_ROW_PARENT_VTABLE, ORIGINAL_ROW_CHILD_OFFSETS,
    ORIGINAL_ROW_CHILD_VTABLES, ORIGINAL_ROW_REGISTRATION_FLAGS,
    ORIGINAL_ROW_STATE_MASK, ORIGINAL_ROW_CHILD_INPUT_FLAG,
    ORIGINAL_ROW_CHILD_STATE_FLAG, OriginalSupportStartRowBitState,
    original_supportstart_row_refresh, original_supportstart_row_native_event,
    original_supportstart_fifth_child_native_rect,
    original_supportstart_teamselect_modal_entry,
)


class OriginalSupportStartInputTests(unittest.TestCase):
    def test_native_constructor_has_five_registered_children_with_split_flags(self):
        self.assertEqual(ORIGINAL_ROW_PARENT_VTABLE, 0x7c6780)
        self.assertEqual(ORIGINAL_ROW_CHILD_OFFSETS, (0x38, 0x3c, 0x40, 0x44, 0x48))
        self.assertEqual(ORIGINAL_ROW_CHILD_VTABLES, (
            0x7be9bc, 0x7c66c8, 0x7c66c8, 0x7be530, 0x7bff14))
        self.assertEqual(ORIGINAL_ROW_REGISTRATION_FLAGS, (0x33, 0x31, 0x31, 0x15, 0x15))
        self.assertEqual(tuple(bool(f & ORIGINAL_ROW_CHILD_STATE_FLAG)
                               for f in ORIGINAL_ROW_REGISTRATION_FLAGS),
                         (True, True, True, False, False))
        self.assertEqual(tuple(bool(f & ORIGINAL_ROW_CHILD_INPUT_FLAG)
                               for f in ORIGINAL_ROW_REGISTRATION_FLAGS),
                         (False, False, False, True, True))

    def test_original_refresh_byte_zero_sets_parent_and_first_three_only(self):
        row = OriginalSupportStartRowBitState(0x24, (0x55, 0x56, 0x57, 0x58, 0x59))
        result = original_supportstart_row_refresh(row, 0)
        self.assertEqual(result.parent, 0x8024)
        self.assertEqual(result.children, (0x8055, 0x8056, 0x8057, 0x58, 0x59))
        self.assertEqual(result.stored_staff_selection_byte_if_applied, 0)
        reverse = original_supportstart_row_refresh(result, 1)
        self.assertEqual(reverse, row)
        self.assertEqual(reverse.stored_staff_selection_byte_if_applied, 1)

    def test_accepted_original_input_toggles_and_rejected_input_is_noop(self):
        row = original_supportstart_row_refresh(
            OriginalSupportStartRowBitState(0x2, (0x2, 0x2, 0x2, 0x2, 0x2)), 1
        )
        self.assertEqual(row.stored_staff_selection_byte_if_applied, 1)
        self.assertIs(original_supportstart_row_native_event(row, False), row)
        clicked = original_supportstart_row_native_event(row, True)
        self.assertEqual(clicked.parent, 0x8002)
        self.assertEqual(clicked.children, (0x8002, 0x8002, 0x8002, 0x2, 0x2))
        self.assertEqual(clicked.stored_staff_selection_byte_if_applied, 0)
        self.assertEqual(original_supportstart_row_native_event(clicked, True), row)

    def test_fifth_text_control_geometry_from_native_rectangle_setup(self):
        self.assertEqual(original_supportstart_fifth_child_native_rect(0),
                         (621, 202, 95, 15))
        self.assertEqual(original_supportstart_fifth_child_native_rect(6),
                         (621, 442, 95, 15))
        for bad in (-1, 7, None, True, 1.0):
            with self.subTest(row=bad):
                with self.assertRaises(ValueError):
                    original_supportstart_fifth_child_native_rect(bad)


    def test_teamselect_modal_requires_native_accept_and_selected_bit(self):
        self.assertFalse(original_supportstart_teamselect_modal_entry(0, False))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8000, False))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8000, True))
        self.assertTrue(original_supportstart_teamselect_modal_entry(0x8002, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8022, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8002, False))
        with self.assertRaises(TypeError):
            original_supportstart_teamselect_modal_entry(0x8000, 1)
        with self.assertRaises(ValueError):
            original_supportstart_teamselect_modal_entry(-1, True)

    def test_empty_unknown_source_flags_are_not_invented(self):
        row = OriginalSupportStartRowBitState(0, (0, 0, 0, 0, 0))
        for invalid in (None, True, -1, 256, 1.0):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    original_supportstart_row_refresh(row, invalid)

    def test_input_requires_explicit_gate_and_unsigned_native_dwords(self):
        row = OriginalSupportStartRowBitState(0, (0, 0, 0, 0, 0))
        for gate in (None, 0, 1, "clicked"):
            with self.subTest(gate=gate):
                with self.assertRaises(TypeError):
                    original_supportstart_row_native_event(row, gate)
        for bad in (True, -1, 0x100000000):
            with self.subTest(state=bad):
                with self.assertRaises(ValueError):
                    OriginalSupportStartRowBitState(bad, (0, 0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
