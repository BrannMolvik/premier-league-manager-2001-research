import hashlib
import os
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage, decode_ea444_file
from ea444_quantization import quantization_from_verified_exe_path
from ea444_tables import tables_from_verified_exe_path
from original_front_end_layout import (
    PSTARTMENU_BACKGROUND_RECT,
    SCREEN_SIZE,
    TEAMSELECT_BACKGROUND_RECT,
    TEAMSELECT_ROOT_RECT,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    TEAMSELECT_HIERARCHY_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    TEAMSELECT_HIERARCHY_BARS_PATH,
    OriginalFrontEndLayoutError,
    compose_pstartmenu_background,
    compose_teamselect_background,
)


def solid(width, height, rgba):
    return EA444DecodedImage(
        width, height, bytes(rgba) * (width * height), 0, 0
    )


class OriginalFrontEndLayoutTests(unittest.TestCase):
    def test_confirmed_executable_rectangles_are_literal(self):
        self.assertEqual(SCREEN_SIZE, (800, 600))
        self.assertEqual(
            PSTARTMENU_BACKGROUND_RECT,
            type(PSTARTMENU_BACKGROUND_RECT)(134, 34, 532, 532),
        )
        self.assertEqual(
            TEAMSELECT_ROOT_RECT,
            type(TEAMSELECT_ROOT_RECT)(0, 0, 800, 600),
        )
        self.assertEqual(
            TEAMSELECT_BACKGROUND_RECT,
            type(TEAMSELECT_BACKGROUND_RECT)(0, 0, 800, 558),
        )
        self.assertEqual(
            TEAMSELECT_HIERARCHY_ROW_ORIGINS,
            tuple((20, 78 + 30 * i) for i in range(16)),
        )
        self.assertEqual(TEAMSELECT_HIERARCHY_ROW_ORIGINS[0], (20, 78))
        self.assertEqual(TEAMSELECT_HIERARCHY_ROW_ORIGINS[-1], (20, 528))
        self.assertEqual(TEAMSELECT_HIERARCHY_FRAME_SIZE, (30, 29))
        self.assertEqual(TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE, (168, 29))
        self.assertTrue(TEAMSELECT_HIERARCHY_ANIM_PATH.endswith(
            "choice_league_but_anim.444"
        ))
        self.assertTrue(TEAMSELECT_HIERARCHY_BARS_PATH.endswith(
            "choice_league_but_bars.444"
        ))

    def test_compositor_preserves_global_margin_and_exact_overlay(self):
        base = solid(800, 600, (1, 2, 3, 255))
        menu = solid(532, 532, (8, 9, 10, 255))
        result = compose_pstartmenu_background(base, menu)
        def pixel(x, y):
            start = (y * 800 + x) * 4
            return tuple(result[start:start + 4])
        self.assertEqual(pixel(0, 0), (1, 2, 3, 255))
        self.assertEqual(pixel(133, 34), (1, 2, 3, 255))
        self.assertEqual(pixel(134, 34), (8, 9, 10, 255))
        self.assertEqual(pixel(665, 565), (8, 9, 10, 255))
        self.assertEqual(pixel(666, 565), (1, 2, 3, 255))

    def test_rejects_wrong_source_geometry(self):
        base = solid(800, 600, (0, 0, 0, 255))
        wrong = solid(1, 1, (0, 0, 0, 255))
        with self.assertRaises(OriginalFrontEndLayoutError):
            compose_pstartmenu_background(base, wrong)
        with self.assertRaises(OriginalFrontEndLayoutError):
            compose_teamselect_background(base, wrong)

    @unittest.skipUnless(
        os.environ.get("FM2001_ORIGINAL_EXE")
        and os.environ.get("FM2001_ORIGINAL_444_ROOT"),
        "Original licensed graphics and executable not bundled with CI",
    )
    def test_real_original_background_compositions_have_exact_rgba_hashes(self):
        exe = Path(os.environ["FM2001_ORIGINAL_EXE"])
        root = Path(os.environ["FM2001_ORIGINAL_444_ROOT"])
        tables = tables_from_verified_exe_path(exe)
        quant = quantization_from_verified_exe_path(exe)
        base = decode_ea444_file(
            root / "Generic/bground.444", tables=tables, quant=quant
        )
        menu = decode_ea444_file(
            root / "Generic/main_menu/main_menu_bground.444",
            tables=tables, quant=quant,
        )
        team = decode_ea444_file(
            root / "Generic/team_choice/background.444",
            tables=tables, quant=quant,
        )
        self.assertEqual(
            hashlib.sha256(
                compose_pstartmenu_background(base, menu)
            ).hexdigest(),
            "e5b9190b830440a340f162a81eab59270182b74a15bae0a3f24660a7c5d21046",
        )
        self.assertEqual(
            hashlib.sha256(
                compose_teamselect_background(base, team)
            ).hexdigest(),
            "6a438ab60e96a3b53667fd1373ad24442d4272d50475a7c89108ac45dbe5f501",
        )


if __name__ == "__main__":
    unittest.main()
