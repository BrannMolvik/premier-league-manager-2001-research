"""Headless exact-source live viewer model and mocked Tk navigation tests."""
from base64 import b64decode
from dataclasses import dataclass
from datetime import date
from types import SimpleNamespace
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_management_source_data import ClubHeaderView
from gate13_original_first_screen_viewer import OriginalFirstScreenTkDebug
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_live_debug_view import (
    OriginalLiveDebugError, build_original_debug_frame
)
from original_management_presenter import OriginalManagementPresenter
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import fixture as team_fixture
from test_gate13_original_pixel_preview import read_png_rgba


def read_png_rgba_bytes(raw: bytes):
    import struct
    import zlib

    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    pos = 8
    payload = bytearray()
    width = height = None
    while pos < len(raw):
        size = struct.unpack_from(">I", raw, pos)[0]
        kind = raw[pos + 4:pos + 8]
        data = raw[pos + 8:pos + 8 + size]
        pos += size + 12
        if kind == b"IHDR":
            width, height, depth, color, *_ = struct.unpack(">IIBBBBB", data)
            assert (depth, color) == (8, 6)
        elif kind == b"IDAT":
            payload.extend(data)
        elif kind == b"IEND":
            break
    pixels = zlib.decompress(bytes(payload))
    stride = width * 4
    rows = [
        pixels[y * (stride + 1) + 1:(y + 1) * (stride + 1)]
        for y in range(height)
    ]
    return width, height, b"".join(rows)


class StubBackend:
    def __init__(self):
        self.selections = []

    def select_club(self, club_id):
        self.selections.append(club_id)
        return ("source-debug-manager", club_id)


@dataclass(frozen=True)
class ManagementRow:
    source_roster_index: int
    player_id: int
    full_name: str
    current_position: int = 12
    condition: int = 90
    recent_form_average: float = 7.0
    current_role_rating: int = 61


class ViewerManagementBridge:
    def __init__(self, backend):
        self.backend = backend

    def club_header(self):
        return ClubHeaderView(12, "Source Club", "Source", date(2000, 8, 1))

    def squad_rows(self):
        return (ManagementRow(0, 1000, "Player 0"),)


