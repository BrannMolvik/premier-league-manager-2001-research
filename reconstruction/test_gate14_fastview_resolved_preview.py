"""Tests for deterministic resolved-only FastView PNG previews."""
from dataclasses import replace
from hashlib import sha256
import struct
import unittest
import zlib

from gate14_fastview_component_rasters import (
    FastViewComponentRasterPlane,
    FastViewComponentRasterSet,
)
from gate14_fastview_resolved_composite import compose_fastview_resolved_only_pixels
from gate14_fastview_resolved_preview import (
    FastViewResolvedPreviewError,
    PNG_SIGNATURE,
    build_fastview_resolved_preview,
)


WIDTH = 800
HEIGHT = 600


def plane(component, pixels):
    rgba = bytearray(WIDTH * HEIGHT * 4)
    for index, value in pixels.items():
        offset = index * 4
        rgba[offset:offset + 4] = bytes(value)
    payload = bytes(rgba)
    return FastViewComponentRasterPlane(
        component=component,
        size=(WIDTH, HEIGHT),
        rgba=payload,
        source_layer_count=1,
        rgba_sha256=sha256(payload).hexdigest(),
    )


def composite():
    rasters = FastViewComponentRasterSet(
        chrome=plane(
            "direct_chrome",
            {
                0: (10, 20, 30, 255),
                1: (11, 21, 31, 255),
            },
        ),
        possession_diagram=plane(
            "possession_diagram",
            {
                1: (40, 50, 60, 255),
                2: (41, 51, 61, 255),
            },
        ),
        possession_figures=plane(
            "possession_figures_text",
            {
                3: (70, 80, 90, 128),
            },
        ),
    )
    return compose_fastview_resolved_only_pixels(rasters)


def png_chunks(payload):
    if not payload.startswith(PNG_SIGNATURE):
        raise AssertionError("not PNG")
    offset = len(PNG_SIGNATURE)
    chunks = []
    while offset < len(payload):
        length = struct.unpack(">I", payload[offset:offset + 4])[0]
        kind = payload[offset + 4:offset + 8]
        data = payload[offset + 8:offset + 8 + length]
        chunks.append((kind, data))
        offset += 12 + length
    return chunks


def decode_filter_zero_png(payload, *, bytes_per_pixel):
    chunks = png_chunks(payload)
    ihdr = next(data for kind, data in chunks if kind == b"IHDR")
    width, height, bit_depth, _color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", ihdr
    )
    if (bit_depth, compression, filtering, interlace) != (8, 0, 0, 0):
        raise AssertionError("unexpected PNG encoding")
    raw = zlib.decompress(
        b"".join(data for kind, data in chunks if kind == b"IDAT")
    )
    stride = width * bytes_per_pixel
    rows = []
    offset = 0
    for _ in range(height):
        if raw[offset] != 0:
            raise AssertionError("unexpected PNG row filter")
        offset += 1
        rows.append(raw[offset:offset + stride])
        offset += stride
    return width, height, b"".join(rows)


class FastViewResolvedPreviewTests(unittest.TestCase):
    def test_exports_exact_resolved_rgba_and_binary_overlap_mask(self):
        source = composite()
        preview = build_fastview_resolved_preview(source)

        self.assertEqual(preview.size, (800, 600))
        self.assertEqual(preview.resolved_pixel_count, 3)
        self.assertEqual(preview.unresolved_overlap_pixel_count, 1)
        self.assertIs(preview.overlap_groups, source.unresolved_overlap_groups)
        self.assertEqual(preview.source_composite_rgba_sha256, source.rgba_sha256)
        self.assertEqual(
            preview.source_overlap_mask_sha256,
            source.unresolved_overlap_mask_sha256,
        )

        width, height, rgba = decode_filter_zero_png(
            preview.rgba_png,
            bytes_per_pixel=4,
        )
        self.assertEqual((width, height), (800, 600))
        self.assertEqual(rgba, source.rgba)

        width, height, mask = decode_filter_zero_png(
            preview.overlap_mask_png,
            bytes_per_pixel=1,
        )
        self.assertEqual((width, height), (800, 600))
        self.assertEqual(
            mask,
            bytes(255 if value else 0 for value in source.unresolved_overlap_mask),
        )

        # Pixel 1 is unresolved, so the visible RGBA export preserves the
        # compositor's transparent fail-closed result instead of choosing a winner.
        self.assertEqual(rgba[4:8], b"\x00\x00\x00\x00")
        self.assertEqual(mask[1], 255)

    def test_png_output_is_deterministic_and_integrity_bound(self):
        source = composite()
        first = build_fastview_resolved_preview(source)
        second = build_fastview_resolved_preview(source)

        self.assertEqual(first.rgba_png, second.rgba_png)
        self.assertEqual(first.overlap_mask_png, second.overlap_mask_png)
        self.assertEqual(first.rgba_png_sha256, sha256(first.rgba_png).hexdigest())
        self.assertEqual(
            first.overlap_mask_png_sha256,
            sha256(first.overlap_mask_png).hexdigest(),
        )

        with self.assertRaisesRegex(FastViewResolvedPreviewError, "SHA-256"):
            replace(first, rgba_png_sha256="0" * 64)

    def test_preview_cannot_promote_unresolved_frame_fidelity(self):
        preview = build_fastview_resolved_preview(composite())
        for field in (
            "cross_component_z_order_recovered",
            "flattened_frame_available",
            "complete_fastview_frame",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(
                    FastViewResolvedPreviewError,
                    "cannot promote",
                ):
                    replace(preview, **{field: True})

    def test_requires_exact_resolved_composite(self):
        with self.assertRaisesRegex(
            FastViewResolvedPreviewError,
            "exact FastViewResolvedOnlyComposite",
        ):
            build_fastview_resolved_preview(object())


if __name__ == "__main__":
    unittest.main()
