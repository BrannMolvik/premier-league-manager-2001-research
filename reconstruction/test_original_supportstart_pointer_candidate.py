"""Source-only WM mouse-to-row dispatch prefilter; no GUI acceptance."""
import unittest
from original_human_user_name import OriginalHumanUserName
from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_staff_lists import OriginalSupportStartLinkedLists
from support_staff import SupportStaffState, original_teamselect_support_slots
from original_window_event_stack import NativeWindow
from original_supportstart_pointer_candidate import (
    SourceSupportStartPointerCandidateError,
    project_source_supportstart_pointer_candidate,
)


class SourceSupportStartPointerCandidateTests(unittest.TestCase):
    def setUp(self):
        staff=tuple(SupportStaffState(n,32+i,3) for i,n in enumerate(
            (1,2,3,4,5,13)
        ))
        self.editor=OriginalSupportStartEditorProjection.open_initial_first_human_modal(
            original_user=OriginalHumanUserName(1,0,"Old","Manager"),
            source_slots=original_teamselect_support_slots(staff),
            before_native_staging=OriginalSupportStartLinkedLists(
                current_staff=staff,global_staff=staff,
            ),
        )
        self.modal=NativeWindow(99,(40,100,800,600),True)
        self.background=NativeWindow(10,(0,0,800,600),True)

    def _point(self,x,y):
        return (y<<16)|x

    def _call(self,point,**overrides):
        values=dict(
            win32_message=0x201,packed_lparam=point,
            original_guard_nonzero=False,
            source_windows=(self.background,self.modal),
            source_modal_window_identity=99,
            owner_capture_flag_nonzero=True,
            actual_viewport_size=(800,600),
            post_window_parent_callback_state_qualified=True,
        )
        values.update(overrides)
        return project_source_supportstart_pointer_candidate(
            self.editor,**values
        )

    def test_original_row0_candidate_matches_win32_pixel_and_native_id8(self):
        r=self._call(self._point(431,281))
        self.assertEqual(r.original_native_client_point,(431,281))
        self.assertTrue(r.source_modal_window_reached)
        self.assertEqual(r.source_candidate_row_indices,(0,))
        self.assertEqual(r.source_candidate_native_control_ids,(8,))
        self.assertFalse(r.native_row_event_accepted)

    def test_row5_and_empty_row6_can_be_dispatched_but_not_assumed_accepted(self):
        a=self._call(self._point(500,490))
        self.assertEqual(a.source_candidate_row_indices,(5,))
        self.assertEqual(a.source_candidate_native_control_ids,(13,))
        blank=self._call(self._point(500,540))
        self.assertEqual(blank.source_candidate_row_indices,(6,))
        self.assertEqual(blank.source_candidate_native_control_ids,(14,))
        self.assertFalse(blank.native_row_event_accepted)

    def test_half_open_boundaries_and_other_modal_buttons_not_staff_rows(self):
        self.assertEqual(self._call(self._point(757,281)).source_candidate_row_indices,())
        self.assertEqual(self._call(self._point(431,318)).source_candidate_row_indices,())
        self.assertEqual(self._call(self._point(500,300)).source_candidate_row_indices,(0,))
        self.assertEqual(self._call(self._point(737,101)).source_candidate_row_indices,())

    def test_guard_or_external_captured_route_no_row_candidate(self):
        guarded=self._call(self._point(500,300),original_guard_nonzero=True)
        self.assertFalse(guarded.source_modal_window_reached)
        self.assertEqual(guarded.source_candidate_row_indices,())
        fallback=self._call(self._point(20,50))
        self.assertFalse(fallback.source_modal_window_reached)
        self.assertTrue(fallback.original_window_route.external_fallback_branch)

    def test_noncaptured_path_does_not_invent_input_of_other_windows(self):
        r=self._call(self._point(500,300),owner_capture_flag_nonzero=False)
        self.assertEqual(r.original_window_route.dispatched_indices,(0,1))
        self.assertEqual(r.source_candidate_row_indices,(0,))
        self.assertFalse(r.native_row_event_accepted)

    def test_unknown_parent_callback_result_fails_closed(self):
        with self.assertRaisesRegex(SourceSupportStartPointerCandidateError,"prechild"):
            self._call(
                self._point(500,300),
                post_window_parent_callback_state_qualified=False,
            )

    def test_modal_pointer_or_viewport_mismatch_fails_closed(self):
        for changes in (
            dict(source_modal_window_identity=100),
            dict(actual_viewport_size=(900,700)),
            dict(source_windows=(self.background,)),
            dict(source_windows=(self.background,NativeWindow(99,(40,100,800,600),False))),
        ):
            with self.subTest(changes=changes), self.assertRaises(
                SourceSupportStartPointerCandidateError
            ):
                self._call(self._point(500,300),**changes)

    def test_original_mouse_up_cannot_be_forged_as_down_row_candidate(self):
        for message in (0x202,0x200,None,True):
            with self.subTest(message=message),self.assertRaises(
                SourceSupportStartPointerCandidateError
            ):
                self._call(self._point(500,300),win32_message=message)
        with self.assertRaises(SourceSupportStartPointerCandidateError):
            self._call(self._point(500,300),source_modal_window_identity=True)
        with self.assertRaises(SourceSupportStartPointerCandidateError):
            self._call(self._point(500,300),post_window_parent_callback_state_qualified=1)


if __name__ == "__main__":
    unittest.main()