def management_presenter_factory(session):
    return OriginalManagementPresenter(
        session, bridge_factory=ViewerManagementBridge
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

    def configure(self, **kwargs):
        self.values.update(kwargs)

    def bind(self, *args, **kwargs):
        self.values["bind"] = (args, kwargs)


class FakeRoot(FakeWidget):
    def title(self, title):
        self.values["title"] = title

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


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeTk:
    LEFT = "left"
    RIGHT = "right"
    Y = "y"
    NW = "nw"
    Canvas = FakeCanvas
    StringVar = FakeVar

    class PhotoImage:
        def __init__(self, *, data, format):
            assert format == "png"
            assert b64decode(data).startswith(b"\x89PNG\r\n\x1a\n")
            self.data = data


class FakeTtk:
    Frame = FakeWidget
    Label = FakeWidget
    Button = FakeWidget
    Entry = FakeWidget


class OriginalLiveDebugTests(unittest.TestCase):
    def test_original_menu_source_pixels_and_native_caption_overlays(self):
        live = presenter()
        snapshot = live.snapshot()
        debug = build_original_debug_frame(snapshot, 0)
        self.assertIs(debug.screen, FrontEndScreen.START_MENU)
        self.assertTrue(debug.native_button_animation_recovered)
        self.assertTrue(debug.native_text_placement_recovered)
        self.assertEqual(len(debug.original_source_frame_overlays), 4)
        self.assertEqual(
            [o.event for o in debug.original_source_frame_overlays],
            [1, 2, 3, 4],
        )
        self.assertEqual(
            [(o.rect.x, o.rect.y) for o in debug.original_source_frame_overlays],
            [(181, 478), (7, 478), (355, 478), (181, 508)],
        )
        self.assertEqual(
            [o.source_label_not_positioned for o in debug.original_source_frame_overlays],
            ["AB", "BA", "A", "B"],
        )
        self.assertEqual(len(debug.native_caption_overlays), 4)
        self.assertEqual(
            [(item.line_origin_x, item.line_origin_y)
             for item in debug.native_caption_overlays],
            [(item.caption.line_origin_x, item.caption.line_origin_y)
             for item in snapshot.controls],
        )
        self.assertTrue(all(
            item.native_color_16 == 0xFFFF
            for item in debug.native_caption_overlays
        ))
        for item in debug.native_caption_overlays:
            _w, _h, rgba = read_png_rgba_bytes(item.glyph_rgba_png)
            nontransparent = [
                tuple(rgba[i:i + 4])
                for i in range(0, len(rgba), 4)
                if rgba[i + 3]
            ]
            self.assertTrue(nontransparent)
            self.assertTrue(all(pixel[:3] == (255, 255, 255)
                                for pixel in nontransparent))
        alternate = build_original_debug_frame(snapshot, 11)
        self.assertTrue(all(
            item.native_color_16 == 0x0000
            for item in alternate.native_caption_overlays
        ))
        for item in alternate.native_caption_overlays:
            _w, _h, rgba = read_png_rgba_bytes(item.glyph_rgba_png)
            self.assertTrue(all(
                tuple(rgba[i:i + 3]) == (0, 0, 0)
                for i in range(0, len(rgba), 4)
                if rgba[i + 3]
            ))
        self.assertEqual(len(debug.background_png) > 0, True)
        with self.assertRaises(OriginalLiveDebugError):
            build_original_debug_frame(snapshot, True)
        for bad in (-1, 23, 100):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalLiveDebugError):
                    build_original_debug_frame(snapshot, bad)

    def test_teamselect_debug_source_frames_are_not_hierarchy_interactions(self):
        live = presenter()
        live.pointer(7, 478)
        debug = build_original_debug_frame(live.snapshot(), 22)
        self.assertIs(debug.screen, FrontEndScreen.TEAM_SELECT)
        self.assertEqual(len(debug.original_source_frame_overlays), 2)
        self.assertEqual(debug.native_caption_overlays, ())
        self.assertEqual(
            [o.event for o in debug.original_source_frame_overlays],
            [0x29, 0x2A],
        )
        self.assertEqual(len(debug.hierarchy_row_origins_not_interactive), 16)
        self.assertTrue(all(
            o.source_label_not_positioned is None
            for o in debug.original_source_frame_overlays
        ))
        self.assertIsNone(live.pointer(20, 78))
        self.assertIsNone(live.session.selected_club_id)

    def test_mock_tk_displays_original_unscaled_background_and_routes_known_pixels(self):
        live = presenter()
        root = FakeRoot()
        window = OriginalFirstScreenTkDebug(
            live,
            root,
            FakeTk,
            FakeTtk,
            management_presenter_factory=management_presenter_factory,
        )
        self.assertEqual(window.canvas.kwargs["width"], 800)
        self.assertEqual(window.canvas.kwargs["height"], 600)
        self.assertIn("DEVELOPER PREVIEW", root.values["title"])
        self.assertEqual(len(window.canvas.images), 9)
        self.assertEqual(
            [(x, y) for x, y, _ in window.canvas.images[1:5]],
            [(181, 478), (7, 478), (355, 478), (181, 508)],
        )
        self.assertEqual(
            [(x, y) for x, y, _ in window.canvas.images[5:]],
            [(item.caption.line_origin_x, item.caption.line_origin_y)
             for item in live.snapshot().controls],
        )
        window.step_source_frame(1)
        self.assertEqual(window.source_frame_index, 1)
        window.step_source_frame(-1)
        self.assertEqual(window.source_frame_index, 0)
        window.on_original_click(SimpleNamespace(x=20, y=78))
        self.assertIs(live.snapshot().screen, FrontEndScreen.START_MENU)
        self.assertEqual(len(window.canvas.images), 9)
        window.on_original_click(SimpleNamespace(x=7, y=478))
        self.assertIs(live.snapshot().screen, FrontEndScreen.TEAM_SELECT)
        self.assertEqual(len(window.canvas.images), 3)
        window.on_original_click(SimpleNamespace(x=20, y=78))
        self.assertIsNone(live.session.selected_club_id)
        window.club_id_text.set("12")
        window.choose_debug_club()
        self.assertEqual(live.session.selected_club_id, 12)
        window.on_original_click(SimpleNamespace(x=426, y=301))
        self.assertTrue(live.session.started)
        self.assertIs(live.session.navigation.screen, FrontEndScreen.MANAGEMENT)
        self.assertEqual(
            live.session.gameplay.selections, [12]
        )
        self.assertEqual(window.canvas.images, [])
        self.assertIn("PMenu management host", window.status.get())
        self.assertIn("PSquadScreen", window.events_label.values["text"])
        self.assertIn("(599, 96, 201, 504)", window.events_label.values["text"])

        # MANAGEMENT clicks may identify only a geometry-proven candidate row.
        # They must not dispatch or mutate the selected native panel until the
        # original PMenu activation/event path is recovered.
        self.assertIsNotNone(window.management_presenter)
        before = window.management_presenter.snapshot()
        self.assertEqual(before.panel_code, 0xCE)
        window.on_original_click(SimpleNamespace(x=600, y=100))
        self.assertIn("PMenu candidate row only", window.status.get())
        self.assertIn("'Team'", window.status.get())
        self.assertIn("menu ID 0x2", window.status.get())
        self.assertIn("no navigation was dispatched", window.status.get())
        after = window.management_presenter.snapshot()
        self.assertEqual(after.panel_code, 0xCE)
        self.assertEqual(after.menu.selected_child_id, 0xCE)
        self.assertEqual(window.canvas.images, [])

        window.on_original_click(SimpleNamespace(x=100, y=100))
        self.assertIn("no source-bounded PMenu candidate row", window.status.get())
        self.assertEqual(window.management_presenter.snapshot().panel_code, 0xCE)


if __name__ == "__main__":
    unittest.main()
