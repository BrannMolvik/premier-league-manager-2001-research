"""Recovery530: authentic PMessageRow three text child owners, 8 native rows."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase, main

from gate13_management_source_data import ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from original_eamail_native_row_fields import (
    ORIGINAL_EAMAIL_ROW_SCREEN_START,
    ORIGINAL_ROW_NATIVE_FIELDS,
    OriginalEAMailRowFieldSourceError,
    build_selected_user_original_eam_source_rows,
    project_original_native_eam_row_fields,
)
from original_eamail_language import (
    ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE,
    load_verified_original_eamail_language,
)
from original_eamail_native_small_window import (
    OriginalInitialEAMailCaptionedWindow,
    build_source_captioned_selected_user_initial_eamail_window,
)
from test_original_eamail_live_user_bridge import controller


SOURCE_ROOT = Path(__file__).resolve().parent.parent / "original_assets" / "source"
DAY = date(2000, 8, 1)


def live_delivered(offsets):
    game = controller()
    game.select_club(1)
    owner = game.state.original_delivered_mailboxes
    for i, offset in enumerate(offsets):
        due = DAY + timedelta(days=offset)
        record = PlayerTransferRequest(
            player_id=3000+i, queued_on=due-timedelta(days=1),
            due_on=due, recipient_manager_key=0, sender_club_id=1,
        )
        owner.deliver_source_ready_transfer_request(
            record, pending_identity=f"real-EAM-{i}", at_date=due,
            original_record_ready=True,
        )
    return game


class OriginalNativeEAMRowFieldsTests(TestCase):
    def test_exact_original_three_text_children_and_relative_screen_owner(self):
        self.assertEqual(ORIGINAL_EAMAIL_ROW_SCREEN_START, (233, 178))
        self.assertEqual(tuple(item[0] for item in ORIGINAL_ROW_NATIVE_FIELDS),
                         (2, 3, 0))
        self.assertEqual(tuple(item[2] for item in ORIGINAL_ROW_NATIVE_FIELDS),
                         (0x1C, 0x18, 0x04))
        game = live_delivered((5, 1, 2, 6, 9, 0, 2, 8, 7, 10))
        source = ManagementSourceDataBridge(game)
        previous = game.state.original_delivered_mailboxes.snapshot()
        data = build_selected_user_original_eam_source_rows(
            source, original_source_root=SOURCE_ROOT,
            filter_index=5, sort_index=3, scroll_offset=1,
        )
        self.assertEqual(data.original_filtered_count, 10)
        self.assertEqual(data.original_max_scroll_offset, 2)
        self.assertEqual(data.original_scroll_offset, 1)
        self.assertEqual(len(data.native_rows), 8)
        for i, row in enumerate(data.native_rows):
            self.assertEqual(row.native_visible_ordinal, i+1)
            self.assertEqual(row.row_screen_rect, (233, 178+i*20, 532, 18))
            self.assertEqual(tuple(child.child_id for child in row.original_text_fields),
                             (2, 3, 0))
            self.assertEqual(tuple(child.screen_rect for child in row.original_text_fields),
                             ((271, 178+i*20, 215, 16),
                              (489, 178+i*20, 215, 16),
                              (707, 178+i*20, 71, 16)))
            self.assertEqual(
                tuple(child.source_verified_visible_text
                      for child in row.original_text_fields),
                (None, "Transfer List", (
                    f"{row.qualified_record_date.day}/"
                    f"{row.qualified_record_date.strftime('%b')}/"
                    f"{row.qualified_record_date.year}"
                )),
            )
            self.assertEqual(row.original_title, "Transfer List")
            self.assertEqual(row.native_record_class, "EAMPlayerAskTransferListsub")
            self.assertEqual(
                row.source_original_unexpanded_preview_template,
                ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE,
            )
            self.assertIn(
                "{PHRASE:PLAYERASKTRANSFERLISTREASON}",
                row.source_original_unexpanded_preview_template,
            )
            self.assertEqual(row.qualified_player_id, 3000+i+1)
            self.assertEqual(row.qualified_record_date, DAY+timedelta(
                days=(5,1,2,6,9,0,2,8,7,10)[i+1]))
            self.assertFalse(row.native_full_text_and_art_rendered)
        self.assertFalse(data.original_gui_accepted)
        self.assertEqual(game.state.original_delivered_mailboxes.snapshot(), previous)

    def test_source_owner_pending_other_manager_not_promoted_to_native_rows(self):
        game = controller()
        game.select_club(1)
        game.state.original_delivered_mailboxes.register_source_user(1)
        owner = game.state.original_delivered_mailboxes
        due = DAY + timedelta(days=1)
        other = PlayerTransferRequest(
            player_id=20, queued_on=DAY, due_on=due,
            recipient_manager_key=1, sender_club_id=1,
        )
        owner.deliver_source_ready_transfer_request(
            other, pending_identity="other-user", at_date=due,
            original_record_ready=True,
        )
        game.state.player_transfer_requests.append(PlayerTransferRequest(
            player_id=21, queued_on=DAY, due_on=due,
            recipient_manager_key=0, sender_club_id=1,
        ))
        rows = build_selected_user_original_eam_source_rows(
            ManagementSourceDataBridge(game), original_source_root=SOURCE_ROOT,
            filter_index=0, sort_index=3,
        )
        self.assertEqual(rows.native_rows, ())
        self.assertEqual(rows.original_filtered_count, 0)
        self.assertEqual(len(owner.delivered_for_manager(1)), 1)
        self.assertEqual(len(game.state.player_transfer_requests), 1)

    def test_row_projection_requires_complete_native_captioned_view(self):
        with self.assertRaisesRegex(OriginalEAMailRowFieldSourceError, "required"):
            project_original_native_eam_row_fields(object())
        game = live_delivered((2, 1))
        captioned = build_source_captioned_selected_user_initial_eamail_window(
            ManagementSourceDataBridge(game),
            original_source_root=SOURCE_ROOT,
            filter_index=5, sort_index=3,
        )
        bad = OriginalInitialEAMailCaptionedWindow(
            window=captioned.window,
            visible_original_subjects=("invented", "invented"),
        )
        with self.assertRaisesRegex(OriginalEAMailRowFieldSourceError, "source-proven"):
            project_original_native_eam_row_fields(bad)
        # Without the source-qualified EAM string mapping the pure row
        # geometry projection must NOT invent body text or use title as body.
        no_language = project_original_native_eam_row_fields(captioned)
        self.assertTrue(no_language.native_rows)
        self.assertTrue(all(
            row.source_original_unexpanded_preview_template is None
            for row in no_language.native_rows
        ))
        with self.assertRaisesRegex(OriginalEAMailRowFieldSourceError, "authenticated"):
            project_original_native_eam_row_fields(captioned, eam_language=object())
        source_language = load_verified_original_eamail_language(SOURCE_ROOT)
        rows_with_source = project_original_native_eam_row_fields(
            captioned, eam_language=source_language,
        )
        self.assertEqual(
            rows_with_source.native_rows[0].source_original_unexpanded_preview_template,
            ORIGINAL_TRANSFER_LIST_BODY_VERIFIED_TEMPLATE,
        )
        with self.assertRaisesRegex(OriginalEAMailRowFieldSourceError, "eight-row"):
            project_original_native_eam_row_fields(
                OriginalInitialEAMailCaptionedWindow(
                    window=captioned.window,
                    visible_original_subjects=("Transfer List",),
                )
            )


if __name__ == "__main__":
    main()
