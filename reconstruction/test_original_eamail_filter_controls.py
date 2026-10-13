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



    @unittest.skipUnless(__import__('os').environ.get('FM2001_ORIGINAL_EXE'),
                         'Canonical private original executable not available')
    def test_private_canonical_original_filter_vtable_and_distinct_filename_literals(self):
        """Opt-in native PE evidence guard; no executable process is launched."""
        from pathlib import Path
        import os
        import struct
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(
            Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes()
        )
        self.assertEqual(
            struct.unpack('<I',pe.read(0x7D6CC8 + 0x6C,4))[0],
            0x5D4AC0,
        )
        self.assertEqual(pe.read(0x5D4F10,7),
                         bytes.fromhex('6a1c68b7000000'))
        self.assertEqual(pe.read(0x5FFF64,5),
                         bytes.fromhex('68bc978300'))
        self.assertEqual(pe.read(0x5F4814,5),
                         bytes.fromhex('68285b8300'))
        self.assertEqual(
            pe.read(0x8397BC, len(
                b'fm2001_art\\generic\\GenericButtonsAndBars\\boost_type_11.444'
            ) + 1),
            b'fm2001_art\\generic\\GenericButtonsAndBars\\boost_type_11.444\x00',
        )
        self.assertEqual(
            pe.read(0x835B28, len(
                b'fm2001_art\\generic\\GenericButtonsAndBars\\button_type_11.444'
            ) + 1),
            b'fm2001_art\\generic\\GenericButtonsAndBars\\button_type_11.444\x00',
        )


    def test_native_event_ids_2_through_11_are_one_exclusive_group(self):
        from original_eamail_filter_controls import (
            project_original_eamail_delivered_filter_event as dispatch,
        )
        for index in range(10):
            with self.subTest(index=index):
                observed = dispatch(
                    native_control_event_id=index + 2,
                    previously_selected_filter_index=0,
                    source_filter_event_delivered=True,
                )
                self.assertEqual(observed.native_control_event_id, index + 2)
                self.assertEqual(observed.source_filter_index, index)
                self.assertEqual(observed.selected_filter_index, index)
                self.assertEqual(observed.previously_selected_filter_index, 0)
                self.assertEqual(observed.native_selected_changed, index != 0)
                self.assertTrue(observed.native_filtered_list_rebuild)
                self.assertTrue(observed.original_preview_selection_cleared)
        same = dispatch(
            native_control_event_id=2, previously_selected_filter_index=0,
            source_filter_event_delivered=True,
        )
        self.assertFalse(same.native_selected_changed)
        self.assertTrue(same.native_filtered_list_rebuild)

    def test_undelivered_mouse_candidate_cannot_be_promoted_to_native_event(self):
        from original_eamail_filter_controls import (
            project_original_eamail_delivered_filter_event as dispatch,
        )
        for id_value in (-1, 0, 1, 12, True, None, "3", 2.0):
            with self.subTest(id=id_value), self.assertRaises(ValueError):
                dispatch(native_control_event_id=id_value,
                         previously_selected_filter_index=0,
                         source_filter_event_delivered=True)
        for previous in (-1, 10, True, None, 0.5):
            with self.subTest(previous=previous), self.assertRaises(ValueError):
                dispatch(native_control_event_id=3,
                         previously_selected_filter_index=previous,
                         source_filter_event_delivered=True)
        for qualifier in (False, None, 1, "true"):
            with self.subTest(qualifier=qualifier), self.assertRaises(ValueError):
                dispatch(native_control_event_id=3,
                         previously_selected_filter_index=0,
                         source_filter_event_delivered=qualifier)

    def test_native_delivery_rebuilds_original_selected_user_mailbox(self):
        from test_original_eamail_list import inbox
        from original_management_presenter import (
            OriginalManagementPresentationError,
        )
        _session, presenter = inbox(12)
        initial = presenter.snapshot()
        self.assertEqual(presenter.eamail_filter_index, 0)
        self.assertEqual(len(initial.eamail.native_rows), 8)
        none, event = presenter.source_accepted_eamail_filter_event(4)
        self.assertEqual(event.native_control_event_id, 4)
        self.assertEqual(event.selected_filter_index, 2)
        self.assertEqual(presenter.eamail_filter_index, 2)
        self.assertEqual(len(none.eamail.native_rows), 0)
        self.assertEqual(presenter.eamail_scroll_offset, 0)
        restored, event = presenter.source_accepted_eamail_filter_event(7)
        self.assertTrue(event.native_selected_changed)
        self.assertEqual(event.selected_filter_index, 5)
        self.assertEqual(len(restored.eamail.native_rows), 8)
        self.assertEqual(presenter.eamail_filter_index, 5)
        current, event = presenter.source_accepted_eamail_filter_event(7)
        self.assertFalse(event.native_selected_changed)
        self.assertTrue(event.native_filtered_list_rebuild)
        self.assertEqual(current.eamail.native_rows, restored.eamail.native_rows)
        presenter.source_accepted_eamail_received_sort()
        self.assertEqual(presenter.eamail_filter_index, 5)
        presenter.source_accepted_eamail_scroll(21)
        self.assertEqual(presenter.eamail_scroll_offset, 1)
        before = presenter.eamail_filter_index
        with self.assertRaises(OriginalManagementPresentationError):
            presenter.source_accepted_eamail_filter_event(3)
        self.assertEqual(presenter.eamail_filter_index, before)
        self.assertEqual(presenter.eamail_scroll_offset, 1)
        presenter.navigate(0x65)
        self.assertEqual(presenter.eamail_filter_index, 0)
        self.assertEqual(presenter.eamail_scroll_offset, 0)
        self.assertIsNone(presenter.eamail_sort_index)

if __name__ == "__main__":
    unittest.main()
