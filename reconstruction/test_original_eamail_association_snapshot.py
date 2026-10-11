"""Producer-time original EAM +0x72 signed-word owner and save lifecycle.

Synthetic inputs model independently traced native 0x417700/0x5CE660/0x41B61E.
Tests do NOT infer current player.club_id as the native association, prove
production integration, paint a row, or run the private original executable.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
import copy
import unittest

from match_postmatch import PlayerTransferRequest
from original_eamail_mailbox import (
    OriginalDeliveredEAMailboxes, OriginalEAMailOwnerError,
)
from original_eamail_pending import (
    OriginalPendingTransferEAMQueue, OriginalPendingEAMSourceError,
)

CREATED = date(2000, 6, 30)
DUE = CREATED + timedelta(days=1)


def source_explicit(word):
    """Only the CALLER can supply an independently qualified native word."""
    return PlayerTransferRequest(
        player_id=1000, queued_on=CREATED, due_on=DUE,
        recipient_manager_key=4, sender_club_id=12,
        verified_native_association_word_at_creation=word,
    )


class ProducerTimeNativeAssociationTests(unittest.TestCase):
    def test_signed_word_contract_and_no_live_inference(self):
        for word in (-32768, -42, -1, 0, 12, 32767):
            self.assertEqual(source_explicit(word).
                             verified_native_association_word_at_creation, word)
        for word in (-32769, 32768, 65535, 1.0, True, "12", [], {}):
            with self.subTest(word=word):
                with self.assertRaisesRegex(ValueError, "signed 16-bit"):
                    source_explicit(word)
        unresolved = PlayerTransferRequest(
            player_id=1000, queued_on=CREATED, due_on=DUE,
            recipient_manager_key=4, sender_club_id=12,
        )
        # Sender identity alone cannot source-qualify typed descriptor+8.
        self.assertIsNone(unresolved.verified_native_association_word_at_creation)
        self.assertIsNone(replace(unresolved, sender_club_id=99).
                          verified_native_association_word_at_creation)

    def test_pending_delivery_preserves_producer_snapshot_after_club_changes(self):
        class MutablePlayer:
            club_id = 12
            loan_club_id = None

        live = MutablePlayer()
        pending = OriginalPendingTransferEAMQueue()
        envelope = pending.append_original_transfer(source_explicit(12))
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(4)
        # Native text must use descriptor+8 captured above, not today's
        # player, effective loan club or mailbox delivery-time sender.
        live.club_id = 83
        live.loan_club_id = 99
        self.assertEqual(pending.process_original_due(CREATED, inbox), ())
        self.assertEqual(pending.entries[0].request.
                         verified_native_association_word_at_creation, 12)
        self.assertEqual(pending.process_original_due(DUE, inbox),
                         (envelope.identity,))
        delivered = inbox.delivered_for_manager(4)[0]
        self.assertEqual(delivered.verified_native_association_word_at_creation, 12)
        self.assertEqual(delivered.sender_club_id, 12)
        self.assertNotEqual(delivered.verified_native_association_word_at_creation,
                            live.loan_club_id)
        self.assertEqual(pending.entries, [])

    def test_optional_word_roundtrip_legacy_and_corruption_fail_closed(self):
        for word in (12, -1, -32768, 0, None):
            with self.subTest(word=word):
                pending = OriginalPendingTransferEAMQueue()
                pending.append_original_transfer(source_explicit(word))
                snap = pending.snapshot()
                entry = snap["entries"][0]
                if word is None:
                    self.assertNotIn("verified_native_association_word_at_creation", entry)
                else:
                    self.assertEqual(
                        entry["verified_native_association_word_at_creation"], word)
                loaded = OriginalPendingTransferEAMQueue.restore(snap)
                self.assertEqual(loaded.snapshot(), snap)
                inbox = OriginalDeliveredEAMailboxes()
                inbox.register_source_user(4)
                loaded.process_original_due(DUE, inbox)
                mail_snap = inbox.snapshot()
                restored = OriginalDeliveredEAMailboxes.restore(mail_snap)
                self.assertEqual(restored.snapshot(), mail_snap)
                self.assertEqual(
                    restored.delivered_for_manager(4)[0].
                    verified_native_association_word_at_creation, word)

        legacy = OriginalPendingTransferEAMQueue()
        legacy.append_original_transfer(source_explicit(None))
        old = legacy.snapshot()
        self.assertNotIn("verified_native_association_word_at_creation",
                         old["entries"][0])
        self.assertIsNone(OriginalPendingTransferEAMQueue.restore(old)
                          .entries[0].request.verified_native_association_word_at_creation)
        bad_pending = copy.deepcopy(legacy.snapshot())
        bad_pending["entries"][0]["verified_native_association_word_at_creation"] = 65535
        with self.assertRaises((ValueError, OriginalPendingEAMSourceError)):
            OriginalPendingTransferEAMQueue.restore(bad_pending)
        bad_pending = copy.deepcopy(legacy.snapshot())
        bad_pending["entries"][0]["unexpected_key"] = True
        with self.assertRaises(OriginalPendingEAMSourceError):
            OriginalPendingTransferEAMQueue.restore(bad_pending)

        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(4)
        inbox.deliver_source_ready_transfer_request(
            source_explicit(None), pending_identity="native:1",
            at_date=DUE, original_record_ready=True,
        )
        bad_mail = inbox.snapshot()
        bad_mail["mailboxes"][0]["records"][0][
            "verified_native_association_word_at_creation"] = True
        with self.assertRaises(OriginalEAMailOwnerError):
            OriginalDeliveredEAMailboxes.restore(bad_mail)


if __name__ == "__main__":
    unittest.main()
