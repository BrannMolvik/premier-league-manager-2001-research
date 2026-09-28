import unittest

from match_schedule import MsvcCrtRng
from scouting import (
    MAX_NUM_FOUND,
    MAX_NUM_USED1,
    MAX_NUM_USED2,
    SCOUT_STRENGTH_MIN_DEFAULT,
    SCOUTING_STRENGTH_LABELS,
    SCOUT_ONE_AGE_BIAS,
    ScoutingReseedState,
    ScoutingSortValues,
    ScoutingRankValues,
    ScoutingFilterControls,
    ScoutingFilterValues,
    scouting_country_context_passes,
    scouting_loan_list_user_match,
    scouting_preferred_position_passes,
    scouting_strength_threshold_passes,
    scouting_rank_score,
    scouting_first_stage_passes,
    scouting_result_compare,
    sort_scouting_results,
    run_scouting_search,
    primary_scouting_results,
    scouting_shuffle,
    secondary_scouting_results,
)


class ScoutingOrderingTests(unittest.TestCase):
    def test_scouting_tuning_defaults_match_executable(self):
        self.assertEqual(SCOUT_ONE_AGE_BIAS, 4)
        self.assertEqual(MAX_NUM_USED1, 80)
        self.assertEqual(MAX_NUM_USED2, 50)
        self.assertEqual(MAX_NUM_FOUND, 20)
        self.assertEqual(SCOUT_STRENGTH_MIN_DEFAULT, 20)
        self.assertEqual(len(SCOUTING_STRENGTH_LABELS), 17)

    def test_exact_scouting_seed_xors_neutral_panel_fields(self):
        state = ScoutingReseedState(
            status_control_7738=1,
            status_control_76f8=2,
            status_control_76b8=3,
            value_high_64d0=123.9,
            value_low_64c8=-45.9,
            field_64e4=0x11223344,
            age_high_64dc=35,
            field_64e0=2,
            age_low_64d8=18,
            class_selector_64c0=3,
        )
        expected = 0
        for value in (1, 2, 3, 123, -45, 0x11223344, 35, 2, 18, 3, -1):
            expected ^= value & 0xFFFFFFFF
        self.assertEqual(state.exact_seed(-1), expected & 0xFFFFFFFF)

    def test_primary_scouting_shuffle_reseeds_instead_of_using_incoming_game_state(self):
        state = ScoutingReseedState(
            status_control_7738=1,
            value_high_64d0=1000.0,
            value_low_64c8=10.0,
            age_high_64dc=35,
            age_low_64d8=18,
            class_selector_64c0=2,
        )
        candidates = tuple(range(12))

        first = primary_scouting_results(candidates, state)
        second = primary_scouting_results(candidates, state)

        self.assertEqual(first, second)

        rng = MsvcCrtRng(state.exact_seed(-1))
        expected = list(candidates)
        for remaining in range(len(expected), 1, -1):
            selected = rng.randbelow(remaining)
            expected[selected], expected[remaining - 1] = (
                expected[remaining - 1],
                expected[selected],
            )
        self.assertEqual(first, tuple(expected))

    def test_country_context_selector_modes_match_executable(self):
        self.assertTrue(
            scouting_country_context_passes(
                0,
                candidate_country_id=26,
                candidate_european_index=1,
                active_club_country_id=26,
            )
        )
        self.assertFalse(
            scouting_country_context_passes(
                0,
                candidate_country_id=33,
                candidate_european_index=1,
                active_club_country_id=26,
            )
        )
        self.assertTrue(
            scouting_country_context_passes(
                1,
                candidate_country_id=33,
                candidate_european_index=1,
                active_club_country_id=26,
            )
        )
        self.assertFalse(
            scouting_country_context_passes(
                1,
                candidate_country_id=40,
                candidate_european_index=0,
                active_club_country_id=26,
            )
        )
        self.assertTrue(
            scouting_country_context_passes(
                2,
                candidate_country_id=40,
                candidate_european_index=0,
                active_club_country_id=26,
            )
        )
        self.assertFalse(
            scouting_country_context_passes(
                -1,
                candidate_country_id=33,
                candidate_european_index=1,
                active_club_country_id=26,
            )
        )

    def test_optional_preferred_position_gate_scans_three_ids(self):
        positions = (3, 7, 11)
        self.assertTrue(scouting_preferred_position_passes(positions, None))
        self.assertTrue(scouting_preferred_position_passes(positions, 7))
        self.assertFalse(scouting_preferred_position_passes(positions, 9))

    def test_scouting_loan_list_user_match_matches_bit12_callsite_reduction(self):
        self.assertFalse(
            scouting_loan_list_user_match(
                transfer_listed=True,
                non_eu=True,
                registered_club_competition_id=4,
                active_club_competition_id=4,
            )
        )
        self.assertTrue(
            scouting_loan_list_user_match(
                transfer_listed=True,
                non_eu=True,
                registered_club_competition_id=4,
                active_club_competition_id=7,
            )
        )
        self.assertFalse(
            scouting_loan_list_user_match(
                transfer_listed=False,
                non_eu=True,
                registered_club_competition_id=4,
                active_club_competition_id=7,
            )
        )
        self.assertTrue(
            scouting_loan_list_user_match(
                transfer_listed=False,
                non_eu=False,
                registered_club_competition_id=4,
                active_club_competition_id=7,
            )
        )

    def test_plain_scouting_rank_uses_best_preferred_role_rating(self):
        skills = [128] * 17
        preferred = (1, 2, 3)
        plain = scouting_rank_score(skills, preferred, age=25, mode=16)
        from match_role_rating import best_preferred_role_rating
        self.assertEqual(
            plain,
            best_preferred_role_rating(skills, preferred),
        )

    def test_age_biased_scouting_rank_uses_exact_integer_factor(self):
        skills = [160] * 17
        preferred = (9, 10, 11)
        from match_role_rating import best_preferred_role_rating
        base = best_preferred_role_rating(skills, preferred)

        self.assertEqual(
            scouting_rank_score(skills, preferred, age=31, mode=5),
            base * 60 // 100,
        )
        self.assertEqual(
            scouting_rank_score(skills, preferred, age=36, mode=5),
            base * 80 // 100,
        )

    def test_skill_biased_scouting_rank_wraps_temporary_bytes_like_executable(self):
        skills = [250] * 17
        preferred = (9, 10, 11)
        transformed = list(skills)
        for slot, percent in ((1, 120), (2, 130), (3, 120), (9, 120)):
            transformed[slot] = (transformed[slot] * percent // 100) & 0xFF

        from match_role_rating import best_preferred_role_rating
        self.assertEqual(
            scouting_rank_score(skills, preferred, age=25, mode=15),
            best_preferred_role_rating(transformed, preferred),
        )
        self.assertEqual(skills, [250] * 17)

    def test_unhandled_scouting_mode_does_not_append_score(self):
        self.assertIsNone(
            scouting_rank_score([128] * 17, (1, 2, 3), age=25, mode=7)
        )


    def test_scouting_sort_modes_match_exact_direction_and_name_ties(self):
        rows = (
            ("a", ScoutingSortValues("Smith", "Alan", 30, 7.5, "ST", "Arsenal", 200.0)),
            ("b", ScoutingSortValues("Brown", "Ben", 20, 6.0, "GK", "Chelsea", 500.0)),
            ("c", ScoutingSortValues("Smith", "Aaron", 30, 9.0, "DC", "Arsenal", 300.0)),
        )
        lookup = dict(rows)

        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 0, lookup.__getitem__),
            ("b", "c", "a"),
        )
        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 1, lookup.__getitem__),
            ("b", "c", "a"),
        )
        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 2, lookup.__getitem__),
            ("c", "a", "b"),
        )
        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 3, lookup.__getitem__),
            ("a", "b", "c"),
        )
        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 4, lookup.__getitem__),
            ("c", "a", "b"),
        )
        self.assertEqual(
            sort_scouting_results(("a", "b", "c"), 5, lookup.__getitem__),
            ("b", "c", "a"),
        )

    def test_scouting_sort_compare_rejects_unknown_mode(self):
        values = ScoutingSortValues("A", "B", 20, 1.0, "GK", "Club", 1.0)
        with self.assertRaises(ValueError):
            scouting_result_compare(values, values, 6)


    def test_composed_scouting_search_preserves_primary_secondary_then_final_sort(self):
        state = ScoutingReseedState(field_64e4=7, age_low_64d8=18)
        items = tuple(range(12))

        def sort_values(item):
            return ScoutingSortValues(
                name_primary=f"S{item:02d}",
                name_secondary=f"F{item:02d}",
                age=20 + item,
                history_average=float(item),
                position_label=f"P{item:02d}",
                club_name=f"C{item:02d}",
                valuation=float(item * 100),
            )

        def rank_values(item):
            return ScoutingRankValues(
                current_raw=(128 + item,) * 17,
                preferred_positions=(9, 10, 11),
                age=20 + item,
            )

        result = run_scouting_search(
            items,
            state,
            candidate_predicate=lambda item: item % 2 == 0,
            sort_mode=0,
            sort_values=sort_values,
            secondary_score_mode=16,
            secondary_caller_argument=3,
            rank_values=rank_values,
        )

        primary = primary_scouting_results(
            tuple(item for item in items if item % 2 == 0),
            state,
        )
        scored = sorted(
            primary,
            key=lambda item: (
                -scouting_rank_score(
                    (128 + item,) * 17,
                    (9, 10, 11),
                    age=20 + item,
                    mode=16,
                ),
                f"S{item:02d}",
                f"F{item:02d}",
            ),
        )
        secondary = secondary_scouting_results(
            scored,
            state,
            caller_argument=3,
        )
        expected = tuple(sorted(secondary, key=lambda item: (f"S{item:02d}", f"F{item:02d}")))
        self.assertEqual(result, expected)

    def test_composed_secondary_search_requires_rank_values(self):
        state = ScoutingReseedState()
        values = lambda item: ScoutingSortValues(
            str(item), "", 0, 0.0, "", "", 0.0
        )
        with self.assertRaisesRegex(ValueError, "rank_values"):
            run_scouting_search(
                (1, 2),
                state,
                candidate_predicate=lambda _item: True,
                sort_mode=0,
                sort_values=values,
                secondary_score_mode=16,
            )


    def test_first_stage_numeric_age_value_and_class_gates_are_inclusive(self):
        panel = ScoutingReseedState(
            age_low_64d8=18,
            age_high_64dc=30,
            value_low_64c8=100.0,
            value_high_64d0=500.0,
            class_selector_64c0=2,
        )
        base = ScoutingFilterValues(
            age=18,
            valuation=100.0,
            player_class=1,
        )
        self.assertTrue(
            scouting_first_stage_passes(panel, base, page_mode=16)
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=30, valuation=500.0, player_class=1),
                page_mode=16,
            )
        )
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=17, valuation=100.0, player_class=1),
                page_mode=16,
            )
        )
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=18, valuation=500.01, player_class=1),
                page_mode=16,
            )
        )

    def test_first_stage_special_mode_15_adds_literal_age_15_to_18_clamp(self):
        panel = ScoutingReseedState(
            age_low_64d8=10,
            age_high_64dc=40,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=0,
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=15, valuation=0.0, player_class=3),
                page_mode=15,
            )
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=18, valuation=1000.0, player_class=3),
                page_mode=15,
            )
        )
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=14, valuation=100.0, player_class=3),
                page_mode=15,
            )
        )
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=19, valuation=100.0, player_class=3),
                page_mode=15,
            )
        )

    def test_first_stage_class_selector_mapping_is_3_0_1_2(self):
        for selector, expected_class in enumerate((3, 0, 1, 2)):
            panel = ScoutingReseedState(
                age_low_64d8=0,
                age_high_64dc=99,
                value_low_64c8=0.0,
                value_high_64d0=1000.0,
                class_selector_64c0=selector,
            )
            self.assertTrue(
                scouting_first_stage_passes(
                    panel,
                    ScoutingFilterValues(
                        age=25,
                        valuation=100.0,
                        player_class=expected_class,
                    ),
                    page_mode=16,
                )
            )

    def test_first_stage_out_of_range_class_selector_bypasses_class_gate(self):
        for selector in (-1, 4, 99):
            panel = ScoutingReseedState(
                age_low_64d8=0,
                age_high_64dc=99,
                value_low_64c8=0.0,
                value_high_64d0=1000.0,
                class_selector_64c0=selector,
            )
            self.assertTrue(
                scouting_first_stage_passes(
                    panel,
                    ScoutingFilterValues(
                        age=25,
                        valuation=100.0,
                        player_class=2,
                    ),
                    page_mode=16,
                )
            )

    def test_first_stage_status_controls_or_together_and_loan_requires_extra_gate(self):
        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
        )
        neutral = ScoutingFilterValues(age=25, valuation=100.0, player_class=0)
        self.assertTrue(scouting_first_stage_passes(panel, neutral, page_mode=16))

        transfer_control = ScoutingFilterControls(transfer_listed=True)
        self.assertFalse(
            scouting_first_stage_passes(
                panel, neutral, page_mode=16, status_controls=transfer_control
            )
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(
                    age=25,
                    valuation=100.0,
                    player_class=0,
                    transfer_listed=True,
                ),
                page_mode=16,
                status_controls=transfer_control,
            )
        )

        loan_control = ScoutingFilterControls(loan_listed=True)
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(
                    age=25,
                    valuation=100.0,
                    player_class=0,
                    loan_listed=True,
                    loan_list_user_match=False,
                ),
                page_mode=16,
                status_controls=loan_control,
            )
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(
                    age=25,
                    valuation=100.0,
                    player_class=0,
                    loan_listed=True,
                    loan_list_user_match=True,
                ),
                page_mode=16,
                status_controls=loan_control,
            )
        )

    def test_strengths_selector_indexes_current_skills_and_uses_shipped_minimum(self):
        raw = [0] * 17
        # raw 170 converts exactly to displayed 20: (30*170 + 128)//255 = 20.
        raw[0] = 170
        raw[16] = 169

        self.assertTrue(
            scouting_strength_threshold_passes(raw, 0, SCOUT_STRENGTH_MIN_DEFAULT)
        )
        self.assertTrue(
            scouting_strength_threshold_passes(raw, 1, SCOUT_STRENGTH_MIN_DEFAULT)
        )
        self.assertFalse(
            scouting_strength_threshold_passes(raw, 17, SCOUT_STRENGTH_MIN_DEFAULT)
        )
        raw[16] = 170
        self.assertTrue(
            scouting_strength_threshold_passes(raw, 17, SCOUT_STRENGTH_MIN_DEFAULT)
        )

        with self.assertRaisesRegex(ValueError, "0 \\(All\\) or 1..17"):
            scouting_strength_threshold_passes(raw, 18)

    def test_out_of_contract_status_control_uses_exact_bit7_semantic_branch(self):
        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
        )
        control = ScoutingFilterControls(out_of_contract=True)
        self.assertFalse(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(age=25, valuation=100.0, player_class=0),
                page_mode=16,
                status_controls=control,
            )
        )
        self.assertTrue(
            scouting_first_stage_passes(
                panel,
                ScoutingFilterValues(
                    age=25,
                    valuation=100.0,
                    player_class=0,
                    out_of_contract=True,
                ),
                page_mode=16,
                status_controls=control,
            )
        )

    def test_first_stage_neutral_gates_fail_independently(self):
        panel = ScoutingReseedState(
            age_low_64d8=0,
            age_high_64dc=99,
            value_low_64c8=0.0,
            value_high_64d0=1000.0,
            class_selector_64c0=1,
        )
        for field in (
            "team_selector_passes",
            "optional_position_passes",
            "threshold_passes",
        ):
            kwargs = dict(
                age=25,
                valuation=100.0,
                player_class=0,
                team_selector_passes=True,
                optional_position_passes=True,
                threshold_passes=True,
            )
            kwargs[field] = False
            self.assertFalse(
                scouting_first_stage_passes(
                    panel,
                    ScoutingFilterValues(**kwargs),
                    page_mode=16,
                )
            )

    def test_secondary_scouting_applies_used_and_found_caps_around_shuffle(self):
        state = ScoutingReseedState(field_64e4=9, age_low_64d8=16)
        ranked = tuple(range(100))

        result = secondary_scouting_results(
            ranked,
            state,
            caller_argument=7,
        )

        self.assertEqual(len(result), 20)
        self.assertTrue(set(result).issubset(set(range(50))))
        self.assertEqual(
            result,
            scouting_shuffle(range(50), state, caller_argument=7)[:20],
        )


if __name__ == "__main__":
    unittest.main()
