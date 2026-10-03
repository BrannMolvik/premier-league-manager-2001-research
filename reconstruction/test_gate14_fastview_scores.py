import unittest

from gate14_fastview_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    EVENT_LEAGUE_TABLE_UPDATE_BASE_VFTABLE,
    FASTVIEW_LEAGUE_SCORES_EVENT_UPDATE_CALLBACK_VA,
    FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE,
    FASTVIEW_LEAGUE_SCORES_RECEIVER_VFTABLE,
    SCORE_COMPOSITE_EVENT_RECEIVERS,
    SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA,
    SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS,
    SCORE_COMPOSITE_NORMAL_LAYOUT_TABLE_VA,
    SCORE_COMPOSITE_NORMAL_PRIMARY_VFTABLE,
    FastViewScoresError,
    fastview_league_scores_grid_rects,
    score_composite_normal_local_grid_size,
)


class FastViewScoresTests(unittest.TestCase):
    def test_current_fixture_assets_have_distinct_source_owners(self):
        self.assertEqual(CURRENT_FIX_GRID_1.size, (309, 19))
        self.assertEqual(CURRENT_FIX_GRID_1.byte_size, 3704)
        self.assertEqual(CURRENT_FIX_GRID_1.path_literal_va, 0x829920)
        self.assertEqual(
            CURRENT_FIX_GRID_1.sha256,
            "bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057",
        )
        self.assertEqual(
            CURRENT_FIX_GRID_1.owner,
            "FastViewPanel::FastViewLeagueScores",
        )

        self.assertEqual(CURRENT_FIX_GRID_2.size, (309, 16))
        self.assertEqual(CURRENT_FIX_GRID_2.byte_size, 4060)
        self.assertEqual(CURRENT_FIX_GRID_2.path_literal_va, 0x828ED0)
        self.assertEqual(
            CURRENT_FIX_GRID_2.sha256,
            "ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e",
        )
        self.assertEqual(CURRENT_FIX_GRID_2.owner, "ScoreCompositeNormal")
        self.assertFalse(CURRENT_FIX_GRID_1.imported)
        self.assertFalse(CURRENT_FIX_GRID_2.imported)

    def test_league_scores_grid_one_strip_or_two_strips_at_source_threshold(self):
        self.assertEqual(
            fastview_league_scores_grid_rects(1),
            ((246, 32, 555, 51),),
        )
        self.assertEqual(
            fastview_league_scores_grid_rects(12),
            ((246, 32, 555, 51),),
        )
        self.assertEqual(
            fastview_league_scores_grid_rects(13),
            ((38, 32, 347, 51), (454, 32, 763, 51)),
        )
        for rect in fastview_league_scores_grid_rects(24):
            self.assertEqual((rect[2] - rect[0], rect[3] - rect[1]), (309, 19))

    def test_invalid_grid_count_fails_closed(self):
        for value in (0, -1, True, 1.5, "12"):
            with self.subTest(value=value):
                with self.assertRaises(FastViewScoresError):
                    fastview_league_scores_grid_rects(value)

    def test_fastview_league_scores_receiver_identity_is_source_bound(self):
        self.assertEqual(FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE, 0x7CA750)
        self.assertEqual(FASTVIEW_LEAGUE_SCORES_RECEIVER_VFTABLE, 0x7CA744)
        self.assertEqual(EVENT_LEAGUE_TABLE_UPDATE_BASE_VFTABLE, 0x7CA7B4)
        self.assertEqual(FASTVIEW_LEAGUE_SCORES_EVENT_UPDATE_CALLBACK_VA, 0x523DB0)

    def test_score_composite_normal_source_table_and_receiver_lifecycle(self):
        self.assertEqual(SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA, 0x51B740)
        self.assertEqual(SCORE_COMPOSITE_NORMAL_PRIMARY_VFTABLE, 0x7CA36C)
        self.assertEqual(SCORE_COMPOSITE_NORMAL_LAYOUT_TABLE_VA, 0x828E98)
        self.assertEqual(
            SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS,
            (309, 16, 0, 0, 0, 0, 2, 139, 177, 158, 130, 16, 13, 16),
        )
        self.assertEqual(score_composite_normal_local_grid_size(), (309, 16))
        self.assertEqual(
            [(name, callback) for name, _, _, callback in SCORE_COMPOSITE_EVENT_RECEIVERS],
            [
                ("EventHalfTime", 0x51B9A0),
                ("EventExtraTime", 0x51B9C0),
                ("EventPenalties", 0x51B9E0),
                ("EventFullTime", 0x51BA00),
                ("EventGlobalSecondHalf", 0x51BA20),
            ],
        )


if __name__ == "__main__":
    unittest.main()
