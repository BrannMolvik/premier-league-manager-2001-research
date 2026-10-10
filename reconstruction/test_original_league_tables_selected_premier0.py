"""Gate13 selected original Premier League0 table strict-fixed-owner regressions.

The canonical original Premier League is NOT a procedural nonPL League. Test
the complete 20-member/380-directed fixture structure and original-name
qsort contract while the human manages Southport (Conference7).
"""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
import unittest

from competition_state import PremierLeagueState, ProceduralPremierFixture
from gate13_management_source_data import ManagementPresentationError, ManagementSourceDataBridge
from original_league_tables_presenter import build_league_tables_snapshot
from test_original_league_tables_selected_source import (
    context as base_context,
    bridge as base_bridge,
)
from test_original_league_fixtures_selected_source import state_two_source_leagues


def prepared_state():
    state = state_two_source_leagues()
    source_club_ids = tuple(range(1000, 1020))
    for index, cid in enumerate(source_club_ids):
        state.clubs[cid] = SimpleNamespace(
            name=f"Premier Club {index:02}", short_name=f"PL{index:02}",
            country_id=26,
        )
        state.club_competition_membership[cid] = 0
    # Two complete directed fixtures for each unordered opponent pair.
    fixtures = tuple(
        ProceduralPremierFixture(
            id=index, round_index=index % 38,
            home_club_id=home, away_club_id=away,
        ) for index, (home, away) in enumerate(
            (home, away) for home in source_club_ids
            for away in source_club_ids if home != away
        )
    )
    assert len(fixtures) == 380
    state.premier_league = PremierLeagueState(fixtures)
    state.premier_league.record_result(0, 2, 1)
    return state


def source_bridge(state):
    return ManagementSourceDataBridge(SimpleNamespace(
        state=state, human=SimpleNamespace(club_id=349),
    ))


def select_premier(state):
    initial = base_context(state)
    assert initial.selected_competition_id == 7  # Real Southport current manager.
    assert initial.division_candidates[0][0][0] == 0
    return initial.accept_native_radio_event(9)


class OriginalPremier0SelectedTableTests(unittest.TestCase):
    def test_native_selection_of_premier0_uses_real_live_results_not_human_league(self):
        state = prepared_state()
        selected = select_premier(state)
        self.assertEqual(selected.selected_competition_id, 0)
        self.assertEqual(selected.active_country_id, 26)
        bridge = source_bridge(state)
        rows = bridge.source_selected_league_table_rows(selected)
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0].club_id, 1000)
        self.assertEqual(rows[0].points, 3)
        self.assertEqual(rows[0].played, 1)
        self.assertEqual(rows[0].goals_for, 2)
        self.assertEqual(rows[1].club_id, 1002)  # All 0-point unplayed clubs sorted by name.
        self.assertEqual(rows[-1].club_id, 1001)  # One 1:2 loss.
        self.assertEqual(rows[-1].goals_against, 2)
        self.assertNotIn(349, tuple(row.club_id for row in rows))
        self.assertEqual(state.club_competition_membership[349], 7)
        view = build_league_tables_snapshot(rows)
        self.assertEqual(len(view.rows), 20)
        self.assertEqual(view.rows[0].points, 3)
        self.assertEqual(view.sort_state, 0)

    def test_selected_dispatch_keeps_legacy_nonpl_source_untouched(self):
        state = prepared_state()
        selected = base_context(state).accept_native_radio_event(10)
        rows = source_bridge(state).source_selected_league_table_rows(selected)
        self.assertEqual(tuple(row.club_id for row in rows), (10, 11))
        self.assertEqual(tuple(row.points for row in rows), (3, 0))

    def test_partial_or_foreign_fixed_live_owner_refused_before_render(self):
        state = prepared_state()
        candidate = select_premier(state)
        state.premier_league.fixtures.pop(379)
        with self.assertRaisesRegex(ManagementPresentationError, "380-fixture"):
            source_bridge(state).source_selected_league_table_rows(candidate)

        state = prepared_state()
        state.club_competition_membership[1019] = 2
        with self.assertRaisesRegex(ManagementPresentationError, "DBRClub"):
            source_bridge(state).source_selected_league_table_rows(
                select_premier(state))

        state = prepared_state()
        state.premier_league = None
        with self.assertRaisesRegex(ManagementPresentationError, "live League owner"):
            source_bridge(state).source_selected_league_table_rows(
                select_premier(state))

    def test_original_cp1252_name_and_exact_tie_fails_without_numeric_fallback(self):
        state = prepared_state()
        candidate = select_premier(state)
        state.clubs[1002].short_name = "🦊"
        with self.assertRaisesRegex(ManagementPresentationError, "CP1252"):
            source_bridge(state).source_selected_league_table_rows(candidate)

        state = prepared_state()
        state.clubs[1002].short_name = state.clubs[1003].short_name
        with self.assertRaisesRegex(ManagementPresentationError, "ID fallback forbidden"):
            source_bridge(state).source_selected_league_table_rows(
                select_premier(state))

    def test_corrupt_selected_source_or_unproven_current_form_never_uses_premier_fallback(self):
        state = prepared_state()
        good = select_premier(state)
        for malformed in (
            replace(good, sort_state=1),
            replace(good, human_competition_id=0),
            replace(good, selected_division_index=True),
            replace(good, active_country_index=1),
            replace(good, division_candidates=tuple(
                (((99, "invented"),) if i == 0 else row)
                for i, row in enumerate(good.division_candidates))),
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(ManagementPresentationError):
                    source_bridge(state).source_selected_league_table_rows(malformed)

    def test_missing_original_premier_definition_refuses_source(self):
        state = prepared_state()
        selected = select_premier(state)
        state.competitions[0].country_region_id = 33
        with self.assertRaises(ManagementPresentationError):
            source_bridge(state).source_selected_league_table_rows(selected)


if __name__ == "__main__":
    unittest.main()
