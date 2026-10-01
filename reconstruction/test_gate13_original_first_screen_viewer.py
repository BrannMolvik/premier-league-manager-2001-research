"""Headless exact-source live viewer model and mocked Tk navigation tests."""
from base64 import b64decode
from types import SimpleNamespace
import unittest

from front_end_session import FrontEndSession
from front_end_state import FrontEndScreen
from gate13_original_first_screen_viewer import OriginalFirstScreenTkDebug
from original_first_screen_presenter import OriginalFirstScreenPresenter
from original_live_debug_view import (
    OriginalLiveDebugError, build_original_debug_frame
)
from original_pstartmenu_resources import assemble_original_pstartmenu_inputs
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_original_pstartmenu_resources import fixture as menu_fixture
from test_original_teamselect_resources import fixture as team_fixture
from test_gate13_original_pixel_preview import read_png_rgba


class StubBackend:
    def __init__(self):
        self.selections = []

    def select_club(self, club_id):
        self.selections.append(club_id)
        return ("source-debug-manager", club_id)


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
    def test_original_menu_source_pixels_and_unpositioned_font_metadata(self):
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
        self.assertEqual(
            len(debug.background_png) > 0,
            True,
        )
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
        window = OriginalFirstScreenTkDebug(live, root, FakeTk, FakeTtk)
        self.assertEqual(window.canvas.kwargs["width"], 800)
        self.assertEqual(window.canvas.kwargs["height"], 600)
        self.assertIn("DEVELOPER PREVIEW", root.values["title"])
        self.assertEqual(len(window.canvas.images), 5)
        self.assertEqual(
            [(x, y) for x, y, _ in window.canvas.images[1:]],
            [(181, 478), (7, 478), (355, 478), (181, 508)],
        )
        window.step_source_frame(1)
        self.assertEqual(window.source_frame_index, 1)
        window.step_source_frame(-1)
        self.assertEqual(window.source_frame_index, 0)
        window.on_original_click(SimpleNamespace(x=20, y=78))
        self.assertIs(live.snapshot().screen, FrontEndScreen.START_MENU)
        self.assertEqual(len(window.canvas.images), 5)
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
        self.assertEqual(
            live.session.gameplay.selections, [12]
        )
        self.assertIn("not yet reconstructed", window.status.get())


if __name__ == "__main__":
    unittest.main()
