import hashlib
import os
from pathlib import Path
import unittest

from ea444_decoder import EA444DecodedImage, decode_ea444_file
from ea444_quantization import quantization_from_verified_exe_path
from ea444_tables import tables_from_verified_exe_path
from original_front_end_layout import (
    PSTARTMENU_BACKGROUND_RECT,
    PSTARTMENU_ACTION_ATLAS_PATH,
    PSTARTMENU_ACTION_FRAME_SIZE,
    PSTARTMENU_ACTIONS,
    SCREEN_SIZE,
    TEAMSELECT_BACKGROUND_RECT,
    TEAMSELECT_ROOT_RECT,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    TEAMSELECT_HIERARCHY_CONTROL_IDS,
    TEAMSELECT_HIERARCHY_OBJECT_OFFSETS,
    TEAMSELECT_CLUB_ROW_ORIGINS,
    TEAMSELECT_CLUB_CONTROL_IDS,
    TEAMSELECT_CLUB_OBJECT_OFFSETS,
    TEAMSELECT_ENGLISH_COUNTRY_ORDER,
    TEAMSELECT_HIERARCHY_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    TEAMSELECT_HIERARCHY_BARS_PATH,
    TEAMSELECT_ACTION_ATLAS_PATH,
    TEAMSELECT_ACTION_FRAME_SIZE,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_RECT,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_START_EVENT,
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
        self.assertEqual(PSTARTMENU_ACTION_FRAME_SIZE, (169, 25))
        self.assertTrue(
            PSTARTMENU_ACTION_ATLAS_PATH.endswith("button_type_1.444")
        )
        self.assertEqual(
            tuple((action.event, action.language_index, action.rect)
                  for action in PSTARTMENU_ACTIONS),
            (
                (1, 0, type(PSTARTMENU_BACKGROUND_RECT)(181, 478, 169, 25)),
                (2, 1, type(PSTARTMENU_BACKGROUND_RECT)(7, 478, 169, 25)),
                (3, 2, type(PSTARTMENU_BACKGROUND_RECT)(355, 478, 169, 25)),
                (4, 6, type(PSTARTMENU_BACKGROUND_RECT)(181, 508, 169, 25)),
            ),
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
        self.assertEqual(TEAMSELECT_HIERARCHY_CONTROL_IDS, tuple(range(1, 17)))
        self.assertEqual(TEAMSELECT_HIERARCHY_OBJECT_OFFSETS,
                         tuple(0x2A24 + 0x4C * i for i in range(16)))
        self.assertEqual(TEAMSELECT_CLUB_ROW_ORIGINS,
                         tuple((581, 78 + 20 * i) for i in range(24)))
        self.assertEqual(TEAMSELECT_CLUB_CONTROL_IDS, tuple(range(0x11, 0x29)))
        self.assertEqual(TEAMSELECT_CLUB_OBJECT_OFFSETS,
                         tuple(0x2EE4 + 0x40 * i for i in range(24)))
        self.assertEqual(
            TEAMSELECT_ENGLISH_COUNTRY_ORDER,
            ((26, "England"), (66, "Scotland"), (33, "Germany"),
             (40, "Italy"), (73, "Spain"), (31, "France"),
             (24, "Holland"), (9, "Belgium")),
        )
        self.assertEqual(TEAMSELECT_HIERARCHY_FRAME_SIZE, (30, 29))
        self.assertEqual(TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE, (168, 29))
        self.assertTrue(TEAMSELECT_HIERARCHY_ANIM_PATH.endswith(
            "choice_league_but_anim.444"
        ))
        self.assertTrue(TEAMSELECT_HIERARCHY_BARS_PATH.endswith(
            "choice_league_but_bars.444"
        ))
        self.assertEqual(TEAMSELECT_ACTION_FRAME_SIZE, (150, 32))
        self.assertTrue(
            TEAMSELECT_ACTION_ATLAS_PATH.endswith("choice_start_anim.444")
        )
        self.assertEqual(
            TEAMSELECT_BACK_RECT,
            type(TEAMSELECT_BACK_RECT)(225, 301, 150, 32),
        )
        self.assertEqual(
            TEAMSELECT_START_RECT,
            type(TEAMSELECT_START_RECT)(426, 301, 150, 32),
        )
        self.assertEqual(TEAMSELECT_BACK_EVENT, 0x29)
        self.assertEqual(TEAMSELECT_START_EVENT, 0x2A)

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
