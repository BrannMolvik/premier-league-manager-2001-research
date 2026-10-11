"""Original DBRUser+0x6B4 delivered-mail owner; no native UI acceptance.

Synthetic source-shaped records; the authorized proprietary original executable
is NEVER included or run in hosted CI. Original lifecycle source is captured in
research/GATE13_EAMAIL_DELIVERY_LIST_VS_IMMEDIATE_MODAL_AUDIT_RECOVERY451.md
and GATE13_MPMEAMAIL_DELAYED_DELIVERY_NEXT_PIPELINE_AUDIT_RECOVERY452.md.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import date, timedelta
import copy
import unittest

from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import (
    dumps_human_gameplay,
    loads_human_gameplay,
    snapshot_human_gameplay,
    restore_human_gameplay,
)
from match_postmatch import PlayerTransferRequest
from original_eamail_mailbox import (
    OriginalDeliveredEAMail,
    OriginalDeliveredEAMailboxes,
    OriginalEAMailOwnerError,
    EAM_PLAYER_ASK_TRANSFER_LIST_CLASS,
    EAM_PLAYER_ASK_TRANSFER_LIST_TYPEDESC_VA,
    EAM_PLAYER_ASK_TRANSFER_LIST_COL_VA,
    EAM_PLAYER_ASK_TRANSFER_LIST_VFTABLE_VA,
    EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VIRTUAL_OFFSET,
    EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VA,
    EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VIRTUAL_OFFSET,
    EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VA,
    EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_NATIVE_DATE_UNITS,
    source_player_ask_transfer_list_record_ready,
    source_known_eam_record_retained,
)
from test_human_gameplay import Database, coefficient_matrix
from match_schedule import MsvcCrtRng


DAY = date(2000, 7, 2)


def event(player=1000, recipient=0, sender=1, due=DAY):
    return PlayerTransferRequest(
        player_id=player, queued_on=due-timedelta(days=1),
        due_on=due, recipient_manager_key=recipient, sender_club_id=sender,
    )


class DeliveredEAMailOwnerTests(unittest.TestCase):
    def test_registered_user_mailboxes_are_empty_and_append_per_owner_only(self):
        registry = OriginalDeliveredEAMailboxes()
        registry.register_source_user(0)
        registry.register_source_user(195)
        self.assertEqual(registry.delivered_for_manager(0), ())
        self.assertEqual(registry.delivered_for_manager(195), ())

        first = registry.deliver_source_ready_transfer_request(
            event(1000, 0), pending_identity="event0",
            at_date=DAY, original_record_ready=True,
        )
        self.assertIsInstance(first, OriginalDeliveredEAMail)
        self.assertEqual(first.node_serial, 1)
        self.assertEqual(first.recipient_manager_key, 0)
        self.assertEqual(first.record_date, DAY)
        self.assertFalse(first.native_status_decoded)
        self.assertFalse(first.original_screen_rendered)
        self.assertEqual(registry.delivered_for_manager(195), ())

        second = registry.deliver_source_ready_transfer_request(
            event(1001, 0), pending_identity="event1",
            at_date=DAY+timedelta(days=2), original_record_ready=True,
        )
        third = registry.deliver_source_ready_transfer_request(
            event(1002, 195), pending_identity="event2",
            at_date=DAY+timedelta(days=3), original_record_ready=True,
        )
        self.assertEqual((first.node_serial, second.node_serial, third.node_serial),
                         (1, 2, 3))
        self.assertEqual([r.player_id for r in registry.delivered_for_manager(0)],
                         [1000, 1001])
        self.assertEqual([r.player_id for r in registry.delivered_for_manager(195)],
                         [1002])

    def test_explicit_readiness_and_original_due_gate_do_not_consume_pending(self):
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        request = event()
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "not yet due"):
            inbox.deliver_source_ready_transfer_request(
                request, pending_identity="future", at_date=DAY-timedelta(days=1),
                original_record_ready=True,
            )
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "readiness"):
            inbox.deliver_source_ready_transfer_request(
                request, pending_identity="unknown", at_date=DAY,
                original_record_ready=None,
            )
        self.assertIsNone(inbox.deliver_source_ready_transfer_request(
            request, pending_identity="false", at_date=DAY,
            original_record_ready=False,
        ))
        self.assertEqual(inbox.delivered_for_manager(0), ())
        self.assertEqual(inbox.next_node_serial, 1)
        first = inbox.deliver_source_ready_transfer_request(
            request, pending_identity="accepted", at_date=DAY,
            original_record_ready=True,
        )
        self.assertEqual(first.record_date, request.due_on)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "twice"):
            inbox.deliver_source_ready_transfer_request(
                request, pending_identity="accepted",
                at_date=DAY+timedelta(days=1), original_record_ready=True,
            )
        self.assertEqual(inbox.delivered_for_manager(0), (first,))

    def test_captured_recipient_never_uses_current_human_or_imported_manager(self):
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        inbox.register_source_user(195)
        captured = event(1000, 0, sender=9)
        first = inbox.deliver_source_ready_transfer_request(
            captured, pending_identity="loaned", at_date=DAY,
            original_record_ready=True,
        )
        self.assertEqual(first.sender_club_id, 9)
        self.assertEqual([r.recipient_manager_key for r in inbox.delivered_for_manager(0)],
                         [0])
        self.assertEqual(inbox.delivered_for_manager(195), ())
        self.assertIsNone(inbox.deliver_source_ready_transfer_request(
            event(1001, recipient=777),
            pending_identity="unregistered", at_date=DAY, original_record_ready=True,
        ))
        self.assertEqual(inbox.next_node_serial, 2)

    def test_missing_original_envelope_context_is_not_fabricated(self):
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        for bad in (
            PlayerTransferRequest(1000, DAY, DAY),
            PlayerTransferRequest(1000, DAY, DAY, recipient_manager_key=None,
                                  sender_club_id=None),
        ):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(OriginalEAMailOwnerError,
                                            "recipient/sender"):
                    inbox.deliver_source_ready_transfer_request(
                        bad, pending_identity="event", at_date=DAY,
                        original_record_ready=True,
                    )
        self.assertEqual(inbox.delivered_for_manager(0), ())

    def test_status_and_original_raster_capability_cannot_be_promoted(self):
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        rec = inbox.deliver_source_ready_transfer_request(
            event(), pending_identity="true", at_date=DAY,
            original_record_ready=True,
        )
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "unknown status"):
            replace(rec, native_status_decoded=True)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "native GUI"):
            replace(rec, original_screen_rendered=True)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "Only original"):
            replace(rec, event_class="EAMChairSeasonTicketssub")

    def test_multiuser_registration_and_node_identity_corruption_refused(self):
        inbox = OriginalDeliveredEAMailboxes()
        for manager in range(6):
            inbox.register_source_user(manager)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "Maximum six"):
            inbox.register_source_user(6)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "already registered"):
            inbox.register_source_user(0)
        with self.assertRaises(OriginalEAMailOwnerError):
            inbox.delivered_for_manager(6)
        row = inbox.deliver_source_ready_transfer_request(
            event(), pending_identity="source-a",
            at_date=DAY, original_record_ready=True,
        )
        bad = inbox.snapshot()
        bad["mailboxes"][0]["records"].append(copy.deepcopy(bad["mailboxes"][0]["records"][0]))
        with self.assertRaises(OriginalEAMailOwnerError):
            OriginalDeliveredEAMailboxes.restore(bad)
        self.assertEqual(inbox.delivered_for_manager(0), (row,))

    def test_native_transfer_readiness_and_exact_retention_without_due_dispatch(self):
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_CLASS, "EAMPlayerAskTransferListsub")
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_TYPEDESC_VA, 0x818F40)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_COL_VA, 0x7DF7C8)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_VFTABLE_VA, 0x7BDB1C)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VIRTUAL_OFFSET, 0x3C)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_READINESS_VA, 0x4093E0)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VIRTUAL_OFFSET, 0x40)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_VA, 0x470CE0)
        self.assertEqual(EAM_PLAYER_ASK_TRANSFER_LIST_RETENTION_NATIVE_DATE_UNITS, 365)
        self.assertTrue(source_player_ask_transfer_list_record_ready(event().event_class))
        for unsupported in ("EAMChairSeasonTicketssub", "MPMEAMail", "", None):
            with self.subTest(unsupported=unsupported):
                with self.assertRaisesRegex(OriginalEAMailOwnerError, "Only verified"):
                    source_player_ask_transfer_list_record_ready(unsupported)
        # A native ready response is NOT the scheduled envelope's date gate.
        pending = event()
        mailbox = OriginalDeliveredEAMailboxes()
        mailbox.register_source_user(0)
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "not yet due"):
            mailbox.deliver_source_ready_transfer_request(
                pending, pending_identity="not-due", at_date=DAY-timedelta(days=1),
                original_record_ready=source_player_ask_transfer_list_record_ready(
                    pending.event_class),
            )
        self.assertEqual(mailbox.delivered_for_manager(0), ())

        for kind, offset in (
            (EAM_PLAYER_ASK_TRANSFER_LIST_CLASS, 365),
            ("EAMChairSeasonTicketssub", 365),
            ("EAMChairSeasonTicketSetsub", 21),
        ):
            with self.subTest(kind=kind):
                self.assertTrue(source_known_eam_record_retained(
                    kind, source_record_day=500, source_current_day=500+offset,
                ))
                self.assertFalse(source_known_eam_record_retained(
                    kind, source_record_day=500, source_current_day=501+offset,
                ))
        with self.assertRaisesRegex(OriginalEAMailOwnerError, "No original"):
            source_known_eam_record_retained(
                "UnverifiedEAMClass",
                source_record_day=500, source_current_day=501,
            )
        for wrong in (True, "500", -1, 500.0):
            with self.subTest(wrong=wrong):
                with self.assertRaises(OriginalEAMailOwnerError):
                    source_known_eam_record_retained(
                        "EAMChairSeasonTicketssub",
                        source_record_day=wrong, source_current_day=501,
                    )

    def test_internal_save_roundtrip_retains_real_mail_nodes_separately_from_pending(self):
        state = GameState.from_database(Database(), date(2000, 6, 30), seed=1, season_year=2000)
        game = HumanGameplayController(
            state, coefficient_matrix(), coefficient_matrix(), MsvcCrtRng(1),
        )
        game.select_club(1)
        first_key, second_key = sorted(state.managers)[:2]
        state.original_delivered_mailboxes.register_source_user(first_key)
        state.original_delivered_mailboxes.register_source_user(second_key)
        due = event(1000, first_key, sender=1)
        future = event(1001, second_key, sender=2,
                       due=DAY+timedelta(days=8))
        state.player_transfer_requests.extend((due, future))
        before = tuple(state.player_transfer_requests)
        delivered = state.original_delivered_mailboxes.deliver_source_ready_transfer_request(
            due, pending_identity="real-source-envelope",
            at_date=DAY, original_record_ready=True,
        )
        saved = snapshot_human_gameplay(game)
        self.assertEqual(
            saved["game_state"]["original_delivered_mailboxes"]["next_node_serial"], 2
        )
        restored = loads_human_gameplay(
            Database(), coefficient_matrix(), coefficient_matrix(),
            dumps_human_gameplay(game),
        )
        self.assertEqual(restored.state.player_transfer_requests, list(before))
        self.assertEqual(
            restored.state.original_delivered_mailboxes.delivered_for_manager(first_key),
            (delivered,),
        )
        self.assertEqual(
            restored.state.original_delivered_mailboxes.delivered_for_manager(second_key), ())
        self.assertEqual(restored.state.original_delivered_mailboxes.next_node_serial, 2)
        self.assertEqual(snapshot_human_gameplay(restored), saved)

        # Schema-48 files produced before the optional source-owned mailbox
        # existed are interpreted as EMPTY, never pending==delivered.
        old = copy.deepcopy(saved)
        del old["game_state"]["original_delivered_mailboxes"]
        legacy = restore_human_gameplay(
            Database(), coefficient_matrix(), coefficient_matrix(), old,
        )
        self.assertEqual(legacy.state.player_transfer_requests, list(before))
        self.assertEqual(legacy.state.original_delivered_mailboxes.registered_manager_keys, ())
        self.assertEqual(legacy.state.original_delivered_mailboxes.mailboxes, {})

    def test_malformed_saved_owner_and_owner_reorder_fail_closed(self):
        inbox = OriginalDeliveredEAMailboxes()
        inbox.register_source_user(0)
        inbox.register_source_user(1)
        inbox.deliver_source_ready_transfer_request(
            event(), pending_identity="a", at_date=DAY, original_record_ready=True,
        )
        base = inbox.snapshot()
        for modify in (
            lambda x: x.update(next_node_serial=1),
            lambda x: x.update(registered_manager_keys=[0, 0]),
            lambda x: x["mailboxes"][0].update(manager_key=1),
            lambda x: x["mailboxes"][0]["records"][0].update(recipient_manager_key=1),
            lambda x: x["mailboxes"][0]["records"][0].update(event_class="fabricated"),
            lambda x: x["mailboxes"][0]["records"][0].update(node_serial=True),
            lambda x: x["mailboxes"][0]["records"][0].update(record_date="bad date"),
        ):
            with self.subTest(modify=modify):
                bad = copy.deepcopy(base)
                modify(bad)
                with self.assertRaises((OriginalEAMailOwnerError, ValueError)):
                    OriginalDeliveredEAMailboxes.restore(bad)


if __name__ == "__main__":
    unittest.main()
