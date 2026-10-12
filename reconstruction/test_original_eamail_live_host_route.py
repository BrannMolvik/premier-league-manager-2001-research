"""Normal host PEAMail entrypoint + actual original 8-row art ownership.

Not native font/status/action acceptance: screen's initial true row strips
only, with selected real user's delivered initial transfer subtype.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main

from ea444_decoder import EA444DecodedImage
from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl
from original_eamail_live_canvas import (
    OriginalEAMailRowArt, OriginalEAMailCanvasError,
    original_eamail_row_at_screen_point, source_original_eamail_row_backgrounds,
    original_empty_eamail_preview, ORIGINAL_EAMAIL_EMPTY_PREVIEW_SCREEN_RECT,
    ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH,
)
from original_eamail_source_contract import (
    ORIGINAL_EAMAIL_GRID_RESOURCES, ORIGINAL_EAMAIL_PANEL_RECT,
)
from original_management_canvas import build_management_canvas_frame
from original_game_host import OriginalGameTkHost
from original_management_presenter import OriginalManagementPresenter
from original_eamail_native_row_fields import build_selected_user_original_eam_source_rows
from gate13_management_source_data import ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from test_original_eamail_live_user_bridge import controller


class FixtureEAMBridge(ManagementSourceDataBridge):
    # Fresh PMenu navigation first snapshots the source Squad screen.
    # The source-shaped synthetic database's numeric positions do not have
    # native player abbreviations. Give this test the already verified
    # presentation-only Row fixtures instead of falsifying simulation data.
    original_paired_squad = None

    def squad_rows(self):
        from test_original_management_presenter import Row
        return tuple(
            Row(i, 1000 + i, "Test", "Player", "Test Player")
            for i in range(20)
        )

    # The test database has no shipped fixed-League header text; this route
    # tests the real source-bound Inbox data and PMenu action separately.
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

    def test_original_empty_preview_art_and_host_source_coordinates(self):
        session = ordinary_inbox()
        delivered(session, player_id=1000)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        presenter.source_accepted_pmenu_action("title", 1, 0)
        presenter.source_accepted_pmenu_action("child", 0x65, 0)
        frame = build_management_canvas_frame(presenter)
        plain = EA444DecodedImage(
            532, 18, bytes((31, 49, 72, 255)) * (532 * 18),
            consumed_bits=0, transparent_pixels=0,
        )
        disabled = EA444DecodedImage(
            532, 187, bytes((44, 55, 66, 255)) * (532 * 187),
            consumed_bits=0, transparent_pixels=0,
        )
        art = OriginalEAMailRowArt(plain, plain, disabled)
        self.assertEqual(ORIGINAL_EAMAIL_EMPTY_PREVIEW_SCREEN_RECT,
                         (246, 343, 532, 187))
        self.assertEqual(ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH,
                         "FM2001_Art/Generic/EAMail/preview_panel_disabled.444")
        overlay = original_empty_eamail_preview(frame.presentation.eamail, art)
        self.assertEqual(overlay.screen_rect, (246, 343, 532, 187))
        self.assertEqual(overlay.source_path, ORIGINAL_EAMAIL_EMPTY_PREVIEW_SOURCE_PATH)
        self.assertTrue(overlay.png.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        self.assertFalse(overlay.native_body_text_rendered)
        self.assertIsNone(original_empty_eamail_preview(
            frame.presentation.eamail, art, selected_node_serial=1
        ))
        self.assertIsNone(original_empty_eamail_preview(
            frame.presentation.eamail, OriginalEAMailRowArt(plain, plain)
        ))
        with self.assertRaisesRegex(OriginalEAMailCanvasError, "geometry"):
            OriginalEAMailRowArt(plain, plain, plain)

        # Check real host draw integration without invoking Tk or original EXE.
        host = object.__new__(OriginalGameTkHost)
        host.eamail_row_art = art
        host._eamail_selected_node_serial = None
        host._eamail_selected_row_token = None
        host.tk = SimpleNamespace(NW="nw")
        host._photo = lambda data: data
        drawn = []
        host._create_native_image = lambda x, y, **kw: drawn.append(
            (x, y, kw.get("anchor"), kw.get("image"))
        )
        self.assertEqual(host._draw_eamail_rows(frame), 2)
        self.assertEqual(tuple((x, y) for x, y, *_ in drawn),
                         ((233, 178), (246, 343)))
        self.assertTrue(all(item[-1].startswith(b"\\x89PNG\\r\\n\\x1a\\n")
                            for item in drawn))
        drawn.clear()
        host._eamail_selected_node_serial = frame.presentation.eamail.native_rows[0].original_internal_node_serial
        self.assertEqual(host._draw_eamail_rows(frame), 1)
        self.assertEqual(tuple((x, y) for x, y, *_ in drawn), ((233, 178),))

    def test_native_row_selection_is_original_sprite_and_second_click_fails_closed(self):
        session = ordinary_inbox()
        delivered(session, player_id=1000)
        delivered(session, player_id=1001)
        presenter = OriginalManagementPresenter(session, bridge_factory=FixtureEAMBridge)
        presenter.source_accepted_pmenu_action("title", 1, 0)
        presenter.source_accepted_pmenu_action("child", 0x65, 0)
        frame = build_management_canvas_frame(presenter)
        rows = frame.presentation.eamail
        self.assertEqual(len(rows.native_rows), 2)
        first, second = rows.native_rows
        self.assertEqual(original_eamail_row_at_screen_point(rows, 233, 178),
                         first.original_internal_node_serial)
        self.assertEqual(original_eamail_row_at_screen_point(rows, 764, 195),
                         first.original_internal_node_serial)
        self.assertIsNone(original_eamail_row_at_screen_point(rows, 765, 178))
        self.assertIsNone(original_eamail_row_at_screen_point(rows, 233, 196))
        self.assertIsNone(original_eamail_row_at_screen_point(rows, 233, 197))
        self.assertEqual(original_eamail_row_at_screen_point(rows, 233, 198),
                         second.original_internal_node_serial)

        normal = EA444DecodedImage(
            532, 18, bytes((31, 49, 72, 255)) * (532 * 18),
            consumed_bits=0, transparent_pixels=0,
        )
        selected = EA444DecodedImage(
            532, 18, bytes((69, 11, 20, 255)) * (532 * 18),
            consumed_bits=0, transparent_pixels=0,
        )
        art = OriginalEAMailRowArt(normal, selected)
        rendered = source_original_eamail_row_backgrounds(
            rows, art, selected_node_serial=first.original_internal_node_serial,
        )
        self.assertTrue(rendered[0].native_selected)
        self.assertEqual(rendered[0].source_path, ORIGINAL_EAMAIL_GRID_RESOURCES[1].source_path)
        self.assertNotEqual(rendered[0].png, rendered[1].png)
        self.assertFalse(rendered[1].native_selected)
        with self.assertRaises(OriginalEAMailCanvasError):
            source_original_eamail_row_backgrounds(rows, art, selected_node_serial=-100)
        with self.assertRaises(OriginalEAMailCanvasError):
            source_original_eamail_row_backgrounds(
                rows, OriginalEAMailRowArt(normal),
                selected_node_serial=first.original_internal_node_serial,
            )

        # Call the real host pointer handler without Tk, recording redraws.
        before_delivered = session.gameplay.state.original_delivered_mailboxes.delivered_for_manager(0)
        host = object.__new__(OriginalGameTkHost)
        host.pmenu_popup_active = False
        host.eamail_row_art = art
        host._eamail_selected_node_serial = None
        host._eamail_selected_row_token = None
        redraws = []
        host.redraw = lambda: redraws.append(host._eamail_selected_node_serial)
        self.assertTrue(host._press_original_eamail_row(SimpleNamespace(x=234, y=179), frame))
        self.assertEqual(redraws, [first.original_internal_node_serial])
        self.assertTrue(host._press_original_eamail_row(SimpleNamespace(x=234, y=179), frame))
        self.assertEqual(len(redraws), 1)
        self.assertIn("unresolved", host.last_status)
        # Switching row deselects the first; the strip is source-accurate.
        self.assertTrue(host._press_original_eamail_row(SimpleNamespace(x=235, y=199), frame))
        self.assertEqual(redraws[-1], second.original_internal_node_serial)
        self.assertFalse(host._press_original_eamail_row(SimpleNamespace(x=234, y=196), frame))
        self.assertEqual(len(redraws), 2)
        # Native pointer comparison cannot depend on Python integer identity:
        # node serials can grow beyond the small-integer interning range.
        high = replace(first, original_internal_node_serial=1000)
        high_rows = replace(rows, native_rows=(high,))
        high_frame = SimpleNamespace(
            presentation=SimpleNamespace(panel_class="PEAMail", eamail=high_rows),
        )
        host._eamail_selected_node_serial = None
        host._eamail_selected_row_token = None
        self.assertTrue(host._press_original_eamail_row(
            SimpleNamespace(x=234, y=179), high_frame,
        ))
        count_after_select = len(redraws)
        self.assertTrue(host._press_original_eamail_row(
            SimpleNamespace(x=234, y=179), high_frame,
        ))
        self.assertEqual(host._eamail_selected_node_serial, 1000)
        self.assertEqual(len(redraws), count_after_select)
        # A second press cannot manufacture a dialog or mutate delivered data.
        self.assertEqual(
            session.gameplay.state.original_delivered_mailboxes.delivered_for_manager(0),
            before_delivered,
        )

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
