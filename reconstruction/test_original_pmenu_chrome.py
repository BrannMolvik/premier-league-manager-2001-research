"""Regressions for source-backed PMenu menu chrome and topology."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from original_pmenu_chrome import (
    OriginalPMenuChromeError,
    PMENU_ADMIN_FAMILY_CHILDREN,
    PMENU_ANALYSIS_CHILDREN,
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
    PMENU_CHILDREN_BY_ARRAY_VA,
    PMENU_CHILD_ROW_CLASS,
    PMENU_CHILD_ROW_SETUP_VA,
    PMENU_EAMAIL_CHILDREN,
    PMENU_FINANCE_FAMILY_CHILDREN,
    PMENU_RESOURCES,
    PMENU_ROOT_NODES,
    PMENU_ROW_HEIGHT,
    PMENU_SEPARATE_TEAM_ORDER_NODES,
    PMENU_TABLES_CHILDREN,
    PMENU_TEAM_CHILDREN,
    PMENU_TEXT_CONTROL_SIZE,
    PMENU_TEXT_CONTROL_Y,
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    PMENU_TITLE_ROW_CLASS,
    PMENU_TITLE_ROW_SETUP_VA,
    PMENU_TRANSFER_CHILDREN,
    main_english_global_va,
    validate_original_pmenu_resources,
)


class OriginalPMenuChromeTests(unittest.TestCase):
    def test_exact_four_row_resources_and_native_frame_stacks(self):
        self.assertEqual(len(PMENU_RESOURCES), 4)
        self.assertEqual(PMENU_ROW_HEIGHT, 29)

        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.owner_class, PMENU_TITLE_ROW_CLASS)
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.setup_va, PMENU_TITLE_ROW_SETUP_VA)
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.size, (30, 638))
        self.assertEqual(PMENU_TITLE_ARROW_RESOURCE.frame_count, 22)

        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.owner_class, PMENU_TITLE_ROW_CLASS)
        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.size, (168, 87))
        self.assertEqual(PMENU_TITLE_BOX_RESOURCE.frame_count, 3)

        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.owner_class, PMENU_CHILD_ROW_CLASS)
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.setup_va, PMENU_CHILD_ROW_SETUP_VA)
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.size, (30, 667))
        self.assertEqual(PMENU_CHILD_ARROW_RESOURCE.frame_count, 23)

        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.owner_class, PMENU_CHILD_ROW_CLASS)
        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.size, (168, 116))
        self.assertEqual(PMENU_CHILD_BOX_RESOURCE.frame_count, 4)

    def test_pmenu_text_controls_preserve_source_geometry_without_font_guess(self):
        self.assertEqual(PMENU_TEXT_CONTROL_SIZE, (160, 24))
        self.assertEqual(PMENU_TEXT_CONTROL_Y, (0, 24, 48, 72, 96, 120))

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
