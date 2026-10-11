"""Recovery533: native EAM kind2 player/club text through actual owner Inbox.

Tests use deterministic source-shaped fixtures and original English STR/IDX
bytes. No original graphical application launch or Win11 acceptance is claimed.
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from types import SimpleNamespace as Obj
from unittest import TestCase, main

from gate13_management_source_data import ManagementPresentationError, ManagementSourceDataBridge
from match_postmatch import PlayerTransferRequest
from original_eamail_native_row_fields import build_selected_user_original_eam_source_rows
from test_original_eamail_live_user_bridge import controller


SOURCE_ROOT = Path(__file__).resolve().parent.parent / "original_assets" / "source"
DAY = date(2000, 8, 1)


def human_with_source_short_name():
    game = controller()
    game.select_club(1)
    original = game.state.clubs[1]
    # Source-shaped Master.dat identities. The full and short names are
    # deliberately different to detect the original +0x08/+0x0C mixup.
    game.state.clubs[1] = Obj(
        **vars(original), name="Example Original Full Club",
        short_name="ExampleShort",
    )
    return game


def deliver(game, *, word, player_id=1000, recipient=0, identity="source:1"):
    request = PlayerTransferRequest(
        player_id=player_id, queued_on=DAY-timedelta(days=1), due_on=DAY,
        recipient_manager_key=recipient, sender_club_id=1,
        verified_native_association_word_at_creation=word,
    )
    return game.state.original_delivered_mailboxes.deliver_source_ready_transfer_request(
        request, pending_identity=identity, at_date=DAY, original_record_ready=True,
    )


def source_rows(game):
    return build_selected_user_original_eam_source_rows(
        ManagementSourceDataBridge(game), original_source_root=SOURCE_ROOT,
        filter_index=5, sort_index=3,
    )


class OriginalEAMPlayerClubRowIntegrationTests(TestCase):
    def test_real_user_delivered_source_player_and_original_short_club(self):
        game = human_with_source_short_name()
        delivered = deliver(game, word=1)
        before = game.state.original_delivered_mailboxes.snapshot()
        rows = source_rows(game)
        self.assertEqual(rows.original_filtered_count, 1)
        self.assertEqual(rows.native_rows[0].original_internal_node_serial,
                         delivered.node_serial)
        self.assertEqual(tuple(
            field.source_verified_visible_text
            for field in rows.native_rows[0].original_text_fields
        ), (
            "<T+P>T. Player<T-> @ <T+C>ExampleShort Football Club<T->",
            "Transfer List", "1/Aug/2000",
        ))
        self.assertEqual(game.state.original_delivered_mailboxes.snapshot(), before)
        self.assertFalse(rows.original_gui_accepted)

    def test_producer_snapshot_survives_live_club_loan_change_and_modern_save(self):
        from internal_save import dumps_human_gameplay, loads_human_gameplay
        from test_original_eamail_live_user_bridge import OriginalManagerMailDatabase
        from test_human_gameplay import coefficient_matrix

        game = human_with_source_short_name()
        deliver(game, word=1)
        # Original type2 association stays creation-time parent +0x72. Native
        # display still reads source player name at rendering time.
        p = game.state.players[1000]
        p.club_id = 2
        p.loan_club_id = 3
        assert "ExampleShort Football Club" in source_rows(game).native_rows[0].original_text_fields[0].source_verified_visible_text
        saved = dumps_human_gameplay(game)
        restored = loads_human_gameplay(
            OriginalManagerMailDatabase(), coefficient_matrix(),
            coefficient_matrix(), saved,
        )
        # Synthetic test names are not part of a canonical database. Restore
        # keeps association independent of the changed current player club.
        self.assertEqual(
            restored.state.original_delivered_mailboxes.delivered_for_manager(0)[0].
            verified_native_association_word_at_creation, 1,
        )

    def test_unknown_historical_association_remains_unrendered(self):
        game = human_with_source_short_name()
        deliver(game, word=None)
        rows = source_rows(game)
        self.assertIsNone(rows.native_rows[0].original_text_fields[0].
                          source_verified_visible_text)
        self.assertEqual(rows.native_rows[0].original_text_fields[1].
                         source_verified_visible_text, "Transfer List")

    def test_native_negative_player_descriptor_has_no_club_suffix(self):
        game = human_with_source_short_name()
        deliver(game, word=-1)
        rows = source_rows(game)
        self.assertEqual(rows.native_rows[0].original_text_fields[0].
                         source_verified_visible_text, "<T+P>T. Player<T->")

    def test_second_registered_human_alias_is_not_guessed(self):
        game = human_with_source_short_name()
        deliver(game, word=1)
        game.state.original_delivered_mailboxes.register_source_user(9)
        with self.assertRaisesRegex(ManagementPresentationError, "single-user"):
            source_rows(game)

    def test_missing_player_and_unauthorized_foreign_mail_fail_closed(self):
        game = human_with_source_short_name()
        deliver(game, word=1, player_id=999999)
        with self.assertRaisesRegex(ManagementPresentationError, "player no longer exists"):
            source_rows(game)
        game = human_with_source_short_name()
        game.state.original_delivered_mailboxes.register_source_user(9)
        deliver(game, word=1, recipient=9)
        self.assertEqual(source_rows(game).native_rows, ())


if __name__ == "__main__":
    main()
