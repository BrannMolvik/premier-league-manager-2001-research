import unittest

from gate14_fastview_team import (
    BLANK_BAR,
    FASTVIEW_TEAM_SETUP_VA,
    FASTVIEW_TEAM_VFTABLE,
    SIDE_0_CONTRACT,
    SIDE_1_CONTRACT,
    TEAM_BAR_1,
    TEAM_BAR_2,
    TEAM_NAME_GRID_1,
    TEAM_NAME_GRID_2,
    TEAM_NAME_GRID_3,
    TEAM_NAME_GRID_4,
    TEAM_ROW_CONSTRUCTOR_VA,
    TEAM_ROW_PRIMARY_NAME_COUNT,
    TEAM_ROW_PRIMARY_VFTABLE,
    TEAM_ROW_STEP,
    TEAM_ROW_TEXT_RAW_FLAGS,
    PLAYER_ROW_ENERGY_RECEIVER_BASE_VFTABLE,
    PLAYER_ROW_ENERGY_RECEIVER_VFTABLE,
    PLAYER_ROW_ENERGY_RECEIVER_OFFSET,
    PLAYER_ROW_ENERGY_CALLBACK_VA,
    PLAYER_ROW_ENERGY_UPDATE_VA,
    PLAYER_ROW_ENERGY_EVENT_VALUE_OFFSET,
    PLAYER_ROW_ENERGY_MIN,
    PLAYER_ROW_ENERGY_MAX,
    PLAYER_ROW_ENERGY_SPAN,
    PLAYER_ROW_ENERGY_SPAN_GLOBAL_VA,
    PLAYER_ROW_ENERGY_SPAN_INIT_VA,
    PLAYER_ROW_ENERGY_BAR_WIDTH,
    PLAYER_ROW_FLOAT_TO_INT_VA,
    TEAM_TABLE_CONSTRUCTOR_VA,
    TEAM_TABLE_VFTABLE,
    FastViewTeamError,
    side_contract,
    team_row_energy_bar_state,
    team_row_name_resource,
    team_row_origin,
    team_row_rects,
)


