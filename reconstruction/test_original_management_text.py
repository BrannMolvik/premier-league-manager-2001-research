from pathlib import Path
from types import SimpleNamespace
import unittest

from original_league_tables_presenter import build_league_tables_snapshot
from original_management_text import (
    LEAGUE_TABLES_ROW_CLUB_FLAGS,
    LEAGUE_TABLES_ROW_FONT_ATLAS_SIZE,
    LEAGUE_TABLES_ROW_FONT_NATIVE_LINE_HEIGHT,
    LEAGUE_TABLES_ROW_FONT_OBJECT_VA,
    LEAGUE_TABLES_ROW_FONT_SLOT_VA,
    LEAGUE_TABLES_ROW_FONT_SOURCE_PATH,
    LEAGUE_TABLES_ROW_NATIVE_COLOR_16,
    LEAGUE_TABLES_ROW_NUMERIC_FLAGS,
    load_verified_management_text_resources,
    league_tables_row_text_overlays,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "original_assets" / "source"


class OriginalManagementTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resources = load_verified_management_text_resources(SOURCE_ROOT)

    def test_exact_league_table_font_binding_and_metrics(self):
        font = self.resources.league_tables_row_font
        self.assertEqual(LEAGUE_TABLES_ROW_FONT_SLOT_VA, 0x947578)
        self.assertEqual(LEAGUE_TABLES_ROW_FONT_OBJECT_VA, 0x9269F0)
        self.assertEqual(
            LEAGUE_TABLES_ROW_FONT_SOURCE_PATH,
            "Fonts/Zurich_BdXCn_BT_16pixel.fnt",
        )
        self.assertEqual(
            (font.atlas_width, font.atlas_height),
            LEAGUE_TABLES_ROW_FONT_ATLAS_SIZE,
        )
        self.assertEqual(
            font.native_line_height(),
            LEAGUE_TABLES_ROW_FONT_NATIVE_LINE_HEIGHT,
        )
        self.assertEqual(LEAGUE_TABLES_ROW_CLUB_FLAGS, 0x21)
        self.assertEqual(LEAGUE_TABLES_ROW_NUMERIC_FLAGS, 0x24)
        self.assertEqual(LEAGUE_TABLES_ROW_NATIVE_COLOR_16, 0xFFFF)

    def test_one_source_row_rasterizes_rank_club_and_seven_stats(self):
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

        overlays = league_tables_row_text_overlays(snapshot, self.resources)

        self.assertEqual(len(overlays), 9)
        self.assertEqual([item.role for item in overlays], [
            "rank", "club", "stat", "stat", "stat", "stat", "stat", "stat", "stat",
        ])
        self.assertEqual([item.text for item in overlays], [
            "1", "Arsenal", "1", "1", "0", "0", "2", "0", "3",
        ])
        self.assertEqual(overlays[0].raw_flags, 0x24)
        self.assertEqual(overlays[1].raw_flags, 0x21)
        self.assertEqual(overlays[1].control_rect, (316, 185, 214, 12))
        self.assertEqual(overlays[2].control_rect, (532, 185, 27, 12))
        for item in overlays:
            self.assertEqual(item.native_color_16, 0xFFFF)
            self.assertEqual(item.font_source_path, LEAGUE_TABLES_ROW_FONT_SOURCE_PATH)
            self.assertGreater(len(item.rgba), 0)
            left, top, width, height = item.control_rect
            self.assertGreaterEqual(item.x, left)
            self.assertGreaterEqual(item.y, top)
            self.assertLessEqual(item.x + item.width, left + width)
            self.assertLessEqual(item.y + item.height, top + height)

    def test_second_row_uses_exact_16_pixel_source_step(self):
        rows = tuple(
            SimpleNamespace(
                position=index + 1,
                club_id=index,
                club_name=("Arsenal", "Chelsea")[index],
                played=1,
                wins=1,
                draws=0,
                losses=0,
                goals_for=1,
                goals_against=0,
                points=3,
            )
            for index in range(2)
        )
        overlays = league_tables_row_text_overlays(
            build_league_tables_snapshot(rows),
            self.resources,
        )
        club_overlays = [item for item in overlays if item.role == "club"]
        self.assertEqual(
            [item.control_rect for item in club_overlays],
            [(316, 185, 214, 12), (316, 201, 214, 12)],
        )


if __name__ == "__main__":
    unittest.main()
