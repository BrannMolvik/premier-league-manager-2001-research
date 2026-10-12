"""Win32 candidate + independent original row callback receipt; no live GUI."""
import unittest
from dataclasses import replace

from original_human_user_name import OriginalHumanUserName
from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_input import project_original_supportstart_row_native_dispatch
from original_supportstart_pointer_candidate import (
    project_source_supportstart_pointer_candidate,
)
from original_supportstart_pointer_observation import (
    OriginalSupportStartPointerObservationError,
    project_original_supportstart_observed_pointer_row_input,
)
from original_supportstart_staff_lists import OriginalSupportStartLinkedLists
from original_window_event_stack import NativeWindow
from support_staff import SupportStaffState, original_teamselect_support_slots


class OriginalSupportStartPointerObservationTests(unittest.TestCase):
    def setUp(self):
        self.staff = tuple(
            SupportStaffState(n, 32 + i, 3)
            for i, n in enumerate((1, 2, 3, 4, 5, 13))
        )
        self.editor = OriginalSupportStartEditorProjection.open_initial_first_human_modal(
            original_user=OriginalHumanUserName(1, 0, "Old", "Manager"),
            source_slots=original_teamselect_support_slots(self.staff),
            before_native_staging=OriginalSupportStartLinkedLists(
                current_staff=self.staff, global_staff=self.staff,
            ),
        )
        self.windows = (
            NativeWindow(10, (0, 0, 800, 600), True),
            NativeWindow(99, (40, 100, 800, 600), True),
        )

    def candidate(self, x=500, y=300, **kwargs):
        args = dict(
            win32_message=0x201, packed_lparam=(y << 16) | x,
            original_guard_nonzero=False,
            source_windows=self.windows,
            source_modal_window_identity=99,
            owner_capture_flag_nonzero=True,
            actual_viewport_size=(800, 600),
            post_window_parent_callback_state_qualified=True,
        )
        args.update(kwargs)
        return project_source_supportstart_pointer_candidate(
            self.editor, **args
        )

    def observe(self, index=0, accepted=True, editor=None):
        ed = self.editor if editor is None else editor
        return project_original_supportstart_row_native_dispatch(
            ed.rows[index], native_second_argument_present=True,
            observed_parent_acceptance=accepted,
            observed_child_acceptances=(False, False) if accepted else (),
            source_row_index=index,
        )

    def test_true_native_row0_observation_can_stage_selection_then_apply(self):
        candidate = self.candidate()
        self.assertFalse(candidate.native_row_event_accepted)
        receipt = project_original_supportstart_observed_pointer_row_input(
            self.editor,
            original_window_candidate=candidate,
            observed_native_input=self.observe(),
        )
        self.assertTrue(receipt.native_row_input_accepted)
        self.assertEqual((receipt.source_row_index, receipt.native_event_id), (0, 8))
        self.assertEqual(receipt.editor_after_observed_input.rows[0].parent, 0x8193)
        self.assertEqual(self.editor.rows[0].parent, 0x183)
        # No staff move until separate native event2 Apply source projection.
        self.assertEqual(receipt.editor_after_observed_input.prior_staff_lists.current_staff, ())
        accepted = receipt.editor_after_observed_input.close(2)
        self.assertEqual(accepted.staff_lists.current_staff, (self.staff[0],))
        self.assertEqual(accepted.original_record_flag_bytes[0], 0)

    def test_original_rejected_row_input_is_non_mutating(self):
        receipt = project_original_supportstart_observed_pointer_row_input(
            self.editor, original_window_candidate=self.candidate(),
            observed_native_input=self.observe(accepted=False),
        )
        self.assertFalse(receipt.native_row_input_accepted)
        self.assertIs(receipt.editor_after_observed_input, self.editor)

    def test_candidate_never_establishes_native_input_by_itself(self):
        with self.assertRaises(TypeError):
            project_original_supportstart_observed_pointer_row_input(
                self.editor, original_window_candidate=self.candidate(),
                observed_native_input=None,
            )
        with self.assertRaises(OriginalSupportStartPointerObservationError):
            project_original_supportstart_observed_pointer_row_input(
                self.editor, original_window_candidate=self.candidate(750, 320),
                observed_native_input=self.observe(),
            )

    def test_stale_and_wrong_source_selector_observations_fail_closed(self):
        with self.assertRaises(OriginalSupportStartPointerObservationError):
            project_original_supportstart_observed_pointer_row_input(
                self.editor,
                original_window_candidate=self.candidate(),
                observed_native_input=self.observe(index=1),
            )
        first = project_original_supportstart_observed_pointer_row_input(
            self.editor,
            original_window_candidate=self.candidate(),
            observed_native_input=self.observe(),
        )
        with self.assertRaises(OriginalSupportStartPointerObservationError):
            project_original_supportstart_observed_pointer_row_input(
                first.editor_after_observed_input,
                original_window_candidate=self.candidate(),
                observed_native_input=self.observe(),
            )

    def test_disabled_seventh_staff_row_may_dispatch_but_cannot_accept(self):
        candidate = self.candidate(500, 540)
        self.assertEqual(candidate.source_candidate_row_indices, (6,))
        denied = self.observe(index=6, accepted=False)
        receipt = project_original_supportstart_observed_pointer_row_input(
            self.editor, original_window_candidate=candidate,
            observed_native_input=denied,
        )
        self.assertFalse(receipt.native_row_input_accepted)
        self.assertIs(receipt.editor_after_observed_input, self.editor)

    def test_source_callback_id_cannot_be_swapped_for_apply_or_cancel(self):
        candidate = self.candidate()
        for wrong in ((1,), (2,), (9,), ()):
            with self.subTest(event=wrong):
                with self.assertRaises(OriginalSupportStartPointerObservationError):
                    project_original_supportstart_observed_pointer_row_input(
                        self.editor,
                        original_window_candidate=replace(
                            candidate,
                            source_candidate_native_control_ids=wrong,
                        ),
                        observed_native_input=self.observe(),
                    )

    def test_never_conflates_nonmodal_windows_or_fabricated_acceptance(self):
        other = self.candidate(20, 50)
        with self.assertRaises(OriginalSupportStartPointerObservationError):
            project_original_supportstart_observed_pointer_row_input(
                self.editor,
                original_window_candidate=other,
                observed_native_input=self.observe(),
            )
        with self.assertRaises(OriginalSupportStartPointerObservationError):
            project_original_supportstart_observed_pointer_row_input(
                self.editor,
                original_window_candidate=replace(
                    self.candidate(), native_row_event_accepted=True,
                ),
                observed_native_input=self.observe(),
            )


if __name__ == "__main__":
    unittest.main()