class FastViewTeamTests(unittest.TestCase):
    def test_source_owners_and_side_asset_pairings_are_exact(self):
        self.assertEqual(FASTVIEW_TEAM_SETUP_VA, 0x524A20)
        self.assertEqual(FASTVIEW_TEAM_VFTABLE, 0x7CA888)
        self.assertEqual(TEAM_TABLE_CONSTRUCTOR_VA, 0x524EC0)
        self.assertEqual(TEAM_TABLE_VFTABLE, 0x7CA950)
        self.assertEqual(TEAM_ROW_CONSTRUCTOR_VA, 0x525DB0)
        self.assertEqual(TEAM_ROW_PRIMARY_VFTABLE, 0x7CA918)

        self.assertEqual(
            (
                SIDE_0_CONTRACT.primary_name_grid,
                SIDE_0_CONTRACT.alternate_name_grid,
                SIDE_0_CONTRACT.dynamic_energy_bar,
                SIDE_0_CONTRACT.static_energy_bar,
            ),
            (TEAM_NAME_GRID_1, TEAM_NAME_GRID_2, TEAM_BAR_1, BLANK_BAR),
        )
        self.assertEqual(
            (
                SIDE_1_CONTRACT.primary_name_grid,
                SIDE_1_CONTRACT.alternate_name_grid,
                SIDE_1_CONTRACT.dynamic_energy_bar,
                SIDE_1_CONTRACT.static_energy_bar,
            ),
            (TEAM_NAME_GRID_3, TEAM_NAME_GRID_4, BLANK_BAR, TEAM_BAR_2),
        )

    def test_name_grid_source_identities_are_exact(self):
        expected = (
            (
                TEAM_NAME_GRID_1,
                3496,
                "368f7c86ef07d9447af886b0a4d8857fa4a732d65f17913f72b2a9155e9a4d93",
                0x829424,
            ),
            (
                TEAM_NAME_GRID_2,
                3512,
                "0cce4d1646afa3dd11da5f0db6b3a887ded8a6d647f39d998eaef8ffe5f71602",
                0x8293F8,
            ),
            (
                TEAM_NAME_GRID_3,
                3512,
                "8deb413437234504cbb6c3a076b172304469d873f4e2df5fbedd314e5f22b095",
                0x829384,
            ),
            (
                TEAM_NAME_GRID_4,
                3496,
                "6fc1446b5d65a07a5165fa0947282dfeb6b783d142ae9edc76f60dbd5cecd3e8",
                0x829358,
            ),
        )
        for resource, byte_size, digest, path_va in expected:
            with self.subTest(resource=resource.name):
                self.assertEqual(resource.size, (259, 16))
                self.assertEqual(resource.byte_size, byte_size)
                self.assertEqual(resource.sha256, digest)
                self.assertEqual(resource.path_literal_va, path_va)
                self.assertFalse(resource.imported)

    def test_bar_source_identities_remain_separate_from_possession_figures(self):
        self.assertEqual(TEAM_BAR_1.size, (82, 16))
        self.assertEqual(BLANK_BAR.size, (82, 16))
        self.assertEqual(TEAM_BAR_2.size, (82, 16))
        self.assertEqual(TEAM_BAR_1.path_literal_va, 0x8293D4)
        self.assertEqual(BLANK_BAR.path_literal_va, 0x8293B0)
        self.assertEqual(TEAM_BAR_2.path_literal_va, 0x829334)

    def test_row_zero_and_step_geometry_are_exact_for_both_side_indices(self):
        self.assertEqual(team_row_origin(0, 0), (37, 27))
        self.assertEqual(team_row_origin(1, 0), (409, 27))
        self.assertEqual(team_row_origin(0, 1), (37, 44))
        self.assertEqual(team_row_origin(1, 1), (409, 44))
        self.assertEqual(TEAM_ROW_STEP, 17)

        name0, bar0, text0 = team_row_rects(0, 0)
        self.assertEqual(name0, (37, 27, 296, 43))
        self.assertEqual(bar0, (309, 27, 391, 43))
        self.assertEqual(
            text0,
            (
                (37, 27, 61, 43),
                (64, 27, 104, 43),
                (107, 27, 243, 43),
                (243, 27, 263, 43),
                (223, 27, 243, 43),
                (276, 27, 296, 43),
            ),
        )

        name1, bar1, text1 = team_row_rects(1, 0)
        self.assertEqual(name1, (504, 27, 763, 43))
        self.assertEqual(bar1, (409, 27, 491, 43))
        self.assertEqual(
            text1,
            (
                (537, 27, 561, 43),
                (564, 27, 604, 43),
                (607, 27, 743, 43),
                (743, 27, 763, 43),
                (723, 27, 743, 43),
                (504, 27, 524, 43),
            ),
        )
        self.assertEqual(TEAM_ROW_TEXT_RAW_FLAGS, (0x24, 0x24, 0x21, 0x21, 0x21, 0x24))

    def test_first_eleven_rows_use_primary_name_grid_then_alternate(self):
        self.assertEqual(TEAM_ROW_PRIMARY_NAME_COUNT, 11)
        for index in range(11):
            self.assertIs(team_row_name_resource(0, index), TEAM_NAME_GRID_1)
            self.assertIs(team_row_name_resource(1, index), TEAM_NAME_GRID_3)
        self.assertIs(team_row_name_resource(0, 11), TEAM_NAME_GRID_2)
        self.assertIs(team_row_name_resource(1, 11), TEAM_NAME_GRID_4)
        self.assertIs(team_row_name_resource(0, 20), TEAM_NAME_GRID_2)

    def test_energy_receiver_and_source_transform_are_exact(self):
        self.assertEqual(PLAYER_ROW_ENERGY_RECEIVER_BASE_VFTABLE, 0x7CA92C)
        self.assertEqual(PLAYER_ROW_ENERGY_RECEIVER_VFTABLE, 0x7CA900)
        self.assertEqual(PLAYER_ROW_ENERGY_RECEIVER_OFFSET, 0x58)
        self.assertEqual(PLAYER_ROW_ENERGY_CALLBACK_VA, 0x5267D0)
        self.assertEqual(PLAYER_ROW_ENERGY_UPDATE_VA, 0x526680)
        self.assertEqual(PLAYER_ROW_ENERGY_EVENT_VALUE_OFFSET, 0x04)
        self.assertEqual(PLAYER_ROW_ENERGY_MIN, 58)
        self.assertEqual(PLAYER_ROW_ENERGY_MAX, 99)
        self.assertEqual(PLAYER_ROW_ENERGY_SPAN, 41)
        self.assertEqual(PLAYER_ROW_ENERGY_SPAN_GLOBAL_VA, 0x877754)
        self.assertEqual(PLAYER_ROW_ENERGY_SPAN_INIT_VA, 0x51F330)
        self.assertEqual(PLAYER_ROW_ENERGY_BAR_WIDTH, 82)
        self.assertEqual(PLAYER_ROW_FLOAT_TO_INT_VA, 0x668350)

    def test_side_zero_energy_expands_team_bar_over_blank_bar(self):
        low = team_row_energy_bar_state(0, 0, 58)
        mid = team_row_energy_bar_state(0, 0, 79)
        full = team_row_energy_bar_state(0, 0, 99)
        over = team_row_energy_bar_state(0, 0, 120)

        self.assertIs(low.dynamic_resource, TEAM_BAR_1)
        self.assertIs(low.static_resource, BLANK_BAR)
        self.assertEqual(low.full_rect, (309, 27, 391, 43))
        self.assertEqual(low.source_scaled_width, 0)
        self.assertEqual(low.dynamic_rect, (309, 27, 309, 43))
        self.assertEqual(mid.source_scaled_width, 42)
        self.assertEqual(mid.dynamic_rect, (309, 27, 351, 43))
        self.assertEqual(full.dynamic_rect, (309, 27, 391, 43))
        self.assertEqual(over.dynamic_rect, (309, 27, 391, 43))

    def test_side_one_energy_shrinks_blank_mask_to_reveal_team_bar(self):
        low = team_row_energy_bar_state(1, 0, 58)
        mid = team_row_energy_bar_state(1, 0, 79)
        full = team_row_energy_bar_state(1, 0, 99)

        self.assertIs(low.dynamic_resource, BLANK_BAR)
        self.assertIs(low.static_resource, TEAM_BAR_2)
        self.assertEqual(low.full_rect, (409, 27, 491, 43))
        self.assertEqual(low.dynamic_rect, (409, 27, 491, 43))
        self.assertEqual(mid.dynamic_rect, (409, 27, 449, 43))
        self.assertEqual(full.dynamic_rect, (409, 27, 409, 43))

    def test_source_does_not_lower_clamp_energy_transform(self):
        low = team_row_energy_bar_state(0, 1, 57)
        self.assertEqual(low.source_scaled_width, -2)
        self.assertEqual(low.dynamic_rect, (309, 44, 307, 60))

    def test_invalid_side_and_row_inputs_fail_closed(self):
        for bad in (-1, 2, True, "0"):
            with self.subTest(side=bad):
                with self.assertRaises(FastViewTeamError):
                    side_contract(bad)
        for bad in (-1, True, 1.5, "0"):
            with self.subTest(row=bad):
                with self.assertRaises(FastViewTeamError):
                    team_row_origin(0, bad)
        with self.assertRaises(FastViewTeamError):
            team_row_energy_bar_state(0, 0, True)


if __name__ == "__main__":
    unittest.main()
