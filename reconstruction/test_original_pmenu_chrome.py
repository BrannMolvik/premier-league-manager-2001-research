"""Regressions for source-backed PMenu menu chrome and topology."""
from pathlib import Path
import tempfile
import unittest
from original_pmenu_chrome import (
    OriginalPMenuChromeError,
    PMENU_ADMIN_FAMILY_CHILDREN,
    PMENU_ANALYSIS_CHILDREN,
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
    PMENU_CHILDREN_BY_ARRAY_VA,
    PMENU_CHILD_ROW_CLASS,
    PMENU_CHILD_ROW_SETUP_VA,
    PMENU_DIRECT_259_CHILDREN,
    PMENU_EAMAIL_CHILDREN,
    PMENU_FINANCE_FAMILY_CHILDREN,
    PMENU_RESOURCES,
    PMENU_ROOT_NODES,
    PMENU_FONT_ATLAS_SIZE,
    PMENU_FONT_NATIVE_LINE_HEIGHT,
    PMENU_FONT_SOURCE_PATH,
    PMENU_CHILD_TEXT_LAYOUT,
    PMENU_TITLE_TEXT_LAYOUT,
    PMENU_ROW_COLOR_COMPONENTS,
    PMENU_ROW_HEIGHT,
    PMENU_LIST_OBJECT_OFFSET,
    PMENU_LIST_ROW_CAPACITY,
    PMENU_LIST_SCREEN_ORIGIN,
    PMENU_LIST_SIZE,
    PMENU_LIST_SETUP_ARGUMENTS,
    PMENU_FRESH_SELECTED_CHILD_ID,
    PMENU_FRESH_SELECTED_ROOT_ID,
    PMENU_NODE_CHILD_ARRAY_OFFSET,
    PMENU_NODE_SELECTED_OR_EXPANDED_BIT,
    PMENU_NODE_STATE_FLAGS_OFFSET,
    PMENU_ROW_FACTORY_VA,
    PMENU_OWNER_CONSTRUCTION_VA,
    PMENU_OWNER_LAYOUT_CALL_VA,
    PMENU_TREE_ORDINAL_TRAVERSAL_VA,
    PMENU_VISIBLE_ROW_LAYOUT_VA,
    PMENU_DIRECT_RESOURCE_BINDING_IN_OWN_METHODS,
    PMENU_SEPARATE_TEAM_ORDER_NODES,
    PMENU_SYSTEM_CHILDREN,
    PMENU_TABLES_CHILDREN,
    PMENU_TEAM_CHILDREN,
    PMENU_TEXT_CONTROL_SIZE,
    PMENU_TEXT_CONTROL_Y,
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    PMENU_TITLE_ROW_CLASS,
    PMENU_TITLE_ROW_SETUP_VA,
    PMENU_TRANSFER_CHILDREN,
    PMENU_STATE_BIT_1,
    PMENU_STATE_BIT_3,
    PMENU_STATE_BIT_15,
    pmenu_arrow_state_from_bits,
    pmenu_arrow_transition_frame,
    pmenu_arrow_update,
    pmenu_child_arrow_frame_count,
    pmenu_child_arrow_source_row,
    pmenu_title_arrow_frame_count,
    pmenu_title_arrow_source_row,
    main_english_global_va,
    pmenu_background_row_index,
    pmenu_background_source_y,
    pmenu_static_row_state,
    validate_original_pmenu_font,
    validate_original_pmenu_row_fonts,
    validate_original_pmenu_resources,
)


