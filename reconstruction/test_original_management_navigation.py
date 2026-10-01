"""Regression tests for recovered Calendar/Tables PMenu identities."""
import unittest

from original_management_navigation import (
    CALENDAR_PANEL,
    CALENDAR_TABLES_PANEL_IDENTITIES,
    CUP_TABLES_PANEL,
    LEAGUE_FIXTURES_PANEL,
    LEAGUE_TABLES_PANEL,
    MANAGEMENT_PANEL_FACTORY_VA,
    OriginalManagementNavigationError,
    calendar_tables_panel_identity,
)


class OriginalManagementNavigationTests(unittest.TestCase):
    def test_exact_calendar_tables_menu_order_and_classes(self):
        self.assertEqual(MANAGEMENT_PANEL_FACTORY_VA, 0x47AEC0)
        self.assertEqual(
            [panel.menu_id for panel in CALENDAR_TABLES_PANEL_IDENTITIES],
            [0x259, 0x25A, 0x25B, 0x25C],
        )
        self.assertEqual(
            [panel.original_caption for panel in CALENDAR_TABLES_PANEL_IDENTITIES],
            ["Calendar", "League Tables", "Cup Tables", "League Fixtures"],
        )
        self.assertEqual(
            [panel.panel_class for panel in CALENDAR_TABLES_PANEL_IDENTITIES],
            ["PCalendar2k", "PLeagueTables", "PCupTable2000", "PLeagueFixtures"],
        )

    def test_calendar_factory_and_rtti_identity_are_exact(self):
        self.assertEqual(CALENDAR_PANEL.factory_case_va, 0x47C62B)
        self.assertEqual(CALENDAR_PANEL.constructor_va, 0x47CCB0)
        self.assertEqual(CALENDAR_PANEL.type_descriptor_va, 0x81CA18)
        self.assertEqual(CALENDAR_PANEL.vftable_va, 0x7C2F04)

    def test_league_and_cup_table_factory_targets_are_not_swapped(self):
        self.assertEqual(LEAGUE_TABLES_PANEL.factory_case_va, 0x47C6D1)
        self.assertEqual(LEAGUE_TABLES_PANEL.constructor_va, 0x448640)
        self.assertEqual(LEAGUE_TABLES_PANEL.vftable_va, 0x7C00C8)

        self.assertEqual(CUP_TABLES_PANEL.factory_case_va, 0x47C67E)
        self.assertEqual(CUP_TABLES_PANEL.constructor_va, 0x44EC80)
        self.assertEqual(CUP_TABLES_PANEL.vftable_va, 0x7C0A78)

    def test_league_fixtures_closes_concrete_panel_identity(self):
        self.assertEqual(LEAGUE_FIXTURES_PANEL.menu_id, 0x25C)
        self.assertEqual(LEAGUE_FIXTURES_PANEL.factory_case_va, 0x47C724)
        self.assertEqual(LEAGUE_FIXTURES_PANEL.constructor_va, 0x46D470)
        self.assertEqual(LEAGUE_FIXTURES_PANEL.type_descriptor_va, 0x81C550)
        self.assertEqual(LEAGUE_FIXTURES_PANEL.vftable_va, 0x7C24B8)

    def test_lookup_fails_closed_outside_recovered_family(self):
        for panel in CALENDAR_TABLES_PANEL_IDENTITIES:
            self.assertIs(calendar_tables_panel_identity(panel.menu_id), panel)
        for bad in (True, "0x259", 0x258, 0x25D):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalManagementNavigationError):
                    calendar_tables_panel_identity(bad)


if __name__ == "__main__":
    unittest.main()
