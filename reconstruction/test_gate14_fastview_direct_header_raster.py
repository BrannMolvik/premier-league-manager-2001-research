"""Tests for exact direct FastView header text rasterization."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import unittest

from gate14_fastview_direct_header_raster import (
    DIRECT_HEADER_FONT_ATLAS_SIZE,
    DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT,
    DIRECT_HEADER_TEXT_COMPONENT,
    FastViewDirectHeaderRasterError,
    build_fastview_direct_header_raster,
    direct_header_line_origin,
    direct_header_raster_contract,
    load_verified_direct_header_font,
)
from gate14_fastview_direct_header_text import (
    FIRST_TEXT_RECT,
    SECOND_TEXT_RECT,
    TEXT_FONT_SOURCE_SHA256,
    TEXT_FONT_SOURCE_SIZE,
    TEXT_NATIVE_COLOR_16,
)


FIRST_SOURCE_SHAPED_TEXT = "FRIENDLY MATCH  -  Referee A. Smith"
SECOND_SOURCE_SHAPED_TEXT = "Highbury  -  Attendance 38123"


class FastViewDirectHeaderRasterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parent.parent
        cls.font = load_verified_direct_header_font(cls.root)

    def test_loads_exact_provenance_staged_style3_font(self):
        path = (
            self.root
            / "original_assets"
            / "source"
            / "Fonts"
            / "Zurich_XCn_BT_16pixel.fnt"
        )
        data = path.read_bytes()
        self.assertEqual(len(data), TEXT_FONT_SOURCE_SIZE)
        self.assertEqual(sha256(data).hexdigest(), TEXT_FONT_SOURCE_SHA256)
        self.assertEqual(
            (self.font.atlas_width, self.font.atlas_height),
            DIRECT_HEADER_FONT_ATLAS_SIZE,
        )
        self.assertEqual(
            self.font.native_line_height(),
            DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT,
        )
        self.assertEqual(DIRECT_HEADER_FONT_ATLAS_SIZE, (1261, 17))
        self.assertEqual(DIRECT_HEADER_FONT_NATIVE_LINE_HEIGHT, 18)

    def test_centering_uses_source_signed_half_and_second_line_clips(self):
        first = direct_header_line_origin(
            self.font, FIRST_SOURCE_SHAPED_TEXT, FIRST_TEXT_RECT
        )
        second = direct_header_line_origin(
            self.font, SECOND_SOURCE_SHAPED_TEXT, SECOND_TEXT_RECT
        )
        self.assertEqual(first[1], 51)
        self.assertEqual(second[1], 69)
        self.assertEqual(
            first[0],
            250 + (300 - self.font.measure_text(FIRST_SOURCE_SHAPED_TEXT)) // 2,
        )
        second_delta = 300 - self.font.measure_text(SECOND_SOURCE_SHAPED_TEXT)
        expected_second_x = 250 + (
            second_delta // 2 if second_delta >= 0 else -((-second_delta) // 2)
        )
        self.assertEqual(second[0], expected_second_x)

    def test_builds_two_layer_white_endpoint_raster_with_exact_clips(self):
        raster = build_fastview_direct_header_raster(
            self.font,
            FIRST_SOURCE_SHAPED_TEXT,
            SECOND_SOURCE_SHAPED_TEXT,
        )
        self.assertEqual(raster.component, DIRECT_HEADER_TEXT_COMPONENT)
        self.assertEqual(raster.size, (800, 600))
        self.assertEqual(raster.source_layer_count, 2)
        self.assertEqual(
            tuple(item.control_rect for item in raster.placements),
            (FIRST_TEXT_RECT, SECOND_TEXT_RECT),
        )
        self.assertEqual(raster.placements[0].line_origin[1], 51)
        self.assertEqual(raster.placements[1].line_origin[1], 69)
        self.assertEqual(raster.native_color_16, TEXT_NATIVE_COLOR_16)
        self.assertEqual(sha256(raster.rgba).hexdigest(), raster.rgba_sha256)

        def alpha_at(x, y):
            return raster.rgba[(y * 800 + x) * 4 + 3]

        # The second line's native line origin is above its 16px source clip.
        # No pixel may escape the control even though native centering places
        # the 18px line at y=69.
        self.assertTrue(all(alpha_at(x, 69) == 0 for x in range(250, 550)))
        self.assertTrue(
            any(
                alpha_at(x, y)
                for y in range(SECOND_TEXT_RECT[1], SECOND_TEXT_RECT[3])
                for x in range(SECOND_TEXT_RECT[0], SECOND_TEXT_RECT[2])
            )
        )
        self.assertTrue(
            any(
                alpha_at(x, y)
                for y in range(FIRST_TEXT_RECT[1], FIRST_TEXT_RECT[3])
                for x in range(FIRST_TEXT_RECT[0], FIRST_TEXT_RECT[2])
            )
        )

    def test_rejects_non_source_rect_empty_text_and_fidelity_promotion(self):
        with self.assertRaisesRegex(
            FastViewDirectHeaderRasterError, "non-empty"
        ):
            direct_header_line_origin(self.font, "", FIRST_TEXT_RECT)
        with self.assertRaisesRegex(
            FastViewDirectHeaderRasterError, "not source-backed"
        ):
            direct_header_line_origin(
                self.font, FIRST_SOURCE_SHAPED_TEXT, (0, 0, 10, 10)
            )

        raster = build_fastview_direct_header_raster(
            self.font,
            FIRST_SOURCE_SHAPED_TEXT,
            SECOND_SOURCE_SHAPED_TEXT,
        )
        with self.assertRaisesRegex(
            FastViewDirectHeaderRasterError, "cannot promote"
        ):
            replace(raster, runtime_metadata_bound=True)
        with self.assertRaisesRegex(
            FastViewDirectHeaderRasterError, "cannot promote"
        ):
            replace(raster, complete_fastview_frame_recovered=True)

    def test_contract_promotes_pixels_only_not_runtime_or_complete_frame(self):
        contract = direct_header_raster_contract()
        self.assertEqual(contract["component"], DIRECT_HEADER_TEXT_COMPONENT)
        self.assertEqual(contract["source_font_size"], TEXT_FONT_SOURCE_SIZE)
        self.assertEqual(contract["source_font_sha256"], TEXT_FONT_SOURCE_SHA256)
        self.assertEqual(
            contract["control_rects"], (FIRST_TEXT_RECT, SECOND_TEXT_RECT)
        )
        self.assertTrue(contract["control_clipping_applied"])
        self.assertTrue(contract["exact_header_text_pixels_recovered"])
        self.assertFalse(contract["runtime_metadata_bound"])
        self.assertFalse(contract["global_fastview_z_order_recovered"])
        self.assertFalse(contract["complete_fastview_frame_recovered"])
        self.assertFalse(contract["gate14_complete"])


if __name__ == "__main__":
    unittest.main()
