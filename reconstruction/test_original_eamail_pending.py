"""Original MPMEAMail transfer-envelope lifecycle regression tests.

No private original executable or game asset is needed in CI; source code
owners and their bytes were verified privately before these source cases.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
import unittest

from game_state import GameState
from match_postmatch import PlayerTransferRequest
from original_eamail_mailbox import OriginalDeliveredEAMailboxes, OriginalEAMailOwnerError
from original_eamail_pending import (
    OriginalPendingEAMSourceError,
    OriginalPendingTransferEAMQueue,
)
from test_human_gameplay import Database


START = date(2000, 6, 30)
DUE = START + timedelta(days=1)


def source_transfer(player=1000, recipient=0, sender=5, due=DUE):
    return PlayerTransferRequest(
        player_id=player, queued_on=due-timedelta(days=1), due_on=due,
        recipient_manager_key=recipient, sender_club_id=sender,
    )


class OriginalPendingEAMTests(unittest.TestCase):
    def test_source_queue_retains_next_day_envelope_until_due_and_consumes_once(self):
        pending = OriginalPendingTransferEAMQueue()
        a = pending.append_original_transfer(source_transfer(1000, 0))
        b = pending.append_original_transfer(source_transfer(1001, 1))
        self.assertEqual((a.sequence, b.sequence), (1, 2))
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        inbox.register_source_user(1)
        self.assertEqual(pending.process_original_due(START, inbox), ())
        self.assertEqual(inbox.delivered_for_manager(0), ())
        self.assertEqual(tuple(row.identity for row in pending.entries),
                         (a.identity, b.identity))
        self.assertEqual(pending.process_original_due(DUE, inbox),
                         (a.identity, b.identity))
        self.assertEqual(tuple(row.player_id for row in inbox.delivered_for_manager(0)), (1000,))
        self.assertEqual(tuple(row.player_id for row in inbox.delivered_for_manager(1)), (1001,))
        self.assertEqual(inbox.delivered_for_manager(0)[0].record_date, DUE)
        self.assertEqual(pending.entries, [])
        self.assertEqual(pending.process_original_due(DUE, inbox), ())
        self.assertEqual(inbox.next_node_serial, 3)

    def test_due_without_registered_recipient_still_consumes_native_queue_node(self):
        pending = OriginalPendingTransferEAMQueue()
        event = pending.append_original_transfer(source_transfer(1001, 195))
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        self.assertEqual(pending.process_original_due(DUE, inbox), (event.identity,))
        self.assertEqual(pending.entries, [])
        self.assertEqual(inbox.delivered_for_manager(0), ())
        self.assertEqual(inbox.next_node_serial, 1)

    def test_no_early_delivery_no_implicit_source_context_and_no_generic_family(self):
        pending = OriginalPendingTransferEAMQueue()
        with self.assertRaisesRegex(OriginalPendingEAMSourceError, "recipient"):
            pending.append_original_transfer(PlayerTransferRequest(
                player_id=1, queued_on=START, due_on=DUE))
        with self.assertRaisesRegex(OriginalPendingEAMSourceError, "next-day"):
            pending.append_original_transfer(PlayerTransferRequest(
                player_id=1, queued_on=START, due_on=DUE+timedelta(days=1),
                recipient_manager_key=0, sender_club_id=5))
        self.assertEqual(pending.entries, [])
        self.assertEqual(pending.next_sequence, 1)

    def test_queue_snapshot_roundtrip_identity_purge_and_strict_restore(self):
        pending = OriginalPendingTransferEAMQueue()
        first = pending.append_original_transfer(source_transfer(7))
        second = pending.append_original_transfer(source_transfer(8))
        snap = pending.snapshot()
        restored = OriginalPendingTransferEAMQueue.restore(snap)
        self.assertEqual(restored.snapshot(), snap)
        self.assertEqual((first.identity, second.identity),
                         tuple(node.identity for node in restored.entries))
        restored.remove_player_linked(7)
        self.assertEqual(tuple(node.identity for node in restored.entries), (second.identity,))
        self.assertEqual(restored.append_original_transfer(source_transfer(9)).sequence, 3)
        self.assertEqual(OriginalPendingTransferEAMQueue.restore(None).entries, [])
        for malformed in (
            {"next_sequence": 1, "entries": [snap["entries"][0]]},
            {"next_sequence": 3, "entries": [snap["entries"][1], snap["entries"][0]]},
            {"next_sequence": "3", "entries": []},
            {"next_sequence": 2, "entries": [{"player_id": 7}]},
        ):
            with self.assertRaises((OriginalPendingEAMSourceError, ValueError)):
                OriginalPendingTransferEAMQueue.restore(malformed)

    def test_actual_game_state_source_producer_due_delivery_and_refusal_atomicity(self):
        state = GameState.from_database(Database(), START, seed=1, season_year=2000)
        player = next(iter(state.players.values()))
        active = (player.club_id if player.loan_club_id is None else player.loan_club_id)
        state.user_controlled_club_id = int(active)
        state.native_user_recipient_key = 0
        state.original_delivered_mailboxes.register_source_user(0)
        request = PlayerTransferRequest(
            player_id=player.index, queued_on=START, due_on=DUE,
        )
        state._retain_player_transfer_request(request)
        self.assertEqual(len(state.player_transfer_requests), 1)
        self.assertEqual(len(state.original_pending_transfer_eam.entries), 1)
        qualified = state.original_pending_transfer_eam.entries[0]
        self.assertEqual(qualified.request.recipient_manager_key, 0)
        self.assertEqual(qualified.request.sender_club_id, active)
        self.assertEqual(state.process_original_eam_due_events(START), ())
        self.assertEqual(state.original_delivered_mailboxes.delivered_for_manager(0), ())
        self.assertEqual(state.process_original_eam_due_events(DUE), (qualified.identity,))
        self.assertEqual(state.original_delivered_mailboxes.delivered_for_manager(0)[0].player_id,
                         player.index)
        self.assertEqual(state.original_pending_transfer_eam.entries, [])
        self.assertEqual(len(state.player_transfer_requests), 1)  # action request != MPM
        self.assertEqual(state.process_original_eam_due_events(DUE), ())

        # Duplicate delivered ID is a rejected reprocessing, never a partially
        # published queue or mailbox mutation on the real GameState object.
        state.original_pending_transfer_eam.append_original_transfer(
            qualified.request
        )
        duplicate = state.original_pending_transfer_eam.entries[0]
        state.original_delivered_mailboxes.deliver_source_ready_transfer_request(
            duplicate.request, pending_identity=duplicate.identity,
            at_date=DUE, original_record_ready=True,
        )
        before_queue = deepcopy(state.original_pending_transfer_eam.snapshot())
        before_mail = deepcopy(state.original_delivered_mailboxes.snapshot())
        with self.assertRaises(OriginalEAMailOwnerError):
            state.process_original_eam_due_events(DUE)
        self.assertEqual(state.original_pending_transfer_eam.snapshot(), before_queue)
        self.assertEqual(state.original_delivered_mailboxes.snapshot(), before_mail)


if __name__ == "__main__":
    unittest.main()
