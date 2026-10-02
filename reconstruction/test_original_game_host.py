from __future__ import annotations

from base64 import b64decode
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from ea444_decoder import EA444DecodedImage
from ea_font import EAFont
from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_management_source_data import ClubHeaderView
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_league_fixtures_art import build_league_fixtures_grid_art
from original_league_fixtures_resources import (
    FIXTURES_HORIZONTAL_GRID,
    FIXTURES_VERTICAL_GRID,
    LEAGUE_FIXTURES_MATCH_INFO_ACTION,
)
from original_league_tables_art import build_league_tables_header_art
from original_league_tables_resources import (
    LEAGUE_TABLES_BAR_RECT,
    LEAGUE_TABLES_RESOURCES,
    LEAGUE_TABLES_RESOURCE_BY_NAME,
)
from original_game_host import (
    DEFAULT_SOURCE_ROOT,
    OriginalGameHostError,
    OriginalGameTkHost,
    build_original_game_presenter,
    play_configured_startup_media,
)
from original_management_presenter import OriginalManagementPresenter
from original_pmatchinfo_presenter import build_staged_pmatchinfo_snapshot
from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES,
)
from original_pmenu_chrome import PMENU_FONT_SOURCE_PATH
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_squad_top_controls import OriginalSquadTopResources

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


def fake_squad_top_resources():
    root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
    font = EAFont.from_bytes((root / PMENU_FONT_SOURCE_PATH).read_bytes())
    width, height = 73, 575
    return OriginalSquadTopResources(
        EA444DecodedImage(
            width,
            height,
            bytes((17, 17, 17, 255)) * (width * height),
            consumed_bits=0,
            transparent_pixels=0,
        ),
        font,
    )


def fake_fixture_grid_art():
    def image(resource, marker):
        width, height = resource.size
        return EA444DecodedImage(
            width,
            height,
            bytes((marker, marker, marker, 255)) * (width * height),
            consumed_bits=0,
            transparent_pixels=0,
        )

    return build_league_fixtures_grid_art(
        {
            FIXTURES_VERTICAL_GRID.name: image(FIXTURES_VERTICAL_GRID, 17),
            FIXTURES_HORIZONTAL_GRID.name: image(FIXTURES_HORIZONTAL_GRID, 33),
        }
    )


def fake_pmatchinfo_snapshot():
    decoded = {}
    for index, name in enumerate(PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES):
        resource = PMATCHINFO_RESOURCE_BY_NAME[name]
        marker = (index * 13) % 240
        decoded[name] = EA444DecodedImage(
            resource.size[0],
            resource.size[1],
            bytes((marker, marker, marker, 255))
            * (resource.size[0] * resource.size[1]),
            consumed_bits=0,
            transparent_pixels=0,
        )
    return build_staged_pmatchinfo_snapshot(
        decoded,
        require_complete_dialog=True,
    )


class MatchInfoActionPresenter:
    def fixture_match_info_action(
        self,
        *,
        fixture_present,
        linked_context_available,
    ):
        if fixture_present and linked_context_available:
            return LEAGUE_FIXTURES_MATCH_INFO_ACTION
        return None


