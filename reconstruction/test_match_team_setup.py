import unittest
from dataclasses import dataclass

from match_team_setup import (
    DEFAULT_SUBSTITUTE_QUOTA,
    ManagerFormationPreferences,
    ManagerTacticalSources,
    TeamTacticalState,
    manager_formation_for_selection_class,
    manager_tactics_packet_fields,
    play_style_to_strategy_code,
    resolved_substitute_quota,
    team_tactics_packet_fields,
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


class TacticsPacketTests(unittest.TestCase):
    def test_exact_play_style_strategy_mapping(self):
        self.assertEqual(play_style_to_strategy_code(0), 3)
        self.assertEqual(play_style_to_strategy_code(1), 2)
        self.assertEqual(play_style_to_strategy_code(2), 1)
        self.assertEqual(play_style_to_strategy_code(3), 2)
        self.assertEqual(play_style_to_strategy_code(255), 2)

    def test_exact_team_tactical_defaults(self):
        state = TeamTacticalState()
        self.assertEqual(state.play_style, 1)
        self.assertEqual(state.without_ball_style, 0)
        self.assertEqual(state.with_ball_style, 0)
        self.assertEqual(state.aggression, 5)

        packet = team_tactics_packet_fields(state)
        self.assertEqual(packet.strategy_code, 2)
        self.assertEqual(packet.aggression_code, 5)
        self.assertEqual(packet.with_ball_code, 0)
        self.assertEqual(packet.without_ball_code, 0)

    def test_manager_packet_uses_exact_40d860_transforms(self):
        # Canonical database values for Alex Ferguson.
        packet = manager_tactics_packet_fields(
            ManagerTacticalSources(3, 80, 2, 3)
        )
        self.assertEqual(packet.strategy_code, 2)
        self.assertEqual(packet.aggression_code, 13)
        self.assertEqual(packet.with_ball_code, 2)
        self.assertEqual(packet.without_ball_code, 3)

    def test_manager_style_sources_are_masked_not_rebased(self):
        # Canonical database values for Arsene Wenger include source value 4.
        packet = manager_tactics_packet_fields(
            ManagerTacticalSources(2, 90, 4, 3)
        )
        self.assertEqual(packet.strategy_code, 1)
        self.assertEqual(packet.aggression_code, 15)
        self.assertEqual(packet.with_ball_code, 0)
        self.assertEqual(packet.without_ball_code, 3)

    def test_invalid_live_team_state_is_rejected(self):
        with self.assertRaises(ValueError):
            TeamTacticalState(play_style=3)
        with self.assertRaises(ValueError):
            TeamTacticalState(aggression=10)


if __name__ == "__main__":
    unittest.main()
