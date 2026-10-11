"""Bound original TeamSelect DBRUser mailbox and read-only manager owner.

Source scope: original 0x424E2E user+0x6B4 constructor and runtime
0x426090/0x4151C0 effective manager key; 0x413020 delivery. Not a GUI,
native double-click, exact message text, physical Win11 or NEXT test.
"""
from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace as Obj
from unittest import TestCase, main

from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import dumps_human_gameplay, loads_human_gameplay
from gate13_management_source_data import (
    ManagementPresentationError, ManagementSourceDataBridge,
)
from match_postmatch import PlayerTransferRequest
from match_schedule import MsvcCrtRng
from test_human_gameplay import Database, coefficient_matrix


class OriginalManagerMailDatabase(Database):
    # Only the manager first-name source identity needed for the native 4151C0
    # unused '!Spare' predicate is supplemented; no fictional email content.
    managers = tuple(
        Obj(
            index=i, first_name="!Spare" if i == 0 else "Manager",
            formation_default=0, formation_class3=2, formation_class1=1,
        )
        for i in range(21)
    )


def controller(database=OriginalManagerMailDatabase):
    state = GameState.from_database(
        database(), date(2000, 6, 30), seed=1, season_year=2000,
    )
    game = HumanGameplayController(
        state, coefficient_matrix(), coefficient_matrix(), MsvcCrtRng(1),
    )
    return game


class OriginalLiveManagerMailboxBridgeTests(TestCase):
    def test_fresh_human_registers_empty_original_user_mailbox(self):
        game = controller()
        self.assertEqual(game.state.original_delivered_mailboxes.registered_manager_keys, ())
        original_ai_manager = game.state.clubs[1].manager_id
        rng_before = game.state.rng.state
        game.select_club(1)
        self.assertEqual(game.state.native_user_recipient_key, 0)
        self.assertEqual(game.state.clubs[1].manager_id, original_ai_manager)
        self.assertEqual(game.state.rng.state, rng_before)
        owner = game.state.original_delivered_mailboxes
        self.assertEqual(owner.registered_manager_keys, (0,))
        self.assertEqual(owner.delivered_for_manager(0), ())
        self.assertEqual(owner.next_node_serial, 1)
        self.assertEqual(
            ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user(), ()
        )

    def test_current_manager_reads_only_delivered_not_future_pending_or_other_user(self):
        game = controller()
        game.select_club(1)
        source = ManagementSourceDataBridge(game)
        source_owner = game.state.original_delivered_mailboxes
        source_owner.register_source_user(1)
        pending = PlayerTransferRequest(
            player_id=1000, queued_on=date(2000, 7, 1),
            due_on=date(2000, 7, 2), recipient_manager_key=0,
            sender_club_id=1,
        )
        future = PlayerTransferRequest(
            player_id=1001, queued_on=date(2000, 7, 1),
            due_on=date(2000, 7, 10), recipient_manager_key=0,
            sender_club_id=1,
        )
        other_manager = PlayerTransferRequest(
            player_id=1002, queued_on=date(2000, 7, 1),
            due_on=date(2000, 7, 2), recipient_manager_key=1,
            sender_club_id=2,
        )
        game.state.player_transfer_requests.extend((pending, future, other_manager))
        self.assertEqual(source.source_delivered_mailbox_for_selected_user(), ())
        first = source_owner.deliver_source_ready_transfer_request(
            pending, pending_identity="source-envelope-0",
            at_date=pending.due_on, original_record_ready=True,
        )
        second = source_owner.deliver_source_ready_transfer_request(
            other_manager, pending_identity="source-envelope-1",
            at_date=other_manager.due_on, original_record_ready=True,
        )
        self.assertEqual(source.source_delivered_mailbox_for_selected_user(), (first,))
        self.assertEqual(source_owner.delivered_for_manager(1), (second,))
        self.assertEqual(tuple(game.state.player_transfer_requests),
                         (pending, future, other_manager))
        self.assertEqual(first.recipient_manager_key, 0)
        self.assertEqual(first.sender_club_id, 1)
        self.assertEqual(second.recipient_manager_key, 1)
        self.assertNotEqual(first.node_serial, second.node_serial)

        saved = dumps_human_gameplay(game)
        restored = loads_human_gameplay(
            OriginalManagerMailDatabase(), coefficient_matrix(),
            coefficient_matrix(), saved,
        )
        self.assertEqual(
            ManagementSourceDataBridge(restored).source_delivered_mailbox_for_selected_user(),
            (first,),
        )
        self.assertEqual(
            restored.state.original_delivered_mailboxes.delivered_for_manager(1), (second,),
        )
        self.assertEqual(
            tuple(restored.state.player_transfer_requests),
            (pending, future, other_manager),
        )

    def test_unknown_or_missing_native_user_recipient_never_falls_back_to_ai_manager(self):
        game = controller(Database)
        game.select_club(1)
        self.assertIsNone(game.state.native_user_recipient_key)
        self.assertEqual(game.state.original_delivered_mailboxes.registered_manager_keys, ())
        with self.assertRaisesRegex(ManagementPresentationError, "unverified"):
            ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()
        self.assertTrue(game.state.clubs[1].manager_id >= 0)

    def test_unregistered_live_manager_cannot_borrow_another_mailbox(self):
        game = controller()
        game.select_club(1)
        game.state.original_delivered_mailboxes.mailboxes.clear()
        game.state.original_delivered_mailboxes.registered_manager_keys = ()
        with self.assertRaisesRegex(ManagementPresentationError, "no source-registered"):
            ManagementSourceDataBridge(game).source_delivered_mailbox_for_selected_user()

    def test_read_only_snapshot_does_not_reorder_or_erase_user_nodes(self):
        game = controller()
        game.select_club(1)
        source = ManagementSourceDataBridge(game)
        owner = game.state.original_delivered_mailboxes
        first = PlayerTransferRequest(
            1000, date(2000, 7, 1), date(2000, 7, 2), 0, 1,
        )
        second = PlayerTransferRequest(
            1001, date(2000, 7, 2), date(2000, 7, 3), 0, 1,
        )
        records = tuple(
            owner.deliver_source_ready_transfer_request(
                request, pending_identity=f"event-{i}",
                at_date=request.due_on, original_record_ready=True,
            )
            for i, request in enumerate((first, second))
        )
        before = owner.snapshot()
        self.assertEqual(source.source_delivered_mailbox_for_selected_user(), records)
        self.assertEqual(source.source_delivered_mailbox_for_selected_user(), records)
        self.assertEqual(owner.snapshot(), before)
        self.assertEqual(tuple(item.node_serial for item in records), (1, 2))


if __name__ == "__main__":
    main()
