"""Pure display-snapshot checks: never launch or manipulate any window."""
import copy
import unittest

from gate13_native_display_watch import DisplayWatch, DisplayWatchError, compare_desktop, has_normal_probe_window


def snapshot():
    return dict(displays=[dict(width=3440, height=1440, bits=32)], foreground_pid=10,
                windows=[dict(hwnd=1, pid=10, rect=[10, 10, 100, 100], caption=True,
                              topmost=False, mouse_capture=False)])


class DisplayWatchTests(unittest.TestCase):
    def test_failure_snapshot_survives_final_post_termination_sample(self):
        watch = DisplayWatch.__new__(DisplayWatch)
        watch.baseline, watch.last = snapshot(), snapshot()
        watch.samples, watch.window_samples = 0, 0
        watch.first_window_time, watch.failure_snapshot = None, None
        watch.problems = []
        failed, final = snapshot(), snapshot()
        failed['foreground_pid'] = 20
        watch.snapshot = lambda pid: failed
        with self.assertRaises(DisplayWatchError):
            watch.check(20)
        watch.snapshot = lambda pid: final
        with self.assertRaises(DisplayWatchError):
            watch.check(20)
        self.assertEqual(watch.receipt()['failure_snapshot'], failed)
        self.assertEqual(watch.receipt()['final'], final)
        self.assertFalse(watch.ready())

    def test_unchanged_desktop_is_not_proof_of_a_game_window(self):
        before = snapshot()
        self.assertEqual(compare_desktop(before, before, 20), [])
        self.assertFalse(has_normal_probe_window(before, 20))

    def test_resolution_and_unrelated_geometry_changes_fail_closed(self):
        for kind in ('resolution', 'geometry'):
            before, after = snapshot(), snapshot()
            if kind == 'resolution':
                after['displays'][0]['width'] = 800
            else:
                after['windows'][0]['rect'][0] = 0
            self.assertTrue(compare_desktop(before, after, 20))

    def test_no_topmost_capture_or_foreground(self):
        before = snapshot()
        for key in ('topmost', 'mouse_capture', 'foreground'):
            after = copy.deepcopy(before)
            window = dict(hwnd=2, pid=20, rect=[0, 0, 800, 600], caption=True,
                          topmost=False, mouse_capture=False)
            after['windows'].append(window)
            if key == 'foreground':
                after['foreground_pid'] = 20
            else:
                window[key] = True
            self.assertTrue(compare_desktop(before, after, 20))

    def test_focus_takeover_fails_even_without_probe_foreground_owner(self):
        before, after = snapshot(), snapshot()
        after['focus_pid'] = 20
        self.assertEqual(compare_desktop(before, after, 20), ['probe_took_focus'])

    def test_captioned_normal_window_required(self):
        after = snapshot()
        window = dict(hwnd=2, pid=20, rect=[0, 0, 800, 600], caption=True,
                      topmost=False, mouse_capture=False)
        after['windows'].append(window)
        self.assertTrue(has_normal_probe_window(after, 20))
        window['caption'] = False
        self.assertFalse(has_normal_probe_window(after, 20))


if __name__ == '__main__':
    unittest.main()
