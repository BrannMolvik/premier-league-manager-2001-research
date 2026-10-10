"""Bounded native426090/41B63F ownership; not delivered-Inbox acceptance."""
import copy
from datetime import date
from types import SimpleNamespace
import unittest

from game_state import GameState
from human_gameplay import HumanGameplayController
from internal_save import dumps_human_gameplay, loads_human_gameplay, snapshot_human_gameplay, restore_human_gameplay
from match_postmatch import PlayerTransferRequest, maybe_queue_player_transfer_request
from match_schedule import MsvcCrtRng
from test_human_gameplay import Database, coefficient_matrix


class OriginalMailRecipientTests(unittest.TestCase):
    def controller(self):
        state = GameState.from_database(Database(), date(2000, 6, 30), seed=1, season_year=2000)
        return HumanGameplayController(state, coefficient_matrix(), coefficient_matrix(), MsvcCrtRng(1))

    def bind_names(self, state, names, old_key):
        state.clubs[1] = SimpleNamespace(index=1, manager_id=old_key)
        state.managers = {i: SimpleNamespace(index=i, first_name=name)
                          for i, name in enumerate(names)}
        state.bind_original_user_mail_recipient(1)

    def test_native_binding_vectors_not_club_or_imported_key(self):
        state = self.controller().state
        cases = (
            (['!', 'B', 'C', 'D'], 0xFFFFFFFF, 0),
            (['A', 'B', 'C', 'Old', 'D', '!', '!'], 3, 5),
            (['!', 'B', 'C', 'Old', 'D', '!', '!'], 3, 0),
            (['A', 'B', 'C', '!', 'D', '!', '!'], 3, 5),
            (['A', 'B', 'C', 'Old', 'D', '!!', '!'], 3, 5),
            (['A', 'B', 'C', 'Old', 'D', ' !', '!'], 3, 6),
            (['A', 'B', 'C', 'Old', 'D', 'E', 'F'], 3, 3),
        )
        for names, old, expected in cases:
            with self.subTest(names=names):
                self.bind_names(state, names, old)
                self.assertEqual(state.native_user_recipient_key, expected)
                self.assertEqual(state.clubs[1].manager_id, old)

    def test_missing_synthetic_manager_source_does_not_invent_key(self):
        controller = self.controller()
        controller.select_club(1)
        self.assertIsNone(controller.state.native_user_recipient_key)
        controller.state.native_user_recipient_key = 9
        controller.state.managers.pop(next(iter(controller.state.managers)))
        controller.state.bind_original_user_mail_recipient(1)
        self.assertIsNone(controller.state.native_user_recipient_key)

    def test_actual_select_club_binds_without_rng_draw(self):
        controller = self.controller()
        old = controller.state.clubs[1].manager_id
        controller.state.managers = {
            i: SimpleNamespace(**(manager.__dict__ | {'index': i}),
                               first_name=('Human' if i == old else '!Spare'))
            for i, manager in enumerate(controller.state.managers.values())}
        before = controller.state.rng.state
        controller.select_club(1)
        self.assertEqual(controller.state.native_user_recipient_key, next(i for i in range(len(controller.state.managers)) if i != old))
        self.assertEqual(controller.state.rng.state, before)

    def queue(self, state):
        state.native_user_recipient_key = 7
        state.user_controlled_club_id = 1
        player = state.players[1000]
        player.club_id, player.loan_club_id = 2, 1
        player.morale, player.transfer_listed, player.wanted = 0, False, False
        draws = []
        rng = SimpleNamespace(randbelow=lambda bound: draws.append(bound) or 2)
        self.assertTrue(maybe_queue_player_transfer_request(
            player, date(2000, 7, 1), rng, club_user_controlled=True,
            active_club_user_controlled=True, request_sink=state._retain_player_transfer_request))
        self.assertEqual(draws, [30])
        return state.player_transfer_requests[-1]

    def test_producer_captures_recipient_and_active_loan_club_not_later_selection(self):
        state = self.controller().state
        request = self.queue(state)
        state.native_user_recipient_key = 8
        state.user_controlled_club_id = 3
        state.players[1000].loan_club_id = 3
        self.assertEqual((request.recipient_manager_key, request.sender_club_id), (7, 1))

    def test_disk_codec_retains_captured_context_not_fresh_binding(self):
        controller = self.controller()
        controller.select_club(1)
        request = self.queue(controller.state)
        restored = loads_human_gameplay(Database(), coefficient_matrix(), coefficient_matrix(),
                                       dumps_human_gameplay(controller))
        self.assertEqual(restored.state.native_user_recipient_key, 7)
        self.assertEqual(restored.state.player_transfer_requests, [request])
        self.assertEqual(restored.state.players[1000].loan_club_id, 1)

    def test_older_schema48_without_context_stays_unknown(self):
        controller = self.controller()
        controller.select_club(1)
        self.queue(controller.state)
        saved = snapshot_human_gameplay(controller)
        saved['game_state'].pop('native_user_recipient_key')
        for request in saved['game_state']['player_transfer_requests']:
            request.pop('recipient_manager_key')
            request.pop('sender_club_id')
        restored = restore_human_gameplay(Database(), coefficient_matrix(), coefficient_matrix(), saved)
        self.assertIsNone(restored.state.native_user_recipient_key)
        request = restored.state.player_transfer_requests[0]
        self.assertIsNone(request.recipient_manager_key)
        self.assertIsNone(request.sender_club_id)

    def test_malformed_saved_context_is_rejected(self):
        controller = self.controller()
        controller.select_club(1)
        self.queue(controller.state)
        saved = snapshot_human_gameplay(controller)
        for key in (True, -1, '7', 999, 0x80000000):
            bad = copy.deepcopy(saved)
            bad['game_state']['native_user_recipient_key'] = key
            with self.subTest(key=key), self.assertRaises(ValueError):
                restore_human_gameplay(Database(), coefficient_matrix(), coefficient_matrix(), bad)
        for pair in ((7, None), (None, 1), (True, 1), (7, -1), (7, '1')):
            with self.subTest(pair=pair), self.assertRaises(ValueError):
                PlayerTransferRequest(1000, date(2000, 7, 1), date(2000, 7, 2), *pair)
