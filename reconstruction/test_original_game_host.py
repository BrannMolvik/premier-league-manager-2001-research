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
from gate13_management_source_data import (
    ClubHeaderView,
    LeagueFixturesGridSourceView,
)
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
from gate13_original_pixel_preview import encode_rgba_png
from original_game_host import (
    DEFAULT_SOURCE_ROOT,
    OriginalGameHostError,
    OriginalGameTkHost,
    build_original_game_presenter,
    play_configured_startup_media,
    _scaled_rgba,
)
from original_management_presenter import OriginalManagementPresenter
from original_management_text import load_verified_management_text_resources
from original_league_tables_presenter import build_league_tables_snapshot
from original_management_header import (
    HEADER_COMPOUND_RECT,
    OriginalManagementHeaderResources,
)
from original_pmatchinfo_presenter import build_staged_pmatchinfo_snapshot
from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES,
)
from original_pmenu_chrome import PMENU_FONT_SOURCE_PATH
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_squad_resources import squad_view_transition
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

    def league_fixtures_grid_source(self):
        return LeagueFixturesGridSourceView(
            competition_id=0,
            member_club_ids=(12, 13),
            scheduled_matchday_count=2,
            schedule_cycle_count=2,
            matrix_layer_count=1,
            fixtures_in_source_order=(),
        )


def management_factory(session):
    return OriginalManagementPresenter(session, bridge_factory=Bridge)


