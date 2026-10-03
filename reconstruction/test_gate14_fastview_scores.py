import unittest

from gate14_fastview_scores import (
    CURRENT_FIX_GRID_1,
    CURRENT_FIX_GRID_2,
    HALF_TIME_ICON,
    FULL_TIME_ICON,
    EXTRA_TIME_ICON,
    PENALTIES_ICON,
    SCORE_COMPOSITE_PHASE_RESOURCES,
    SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA,
    SCORE_COMPOSITE_PHASE_DISPLAY_CLEAR_VA,
    SCORE_COMPOSITE_PHASE_ICON_LOCAL_RECT,
    SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT,
    SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS,
    SCORE_COMPOSITE_PHASE_TEXT_STYLE_INDEX,
    SCORE_COMPOSITE_PHASE_PICTURE_VARIANT,
    SCORE_COMPOSITE_PHASE_ACTIVE_FLAG_OFFSET,
    SCORE_COMPOSITE_PHASE_PICTURE_PTR_OFFSET,
    SCORE_COMPOSITE_PHASE_TEXT_PTR_OFFSET,
    EVENT_LEAGUE_TABLE_UPDATE_BASE_VFTABLE,
    FASTVIEW_LEAGUE_SCORES_EVENT_UPDATE_CALLBACK_VA,
    FASTVIEW_LEAGUE_SCORES_PRIMARY_VFTABLE,
    FASTVIEW_LEAGUE_SCORES_RECEIVER_VFTABLE,
    SCORE_COMPOSITE_EVENT_RECEIVERS,
    SCORE_COMPOSITE_NORMAL_CONSTRUCTOR_VA,
    SCORE_COMPOSITE_NORMAL_LAYOUT_DWORDS,
    SCORE_COMPOSITE_NORMAL_LAYOUT_TABLE_VA,
    SCORE_COMPOSITE_NORMAL_PRIMARY_VFTABLE,
    SCORE_COMPOSITE_NORMAL_GRID_LOCAL_RECT,
    SCORE_COMPOSITE_NORMAL_TEXT_LOCAL_RECTS,
    FASTVIEW_LEAGUE_SCORES_ROW_COUNT,
    FASTVIEW_LEAGUE_SCORES_ROW_STEP,
    FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_STEP,
    FastViewScoresError,
    fastview_league_scores_grid_rects,
    fastview_league_scores_page_layout,
    score_composite_normal_local_grid_size,
    score_composite_normal_page_slot_rects,
    score_composite_normal_rects,
    score_composite_phase_local_rects,
    score_composite_phase_rects,
    score_composite_phase_resource,
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

    def test_phase_icons_are_exact_typed_source_resources(self):
        expected = {
            "EventHalfTime": (
                HALF_TIME_ICON,
                568,
                "351589aa787ef62dae4013c67e231c90c7b6f2e82acd635fb67adb13e1c994c8",
                0x828DD0,
                0x51B650,
                0x877628,
                0x51B9A0,
                0x877630,
                0x982380,
            ),
            "EventFullTime": (
                FULL_TIME_ICON,
                616,
                "9a24ab846620d6460afe265c6c98488870a08e2802d55476b9735a8641ae81b8",
                0x828DF8,
                0x51B690,
                0x877610,
                0x51BA00,
                0x877618,
                0x98237C,
            ),
            "EventExtraTime": (
                EXTRA_TIME_ICON,
                400,
                "cf8af734450ab3069e0b32d82a770909d962ade9545533e7715d36d53e0eea2e",
                0x828E20,
                0x51B6D0,
                0x8775F8,
                0x51B9C0,
                0x877600,
                0x982378,
            ),
            "EventPenalties": (
                PENALTIES_ICON,
                280,
                "0fc5b157ecfadfa437f65ef5a4b940b5de6886e8c1e81e1f4ccba8d97af23545",
                0x828E48,
                0x51B710,
                0x8775E0,
                0x51B9E0,
                0x8775E8,
                0x982374,
            ),
        }
        self.assertEqual(len(SCORE_COMPOSITE_PHASE_RESOURCES), 4)
        for event_name, values in expected.items():
            (
                resource,
                byte_size,
                sha256,
                path_va,
                init_va,
                object_va,
                callback_va,
                icon_pointer_va,
                label_global_va,
            ) = values
            with self.subTest(event_name=event_name):
                self.assertIs(score_composite_phase_resource(event_name), resource)
                self.assertEqual(resource.event_name, event_name)
                self.assertEqual(resource.size, (18, 16))
                self.assertEqual(resource.byte_size, byte_size)
                self.assertEqual(resource.sha256, sha256)
                self.assertEqual(resource.path_literal_va, path_va)
                self.assertEqual(resource.static_string_initializer_va, init_va)
                self.assertEqual(resource.static_string_object_va, object_va)
                self.assertEqual(resource.callback_va, callback_va)
                self.assertEqual(resource.callback_icon_pointer_va, icon_pointer_va)
                self.assertEqual(resource.callback_label_global_va, label_global_va)
                self.assertFalse(resource.imported)

    def test_phase_helper_constructs_exact_icon_and_paired_text_rectangles(self):
        self.assertEqual(SCORE_COMPOSITE_PHASE_DISPLAY_HELPER_VA, 0x51BA30)
        self.assertEqual(SCORE_COMPOSITE_PHASE_DISPLAY_CLEAR_VA, 0x51BBE0)
        self.assertEqual(SCORE_COMPOSITE_PHASE_ICON_LOCAL_RECT, (316, 0, 334, 16))
        self.assertEqual(SCORE_COMPOSITE_PHASE_TEXT_LOCAL_RECT, (311, 0, 339, 16))
        self.assertEqual(
            score_composite_phase_local_rects(),
            ((316, 0, 334, 16), (311, 0, 339, 16)),
        )
        self.assertEqual(
            score_composite_phase_rects((246, 55)),
            ((562, 55, 580, 71), (557, 55, 585, 71)),
        )
        self.assertEqual(SCORE_COMPOSITE_PHASE_PICTURE_VARIANT, 0)
        self.assertEqual(SCORE_COMPOSITE_PHASE_TEXT_RAW_FLAGS, 0x24)
        self.assertEqual(SCORE_COMPOSITE_PHASE_TEXT_STYLE_INDEX, 1)
        self.assertEqual(SCORE_COMPOSITE_PHASE_ACTIVE_FLAG_OFFSET, 0xAC)
        self.assertEqual(SCORE_COMPOSITE_PHASE_PICTURE_PTR_OFFSET, 0xD8)
        self.assertEqual(SCORE_COMPOSITE_PHASE_TEXT_PTR_OFFSET, 0xDC)

    def test_phase_mapping_fails_closed_for_unproved_event_or_origin(self):
        with self.assertRaises(FastViewScoresError):
            score_composite_phase_resource("EventGlobalSecondHalf")
        with self.assertRaises(FastViewScoresError):
            score_composite_phase_resource(1)
        with self.assertRaises(FastViewScoresError):
            score_composite_phase_rects([246, 55])

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

    def test_score_composite_final_page_origins_follow_source_relayout(self):
        one = fastview_league_scores_page_layout(12)
        self.assertEqual(one.columns, 1)
        self.assertEqual(one.rows_per_column, FASTVIEW_LEAGUE_SCORES_ROW_COUNT)
        self.assertEqual(one.row_step, FASTVIEW_LEAGUE_SCORES_ROW_STEP)
        self.assertEqual(one.slot_origin(0, 0), (246, 55))
        self.assertEqual(one.slot_origin(0, 11), (246, 264))

        two = fastview_league_scores_page_layout(13)
        self.assertEqual(two.columns, 2)
        self.assertEqual(two.column_step, FASTVIEW_LEAGUE_SCORES_TWO_COLUMN_STEP)
        self.assertEqual(two.slot_origin(0, 0), (38, 55))
        self.assertEqual(two.slot_origin(0, 11), (38, 264))
        self.assertEqual(two.slot_origin(1, 0), (454, 55))
        self.assertEqual(two.slot_origin(1, 11), (454, 264))

    def test_score_composite_grid_and_text_rectangles_translate_from_fixed_table(self):
        self.assertEqual(SCORE_COMPOSITE_NORMAL_GRID_LOCAL_RECT, (0, 0, 309, 16))
        self.assertEqual(
            SCORE_COMPOSITE_NORMAL_TEXT_LOCAL_RECTS,
            (
                (2, 0, 132, 16),
                (177, 0, 307, 16),
                (139, 0, 152, 16),
                (158, 0, 171, 16),
            ),
        )
        grid, text = score_composite_normal_rects((246, 55))
        self.assertEqual(grid, (246, 55, 555, 71))
        self.assertEqual(
            text,
            (
                (248, 55, 378, 71),
                (423, 55, 553, 71),
                (385, 55, 398, 71),
                (404, 55, 417, 71),
            ),
        )
        grid2, text2 = score_composite_normal_page_slot_rects(13, 1, 0)
        self.assertEqual(grid2, (454, 55, 763, 71))
        self.assertEqual(text2[0], (456, 55, 586, 71))
        self.assertEqual(text2[3], (612, 55, 625, 71))

    def test_invalid_page_slot_and_origin_fail_closed(self):
        with self.assertRaises(FastViewScoresError):
            fastview_league_scores_page_layout(True)
        with self.assertRaises(FastViewScoresError):
            fastview_league_scores_page_layout(13).slot_origin(2, 0)
        with self.assertRaises(FastViewScoresError):
            fastview_league_scores_page_layout(13).slot_origin(1, 12)
        with self.assertRaises(FastViewScoresError):
            score_composite_normal_rects([38, 55])

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
