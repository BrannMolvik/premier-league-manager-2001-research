import unittest
from dataclasses import dataclass

from match_team_setup import (
    DEFAULT_SUBSTITUTE_QUOTA,
    FormationSelectionClass,
    LeagueObjectiveGaps,
    ManagerFormationPreferences,
    ManagerTacticalSources,
    TeamTacticalState,
    aggregate_deficit_pressure,
    cup_round_strategy_bias,
    formation_selection_class_from_score,
    game_strategy_score,
    late_season_league_strategy_bias,
    league_objective_gaps_from_sorted_points,
    league_objective_pressure,
    manager_formation_for_game_strategy,
    manager_formation_for_selection_class,
    manager_tactics_packet_fields,
    play_style_to_strategy_code,
    premier_league_strategy_bias,
    rating_difference_pressure,
    resolved_substitute_quota,
    strategy_team_rating,
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


class FormationStrategyClassifierTests(unittest.TestCase):
    def test_exact_default_threshold_buckets(self):
        self.assertEqual(
            formation_selection_class_from_score(-4),
            FormationSelectionClass.DEFENSIVE,
        )
        self.assertEqual(
            formation_selection_class_from_score(-3),
            FormationSelectionClass.DEFENSIVE,
        )
        for score in (-2, -1, 0, 1, 2):
            self.assertEqual(
                formation_selection_class_from_score(score),
                FormationSelectionClass.NORMAL,
            )
        self.assertEqual(
            formation_selection_class_from_score(3),
            FormationSelectionClass.ATTACKING,
        )
        self.assertEqual(
            formation_selection_class_from_score(8),
            FormationSelectionClass.ATTACKING,
        )

    def test_manager_class_mapping_now_has_exact_semantics(self):
        manager = Manager()
        self.assertEqual(
            manager_formation_for_selection_class(
                manager,
                FormationSelectionClass.ATTACKING,
            ),
            14,
        )
        self.assertEqual(
            manager_formation_for_selection_class(
                manager,
                FormationSelectionClass.NORMAL,
            ),
            4,
        )
        self.assertEqual(
            manager_formation_for_selection_class(
                manager,
                FormationSelectionClass.DEFENSIVE,
            ),
            9,
        )

    def test_relative_rating_pressure_thresholds_and_sign(self):
        # Use a small test divisor so the original 5/10/20/50/100 thresholds
        # can be exercised without enormous synthetic squad totals.
        self.assertEqual(rating_difference_pressure(104, 100, divisor=1), 0)
        self.assertEqual(rating_difference_pressure(105, 100, divisor=1), -1)
        self.assertEqual(rating_difference_pressure(110, 100, divisor=1), -2)
        self.assertEqual(rating_difference_pressure(120, 100, divisor=1), -3)
        self.assertEqual(rating_difference_pressure(150, 100, divisor=1), -4)
        self.assertEqual(rating_difference_pressure(200, 100, divisor=1), -5)
        self.assertEqual(rating_difference_pressure(95, 100, divisor=1), 1)
        self.assertEqual(rating_difference_pressure(90, 100, divisor=1), 2)

    def test_aggregate_deficit_pressure_is_exact_step_function(self):
        expected = {
            -1: 0,
            0: 0,
            1: 2,
            2: 5,
            3: 6,
            4: 7,
            8: 7,
        }
        for deficit, pressure in expected.items():
            self.assertEqual(aggregate_deficit_pressure(deficit), pressure)

    def test_exact_cup_round_bias_defaults(self):
        # precedence 0 still contributes floor((0+12)/3) == 4.
        self.assertEqual(cup_round_strategy_bias(1, 0), 7)
        self.assertEqual(cup_round_strategy_bias(2, 0), 6)
        self.assertEqual(cup_round_strategy_bias(3, 0), 5)
        self.assertEqual(cup_round_strategy_bias(4, 0), 4)

    def test_exact_league_cut_line_gap_mapping_for_top_division(self):
        points = [80, 72, 68, 60, 45, 41, 38, 35, 30, 25]
        gaps = league_objective_gaps_from_sorted_points(
            points,
            current_rank=7,
            automatic_promotion_places=0,
            playoff_places=0,
            relegation_places=3,
        )
        self.assertEqual(gaps.win_league, 45)
        self.assertIsNone(gaps.promotion)
        self.assertIsNone(gaps.promotion_playoff)
        self.assertEqual(gaps.avoid_relegation, 3)
        self.assertIsNone(gaps.avoid_relegation_playoff)

    def test_exact_league_cut_line_gap_mapping_with_promotion_and_playoffs(self):
        points = [80, 74, 70, 66, 64, 60, 55, 50, 45, 40]
        gaps = league_objective_gaps_from_sorted_points(
            points,
            current_rank=6,
            automatic_promotion_places=2,
            playoff_places=4,
            relegation_places=2,
        )
        self.assertIsNone(gaps.win_league)
        self.assertEqual(gaps.promotion, 19)
        self.assertEqual(gaps.promotion_playoff, 5)
        self.assertEqual(gaps.avoid_relegation, -5)
        self.assertEqual(gaps.avoid_relegation_playoff, 19)

    def test_late_season_strategy_uses_first_reachable_objective(self):
        gaps = LeagueObjectiveGaps(
            win_league=20,        # 20 / 4 >= 3, unreachable -> continue.
            avoid_relegation=2,   # 2 / 4 reachable -> +1 base.
        )
        self.assertEqual(
            late_season_league_strategy_bias(gaps, 4),
            1,
        )

    def test_premier_league_style_bottom_team_gets_relegation_pressure(self):
        points = [80, 70, 65, 60, 55, 50, 45, 40, 38, 30, 28, 27, 26, 25, 24, 23, 22, 20, 18, 16]
        gaps = league_objective_gaps_from_sorted_points(
            points,
            current_rank=18,
            relegation_places=3,
        )
        # Title gap is mathematically impossible in four matches, so the
        # original ordered scan continues to the relegation cut line.
        self.assertEqual(
            late_season_league_strategy_bias(gaps, 4),
            2,
        )

    def test_game_strategy_score_composes_home_rating_deficit_and_context(self):
        # Home +1, equal rating 0, one behind +2, context +1 => +4 -> attack.
        score = game_strategy_score(
            is_home=True,
            current_rating=500,
            opponent_rating=500,
            aggregate_goals_behind=1,
            competition_context_bias=1,
        )
        self.assertEqual(score, 4)
        self.assertEqual(
            formation_selection_class_from_score(score),
            FormationSelectionClass.ATTACKING,
        )

    def test_strategy_team_rating_uses_only_first_eleven_roster_entries(self):
        @dataclass(frozen=True)
        class RatedPlayer:
            skills: tuple[int, ...]
            preferred_positions: tuple[int, int, int]

        players = [
            RatedPlayer((100,) * 17, (12, 0, 0))
            for _ in range(11)
        ]
        extra = RatedPlayer((255,) * 17, (19, 0, 0))
        expected_one = strategy_team_rating(players[:1])
        self.assertEqual(
            strategy_team_rating(players + [extra]),
            expected_one * 11,
        )

    def test_premier_league_bias_uses_title_then_relegation_cut(self):
        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        rows = [
            Row(1, 34, 80),
            Row(2, 34, 70),
            Row(3, 34, 60),
            Row(4, 34, 50),
            Row(5, 34, 40),
            Row(6, 34, 30),
            Row(7, 34, 24),
            Row(8, 34, 22),
            Row(9, 34, 20),
            Row(10, 34, 18),
        ]

        # Club 9 cannot reach the title in four matches, but is two points
        # below the safe cut at rank count-3-1, so relegation pressure applies.
        self.assertEqual(
            premier_league_strategy_bias(rows, 9, total_matches=38),
            2,
        )

    def test_premier_league_bias_is_zero_before_final_eight_matches(self):
        @dataclass(frozen=True)
        class Row:
            club_id: int
            played: int
            points: int

        rows = [
            Row(1, 20, 50),
            Row(2, 20, 45),
            Row(3, 20, 40),
            Row(4, 20, 35),
            Row(5, 20, 30),
            Row(6, 20, 25),
            Row(7, 20, 20),
            Row(8, 20, 15),
            Row(9, 20, 10),
            Row(10, 20, 5),
        ]
        self.assertEqual(
            premier_league_strategy_bias(rows, 9, total_matches=38),
            0,
        )

    def test_game_strategy_can_choose_manager_formation_directly(self):
        manager = Manager()
        self.assertEqual(
            manager_formation_for_game_strategy(
                manager,
                is_home=True,
                current_rating=500,
                opponent_rating=500,
                aggregate_goals_behind=1,
            ),
            14,
        )

    def test_late_season_objective_pressure_window_and_halving(self):
        # Outside the final eight matches there is no league-position pressure.
        self.assertEqual(league_objective_pressure(4, 9, 2), 0)

        # 4 points / 8 matches = 0.5 -> int(0.999)=0, +2 base, then half.
        self.assertEqual(league_objective_pressure(4, 8, 2), 1)

        # In the final four matches the same objective uses full pressure.
        self.assertEqual(league_objective_pressure(2, 4, 2), 2)

        # Three points per match is rejected by the executable's < 3.0 gate.
        self.assertEqual(league_objective_pressure(12, 4, 2), 0)


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