def fake_pmenu_render():
    return SimpleNamespace(
        overlays=(
            SimpleNamespace(
                x=0,
                y=0,
                png=encode_rgba_png(1, 1, bytes((1, 2, 3, 255))),
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


class FakeHeaderFont:
    def measure_text(self, text):
        if text != "MENU":
            raise AssertionError(text)
        return 20

    def render_text_alpha(self, text):
        if text != "MENU":
            raise AssertionError(text)
        return SimpleNamespace(
            width=20,
            height=5,
            alpha=bytes([255]) * 100,
        )


def fake_management_header_resources():
    return OriginalManagementHeaderResources(
        EA444DecodedImage(
            30,
            4845,
            bytes((11, 11, 11, 255)) * (30 * 4845),
            consumed_bits=0,
            transparent_pixels=0,
        ),
        EA444DecodedImage(
            70,
            380,
            bytes((22, 22, 22, 255)) * (70 * 380),
            consumed_bits=0,
            transparent_pixels=0,
        ),
        FakeHeaderFont(),
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


class LeagueFixturesPagePresenter:
    def __init__(self):
        self.calls = []

    def source_accepted_league_fixtures_page(self, direction):
        self.calls.append(direction)
        return SimpleNamespace(
            direction=direction,
            previous_offset=0,
            column_offset=8,
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
        self.values.setdefault("bindings", {})[args[0]] = (args, kwargs)


class FakeRoot(FakeWidget):
    def after_idle(self, callback):
        queue = self.values.setdefault('idle', {})
        key = max(queue, default=0) + 1
        queue[key] = callback
        return key

    def after_cancel(self, key):
        self.values.setdefault('idle', {}).pop(key, None)

    def run_idle(self):
        queue = self.values.setdefault('idle', {})
        key = next(iter(queue))
        queue.pop(key)()

    def title(self, value):
        self.values["title"] = value

    def resizable(self, x, y):
        self.values["resizable"] = (x, y)

    def configure(self, **kwargs):
        self.values["configure"] = kwargs

    def attributes(self, name, value):
        self.values.setdefault("attributes", {})[name] = value

    def destroy(self):
        self.values["destroyed"] = True


class FakeCanvas(FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.images = []
        self.delete_count = 0
        self.itemconfigure_count = 0

    def delete(self, *args):
        self.delete_count += 1
        self.images = []

    def create_image(self, x, y, **kwargs):
        self.images.append((x, y, kwargs))
        return len(self.images)

    def itemconfigure(self, item_id, **kwargs):
        self.itemconfigure_count += 1
        x, y, current = self.images[item_id - 1]
        updated = dict(current)
        updated.update(kwargs)
        self.images[item_id - 1] = (x, y, updated)


class FakeTk:
    NW = "nw"
    Canvas = FakeCanvas

    class PhotoImage:
        def __init__(self, *, data, format):
            assert format == "png"
            assert b64decode(data).startswith(b"\x89PNG\r\n\x1a\n")
            self.data = data
            raw = b64decode(data)
            self.width = int.from_bytes(raw[16:20], "big")
            self.height = int.from_bytes(raw[20:24], "big")
            self.zoom_factor = 1

        def zoom(self, x, y):
            assert x == y
            clone = object.__new__(type(self))
            clone.data = self.data
            clone.zoom_factor = self.zoom_factor * x
            clone.subsample_factor = getattr(self, "subsample_factor", 1)
            return clone

        def subsample(self, x, y):
            assert x == y
            clone = object.__new__(type(self))
            clone.data = self.data
            clone.zoom_factor = getattr(self, "zoom_factor", 1)
            clone.subsample_factor = getattr(self, "subsample_factor", 1) * x
            return clone


class LargeFakeRoot(FakeRoot):
    def winfo_screenwidth(self):
        return 2560

    def winfo_screenheight(self):
        return 1440


class FullHDFakeRoot(FakeRoot):
    def winfo_screenwidth(self):
        return 1920

    def winfo_screenheight(self):
        return 1080


class OriginalGameHostTests(unittest.TestCase):
    def test_fullhd_fullscreen_fills_height_without_vertical_bars(self):
        root = FullHDFakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)

        self.assertEqual(
            (host.display_scale_num, host.display_scale_den),
            (9, 5),
        )
        self.assertEqual(host.canvas.kwargs["width"], 1440)
        self.assertEqual(host.canvas.kwargs["height"], 1080)
        background = host._first_screen_photo_cache[
            (FrontEndScreen.START_MENU, "background")
        ]
        self.assertEqual((background.width, background.height), (1440, 1080))

    def test_high_resolution_fullscreen_uses_fractional_scale_and_native_pointer_mapping(self):
        root = LargeFakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)

        self.assertEqual((host.display_scale_num, host.display_scale_den), (12, 5))
        self.assertAlmostEqual(host.display_scale, 12 / 5)
        self.assertEqual(host.canvas.kwargs["width"], 1920)
        self.assertEqual(host.canvas.kwargs["height"], 1440)
        background = host._first_screen_photo_cache[
            (FrontEndScreen.START_MENU, "background")
        ]
        self.assertEqual((background.width, background.height), (1920, 1440))
        self.assertEqual(getattr(background, "zoom_factor", 1), 1)
        event = SimpleNamespace(
            x=host._native_to_display(7),
            y=host._native_to_display(478),
            widget=host.canvas,
        )
        native = host._normalize_pointer_event(event)
        self.assertEqual((native.x, native.y), (7, 478))

    def test_direct_scaler_never_builds_an_oversized_intermediate_surface(self):
        width, height, rgba = _scaled_rgba(
            8,
            6,
            bytes((10, 20, 30, 255)) * (8 * 6),
            7,
            4,
        )
        self.assertEqual((width, height), (14, 11))
        self.assertEqual(len(rgba), 14 * 11 * 4)
        self.assertEqual(rgba[:4], bytes((10, 20, 30, 255)))
        self.assertEqual(rgba[-4:], bytes((10, 20, 30, 255)))

    def test_quit_to_windows_destroys_host_after_recovered_event(self):
        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(live, root, FakeTk)
        quit_overlay = next(
            item
            for item in host.first_screen_frame.original_source_frame_overlays
            if item.event == 4
        )

        host.on_click(
            SimpleNamespace(
                x=quit_overlay.rect.x + 1,
                y=quit_overlay.rect.y + 1,
            )
        )

        self.assertTrue(root.values["destroyed"])
        self.assertEqual(host.last_status, "QUIT_TO_WINDOWS")

    def test_management_resources_are_loaded_only_on_explicit_management_boundary(self):
        calls = []
        payload = {
            "management_pmenu_resources": object(),
            "league_fixtures_grid_art": object(),
            "fixtures_pager_art": object(),
            "squad_top_resources": object(),
            "league_tables_header_art": object(),
            "pmatchinfo_snapshot": object(),
            "pmatchinfo_font": object(),
            "pmatchinfo_nested_font": object(),
            "pmatchinfo_script_art": object(),
            "management_background": object(),
            "management_header_resources": object(),
            "management_text_resources": object(),
        }

        def loader():
            calls.append("load")
            return payload

        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_resource_loader=loader,
        )
        self.assertEqual(calls, [])
        self.assertFalse(host._management_resources_loaded)

        host._ensure_management_resources()
        self.assertEqual(calls, ["load"])
        self.assertTrue(host._management_resources_loaded)
        host._ensure_management_resources()
        self.assertEqual(calls, ["load"])
        for name, value in payload.items():
            self.assertIs(getattr(host, name), value)

    def test_game_host_starts_fullscreen_and_preserves_native_canvas_size(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)

        self.assertTrue(host._fullscreen)
        self.assertTrue(root.values["attributes"]["-fullscreen"])
        self.assertEqual(root.values["configure"]["background"], "black")
        self.assertEqual(host.canvas.kwargs["width"], 800)
        self.assertEqual(host.canvas.kwargs["height"], 600)
        self.assertTrue(host.canvas.values["pack"]["expand"])

        host.leave_fullscreen()
        self.assertFalse(host._fullscreen)
        self.assertFalse(root.values["attributes"]["-fullscreen"])
        host.toggle_fullscreen()
        self.assertTrue(host._fullscreen)
        self.assertTrue(root.values["attributes"]["-fullscreen"])

    def test_first_screen_photo_cache_reuses_background_and_source_frame_images(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        first_cache_size = len(host._first_screen_photo_cache)

        # A redraw at the same native frame must reuse all immutable images.
        host.redraw()
        self.assertEqual(len(host._first_screen_photo_cache), first_cache_size)

        # One native hover step may add only the newly reached source frame
        # (and, if its endpoint color changes, one caption image), never a
        # second 800x600 background image.
        event = host.first_screen_frame.original_source_frame_overlays[0].event
        rect = host.first_screen_frame.original_source_frame_overlays[0].rect
        host.on_fixtures_pager_motion(SimpleNamespace(x=rect.x, y=rect.y))
        root.run_idle()
        self.assertIn(
            (FrontEndScreen.START_MENU, "background"),
            host._first_screen_photo_cache,
        )
        backgrounds = [
            key for key in host._first_screen_photo_cache
            if len(key) >= 2 and key[1] == "background"
        ]
        self.assertEqual(backgrounds, [(FrontEndScreen.START_MENU, "background")])

    def test_teamselect_club_toggle_updates_only_existing_row_layers(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        host.presenter.session.navigation.screen = FrontEndScreen.TEAM_SELECT

        row = SimpleNamespace(
            row_kind="club",
            source_id=77,
            animation_source_index=0,
            bar_source_index=0,
            animation_frame=SimpleNamespace(
                width=1, height=1, rgba=bytes((1, 2, 3, 255))
            ),
            bar_frame=SimpleNamespace(
                width=1, height=1, rgba=bytes((4, 5, 6, 255))
            ),
            glyph_mask=SimpleNamespace(
                width=1, height=1, alpha=bytes((255,))
            ),
            native_color_16=0xFFFF,
            text="Southport",
        )
        host.presenter.snapshot = lambda: SimpleNamespace(
            screen=FrontEndScreen.TEAM_SELECT,
            club_rows=(row,),
        )
        host.canvas.images = [
            (0, 0, {"image": object()}),
            (0, 0, {"image": object()}),
            (0, 0, {"image": object()}),
        ]
        host._first_screen_items = {
            ("team-row-animation", "club", 77): 1,
            ("team-row-bar", "club", 77): 2,
            ("team-row-text", "club", 77): 3,
        }
        before_delete_count = host.canvas.delete_count

        self.assertTrue(host._update_teamselect_club_row(77))
        self.assertEqual(host.canvas.delete_count, before_delete_count)
        self.assertEqual(host.canvas.itemconfigure_count, 3)

    def test_first_screen_idle_animation_does_not_rebuild_canvas(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        overlay = host.first_screen_frame.original_source_frame_overlays[0]
        before_delete_count = host.canvas.delete_count
        before_items = len(host.canvas.images)

        host.on_fixtures_pager_motion(
            SimpleNamespace(x=overlay.rect.x, y=overlay.rect.y)
        )
        root.run_idle()

        self.assertEqual(host.canvas.delete_count, before_delete_count)
        self.assertEqual(len(host.canvas.images), before_items)
        self.assertGreater(host.canvas.itemconfigure_count, 0)

    def test_source_idle_hover_advances_and_retreats_one_frame_per_pass(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        event = host.first_screen_frame.original_source_frame_overlays[0].event
        rect = host.first_screen_frame.original_source_frame_overlays[0].rect
        host.on_fixtures_pager_motion(SimpleNamespace(x=rect.x, y=rect.y))
        for index in range(1, 11):
            self.assertEqual(len(root.values['idle']), 1)
            root.run_idle()
            frames = {o.event: o.source_frame_index for o in host.first_screen_frame.original_source_frame_overlays}
            self.assertEqual(frames[event], index)
            self.assertTrue(all(v == 0 for k, v in frames.items() if k != event))
        self.assertFalse(root.values['idle'])
        host.on_fixtures_pager_leave(None)
        for index in range(9, -1, -1):
            root.run_idle()
            self.assertEqual(host.first_screen_frame.original_source_frame_overlays[0].source_frame_index, index)
        self.assertFalse(root.values['idle'])

    def test_rejected_start_is_visible_and_retains_retryable_selection(self):
        live = presenter()
        messages = []
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
                                  error_reporter=messages.append)
        host.on_click(SimpleNamespace(x=7, y=478))
        live.session.choose_club(999)
        def reject(club_id):
            raise ValueError(f"club {club_id} is not in the Premier League")
        live.session.gameplay.select_club = reject
        host.on_click(SimpleNamespace(x=426, y=301))
        self.assertEqual(messages, ["ValueError: club 999 is not in the Premier League"])
        self.assertEqual(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertEqual(live.session.selected_club_ids, (999,))
        self.assertFalse(live.session.started)

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
            bind_args, bind_kwargs = host.canvas.values["bindings"]["<Button-1>"]
            self.assertEqual(bind_args[0], "<Button-1>")
            self.assertIs(bind_args[1].__self__, host)
            self.assertEqual(bind_args[1].__func__, host.on_click.__func__)
            self.assertEqual(bind_kwargs, {})
            self.assertEqual(host.canvas.values["bindings"]["<ButtonRelease-1>"][0][1].__func__,
                             host.on_script_arrow_release.__func__)
            self.assertEqual(len(host.canvas.images), 9)

            host.on_click(SimpleNamespace(x=7, y=478))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
            self.assertEqual(len(host.canvas.images), 3)

            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
            self.assertTrue(live.session.started)
            self.assertEqual(live.session.gameplay.selections, [12])
            self.assertFalse(host.pmenu_popup_active)
            self.assertEqual(len(host.canvas.images), 6)
            host.on_click(SimpleNamespace(x=600, y=1))
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

    def test_management_header_draws_exact_two_bitmaps_plus_menu_caption(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        host.canvas.delete("all")
        host._photos = []

        count = host._draw_management_header()

        self.assertEqual(count, 3)
        self.assertEqual(len(host.canvas.images), 3)
        self.assertEqual(host.canvas.images[0][:2], (599, 0))
        self.assertEqual(host.canvas.images[1][:2], (629, 0))
        self.assertEqual(host.canvas.images[2][:2], (681, 62))

    def test_management_header_hover_uses_one_idle_update_per_pass(self):
        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        host.management_presenter = object()

        x, y, _w, _h = HEADER_COMPOUND_RECT
        with patch.object(host, "redraw") as redraw:
            host.on_fixtures_pager_motion(SimpleNamespace(x=x, y=y))
            self.assertEqual(len(root.values["idle"]), 1)
            root.run_idle()
            redraw.assert_called_once_with()

        self.assertEqual(host.management_header_state.left_subframe, 1)
        self.assertEqual(host.management_header_state.right_subframe, 1)

        with patch.object(host, "redraw") as redraw:
            host.on_fixtures_pager_leave(None)
            root.run_idle()
            redraw.assert_called_once_with()
        self.assertEqual(host.management_header_state.left_subframe, 0)
        self.assertEqual(host.management_header_state.right_subframe, 0)

    def test_management_header_selected_state_follows_open_pmenu(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        host.pmenu_popup_active = True
        host.canvas.delete("all")
        host._photos = []

        host._draw_management_header()
        self.assertTrue(host.management_header_state.pending())
        host.management_header_state.update()
        frame = host.management_header_state.source_frame()
        self.assertEqual((frame.left_source_row, frame.right_source_row), (50, 2))

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
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=squad_view_transition(3),
            )
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
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=squad_view_transition(3),
            )
        )
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "verified original top-control resources",
        ):
            host._draw_squad_top_controls(frame)

    def test_post_transition_squad_pixels_fail_closed_until_their_state_is_proven(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            squad_top_resources=fake_squad_top_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=squad_view_transition(4),
            )
        )

        count = host._draw_squad_top_controls(frame)

        self.assertEqual(count, 0)
        self.assertEqual(host.canvas.images, [])
        self.assertEqual(host._photos, [])

    def test_source_accepted_squad_view_seam_changes_only_proven_container_state(self):
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
            host.on_click(SimpleNamespace(x=7, y=478))
            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            host.on_click(SimpleNamespace(x=600, y=1))
            self.assertEqual(len(host.canvas.images), 7)

            activation = host.apply_source_accepted_squad_view(4)
            self.assertEqual(activation.transition.control_id, 4)
            self.assertEqual(activation.transition.left_roster, "first")
            self.assertFalse(activation.transition.second_roster_mask1)
            self.assertTrue(activation.transition.pitch_mask1)
            self.assertEqual(activation.transition.pitch_team_index, 0)
            self.assertEqual(len(host.canvas.images), 1)
            self.assertIn("source-accepted Squad view transition", host.last_status)
            self.assertIn("formation/player pixels remain fail-closed", host.last_status)

            # A normal modern click inside the top-control region is still not
            # promoted into control 3/4/5 event equivalence.
            before = host.management_presenter.squad_view_control_id
            host.on_click(SimpleNamespace(x=120, y=180))
            self.assertEqual(host.management_presenter.squad_view_control_id, before)
            self.assertIn("no source-bounded PMenu candidate row", host.last_status)

            restored = host.apply_source_accepted_squad_view(3)
            self.assertEqual(restored.transition.control_id, 3)
            self.assertEqual(len(host.canvas.images), 7)

    def test_native_league_fixtures_grid_left_press_uses_exact_source_control(self):
        live = presenter()
        with patch(
            "original_game_host.build_management_pmenu_render",
            side_effect=lambda frame, resources: fake_pmenu_render(),
        ):
            host = OriginalGameTkHost(
                live,
                FakeRoot(),
                FakeTk,
                management_presenter_factory=management_factory,
                management_pmenu_resources=object(),
                squad_top_resources=fake_squad_top_resources(),
            )
            host.on_click(SimpleNamespace(x=7, y=478))
            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            host.management_presenter.navigate(0x25C)

            # Exact PLeagueGrid screen origin (378,235), cell (1,0).
            with patch.object(host, "redraw") as redraw:
                host.on_click(SimpleNamespace(x=378 + 29 + 1, y=235 + 1))

        activation = host.last_league_fixtures_grid_activation
        self.assertIsNotNone(activation)
        self.assertEqual((activation.column, activation.row), (1, 0))
        self.assertIsNone(activation.fixture_id)
        self.assertFalse(
            any(
                cell.selected
                for cell in activation.presentation.league_fixtures.cells
            )
        )
        redraw.assert_called_once_with()
        self.assertIn("League Fixtures source grid press", host.last_status)
        self.assertIn("column 1, row 0", host.last_status)

    def test_native_grid_press_is_noop_outside_source_grid_and_keeps_page_buttons_unmapped(self):
        live = presenter()
        with patch(
            "original_game_host.build_management_pmenu_render",
            side_effect=lambda frame, resources: fake_pmenu_render(),
        ):
            host = OriginalGameTkHost(
                live,
                FakeRoot(),
                FakeTk,
                management_presenter_factory=management_factory,
                management_pmenu_resources=object(),
                squad_top_resources=fake_squad_top_resources(),
            )
            host.on_click(SimpleNamespace(x=7, y=478))
            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            host.management_presenter.navigate(0x25C)

            # Outside the exact 378..725 x 235..570 grid and outside PMenu.
            host.on_click(SimpleNamespace(x=350, y=200))

        self.assertIsNone(host.last_league_fixtures_grid_activation)
        self.assertIn("no source-bounded PMenu candidate row", host.last_status)
        self.assertIn("League Fixtures grid control", host.last_status)

    def test_source_accepted_league_fixtures_page_host_seam_redraws_without_pointer_mapping(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk)
        # Enter MANAGEMENT through the same source-backed Start route as the
        # application host. Do not fabricate navigation state that violates the
        # completed-TeamSelect invariant enforced by the management canvas.
        host.on_click(SimpleNamespace(x=7, y=478))
        live.choose_club(12)
        # Start must still run through the real host/session transition, but the
        # test backend intentionally lacks the unrelated management source-data
        # surface. Suppress only the automatic post-Start redraw until the
        # paging stub is installed.
        with patch.object(host, "redraw"):
            host.on_click(SimpleNamespace(x=426, y=301))
        self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
        self.assertTrue(live.session.started)
        page_presenter = LeagueFixturesPagePresenter()
        host.management_presenter = page_presenter

        with patch.object(host, "redraw") as redraw:
            activation = host.apply_source_accepted_league_fixtures_page(1)

        self.assertEqual(page_presenter.calls, [1])
        self.assertEqual((activation.previous_offset, activation.column_offset), (0, 8))
        redraw.assert_called_once_with()
        self.assertIn("source-accepted League Fixtures page transition", host.last_status)
        self.assertIn("0 -> 8", host.last_status)
        self.assertIn("pointer mapping remains fail-closed", host.last_status)

    def test_source_accepted_league_fixtures_page_requires_management_host(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "requires the MANAGEMENT host",
        ):
            host.apply_source_accepted_league_fixtures_page(1)

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

    def test_league_tables_draws_source_qualified_row_text(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_text_resources=load_verified_management_text_resources(source_root),
        )
        host.canvas.delete("all")
        host._photos = []
        snapshot = build_league_tables_snapshot(
            (
                SimpleNamespace(
                    position=1,
                    club_id=0,
                    club_name="Arsenal",
                    played=1,
                    wins=1,
                    draws=0,
                    losses=0,
                    goals_for=2,
                    goals_against=0,
                    points=3,
                ),
            )
        )
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PLeagueTables",
                league_tables=snapshot,
            )
        )

        count = host._draw_league_tables_row_text(frame)

        self.assertEqual(count, 9)
        self.assertEqual(len(host.canvas.images), 9)
        self.assertEqual(len(host._photos), 9)
        # Club text is left-aligned in the exact 214x12 source control.
        self.assertEqual(host.canvas.images[1][0], 316)

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
                self.assertNotIn("team", calls)
                built._ensure_team_select_resources()

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