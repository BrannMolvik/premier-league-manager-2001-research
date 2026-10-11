"""Gate13 non-pointer selected-League native event integration regressions.

The producer remains the separately source-audited original-selected League
member/373-head calendar bridge. No test authorizes UI hit-test acceptance.
"""
from __future__ import annotations

from datetime import date
from types import SimpleNamespace
import unittest

from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl
from gate13_management_source_data import (
    ClubHeaderView,
    ManagementSourceDataBridge,
    ManagementPresentationError,
)
from original_management_presenter import (
    OriginalManagementPresenter,
    OriginalManagementPresentationError,
)
from test_original_management_presenter import Backend, Bridge
from test_original_league_fixtures_selected_source import state_two_source_leagues


class AuthenticSelectedLeagueBridge(Bridge):
    """Reuse the real source-qualified bridge; fake only unrelated shell rows."""

    def __init__(self, backend):
        super().__init__(backend)
        self.source = ManagementSourceDataBridge(SimpleNamespace(
            state=state_two_source_leagues(),
            human=SimpleNamespace(club_id=349),
        ))

    def club_header(self):
        return ClubHeaderView(349, "Southport", "Southport", date(2000, 8, 1))

    def league_fixtures_grid_source(self):
        return self.source.league_fixtures_grid_source()

    def original_league_fixtures_selection_context(self):
        return self.source.original_league_fixtures_selection_context()

    def source_selected_nonpl_league_fixtures_grid_source(self, context):
        return self.source.source_selected_nonpl_league_fixtures_grid_source(context)

    def source_selected_league_fixtures_grid_source(self, context):
        return self.source.source_selected_league_fixtures_grid_source(context)


def started_session():
    session = FrontEndSession(Backend)
    session.dispatch(StartMenuControl.NEW_GAME)
    session.choose_club(12)
    session.dispatch(TeamSelectControl.START_CONTINUE)
    return session


class SourceSelectedRadioEventPresenterTests(unittest.TestCase):
    def presenter(self):
        return OriginalManagementPresenter(
            started_session(), bridge_factory=AuthenticSelectedLeagueBridge,
        )

    def test_source_accepted_event_switches_actual_calendar_without_fake_manager(self):
        panel = self.presenter()
        original = panel.navigate(0x25C)
        self.assertEqual(original.league_fixtures.competition_id, 7)
        self.assertIsNone(original.league_fixtures_selection)

        activation = panel.source_accepted_league_fixtures_radio_event(10)
        self.assertEqual(activation.event_id, 10)
        self.assertEqual(activation.selection.selected_competition_id, 2)
        self.assertEqual(activation.presentation.league_fixtures.competition_id, 2)
        self.assertEqual(activation.presentation.league_fixtures_selection,
                         activation.selection)
        self.assertEqual(
            tuple(row.source_node_token
                  for row in activation.presentation.fixtures_in_source_order),
            (("alt", 1), ("alt", 0)),
        )
        self.assertTrue(all(row.fixture_id is None
                            for row in activation.presentation.fixtures_in_source_order))
        texts = sorted(cell.text for cell in activation.presentation.league_fixtures.cells
                       if cell.text is not None)
        self.assertEqual(texts, ["17.08", "3:1"])
        self.assertEqual(panel.snapshot(), activation.presentation)
        self.assertEqual(panel.league_fixtures_column_offset, 0)

    def test_unqualified_country_or_premier_does_not_change_committed_selection(self):
        panel = self.presenter()
        panel.navigate(0x25C)
        accepted = panel.source_accepted_league_fixtures_radio_event(10)
        previous = accepted.presentation
        context = panel.league_fixtures_selection
        for event in (9, 2):
            with self.subTest(event=event):
                with self.assertRaises(ManagementPresentationError):
                    panel.source_accepted_league_fixtures_radio_event(event)
                self.assertEqual(panel.league_fixtures_selection, context)
                self.assertEqual(panel.snapshot(), previous)

    def test_unconstructed_and_invalid_native_events_fail_without_mutation(self):
        panel = self.presenter()
        panel.navigate(0x25C)
        for event in (14, 15, True, "10", None):
            with self.subTest(event=event):
                with self.assertRaises(OriginalManagementPresentationError):
                    panel.source_accepted_league_fixtures_radio_event(event)
                self.assertIsNone(panel.league_fixtures_selection)
                self.assertEqual(panel.snapshot().league_fixtures.competition_id, 7)

    def test_event_outside_original_league_fixtures_panel_refuses_action(self):
        panel = self.presenter()
        with self.assertRaisesRegex(
            OriginalManagementPresentationError, "require the integrated"
        ):
            panel.source_accepted_league_fixtures_radio_event(10)
        self.assertEqual(panel.selected_child_id, 0xCE)
        self.assertIsNone(panel.league_fixtures_selection)

    def test_new_panel_construction_resets_selected_source_and_column_window(self):
        panel = self.presenter()
        panel.navigate(0x25C)
        panel.source_accepted_league_fixtures_radio_event(10)
        panel.navigate(0x25A)
        self.assertIsNone(panel.league_fixtures_selection)
        self.assertEqual(panel.navigate(0x25C).league_fixtures.competition_id, 7)
        self.assertEqual(panel.league_fixtures_column_offset, 0)


if __name__ == "__main__":
    unittest.main()
