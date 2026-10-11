"""Original PEAMail initial transfer subtype: small sorter and viewport tests.

Native original SHA-256 833bf95e...b7cc3, insertion 0x47293D..0x4729A4,
default descending-date comparator 0x472C60 and CMessageList eight rows.
All messages here have real source-qualified MPM due + DBRUser delivery.
No original GUI, text, pointer-click, native >16 sort or invented status labels.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from unittest import TestCase, main

from gate13_management_source_data import ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from original_eamail_native_filter import OriginalEAMailFilterSourceError
from original_eamail_native_small_window import (
    ORIGINAL_EAMAIL_SORT_COMPARATORS, ORIGINAL_EAMAIL_SMALL_THRESHOLD,
    original_initial_transfer_eam_sorted_window,
    build_selected_user_initial_eamail_window,
    build_source_captioned_selected_user_initial_eamail_window,
)
from test_original_eamail_live_user_bridge import controller


DAY = date(2000, 7, 1)


def deliver_source_records(game, offsets):
    """Use the actual registered selected human mailbox; no global MPM view."""
    owner = game.state.original_delivered_mailboxes
    for n, offset in enumerate(offsets):
        due = DAY + timedelta(days=offset)
        record = PlayerTransferRequest(
            player_id=n + 1000, queued_on=due-timedelta(days=1),
            due_on=due, recipient_manager_key=0, sender_club_id=1,
        )
        owner.deliver_source_ready_transfer_request(
            record, pending_identity=f"source-event-{n}",
            at_date=due, original_record_ready=True,
        )
    return ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()


class OriginalNativeSmallSortedWindowTests(TestCase):
    def test_real_manager_delivered_mail_is_captioned_from_original_game_bytes(self):
        original_assets_root = (
            Path(__file__).resolve().parent.parent / "original_assets" / "source"
        )
        game = controller()
        game.select_club(1)
        delivered = deliver_source_records(game, (4, 1, 2, 3, 5, 0, 6, 7, 8))
        source = ManagementSourceDataBridge(game)
        result = build_source_captioned_selected_user_initial_eamail_window(
            source, original_source_root=original_assets_root,
            filter_index=5, sort_index=3, scroll_offset=1,
        )
        self.assertEqual(result.window.native_comparator_va, 0x472C00)
        self.assertEqual(result.window.original_sorted_rows, delivered)
        self.assertEqual(len(result.window.viewport.visible_rows), 8)
        self.assertEqual(result.visible_original_subjects, ("Transfer List",) * 8)
        self.assertEqual(result.window.viewport.max_scroll_offset, 1)
        rejected = build_source_captioned_selected_user_initial_eamail_window(
            source, original_source_root=original_assets_root,
            filter_index=2, sort_index=3,
        )
        self.assertEqual(rejected.window.original_filtered_count, 0)
        self.assertEqual(rejected.visible_original_subjects, ())
        from original_eamail_language import OriginalEAMailLanguageError
        with self.assertRaises(OriginalEAMailLanguageError):
            build_source_captioned_selected_user_initial_eamail_window(
                source, original_source_root=original_assets_root / "nonexistent",
                filter_index=5, sort_index=3,
            )

    def test_source_bridge_is_required_and_not_generic_pending_queues(self):
        with self.assertRaisesRegex(OriginalEAMailFilterSourceError, "selected-human"):
            build_selected_user_initial_eamail_window(
                object(), filter_index=0, sort_index=4,
            )
        game = controller()
        game.select_club(1)
        state = game.state
        pending = PlayerTransferRequest(
            player_id=1, queued_on=DAY,
            due_on=DAY+timedelta(days=1), recipient_manager_key=0,
            sender_club_id=1,
        )
        state.player_transfer_requests.append(pending)
        self.assertEqual(build_selected_user_initial_eamail_window(
            ManagementSourceDataBridge(game), filter_index=0, sort_index=4,
        ).original_sorted_rows, ())
        self.assertEqual(len(state.player_transfer_requests), 1)

    def test_source_insert_date_descending_and_equal_day_append_order(self):
        game = controller()
        game.select_club(1)
        dates = (3, 1, 3, 2, 0, 3, 1, 4, 4, 2)
        delivered = deliver_source_records(game, dates)
        before = game.state.original_delivered_mailboxes.snapshot()
        snapshot = build_selected_user_initial_eamail_window(
            ManagementSourceDataBridge(game),
            filter_index=5, sort_index=None,
        )
        self.assertEqual(snapshot.native_comparator_va, 0x472C60)
        self.assertEqual(snapshot.selected_sort_index, 4)
        self.assertEqual(snapshot.original_filtered_count, 10)
        # Stable original <=16 insertion branch: equal-date envelope nodes
        # retain append order, not sorted by player ID or a fabricated title.
        self.assertEqual(
            tuple(row.player_id - 1000 for row in snapshot.original_sorted_rows),
            (7, 8, 0, 2, 5, 3, 9, 1, 6, 4),
        )
        self.assertEqual(len(snapshot.viewport.visible_rows), 8)
        self.assertEqual(snapshot.viewport.max_scroll_offset, 2)
        scrolled = original_initial_transfer_eam_sorted_window(
            delivered, filter_index=5, sort_index=4, scroll_offset=2,
        )
        self.assertEqual(
            scrolled.viewport.visible_rows,
            snapshot.original_sorted_rows[2:10],
        )
        self.assertEqual(
            game.state.original_delivered_mailboxes.snapshot(), before,
        )

    def test_initial_status_sort_controls_preserve_all_mail_order(self):
        game = controller()
        game.select_club(1)
        delivered = deliver_source_records(game, (2, 0, 1, 0))
        for index in (0, 1):
            snapshot = original_initial_transfer_eam_sorted_window(
                delivered, filter_index=0, sort_index=index,
            )
            self.assertEqual(snapshot.native_comparator_va,
                             ORIGINAL_EAMAIL_SORT_COMPARATORS[index])
            self.assertEqual(snapshot.original_sorted_rows, delivered)
        # Initial subtype's category is 5; 2..9 other than 5 are empty.
        self.assertEqual(
            original_initial_transfer_eam_sorted_window(
                delivered, filter_index=3, sort_index=4,
            ).original_sorted_rows, (),
        )
        self.assertEqual(
            original_initial_transfer_eam_sorted_window(
                delivered, filter_index=1, sort_index=4,
            ).original_filtered_count, 4,
        )

    def test_all_initial_transfer_subject_sort_ties_are_stable_to_sixteen(self):
        game = controller()
        game.select_club(1)
        delivered = deliver_source_records(
            game, tuple((i * 7) % 13 for i in range(16)),
        )
        native = original_initial_transfer_eam_sorted_window(
            delivered, filter_index=5, sort_index=3, scroll_offset=8,
        )
        self.assertEqual(native.original_filtered_count, 16)
        self.assertEqual(native.original_sorted_rows, delivered)
        self.assertEqual(native.viewport.visible_rows, delivered[8:16])

    def test_first_sixteen_native_sort_accepted_seventeen_fail_closed(self):
        game = controller()
        game.select_club(1)
        first = deliver_source_records(game, tuple(15-i for i in range(16)))
        self.assertEqual(ORIGINAL_EAMAIL_SMALL_THRESHOLD, 16)
        result = original_initial_transfer_eam_sorted_window(
            first, filter_index=5, sort_index=4, scroll_offset=8,
        )
        self.assertEqual(result.viewport.max_scroll_offset, 8)
        self.assertEqual(result.original_sorted_rows, first)
        extra = PlayerTransferRequest(
            player_id=1117, queued_on=DAY, due_on=DAY+timedelta(days=1),
            recipient_manager_key=0, sender_club_id=1,
        )
        game.state.original_delivered_mailboxes.deliver_source_ready_transfer_request(
            extra, pending_identity="source-event-16",
            at_date=extra.due_on, original_record_ready=True,
        )
        seventeen = ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()
        with self.assertRaisesRegex(OriginalEAMailFilterSourceError, ">16"):
            original_initial_transfer_eam_sorted_window(
                seventeen, filter_index=5, sort_index=4,
            )

    def test_string_sort_requires_native_source_bytes_but_single_row_safe(self):
        game = controller()
        game.select_club(1)
        two = deliver_source_records(game, (1, 2))
        # Source EAMPlayerAskTransferListsub +0x18 = 0x56FB70 always
        # reads original EnglishEAM.idx ordinal1313: all title strings
        # are exactly "Transfer List", so strict sort3 is always tied.
        by_title = original_initial_transfer_eam_sorted_window(
            two, filter_index=1, sort_index=3,
        )
        self.assertEqual(by_title.native_comparator_va, 0x472C00)
        self.assertEqual(by_title.original_sorted_rows, two)
        # Native record +0x1C resolves a player-specific typed descriptor;
        # comparator2 is NOT qualified to compare two distinct players.
        with self.assertRaisesRegex(OriginalEAMailFilterSourceError, "player-specific"):
            original_initial_transfer_eam_sorted_window(
                two, filter_index=1, sort_index=2,
            )
        for index in (2, 3):
            # Filter 2 selects no category5 messages: no comparison made.
            self.assertEqual(
                original_initial_transfer_eam_sorted_window(
                    two, filter_index=2, sort_index=index,
                ).original_sorted_rows, (),
            )
        for bad in (-1, 5, "4", True):
            with self.assertRaises(OriginalEAMailFilterSourceError):
                original_initial_transfer_eam_sorted_window(
                    two, filter_index=1, sort_index=bad,
                )
        with self.assertRaisesRegex(ValueError, "offset"):
            original_initial_transfer_eam_sorted_window(
                two, filter_index=1, sort_index=4, scroll_offset=1,
            )

    def test_selected_manager_only_and_no_early_pending_delivery(self):
        game = controller()
        game.select_club(1)
        state = game.state
        registered = state.original_delivered_mailboxes
        registered.register_source_user(1)
        other = PlayerTransferRequest(
            player_id=2000, queued_on=DAY, due_on=DAY+timedelta(days=1),
            recipient_manager_key=1, sender_club_id=2,
        )
        registered.deliver_source_ready_transfer_request(
            other, pending_identity="other-user-event",
            at_date=other.due_on, original_record_ready=True,
        )
        pending = PlayerTransferRequest(
            player_id=3000, queued_on=DAY, due_on=DAY+timedelta(days=1),
            recipient_manager_key=0, sender_club_id=1,
        )
        state.player_transfer_requests.append(pending)
        selected = ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()
        self.assertEqual(selected, ())
        self.assertEqual(original_initial_transfer_eam_sorted_window(
            selected, filter_index=1, sort_index=4,
        ).original_sorted_rows, ())
        self.assertEqual(len(registered.delivered_for_manager(1)), 1)


if __name__ == "__main__":
    main()
