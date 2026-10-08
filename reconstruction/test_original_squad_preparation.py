import unittest
from dataclasses import replace

from original_squad_preparation import (
    PreparedSquadPlayer, prepare_primary_squad, native_role_occupancy,
    NATIVE_ROLE_CAPACITIES,
)


def player(index, selection=0, role=4):
    return PreparedSquadPlayer(index, selection, role, 0, 0, 0,
                               (role, 0, 0), (80,) * 17, 2, False)


class SquadPreparationTests(unittest.TestCase):
    def prepare(self, players, quota=5, formation=0, score=None):
        return prepare_primary_squad(players, substitute_quota=quota,
                                     reserve_formation=formation,
                                     on_first_active=lambda p: None,
                                     target_score=score or (lambda p, role: 1))

    def test_reserve_selector_uses_original_order_for_ties_and_bench(self):
        # Eleven first-XI + five first-subs leave fourteen eligible members.
        members = [player(i, 4 if i < 11 else 3 if i < 16 else 0) for i in range(30)]
        result = self.prepare(members)
        self.assertTrue(result.reserve_selection_complete)
        self.assertEqual([p.player_id for p in result.players if p.selection == 2], list(range(16, 27)))
        self.assertEqual([p.player_id for p in result.players if p.selection == 1], [27, 28, 29])
        # Native formation roles are committed in eleven-slot order, not an
        # ascending sort or preferred-role prepass.
        self.assertEqual(result.players[16].current_role, 19)
        self.assertEqual(result.players[16].current_aux, 1)
        self.assertEqual(result.players[16].reserve_role, 4)

    def test_target_rating_can_choose_nonpreferred_before_preferred(self):
        members = [player(i, 4 if i < 11 else 3 if i < 16 else 0) for i in range(30)]
        members[16] = replace(members[16], preferred_roles=(19, 0, 0))
        result = self.prepare(members, score=lambda p, r: 9 if p.player_id == 17 else 1)
        self.assertEqual(result.players[17].current_role, 19)
        self.assertEqual(result.players[17].current_aux, 1)
        self.assertEqual(result.players[16].current_aux, 0)

    def test_insufficient_candidates_do_not_publish_partial_reserve_xi(self):
        members = [player(i, 4 if i < 11 else 3 if i < 16 else 0) for i in range(30)]
        members = [replace(p, unavailable=p.player_id >= 25) for p in members]
        result = self.prepare(members)
        self.assertTrue(result.reserve_selection_attempted)
        self.assertFalse(result.reserve_selection_complete)
        self.assertFalse(any(p.selection == 2 for p in result.players))
        # The following 4067B0 overflow pass independently writes two bench
        # states even for unavailable players; it is not a partial XI commit.
        self.assertEqual([p.player_id for p in result.players if p.selection == 1], [28, 29])

    def test_small_roster_clears_reserve_with_role_swap_and_preferred_reset(self):
        member = replace(player(0, 2, 19), current_aux=1, reserve_role=4, reserve_aux=2,
                         preferred_roles=(3, 0, 0))
        result = self.prepare([member])
        self.assertEqual(result.players[0].selection, 0)
        self.assertEqual((result.players[0].current_role, result.players[0].current_aux), (3, 0))
        self.assertEqual((result.players[0].reserve_role, result.players[0].reserve_aux), (19, 1))

    def test_overflow_quota_checks_are_sequential_not_mutually_exclusive(self):
        # Existing reserves suppress auto-selection. Three overflowing members
        # enter both first-XI and first-bench setters; final flags are bench.
        members = [player(i, 2 if i < 11 else 1 if i < 14 else 0) for i in range(30)]
        calls = []
        result = prepare_primary_squad(members, substitute_quota=5,
                                       reserve_formation=0,
                                       on_first_active=lambda p: calls.append(p.player_id))
        self.assertEqual(calls, [29, 28, 27])
        self.assertEqual([p.player_id for p in result.players if p.selection == 3], [27, 28, 29])
        self.assertFalse(any(p.selection == 4 for p in result.players))

    def test_occupancy_has_distinct_first_and_reserve_role_eight_divisor(self):
        first = [player(i, 4, 4) for i in range(5)]
        reserve = [player(i, 2, 4) for i in range(5)]
        self.assertEqual(native_role_occupancy(first, role=8, reserve=False, excluded_player_id=99), 1)
        self.assertEqual(native_role_occupancy(reserve, role=8, reserve=True, excluded_player_id=99), 5)
        self.assertEqual(NATIVE_ROLE_CAPACITIES[4], 3)
        self.assertEqual(NATIVE_ROLE_CAPACITIES[19], 3)

    def test_no_guessed_quota_formation_availability_or_setter_contract(self):
        for kwargs in ({'substitute_quota': None}, {'reserve_formation': None},
                       {'on_first_active': None}):
            values = dict(substitute_quota=5, reserve_formation=0, on_first_active=lambda p: None)
            values.update(kwargs)
            with self.assertRaises(ValueError):
                prepare_primary_squad([player(0)], **values)
        with self.assertRaises(ValueError):
            replace(player(0), unavailable=None)

    def test_normalized_formation_22_is_retained_even_if_selection_fails(self):
        members = [replace(player(i), unavailable=True) for i in range(30)]
        result = self.prepare(members, formation=22)
        self.assertEqual(result.reserve_formation, 0)
        self.assertFalse(result.reserve_selection_complete)


