"""Bounded day-owner integration, independently of unrecovered live modal UI."""
from datetime import date, timedelta
from pathlib import Path
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

from game_state import GameCalendar
from human_gameplay import HumanGameplayController
from primary_schedule_shadow import PrimaryScheduleShadowState, PrimaryScheduleShadowEntry
from competition_schedule import direct_club_ref


class OriginalManagementTurnTests(unittest.TestCase):
    today = date(2000, 8, 1)
    end = date(2001, 7, 1)

    def controller(self, due_date=None, entries=()):
        state = SimpleNamespace(
            premier_league=object(), calendar=GameCalendar(self.today),
            clubs={i: SimpleNamespace(team_category_code=1) for i in range(1, 5)},
            primary_schedule_shadow=PrimaryScheduleShadowState(days={}),
            invalidate_primary_schedule_wrapper_links=Mock(),
            primary_entries_due_today=Mock(),
            simulate_due_primary_ai_entries=Mock(return_value=()),
            simulate_primary_ai_entry=Mock(side_effect=lambda entry, *a, **k: ('result', entry)),
        )
        state.primary_entries_due_today.side_effect = lambda: (
            entries if state.calendar.current_date == due_date else ())
        c = HumanGameplayController(state, 'attack', 'defence', 'rng', 'engine_rng')
        c.human = SimpleNamespace(club_id=1)
        c.current_selection = Mock()
        c._finish_shared_primary_day = Mock()
        c._primary_entry_clubs = Mock(side_effect=lambda entry: (
            (1, 2) if entry == ('premier_league', 7) else (3, 4)))
        state.primary_schedule_shadow.days[due_date] = tuple(
            PrimaryScheduleShadowEntry('fixed_league_match', 0, 0,
                ('fixed_league_match', 0, 0, entry[1]),
                direct_club_ref(1 if entry[1] == 7 else 3),
                direct_club_ref(2 if entry[1] == 7 else 4),
                frozenset((1 if entry[1] == 7 else 3,)),
                frozenset((2 if entry[1] == 7 else 4,)))
            for entry in entries)
        return c

    def advance(self, c, next_date, **kwargs):
        return c.advance_original_management_turn(
            next_match_date=next_date, selector_source_qualified=True,
            container_end_date=self.end, **kwargs)

    def test_distant_match_stops_after_seven_not_prototype_skip(self):
        c = self.controller(self.today + timedelta(days=30), (('premier_league', 7),))
        result = self.advance(c, self.today + timedelta(days=30))
        expected = tuple(self.today + timedelta(days=i) for i in range(1, 8))
        self.assertEqual(result.processed_dates, expected)
        self.assertEqual(c.state.calendar.current_date, expected[-1])
        self.assertIsNone(result.pending_primary_entry)
        self.assertEqual(c.state.invalidate_primary_schedule_wrapper_links.call_count, 7)
        self.assertEqual(c._finish_shared_primary_day.call_count, 7)
        c.current_selection.assert_not_called()

    def test_stops_day_before_near_match_without_human_calculation(self):
        c = self.controller(self.today + timedelta(days=4), (('premier_league', 7),))
        result = self.advance(c, self.today + timedelta(days=4))
        self.assertEqual(len(result.processed_dates), 3)
        self.assertIsNone(result.pending_primary_entry)
        c.state.simulate_primary_ai_entry.assert_not_called()

    def test_tomorrow_suspends_order_at_human_before_modal_choice(self):
        before, human, after = ('premier_league', 5), ('premier_league', 7), ('premier_league', 9)
        c = self.controller(self.today + timedelta(days=1), (before, human, after))
        result = self.advance(c, self.today + timedelta(days=1))
        self.assertEqual(result.pending_primary_entry, human)
        self.assertEqual(result.processed_dates, (self.today + timedelta(days=1),))
        self.assertEqual([call.args[0] for call in c.state.simulate_primary_ai_entry.call_args_list],
                         [before, after])
        self.assertEqual(c._pending_prior_primary_results,
                         ((before, ('result', before)), (after, ('result', after))))
        self.assertEqual(c._pending_after_primary_entries, ())
        c.state.simulate_due_primary_ai_entries.assert_not_called()
        c._finish_shared_primary_day.assert_not_called()
        c.current_selection.assert_called_once_with()
        # A repeated action must not replay the partial day or consume RNG.
        repeated = self.advance(c, c.state.calendar.current_date)
        self.assertEqual(repeated.processed_dates, ())
        self.assertEqual(repeated.pending_primary_entry, human)
        self.assertEqual(c.state.simulate_primary_ai_entry.call_count, 2)

    def test_current_day_and_zero_length_do_not_reprocess_today(self):
        for next_date, length in ((self.today, 7), (None, 0)):
            c = self.controller(self.today, (('premier_league', 7),))
            result = self.advance(c, next_date, turn_length=length)
            self.assertEqual(result.processed_dates, ())
            self.assertEqual(c.state.calendar.current_date, self.today)
            c.state.primary_entries_due_today.assert_not_called()

    def test_unknown_selector_or_invalid_lineup_has_no_date_rng_writes(self):
        c = self.controller()
        with self.assertRaisesRegex(RuntimeError, 'selector'):
            c.advance_original_management_turn(next_match_date=None,
                selector_source_qualified=False, container_end_date=self.end)
        c.current_selection.assert_not_called()
        c.current_selection.side_effect = ValueError('native lineup unavailable')
        with self.assertRaisesRegex(ValueError, 'lineup'):
            self.advance(c, self.today + timedelta(days=1))
        self.assertEqual(c.state.calendar.current_date, self.today)
        c.state.invalidate_primary_schedule_wrapper_links.assert_not_called()
        c.state.simulate_due_primary_ai_entries.assert_not_called()

    def test_unresolved_participant_and_multiple_human_entries_fail_before_ai_rng(self):
        for pairs in (None, (1, 2)):
            c = self.controller(self.today + timedelta(days=1),
                                (('premier_league', 5), ('premier_league', 7)))
            c._primary_entry_clubs.side_effect = None
            c._primary_entry_clubs.return_value = pairs
            with self.assertRaisesRegex(RuntimeError, 'unresolved|at most one'):
                self.advance(c, self.today + timedelta(days=1))
            c.state.simulate_primary_ai_entry.assert_not_called()
            c.state.simulate_due_primary_ai_entries.assert_not_called()
            c._finish_shared_primary_day.assert_not_called()

    def test_original_exit_during_maintenance_does_not_advance_more_days(self):
        c = self.controller()
        c._finish_shared_primary_day.side_effect = lambda _: setattr(c, 'human', None)
        result = self.advance(c, None)
        self.assertEqual(len(result.processed_dates), 1)
        self.assertIsNone(result.pending_primary_entry)

    def test_nonprimary_or_nonleague_owner_is_not_assumed_to_use_primary_two_passes(self):
        for category, kind in ((2, 'premier_league'), (1, 'domestic_cup')):
            c = self.controller(self.today + timedelta(days=1), ((kind, 5),))
            c.state.clubs[3].team_category_code = category
            with self.assertRaisesRegex(RuntimeError, 'primary club|non-League|wrapper lifecycle'):
                self.advance(c, self.today + timedelta(days=1))
            c.state.simulate_primary_ai_entry.assert_not_called()
            c.state.simulate_due_primary_ai_entries.assert_not_called()

    def test_real_backend_pending_owner_saves_reloads_and_finishes_without_ai_replay(self):
        # Synthetic database/explicit lineup tests controller and codec
        # integration; it is not source evidence or original-screen acceptance.
        import test_human_gameplay as fixtures
        from internal_save import save_human_gameplay, load_human_gameplay
        helper = fixtures.HumanGameplayControllerTests()
        c = helper.build_controller()
        c.state.clubs = {i: SimpleNamespace(**vars(club), team_category_code=1)
                         for i, club in c.state.clubs.items()}
        class PrimaryDatabase(fixtures.Database):
            clubs = tuple(c.state.clubs.values())
        c.select_club(1)
        helper.set_available_lineup(c)
        c.state.primary_matchday_order = {
            c.state.premier_league.round_date(round_id):
                tuple(('premier_league', fixture_id) for fixture_id in ids)
            for round_id, ids in c.state.premier_league_scheduler_order.items()
        }
        match_date = min(c.state.primary_matchday_order)
        c.state.calendar.current_date = match_date - timedelta(days=1)
        due = c.state.primary_matchday_order[match_date]
        c.state.primary_schedule_shadow.days[match_date] = tuple(
            PrimaryScheduleShadowEntry('fixed_league_match', 0, 0,
                ('fixed_league_match', 0, 0, entry[1]),
                direct_club_ref(c.state.premier_league.fixtures[entry[1]].home_club_id),
                direct_club_ref(c.state.premier_league.fixtures[entry[1]].away_club_id),
                frozenset((c.state.premier_league.fixtures[entry[1]].home_club_id,)),
                frozenset((c.state.premier_league.fixtures[entry[1]].away_club_id,)))
            for entry in due)
        # Supplied phase boundary for this synthetic integration regression.
        # Production invalidation is NOT disabled; native post-start sources
        # must qualify current-day wrappers before an ordinary UI can use them.
        c.state.invalidate_primary_schedule_wrapper_links = Mock()
        human = ('premier_league', 0)
        ai_order = tuple(entry for entry in due if entry != human)
        result = c.advance_original_management_turn(next_match_date=match_date,
            selector_source_qualified=True, container_end_date=self.end)
        self.assertEqual(result.pending_primary_entry, human)
        self.assertEqual(tuple(entry for entry, _ in c._pending_prior_primary_results), ai_order)
        self.assertEqual(len(c.state.premier_league.results), 9)
        self.assertNotIn(0, c.state.premier_league.results)
        self.assertEqual(c._pending_after_primary_entries, ())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'pending-native-turn.fm2k'
            save_human_gameplay(c, path)
            restored = load_human_gameplay(PrimaryDatabase(), c.attack_matrix, c.defence_matrix, path)
        self.assertEqual(restored.pending_primary_entry, human)
        self.assertEqual(tuple(entry for entry, _ in restored._pending_prior_primary_results), ai_order)
        self.assertEqual(restored._pending_after_primary_entries, ())
        outcome = restored.play_user_primary_match()
        self.assertEqual(tuple(entry for entry, _ in outcome.matchday_results), ai_order + (human,))
        self.assertEqual(len(restored.state.premier_league.results), 10)
        self.assertIsNone(restored.pending_primary_entry)

    def test_unknown_current_day_wrapper_cannot_be_promoted_from_due_date(self):
        from dataclasses import replace
        c = self.controller(self.today + timedelta(days=1), (('premier_league', 7),))
        owners = c.state.primary_schedule_shadow.days[self.today + timedelta(days=1)]
        c.state.primary_schedule_shadow.days[self.today + timedelta(days=1)] = (
            replace(owners[0], wrapper_link_state='unknown'),)
        with self.assertRaisesRegex(RuntimeError, 'wrapper lifecycle'):
            self.advance(c, self.today + timedelta(days=1))
        self.assertIsNone(c.pending_primary_entry)
        c.state.simulate_primary_ai_entry.assert_not_called()


if __name__ == '__main__':
    unittest.main()
