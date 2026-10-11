"""Source PBg ID1 direct mail header action, separate from popup child press."""

from types import SimpleNamespace
from unittest import TestCase, main

from original_pbg_direct_inbox import (
    PBG_DIRECT_EAMAIL_RECT, PBG_DIRECT_EAMAIL_FACTORY_ID,
    original_pbg_direct_eamail_press,
)
from original_game_host import OriginalGameTkHost
from original_management_canvas import build_management_canvas_frame
from original_management_presenter import OriginalManagementPresenter
from test_original_eamail_live_host_route import (
    FixtureEAMBridge, delivered, ordinary_inbox,
)


class OriginalPBgDirectMailTests(TestCase):
    def test_source_original_header_rectangle_and_panel_stack_guard(self):
        self.assertEqual(PBG_DIRECT_EAMAIL_RECT, (558, 0, 40, 95))
        self.assertEqual(PBG_DIRECT_EAMAIL_FACTORY_ID, 0x65)
        def accepted(x, y, panel="PSquadScreen", popup=False):
            return original_pbg_direct_eamail_press(
                x, y, active_panel_class=panel, pmenu_popup_active=popup,
            )
        for point in ((558, 0), (597, 0), (558, 94), (597, 94)):
            self.assertTrue(accepted(*point))
        for point in ((557, 10), (598, 10), (560, -1), (560, 95),
                      (599, 10), (700, 10), (558, 178)):
            self.assertFalse(accepted(*point))
        self.assertFalse(accepted(558, 0, panel="PEAMail"))
        self.assertFalse(accepted(558, 0, popup=True))
        with self.assertRaises(ValueError):
            accepted(558.1, 0)
        with self.assertRaises(ValueError):
            original_pbg_direct_eamail_press(
                558, 0, active_panel_class="PSquadScreen", pmenu_popup_active=1
            )

    def test_real_manager_from_squad_to_delivered_inbox_and_no_duplicate(self):
        session = ordinary_inbox()
        delivered(session)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        self.assertEqual(presenter.selected_child_id, 0xCE)
        self.assertIsNone(presenter.expanded_root_id)
        snapshot = presenter.source_accepted_pbg_direct_inbox_action()
        self.assertEqual(snapshot.panel_class, "PEAMail")
        self.assertEqual(snapshot.eamail.original_filtered_count, 1)
        self.assertEqual(presenter.selected_child_id, 0x65)
        self.assertEqual(presenter.expanded_root_id, 1)
        self.assertIsNone(presenter.source_accepted_pbg_direct_inbox_action())
        self.assertEqual(presenter.snapshot().eamail.original_filtered_count, 1)
        self.assertEqual(build_management_canvas_frame(presenter).panel_rect,
                         (0, 148, 800, 530))

    def test_normal_host_direct_press_reuses_existing_source_panel_and_art_load(self):
        session = ordinary_inbox()
        delivered(session)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        host = object.__new__(OriginalGameTkHost)
        host.management_presenter = presenter
        host.pmenu_popup_active = False
        host._eamail_selected_node_serial = 999
        host._eamail_selected_row_token = object()
        host._management_resource_families_loaded = {"squad", "eamail"}
        redraws = []
        host.redraw = lambda: redraws.append(presenter.selected_child_id)
        frame = build_management_canvas_frame(presenter)
        self.assertFalse(host._press_original_pbg_direct_inbox(
            SimpleNamespace(x=598, y=0), frame,
        ))
        self.assertTrue(host._press_original_pbg_direct_inbox(
            SimpleNamespace(x=558, y=0), frame,
        ))
        self.assertEqual(redraws, [0x65])
        self.assertIsNone(host._eamail_selected_node_serial)
        self.assertIsNone(host._eamail_selected_row_token)
        self.assertTrue(host._press_original_pbg_direct_inbox(
            SimpleNamespace(x=558, y=0), build_management_canvas_frame(presenter),
        ) is False)
        self.assertEqual(redraws, [0x65])
        host.pmenu_popup_active = True
        self.assertFalse(host._press_original_pbg_direct_inbox(
            SimpleNamespace(x=558, y=0), build_management_canvas_frame(presenter),
        ))


if __name__ == "__main__":
    main()
