"""Source-only window stack evidence tests, not Win11 input acceptance."""
import unittest
from original_window_event_stack import (
    NativeWindow, NativeWindowStackError,
    project_original_native_window_route,
)


class NativeWindowStackTests(unittest.TestCase):
    def setUp(self):
        self.base = NativeWindow(10, (0, 0, 800, 600), True)
        self.modal = NativeWindow(11, (40, 100, 800, 600), True)
        self.disabled = NativeWindow(12, (0, 0, 800, 600), False)

    def test_captured_selects_topmost_source_modal(self):
        r = project_original_native_window_route(
            (self.base, self.modal), source_point=(431,281),
            owner_capture_flag_nonzero=True)
        self.assertEqual(r.checked_vft44_indices, (1,))
        self.assertEqual(r.dispatched_indices, (1,))
        self.assertEqual(r.selected_index, 1)

    def test_captured_skips_vft44_false_owner(self):
        r = project_original_native_window_route(
            (self.base, self.modal, self.disabled), source_point=(431,281),
            owner_capture_flag_nonzero=True)
        self.assertEqual(r.checked_vft44_indices, (2,1))
        self.assertEqual(r.dispatched_indices, (1,))

    def test_captured_outside_uses_external_fallback_not_lower_window(self):
        r = project_original_native_window_route(
            (self.base, self.modal), source_point=(20,50),
            owner_capture_flag_nonzero=True)
        self.assertEqual(r.selected_index, 1)
        self.assertEqual(r.dispatched_indices, ())
        self.assertTrue(r.external_fallback_branch)

    def test_uncaptured_dispatches_all_in_bounds_in_original_order(self):
        r = project_original_native_window_route(
            (self.disabled, self.base, self.modal),
            source_point=(431,281), owner_capture_flag_nonzero=False)
        self.assertEqual(r.dispatched_indices, (0,1,2))
        self.assertEqual(r.checked_vft44_indices, ())

    def test_native_window_bounds_are_half_open(self):
        r = project_original_native_window_route(
            (self.modal,), source_point=(800,200),
            owner_capture_flag_nonzero=False)
        self.assertEqual(r.dispatched_indices, ())
        self.assertEqual(project_original_native_window_route(
            (self.modal,), source_point=(40,100),
            owner_capture_flag_nonzero=False).dispatched_indices, (0,))

    def test_uncaptured_empty_allowed_captured_empty_fails_closed(self):
        r = project_original_native_window_route(
            (), source_point=(1,1), owner_capture_flag_nonzero=False)
        self.assertEqual(r.dispatched_indices, ())
        with self.assertRaises(NativeWindowStackError):
            project_original_native_window_route(
                (self.disabled,), source_point=(1,1),
                owner_capture_flag_nonzero=True)

    def test_invalid_source_inputs_do_not_manufacture_mouse_dispatch(self):
        for bounds in ((0,0,0,10), [0,0,1,1], (True,0,1,1),
                       (0,0,1), (0,0,1,0x80000000)):
            with self.assertRaises(NativeWindowStackError):
                NativeWindow(1,bounds,True)
        for identity in (True, -1, None):
            with self.assertRaises(NativeWindowStackError):
                NativeWindow(identity,(0,0,1,1),True)
        with self.assertRaises(NativeWindowStackError):
            project_original_native_window_route(
                (self.base,self.base),source_point=(1,1),
                owner_capture_flag_nonzero=False)
        for point in ((True,0), [1,1], (1,), None):
            with self.assertRaises(NativeWindowStackError):
                project_original_native_window_route(
                    (self.base,),source_point=point,
                    owner_capture_flag_nonzero=False)
        with self.assertRaises(NativeWindowStackError):
            project_original_native_window_route(
                (self.base,),source_point=(1,1),
                owner_capture_flag_nonzero=1)


if __name__ == "__main__":
    unittest.main()
