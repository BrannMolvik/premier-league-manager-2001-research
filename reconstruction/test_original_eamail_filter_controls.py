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


    @unittest.skipUnless(__import__('os').environ.get('FM2001_ORIGINAL_EXE'),
                         'Original private EXE unavailable for static audit')
    def test_private_pea_group_and_ten_native_event_dispatch(self):
        """Re-audit actual original callback/vtable and jump table; never execute EXE."""
        import os
        import struct
        from pathlib import Path
        from gate13_button_source_trace import OriginalPE32

        pe = OriginalPE32.parse(Path(os.environ['FM2001_ORIGINAL_EXE']).read_bytes())
        def dword(va):
            return struct.unpack('<I', pe.read(va, 4))[0]
        self.assertEqual(dword(0x7D6CC8 + 0x98), 0x5D49F0)
        self.assertEqual(dword(0x7BE674 + 0x0C), 0x42DE00)
        self.assertEqual(dword(0x7BE674 + 0x10), 0x428AE0)
        self.assertEqual(pe.read(0x42DE00, 8),
                         bytes.fromhex('b801000000c20800'))
        self.assertEqual(pe.read(0x46E8E8, 5),
                         bytes.fromhex('bd02000000'))
        self.assertEqual(pe.read(0x46EA3A, 2),
                         bytes.fromhex('56 55'))
        self.assertEqual(pe.read(0x46EA5C, 3),
                         bytes.fromhex('6a0157'))
        # The exact original PEAMail::0x4721C0 switch table contains
        # ten branches to 0x4722C3, one for each native filter ID2..11.
        for event in range(2, 12):
            jump_index = pe.read(0x47236C + event - 1, 1)[0]
            self.assertEqual(dword(0x472354 + 4 * jump_index), 0x4722C3)
        self.assertEqual(pe.read(0x4722C3, 2),
                         bytes.fromhex('55 8d')[:2])



class OriginalEAMailGroupedNativeCallbackGateTests(unittest.TestCase):
    def test_inactive_original_radio_can_attempt_callback_but_not_deliver(self):
        from original_eamail_filter_controls import (
            original_eamail_native_grouped_callback_candidate as eligible,
            project_original_eamail_delivered_filter_event as delivered,
        )
        base = dict(native_control_state_dword=0x2, native_event_id=3,
                    shared_group_registered=True, native_event_argument_present=True,
                    owner_pre_callback_accepted=True, currently_selected=False)
        self.assertTrue(eligible(**base))
        for change in ({"native_control_state_dword": 0},
                       {"native_event_id": 0}, {"native_event_id": 12},
                       {"shared_group_registered": False},
                       {"native_event_argument_present": False},
                       {"owner_pre_callback_accepted": False},
                       {"currently_selected": True}):
            with self.subTest(change=change):
                self.assertFalse(eligible(**(base | change)))
        # Repeated click on the originally selected radio is not proof of a
        # second source-delivered event, though delivery would rebuild the list.
        self.assertFalse(eligible(**(base | {
            "native_event_id": 2, "currently_selected": True,
        })))
        with self.assertRaises(ValueError):
            delivered(native_control_event_id=3,
                      previously_selected_filter_index=0,
                      source_filter_event_delivered=False)

    def test_reject_unqualified_group_event_receipts(self):
        from original_eamail_filter_controls import (
            original_eamail_native_grouped_callback_candidate as eligible,
        )
        base = dict(native_control_state_dword=2, native_event_id=3,
                    shared_group_registered=True, native_event_argument_present=True,
                    owner_pre_callback_accepted=True, currently_selected=False)
        for bad in (False, None, -1, 0x100000000, "2"):
            with self.subTest(state=bad), self.assertRaises(ValueError):
                eligible(**(base | {"native_control_state_dword": bad}))
        for bad in (True, None, -1, 0x100000000, "3"):
            with self.subTest(event=bad), self.assertRaises(ValueError):
                eligible(**(base | {"native_event_id": bad}))
        for gate in ("shared_group_registered", "native_event_argument_present",
                     "owner_pre_callback_accepted", "currently_selected"):
            for bad in (None, 1, "true"):
                with self.subTest(gate=gate, bad=bad), self.assertRaises(ValueError):
                    eligible(**(base | {gate: bad}))

    @unittest.skipUnless(__import__("os").environ.get("FM2001_ORIGINAL_EXE"),
                         "Canonical private EXE unavailable")
    def test_original_group_native_callback_bytes(self):
        import os
        from pathlib import Path
        from gate13_button_source_trace import OriginalPE32
        pe = OriginalPE32.parse(Path(os.environ["FM2001_ORIGINAL_EXE"]).read_bytes())
        for addr, hexdump in (
                (0x5D49B9, "89 71 38"),
                (0x5D4ACC, "8b 46 38"),
                (0x5D4AD3, "8b 46 20"),
                (0x5D4AE3, "8b 4e 24"),
                (0x5D4AF5, "8a 46 40"),
                (0x5D4B02, "ff 90 98 00 00 00")):
            with self.subTest(addr=hex(addr)):
                self.assertEqual(pe.read(addr, len(bytes.fromhex(hexdump))),
                                 bytes.fromhex(hexdump))


if __name__ == "__main__":
    unittest.main()
