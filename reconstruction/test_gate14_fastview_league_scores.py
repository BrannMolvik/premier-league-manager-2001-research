import tempfile
import unittest
from pathlib import Path

from gate14_fastview_league_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_1_OWNER_LOCAL_RECT,
    CURRENT_FIX_GRID_1_PATH_LITERAL_VA,
    CURRENT_FIX_GRID_1_PICTURE_CONTROL_CALL_VA,
    CURRENT_FIX_GRID_1_STRING_INIT_VA,
    CURRENT_FIX_GRID_2,
    CURRENT_FIX_GRID_2_OWNER_LOCAL_RECT,
    SOURCE_FASTVIEW_LEAGUE_SCORES_CONSTRUCT_VFUNC_CALL_VA,
    SOURCE_FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE,
    SOURCE_FASTVIEW_LEAGUE_SCORES_RTTI,
    SOURCE_FASTVIEW_LEAGUE_SCORES_SETUP_VA,
    FastViewLeagueScoresError,
    current_fixture_grid1_rect,
    validate_staged_current_fixture_grid1,
)


class FastViewLeagueScoresTests(unittest.TestCase):
    def test_class_and_setup_method_are_source_bound(self):
        self.assertEqual(SOURCE_FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE, 0x7CA750)
        self.assertEqual(
            SOURCE_FASTVIEW_LEAGUE_SCORES_RTTI,
            ".?AVFastViewLeagueScores@FastViewPanel@@",
        )
        self.assertEqual(SOURCE_FASTVIEW_LEAGUE_SCORES_SETUP_VA, 0x523370)
        self.assertEqual(
            SOURCE_FASTVIEW_LEAGUE_SCORES_CONSTRUCT_VFUNC_CALL_VA,
            0x520D82,
        )

    def test_current_fixture_grid1_is_exact_direct_picture_control(self):
        self.assertTrue(CURRENT_FIX_GRID_1.direct_picture_control)
        self.assertEqual(CURRENT_FIX_GRID_1_PATH_LITERAL_VA, 0x829920)
        self.assertEqual(CURRENT_FIX_GRID_1_STRING_INIT_VA, 0x5239AB)
        self.assertEqual(CURRENT_FIX_GRID_1_PICTURE_CONTROL_CALL_VA, 0x5239F3)
        self.assertEqual(CURRENT_FIX_GRID_1.byte_size, 3704)
        self.assertEqual(CURRENT_FIX_GRID_1.size, (309, 19))
        self.assertEqual(
            CURRENT_FIX_GRID_1.sha256,
            "bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057",
        )
        self.assertEqual(current_fixture_grid1_rect(), (38, 32, 347, 51))
        self.assertEqual(
            CURRENT_FIX_GRID_1_OWNER_LOCAL_RECT,
            (38, 32, 347, 51),
        )

    def test_grid2_remains_ownership_only_until_layout_descriptor_is_decoded(self):
        self.assertEqual(CURRENT_FIX_GRID_2.byte_size, 4060)
        self.assertEqual(CURRENT_FIX_GRID_2.size, (309, 16))
        self.assertEqual(
            CURRENT_FIX_GRID_2.sha256,
            "ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e",
        )
        self.assertFalse(CURRENT_FIX_GRID_2.direct_picture_control)
        self.assertIsNone(CURRENT_FIX_GRID_2_OWNER_LOCAL_RECT)

    def test_missing_staged_grid_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(FastViewLeagueScoresError, "Missing staged"):
                validate_staged_current_fixture_grid1(Path(tmp))


if __name__ == "__main__":
    unittest.main()
