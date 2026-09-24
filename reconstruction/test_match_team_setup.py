import unittest
from dataclasses import dataclass

from match_team_setup import (
    DEFAULT_SUBSTITUTE_QUOTA,
    ManagerFormationPreferences,
    manager_formation_for_selection_class,
    resolved_substitute_quota,
)


@dataclass(frozen=True)
class Manager:
    formation_default: int = 4
    formation_class3: int = 9
    formation_class1: int = 14


class ManagerFormationTests(unittest.TestCase):
    def test_exact_409b50_class_mapping(self):
        manager = Manager()

        self.assertEqual(manager_formation_for_selection_class(manager, 0), 4)
        self.assertEqual(manager_formation_for_selection_class(manager, 1), 14)
        self.assertEqual(manager_formation_for_selection_class(manager, 2), 4)
        self.assertEqual(manager_formation_for_selection_class(manager, 3), 9)

    def test_ff_alternate_is_not_silently_replaced(self):
        prefs = ManagerFormationPreferences(4, 0xFF, 14)
        with self.assertRaises(ValueError):
            manager_formation_for_selection_class(prefs, 3)

    def test_invalid_class_is_rejected(self):
        with self.assertRaises(ValueError):
            manager_formation_for_selection_class(Manager(), 4)


class SubstituteQuotaTests(unittest.TestCase):
    def test_missing_match_context_uses_exact_fallback_five(self):
        self.assertEqual(resolved_substitute_quota(None), DEFAULT_SUBSTITUTE_QUOTA)
        self.assertEqual(DEFAULT_SUBSTITUTE_QUOTA, 5)

    def test_resolved_context_value_is_used_verbatim(self):
        self.assertEqual(resolved_substitute_quota(3), 3)
        self.assertEqual(resolved_substitute_quota(7), 7)


if __name__ == "__main__":
    unittest.main()
