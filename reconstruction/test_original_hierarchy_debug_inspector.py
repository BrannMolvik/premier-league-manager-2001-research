"""Actual original-source bindings with synthetic off-canvas hierarchy preview tests.

Hosted tests verify lossless pixels and explicit source-only annotations.
Canonical original license-gated bundle decoding is tested separately and
must never be conflated with this synthetic GUI exercise.
"""
from hashlib import sha256
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from ea444_decoder import EA444DecodedImage
from front_end_state import FrontEndScreen
from gate13_original_first_screen_viewer import OriginalFirstScreenTkDebug
from original_hierarchy_debug_inspector import (
    OriginalHierarchyDebugError, inspect_original_hierarchy_source_frames,
)
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC,
    OriginalTeamSelectHierarchyArt, split_hierarchy_source_strip,
)
from original_teamselect_resources import assemble_original_teamselect_inputs
from test_gate13_original_first_screen_viewer import (
    FakeRoot, FakeTk, FakeTtk, presenter,
)
from test_gate13_original_pixel_preview import read_png_rgba
from test_original_teamselect_resources import fixture as team_fixture


def strip(spec, colors):
    size = spec.frame_width * spec.frame_height
    pixels = b"".join(bytes(color) * size for color in colors)
    image = EA444DecodedImage(
        spec.frame_width, spec.frame_height * len(colors), pixels, 0, 0
    )
    return split_hierarchy_source_strip(image, spec)


def presenter_with_hierarchy_art():
    live = presenter()
    animation = strip(
        HIERARCHY_ANIM_SPEC,
        ((11, 22, 33, 255), (44, 55, 66, 88)),
    )
    bars = strip(
        HIERARCHY_BARS_SPEC,
        ((77, 88, 99, 255), (100, 101, 102, 1), (103, 104, 105, 200)),
    )
    live.team_select = assemble_original_teamselect_inputs(
        *team_fixture(), OriginalTeamSelectHierarchyArt(animation, bars),
    )
    return live


class HierarchyPrivateDebugTests(unittest.TestCase):
    def test_only_verified_teamselect_art_can_be_previewed_off_canvas(self):
        live = presenter_with_hierarchy_art()
        self.assertIsNone(inspect_original_hierarchy_source_frames(live.snapshot()))
        live.pointer(7, 478)
        view = live.snapshot()
        self.assertIs(view.screen, FrontEndScreen.TEAM_SELECT)
        bundle = inspect_original_hierarchy_source_frames(
            view, animation_source_index=1, bars_source_index=2,
        )
        self.assertIsNotNone(bundle)
        self.assertEqual(
            len(bundle.proven_row_construction_origins_only), 16,
        )
        self.assertFalse(bundle.native_row_hit_behavior_recovered)
        self.assertEqual(
            (bundle.animation.source_frame_index_only,
             bundle.animation.source_frame_count,
             bundle.bars.source_frame_index_only,
             bundle.bars.source_frame_count),
            (1, 2, 2, 3),
        )
        for source, pixels, spec in (
            (bundle.animation, bytes((44, 55, 66, 88)), HIERARCHY_ANIM_SPEC),
            (bundle.bars, bytes((103, 104, 105, 200)), HIERARCHY_BARS_SPEC),
        ):
            with tempfile.TemporaryDirectory() as temp:
                png_file = Path(temp) / "diagnostic.png"
                png_file.write_bytes(source.source_frame_png)
                width, height, rgba = read_png_rgba(png_file)
            expected = pixels * (spec.frame_width * spec.frame_height)
            self.assertEqual((width, height), (spec.frame_width, spec.frame_height))
            self.assertEqual(rgba, expected)
            self.assertEqual(source.source_frame_rgba_sha256, sha256(expected).hexdigest())
            self.assertEqual(source.original_source_sha256, spec.source_sha256)
            self.assertIsNone(source.native_screen_placement)
            self.assertIsNone(source.native_mouse_state)
            self.assertIsNone(source.native_row_label_or_club)
        for bad in (-1, True, 2, 500):
            with self.subTest(index=bad):
                with self.assertRaises(OriginalHierarchyDebugError):
                    inspect_original_hierarchy_source_frames(
                        view, animation_source_index=bad,
                    )
        for bad in (-1, True, 3):
            with self.subTest(bars_index=bad):
                with self.assertRaises(OriginalHierarchyDebugError):
                    inspect_original_hierarchy_source_frames(
                        view, bars_source_index=bad,
                    )

    def test_absent_hierarchy_resources_do_not_invent_atlas_pixels(self):
        live = presenter()
        live.pointer(7, 478)
        self.assertIsNone(inspect_original_hierarchy_source_frames(live.snapshot()))
        window = OriginalFirstScreenTkDebug(live, FakeRoot(), FakeTk, FakeTtk)
        self.assertEqual(len(window.canvas.images), 3)
        window.step_hierarchy_source_frame("animation", 1)
        self.assertIn("No original hierarchy", window.status.get())

    def test_tk_inspector_shows_original_strips_only_in_debug_sidebar(self):
        live = presenter_with_hierarchy_art()
        root = FakeRoot()
        window = OriginalFirstScreenTkDebug(live, root, FakeTk, FakeTtk)
        self.assertEqual(len(window.canvas.images), 5)
        self.assertEqual(window.hierarchy_anim_label.values.get("image"), "")
        self.assertEqual(window.hierarchy_bars_label.values.get("image"), "")
        window.on_original_click(SimpleNamespace(x=7, y=478))
        # Only proven Back/Start geometry reaches original 800x600 canvas.
        self.assertEqual(len(window.canvas.images), 3)
        self.assertEqual(
            [(x, y) for x, y, _ in window.canvas.images[1:]],
            [(225, 301), (426, 301)],
        )
        self.assertEqual(
            (window.hierarchy_animation_source_index,
             window.hierarchy_bars_source_index), (0, 0),
        )
        self.assertIsInstance(window.hierarchy_anim_label.values["image"],
                              FakeTk.PhotoImage)
        self.assertIsInstance(window.hierarchy_bars_label.values["image"],
                              FakeTk.PhotoImage)
        self.assertIn("NOT original screen placement",
                      window.hierarchy_anim_label.values["text"])
        window.step_hierarchy_source_frame("animation", 1)
        self.assertEqual(
            (window.hierarchy_animation_source_index,
             window.hierarchy_bars_source_index), (1, 0),
        )
        window.step_hierarchy_source_frame("bars", 2)
        self.assertEqual(
            (window.hierarchy_animation_source_index,
             window.hierarchy_bars_source_index), (1, 2),
        )
        window.step_hierarchy_source_frame("animation", 1)
        window.step_hierarchy_source_frame("bars", 1)
        self.assertEqual(
            (window.hierarchy_animation_source_index,
             window.hierarchy_bars_source_index), (0, 0),
        )
        with self.assertRaisesRegex(ValueError, "Unknown"):
            window.step_hierarchy_source_frame("invented", 1)
        # Hierarchy pixels in the sidebar never synthesize a club selection.
        window.on_original_click(SimpleNamespace(x=20, y=78))
        self.assertIsNone(live.session.selected_club_id)
        self.assertEqual(len(window.canvas.images), 3)


if __name__ == "__main__":
    unittest.main()
