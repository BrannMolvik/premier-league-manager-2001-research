"""Regressions for source-backed PLeagueTables selector/header shell."""
import unittest

import original_league_tables_resources as lt

from original_league_tables_resources import (
    LEAGUE_TABLES_ACTIVE_COUNTRY_INDEX_OFFSET,
    LEAGUE_TABLES_CLASS,
    LEAGUE_TABLES_CONSTRUCTOR_VA,
    LEAGUE_TABLES_COUNTRY_CONTROL_BASE_OFFSET,
    LEAGUE_TABLES_COUNTRY_EVENT_FIRST,
    LEAGUE_TABLES_COUNTRY_HEADER_CALL_VA,
    LEAGUE_TABLES_COUNTRY_HEADER_CONTROL_OFFSET,
    LEAGUE_TABLES_COUNTRY_HEADER_ENGLISH_INDEX,
    LEAGUE_TABLES_COUNTRY_HEADER_GLOBAL_VA,
    LEAGUE_TABLES_COUNTRY_HEADER_SETUP_VA,
    LEAGUE_TABLES_COUNTRY_HEADER_TEXT,
    LEAGUE_TABLES_COUNTRY_HEADER_WIDTH,
    LEAGUE_TABLES_COUNTRY_HEADER_X,
    LEAGUE_TABLES_COUNTRY_IDS,
    LEAGUE_TABLES_COUNTRY_ID_BASE_OFFSET,
    LEAGUE_TABLES_COUNTRY_NAMES,
    LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT,
    LEAGUE_TABLES_COUNTRY_SETUP_CALLS,
    LEAGUE_TABLES_EVENT_VA,
    LEAGUE_TABLES_HEADER_TEXTS,
    LEAGUE_TABLES_SECONDARY_SELECTOR_BASE_OFFSET,
    LEAGUE_TABLES_SECONDARY_SELECTOR_COUNT,
    LEAGUE_TABLES_SECONDARY_SETUP_CALLS,
    LEAGUE_TABLES_SELECTOR_CLASS,
    LEAGUE_TABLES_SELECTOR_CONSTRUCTOR_VA,
    LEAGUE_TABLES_SELECTOR_SETUP_VA,
    LEAGUE_TABLES_SELECTOR_STRIDE,
    LEAGUE_TABLES_SETUP_VA,
    LEAGUE_TABLES_TERTIARY_SELECTOR_BASE_OFFSET,
    LEAGUE_TABLES_TERTIARY_SELECTOR_COUNT,
    LEAGUE_TABLES_TERTIARY_SETUP_CALLS,
    LEAGUE_TABLES_TEXT_SETUP_VA,
    LEAGUE_TABLES_TYPE_DESCRIPTOR_VA,
    LEAGUE_TABLES_VFTABLE_VA,
    OriginalLeagueTablesError,
    assert_league_tables_identity_contract,
    league_tables_country_event_index,
    league_tables_country_identity,
)


