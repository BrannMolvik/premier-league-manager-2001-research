"""Native PLeagueTables event15 data-state, NOT original alternate-row raster/mouse."""
from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace as Obj
import unittest

from gate13_management_source_data import (
    LeagueCurrentFormSourceRowView, ManagementSourceDataBridge,
    ManagementPresentationError,
)
from original_league_tables_current_form_data_snapshot import (
    OriginalLeagueTablesCurrentFormDataError,
    OriginalLeagueTablesCurrentFormDataSnapshot,
    build_league_tables_current_form_data_snapshot,
)
from original_management_presenter import (
    OriginalManagementPresenter, OriginalManagementPresentationError,
)
from test_original_management_league_tables_radio_events import SourceSelectedTablesBridge
from test_original_management_league_fixtures_radio_events import started_session
from test_original_league_tables_current_form_selected_bridge import nonpl_ready, premier_ready


def presenter_from_source(state):
    class SelectedCurrentFormBridge(SourceSelectedTablesBridge):
        def __init__(self, backend):
            super().__init__(backend)
            self.source = ManagementSourceDataBridge(
                Obj(state=state, human=Obj(club_id=349))
            )

    return OriginalManagementPresenter(
        started_session(), bridge_factory=SelectedCurrentFormBridge,
    )


class SourceSelectedLeagueTablesCurrentFormPresentationTests(unittest.TestCase):
    def test_nonpl_event15_is_native_six_result_data_not_seven_stat_row(self):
        state, _ = nonpl_ready()
        presenter = presenter_from_source(state)
        initial = presenter.navigate(0x25A)
        self.assertIsNotNone(initial.league_tables)
        self.assertIsNone(initial.league_tables_current_form)
        prior = presenter.source_accepted_league_tables_radio_event(10)
        self.assertEqual(prior.selection.selected_competition_id, 2)
        self.assertIsNotNone(prior.presentation.league_tables)

        action = presenter.source_accepted_league_tables_radio_event(15)
        self.assertEqual(action.event_id, 15)
        self.assertEqual(action.selection.sort_state, 1)
        self.assertIsNone(action.presentation.league_tables)
        data = action.presentation.league_tables_current_form
        self.assertIsInstance(data, OriginalLeagueTablesCurrentFormDataSnapshot)
        self.assertEqual((data.competition_id, data.country_id, data.sort_state),
                         (2, 26, 1))
        self.assertEqual(tuple((r.club_id, r.form_score) for r in data.rows),
                         ((10, 4), (11, 1)))
        self.assertEqual(data.rows[0].six_form_labels,
                         (" ", " ", " ", " ", "D", "W"))
        self.assertEqual(data.rows[1].six_form_labels,
                         (" ", " ", " ", " ", "D", "L"))
        self.assertFalse(data.native_alternate_row_geometry_recovered)
        self.assertFalse(data.native_mouse_event15_recovered)
        self.assertEqual(presenter.snapshot(), action.presentation)
        self.assertEqual(state.club_competition_membership[349], 7)

        restored = presenter.source_accepted_league_tables_radio_event(14)
        self.assertEqual(restored.selection.sort_state, 0)
        self.assertIsNone(restored.presentation.league_tables_current_form)
        self.assertIsNotNone(restored.presentation.league_tables)
        self.assertEqual(tuple(r.club_id for r in restored.presentation.league_tables.rows),
                         (10, 11))
        self.assertEqual(presenter.snapshot(), restored.presentation)

    def test_premier0_fixed_380_member_sort_is_separate_source_owner(self):
        state, _ = premier_ready()
        presenter = presenter_from_source(state)
        presenter.navigate(0x25A)
        position = presenter.source_accepted_league_tables_radio_event(9)
        self.assertEqual(position.selection.selected_competition_id, 0)
        self.assertEqual(len(position.presentation.league_tables.rows), 20)
        form = presenter.source_accepted_league_tables_radio_event(15)
        self.assertIsNone(form.presentation.league_tables)
        snapshot = form.presentation.league_tables_current_form
        self.assertEqual(snapshot.competition_id, 0)
        self.assertEqual(len(snapshot.rows), 20)
        self.assertEqual({r.club_id for r in snapshot.rows}, set(range(1000, 1020)))
        by_club = {r.club_id: r for r in snapshot.rows}
        self.assertEqual(by_club[1000].six_form_labels[-1], "W")
        self.assertEqual(by_club[1001].six_form_labels[-1], "L")
        self.assertEqual(state.club_competition_membership[349], 7)

    def test_missing_source_season_does_not_commit_event15(self):
        state, _ = nonpl_ready()
        presenter = presenter_from_source(state)
        presenter.navigate(0x25A)
        accepted = presenter.source_accepted_league_tables_radio_event(10)
        prior = accepted.presentation
        state.competitions[2].scheduled_matchday_count = 4
        with self.assertRaisesRegex(ManagementPresentationError, "fixture count"):
            presenter.source_accepted_league_tables_radio_event(15)
        self.assertEqual(presenter.league_tables_selection, accepted.selection)
        # Restore the deliberately corrupted backing source before rebuilding
        # any *new* snapshot. A transactional event cannot repair live data.
        state.competitions[2].scheduled_matchday_count = 2
        self.assertEqual(presenter.snapshot(), prior)

    def test_new_original_panel_discards_unpainted_current_form_state(self):
        state, _ = nonpl_ready()
        presenter = presenter_from_source(state)
        presenter.navigate(0x25A)
        presenter.source_accepted_league_tables_radio_event(10)
        accepted = presenter.source_accepted_league_tables_radio_event(15)
        self.assertIsNotNone(accepted.presentation.league_tables_current_form)
        presenter.navigate(0x25C)
        self.assertIsNone(presenter.league_tables_selection)
        fresh = presenter.navigate(0x25A)
        self.assertIsNone(fresh.league_tables_current_form)
        self.assertIsNotNone(fresh.league_tables)

    def test_source_only_row_validator_cannot_promote_fabricated_layout(self):
        state, selected = nonpl_ready()
        source = ManagementSourceDataBridge(
            Obj(state=state, human=Obj(club_id=349))
        )
        rows = source.source_selected_league_current_form_rows(selected)
        view = build_league_tables_current_form_data_snapshot(selected, rows)
        self.assertEqual(view.rows, rows)
        with self.assertRaisesRegex(OriginalLeagueTablesCurrentFormDataError, "unproven"):
            replace(view, native_mouse_event15_recovered=True)
        with self.assertRaisesRegex(OriginalLeagueTablesCurrentFormDataError, "unproven"):
            replace(view, native_alternate_row_geometry_recovered=True)
        with self.assertRaisesRegex(OriginalLeagueTablesCurrentFormDataError, "native event15"):
            build_league_tables_current_form_data_snapshot(
                selected.accept_native_radio_event(14), rows,
            )
        for malformed in (
            (replace(rows[0], form_score=True), rows[1]),
            (replace(rows[0], six_form_labels=("W",) * 5), rows[1]),
            (replace(rows[0], six_form_labels=("W",) * 5 + ("?",)), rows[1]),
            (replace(rows[0], source_index=3), rows[1]),
            (rows[0], replace(rows[1], club_id=rows[0].club_id)),
        ):
            with self.subTest(malformed=malformed):
                with self.assertRaises(OriginalLeagueTablesCurrentFormDataError):
                    build_league_tables_current_form_data_snapshot(selected, malformed)

    def test_legacy_missing_source_still_cannot_turn_event15_into_fake_table(self):
        from test_original_management_league_tables_radio_events import (
            SourceSelectedTablesBridge,
        )
        presenter = OriginalManagementPresenter(
            started_session(), bridge_factory=SourceSelectedTablesBridge,
        )
        presenter.navigate(0x25A)
        prior = presenter.source_accepted_league_tables_radio_event(10)
        with self.assertRaises(ManagementPresentationError):
            presenter.source_accepted_league_tables_radio_event(15)
        self.assertEqual(presenter.league_tables_selection, prior.selection)
        self.assertEqual(presenter.snapshot(), prior.presentation)


if __name__ == "__main__":
    unittest.main()
