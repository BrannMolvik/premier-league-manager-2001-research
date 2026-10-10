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
from human_gameplay import OriginalResultsProgress
from match_detail_mode import MatchDetailMode
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
    DEFAULT_PSTARTMENU_DERIVATIVE_ROOT,
    DEFAULT_SOURCE_ROOT,
    PSTARTMENU_DERIVATIVE_DECODER,
    PSTARTMENU_DERIVATIVE_MANIFEST_SHA256,
    OriginalGameHostError,
    OriginalGameTkHost,
    build_original_game_presenter,
    play_configured_startup_media,
    _cached_runtime_png,
    _scaled_rgba,
)
from original_management_presenter import OriginalManagementPresenter
from original_management_text import load_verified_management_text_resources
from original_league_tables_presenter import build_league_tables_snapshot
from original_management_header import (
    HEADER_COMPOUND_RECT,
    OriginalManagementHeaderResources,
    management_header_club_name_overlay,
    validate_management_header_club_name_font,
)
from original_pmatchinfo_presenter import build_staged_pmatchinfo_snapshot
from original_pmatchinfo_resources import (
    PMATCHINFO_RESOURCE_BY_NAME,
    PMATCHINFO_STAGED_PRESENTATION_RESOURCE_NAMES,
)
from original_pmenu_chrome import PMENU_FONT_SOURCE_PATH
from original_prematch_panel import PREMATCH_SELECTORS
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_squad_resources import squad_view_transition
from original_squad_status import (
    OriginalSquadStatusResources,
    load_verified_squad_status_resources,
)
from original_squad_row_style import (
    OriginalSquadRowTextResources,
    load_verified_squad_row_text_resources,
)
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
    first_name: str
    surname: str
    full_name: str
    positions: tuple[int, int, int] = (12, 4, 7)
    current_position: int = 12
    assigned_role_abbreviation: str = "FC"
    match_active: bool = True
    match_substitute_available: bool = False
    condition: int = 90
    recent_form_average: float = 7.0
    current_role_rating: int = 61
    injured: bool = False
    suspended: bool = False
    international: bool = False


class Bridge:
    def __init__(self, backend):
        self.backend = backend

    def club_header(self):
        return ClubHeaderView(12, "Source Club", "Source", date(2000, 8, 1))

    def squad_rows(self):
        return (Row(0, 1000, "Player", "0", "Player 0"),)

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


def fake_squad_row_text_resources():
    root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
    resources = load_verified_squad_row_text_resources(root)
    if not isinstance(resources, OriginalSquadRowTextResources):
        raise AssertionError("unexpected Squad row text resource type")
    return resources


def fake_squad_status_resources():
    root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
    resources = load_verified_squad_status_resources(root)
    if not isinstance(resources, OriginalSquadStatusResources):
        raise AssertionError("unexpected Squad status resource type")
    return resources


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


class FakeHeaderDateFont:
    atlas_width = 1261
    atlas_height = 17

    def measure_text(self, text):
        return 100

    def native_line_height(self):
        return 18

    def render_text_alpha(self, text):
        return SimpleNamespace(
            width=100,
            height=10,
            alpha=bytes([255]) * 1000,
        )


def fake_management_header_resources(*, club_name_font=None):
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
        FakeHeaderDateFont(),
        club_name_font=club_name_font,
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

    def after(self, delay_ms, callback):
        queue = self.values.setdefault('timers', {})
        key = max(queue, default=1000) + 1
        queue[key] = (delay_ms, callback)
        return key

    def after_cancel(self, key):
        self.values.setdefault('idle', {}).pop(key, None)
        self.values.setdefault('timers', {}).pop(key, None)

    def run_idle(self):
        queue = self.values.setdefault('idle', {})
        key = next(iter(queue))
        queue.pop(key)()

    def run_timer(self):
        queue = self.values.setdefault('timers', {})
        key = next(iter(queue))
        _delay_ms, callback = queue.pop(key)
        callback()

    def title(self, value):
        self.values["title"] = value

    def resizable(self, x, y):
        self.values["resizable"] = (x, y)

    def configure(self, **kwargs):
        self.values.setdefault("configure", {}).update(kwargs)

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

    def configure(self, **kwargs):
        self.kwargs.update(kwargs)

    def coords(self, item, *values):
        self.values.setdefault('coords', {})[item] = values

    def delete(self, *args):
        self.delete_count += 1
        self.images = []

    def create_image(self, x, y, **kwargs):
        self.images.append((x, y, kwargs))
        return len(self.images)

    def create_rectangle(self, x0, y0, x1, y1, **kwargs):
        rectangles = self.values.setdefault("rectangles", [])
        rectangles.append((x0, y0, x1, y1, kwargs))
        return ("rectangle", len(rectangles))

    def tag_raise(self, item_id):
        self.values["tag_raise"] = item_id

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


