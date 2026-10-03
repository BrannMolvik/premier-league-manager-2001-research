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
    TEAM_TABLE_CONSTRUCTOR_VA,
    TEAM_TABLE_VFTABLE,
    FastViewTeamError,
    side_contract,
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
                SIDE_0_CONTRACT.bar_a,
                SIDE_0_CONTRACT.bar_b,
            ),
            (TEAM_NAME_GRID_1, TEAM_NAME_GRID_2, TEAM_BAR_1, BLANK_BAR),
        )
        self.assertEqual(
            (
                SIDE_1_CONTRACT.primary_name_grid,
                SIDE_1_CONTRACT.alternate_name_grid,
                SIDE_1_CONTRACT.bar_a,
                SIDE_1_CONTRACT.bar_b,
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

    def test_invalid_side_and_row_inputs_fail_closed(self):
        for bad in (-1, 2, True, "0"):
            with self.subTest(side=bad):
                with self.assertRaises(FastViewTeamError):
                    side_contract(bad)
        for bad in (-1, True, 1.5, "0"):
            with self.subTest(row=bad):
                with self.assertRaises(FastViewTeamError):
                    team_row_origin(0, bad)


if __name__ == "__main__":
    unittest.main()
