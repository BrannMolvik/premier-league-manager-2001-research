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
    OriginalGameHostError,
    OriginalGameTkHost,
    build_original_game_presenter,
    play_configured_startup_media,
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


def fake_pmenu_render():
    return SimpleNamespace(
        overlays=(
            SimpleNamespace(
                x=0,
                y=0,
                png=b"\x89PNG\r\n\x1a\nsource-backed-test-overlay",
            ),
        ),
    )


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
        with patch(
            "original_game_host.build_management_pmenu_render",
            side_effect=lambda frame, resources: fake_pmenu_render(),
        ):
            host = OriginalGameTkHost(
                live,
                root,
                FakeTk,
                management_presenter_factory=management_factory,
                management_pmenu_resources=object(),
            )

            self.assertEqual(root.values["title"], "Premier League Manager 2001")
            self.assertEqual(host.canvas.kwargs["width"], 800)
            self.assertEqual(host.canvas.kwargs["height"], 600)
            self.assertEqual(host.canvas.values["bind"][0], ("<Button-1>",))
            self.assertEqual(len(host.canvas.images), 9)

            host.on_click(SimpleNamespace(x=7, y=478))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
            self.assertEqual(len(host.canvas.images), 3)

            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
            self.assertTrue(live.session.started)
            self.assertEqual(live.session.gameplay.selections, [12])
            self.assertEqual(len(host.canvas.images), 1)
            self.assertIn("source PMenu rows rendered", host.last_status)
            self.assertIn("surrounding management background unresolved", host.last_status)

            before = host.management_presenter.snapshot()
            self.assertEqual(before.panel_code, 0xCE)

            host.on_click(SimpleNamespace(x=700, y=120))
            self.assertIn("PMenu source pointer press", host.last_status)
            self.assertIn("no_action 0x2", host.last_status)
            after = host.management_presenter.snapshot()
            self.assertEqual(after.panel_code, 0xCE)
            self.assertEqual(after.menu.selected_child_id, 0xCE)
            self.assertEqual(len(host.canvas.images), 1)

            # The ninth fresh visible row is Calendar.  Tk <Button-1> is a press,
            # matching the recovered SelectBmp +0x6C input virtual.
            host.on_click(SimpleNamespace(x=700, y=96 + 8 * 29))
            native = host.management_presenter.snapshot()
            self.assertEqual(native.panel_code, 0xCE)
            self.assertEqual(native.menu.selected_root_id, 0x259)
            self.assertIn("expand_root 0x259", host.last_status)
            self.assertEqual(len(host.canvas.images), 1)

            accepted = host.apply_source_accepted_pmenu_action("title", 3, 0)
            self.assertTrue(accepted.action.accepted)
            self.assertEqual(accepted.action.action_kind, "expand_root")
            self.assertEqual(accepted.presentation.panel_code, 0xCE)
            self.assertEqual(accepted.presentation.menu.selected_root_id, 3)
            self.assertEqual(accepted.presentation.menu.selected_child_id, 0xCE)
            self.assertIn("source-accepted PMenu action", host.last_status)
            self.assertEqual(len(host.canvas.images), 1)

            host.on_click(SimpleNamespace(x=100, y=120))
            self.assertIn("no source-bounded PMenu candidate row", host.last_status)
            self.assertEqual(host.management_presenter.snapshot().panel_code, 0xCE)
            self.assertEqual(len(host.canvas.images), 1)

    def test_management_redraw_requires_verified_pmenu_resources(self):
        live = presenter()
        host = OriginalGameTkHost(
            live,
            FakeRoot(),
            FakeTk,
            management_presenter_factory=management_factory,
        )
        host.on_click(SimpleNamespace(x=7, y=478))
        live.choose_club(12)
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "verified original row resources",
        ):
            host.on_click(SimpleNamespace(x=426, y=301))

    def test_source_accepted_pmenu_seam_rejects_pre_management_host(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "requires the MANAGEMENT host",
        ):
            host.apply_source_accepted_pmenu_action("title", 0x259, 0)
    def test_startup_media_runtime_integration_requires_explicit_receipt_and_backend(self):
        self.assertIsNone(
            play_configured_startup_media(
                receipt_path=None,
                backend=None,
            )
        )

        backend = object()
        receipt = Path("/private/startup-receipt.json")
        repo_root = Path("/repo")
        with patch(
            "original_game_host.load_and_play_verified_startup_sequence",
            return_value="summary",
        ) as play:
            result = play_configured_startup_media(
                receipt_path=receipt,
                backend=backend,
                repo_root=repo_root,
            )

        self.assertEqual(result, "summary")
        play.assert_called_once_with(
            receipt_path=receipt,
            repo_root=repo_root,
            backend=backend,
        )

        for bad_receipt, bad_backend in (
            (receipt, None),
            (None, backend),
        ):
            with self.subTest(receipt=bad_receipt, backend=bad_backend):
                with self.assertRaises(OriginalGameHostError):
                    play_configured_startup_media(
                        receipt_path=bad_receipt,
                        backend=bad_backend,
                    )

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
