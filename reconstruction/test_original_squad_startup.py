from dataclasses import dataclass, replace
import unittest

from original_squad_startup import select_first_season_primary_squad
from match_lineup import AI_FORMATIONS


@dataclass(frozen=True)
class Player:
    player_index: int
    preferred_positions: tuple
    skills: tuple = (80,) * 17
    form_state: int = 2
    non_eu: bool = False
    injured: bool = False
    suspended: bool = False
    selection_excluded: bool = False


def roster():
    return tuple(Player(i, (slot.role, 0, 0))
                 for i, slot in enumerate(AI_FORMATIONS[0])) + tuple(
        Player(i, (role, 0, 0)) for i, role in enumerate(
            (12, 19, 4, 1, 12, 19, 4, 1, 12), 11))


class FirstSeasonSquadSelectionTests(unittest.TestCase):
    def select(self, players, **kwargs):
        return select_first_season_primary_squad(
            players, formation_id=kwargs.get('formation_id', 0),
            non_eu_limit=kwargs.get('non_eu_limit', 11))

    def test_initial_native_quota_is_two_not_competition_five(self):
        result = self.select(roster())
        self.assertTrue(result.complete)
        self.assertEqual(len(result.lineup.starters), 11)
        self.assertEqual(result.lineup.substitutes, (11, 12))
        self.assertEqual([(p.role, p.auxiliary_code) for p in result.lineup.starters],
                         [(s.role, s.auxiliary_code) for s in AI_FORMATIONS[0]])

    def test_startup_uses_low_two_bits_not_ordinary_bit_two_filter(self):
        normal = self.select(roster())
        excluded = self.select(tuple(replace(p, selection_excluded=True) for p in roster()))
        self.assertEqual(normal, excluded)
        unavailable = self.select(tuple(replace(p, injured=True) for p in roster()))
        self.assertFalse(unavailable.complete)
        self.assertEqual(unavailable.lineup.starters, ())
        self.assertEqual(unavailable.lineup.substitutes, ())
        suspended = self.select(tuple(replace(p, suspended=True) for p in roster()))
        self.assertEqual(unavailable, suspended)

    def test_bench_keeps_first_eligible_not_strongest_candidate(self):
        # XI occupy all preferred slots with 100 skills. The later extras
        # are stronger than the first group candidates, but 40A393 et al.
        # score the retained last-XI pointer, not those candidates.
        players = tuple(replace(p, skills=(100,) * 17) for p in roster()[:11])
        players += (Player(11, (12, 0, 0), skills=(10,) * 17),
                    Player(12, (19, 0, 0), skills=(10,) * 17),
                    Player(13, (12, 0, 0), skills=(90,) * 17),
                    Player(14, (19, 0, 0), skills=(90,) * 17))
        result = self.select(players)
        self.assertTrue(result.complete)
        self.assertEqual(result.lineup.substitutes, (11, 12))
        from match_lineup import select_ai_lineup_core
        differently_ranked = select_ai_lineup_core(players, 0, 2)
        self.assertEqual(differently_ranked.substitutes, (13, 14))

    def test_native_counting_is_disabled_but_zero_limit_still_rejects(self):
        members = tuple(replace(p, non_eu=True) for p in roster())
        # No running increments: a positive limit allows more than one.
        result = self.select(members, non_eu_limit=1)
        self.assertTrue(result.complete)
        self.assertEqual(len(result.lineup.starters), 11)
        blocked = self.select(members, non_eu_limit=0)
        self.assertFalse(blocked.complete)
        self.assertEqual(blocked.lineup.starters, ())
        self.assertEqual(blocked.lineup.substitutes, ())

    def test_unknown_context_is_not_a_default_and_selection_is_read_only(self):
        players = roster()
        for kwargs in ({'formation_id': None}, {'formation_id': True},
                       {'non_eu_limit': None}, {'non_eu_limit': True},
                       {'non_eu_limit': -1}):
            with self.assertRaises(ValueError):
                self.select(players, **kwargs)
        self.select(players)
        self.assertEqual(players, roster())
        with self.assertRaisesRegex(ValueError, 'flag inputs'):
            self.select((replace(players[0], injured=None),))

    def test_missing_xi_is_exposed_not_retried_or_filled_with_placeholders(self):
        result = self.select(roster()[:10])
        self.assertFalse(result.complete)
        self.assertEqual(len(result.lineup.starters), 10)
        self.assertTrue(result.lineup.unfilled_slot_indices)