class OriginalLeagueTablesResourceTests(unittest.TestCase):
    def test_concrete_panel_and_shared_selector_identity_are_exact(self):
        assert_league_tables_identity_contract()
        self.assertEqual(LEAGUE_TABLES_CLASS, "PLeagueTables")
        self.assertEqual(LEAGUE_TABLES_CONSTRUCTOR_VA, 0x448640)
        self.assertEqual(LEAGUE_TABLES_SETUP_VA, 0x446F00)
        self.assertEqual(LEAGUE_TABLES_EVENT_VA, 0x448C40)
        self.assertEqual(LEAGUE_TABLES_TYPE_DESCRIPTOR_VA, 0x81B458)
        self.assertEqual(LEAGUE_TABLES_VFTABLE_VA, 0x7C00C8)
        self.assertEqual(LEAGUE_TABLES_SELECTOR_CLASS, "fmRadioTextSm@fm2001_ctrls")
        self.assertEqual(LEAGUE_TABLES_SELECTOR_CONSTRUCTOR_VA, 0x5D4B50)
        self.assertEqual(LEAGUE_TABLES_SELECTOR_SETUP_VA, 0x5D4C70)
        self.assertEqual(LEAGUE_TABLES_SELECTOR_STRIDE, 0x4C)

    def test_eight_country_selector_order_events_and_object_offsets_are_exact(self):
        self.assertEqual(LEAGUE_TABLES_ACTIVE_COUNTRY_INDEX_OFFSET, 0x64)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_ID_BASE_OFFSET, 0x1D4)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_CONTROL_BASE_OFFSET, 0x23C)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT, 8)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_EVENT_FIRST, 1)
        self.assertEqual(
            LEAGUE_TABLES_COUNTRY_IDS,
            (26, 33, 40, 73, 66, 31, 24, 9),
        )
        self.assertEqual(
            LEAGUE_TABLES_COUNTRY_NAMES,
            ("England", "Germany", "Italy", "Spain", "Scotland", "France", "Holland", "Belgium"),
        )
        self.assertEqual(
            LEAGUE_TABLES_COUNTRY_SETUP_CALLS,
            (0x446FE5, 0x447044, 0x4470A5, 0x447103, 0x447164, 0x4471C4, 0x447227, 0x44728F),
        )
        for event_id, expected in enumerate(zip(LEAGUE_TABLES_COUNTRY_IDS, LEAGUE_TABLES_COUNTRY_NAMES), 1):
            self.assertEqual(league_tables_country_event_index(event_id), event_id - 1)
            self.assertEqual(league_tables_country_identity(event_id), expected)

    def test_country_event_lookup_fails_closed_outside_exact_1_to_8_range(self):
        for bad in (True, "1", 0, 9, -1):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalLeagueTablesError):
                    league_tables_country_event_index(bad)

    def test_division_selector_family_is_dynamic_leaguebase_content(self):
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_HEADER_CONTROL_OFFSET, 0x49C)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_HEADER_CALL_VA, 0x4472C1)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_HEADER_GLOBAL_VA, 0x982678)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_HEADER_ENGLISH_INDEX, 2144)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_HEADER_TEXT, "DIVISION")
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_SELECTOR_BASE_OFFSET, 0x4E4)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_SELECTOR_COUNT, 5)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_EVENT_FIRST, 9)
        self.assertEqual(lt.LEAGUE_TABLES_SELECTED_DIVISION_INDEX_OFFSET, 0x68)
        self.assertEqual(lt.LEAGUE_TABLES_SELECTED_DIVISION_IDENTITY_OFFSET, 0x8C)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_IDENTITY_ARRAY_OFFSET, 0xA0)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_REBUILD_VA, 0x448E60)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_SET_TEXT_VA, 0x5D3F10)
        self.assertEqual(lt.LEAGUE_TABLES_LEAGUE_BASE_TYPE_DESCRIPTOR_VA, 0x818AA0)
        self.assertEqual(lt.LEAGUE_TABLES_DUMMY_LEAGUE_TYPE_DESCRIPTOR_VA, 0x81B498)
        self.assertEqual(lt.LEAGUE_TABLES_RTDYNAMICCAST_VA, 0x668995)
        self.assertEqual(lt.LEAGUE_TABLES_COUNTRY_COMPETITION_ARRAY_OFFSET, 0x48)
        self.assertEqual(lt.LEAGUE_TABLES_COUNTRY_COMPETITION_COUNT_OFFSET, 0x4C)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_CAPTION_OFFSET, 0x14)
        self.assertEqual(lt.LEAGUE_TABLES_DIVISION_IDENTITY_WORD_OFFSET, 0x20)
        self.assertEqual(
            lt.LEAGUE_TABLES_DIVISION_SETUP_CALLS,
            (0x447306, 0x447353, 0x4473A1, 0x4473F2, 0x447440),
        )
        for event_id in range(9, 14):
            self.assertEqual(lt.league_tables_division_event_index(event_id), event_id - 9)
        for bad in (True, "9", 8, 14, -1):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalLeagueTablesError):
                    lt.league_tables_division_event_index(bad)

    def test_sort_by_family_is_exact_league_position_vs_current_form(self):
        self.assertEqual(lt.LEAGUE_TABLES_SORT_HEADER_CONTROL_OFFSET, 0x660)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_HEADER_CALL_VA, 0x447472)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_HEADER_GLOBAL_VA, 0x983A94)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_HEADER_ENGLISH_INDEX, 857)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_HEADER_TEXT, "Sort By")
        self.assertEqual(lt.LEAGUE_TABLES_SORT_SELECTOR_BASE_OFFSET, 0x6A8)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_SELECTOR_COUNT, 2)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_EVENT_FIRST, 14)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_STATE_OFFSET, 0x98)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_DEFAULT_STATE, 0)
        self.assertEqual(lt.LEAGUE_TABLES_SORT_SETUP_CALLS, (0x4474B5, 0x447501))
        self.assertEqual(
            lt.LEAGUE_TABLES_SORT_OPTIONS,
            (
                ("League Position", 0x983C04, 765, 14, 0),
                ("Current Form", 0x983A90, 858, 15, 1),
            ),
        )
        self.assertEqual(lt.LEAGUE_TABLES_SORT_APPLY_VA, 0x449090)
        self.assertEqual(lt.league_tables_sort_state(14), 0)
        self.assertEqual(lt.league_tables_sort_state(15), 1)
        for bad in (True, "14", 13, 16, -1):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalLeagueTablesError):
                    lt.league_tables_sort_state(bad)

    def test_country_header_is_source_bound_to_original_english_text(self):
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_CONTROL_OFFSET, 0x1F4)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_SETUP_VA, 0x5D6090)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_CALL_VA, 0x446F92)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_X, 27)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_WIDTH, 150)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_GLOBAL_VA, 0x982670)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_ENGLISH_INDEX, 2146)
        self.assertEqual(LEAGUE_TABLES_COUNTRY_HEADER_TEXT, "Country")

    def test_table_header_band_preserves_exact_text_and_rectangles(self):
        self.assertEqual(LEAGUE_TABLES_TEXT_SETUP_VA, 0x6503F0)
        self.assertEqual(
            [(h.label, h.english_global_va, h.english_index, h.setup_call_va, h.rect)
             for h in LEAGUE_TABLES_HEADER_TEXTS],
            [
                (None, None, None, 0x447594, (316, 152, 214, 19)),
                ("P", 0x9830F4, 1473, 0x4475D7, (532, 152, 27, 19)),
                ("W", 0x9830F0, 1474, 0x44761A, (561, 152, 27, 19)),
                ("D", 0x9830EC, 1475, 0x44765D, (590, 152, 27, 19)),
                ("L", 0x9830E8, 1476, 0x4476A0, (619, 152, 27, 19)),
                ("F", 0x9830E4, 1477, 0x4476E3, (648, 152, 27, 19)),
                ("A", 0x9830E0, 1478, 0x447726, (677, 152, 27, 19)),
                ("Pts", 0x9830DC, 1479, 0x447769, (706, 152, 27, 19)),
            ],
        )


    def test_concrete_list_and_row_identity_geometry_are_exact(self):
        self.assertEqual(lt.LEAGUE_TABLES_LIST_CLASS, "CLeagueTableList")
        self.assertEqual(lt.LEAGUE_TABLES_LIST_TYPE_DESCRIPTOR_VA, 0x81B478)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_COL_VA, 0x7E1520)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_VFTABLE_VA, 0x7C011C)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_OBJECT_OFFSET, 0x9BC)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_RECT, (270, 184, 477, 384))
        self.assertEqual(lt.LEAGUE_TABLES_LIST_ROW_COUNT, 24)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_ROW_STEP, 16)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_AUX_VALUE, 8)
        self.assertEqual(lt.LEAGUE_TABLES_LIST_ROW_CREATE_VA, 0x447820)

        self.assertEqual(lt.LEAGUE_TABLES_ROW_CLASS, "PLeagueTableRow")
        self.assertEqual(lt.LEAGUE_TABLES_ROW_TYPE_DESCRIPTOR_VA, 0x81B378)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_COL_VA, 0x7E1398)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_VFTABLE_VA, 0x7BFEC0)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_SETUP_VA, 0x446930)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_ALLOC_SIZE, 0x4A8)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_CHILD_COUNT, 12)

    def test_row_column_projection_matches_header_and_source_fields(self):
        self.assertEqual(
            lt.LEAGUE_TABLES_ROW_COLUMN_LABELS,
            ("P", "W", "D", "L", "F", "A", "Pts"),
        )
        self.assertEqual(
            lt.LEAGUE_TABLES_ROW_STAT_TEXT_OFFSETS,
            (0x208, 0x268, 0x2C8, 0x328, 0x388, 0x3E8, 0x448),
        )
        self.assertEqual(
            lt.LEAGUE_TABLES_ROW_STAT_RECTS,
            (
                (262, 1, 27, 12),
                (291, 1, 27, 12),
                (320, 1, 27, 12),
                (349, 1, 27, 12),
                (378, 1, 27, 12),
                (407, 1, 27, 12),
                (436, 1, 27, 12),
            ),
        )
        self.assertEqual(
            lt.LEAGUE_TABLES_ROW_COLUMN_SOURCE_OFFSETS,
            {
                "P": (0x10,),
                "W": (0x14,),
                "D": (0x18,),
                "L": (0x1C,),
                "F": (0x20,),
                "A": (0x24,),
                "Pts": (0x14, 0x18),
            },
        )
        self.assertEqual(
            lt.LEAGUE_TABLES_ROW_COLUMN_EXPRESSIONS["Pts"],
            "3*field_0x14 + field_0x18",
        )
        self.assertEqual(lt.LEAGUE_TABLES_ROW_RANK_RECT, (23, 1, 21, 12))
        self.assertEqual(lt.LEAGUE_TABLES_ROW_CLUB_RECT, (46, 1, 214, 12))
        self.assertEqual(lt.LEAGUE_TABLES_ROW_SOURCE_RECORD_OFFSET, 0x70)
        self.assertEqual(lt.LEAGUE_TABLES_ROW_RANK_VALUE_OFFSET, 0xC4)

    def test_exact_fifteen_league_table_resources_are_source_bound(self):
        expected = [
            ("champion_grid", 8512, (477, 14), 0x944F10, 0x944EF0, 0x836A08),
            ("promotion_grid", 7096, (477, 14), 0x944ED0, 0x944EB0, 0x836A3C),
            ("relegation_grid", 7288, (477, 14), 0x944E90, 0x944E70, 0x836A70),
            ("standard_grid", 7304, (477, 14), 0x944E50, 0x944E30, 0x836AA8),
            ("your_team_grid", 8068, (477, 14), 0x944E10, 0x944DF0, 0x836ADC),
            ("playoff_grid", 7068, (477, 14), 0x944DD0, 0x944DB0, 0x836B10),
            ("champion_icon", 688, (20, 12), 0x944D90, 0x944D70, 0x836B44),
            ("promotion_icon", 512, (20, 12), 0x944D50, 0x944D30, 0x836B78),
            ("relegation_icon", 644, (20, 12), 0x944D10, 0x944CF0, 0x836BAC),
            ("playoff_icon", 552, (20, 12), 0x944CD0, 0x944CB0, 0x836BE4),
            ("your_champion_icon", 576, (20, 12), 0x944C90, 0x944C70, 0x836C18),
            ("your_promotion_icon", 488, (20, 12), 0x944C50, 0x944C30, 0x836C50),
            ("your_relegation_icon", 492, (20, 12), 0x944C10, 0x944BF0, 0x836C8C),
            ("your_playoff_icon", 552, (20, 12), 0x944BD0, 0x944BB0, 0x836CC8),
            ("league_bar", 5552, (475, 19), 0x944B90, 0x944B70, 0x836D00),
        ]
        self.assertEqual(len(lt.LEAGUE_TABLES_RESOURCES), 15)
        self.assertEqual(
            [
                (
                    r.name,
                    r.byte_size,
                    r.size,
                    r.raw_handle_va,
                    r.wrapper_va,
                    lt.LEAGUE_TABLES_RESOURCE_PATH_LITERAL_VAS[r.name],
                )
                for r in lt.LEAGUE_TABLES_RESOURCES
            ],
            expected,
        )
        self.assertTrue(
            all(
                r.source_path.startswith("FM2001_Art/Generic/league_tables/")
                for r in lt.LEAGUE_TABLES_RESOURCES
            )
        )
        self.assertEqual(lt.LEAGUE_TABLES_RESOURCE_LOADER_START_VA, 0x5F7870)
        self.assertEqual(lt.LEAGUE_TABLES_RESOURCE_LOADER_END_VA, 0x5F80C0)

    def test_grid_icon_and_bar_wrapper_bindings_preserve_source_roles(self):
        self.assertEqual(
            lt.LEAGUE_TABLES_GRID_WRAPPERS,
            {
                "champion": 0x944EF0,
                "promotion": 0x944EB0,
                "relegation": 0x944E70,
                "standard": 0x944E30,
                "your_team": 0x944DF0,
                "playoff": 0x944DB0,
            },
        )
        self.assertEqual(
            lt.LEAGUE_TABLES_ICON_WRAPPERS,
            {
                "champion": (0x944D70, 0x944C70),
                "promotion": (0x944D30, 0x944C30),
                "relegation": (0x944CF0, 0x944BF0),
                "playoff": (0x944CB0, 0x944BB0),
            },
        )
        self.assertEqual(lt.LEAGUE_TABLES_BAR_CONTROL_OFFSET, 0x788)
        self.assertEqual(lt.LEAGUE_TABLES_BAR_WRAPPER_VA, 0x944B70)
        self.assertEqual(lt.LEAGUE_TABLES_BAR_RECT, (270, 152, 475, 19))



if __name__ == "__main__":
    unittest.main()
