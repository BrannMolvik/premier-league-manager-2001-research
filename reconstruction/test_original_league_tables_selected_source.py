"""Native PLeagueTables selected root-country/DIVISION source-only regressions."""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace
import unittest

from gate13_management_source_data import ManagementSourceDataBridge, ManagementPresentationError
from original_league_tables_presenter import build_league_tables_snapshot
from original_league_tables_selector_context import (
    OriginalLeagueTablesSelectorError,
    build_original_league_tables_selection_context,
)
from test_original_league_fixtures_selected_source import state_two_source_leagues


def context(state):
    return build_original_league_tables_selection_context(
        human_club_id=349,
        clubs=state.clubs,
        membership=state.club_competition_membership,
        competitions=state.competitions.values(),
    )


def bridge(state):
    return ManagementSourceDataBridge(SimpleNamespace(
        state=state, human=SimpleNamespace(club_id=349),
    ))


class RealSelectedLeagueTablesSourceTests(unittest.TestCase):
    def test_original_country8_division5_constructor_initially_selects_manager_league(self):
        state = state_two_source_leagues()
        original = context(state)
        self.assertEqual(original.active_country_id, 26)
        self.assertEqual(original.selected_competition_id, 7)
        self.assertEqual(original.selected_division_index, 4)
        self.assertEqual(original.sort_state, 0)
        self.assertEqual(tuple(cid for cid, _ in original.division_candidates[0]),
                         (0, 2, 3, 4, 7))
        self.assertEqual(len(original.division_candidates), 8)

    def test_other_real_english_division_renders_actual_results_not_managed_club(self):
        state = state_two_source_leagues()
        initial = context(state)
        selected = initial.accept_native_radio_event(10)
        self.assertEqual(selected.selected_competition_id, 2)
        self.assertEqual(selected.selected_division_index, 1)
        self.assertEqual(initial.selected_competition_id, 7)
        view = bridge(state).source_selected_nonpl_league_table_rows(selected)
        self.assertEqual(tuple(row.club_id for row in view), (10, 11))
        self.assertEqual(tuple(row.points for row in view), (3, 0))
        self.assertEqual(tuple(row.club_name for row in view), ("Alpha", "Beta"))
        self.assertEqual(tuple(row.position for row in view), (1, 2))
        rendered = build_league_tables_snapshot(view)
        self.assertEqual(tuple(row.points for row in rendered.rows), (3, 0))
        self.assertEqual(state.club_competition_membership[349], 7)

    def test_sort_by_controls_are_distinct_and_unproved_current_form_refuses(self):
        state = state_two_source_leagues()
        selection = context(state).accept_native_radio_event(10)
        current_form = selection.accept_native_radio_event(15)
        self.assertEqual(current_form.sort_state, 1)
        self.assertEqual(current_form.accept_native_radio_event(14).sort_state, 0)
        with self.assertRaisesRegex(ManagementPresentationError, "unqualified"):
            bridge(state).source_selected_nonpl_league_table_rows(current_form)
        self.assertEqual(bridge(state).source_selected_nonpl_league_table_rows(selection)[0].club_id, 10)

    def test_hidden_fifth_slot_other_country_and_missing_live_source_fail_closed(self):
        state = state_two_source_leagues()
        original = context(state)
        german = original.accept_native_radio_event(2)
        self.assertEqual(german.active_country_id, 33)
        self.assertEqual(german.selected_division_index, 0)
        with self.assertRaisesRegex(OriginalLeagueTablesSelectorError, "unconstructed"):
            german.accept_native_radio_event(13)
        with self.assertRaisesRegex(ManagementPresentationError, "context-zero"):
            bridge(state).source_selected_nonpl_league_table_rows(german)
        returned = german.accept_native_radio_event(1)
        self.assertEqual(returned.selected_competition_id, 7)
        self.assertEqual(returned.selected_division_index, 4)

    def test_tamper_unconstructed_selectors_and_original_premier_fixed_path_refused(self):
        state = state_two_source_leagues()
        selection = context(state).accept_native_radio_event(10)
        variants = (
            replace(selection, selected_division_index=True),
            replace(selection, active_country_index=-1),
            replace(selection, division_candidates=tuple(
                (((99, "invented"),) if i == 0 else row)
                for i, row in enumerate(selection.division_candidates))),
            replace(selection, human_competition_id=0),
        )
        for altered in variants:
            with self.subTest(altered=altered):
                with self.assertRaises(ManagementPresentationError):
                    bridge(state).source_selected_nonpl_league_table_rows(altered)
        with self.assertRaisesRegex(ManagementPresentationError, "distinct fixed source"):
            bridge(state).source_selected_nonpl_league_table_rows(
                context(state).accept_native_radio_event(9))
        for invalid in (0, 16, True, "10", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(OriginalLeagueTablesSelectorError):
                    selection.accept_native_radio_event(invalid)


if __name__ == "__main__":
    unittest.main()
