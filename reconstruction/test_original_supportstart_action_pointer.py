"""Original SupportStart input-to-transaction boundary, not Windows GUI acceptance."""
import unittest

from original_human_user_name import OriginalHumanUserName
from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_staff_lists import OriginalSupportStartLinkedLists
from original_supportstart_pointer_candidate import project_source_supportstart_pointer_candidate
from original_supportstart_action_pointer import (
    OriginalSupportStartActionPointerError,
    project_original_supportstart_action_pointer_down,
)
from original_window_event_stack import NativeWindow
from support_staff import SupportStaffState, original_teamselect_support_slots


class SupportStartActionPointerTests(unittest.TestCase):
    def setUp(self):
        staff = tuple(
            SupportStaffState(code, 32 + i, 3)
            for i, code in enumerate((1, 2, 3, 4, 5, 13))
        )
        self.editor = OriginalSupportStartEditorProjection.open_initial_first_human_modal(
            original_user=OriginalHumanUserName(1, 0, "Old", "Manager"),
            source_slots=original_teamselect_support_slots(staff),
            before_native_staging=OriginalSupportStartLinkedLists(
                current_staff=staff, global_staff=staff,
            ),
        )
        self.windows = (
            NativeWindow(10, (0, 0, 800, 600), True),
            NativeWindow(99, (40, 100, 800, 600), True),
        )

    @staticmethod
    def point(x, y):
        return (y << 16) | x

    def candidate(self, x, y, **overrides):
        args = dict(
            win32_message=0x201,
            packed_lparam=self.point(x, y),
            original_guard_nonzero=False,
            source_windows=self.windows,
            source_modal_window_identity=99,
            owner_capture_flag_nonzero=True,
            actual_viewport_size=(800, 600),
            post_window_parent_callback_state_qualified=True,
        )
        args.update(overrides)
        return project_source_supportstart_pointer_candidate(self.editor, **args)

    def click(self, x, y, **overrides):
        args = dict(
            editor=self.editor,
            candidate=self.candidate(x, y),
            source_windows=self.windows,
            modal_window_identity=99,
            viewport_size=(800, 600),
            action_control_dwords=(0x183, 0x183),
            teamselect_owner_event_accepted=True,
            teamselect_selected_control_bit15=True,
        )
        args.update(overrides)
        return project_original_supportstart_action_pointer_down(**args)

    def test_native_exit_is_immediate_mouse_down_cancel_with_no_apply(self):
        result = self.click(769, 101)
        self.assertEqual(result.native_event, 1)
        self.assertEqual(result.source_button_owner_offset, 0x1EB8)
        self.assertEqual(result.source_button_state_after_press, 0x197)
        self.assertEqual(result.editor_close.source_modal_result, 0)
        self.assertFalse(result.editor_close.invoked_original_apply)
        self.assertEqual(result.editor_close.original_human_user_name,
                         self.editor.original_user)
        self.assertEqual(result.editor_close.staff_lists, self.editor.prior_staff_lists)
        self.assertEqual(result.modal_dispatch.native_modal_result_byte, 0)
        self.assertEqual(result.modal_dispatch.source_posted_close_message, (0x400, 0))
        self.assertEqual(result.modal_dispatch.source_window_loop_return, 0)
        self.assertEqual(result.modal_dispatch.outer_teamselect_handler_result, 1)

    def test_native_tick_applies_full_editor_state_on_mouse_down(self):
        edited = self.editor.with_edited_name("Jane", "Doe")
        expected = edited.close(2)
        result = self.click(737, 101, editor=edited)
        self.assertEqual(result.native_event, 2)
        self.assertEqual(result.source_button_owner_offset, 0x1F08)
        self.assertEqual(result.source_button_state_after_press, 0x197)
        self.assertEqual(result.editor_close, expected)
        self.assertTrue(result.editor_close.invoked_original_apply)
        self.assertEqual(result.editor_close.original_human_user_name.first_name, "Jane")
        self.assertEqual(result.editor_close.original_human_user_name.surname, "Doe")
        self.assertTrue(result.modal_dispatch.native_apply_called)
        self.assertEqual(result.modal_dispatch.native_modal_result_byte, 1)
        self.assertEqual(result.modal_dispatch.source_posted_close_message, (0x400, 0))
        self.assertEqual(result.modal_dispatch.outer_teamselect_handler_result, 1)

    def test_half_open_original_button_rectangles_and_gap(self):
        self.assertEqual(self.click(766, 130).native_event, 2)
        self.assertEqual(self.click(798, 130).native_event, 1)
        for x, y in ((736, 101), (737, 100), (737, 131),
                     (767, 101), (768, 101), (400, 150)):
            with self.subTest(point=(x, y)):
                self.assertIsNone(self.click(x, y))

    def test_pressed_hidden_disabled_buttons_cannot_apply_or_cancel(self):
        for flags in (0x181, 0x182, 0x193, 0x180, 0, 0x8001):
            with self.subTest(flags=flags):
                self.assertIsNone(self.click(737, 101,
                                             action_control_dwords=(0x183, flags)))
                self.assertIsNone(self.click(769, 101,
                                             action_control_dwords=(flags, 0x183)))

    def test_valid_win32_double_click_has_same_action_owner(self):
        c = self.candidate(737, 101, win32_message=0x203)
        result = self.click(737, 101, candidate=c)
        self.assertEqual(result.native_event, 2)

    def test_row_input_is_never_confused_with_close_action(self):
        row = self.candidate(500, 300)
        self.assertEqual(row.source_candidate_row_indices, (0,))
        with self.assertRaisesRegex(OriginalSupportStartActionPointerError,
                                    "unclaimed"):
            self.click(737, 101, candidate=row)

    def test_reject_unknown_window_capture_registration_and_modal_entry(self):
        candidate = self.candidate(737, 101)
        for changes in (
            dict(source_windows=self.windows[:-1]),
            dict(modal_window_identity=10),
            dict(viewport_size=(900, 700)),
            dict(source_windows=tuple(reversed(self.windows))),
            dict(teamselect_owner_event_accepted=False),
            dict(teamselect_selected_control_bit15=False),
        ):
            with self.subTest(changes=changes), self.assertRaises(
                    OriginalSupportStartActionPointerError):
                self.click(737, 101, candidate=candidate, **changes)
        not_captured = self.candidate(737, 101,
                                      owner_capture_flag_nonzero=False)
        with self.assertRaises(OriginalSupportStartActionPointerError):
            self.click(737, 101, candidate=not_captured)
        outside = self.candidate(20, 50)
        with self.assertRaises(OriginalSupportStartActionPointerError):
            self.click(737, 101, candidate=outside)

    def test_malformed_or_invented_button_state_fails_closed(self):
        for control_states in (
            None, (), (0x183,), (0x183, 0x183, 0x183),
            (0x183, True), (0x183, None), (-1, 0x183),
            (0x183, 0x100000000), [0x183, 0x183],
        ):
            with self.subTest(states=control_states), self.assertRaises(
                    OriginalSupportStartActionPointerError):
                self.click(737, 101, action_control_dwords=control_states)
        for owner, selected in ((1, True), (True, 1), (None, True)):
            with self.subTest(flags=(owner, selected)), self.assertRaises(
                    OriginalSupportStartActionPointerError):
                self.click(
                    737, 101, teamselect_owner_event_accepted=owner,
                    teamselect_selected_control_bit15=selected,
                )


if __name__ == "__main__":
    unittest.main()
