"""Tests for the standalone resolved-only Gate-14 Tk surface."""
from base64 import b64decode
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import struct
import unittest
import zlib

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_resolved_composite import (
    FastViewUnresolvedOverlapGroup,
    compose_fastview_resolved_only_pixels,
)
from gate14_fastview_tk_surface import (
    FastViewResolvedTkSurfaceError,
    draw_fastview_resolved_on_tk_canvas,
    encode_fastview_resolved_png,
)


SURFACE_PIXELS = 800 * 600


def plane(component, pixels):
    rgba = bytearray(SURFACE_PIXELS * 4)
    for pixel_index, value in pixels.items():
        offset = pixel_index * 4
        rgba[offset:offset + 4] = bytes(value)
    raw = bytes(rgba)
    return FastViewComponentRasterPlane(
        component=component,
        size=(800, 600),
        rgba=raw,
        source_layer_count=1,
        rgba_sha256=sha256(raw).hexdigest(),
    )


def composite():
    return compose_fastview_resolved_only_pixels(
        FastViewComponentRasterSet(
            chrome=plane(
                "direct_chrome",
                {
                    0: (10, 20, 30, 255),
                    10: (1, 2, 3, 255),
                },
            ),
            possession_diagram=plane(
                "possession_diagram",
                {
                    1: (40, 50, 60, 128),
                    10: (4, 5, 6, 255),
                },
            ),
            possession_figures=plane(
                "possession_figures_text",
                {2: (70, 80, 90, 255)},
            ),
        )
    )


def png_chunks(png):
    if png[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError("not a PNG")
    offset = 8
    output = []
    while offset < len(png):
        length = struct.unpack(">I", png[offset:offset + 4])[0]
        kind = png[offset + 4:offset + 8]
        payload = png[offset + 8:offset + 8 + length]
        output.append((kind, payload))
        offset += 12 + length
    return output


class FakePhotoImage:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeTk:
    NW = "nw"
    PhotoImage = FakePhotoImage


class FakeCanvas:
    def __init__(self):
        self.calls = []

    def create_image(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return 73


class FastViewResolvedTkSurfaceTests(unittest.TestCase):
    def test_png_preserves_exact_resolved_rgba_and_transparent_holes(self):
        source = composite()
        png = encode_fastview_resolved_png(source)
        chunks = png_chunks(png)

        ihdr = next(payload for kind, payload in chunks if kind == b"IHDR")
        self.assertEqual(
            struct.unpack(">IIBBBBB", ihdr),
            (800, 600, 8, 6, 0, 0, 0),
        )

        compressed = b"".join(
            payload for kind, payload in chunks if kind == b"IDAT"
        )
        scanlines = zlib.decompress(compressed)
        row_bytes = 800 * 4
        rebuilt = bytearray()
        for y in range(600):
            start = y * (row_bytes + 1)
            self.assertEqual(scanlines[start], 0)
            rebuilt.extend(scanlines[start + 1:start + 1 + row_bytes])

        self.assertEqual(bytes(rebuilt), source.rgba)
        # Pixel 10 is an unresolved overlap and therefore remains alpha-zero.
        self.assertEqual(source.unresolved_overlap_mask[10], 1)
        self.assertEqual(bytes(rebuilt[40:44]), b"\x00\x00\x00\x00")

    def test_draw_uses_native_origin_and_retains_unresolved_audit_state(self):
        source = composite()
        canvas = FakeCanvas()

        draw = draw_fastview_resolved_on_tk_canvas(source, FakeTk, canvas)

        self.assertEqual(draw.canvas_item_id, 73)
        self.assertEqual(len(canvas.calls), 1)
        args, kwargs = canvas.calls[0]
        self.assertEqual(args, (0, 0))
        self.assertIs(kwargs["image"], draw.photo_image)
        self.assertEqual(kwargs["anchor"], "nw")
        self.assertEqual(draw.photo_image.kwargs["format"], "png")
        self.assertEqual(
            b64decode(draw.photo_image.kwargs["data"]),
            draw.png,
        )
        self.assertEqual(draw.png_sha256, sha256(draw.png).hexdigest())
        self.assertEqual(draw.resolved_pixel_count, source.resolved_pixel_count)
        self.assertEqual(
            draw.unresolved_overlap_pixel_count,
            source.unresolved_overlap_pixel_count,
        )
        self.assertEqual(
            draw.unresolved_overlap_groups,
            (
                FastViewUnresolvedOverlapGroup(
                    components=("direct_chrome", "possession_diagram"),
                    pixel_count=1,
                    bounding_rect=(10, 0, 11, 1),
                ),
            ),
        )
        self.assertTrue(draw.unresolved_pixels_remain_transparent)
        self.assertFalse(draw.cross_component_z_order_recovered)
        self.assertFalse(draw.complete_fastview_frame)

    def test_rejects_wrong_inputs_and_false_fidelity_promotion(self):
        with self.assertRaisesRegex(
            FastViewResolvedTkSurfaceError,
            "exact resolved-only composite",
        ):
            encode_fastview_resolved_png(object())

        source = composite()
        canvas = FakeCanvas()
        draw = draw_fastview_resolved_on_tk_canvas(source, FakeTk, canvas)

        with self.assertRaisesRegex(
            FastViewResolvedTkSurfaceError,
            "cannot promote",
        ):
            replace(draw, complete_fastview_frame=True)

        class MissingTk:
            pass

        with self.assertRaisesRegex(
            FastViewResolvedTkSurfaceError,
            "PhotoImage and NW",
        ):
            draw_fastview_resolved_on_tk_canvas(source, MissingTk, canvas)

        with self.assertRaisesRegex(
            FastViewResolvedTkSurfaceError,
            "create_image",
        ):
            draw_fastview_resolved_on_tk_canvas(source, FakeTk, object())

    def test_surface_module_does_not_import_gameplay_or_gate13_host(self):
        source = Path(__file__).with_name(
            "gate14_fastview_tk_surface.py"
        ).read_text(encoding="utf-8")
        for forbidden in (
            "match_simulation",
            "match_calculator",
            "match_engine_rng",
            "human_gameplay",
            "original_game_host",
            "gate13_",
            "random",
        ):
            self.assertNotIn(f"import {forbidden}", source)
            self.assertNotIn(f"from {forbidden}", source)


if __name__ == "__main__":
    unittest.main()
