"""Separate native modal result byte from already-accepted TeamSelect event."""
import unittest

from original_supportstart_modal_result import (
    OriginalSupportStartModalResultError,
    source_teamselect_supportstart_modal_dispatch,
)


class OriginalSupportStartModalResultTests(unittest.TestCase):
    def test_rejected_original_parent_event_never_opens_editor(self):
        result = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=False, selected_control_bit15=True
        )
        self.assertFalse(result.modal_opened)
        self.assertFalse(result.native_apply_called)
        self.assertIsNone(result.native_modal_result_byte)
        self.assertEqual(result.outer_teamselect_handler_result, 0)

    def test_handled_unselected_event_does_not_open_editor(self):
        result = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True, selected_control_bit15=False
        )
        self.assertFalse(result.modal_opened)
        self.assertEqual(result.outer_teamselect_handler_result, 1)
        self.assertIsNone(result.native_modal_result_byte)
        self.assertFalse(result.original_editor_applied)

    def test_native_exit_does_not_apply_but_outer_event_is_handled(self):
        result = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True, selected_control_bit15=True,
            native_action_event=1
        )
        self.assertTrue(result.modal_opened)
        self.assertEqual(result.native_action_event, 1)
        self.assertEqual(result.native_modal_result_byte, 0)
        self.assertFalse(result.native_apply_called)
        self.assertFalse(result.original_editor_applied)
        self.assertEqual(result.outer_teamselect_handler_result, 1)

    def test_native_tick_invokes_apply_and_outer_handler_still_returns_one(self):
        result = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True, selected_control_bit15=True,
            native_action_event=2
        )
        self.assertTrue(result.modal_opened)
        self.assertEqual(result.native_action_event, 2)
        self.assertEqual(result.native_modal_result_byte, 1)
        self.assertTrue(result.native_apply_called)
        self.assertTrue(result.original_editor_applied)
        self.assertEqual(result.outer_teamselect_handler_result, 1)

    def test_win32_close_message_is_identical_but_editor_result_differs(self):
        canceled = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True, selected_control_bit15=True,
            native_action_event=1,
        )
        applied = source_teamselect_supportstart_modal_dispatch(
            owner_event_accepted=True, selected_control_bit15=True,
            native_action_event=2,
        )
        self.assertEqual(canceled.source_posted_close_message, (0x400, 0))
        self.assertEqual(applied.source_posted_close_message, (0x400, 0))
        self.assertEqual(canceled.source_window_loop_return, 0)
        self.assertEqual(applied.source_window_loop_return, 0)
        self.assertEqual(canceled.native_modal_result_byte, 0)
        self.assertEqual(applied.native_modal_result_byte, 1)
        self.assertFalse(canceled.native_apply_called)
        self.assertTrue(applied.native_apply_called)
        self.assertEqual(canceled.outer_teamselect_handler_result, 1)
        self.assertEqual(applied.outer_teamselect_handler_result, 1)

    def test_no_win32_modal_close_message_before_accepted_native_action(self):
        for accepted, selected in ((False, True), (True, False), (False, False)):
            projected = source_teamselect_supportstart_modal_dispatch(
                owner_event_accepted=accepted,
                selected_control_bit15=selected,
            )
            self.assertIsNone(projected.source_posted_close_message)
            self.assertIsNone(projected.source_window_loop_return)

    def test_invented_visual_or_keyboard_actions_fail_closed(self):
        for args in (
            {"owner_event_accepted": 1, "selected_control_bit15": True},
            {"owner_event_accepted": True, "selected_control_bit15": 1},
            {"owner_event_accepted": True, "selected_control_bit15": True},
            {"owner_event_accepted": True, "selected_control_bit15": True,
             "native_action_event": 0},
            {"owner_event_accepted": True, "selected_control_bit15": True,
             "native_action_event": True},
            {"owner_event_accepted": True, "selected_control_bit15": True,
             "native_action_event": 3},
            {"owner_event_accepted": False, "selected_control_bit15": True,
             "native_action_event": 1},
            {"owner_event_accepted": True, "selected_control_bit15": False,
             "native_action_event": 2},
        ):
            with self.subTest(args=args):
                with self.assertRaises(OriginalSupportStartModalResultError):
                    source_teamselect_supportstart_modal_dispatch(**args)


if __name__ == "__main__":
    unittest.main()