class FirstSeasonStateProducerTests(unittest.TestCase):
    def state(self, *, manager_valid=True):
        from datetime import date
        from types import SimpleNamespace
        from game_state import GameState
        from runtime_state import RuntimePlayer
        from match_schedule import MsvcCrtRng
        from test_runtime_state import FakePlayer
        players = tuple(RuntimePlayer.from_database_player(replace(
            FakePlayer(), index=p.player_index, club_id=17, positions=p.preferred_positions),
            date(2000, 7, 4), MsvcCrtRng(1)) for p in roster())
        state = GameState.from_players(players, date(2000, 7, 4))
        state.clubs[17] = SimpleNamespace(team_category_code=1, name='Ordinary', manager_id=5)
        state.managers[5] = SimpleNamespace(club_id=17 if manager_valid else None, formation_default=3)
        return state

    def initialize(self, state):
        return state.initialize_original_primary_first_season_squad(
            17, primary_pass_before_secondary=True)

    def test_exact_setters_and_retained_first_formation(self):
        state = self.state()
        result = self.initialize(state)
        self.assertTrue(result.complete)
        self.assertEqual(state.native_squad_first_formations, {17: 3})
        for p in state.ordered_club_roster(17):
            self.assertEqual(p.match_active, p.index in {a.player_index for a in result.lineup.starters})
            self.assertEqual(p.match_substitute_available, p.index in result.lineup.substitutes)
            self.assertFalse(p.reserve_active or p.reserve_substitute)
        for a in result.lineup.starters:
            p = state.players[a.player_index]
            self.assertEqual((p.current_position, p.position_aux_code), (a.role, a.auxiliary_code))
        with self.assertRaisesRegex(RuntimeError, 'already produced'):
            self.initialize(state)

    def test_manager_invalid_branch_and_incomplete_no_partial_commit(self):
        state = self.state(manager_valid=False)
        for p in state.players.values():
            p.injured = True
        result = self.initialize(state)
        self.assertFalse(result.complete)
        self.assertEqual(state.native_squad_first_formations, {17: 0})
        self.assertFalse(any(p.match_active or p.match_substitute_available for p in state.players.values()))

    def test_missing_phase_and_loan_side_effect_fail_atomically(self):
        state = self.state()
        with self.assertRaisesRegex(RuntimeError, 'qualified startup phase'):
            state.initialize_original_primary_first_season_squad(17)
        state.players[0].loan_listed = True
        with self.assertRaisesRegex(RuntimeError, 'fresh own-club state'):
            self.initialize(state)
        self.assertEqual(state.native_squad_first_formations, {})
        self.assertFalse(any(p.match_active for p in state.players.values()))

    def test_snapshot_restore_retains_output_without_reselection(self):
        from internal_save import snapshot_game_state, restore_game_state
        state = self.state()
        self.initialize(state)
        snapshot = snapshot_game_state(state)
        from types import SimpleNamespace
        from test_runtime_state import FakePlayer
        database = SimpleNamespace(clubs=(), managers=(), competitions=(),
            players=tuple(replace(FakePlayer(), index=p.player_index, club_id=17,
                                  positions=p.preferred_positions) for p in roster()))
        restored = restore_game_state(database, snapshot)
        self.assertEqual(restored.native_squad_first_formations, {17: 3})
        self.assertEqual([p.match_selection_state_code for p in restored.ordered_club_roster(17)],
                         [p.match_selection_state_code for p in state.ordered_club_roster(17)])

    def entry(self, *, kind='league_match', linked='clear', competition=5):
        from primary_schedule_shadow import PrimaryScheduleShadowEntry
        from competition_schedule import direct_club_ref
        return PrimaryScheduleShadowEntry(kind, competition, 0, ('qualified', 1),
            direct_club_ref(17), direct_club_ref(18), frozenset((17,)), frozenset((18,)), linked)

    def test_constructor_quota_uses_current_day_first_exact_owner_not_displayed_league(self):
        from types import SimpleNamespace
        from datetime import timedelta
        state = self.state()
        day = state.calendar.current_date
        state.competitions[5] = SimpleNamespace(substitute_quota=3)
        state.competitions[6] = SimpleNamespace(substitute_quota=7)
        state.primary_schedule_shadow.days = {
            day: (self.entry(competition=5),),
            day + timedelta(days=1): (self.entry(competition=6),)}
        self.assertEqual(state.original_primary_squad_constructor_quota(17), 3)
        state.primary_schedule_shadow.days[day] = (self.entry(linked='linked'),)
        self.assertEqual(state.original_primary_squad_constructor_quota(17), 7)

    def test_constructor_quota_unknown_is_not_five(self):
        from types import SimpleNamespace
        state = self.state()
        state.competitions[5] = SimpleNamespace(substitute_quota=5)
        with self.assertRaisesRegex(RuntimeError, 'no proven'):
            state.original_primary_squad_constructor_quota(17)
        for e in (self.entry(linked='unknown'), self.entry(kind='unsupported'),
                  replace(self.entry(), participant_0_ref=SimpleNamespace(direct_club_id=None))):
            state.primary_schedule_shadow.days = {state.calendar.current_date: (e,)}
            with self.assertRaises(RuntimeError):
                state.original_primary_squad_constructor_quota(17)


if __name__ == '__main__':
    unittest.main()
