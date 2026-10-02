from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_management_source_data import ClubHeaderView
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_game_host import (
    DEFAULT_SOURCE_ROOT,
    OriginalGameTkHost,
    build_original_game_presenter,
)
from original_management_presenter import OriginalManagementPresenter
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import fixture as team_fixture


class StubBackend:
    def __init__(self):
        self.selections = []

    def select_club(self, club_id):
        self.selections.append(club_id)
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
        return (Row(0, 1000, "Player 0"),)


def management_factory(session):
    return OriginalManagementPresenter(session, bridge_factory=Bridge)


def presenter():
    return OriginalFirstScreenPresenter(
        FrontEndSession(StubBackend),
        assemble_original_pstartmenu_inputs(*menu_fixture()),
        assemble_original_teamselect_inputs(*team_fixture()),
    )


class FakeWidget:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.values = {}

    def pack(self, **kwargs):
        self.values["pack"] = kwargs

    def bind(self, *args, **kwargs):
        self.values["bind"] = (args, kwargs)


class FakeRoot(FakeWidget):
    def title(self, value):
        self.values["title"] = value

    def resizable(self, x, y):
        self.values["resizable"] = (x, y)


class FakeCanvas(FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = []

    def delete(self, *args):
        self.images = []

    def create_image(self, x, y, **kwargs):
        self.images.append((x, y, kwargs))


class FakeTk:
    NW = "nw"
    Canvas = FakeCanvas

    class PhotoImage:
        def __init__(self, *, data, format):
            assert format == "png"
            assert b64decode(data).startswith(b"\x89PNG\r\n\x1a\n")
            self.data = data


class OriginalGameHostTests(unittest.TestCase):
    def test_clean_host_routes_first_screens_into_fixed_management_without_debug_ui(self):
        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_presenter_factory=management_factory,
        )

        self.assertEqual(root.values["title"], "Premier League Manager 2001")
        self.assertEqual(host.canvas.kwargs["width"], 800)
        self.assertEqual(host.canvas.kwargs["height"], 600)
        self.assertEqual(len(host.canvas.images), 9)

        host.on_click(SimpleNamespace(x=7, y=478))
        self.assertIs(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertEqual(len(host.canvas.images), 3)

        live.choose_club(12)
        host.on_click(SimpleNamespace(x=426, y=301))
        self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
        self.assertTrue(live.session.started)
        self.assertEqual(live.session.gameplay.selections, [12])
        self.assertEqual(host.canvas.images, [])
        self.assertIn("Management host active", host.last_status)

        host.on_click(SimpleNamespace(x=700, y=120))
        self.assertIn("PMenu input is not yet source-bound", host.last_status)

    def test_default_source_root_is_repository_original_asset_store(self):
        self.assertEqual(
            DEFAULT_SOURCE_ROOT.name,
            "source",
        )
        self.assertEqual(DEFAULT_SOURCE_ROOT.parent.name, "original_assets")

    def test_presenter_loader_uses_canonical_game_executable_and_imported_source_root(self):
        calls = {}

        def load_menu(**kwargs):
            calls["menu"] = kwargs
            return object()

        def load_team(**kwargs):
            calls["team"] = kwargs
            return object()

        fake_session = object()
        with tempfile.TemporaryDirectory() as temp:
            game_dir = Path(temp) / "game"
            source_root = Path(temp) / "source"
            game_dir.mkdir()
            source_root.mkdir()
            with patch(
                "original_game_host.load_verified_english_pstartmenu_inputs",
                side_effect=load_menu,
            ), patch(
                "original_game_host.load_verified_original_teamselect_inputs",
                side_effect=load_team,
            ), patch(
                "original_game_host.FrontEndSession.for_canonical_game_dir",
                return_value=fake_session,
            ):
                built = build_original_game_presenter(
                    game_dir,
                    source_root=source_root,
                )

        self.assertIs(built.session, fake_session)
        self.assertEqual(
            calls["menu"]["original_executable"],
            game_dir / "FOOTBAL.EXE",
        )
        self.assertEqual(
            calls["menu"]["original_art_dir"],
            source_root / "FM2001_Art",
        )
        self.assertEqual(
            calls["menu"]["original_language_dir"],
            source_root,
        )
        self.assertEqual(
            calls["menu"]["original_zurich_font20"],
            source_root / "Fonts" / "Zurich_BdXCn_BT_20pixel.fnt",
        )
        self.assertEqual(
            calls["team"]["original_executable"],
            game_dir / "FOOTBAL.EXE",
        )
        self.assertEqual(
            calls["team"]["original_art_dir"],
            source_root / "FM2001_Art",
        )


if __name__ == "__main__":
    unittest.main()