class DeferredThread:
    def __init__(self, *, target, daemon):
        self.target = target
        self.daemon = daemon
        self.started = False

    def start(self):
        self.started = True

    def run(self):
        if not self.started:
            raise AssertionError("thread must be started before run")
        self.target()


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
    def test_normal_menu_motion_uses_shared_idle_and_only_updates_existing_bitmaps(self):
        from test_original_management_canvas import _pmenu_resources
        live, root = presenter(), FakeRoot()
        host = OriginalGameTkHost(live, root, FakeTk,
            management_presenter_factory=management_factory,
            management_pmenu_resources=_pmenu_resources(),
            squad_top_resources=fake_squad_top_resources(),
            squad_row_text_resources=fake_squad_row_text_resources())
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)
        host.on_click(SimpleNamespace(x=426, y=301))
        host.on_click(SimpleNamespace(x=640, y=30))
        counts = host.canvas.delete_count, len(host.canvas.images), len(host._photos)
        with patch.object(host.management_presenter, 'snapshot', side_effect=AssertionError('hover snapshot')), \
                patch.object(host, 'redraw', side_effect=AssertionError('hover redraw')):
            host.on_fixtures_pager_motion(SimpleNamespace(x=640, y=155))
            for frame in range(1, 11):
                root.run_idle()
                self.assertEqual(host._pmenu_animation.snapshot().rows[2].arrow_frame, frame)
            self.assertFalse(root.values['idle'])
            self.assertEqual(host._pmenu_animation.snapshot().rows[2].background_state_bits, 10)
            host.on_fixtures_pager_motion(SimpleNamespace(x=790, y=598))
            for frame in range(9, -1, -1):
                root.run_idle()
                self.assertEqual(host._pmenu_animation.snapshot().rows[2].arrow_frame, frame)
            self.assertFalse(root.values['idle'])
        self.assertEqual((host.canvas.delete_count, len(host.canvas.images), len(host._photos)), counts)
        self.assertGreater(host.canvas.itemconfigure_count, 0)
        self.assertEqual(host.management_presenter.selected_child_id, 0xCE)

    def test_normal_game_options_return_main_and_continue_preserve_live_game(self):
        for club_id in (12, 13):
            with self.subTest(club_id=club_id), patch(
                    'original_game_host.build_management_pmenu_render',
                    side_effect=lambda *_: fake_pmenu_render()):
                live = presenter()
                host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
                    management_presenter_factory=management_factory,
                    management_pmenu_resources=object(),
                    squad_top_resources=fake_squad_top_resources(),
                    squad_row_text_resources=fake_squad_row_text_resources())
                host.on_click(SimpleNamespace(x=141, y=512))
                live.choose_club(club_id)
                host.on_click(SimpleNamespace(x=426, y=301))
                gameplay = live.session.gameplay
                host.on_click(SimpleNamespace(x=640, y=30))
                menu = host.management_presenter.snapshot().menu
                options = next(row for row in menu.rows if row.row_kind == 'title' and row.menu_id == 8)
                host.on_click(SimpleNamespace(x=640, y=96 + options.y + 10))
                menu = host.management_presenter.snapshot().menu
                back = next(row for row in menu.rows if row.menu_id == 0x323)
                host.on_click(SimpleNamespace(x=640, y=96 + back.y + 10))
                self.assertIs(live.session.navigation.screen, FrontEndScreen.START_MENU)
                self.assertIs(live.session.gameplay, gameplay)
                self.assertTrue(live.session.started)
                self.assertFalse(host.pmenu_popup_active)
                self.assertIsNone(host.management_presenter)
                self.assertEqual(gameplay.selections, [club_id])
                control = next(c for c in live.snapshot().controls if int(c.event) == 1)
                host.on_click(SimpleNamespace(x=control.rect.x + 5, y=control.rect.y + 5))
                self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
                self.assertIs(live.session.gameplay, gameplay)
                self.assertEqual(gameplay.selections, [club_id])
                self.assertEqual(host.management_presenter.selected_child_id, 0xCE)

    def test_next_press_runs_off_tk_and_publishes_only_after_successful_poll(self):
        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(live, root, FakeTk,
            management_presenter_factory=management_factory,
            management_thread_factory=DeferredThread)
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)
        with patch.object(host, 'redraw'):
            host.on_click(SimpleNamespace(x=426, y=301))
        gameplay = live.session.gameplay
        gameplay.turns = 0
        gameplay.state = SimpleNamespace(calendar=SimpleNamespace(current_date=date(2000, 8, 1)))

        def advance(staged):
            staged.turns += 1
            return SimpleNamespace(pending_primary_entry=None)

        with patch.object(StubBackend, 'advance_original_management', advance, create=True), \
                patch.object(host, 'redraw'):
            host.on_click(SimpleNamespace(x=750, y=40))
            thread = host._management_turn_thread
            self.assertTrue(thread.started)
            self.assertEqual(host.management_next_flags & 0x10, 0x10)
            self.assertEqual(gameplay.turns, 0)
            host.on_click(SimpleNamespace(x=750, y=40))
            self.assertIs(host._management_turn_thread, thread)
            thread.run()
            self.assertEqual(gameplay.turns, 0)
            host._poll_original_management_turn()
            self.assertEqual(gameplay.turns, 1)
            self.assertIsNone(host._management_turn_thread)
            self.assertEqual(host.management_next_flags, 2)
            self.assertIn('2000-08-01', host.last_status)

    def test_next_failure_leaves_live_state_retryable_and_owns_all_pointer_input(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
            management_thread_factory=DeferredThread, error_reporter=lambda text: None)
        live.session.gameplay = StubBackend()
        live.session.gameplay.turns = 0

        def advance(staged):
            staged.turns += 1
            raise RuntimeError('unresolved native event')

        with patch.object(StubBackend, 'advance_original_management', advance, create=True), \
                patch.object(host, 'redraw'), patch('sys.stderr'):
            host._begin_original_management_turn()
            with patch.object(host, '_normalize_pointer_event', side_effect=AssertionError('input leaked')):
                host.on_click(None)
                host.on_fixture_report_press(None)
                host.on_script_arrow_release(None)
            host._management_turn_thread.run()
            host._poll_original_management_turn()
            self.assertEqual(live.session.gameplay.turns, 0)
            self.assertIn('unresolved native event', host.last_status)
            self.assertEqual(host.management_next_flags, 2)
            self.assertIsNone(host._management_turn_thread)

    def test_pending_match_owns_every_background_pointer_path_after_poll(self):
        live = presenter()
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
            management_thread_factory=DeferredThread)
        live.session.gameplay = StubBackend()
        live.session.gameplay.pending_primary_entry = ('premier_league', 7)
        host._squad_drag_source = ('retained',)
        before = (
            host.pmenu_popup_active,
            host.management_next_flags,
            dict(host.fixtures_pager_flags),
            host._squad_drag_source,
        )
        event = SimpleNamespace(x=640, y=30)
        host.on_click(event)
        host.on_fixture_report_press(event)
        host.on_script_arrow_release(event)
        host.on_fixtures_pager_motion(event)
        host._begin_original_management_turn()
        self.assertIsNone(host._management_turn_thread)
        self.assertEqual((
            host.pmenu_popup_active,
            host.management_next_flags,
            host.fixtures_pager_flags,
            host._squad_drag_source,
        ), before)

    def test_explicit_quick_selector_calculates_once_and_returns_to_management(self):
        live = presenter()
        host = OriginalGameTkHost(
            live, FakeRoot(), FakeTk,
            management_thread_factory=DeferredThread,
            prematch_resource_loader=lambda staged, pending: SimpleNamespace(),
        )
        gameplay = StubBackend()
        live.session.gameplay = gameplay
        live.session.started = True
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        live.session.match_detail_settings_owner_present = False
        gameplay.pending_primary_entry = None
        gameplay.matches = 0
        gameplay.turns = 0
        entry = ('premier_league', 7)
        pending_progress = OriginalResultsProgress(2, 3)
        final_progress = OriginalResultsProgress(3, 3)

        def advance(staged):
            staged.turns += 1
            staged.pending_primary_entry = entry
            return SimpleNamespace(
                pending_primary_entry=entry,
                results_progress=pending_progress,
            )

        def play(staged, mode):
            self.assertEqual(mode, MatchDetailMode.QUICK_MATCH)
            staged.matches += 1
            staged.pending_primary_entry = None
            return SimpleNamespace(
                match_entry=entry,
                user_result=SimpleNamespace(score=(2, 1)),
                results_progress=final_progress,
            )

        with patch.object(StubBackend, 'advance_original_management', advance, create=True), \
                patch.object(StubBackend, 'play_original_user_primary_match', play, create=True), \
                patch.object(host, 'redraw'):
            host._begin_original_management_turn()
            host._management_turn_thread.run()
            host._poll_original_management_turn()
            self.assertEqual(gameplay.turns, 1)
            self.assertEqual(gameplay.pending_primary_entry, entry)
            self.assertIsNotNone(host.prematch_surface)
            host.on_click(SimpleNamespace(x=640, y=30))
            self.assertIsNone(host._management_turn_thread)
            host.on_click(SimpleNamespace(x=520, y=110))
            self.assertEqual(live.session.match_detail_mode,
                             MatchDetailMode.QUICK_MATCH)
            host._management_turn_thread.run()
            host._poll_original_management_turn()
            self.assertIs(host.last_results_progress, final_progress)
            self.assertEqual(gameplay.matches, 0)
            host._poll_original_management_turn()
            self.assertEqual(gameplay.matches, 1)
            self.assertIsNone(gameplay.pending_primary_entry)
            host._begin_original_management_turn()
            self.assertIsNotNone(host._management_turn_thread)
            host._management_turn_thread.run()
            host._poll_original_management_turn()
        self.assertEqual(gameplay.matches, 1)
        self.assertEqual(gameplay.turns, 2)
        self.assertEqual(gameplay.pending_primary_entry, entry)
        self.assertIsNone(host._management_turn_thread)
        self.assertIn('conditional PPreMatch', host.last_status)

    def test_unimplemented_prematch_modes_do_not_commit_selection_or_simulate(self):
        live = presenter()
        errors = []
        host = OriginalGameTkHost(
            live, FakeRoot(), FakeTk, error_reporter=errors.append
        )
        live.session.gameplay = StubBackend()
        live.session.started = True
        live.session.navigation.screen = FrontEndScreen.MANAGEMENT
        pending = ("premier_league", 7)
        live.session.gameplay.pending_primary_entry = pending
        host.prematch_surface = SimpleNamespace()
        self.assertIsNone(live.session.match_detail_mode)

        with patch.object(host, "_begin_original_human_match") as begin:
            for selector in PREMATCH_SELECTORS:
                if selector.mode is MatchDetailMode.QUICK_MATCH:
                    continue
                rect = selector.rect
                host.on_click(SimpleNamespace(
                    x=rect.x + rect.width // 2,
                    y=rect.y + rect.height // 2,
                ))
                self.assertIsNone(live.session.match_detail_mode)
                self.assertEqual(live.session.gameplay.pending_primary_entry, pending)
                self.assertIsNone(host._management_turn_thread)
            begin.assert_not_called()
        self.assertEqual(len(errors), 3)
        self.assertTrue(all("unfinished source renderer" in error for error in errors))

        quick = next(selector for selector in PREMATCH_SELECTORS
                     if selector.mode is MatchDetailMode.QUICK_MATCH)
        with patch.object(host, "_begin_original_human_match") as begin:
            host.on_click(SimpleNamespace(
                x=quick.rect.x + quick.rect.width // 2,
                y=quick.rect.y + quick.rect.height // 2,
            ))
            begin.assert_called_once_with(MatchDetailMode.QUICK_MATCH)
        self.assertEqual(live.session.match_detail_mode, MatchDetailMode.QUICK_MATCH)
        self.assertEqual(live.session.gameplay.pending_primary_entry, pending)

    def test_next_thread_start_failure_releases_busy_state(self):
        live = presenter()
        live.session.gameplay = SimpleNamespace(advance_original_management=lambda: None)
        host = OriginalGameTkHost(live, FakeRoot(), FakeTk,
            management_thread_factory=lambda **kwargs: SimpleNamespace(
                start=lambda: (_ for _ in ()).throw(RuntimeError('thread unavailable'))))
        with self.assertRaisesRegex(RuntimeError, 'thread unavailable'):
            host._begin_original_management_turn()
        self.assertIsNone(host._management_turn_queue)
        self.assertIsNone(host._management_turn_thread)
        self.assertEqual(host.management_next_flags, 2)
        self.assertEqual(host.root.values['configure']['cursor'], '')

    def test_rgba_photo_cache_precedes_encoding_and_tracks_content_geometry(self):
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk)
        pixels = bytes((1, 2, 3, 255)) * 2
        with patch('original_game_host.encode_rgba_png', wraps=encode_rgba_png) as encoder:
            first = host._rgba_photo(2, 1, pixels)
            self.assertIs(first, host._rgba_photo(2, 1, pixels))
            self.assertEqual(encoder.call_count, 1)
            self.assertIsNot(first, host._rgba_photo(1, 2, pixels))
            self.assertIsNot(first, host._rgba_photo(2, 1, bytes((3, 2, 1, 255))*2))
            self.assertEqual(encoder.call_count, 3)
        self.assertIn(first, host._photos)  # Own lifetime beyond canvas redraw.
        host.on_window_configure(SimpleNamespace(widget=host.root, width=400, height=300))
        host.root.run_timer()
        self.assertIsNot(first, host._rgba_photo(2, 1, pixels))

    def test_window_resize_rebuilds_scaled_images_and_pointer_mapping(self):
        root = LargeFakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        old_background = host._first_screen_photo_cache[(FrontEndScreen.START_MENU, 'background')]
        host._generic_photo_cache[b'old scale'] = object()
        host.on_window_configure(SimpleNamespace(widget=root, width=640, height=480))
        root.run_timer()
        self.assertEqual((host.display_scale_num, host.display_scale_den), (4, 5))
        self.assertEqual((host.canvas.kwargs['width'], host.canvas.kwargs['height']), (640, 480))
        new_background = host._first_screen_photo_cache[(FrontEndScreen.START_MENU, 'background')]
        self.assertIsNot(new_background, old_background)
        self.assertEqual((new_background.width, new_background.height), (640, 480))
        self.assertEqual(host._generic_photo_cache, {})
        native = host._normalize_pointer_event(SimpleNamespace(widget=host.canvas,
            x=host._native_to_display(141), y=host._native_to_display(512)))
        self.assertEqual((native.x, native.y), (141, 512))
        host.on_window_configure(SimpleNamespace(widget=host.canvas, width=2, height=2))
        self.assertIsNone(host._viewport_resize_idle)

    def test_startup_resize_scales_black_field_without_drawing_menu(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        host._startup_media_active = True
        host._startup_media_backdrop = 42
        before = host.canvas.delete_count
        host.on_window_configure(SimpleNamespace(widget=root, width=1000, height=750))
        root.run_timer()
        self.assertEqual((host.display_width, host.display_height), (1000, 750))
        self.assertEqual(host.canvas.values['coords'][42], (0, 0, 1000, 750))
        self.assertEqual(host.canvas.delete_count, before)
        self.assertEqual(host._first_screen_photo_cache, {})

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
            x=host._native_to_display(141),
            y=host._native_to_display(512),
            widget=host.canvas,
        )
        native = host._normalize_pointer_event(event)
        self.assertEqual((native.x, native.y), (141, 512))

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

    def test_management_resources_are_route_scoped_and_cached_once(self):
        calls = []
        payloads = {
            "squad": {
                "management_pmenu_resources": object(),
                "squad_top_resources": object(),
                "squad_row_text_resources": object(),
                "squad_status_resources": object(),
                "management_background": object(),
                "management_header_resources": object(),
            },
            "fixtures": {
                "league_fixtures_grid_art": object(),
                "fixtures_pager_art": object(),
                "pmatchinfo_snapshot": object(),
                "pmatchinfo_font": object(),
                "pmatchinfo_nested_font": object(),
                "pmatchinfo_script_art": object(),
                "_fixture_resource_names": ("fixture-grid",),
            },
            "league_tables": {
                "league_tables_header_art": object(),
                "management_text_resources": object(),
                "_league_table_resource_names": ("league-table",),
            },
        }

        def loader(family):
            calls.append(family)
            return payloads[family]

        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_resource_loader=loader,
        )
        self.assertEqual(calls, [])
        self.assertFalse(host._management_resources_loaded)

        host._ensure_management_resources("squad")
        self.assertEqual(calls, ["squad"])
        self.assertTrue(host._management_resources_loaded)
        self.assertEqual(host._management_resource_families_loaded, {"squad"})
        self.assertIsNone(host.league_fixtures_grid_art)
        self.assertIsNone(host.fixtures_pager_art)
        self.assertIsNone(host.league_tables_header_art)
        self.assertIsNone(host.pmatchinfo_snapshot)
        self.assertIsNone(host.management_text_resources)

        host._ensure_management_resources("squad")
        self.assertEqual(calls, ["squad"])

        host._ensure_management_resources("fixtures")
        self.assertEqual(calls, ["squad", "fixtures"])
        self.assertEqual(
            host._management_resource_families_loaded,
            {"squad", "fixtures"},
        )
        host._ensure_management_resources("fixtures")
        self.assertEqual(calls, ["squad", "fixtures"])

        host._ensure_management_resources("league_tables")
        self.assertEqual(calls, ["squad", "fixtures", "league_tables"])
        self.assertEqual(
            host._management_resource_families_loaded,
            {"squad", "fixtures", "league_tables"},
        )
        host._ensure_management_resources("league_tables")
        self.assertEqual(calls, ["squad", "fixtures", "league_tables"])

        for family in ("squad", "fixtures", "league_tables"):
            for name, value in payloads[family].items():
                self.assertIs(getattr(host, name), value)

    def test_source_accepted_panel_routes_load_each_family_once_then_reuse_it(self):
        calls = []
        threads = []
        payloads = {
            "fixtures": {
                "league_fixtures_grid_art": object(),
                "fixtures_pager_art": object(),
                "pmatchinfo_snapshot": object(),
                "pmatchinfo_font": object(),
                "pmatchinfo_nested_font": object(),
                "pmatchinfo_script_art": object(),
                "_fixture_resource_names": ("fixture-grid",),
            },
            "league_tables": {
                "league_tables_header_art": object(),
                "management_text_resources": object(),
                "_league_table_resource_names": ("league-table",),
            },
        }

        def loader(family):
            calls.append(family)
            return payloads[family]

        def thread_factory(**kwargs):
            thread = DeferredThread(**kwargs)
            threads.append(thread)
            return thread

        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_resource_loader=None,
            management_thread_factory=thread_factory,
        )
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)
        with patch.object(host, "redraw"):
            host.on_click(SimpleNamespace(x=426, y=301))
        self.assertTrue(live.session.started)
        self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)

        # The fresh Squad family is the only family considered ready when the
        # deferred route-loader seam is installed for this host-level test.
        host.management_resource_loader = loader
        host._management_resource_families_loaded = {"squad"}
        host._management_resources_loaded = True

        class RoutePresenter:
            def __init__(self):
                self.panel_class = "PLeagueFixtures"

            def source_accepted_pmenu_action(self, row_kind, menu_id, source_flags):
                return SimpleNamespace(
                    action=SimpleNamespace(action_kind="open_panel"),
                    presentation=SimpleNamespace(panel_class=self.panel_class),
                )

        route = RoutePresenter()
        host.management_presenter = route

        first = host.apply_source_accepted_pmenu_action("child", 0x25C, 0)
        self.assertEqual(first.presentation.panel_class, "PLeagueFixtures")
        self.assertEqual(len(threads), 1)
        self.assertEqual(host._management_loading_family, "fixtures")
        self.assertEqual(calls, [])

        with patch.object(host, "redraw") as redraw:
            threads[0].run()
            root.run_timer()
            redraw.assert_called_once_with()
        self.assertEqual(calls, ["fixtures"])
        self.assertIn("fixtures", host._management_resource_families_loaded)

        with patch.object(host, "redraw") as redraw:
            host.apply_source_accepted_pmenu_action("child", 0x25C, 0)
            redraw.assert_called_once_with()
        self.assertEqual(len(threads), 1)
        self.assertEqual(calls, ["fixtures"])

        route.panel_class = "PLeagueTables"
        host.apply_source_accepted_pmenu_action("child", 0x25A, 0)
        self.assertEqual(len(threads), 2)
        self.assertEqual(host._management_loading_family, "league_tables")

        with patch.object(host, "redraw") as redraw:
            threads[1].run()
            root.run_timer()
            redraw.assert_called_once_with()
        self.assertEqual(calls, ["fixtures", "league_tables"])
        self.assertIn("league_tables", host._management_resource_families_loaded)

        with patch.object(host, "redraw") as redraw:
            host.apply_source_accepted_pmenu_action("child", 0x25A, 0)
            redraw.assert_called_once_with()
        self.assertEqual(len(threads), 2)
        self.assertEqual(calls, ["fixtures", "league_tables"])

    def test_teamselect_start_defers_only_fresh_squad_resources_off_tk_thread(self):
        calls = []
        threads = []
        payload = {
            "management_pmenu_resources": object(),
            "squad_top_resources": object(),
                "squad_row_text_resources": object(),
                "squad_status_resources": object(),
            "management_background": object(),
            "management_header_resources": object(),
        }

        def loader(family):
            calls.append(family)
            self.assertEqual(family, "squad")
            return payload

        def thread_factory(**kwargs):
            thread = DeferredThread(**kwargs)
            threads.append(thread)
            return thread

        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_presenter_factory=management_factory,
            management_resource_loader=loader,
            management_thread_factory=thread_factory,
        )
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)

        with patch.object(host, "redraw") as redraw:
            host.on_click(SimpleNamespace(x=426, y=301))

            self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
            self.assertTrue(live.session.started)
            self.assertEqual(calls, [])
            self.assertEqual(len(threads), 1)
            self.assertTrue(threads[0].started)
            self.assertEqual(host._management_loading_family, "squad")
            self.assertFalse(host._management_resources_loaded)
            self.assertIsNotNone(host._management_load_poll)
            redraw.assert_not_called()
            self.assertEqual(root.values["configure"]["cursor"], "watch")

            threads[0].run()
            root.run_timer()

            self.assertEqual(calls, ["squad"])
            self.assertTrue(host._management_resources_loaded)
            self.assertEqual(host._management_resource_families_loaded, {"squad"})
            redraw.assert_called_once_with()
            self.assertEqual(root.values["configure"]["cursor"], "")
            for name, value in payload.items():
                self.assertIs(getattr(host, name), value)
            self.assertIsNone(host.league_fixtures_grid_art)
            self.assertIsNone(host.fixtures_pager_art)
            self.assertIsNone(host.league_tables_header_art)
            self.assertIsNone(host.pmatchinfo_snapshot)
            self.assertIsNone(host.management_text_resources)

    def test_teamselect_async_management_loader_surfaces_worker_exception(self):
        threads = []
        messages = []

        def loader(family):
            self.assertEqual(family, "squad")
            raise RuntimeError("management decode exploded")

        def thread_factory(**kwargs):
            thread = DeferredThread(**kwargs)
            threads.append(thread)
            return thread

        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_presenter_factory=management_factory,
            management_resource_loader=loader,
            management_thread_factory=thread_factory,
            error_reporter=messages.append,
        )
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)

        with patch.object(host, "redraw") as redraw:
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertEqual(messages, [])
            self.assertEqual(len(threads), 1)

            threads[0].run()
            root.run_timer()

        self.assertEqual(messages, ["RuntimeError: management decode exploded"])
        self.assertEqual(host.last_status, "RuntimeError: management decode exploded")
        self.assertFalse(host._management_resources_loaded)
        self.assertIsNone(host._management_load_thread)
        self.assertIsNone(host._management_load_queue)
        self.assertEqual(root.values["configure"]["cursor"], "")
        redraw.assert_not_called()

    def test_management_input_is_ignored_while_async_resources_are_loading(self):
        threads = []

        def loader(family):
            self.assertEqual(family, "squad")
            raise AssertionError("deferred worker should not have run yet")

        def thread_factory(**kwargs):
            thread = DeferredThread(**kwargs)
            threads.append(thread)
            return thread

        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_presenter_factory=management_factory,
            management_resource_loader=loader,
            management_thread_factory=thread_factory,
        )
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)
        host.on_click(SimpleNamespace(x=426, y=301))
        self.assertEqual(len(threads), 1)

        host.on_click(SimpleNamespace(x=400, y=300))

        self.assertIsNone(host.management_presenter)
        self.assertEqual(
            host.last_status,
            "Preparing source-backed management squad resources...",
        )
        self.assertEqual(len(threads), 1)

    def test_later_management_route_decode_blocks_input_and_surfaces_failure(self):
        threads = []
        messages = []
        squad_payload = {
            "management_pmenu_resources": object(),
            "squad_top_resources": object(),
                "squad_row_text_resources": object(),
                "squad_status_resources": object(),
            "management_background": object(),
            "management_header_resources": object(),
        }

        def loader(family):
            if family == "squad":
                return squad_payload
            if family == "fixtures":
                raise RuntimeError("fixture decode exploded")
            raise AssertionError(f"unexpected family {family}")

        def thread_factory(**kwargs):
            thread = DeferredThread(**kwargs)
            threads.append(thread)
            return thread

        live = presenter()
        root = FakeRoot()
        host = OriginalGameTkHost(
            live,
            root,
            FakeTk,
            management_presenter_factory=management_factory,
            management_resource_loader=loader,
            management_thread_factory=thread_factory,
            error_reporter=messages.append,
        )

        # Reach MANAGEMENT through the real recovered lifecycle before testing a
        # later route family. The initial Squad decode is completed under a
        # redraw stub because this test exercises loading/error lifecycle, not
        # bitmap rendering of the deliberately minimal object payload.
        host.on_click(SimpleNamespace(x=141, y=512))
        live.choose_club(12)
        with patch.object(host, "redraw"):
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertEqual(len(threads), 1)
            self.assertEqual(host._management_loading_family, "squad")
            threads[0].run()
            root.run_timer()

        self.assertTrue(live.session.started)
        self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
        self.assertEqual(host._management_resource_families_loaded, {"squad"})
        self.assertTrue(host._management_resources_loaded)

        host._begin_management_resource_load("fixtures")
        self.assertEqual(host._management_loading_family, "fixtures")
        self.assertEqual(len(threads), 2)

        with patch.object(host, "redraw") as redraw:
            host.on_click(SimpleNamespace(x=400, y=300))
            self.assertEqual(
                host.last_status,
                "Preparing source-backed management fixtures resources...",
            )
            redraw.assert_not_called()

            threads[1].run()
            root.run_timer()

        self.assertEqual(messages, ["RuntimeError: fixture decode exploded"])
        self.assertEqual(host.last_status, "RuntimeError: fixture decode exploded")
        self.assertNotIn("fixtures", host._management_resource_families_loaded)
        self.assertIsNone(host._management_load_thread)
        self.assertIsNone(host._management_load_queue)
        self.assertIsNone(host._management_loading_family)
        self.assertEqual(root.values["configure"]["cursor"], "")

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

    def test_startup_escape_forwards_native_input_without_geometry_change(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        requests = []
        host._startup_media_active = True
        host._startup_native_input = lambda *args: requests.append(args)
        self.assertEqual(host.leave_fullscreen(), 'break')
        self.assertEqual(requests, [(0x100, 0x1B)])
        host.toggle_fullscreen()
        self.assertTrue(host._fullscreen)
        self.assertTrue(root.values['attributes']['-fullscreen'])
        self.assertEqual(requests, [(0x100, 0x1B)])
        host._startup_media_active = False
        host.leave_fullscreen()
        self.assertFalse(host._fullscreen)
        self.assertEqual(requests, [(0x100, 0x1B)])

    def test_escape_fails_closed_during_unrecovered_startup_input_semantics(self):
        root = FakeRoot()
        host = OriginalGameTkHost(presenter(), root, FakeTk)
        host.show_startup_media_backdrop()

        self.assertTrue(host._fullscreen)
        self.assertEqual(host.leave_fullscreen(), "break")
        self.assertTrue(host._fullscreen)
        self.assertTrue(root.values["attributes"]["-fullscreen"])

        host.hide_startup_media_backdrop()
        self.assertEqual(host.leave_fullscreen(), "break")
        self.assertFalse(host._fullscreen)
        self.assertFalse(root.values["attributes"]["-fullscreen"])

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
        host.on_click(SimpleNamespace(x=141, y=512))
        live.session.choose_club(999)
        def reject(club_id):
            raise ValueError(f"club {club_id} is not in the Premier League")
        live.session.gameplay.select_club = reject
        host.on_click(SimpleNamespace(x=426, y=301))
        self.assertEqual(messages, ["ValueError: club 999 is not in the Premier League"])
        self.assertEqual(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
        self.assertEqual(live.session.selected_club_ids, (999,))
        self.assertFalse(live.session.started)

    def test_closed_pmenu_skips_render_and_open_snapshot_reuses_render(self):
        live = presenter()
        root = FakeRoot()
        with patch(
            "original_game_host.build_management_pmenu_render",
            side_effect=lambda frame, resources: fake_pmenu_render(),
        ) as render:
            host = OriginalGameTkHost(
                live,
                root,
                FakeTk,
                management_presenter_factory=management_factory,
                management_pmenu_resources=object(),
                squad_top_resources=fake_squad_top_resources(),
                squad_row_text_resources=fake_squad_row_text_resources(),
            )

            host.on_click(SimpleNamespace(x=141, y=512))
            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))

            self.assertFalse(host.pmenu_popup_active)
            render.assert_not_called()

            host.on_click(SimpleNamespace(x=600, y=1))
            self.assertTrue(host.pmenu_popup_active)
            self.assertEqual(render.call_count, 1)

            host.redraw()
            self.assertEqual(render.call_count, 1)

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
                squad_row_text_resources=fake_squad_row_text_resources(),
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

            host.on_click(SimpleNamespace(x=141, y=512))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.TEAM_SELECT)
            self.assertEqual(len(host.canvas.images), 3)

            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
            self.assertTrue(live.session.started)
            self.assertEqual(live.session.gameplay.selections, [12])
            self.assertFalse(host.pmenu_popup_active)
            self.assertEqual(len(host.canvas.images), 18)
            # Six top controls, three original populated cell backgrounds,
            # and four native column headings precede row text.
            # Role/name remain first in that row-text group; the three new
            # PSCF numeric controls follow them.
            self.assertEqual(host.canvas.images[13][:2], (77, 234))
            self.assertEqual(host.canvas.images[14][:2], (113, 234))
            host.on_click(SimpleNamespace(x=600, y=1))
            self.assertEqual(len(host.canvas.images), 19)
            self.assertIn("source PMenu rows rendered", host.last_status)
            self.assertIn("18 source panel bitmaps rendered", host.last_status)
            self.assertIn("surrounding management background unresolved", host.last_status)

            before = host.management_presenter.snapshot()
            self.assertEqual(before.panel_code, 0xCE)

            host.on_click(SimpleNamespace(x=700, y=120))
            self.assertIn("PMenu source pointer press", host.last_status)
            self.assertIn("no_action 0x2", host.last_status)
            after = host.management_presenter.snapshot()
            self.assertEqual(after.panel_code, 0xCE)
            self.assertEqual(after.menu.selected_child_id, 0xCE)
            self.assertEqual(len(host.canvas.images), 19)

            # The ninth fresh visible row is Calendar.  Tk <Button-1> is a press,
            # matching the recovered SelectBmp +0x6C input virtual.
            host.on_click(SimpleNamespace(x=700, y=96 + 8 * 29))
            native = host.management_presenter.snapshot()
            self.assertEqual(native.panel_code, 0xCE)
            self.assertEqual(native.menu.selected_root_id, 0x259)
            self.assertIn("expand_root 0x259", host.last_status)
            self.assertEqual(len(host.canvas.images), 19)

            accepted = host.apply_source_accepted_pmenu_action("title", 3, 0)
            self.assertTrue(accepted.action.accepted)
            self.assertEqual(accepted.action.action_kind, "expand_root")
            self.assertEqual(accepted.presentation.panel_code, 0xCE)
            self.assertEqual(accepted.presentation.menu.selected_root_id, 3)
            self.assertEqual(accepted.presentation.menu.selected_child_id, 0xCE)
            self.assertIn("source-accepted PMenu action", host.last_status)
            self.assertEqual(len(host.canvas.images), 19)

            host.on_click(SimpleNamespace(x=100, y=120))
            self.assertIn("no source-bounded PMenu candidate row", host.last_status)
            self.assertEqual(host.management_presenter.snapshot().panel_code, 0xCE)
            self.assertEqual(len(host.canvas.images), 19)

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

    def test_management_header_binds_fresh_club_caption_to_native_control(self):
        from dataclasses import replace
        from original_management_club_caption import load_verified_management_club_font
        source = Path(__file__).resolve().parents[1] / 'original_assets/source'
        resources = replace(fake_management_header_resources(),
                            club_font=load_verified_management_club_font(source))
        host = OriginalGameTkHost(presenter(), FakeRoot(), FakeTk,
                                  management_header_resources=resources)
        host.canvas.delete('all')
        club = ClubHeaderView(1, 'Southport', 'Southport', date(2000, 7, 1),
                              native_user_club_caption='')
        self.assertEqual(host._draw_management_header(club), 4)
        self.assertEqual(host.canvas.images[-1][:2], (460, 1))
        self.assertEqual(host._draw_management_header(replace(club, native_user_club_caption=None)), 3)

    def test_management_header_redraw_reuses_cached_native_pngs(self):
        _cached_runtime_png.cache_clear()
        try:
            host = OriginalGameTkHost(
                presenter(),
                FakeRoot(),
                FakeTk,
                management_header_resources=fake_management_header_resources(),
            )
            host.canvas.delete("all")
            host._photos = []

            with patch("original_game_host.encode_rgba_png", wraps=encode_rgba_png) as encoder:
                host._draw_management_header()
                first_draw_calls = encoder.call_count
                self.assertGreater(first_draw_calls, 0)

                host.canvas.delete("all")
                host._photos = []
                host._draw_management_header()

                self.assertEqual(encoder.call_count, first_draw_calls)
                self.assertGreaterEqual(_cached_runtime_png.cache_info().hits, 3)
        finally:
            _cached_runtime_png.cache_clear()

    def test_original_club_name_renders_southport_and_another_club_without_special_cases(self):
        font = validate_management_header_club_name_font(DEFAULT_SOURCE_ROOT)
        for club_name in ("Southport", "Arsenal"):
            with self.subTest(club=club_name):
                host = OriginalGameTkHost(
                    presenter(),
                    FakeRoot(),
                    FakeTk,
                    management_header_resources=fake_management_header_resources(
                        club_name_font=font
                    ),
                )
                host.canvas.delete("all")
                host._photos = []
                frame = SimpleNamespace(
                    presentation=SimpleNamespace(
                        club=ClubHeaderView(12, club_name, club_name, date(2000, 8, 1)),
                    )
                )
                count = host._draw_management_club_name(frame)
                overlay = management_header_club_name_overlay(font, club_name)
                self.assertEqual(count, 1)
                self.assertEqual(len(host.canvas.images), 1)
                self.assertEqual(host.canvas.images[0][:2], (overlay.x, overlay.y))
                self.assertEqual(len(host._photos), 1)

    def test_original_club_name_fails_closed_without_exact_font(self):
        host = OriginalGameTkHost(
            presenter(), FakeRoot(), FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                club=ClubHeaderView(12, "Southport", "Southport", date(2000, 8, 1)),
            )
        )
        self.assertEqual(host._draw_management_club_name(frame), 0)

    def test_management_current_date_draws_exact_source_control(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                club=ClubHeaderView(
                    12,
                    "Source Club",
                    "Source",
                    date(2000, 8, 1),
                ),
            )
        )

        count = host._draw_management_current_date(frame)

        self.assertEqual(count, 1)
        self.assertEqual(len(host.canvas.images), 1)
        self.assertEqual(host.canvas.images[0][:2], (450, 68))
        self.assertEqual(len(host._photos), 1)

    def test_management_match_lines_draw_exact_two_source_controls(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                header_match=SimpleNamespace(
                    competition_name="Premier League",
                    home_short_name="Beta",
                    away_short_name="Alpha",
                    scheduled_date=date(2000, 8, 26),
                ),
            )
        )

        count = host._draw_management_match_lines(frame)

        self.assertEqual(count, 2)
        self.assertEqual(len(host.canvas.images), 2)
        self.assertEqual(host.canvas.images[0][:2], (450, 34))
        self.assertEqual(host.canvas.images[1][:2], (450, 51))
        self.assertEqual(len(host._photos), 2)

    def test_management_match_lines_fail_closed_without_candidate(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            management_header_resources=fake_management_header_resources(),
        )
        frame = SimpleNamespace(
            presentation=SimpleNamespace(header_match=None)
        )
        self.assertEqual(host._draw_management_match_lines(frame), 0)

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
                squad_row_text_resources=fake_squad_row_text_resources(),
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

    def test_squad_landing_draws_source_player_and_scf_numeric_controls(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            squad_row_text_resources=fake_squad_row_text_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        row = SimpleNamespace(
            y=154,
            assigned_role_abbreviation="FC",
            assigned_role_rgb=(255, 255, 255),
            display_name="P. 0",
            display_name_rgb=(255, 255, 255),
            condition=75,
            recent_form_average=7.35,
            current_role_rating=63,
        )
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=squad_view_transition(3),
                squad=SimpleNamespace(rows=(row,)),
            )
        )

        count = host._draw_squad_rows(frame)

        self.assertEqual(count, 9)
        self.assertEqual(len(host.canvas.images), 9)
        for item, left in zip(host.canvas.images[:4], (275, 298, 321, 344)):
            self.assertGreaterEqual(item[0], left)
            self.assertLess(item[0], left + 22)
            self.assertGreaterEqual(item[1], 123)
            self.assertLessEqual(item[1] + item[2]["image"].height, 222)
        self.assertEqual(host.canvas.images[4][:2], (77, 234))
        self.assertEqual(host.canvas.images[5][:2], (113, 234))
        # PSCFRow controls are centered inside native screen x ranges
        # 300..318, 323..341 and 346..364 respectively.
        for item, left in zip(host.canvas.images[6:], (300, 323, 346)):
            self.assertGreaterEqual(item[0], left)
            self.assertLess(item[0], left + 19)
            self.assertGreaterEqual(item[1], 234)
            self.assertLess(item[1], 248)

    def test_squad_landing_draws_source_qualified_native_status_icons(self):
        host = OriginalGameTkHost(
            presenter(),
            FakeRoot(),
            FakeTk,
            squad_row_text_resources=fake_squad_row_text_resources(),
            squad_status_resources=fake_squad_status_resources(),
        )
        host.canvas.delete("all")
        host._photos = []
        row = SimpleNamespace(
            y=154,
            assigned_role_abbreviation="FC",
            assigned_role_rgb=(255, 255, 255),
            display_name="P. 0",
            display_name_rgb=(255, 255, 255),
            condition=88,
            recent_form_average=7.0,
            current_role_rating=63,
            native_status_frame_index=0,
        )
        frame = SimpleNamespace(
            presentation=SimpleNamespace(
                panel_class="PSquadScreen",
                squad_view_transition=squad_view_transition(3),
                squad=SimpleNamespace(rows=(row,)),
            )
        )

        count = host._draw_squad_rows(frame)

        self.assertEqual(count, 10)
        self.assertEqual(len(host.canvas.images), 10)
        self.assertEqual(host.canvas.images[-1][:2], (277, 234))
        status_photo = host.canvas.images[-1][2]["image"]
        self.assertEqual((status_photo.width, status_photo.height), (18, 14))

        for frame_index in (3, 13):
            host.canvas.delete("all")
            host._photos = []
            qualified = SimpleNamespace(**{
                **row.__dict__,
                "native_status_frame_index": frame_index,
            })
            qualified_frame = SimpleNamespace(
                presentation=SimpleNamespace(
                    panel_class="PSquadScreen",
                    squad_view_transition=squad_view_transition(3),
                    squad=SimpleNamespace(rows=(qualified,)),
                )
            )
            self.assertEqual(host._draw_squad_rows(qualified_frame), 10)
            self.assertEqual(host.canvas.images[-1][:2], (277, 234))
            status_photo = host.canvas.images[-1][2]["image"]
            self.assertEqual((status_photo.width, status_photo.height), (18, 14))

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
                squad_row_text_resources=fake_squad_row_text_resources(),
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
                squad_row_text_resources=fake_squad_row_text_resources(),
            )
            host.on_click(SimpleNamespace(x=141, y=512))
            live.choose_club(12)
            host.on_click(SimpleNamespace(x=426, y=301))
            host.on_click(SimpleNamespace(x=600, y=1))
            self.assertEqual(len(host.canvas.images), 19)

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
            self.assertEqual(len(host.canvas.images), 19)

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
                squad_row_text_resources=fake_squad_row_text_resources(),
            )
            host.on_click(SimpleNamespace(x=141, y=512))
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
                squad_row_text_resources=fake_squad_row_text_resources(),
            )
            host.on_click(SimpleNamespace(x=141, y=512))
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
        host.on_click(SimpleNamespace(x=141, y=512))
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
        host.on_click(SimpleNamespace(x=141, y=512))
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

    def test_startup_media_runtime_accepts_already_verified_bundled_derivatives(self):
        backend = object()
        derivatives = (object(), object())
        with patch(
            "original_game_host.play_verified_startup_sequence",
            return_value="bundled-summary",
        ) as play:
            result = play_configured_startup_media(
                receipt_path=None,
                backend=backend,
                derivatives=derivatives,
            )

        self.assertEqual(result, "bundled-summary")
        play.assert_called_once_with(derivatives, backend)

        with self.assertRaisesRegex(
            OriginalGameHostError,
            "cannot combine bundled derivatives",
        ):
            play_configured_startup_media(
                receipt_path=Path("/private/receipt.json"),
                backend=backend,
                derivatives=derivatives,
            )
        with self.assertRaisesRegex(
            OriginalGameHostError,
            "requires a playback backend",
        ):
            play_configured_startup_media(
                receipt_path=None,
                backend=None,
                derivatives=derivatives,
            )

    def test_default_source_root_is_repository_original_asset_store(self):
        self.assertEqual(
            DEFAULT_SOURCE_ROOT.name,
            "source",
        )
        self.assertEqual(DEFAULT_SOURCE_ROOT.parent.name, "original_assets")


    def test_default_presenter_uses_only_pinned_pstartmenu_derivative(self):
        calls = {}

        def load_derivative(bundle_dir, **kwargs):
            calls["derivative"] = (bundle_dir, kwargs)
            return object()

        def reject_source(**kwargs):
            raise AssertionError("default runtime must not cold-decode PStartMenu")

        fake_session = object()
        with tempfile.TemporaryDirectory() as temp:
            game_dir = Path(temp) / "game"
            game_dir.mkdir()
            with patch(
                "original_game_host.load_verified_pstartmenu_derivative_bundle",
                side_effect=load_derivative,
            ), patch(
                "original_game_host.load_verified_english_pstartmenu_inputs",
                side_effect=reject_source,
            ), patch(
                "original_game_host.FrontEndSession.for_canonical_game_dir",
                return_value=fake_session,
            ):
                built = build_original_game_presenter(game_dir)

        self.assertIs(built.session, fake_session)
        self.assertIsNone(built.settings_resources)
        bundle_dir, kwargs = calls["derivative"]
        self.assertEqual(bundle_dir, DEFAULT_PSTARTMENU_DERIVATIVE_ROOT)
        self.assertEqual(
            kwargs["expected_decoder"], PSTARTMENU_DERIVATIVE_DECODER
        )
        self.assertEqual(
            kwargs["expected_manifest_sha256"],
            PSTARTMENU_DERIVATIVE_MANIFEST_SHA256,
        )
        self.assertEqual(len(kwargs["expected_sources"]), 6)

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
        self.assertIsNone(built.settings_resources)
        self.assertNotIn("settings", calls)
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
