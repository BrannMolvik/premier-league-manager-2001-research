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
    PLAYER_ROW_FORM_RECEIVER_BASE_VFTABLE,
    PLAYER_ROW_GOAL_RECEIVER_BASE_VFTABLE,
    PLAYER_ROW_OWN_GOAL_RECEIVER_BASE_VFTABLE,
    PLAYER_ROW_FORM_RECEIVER_VFTABLE,
    PLAYER_ROW_GOAL_RECEIVER_VFTABLE,
    PLAYER_ROW_OWN_GOAL_RECEIVER_VFTABLE,
    PLAYER_ROW_FORM_RECEIVER_OFFSET,
    PLAYER_ROW_GOAL_RECEIVER_OFFSET,
    PLAYER_ROW_OWN_GOAL_RECEIVER_OFFSET,
    PLAYER_ROW_FORM_CALLBACK_VA,
    PLAYER_ROW_GOAL_CALLBACK_VA,
    PLAYER_ROW_OWN_GOAL_CALLBACK_VA,
    PLAYER_ROW_FORM_EVENT_VALUE_OFFSET,
    PLAYER_ROW_FORM_TEXT_CONTROL_OFFSET,
    PLAYER_ROW_GOAL_COUNTER_OFFSET,
    PLAYER_ROW_GOAL_TEXT_CONTROL_OFFSET,
    PLAYER_ROW_OWN_GOAL_COUNTER_OFFSET,
    PLAYER_ROW_OWN_GOAL_TEXT_CONTROL_OFFSET,
    PLAYER_ROW_FORM_FORMAT_VA,
    PLAYER_ROW_FORM_FORMAT,
    PLAYER_ROW_GOAL_COUNT_FORMAT_VA,
    PLAYER_ROW_GOAL_COUNT_FORMAT,
    PLAYER_ROW_OWN_GOAL_COLOR_SETTER_VA,
    PLAYER_ROW_SHARED_REFRESH_VA,
    TEAM_TABLE_SHARED_REFRESH_CALL_VA,
    TEAM_TABLE_ROW_DATA_PRODUCER_VA,
    PLAYER_ROW_POSITION_LOOKUP_VA,
    PLAYER_ROW_POSITION_LOCALIZER_VA,
    PLAYER_ROW_POSITION_TABLE_VA,
    PLAYER_ROW_POSITION_TEXT_CELL_INDEX,
    PLAYER_ROW_POSITION_KEYS,
    DBRPLAYER_SQUAD_NUMBER_RUNTIME_OFFSET,
    PLAYER_ROW_CELL1_MATCH_PROXY_OFFSET,
    PLAYER_ROW_NAME_RECORD_BUILDER_VA,
    PLAYER_ROW_DBRPLAYER_FIRST_NAME_RUNTIME_OFFSET,
    PLAYER_ROW_DBRPLAYER_SURNAME_RUNTIME_OFFSET,
    PLAYER_ROW_NAME_STRING_OFFSET,
    PLAYER_ROW_NAME_PREFIX_OFFSET,
    PLAYER_ROW_NAME_SENTINEL,
    PLAYER_ROW_NAME_PLAIN_FORMAT_VA,
    PLAYER_ROW_NAME_PLAIN_FORMAT,
    PLAYER_ROW_NAME_PREFIX_FORMAT_VA,
    PLAYER_ROW_NAME_PREFIX_FORMAT,
    PLAYER_ROW_NAME_WITH_POSITION_FORMAT_VA,
    PLAYER_ROW_NAME_WITH_POSITION_FORMAT,
    PLAYER_ROW_NAME_TEXT_CELL_INDEX,
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
    player_row_form_text_state,
    player_row_goal_text_state,
    player_row_position_state,
    player_row_name_text_state,
    side_contract,
    team_row_energy_bar_state,
    team_row_name_resource,
    team_row_origin,
    team_row_rects,
    team_row_text_rect,
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

    def test_playerrow_cell2_is_source_position_lookup(self):
        self.assertEqual(PLAYER_ROW_SHARED_REFRESH_VA, 0x526470)
        self.assertEqual(TEAM_TABLE_SHARED_REFRESH_CALL_VA, 0x525B66)
        self.assertEqual(TEAM_TABLE_ROW_DATA_PRODUCER_VA, 0x525BD0)
        self.assertEqual(PLAYER_ROW_POSITION_LOOKUP_VA, 0x635EC0)
        self.assertEqual(PLAYER_ROW_POSITION_LOCALIZER_VA, 0x6350D0)
        self.assertEqual(PLAYER_ROW_POSITION_TABLE_VA, 0x849930)
        self.assertEqual(PLAYER_ROW_POSITION_TEXT_CELL_INDEX, 2)
        self.assertEqual(
            PLAYER_ROW_POSITION_KEYS,
            (
                "", "PositionGK", "PositionRB", "PositionLB", "PositionCD",
                "PositionSW", "PositionRWB", "PositionLWB", "PositionANC",
                "PositionDM", "PositionRM", "PositionLM", "PositionCM",
                "PositionRW", "PositionLW", "PositionAM", "PositionRF",
                "PositionLF", "PositionCF", "PositionST",
            ),
        )
        state = player_row_position_state(0, 0, 1)
        self.assertEqual(state.text_cell_index, 2)
        self.assertEqual(state.rect, (64, 27, 104, 43))
        self.assertEqual(state.source_position_code, 1)
        self.assertEqual(state.localization_key, "PositionGK")
        away = player_row_position_state(1, 2, 19)
        self.assertEqual(away.rect, (564, 61, 604, 77))
        self.assertEqual(away.localization_key, "PositionST")

    def test_cell1_proxy_byte_is_not_equated_to_dbrplayer_squad_number(self):
        self.assertEqual(DBRPLAYER_SQUAD_NUMBER_RUNTIME_OFFSET, 0x70)
        self.assertEqual(PLAYER_ROW_CELL1_MATCH_PROXY_OFFSET, 0x47)
        self.assertNotEqual(
            DBRPLAYER_SQUAD_NUMBER_RUNTIME_OFFSET,
            PLAYER_ROW_CELL1_MATCH_PROXY_OFFSET,
        )
        for bad in (-1, 20, True, "1"):
            with self.subTest(bad=bad):
                with self.assertRaises(FastViewTeamError):
                    player_row_position_state(0, 0, bad)

    def test_playerrow_cell3_is_source_player_display_name(self):
        self.assertEqual(PLAYER_ROW_NAME_RECORD_BUILDER_VA, 0x533A00)
        self.assertEqual(PLAYER_ROW_DBRPLAYER_FIRST_NAME_RUNTIME_OFFSET, 0x08)
        self.assertEqual(PLAYER_ROW_DBRPLAYER_SURNAME_RUNTIME_OFFSET, 0x0C)
        self.assertEqual(PLAYER_ROW_NAME_STRING_OFFSET, 0x00)
        self.assertEqual(PLAYER_ROW_NAME_PREFIX_OFFSET, 0x20)
        self.assertEqual(PLAYER_ROW_NAME_SENTINEL, "-")
        self.assertEqual(PLAYER_ROW_NAME_PLAIN_FORMAT_VA, 0x81D97C)
        self.assertEqual(PLAYER_ROW_NAME_PLAIN_FORMAT, "%s")
        self.assertEqual(PLAYER_ROW_NAME_PREFIX_FORMAT_VA, 0x829B8C)
        self.assertEqual(PLAYER_ROW_NAME_PREFIX_FORMAT, "%c %s")
        self.assertEqual(PLAYER_ROW_NAME_WITH_POSITION_FORMAT_VA, 0x829EB8)
        self.assertEqual(PLAYER_ROW_NAME_WITH_POSITION_FORMAT, "%c %s (%s)")
        self.assertEqual(PLAYER_ROW_NAME_TEXT_CELL_INDEX, 3)

        named = player_row_name_text_state(0, 0, "Seaman", "D")
        self.assertEqual(named.semantic, "player_display_name")
        self.assertEqual(named.text_cell_index, 3)
        self.assertEqual(named.rect, (107, 27, 243, 43))
        self.assertEqual(named.text, "D Seaman")

        sentinel = player_row_name_text_state(1, 1, "Ronaldo", "-")
        self.assertEqual(sentinel.rect, (607, 44, 743, 60))
        self.assertEqual(sentinel.text, "Ronaldo")

        for args in (("", "D"), ("Seaman", ""), ("Seaman", "AB")):
            with self.subTest(args=args):
                with self.assertRaises(FastViewTeamError):
                    player_row_name_text_state(0, 0, *args)

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

    def test_typed_form_goal_and_own_goal_receivers_are_exact(self):
        self.assertEqual(PLAYER_ROW_FORM_RECEIVER_BASE_VFTABLE, 0x7CA938)
        self.assertEqual(PLAYER_ROW_GOAL_RECEIVER_BASE_VFTABLE, 0x7CA920)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_RECEIVER_BASE_VFTABLE, 0x7CA95C)
        self.assertEqual(PLAYER_ROW_FORM_RECEIVER_VFTABLE, 0x7CA90C)
        self.assertEqual(PLAYER_ROW_GOAL_RECEIVER_VFTABLE, 0x7CA8F4)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_RECEIVER_VFTABLE, 0x7CA8E8)
        self.assertEqual(PLAYER_ROW_FORM_RECEIVER_OFFSET, 0x54)
        self.assertEqual(PLAYER_ROW_GOAL_RECEIVER_OFFSET, 0x5C)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_RECEIVER_OFFSET, 0x60)
        self.assertEqual(PLAYER_ROW_FORM_CALLBACK_VA, 0x526740)
        self.assertEqual(PLAYER_ROW_GOAL_CALLBACK_VA, 0x526800)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_CALLBACK_VA, 0x526880)
        self.assertEqual(PLAYER_ROW_FORM_EVENT_VALUE_OFFSET, 0x04)
        self.assertEqual(PLAYER_ROW_FORM_TEXT_CONTROL_OFFSET, 0x34)
        self.assertEqual(PLAYER_ROW_GOAL_COUNTER_OFFSET, 0x18)
        self.assertEqual(PLAYER_ROW_GOAL_TEXT_CONTROL_OFFSET, 0x2C)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_COUNTER_OFFSET, 0x1C)
        self.assertEqual(PLAYER_ROW_OWN_GOAL_TEXT_CONTROL_OFFSET, 0x30)
        self.assertEqual(PLAYER_ROW_FORM_FORMAT_VA, 0x828D3C)
        self.assertEqual(PLAYER_ROW_FORM_FORMAT, "%u")
        self.assertEqual(PLAYER_ROW_GOAL_COUNT_FORMAT_VA, 0x829B94)
        self.assertEqual(PLAYER_ROW_GOAL_COUNT_FORMAT, "(%u)")
        self.assertEqual(PLAYER_ROW_OWN_GOAL_COLOR_SETTER_VA, 0x650480)

    def test_form_event_writes_text_cell_six_on_each_side(self):
        side0 = player_row_form_text_state(0, 0, 4)
        side1 = player_row_form_text_state(1, 2, 7)
        self.assertEqual((side0.text_cell_index, side0.text), (6, "4"))
        self.assertEqual(side0.rect, (276, 27, 296, 43))
        self.assertEqual(side1.rect, (504, 61, 524, 77))
        self.assertFalse(side0.source_color_update)

    def test_goal_and_own_goal_events_increment_separate_parenthesized_counters(self):
        goal = player_row_goal_text_state(0, 0, 2)
        own = player_row_goal_text_state(1, 0, 0, own_goal=True)
        self.assertEqual(goal.semantic, "player_goal_count")
        self.assertEqual(goal.stored_value, 3)
        self.assertEqual(goal.text, "(3)")
        self.assertEqual(goal.text_cell_index, 4)
        self.assertEqual(goal.rect, (243, 27, 263, 43))
        self.assertFalse(goal.source_color_update)

        self.assertEqual(own.semantic, "player_own_goal_count")
        self.assertEqual(own.stored_value, 1)
        self.assertEqual(own.text, "(1)")
        self.assertEqual(own.text_cell_index, 5)
        self.assertEqual(own.rect, (723, 27, 743, 43))
        self.assertTrue(own.source_color_update)

    def test_goal_counter_wrap_and_source_u32_validation_are_explicit(self):
        wrapped = player_row_goal_text_state(0, 0, 0xFFFFFFFF)
        self.assertEqual(wrapped.stored_value, 0)
        self.assertEqual(wrapped.text, "(0)")
        with self.assertRaises(FastViewTeamError):
            player_row_form_text_state(0, 0, -1)
        with self.assertRaises(FastViewTeamError):
            player_row_goal_text_state(0, 0, 0x100000000)
        with self.assertRaises(FastViewTeamError):
            team_row_text_rect(0, 0, 7)

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
