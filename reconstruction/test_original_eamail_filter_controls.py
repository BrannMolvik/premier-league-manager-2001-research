"""Native-source Inbox filter control contract; no GUI/input acceptance."""
import unittest
from original_eamail_filter_controls import (
    NATIVE_FILTER_COUNT,
    NATIVE_FILTER_FIRST_OWNER_OFFSET,
    NATIVE_FILTER_OWNER_STRIDE,
    NATIVE_FILTER_RADIO_WRAPPER,
    original_eamail_filter_controls,
    original_eamail_filter_native_window_candidate,
)


class OriginalEAMailFilterControlTests(unittest.TestCase):
    def test_original_ten_control_owners_labels_children_and_local_bounds(self):
        controls = original_eamail_filter_controls()
        self.assertEqual(len(controls), NATIVE_FILTER_COUNT)
        self.assertEqual(NATIVE_FILTER_RADIO_WRAPPER, 0x941430)
        for index, control in enumerate(controls):
            with self.subTest(index=index):
                self.assertEqual(control.index, index)
                self.assertEqual(control.native_owner_offset,
                                 NATIVE_FILTER_FIRST_OWNER_OFFSET
                                 + index * NATIVE_FILTER_OWNER_STRIDE)
                self.assertEqual(control.original_english_idx_ordinal, 177 + index)
                self.assertEqual(control.native_radio_child_offset, 0x44)
                self.assertEqual(control.native_text_child_offset, 0x48)
                self.assertEqual(control.panel_local_rect,
                                 (22, 30 + 30 * index, 183, 28))
        self.assertEqual(controls[-1].panel_local_rect, (22, 300, 183, 28))

    def test_native_rect_is_half_open_prefilter_not_an_accepted_filter_event(self):
        hit = original_eamail_filter_native_window_candidate
        base = dict(index=0, source_panel_origin=(0, 148),
                    native_filter_control_dword=0x183)
        for point in ((22,178), (204,205), (50,190)):
            self.assertTrue(hit(source_screen_point=point, **base))
        for point in ((21,178), (205,178), (22,177), (22,206),
                      (50,208), (22,148)):
            self.assertFalse(hit(source_screen_point=point, **base))
        self.assertTrue(hit(9, source_panel_origin=(0,148),
                            source_screen_point=(22,448),
                            native_filter_control_dword=0x183))
        self.assertFalse(hit(9, source_panel_origin=(0,148),
                             source_screen_point=(22,476),
                             native_filter_control_dword=0x183))
        # A rectangle cannot override disabled bit0.
        self.assertFalse(hit(source_screen_point=(30,190),
                             native_filter_control_dword=0x182,
                             index=0, source_panel_origin=(0,148)))

    def test_guessed_or_invalid_source_objects_are_rejected(self):
        hit = original_eamail_filter_native_window_candidate
        for index in (-1, 10, True, None, 1.5):
            with self.subTest(index=index), self.assertRaises(ValueError):
                hit(index, source_panel_origin=(0,148),
                    source_screen_point=(30,190),
                    native_filter_control_dword=0x183)
        for flags in (None, False, -1, 0x100000000, '259'):
            with self.subTest(flags=flags), self.assertRaises(ValueError):
                hit(0, source_panel_origin=(0,148),
                    source_screen_point=(30,190),
                    native_filter_control_dword=flags)
        for origin, point in (((0,148), (True,180)),
                              ((0,148), [20,180]),
                              (None,(30,190)), ([0,148],(30,190)),
                              ((0,), (30,190)),
                              ((0,148),(0x80000000,180))):
            with self.subTest(point=point,origin=origin), self.assertRaises(ValueError):
                hit(0, source_panel_origin=origin,
                    source_screen_point=point,
                    native_filter_control_dword=0x183)


if __name__ == "__main__":
    unittest.main()
