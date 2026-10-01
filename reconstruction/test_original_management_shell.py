"""Regressions for the executable-recovered PMenu management-shell route."""
import unittest

from original_management_shell import (
    FRESH_USER_ROUTE_STATE,
    LEAGUE_TABLE_PANEL_CODE,
    LEAGUE_TABLE_PANEL_VFTABLE_VA,
    OriginalManagementShellError,
    SQUAD_PANEL_CODE,
    SQUAD_PANEL_VFTABLE_VA,
    fresh_new_game_management_route,
    management_route_for_user_state,
)


class OriginalManagementShellTests(unittest.TestCase):
    def test_fresh_user_routes_to_squad_not_an_invented_manager_home(self):
        route = fresh_new_game_management_route()
        self.assertEqual(route.user_route_state, FRESH_USER_ROUTE_STATE)
        self.assertEqual(route.panel_code, SQUAD_PANEL_CODE)
        self.assertEqual(route.panel_class, "PSquadScreen")
        self.assertEqual(route.vftable_va, SQUAD_PANEL_VFTABLE_VA)
        self.assertEqual(route.menu_node_id, 2)
        self.assertFalse(route.resets_user_route_state_to_zero)

    def test_state_one_routes_once_to_native_league_table_panel(self):
        route = management_route_for_user_state(1)
        self.assertEqual(route.panel_code, LEAGUE_TABLE_PANEL_CODE)
        self.assertEqual(route.panel_class, "PLeagueTables")
        self.assertEqual(route.vftable_va, LEAGUE_TABLE_PANEL_VFTABLE_VA)
        self.assertEqual(route.menu_node_id, 6)
        self.assertTrue(route.resets_user_route_state_to_zero)

    def test_other_nonzero_state_uses_squad_and_is_cleared(self):
        route = management_route_for_user_state(7)
        self.assertEqual(route.panel_code, SQUAD_PANEL_CODE)
        self.assertEqual(route.panel_class, "PSquadScreen")
        self.assertTrue(route.resets_user_route_state_to_zero)

    def test_route_state_is_strict_integer(self):
        for bad in (True, None, "0", 0.0):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalManagementShellError):
                    management_route_for_user_state(bad)


if __name__ == "__main__":
    unittest.main()
