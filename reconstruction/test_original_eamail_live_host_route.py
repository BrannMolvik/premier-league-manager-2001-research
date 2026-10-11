"""Normal host PEAMail entrypoint + actual original 8-row art ownership.

Not native font/status/action acceptance: screen's initial true row strips
only, with selected real user's delivered initial transfer subtype.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main

from ea444_decoder import EA444DecodedImage
from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl
from original_eamail_live_canvas import (
    OriginalEAMailRowArt, OriginalEAMailCanvasError,
    source_original_eamail_row_backgrounds,
)
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_GRID_RESOURCES, ORIGINAL_EAMAIL_PANEL_RECT,
)
from original_management_canvas import build_management_canvas_frame
from original_management_presenter import OriginalManagementPresenter
from original_eamail_native_row_fields import build_selected_user_original_eam_source_rows
from gate13_management_source_data import ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from test_original_eamail_live_user_bridge import controller


class FixtureEAMBridge(ManagementSourceDataBridge):
    # The source-shaped integration fixture has no scheduled original fixed-
    # League header text yet; only assert the independently proven EAM path.
    def management_header_match(self):
        return None


def ordinary_inbox():
    game = controller()
    session = FrontEndSession(lambda: game)
    session.dispatch(StartMenuControl.NEW_GAME)
    session.choose_club(1)
    session.dispatch(TeamSelectControl.START_CONTINUE)
    # Synthetic canonical fixture's Club dataclass omits the original STR
    # names, so provide distinct source-shaped full and short names.
    state = session.gameplay.state
    for index, club in tuple(state.clubs.items()):
        state.clubs[index] = SimpleNamespace(
            **vars(club), name=f"Full Club {index}", short_name=f"C{index}",
        )
    return session


def delivered(session, player_id=1000, day=date(2000, 8, 1)):
    request = PlayerTransferRequest(
        player_id=player_id,
        queued_on=day-timedelta(days=1), due_on=day,
        recipient_manager_key=0, sender_club_id=1,
        verified_native_association_word_at_creation=1,
    )
    return session.gameplay.state.original_delivered_mailboxes.deliver_source_ready_transfer_request(
        request, pending_identity=f"native:{player_id}", at_date=day,
        original_record_ready=True,
    )


class OriginalInboxHostRouteTests(TestCase):
    def test_source_pmenu_root_and_child_navigate_real_delivered_owner(self):
        session = ordinary_inbox()
        delivered(session)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        root = presenter.source_accepted_pmenu_action("title", 1, 0)
        self.assertEqual(root.action.action_kind, "expand_root")
        self.assertEqual(presenter.expanded_root_id, 1)
        nav = presenter.source_accepted_pmenu_action("child", 0x65, 0)
        self.assertEqual(nav.action.action_kind, "open_panel")
        self.assertEqual(nav.presentation.panel_class, "PEAMail")
        self.assertEqual(presenter.selected_child_id, 0x65)
        self.assertEqual(nav.presentation.eamail.original_filtered_count, 1)
        texts = nav.presentation.eamail.native_rows[0].original_text_fields
        self.assertEqual(texts[1].source_verified_visible_text, "Transfer List")
        self.assertEqual(texts[2].source_verified_visible_text, "1/Aug/2000")
        self.assertIn("Football Club", texts[0].source_verified_visible_text)
        frame = build_management_canvas_frame(presenter)
        self.assertEqual(frame.panel_rect, ORIGINAL_EAMAIL_PANEL_RECT)
        self.assertFalse(frame.complete_source_pixel_frame_available)
        self.assertFalse(frame.presentation.eamail.original_gui_accepted)

    def test_normal_original_row_bitmap_layers_are_532x18_at_native_screen(self):
        session = ordinary_inbox()
        delivered(session)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        presenter.source_accepted_pmenu_action("title", 1, 0)
        rows = presenter.source_accepted_pmenu_action("child", 0x65, 0).presentation.eamail
        image = EA444DecodedImage(
            532, 18, bytes((31, 49, 72, 255)) * (532 * 18),
            consumed_bits=0, transparent_pixels=0,
        )
        rendered = source_original_eamail_row_backgrounds(rows, OriginalEAMailRowArt(image))
        self.assertEqual(len(rendered), 1)
        self.assertEqual((rendered[0].x, rendered[0].y, rendered[0].width,
                          rendered[0].height), (233, 178, 532, 18))
        self.assertEqual(rendered[0].source_path, ORIGINAL_EAMAIL_GRID_RESOURCES[0].source_path)
        self.assertTrue(rendered[0].png.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertFalse(rendered[0].native_full_text_and_art_rendered)
        self.assertFalse(rows.original_gui_accepted)

    def test_foreign_manager_pending_and_empty_inbox_never_draw_art_rows(self):
        session = ordinary_inbox()
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        presenter.source_accepted_pmenu_action("title", 1, 0)
        rows = presenter.source_accepted_pmenu_action("child", 0x65, 0).presentation.eamail
        self.assertEqual(rows.native_rows, ())
        image = EA444DecodedImage(
            532, 18, bytes((0, 0, 0, 255)) * (532 * 18),
            consumed_bits=0, transparent_pixels=0,
        )
        art = OriginalEAMailRowArt(image)
        self.assertEqual(source_original_eamail_row_backgrounds(rows, art), ())
        with self.assertRaises(OriginalEAMailCanvasError):
            OriginalEAMailRowArt(EA444DecodedImage(
                2, 2, bytes((0, 0, 0, 255)) * 4,
                consumed_bits=0, transparent_pixels=0,
            ))


if __name__ == "__main__":
    main()