class LiveSquadPreparationTests(unittest.TestCase):
    def state(self, count=30):
        from datetime import date
        from game_state import GameState
        from match_schedule import MsvcCrtRng
        from runtime_state import RuntimePlayer
        from test_runtime_state import FakePlayer
        members = tuple(RuntimePlayer.from_database_player(
            FakePlayer(index=i, club_id=1, positions=(4, 3, 0)),
            date(2000, 7, 1), MsvcCrtRng(i + 1)) for i in range(count))
        state = GameState.from_players(members, date(2000, 7, 1))
        # Explicit imported source value, not a fallback for arbitrary saves.
        state.native_squad_reserve_formations[1] = 0
        return state

    def test_live_preparation_commits_the_exact_pure_producer_then_orders(self):
        state = self.state()
        roster = state.ordered_club_roster(1)
        for i, p in enumerate(roster[:16]):
            if i < 11:
                p.set_match_active()
            else:
                p.set_match_substitute_available()
        prepared = state.prepare_original_primary_squad(1, substitute_quota=5)
        self.assertTrue(prepared.reserve_selection_complete)
        self.assertEqual(sum(p.reserve_active for p in roster), 11)
        self.assertEqual(sum(p.reserve_substitute for p in roster), 3)
        for source in prepared.players:
            live = state.players[source.player_id]
            self.assertEqual(live.match_selection_state_code, source.selection)
            self.assertEqual((live.current_position, live.position_aux_code),
                             (source.current_role, source.current_aux))
            self.assertEqual((live.saved_reserve_role_152, live.saved_reserve_aux_153),
                             (source.reserve_role, source.reserve_aux))
        membership = state.original_primary_squad_membership(1, substitute_quota=5)
        self.assertEqual(state.club_roster_order[1], [p.player_id for p in membership.members])
        self.assertEqual(len(set(state.club_roster_order[1])), 30)

    def test_missing_formation_or_secondary_context_does_not_mutate_live_state(self):
        state = self.state()
        before = tuple((p.match_selection_state_code, p.current_position,
                        p.saved_reserve_role_152) for p in state.ordered_club_roster(1))
        state.native_squad_reserve_formations.clear()
        with self.assertRaisesRegex(RuntimeError, 'not been retained'):
            state.prepare_original_primary_squad(1, substitute_quota=5)
        state.native_squad_reserve_formations[1] = 0
        state.players[0].loan_club_id = 2
        with self.assertRaisesRegex(RuntimeError, 'Secondary-club'):
            state.prepare_original_primary_squad(1, substitute_quota=5)
        self.assertEqual(before, tuple((p.match_selection_state_code, p.current_position,
                         p.saved_reserve_role_152) for p in state.ordered_club_roster(1)))


if __name__ == '__main__':
    unittest.main()
