"""Original PLeagueTables native-event-to-presentation transaction regressions.

Actual selected-table rows come from the strict real Recovery511 management
bridge. The unrelated original PMenu test shell is stubbed only to exercise
the UI-independent navigation event seam, never original mouse acceptance.
"""
from __future__ import annotations

import unittest

from gate13_management_source_data import ManagementPresentationError
from original_management_presenter import (
    OriginalManagementPresenter,
    OriginalManagementPresentationError,
)
from test_original_management_league_fixtures_radio_events import (
    AuthenticSelectedLeagueBridge,
    started_session,
)


class SourceSelectedTablesBridge(AuthenticSelectedLeagueBridge):
    def league_table_rows(self):
        return self.source.league_table_rows()

    def original_league_tables_selection_context(self):
        return self.source.original_league_tables_selection_context()

    def source_selected_nonpl_league_table_rows(self, selection):
        return self.source.source_selected_nonpl_league_table_rows(selection)


class OriginalLeagueTablesNativeEventsTests(unittest.TestCase):
    def presenter(self):
        return OriginalManagementPresenter(
            started_session(), bridge_factory=SourceSelectedTablesBridge,
        )

    def test_real_source_country_division_event_projects_other_league_standings(self):
        presenter = self.presenter()
        initial = presenter.navigate(0x25A)
        self.assertEqual(len(initial.league_tables.rows), 2)
        self.assertIsNone(initial.league_tables_selection)

        activated = presenter.source_accepted_league_tables_radio_event(10)
        self.assertEqual(activated.event_id, 10)
        self.assertEqual(activated.selection.active_country_id, 26)
        self.assertEqual(activated.selection.selected_competition_id, 2)
        self.assertEqual(activated.selection.selected_division_index, 1)
        self.assertEqual(activated.presentation.league_tables_selection, activated.selection)
        self.assertEqual(tuple(row.club_id for row in activated.presentation.league_tables.rows),
                         (10, 11))
        self.assertEqual(tuple(row.points for row in activated.presentation.league_tables.rows),
                         (3, 0))
        self.assertEqual(presenter.snapshot(), activated.presentation)

    def test_current_form_and_distinct_fixed_premier_source_fail_atomically(self):
        presenter = self.presenter()
        presenter.navigate(0x25A)
        good = presenter.source_accepted_league_tables_radio_event(10)
        prior = presenter.snapshot()
        for event in (15, 9):
            with self.subTest(event=event):
                with self.assertRaises(ManagementPresentationError):
                    presenter.source_accepted_league_tables_radio_event(event)
                self.assertEqual(presenter.league_tables_selection, good.selection)
                self.assertEqual(presenter.snapshot(), prior)

    def test_missing_live_foreign_country_does_not_replace_last_complete_table(self):
        presenter = self.presenter()
        presenter.navigate(0x25A)
        stable = presenter.source_accepted_league_tables_radio_event(10)
        with self.assertRaises(ManagementPresentationError):
            presenter.source_accepted_league_tables_radio_event(2)
        self.assertEqual(presenter.snapshot(), stable.presentation)
        self.assertEqual(presenter.league_tables_selection, stable.selection)

    def test_invalid_source_radio_events_leave_original_panel_unmodified(self):
        presenter = self.presenter()
        presenter.navigate(0x25A)
        initial = presenter.snapshot()
        for invalid in (0, 16, 100, True, "10", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(OriginalManagementPresentationError):
                    presenter.source_accepted_league_tables_radio_event(invalid)
                self.assertIsNone(presenter.league_tables_selection)
                self.assertEqual(presenter.snapshot(), initial)

    def test_wrong_panel_and_new_panel_constructor_reset_selection(self):
        presenter = self.presenter()
        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "requires the integrated PLeagueTables",
        ):
            presenter.source_accepted_league_tables_radio_event(10)
        presenter.navigate(0x25A)
        presenter.source_accepted_league_tables_radio_event(10)
        self.assertIsNotNone(presenter.league_tables_selection)
        presenter.navigate(0x25C)
        self.assertIsNone(presenter.league_tables_selection)
        again = presenter.navigate(0x25A)
        self.assertIsNone(again.league_tables_selection)
        self.assertEqual(tuple(row.club_id for row in again.league_tables.rows),
                         tuple(row.club_id for row in presenter.snapshot().league_tables.rows))


if __name__ == "__main__":
    unittest.main()
