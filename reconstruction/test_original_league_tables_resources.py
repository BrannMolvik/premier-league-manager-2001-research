"""Regressions for source-backed PLeagueTables selector/header shell."""
import unittest

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

    def test_two_unresolved_selector_families_stay_structurally_bounded_and_neutral(self):
        self.assertEqual(LEAGUE_TABLES_SECONDARY_SELECTOR_BASE_OFFSET, 0x4E4)
        self.assertEqual(LEAGUE_TABLES_SECONDARY_SELECTOR_COUNT, 5)
        self.assertEqual(
            LEAGUE_TABLES_SECONDARY_SETUP_CALLS,
            (0x447306, 0x447353, 0x4473A1, 0x4473F2, 0x447440),
        )
        self.assertEqual(LEAGUE_TABLES_TERTIARY_SELECTOR_BASE_OFFSET, 0x6A8)
        self.assertEqual(LEAGUE_TABLES_TERTIARY_SELECTOR_COUNT, 2)
        self.assertEqual(LEAGUE_TABLES_TERTIARY_SETUP_CALLS, (0x4474B5, 0x447501))

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


if __name__ == "__main__":
    unittest.main()
