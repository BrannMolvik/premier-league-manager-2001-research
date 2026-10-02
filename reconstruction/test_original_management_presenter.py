from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import unittest

from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl
from gate13_management_source_data import ClubHeaderView
from original_management_presenter import (
    OriginalManagementPresentationError,
    build_fresh_management_snapshot,
)


class Backend:
    def select_club(self, club_id):
        return ("manager", club_id)


@dataclass(frozen=True)
class Row:
    source_roster_index: int
    player_id: int
    full_name: str
    current_position: int = 12
    condition: int = 90
    recent_form_average: float = 7.0
    current_role_rating: int = 61


class Bridge:
    def __init__(self, backend):
        self.backend = backend

    def club_header(self):
        return ClubHeaderView(12, "Source Club", "Source", date(2000, 8, 1))

    def squad_rows(self):
        return tuple(Row(i, 1000 + i, f"Player {i}") for i in range(23))


class OriginalManagementPresenterTests(unittest.TestCase):
    def test_integration_presenter_has_no_direct_simulation_import(self):
        source = Path(__file__).with_name("original_management_presenter.py").read_text(
            encoding="utf-8"
        )
        for forbidden in (
            "human_gameplay",
            "game_state",
            "match_engine",
            "season_scheduler",
        ):
            self.assertNotIn(forbidden, source)

    def started_session(self):
        session = FrontEndSession(Backend)
        session.dispatch(StartMenuControl.NEW_GAME)
        session.choose_club(12)
        session.dispatch(TeamSelectControl.START_CONTINUE)
        return session

    def test_teamselect_start_composes_fresh_team_squad_landing(self):
        snapshot = build_fresh_management_snapshot(
            self.started_session(), bridge_factory=Bridge
        )

        self.assertEqual(snapshot.club.name, "Source Club")
        self.assertEqual((snapshot.menu.selected_root_id, snapshot.menu.selected_child_id), (2, 0xCE))
        self.assertEqual(snapshot.menu.rows[0].caption, "Team")
        self.assertEqual(snapshot.menu.rows[1].caption, "Squad")
        self.assertEqual(snapshot.source_squad_count, 23)
        self.assertEqual(snapshot.rows_beyond_initial_viewport, 3)
        self.assertEqual(len(snapshot.squad.rows), 20)
        self.assertEqual(tuple(row.player_id for row in snapshot.squad.rows), tuple(range(1000, 1020)))

    def test_management_composition_rejects_pre_start_session(self):
        with self.assertRaisesRegex(
            OriginalManagementPresentationError,
            "TeamSelect Start",
        ):
            build_fresh_management_snapshot(
                FrontEndSession(Backend), bridge_factory=Bridge
            )

    def test_first_screen_presenter_method_uses_same_seam(self):
        from original_first_screen_presenter import OriginalFirstScreenPresenter

        presenter = object.__new__(OriginalFirstScreenPresenter)
        presenter.session = self.started_session()
        snapshot = presenter.fresh_management_snapshot(bridge_factory=Bridge)
        self.assertEqual(snapshot.club.club_id, 12)
        self.assertEqual(snapshot.menu.selected_child_id, 0xCE)


if __name__ == "__main__":
    unittest.main()
