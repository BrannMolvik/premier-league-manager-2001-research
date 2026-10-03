import unittest

from gate14_fastview_teamtable import (
    BLANK_BAR_PATH,
    FASTVIEW_TEAM_CONSTRUCTOR_VA,
    FASTVIEW_TEAM_TYPE_DESCRIPTOR_VA,
    FASTVIEW_TEAM_VFTABLE_VA,
    TEAMTABLE_BAR_HEIGHT,
    TEAMTABLE_BAR_WIDTH,
    TEAMTABLE_CONSTRUCTOR_VA,
    TEAMTABLE_FIRST_ROW_Y,
    TEAMTABLE_ROW_CONSTRUCTOR_VA,
    TEAMTABLE_ROW_COUNT,
    TEAMTABLE_ROW_DYNAMIC_BAR_UPDATE_VA,
    TEAMTABLE_ROW_DYNAMIC_CONTROL_OFFSET,
    TEAMTABLE_ROW_PAIRED_CONTROL_OFFSET,
    TEAMTABLE_ROW_SIDE_FLAG_OFFSET,
    TEAMTABLE_ROW_STEP,
    TEAMTABLE_ROW_TYPE_DESCRIPTOR_VA,
    TEAMTABLE_ROW_VFTABLE_VA,
    TEAMTABLE_SIDE0_BAR_X,
    TEAMTABLE_SIDE1_BAR_X,
    TEAMTABLE_TYPE_DESCRIPTOR_VA,
    TEAMTABLE_VFTABLE_VA,
    TEAM_BAR_1_PATH,
    TEAM_BAR_2_PATH,
    FastViewTeamTableError,
    teamtable_bar_pair,
)


class FastViewTeamTableTests(unittest.TestCase):
    def test_rtti_and_constructor_chain_is_exact(self):
        self.assertEqual(FASTVIEW_TEAM_CONSTRUCTOR_VA, 0x524A20)
        self.assertEqual(FASTVIEW_TEAM_VFTABLE_VA, 0x7CA888)
        self.assertEqual(FASTVIEW_TEAM_TYPE_DESCRIPTOR_VA, 0x8299D8)
        self.assertEqual(TEAMTABLE_CONSTRUCTOR_VA, 0x524EC0)
        self.assertEqual(TEAMTABLE_VFTABLE_VA, 0x7CA950)
        self.assertEqual(TEAMTABLE_TYPE_DESCRIPTOR_VA, 0x829B50)
        self.assertEqual(TEAMTABLE_ROW_CONSTRUCTOR_VA, 0x525DB0)
        self.assertEqual(TEAMTABLE_ROW_VFTABLE_VA, 0x7CA968)
        self.assertEqual(TEAMTABLE_ROW_TYPE_DESCRIPTOR_VA, 0x829A78)
        self.assertEqual(TEAMTABLE_ROW_DYNAMIC_BAR_UPDATE_VA, 0x526680)

    def test_row_geometry_is_eleven_rows_of_82x16_at_17_pixel_step(self):
        self.assertEqual(TEAMTABLE_ROW_COUNT, 11)
        self.assertEqual(TEAMTABLE_ROW_STEP, 17)
        self.assertEqual(TEAMTABLE_BAR_WIDTH, 82)
        self.assertEqual(TEAMTABLE_BAR_HEIGHT, 16)
        self.assertEqual(TEAMTABLE_FIRST_ROW_Y, 27)
        self.assertEqual(TEAMTABLE_SIDE0_BAR_X, 309)
        self.assertEqual(TEAMTABLE_SIDE1_BAR_X, 409)

        self.assertEqual(teamtable_bar_pair(0, 0).rect, (309, 27, 391, 43))
        self.assertEqual(teamtable_bar_pair(0, 10).rect, (309, 197, 391, 213))
        self.assertEqual(teamtable_bar_pair(1, 0).rect, (409, 27, 491, 43))
        self.assertEqual(teamtable_bar_pair(1, 10).rect, (409, 197, 491, 213))

    def test_resource_pairing_preserves_source_side_index_without_user_semantics(self):
        side0 = teamtable_bar_pair(0, 4)
        self.assertEqual(side0.dynamic_resource_path, TEAM_BAR_1_PATH)
        self.assertEqual(side0.paired_resource_path, BLANK_BAR_PATH)

        side1 = teamtable_bar_pair(1, 4)
        self.assertEqual(side1.dynamic_resource_path, BLANK_BAR_PATH)
        self.assertEqual(side1.paired_resource_path, TEAM_BAR_2_PATH)

        self.assertEqual(side0.dynamic_control_offset, 0x38)
        self.assertEqual(side0.paired_control_offset, 0x3C)
        self.assertEqual(TEAMTABLE_ROW_SIDE_FLAG_OFFSET, 0x40)
        self.assertEqual(TEAMTABLE_ROW_DYNAMIC_CONTROL_OFFSET, 0x38)
        self.assertEqual(TEAMTABLE_ROW_PAIRED_CONTROL_OFFSET, 0x3C)

    def test_invalid_side_or_row_fails_closed(self):
        for side, row in ((-1, 0), (2, 0), (True, 0), (0, -1), (0, 11), (0, True)):
            with self.subTest(side=side, row=row):
                with self.assertRaises(FastViewTeamTableError):
                    teamtable_bar_pair(side, row)


if __name__ == "__main__":
    unittest.main()
