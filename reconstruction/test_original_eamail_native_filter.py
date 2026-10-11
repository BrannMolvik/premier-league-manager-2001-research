"""Direct original ten-category EAMail filter proof on real manager mailbox.

No private source bytes; original constructor 0x56FAD0 status/category and
PEAMail 0x472680 predicates were independently verified from original EXE.
This is NOT complete native screen, sorting, or mouse acceptance.
"""
from __future__ import annotations

from datetime import date, timedelta
from unittest import TestCase, main

from game_state import GameState
from gate13_management_source_data import ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from original_eamail_native_filter import (
    OriginalEAMailFilterSourceError,
    ORIGINAL_EAMAIL_FIRST_STATUS_FILTER_BIT,
    ORIGINAL_EAMAIL_FILTER_OPTION_COUNT,
    ORIGINAL_TRANSFER_EAM_NATIVE_CATEGORY,
    ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS,
    original_filter_initial_transfer_mail,
)
from test_original_eamail_live_user_bridge import controller


START = date(2000, 7, 1)


class OriginalNativeTransferFilterTests(TestCase):
    def test_native_constructor_category_flags_and_ten_filter_predicates(self):
        self.assertEqual(ORIGINAL_EAMAIL_FILTER_OPTION_COUNT, 10)
        self.assertEqual(ORIGINAL_TRANSFER_EAM_NATIVE_CATEGORY, 5)
        self.assertEqual(ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS, 6)
        self.assertTrue(ORIGINAL_TRANSFER_EAM_NATIVE_INITIAL_FLAGS
                        & ORIGINAL_EAMAIL_FIRST_STATUS_FILTER_BIT)
        game = controller()
        game.select_club(1)
        mailbox = game.state.original_delivered_mailboxes
        # Source class/category is not fabricated for future MPM event input.
        player = next(p for p in game.state.players.values()
                      if p.club_id == 1 and p.loan_club_id is None)
        req = PlayerTransferRequest(
            player_id=player.index,
            queued_on=START, due_on=START+timedelta(days=1),
        )
        game.state._retain_player_transfer_request(req)
        bridge = ManagementSourceDataBridge(game)
        self.assertEqual(bridge.source_delivered_mailbox_for_selected_user(), ())
        game.state.process_original_eam_due_events(START)
        self.assertEqual(bridge.source_delivered_mailbox_for_selected_user(), ())
        game.state.process_original_eam_due_events(START+timedelta(days=1))
        actual = bridge.source_delivered_mailbox_for_selected_user()
        self.assertEqual(len(actual), 1)
        self.assertEqual(game.state.original_delivered_mailboxes.delivered_for_manager(0), actual)
        for index in range(10):
            result = original_filter_initial_transfer_mail(actual, index)
            self.assertEqual(result.selected_filter_index, index)
            self.assertEqual(result.source_delivered_count, 1)
            self.assertTrue(result.sort_and_native_gui_unverified)
            self.assertEqual(
                result.filtered_in_native_mailbox_order,
                actual if index in (0, 1, 5) else (),
            )
        # Viewing native filter candidates does not reorder/consume mailbox.
        self.assertEqual(bridge.source_delivered_mailbox_for_selected_user(), actual)
        self.assertEqual(game.state.original_pending_transfer_eam.entries, [])

    def test_source_delivery_order_is_preserved_before_unimplemented_native_sort(self):
        game = controller()
        game.select_club(1)
        source = game.state.original_delivered_mailboxes
        rows = ()
        for i in range(10):
            pending = PlayerTransferRequest(
                player_id=i+1, queued_on=START,
                due_on=START+timedelta(days=1),
                recipient_manager_key=0, sender_club_id=1,
            )
            source.deliver_source_ready_transfer_request(
                pending, pending_identity=f"source-envelope-{i}",
                at_date=pending.due_on, original_record_ready=True,
            )
        rows = ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()
        self.assertEqual(tuple(r.node_serial for r in rows), tuple(range(1, 11)))
        for index in (0, 1, 5):
            filtered = original_filter_initial_transfer_mail(rows, index)
            self.assertEqual(
                tuple(r.node_serial for r in filtered.filtered_in_native_mailbox_order),
                tuple(range(1, 11)),
            )
        self.assertEqual(source.snapshot()["next_node_serial"], 11)

    def test_reject_unknown_filter_index_non_source_rows_and_unbound_recipients(self):
        for bad_index in (-1, 10, True, 1.0, "1"):
            with self.assertRaises(OriginalEAMailFilterSourceError):
                original_filter_initial_transfer_mail((), bad_index)
        for invalid in ([1], (object(),), (None,), ({"event_class": "EAMPlayerAskTransferListsub"},)):
            with self.assertRaises(OriginalEAMailFilterSourceError):
                original_filter_initial_transfer_mail(invalid, 0)
        self.assertEqual(original_filter_initial_transfer_mail((), 0).source_delivered_count, 0)
        self.assertEqual(original_filter_initial_transfer_mail((), 5).filtered_in_native_mailbox_order, ())


if __name__ == "__main__":
    main()