def fake_league_tables_header_art():
    resource = LEAGUE_TABLES_RESOURCE_BY_NAME["league_bar"]
    image = EA444DecodedImage(
        resource.size[0],
        resource.size[1],
        bytes((55, 55, 55, 255)) * (resource.size[0] * resource.size[1]),
        consumed_bits=0,
        transparent_pixels=0,
    )
    return build_league_tables_header_art(
        image,
        staged_resource_names=tuple(item.name for item in LEAGUE_TABLES_RESOURCES),
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
                squad_top_resources=fake_squad_top_resources(),
            )

            self.assertEqual(root.values["title"], "Premier League Manager 2001")
            self.assertEqual(host.canvas.kwargs["width"], 800)
            self.assertEqual(host.canvas.kwargs["height"], 600)
            bind_args, bind_kwargs = host.canvas.values["bind"]
            self.assertEqual(bind_args[0], "<Button-1>")
            self.assertIs(bind_args[1].__self__, host)
            self.assertEqual(bind_args[1].__func__, host.on_click.__func__)
            self.assertEqual(bind_kwargs, {})
            self.assertEqual(len(host.canvas.images), 9)

            host.on_click(SimpleNamespace(x=7, y=478))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
            self.assertEqual(len(host.canvas.images), 3)

            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
            self.assertTrue(live.session.started)
            self.assertEqual(live.session.gameplay.selections, [12])
            self.assertEqual(len(host.canvas.images), 7)
            self.assertIn("source PMenu rows rendered", host.last_status)
            self.assertIn("6 source panel bitmaps rendered", host.last_status)
            self.assertIn("surrounding management background unresolved", host.last_status)

            before = host.management_presenter.snapshot()
            self.assertEqual(before.panel_code, 0xCE)

            host.on_click(SimpleNamespace(x=700, y=120))
            self.assertIn("PMenu source pointer press", host.last_status)
            self.assertIn("no_action 0x2", host.last_status)
            after = host.management_presenter.snapshot()
            self.assertEqual(after.panel_code, 0xCE)
            self.assertEqual(after.menu.selected_child_id, 0xCE)
            self.assertEqual(len(host.canvas.images), 7)

            # The ninth fresh visible row is Calendar.  Tk <Button-1> is a press,
            # matching the recovered SelectBmp +0x6C input virtual.
            host.on_click(SimpleNamespace(x=700, y=96 + 8 * 29))
            native = host.management_presenter.snapshot()
            self.assertEqual(native.panel_code, 0xCE)
            self.assertEqual(native.menu.selected_root_id, 0x259)
            self.assertIn("expand_root 0x259", host.last_status)
            self.assertEqual(len(host.canvas.images), 7)

            accepted = host.apply_source_accepted_pmenu_action("title", 3, 0)
            self.assertTrue(accepted.action.accepted)
            self.assertEqual(accepted.action.action_kind, "expand_root")
            self.assertEqual(accepted.presentation.panel_code, 0xCE)
            self.assertEqual(accepted.presentation.menu.selected_root_id, 3)
            self.assertEqual(accepted.presentation.menu.selected_child_id, 0xCE)
            self.assertIn("source-accepted PMenu action", host.last_status)
            self.assertEqual(len(host.canvas.images), 7)

            host.on_click(SimpleNamespace(x=100, y=120))
            self.assertIn("no source-bounded PMenu candidate row", host.last_status)
            self.assertEqual(host.management_presenter.snapshot().panel_code, 0xCE)
            self.assertEqual(len(host.canvas.images), 7)

    def test_squad_landing_draws_only_six_source_backed_top_control_overlays(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            squad_top_resources=fake_squad_top_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(panel_class="PSquadScreen")
        )

        count = host._draw_squad_top_controls(frame)

        self.assertEqual(count, 6)
        self.assertEqual(len(host.canvas.images), 6)
        self.assertEqual(len(host._photos), 6)
        self.assertEqual(host.canvas.images[0][:2], (37, 171))
        self.assertEqual(host.canvas.images[2][:2], (113, 171))
        self.assertEqual(host.canvas.images[4][:2], (189, 171))

    def test_squad_landing_fails_closed_without_verified_top_control_resources(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        frame = SimpleNamespace(
            presentation=SimpleNamespace(panel_class="PSquadScreen")
        )
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "verified original top-control resources",
        ):
            host._draw_squad_top_controls(frame)

    def test_league_fixtures_draws_only_the_36_position_proven_grid_bitmaps(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        host.league_fixtures_grid_art = fake_fixture_grid_art()
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueFixtures",
                league_fixtures=SimpleNamespace(exact_art_staged=True),
            )
        )

        count = host._draw_league_fixtures_grid_art(frame)

        self.assertEqual(count, 36)
        self.assertEqual(len(host.canvas.images), 36)
        self.assertEqual(len(host._photos), 36)
        self.assertEqual(host.canvas.images[0][:2], (378, 98))
        self.assertEqual(host.canvas.images[11][:2], (697, 98))
        self.assertEqual(host.canvas.images[12][:2], (241, 235))
        self.assertEqual(host.canvas.images[-1][:2], (241, 557))

    def test_league_tables_draws_only_the_source_proven_header_band(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        host.league_tables_header_art = fake_league_tables_header_art()
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueTables",
                league_tables=SimpleNamespace(exact_art_staged=True),
            )
        )

        count = host._draw_league_tables_header_art(frame)

        self.assertEqual(count, 1)
        self.assertEqual(len(host.canvas.images), 1)
        self.assertEqual(len(host._photos), 1)
        self.assertEqual(host.canvas.images[0][:2], LEAGUE_TABLES_BAR_RECT[:2])

    def test_league_tables_header_fails_closed_without_complete_staging(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        host.league_tables_header_art = fake_league_tables_header_art()
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueTables",
                league_tables=SimpleNamespace(exact_art_staged=False),
            )
        )
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "all 15 verified original assets",
        ):
            host._draw_league_tables_header_art(frame)

    def test_league_fixtures_grid_art_fails_closed_without_complete_staging(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        host.league_fixtures_grid_art = fake_fixture_grid_art()
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueFixtures",
                league_fixtures=SimpleNamespace(exact_art_staged=False),
            )
        )
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "all six verified original assets",
        ):
            host._draw_league_fixtures_grid_art(frame)

    def test_source_accepted_pmatchinfo_persists_exact_popup_for_redraw(self):
        live = presenter()
        host = OriginalGameTkHost(
            live,
            FakeRoot(),
            FakeTk,
            pmatchinfo_snapshot=fake_pmatchinfo_snapshot(),
        )
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = MatchInfoActionPresenter()

        with patch.object(host, "redraw") as redraw:
            action = host.apply_source_accepted_fixture_match_info(
                fixture_present=True,
                linked_context_available=True,
                pointer_x=400,
                pointer_y=300,
            )

        self.assertIs(action, LEAGUE_FIXTURES_MATCH_INFO_ACTION)
        self.assertEqual(
            (host.active_pmatchinfo_art.x, host.active_pmatchinfo_art.y),
            (20, 50),
        )
        redraw.assert_called_once_with()
        self.assertIn("source-accepted PMatchInfo", host.last_status)
        self.assertIn("owner-local child art remains fail-closed", host.last_status)

        host.canvas.delete("all")
        host._photos = []
        self.assertEqual(host._draw_pmatchinfo_dialog(), 1)
        self.assertEqual(host.canvas.images[-1][:2], (20, 50))

    def test_source_accepted_pmatchinfo_keeps_missing_context_fail_closed(self):
        live = presenter()
        host = OriginalGameTkHost(
            live,
            FakeRoot(),
            FakeTk,
            pmatchinfo_snapshot=fake_pmatchinfo_snapshot(),
        )
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = MatchInfoActionPresenter()

        with patch.object(host, "redraw") as redraw:
            action = host.apply_source_accepted_fixture_match_info(
                fixture_present=True,
                linked_context_available=False,
                pointer_x=400,
                pointer_y=300,
            )

        self.assertIsNone(action)
        self.assertIsNone(host.active_pmatchinfo_art)
        redraw.assert_not_called()
        self.assertIn("rejected by recovered fixture gates", host.last_status)

    def test_source_accepted_pmatchinfo_requires_verified_popup_snapshot(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk)
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = MatchInfoActionPresenter()

        with self.assertRaisesRegex(
            OriginalGameHostError,
            "verified complete popup snapshot",
        ):
            host.apply_source_accepted_fixture_match_info(
                fixture_present=True,
                linked_context_available=True,
                pointer_x=400,
                pointer_y=300,
            )

    def test_pmatchinfo_exit_and_pointer_interaction_remain_explicit(self):
        live = presenter()
        host = OriginalGameTkHost(
            live,
            FakeRoot(),
            FakeTk,
            pmatchinfo_snapshot=fake_pmatchinfo_snapshot(),
        )
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = MatchInfoActionPresenter()
        snapshot = fake_pmatchinfo_snapshot()
        from original_pmatchinfo_art import build_pmatchinfo_popup_art
        host.active_pmatchinfo_art = build_pmatchinfo_popup_art(
            snapshot,
            pointer_x=799,
            pointer_y=599,
        )

        host.on_click(SimpleNamespace(x=40, y=110))
        self.assertIn("pointer interaction remains fail-closed", host.last_status)
        self.assertEqual(
            (host.active_pmatchinfo_art.x, host.active_pmatchinfo_art.y),
            (39, 99),
        )

        with patch.object(host, "redraw") as redraw:
            host.apply_source_accepted_pmatchinfo_exit()
        self.assertIsNone(host.active_pmatchinfo_art)
        redraw.assert_called_once_with()
        self.assertIn("Closed source-accepted PMatchInfo", host.last_status)

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