class OriginalPMenuChromeTests(unittest.TestCase):
    def test_exact_four_row_resources_and_native_frame_stacks(self):
        self.assertEqual(len(PMENU_RESOURCES), 4)
        self.assertEqual(PMENU_ROW_HEIGHT, 29)

        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.owner_class, PMENU_TITLE_ROW_CLASS)
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.setup_va, PMENU_TITLE_ROW_SETUP_VA)
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.size, (30, 638))
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.frame_height, 58)
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.frame_count, 11)

        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.owner_class, PMENU_TITLE_ROW_CLASS)
        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.size, (168, 87))
        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.frame_count, 3)

        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.owner_class, PMENU_CHILD_ROW_CLASS)
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.setup_va, PMENU_CHILD_ROW_SETUP_VA)
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.size, (30, 667))
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.frame_height, 29)
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.frame_count, 23)

        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.owner_class, PMENU_CHILD_ROW_CLASS)
        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.size, (168, 116))
        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.frame_count, 4)

    def test_pmenu_setup_preserves_raw_list_geometry_and_no_direct_resource_binding(self):
        self.assertEqual(PMENU_LIST_OBJECT_OFFSET, 0x68)
        self.assertEqual(
            PMENU_LIST_SETUP_ARGUMENTS,
            (0, 0, 201, 504, 16, 29, 0, 0, 0),
        )
        self.assertEqual(PMENU_LIST_SIZE, (201, 504))
        self.assertEqual(PMENU_LIST_SCREEN_ORIGIN, (599, 96))
        self.assertEqual(PMENU_LIST_ROW_CAPACITY, 16)
        self.assertEqual(PMENU_OWNER_CONSTRUCTION_VA, 0x4C2FB0)
        self.assertEqual(PMENU_OWNER_LAYOUT_CALL_VA, 0x4C301F)
        self.assertEqual(PMENU_VISIBLE_ROW_LAYOUT_VA, 0x482300)
        self.assertEqual(PMENU_ROW_FACTORY_VA, 0x4823A0)
        self.assertEqual(PMENU_TREE_ORDINAL_TRAVERSAL_VA, 0x60CA70)
        self.assertEqual(PMENU_NODE_CHILD_ARRAY_OFFSET, 0x10)
        self.assertEqual(PMENU_NODE_STATE_FLAGS_OFFSET, 0x14)
        self.assertEqual(PMENU_NODE_SELECTED_OR_EXPANDED_BIT, 1)
        self.assertEqual((PMENU_FRESH_SELECTED_ROOT_ID, PMENU_FRESH_SELECTED_CHILD_ID), (2, 0xCE))
        self.assertFalse(PMENU_DIRECT_RESOURCE_BINDING_IN_OWN_METHODS)

    def test_pmenu_text_controls_preserve_source_geometry_without_font_guess(self):
        self.assertEqual(PMENU_TEXT_CONTROL_SIZE, (160, 24))
        self.assertEqual(PMENU_TEXT_CONTROL_Y, (0, 24, 48, 72, 96, 120))

    def test_exact_imported_pmenu_font_matches_native_loader_binding(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        self.assertTrue((source_root / PMENU_FONT_SOURCE_PATH).is_file())
        font = validate_original_pmenu_font(source_root)
        self.assertEqual((font.atlas_width, font.atlas_height), PMENU_FONT_ATLAS_SIZE)
        self.assertEqual(font.native_line_height(), PMENU_FONT_NATIVE_LINE_HEIGHT)

    def test_concrete_row_fonts_and_label_geometry_match_native_draw_path(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        validated = validate_original_pmenu_row_fonts(source_root)
        self.assertEqual(
            tuple(layout for layout, _font in validated),
            (PMENU_TITLE_TEXT_LAYOUT, PMENU_CHILD_TEXT_LAYOUT),
        )
        self.assertEqual(PMENU_TITLE_TEXT_LAYOUT.font_object_va, 0x8A3550)
        self.assertEqual(PMENU_CHILD_TEXT_LAYOUT.font_object_va, 0x8CAB80)
        self.assertEqual(PMENU_TITLE_TEXT_LAYOUT.control_rect, (30, 0, 168, 29))
        self.assertEqual(PMENU_CHILD_TEXT_LAYOUT.control_rect, (30, 0, 168, 29))
        self.assertEqual(PMENU_TITLE_TEXT_LAYOUT.line_origin, (30, 1))
        self.assertEqual(PMENU_CHILD_TEXT_LAYOUT.line_origin, (30, 17))
        self.assertEqual(PMENU_TITLE_TEXT_LAYOUT.clip_rect, (30, 0, 198, 29))
        self.assertEqual(PMENU_CHILD_TEXT_LAYOUT.clip_rect, (30, 0, 198, 29))

    def test_row_setup_uses_exact_black_and_white_component_triples(self):
        self.assertEqual(PMENU_ROW_COLOR_COMPONENTS, ((0, 0, 0), (255, 255, 255)))

    def test_row_factory_state_propagation_closes_static_color_choice(self):
        title = pmenu_static_row_state("title", selected=False)
        selected_title = pmenu_static_row_state("title", selected=True)
        child = pmenu_static_row_state("child", selected=False)
        selected_child = pmenu_static_row_state("child", selected=True)
        self.assertEqual((title.arrow_state_bits, title.background_state_bits), (0x2, 0x8002))
        self.assertEqual(
            (selected_title.arrow_state_bits, selected_title.background_state_bits),
            (0x8002, 0x8002),
        )
        self.assertEqual(title.text_color_16, 0xFFFF)
        self.assertEqual((child.arrow_state_bits, child.background_state_bits), (0x2, 0x2))
        self.assertEqual(child.text_color_16, 0x0000)
        self.assertEqual(
            (selected_child.arrow_state_bits, selected_child.background_state_bits),
            (0x8002, 0x8002),
        )
        self.assertEqual(selected_child.text_color_16, 0xFFFF)
        with self.assertRaises(OriginalPMenuChromeError):
            pmenu_static_row_state("other", selected=False)

    def test_background_toggle_state_to_source_row_is_exact(self):
        self.assertEqual(pmenu_background_row_index(0), 3)
        self.assertEqual(pmenu_background_source_y(0), 87)
        self.assertEqual(pmenu_background_row_index(0x2), 0)
        self.assertEqual(pmenu_background_source_y(0x2), 0)
        self.assertEqual(pmenu_background_row_index(0x2 | 0x8), 1)
        self.assertEqual(pmenu_background_source_y(0x2 | 0x8), 29)
        self.assertEqual(pmenu_background_row_index(0x2 | 0x8000), 2)
        self.assertEqual(pmenu_background_source_y(0x2 | 0x8000), 58)
        # The 0x8000 branch has source precedence over the 0x8 branch.
        self.assertEqual(pmenu_background_row_index(0x2 | 0x8 | 0x8000), 2)
        for bad in (True, -1, 1.5, "2"):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalPMenuChromeError):
                    pmenu_background_row_index(bad)

    def test_arrow_state_selector_uses_exact_neutral_bit_precedence(self):
        self.assertEqual(pmenu_arrow_state_from_bits(0), 2)
        self.assertEqual(pmenu_arrow_state_from_bits(PMENU_STATE_BIT_1), 0)
        self.assertEqual(
            pmenu_arrow_state_from_bits(PMENU_STATE_BIT_1 | PMENU_STATE_BIT_15),
            1,
        )
        self.assertEqual(
            pmenu_arrow_state_from_bits(
                PMENU_STATE_BIT_1 | PMENU_STATE_BIT_3 | PMENU_STATE_BIT_15
            ),
            1,
        )

    def test_child_arrow_partitions_exact_23_rows_as_11_11_1(self):
        self.assertEqual(
            [pmenu_child_arrow_frame_count(state) for state in (0, 1, 2)],
            [11, 11, 1],
        )
        self.assertEqual(pmenu_child_arrow_source_row(0, 0), 0)
        self.assertEqual(pmenu_child_arrow_source_row(0, 10), 10)
        self.assertEqual(pmenu_child_arrow_source_row(1, 0), 11)
        self.assertEqual(pmenu_child_arrow_source_row(1, 10), 21)
        self.assertEqual(pmenu_child_arrow_source_row(2, 0), 22)

    def test_title_arrow_uses_eleven_58px_frames_and_custom_state_offsets(self):
        self.assertEqual(
            [pmenu_title_arrow_frame_count(state) for state in (0, 1, 2)],
            [11, 1, 1],
        )
        self.assertEqual(pmenu_title_arrow_source_row(0, 0), 0)
        self.assertEqual(pmenu_title_arrow_source_row(0, 10), 10)
        self.assertEqual(pmenu_title_arrow_source_row(1, 0), 10)
        self.assertEqual(pmenu_title_arrow_source_row(2, 0), 0)
        self.assertEqual(
            PMENU_TITLE_ARROW_RESOURCE.frame_count
            * PMENU_TITLE_ARROW_RESOURCE.frame_height,
            PMENU_TITLE_ARROW_RESOURCE.size[1],
        )

    def test_arrow_state_transition_preserves_source_fraction_by_integer_division(self):
        self.assertEqual(
            pmenu_arrow_transition_frame(0, 10, 1, title=False),
            10,
        )
        self.assertEqual(
            pmenu_arrow_transition_frame(1, 10, 2, title=False),
            0,
        )
        self.assertEqual(
            pmenu_arrow_transition_frame(0, 10, 1, title=True),
            0,
        )

    def test_arrow_tick_advances_or_retreats_without_semantic_state_names(self):
        bits = PMENU_STATE_BIT_1 | PMENU_STATE_BIT_3
        self.assertEqual(pmenu_arrow_update(0, 0, bits, title=False), (0, 1))
        self.assertEqual(
            pmenu_arrow_update(0, 10, PMENU_STATE_BIT_1, title=False),
            (0, 9),
        )
        # The transition preserves frame 10, then this same native tick
        # sees bit 0x8 clear and retreats once to frame 9.
        self.assertEqual(
            pmenu_arrow_update(
                0,
                10,
                PMENU_STATE_BIT_1 | PMENU_STATE_BIT_15,
                title=False,
            ),
            (1, 9),
        )
        self.assertEqual(
            pmenu_arrow_update(
                0,
                10,
                PMENU_STATE_BIT_1 | PMENU_STATE_BIT_15,
                title=True,
            ),
            (1, 0),
        )

    def test_arrow_helpers_fail_closed_on_invalid_state_or_frame(self):
        for call in (
            lambda: pmenu_child_arrow_frame_count(3),
            lambda: pmenu_title_arrow_frame_count(-1),
            lambda: pmenu_child_arrow_source_row(2, 1),
            lambda: pmenu_title_arrow_source_row(1, 1),
            lambda: pmenu_arrow_transition_frame(0, 11, 1, title=False),
            lambda: pmenu_arrow_update(0, 11, PMENU_STATE_BIT_1, title=False),
        ):
            with self.assertRaises(OriginalPMenuChromeError):
                call()

    def test_root_order_and_child_arrays_are_literal_source_topology(self):
        self.assertEqual(
            tuple(node.menu_id for node in PMENU_ROOT_NODES),
            (2, 3, 0x259, 6, 7, 4, 5, 1, 8),
        )
        self.assertEqual(
            tuple(node.children_array_va for node in PMENU_ROOT_NODES),
            (0x9479C8, 0x947968, 0x947728, 0x947830, 0x9477D0,
             0x9478D8, 0x947878, 0x947A70, 0x947770),
        )
        self.assertEqual(
            set(PMENU_CHILDREN_BY_ARRAY_VA),
            {node.children_array_va for node in PMENU_ROOT_NODES},
        )

    def test_all_root_labels_are_exact_loader_correlations(self):
        self.assertEqual(
            [node.require_original_text() for node in PMENU_ROOT_NODES],
            [
                "Team",
                "Transfers",
                "Calendar",
                "TABLES",
                "Analysis",
                "ADMIN",
                "ACCOUNTS",
                "EAMail",
                "GAME OPTIONS",
            ],
        )
        for node in PMENU_ROOT_NODES:
            with self.subTest(menu_id=node.menu_id):
                self.assertEqual(
                    node.label_global_va,
                    main_english_global_va(node.english_index),
                )

    def test_all_modeled_child_labels_are_exact_loader_correlations(self):
        self.assertEqual(
            [node.require_original_text() for node in PMENU_TEAM_CHILDREN],
            ["Squad", "Stats", "Indiv. Orders", "Team Orders", "Training", "Youth Team"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_TRANSFER_CHILDREN],
            ["Transfer List", "Scouts", "Player/Club Search"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_DIRECT_259_CHILDREN],
            ["Calendar", "League Fixtures"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_TABLES_CHILDREN],
            ["League Tables", "Cup Tables"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_ANALYSIS_CHILDREN],
            ["Charts", "RATINGS", "Trophy Cupboard"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_ADMIN_FAMILY_CHILDREN],
            ["Overview", "Support Staff", "Stadium", "Development", "Maintenance"],
        )
        self.assertEqual(
            [node.require_original_text() for node in PMENU_FINANCE_FAMILY_CHILDREN],
            ["Cash Flow", "Tickets", "Contracts"],
        )
        self.assertEqual(PMENU_EAMAIL_CHILDREN[0].require_original_text(), "EAMail")
        self.assertEqual(
            [node.require_original_text() for node in PMENU_SYSTEM_CHILDREN],
            ["SAVE GAME", "SETTINGS", "RETURN TO MAIN MENU"],
        )
        for children in PMENU_CHILDREN_BY_ARRAY_VA.values():
            for node in children:
                with self.subTest(menu_id=node.menu_id):
                    self.assertEqual(
                        node.label_global_va,
                        main_english_global_va(node.english_index),
                    )

    def test_separate_team_order_array_is_not_misrepresented_as_root_children(self):
        self.assertEqual(
            [node.require_original_text() for node in PMENU_SEPARATE_TEAM_ORDER_NODES],
            ["Formation", "Stats", "Ind Orders", "Specific Roles", "Team Orders"],
        )
        ids = {node.menu_id for children in PMENU_CHILDREN_BY_ARRAY_VA.values()
               for node in children}
        self.assertFalse({node.menu_id for node in PMENU_SEPARATE_TEAM_ORDER_NODES} <= ids)

    def test_resource_validation_checks_bytes_hash_and_geometry(self):
        class Header:
            width = 30
            height = 638

        resource = PMENU_TITLE_ARROW_RESOURCE
        data = b"x" * resource.byte_size
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for item in PMENU_RESOURCES:
                path = root / item.source_path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"x" * item.byte_size)

            # Hashes intentionally do not match synthetic bytes, proving the
            # validator fails before any unverified asset can be accepted.
            with self.assertRaisesRegex(
                OriginalPMenuChromeError, "checksum mismatch"
            ):
                validate_original_pmenu_resources(root)

    def test_imported_pmenu_resources_match_the_source_contract(self):
        source_root = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        self.assertEqual(
            validate_original_pmenu_resources(source_root),
            PMENU_RESOURCES,
        )

    def test_main_english_global_mapping_is_exact_and_fails_closed(self):
        self.assertEqual(main_english_global_va(44), 0x984748)
        self.assertEqual(main_english_global_va(2392), 0x982298)
        self.assertEqual(main_english_global_va(2522), 0x982090)
        for bad in (True, -1, 1.5, "44", 100):
            with self.subTest(bad=bad):
                with self.assertRaises(OriginalPMenuChromeError):
                    main_english_global_va(bad)


if __name__ == "__main__":
    unittest.main()
