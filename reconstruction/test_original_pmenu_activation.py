from __future__ import annotations

import unittest

from original_pmenu_activation import (
    PMENU_BASE_ROW_ACTION_PURECALL_VA,
    PMENU_CHILD_PARENT_OFFSET,
    PMENU_CHILD_ROW_ACTION_VA,
    PMENU_GENERIC_CONTROL_DISPATCH_VA,
    PMENU_GENERIC_PARENT_ACTION_CALL_VA,
    PMENU_MANAGEMENT_PANEL_FACTORY_VA,
    PMENU_NODE_CHILD_ARRAY_OFFSET,
    PMENU_NODE_MENU_ID_OFFSET,
    PMENU_NODE_STATE_FLAGS_OFFSET,
    PMENU_OWNER_REFRESH_VTABLE_OFFSET,
    PMENU_ROW_ACTION_VTABLE_OFFSET,
    PMENU_SOURCE_GUARD_BIT_1,
    PMENU_TITLE_ROW_ACTION_VA,
    PMENU_TREE_ORDINAL_TRAVERSAL_VA,
    OriginalPMenuActivationError,
    resolve_pmenu_row_action,
    source_pmenu_node,
)


class OriginalPMenuActivationTests(unittest.TestCase):
    def test_recovered_action_ownership_addresses_are_locked(self):
        self.assertEqual(PMENU_ROW_ACTION_VTABLE_OFFSET, 0x10)
        self.assertEqual(PMENU_BASE_ROW_ACTION_PURECALL_VA, 0x668766)
        self.assertEqual(PMENU_TITLE_ROW_ACTION_VA, 0x47AC60)
        self.assertEqual(PMENU_CHILD_ROW_ACTION_VA, 0x47AD60)
        self.assertEqual(PMENU_CHILD_PARENT_OFFSET, 0x24)
        self.assertEqual(PMENU_GENERIC_CONTROL_DISPATCH_VA, 0x64FE50)
        self.assertEqual(PMENU_GENERIC_PARENT_ACTION_CALL_VA, 0x64FF21)
        self.assertEqual(PMENU_TREE_ORDINAL_TRAVERSAL_VA, 0x60CA70)
        self.assertEqual(PMENU_MANAGEMENT_PANEL_FACTORY_VA, 0x47AEC0)
        self.assertEqual(PMENU_OWNER_REFRESH_VTABLE_OFFSET, 0xA8)
        self.assertEqual(PMENU_NODE_MENU_ID_OFFSET, 0x0C)
        self.assertEqual(PMENU_NODE_CHILD_ARRAY_OFFSET, 0x10)
        self.assertEqual(PMENU_NODE_STATE_FLAGS_OFFSET, 0x14)

    def test_title_action_sets_open_bit_and_closes_other_expandable_roots(self):
        action = resolve_pmenu_row_action("title", 3, 0)

        self.assertTrue(action.accepted)
        self.assertEqual(action.action_kind, "expand_root")
        self.assertEqual(action.source_flags_after, 1)
        self.assertTrue(action.clear_open_bit_on_other_expandable_roots)
        self.assertIsNone(action.panel_factory_va)
        self.assertIsNone(action.panel_factory_arguments)
        self.assertEqual(
            action.owner_refresh_vtable_offset,
            PMENU_OWNER_REFRESH_VTABLE_OFFSET,
        )

    def test_title_with_source_bit0_already_set_is_a_no_action(self):
        action = resolve_pmenu_row_action("title", 2, 1)

        self.assertFalse(action.accepted)
        self.assertEqual(action.action_kind, "no_action")
        self.assertEqual(action.source_flags_after, 1)
        self.assertEqual(action.rejection_reason, "source_bit0_already_set")

    def test_child_action_dispatches_exact_node_id_to_management_factory(self):
        action = resolve_pmenu_row_action("child", 0x25A, 0)

        self.assertTrue(action.accepted)
        self.assertEqual(action.action_kind, "open_panel")
        self.assertEqual(action.source_flags_after, 1)
        self.assertEqual(
            action.panel_factory_va,
            PMENU_MANAGEMENT_PANEL_FACTORY_VA,
        )
        self.assertEqual(action.panel_factory_arguments, (0x25A, 0))
        self.assertEqual(
            action.owner_refresh_vtable_offset,
            PMENU_OWNER_REFRESH_VTABLE_OFFSET,
        )

    def test_child_source_bit0_and_neutral_bit1_each_gate_dispatch(self):
        selected = resolve_pmenu_row_action("child", 0xCE, 1)
        self.assertFalse(selected.accepted)
        self.assertEqual(selected.rejection_reason, "source_bit0_already_set")

        guarded = resolve_pmenu_row_action(
            "child",
            0xCA,
            PMENU_SOURCE_GUARD_BIT_1,
        )
        self.assertFalse(guarded.accepted)
        self.assertEqual(guarded.rejection_reason, "source_bit1_set")
        self.assertIsNone(guarded.panel_factory_va)

    def test_duplicate_calendar_id_is_unambiguous_only_with_row_kind(self):
        root = source_pmenu_node("title", 0x259)
        child = source_pmenu_node("child", 0x259)

        self.assertEqual(root.menu_id, child.menu_id)
        self.assertIsNotNone(root.children_array_va)
        self.assertIsNone(child.children_array_va)

    def test_invalid_requests_fail_closed(self):
        cases = (
            ("other", 2, 0),
            ("title", 0xDEADBEEF, 0),
            ("child", 0xDEADBEEF, 0),
            ("child", "Squad", 0),
            ("child", 0xCE, -1),
            ("child", 0xCE, True),
        )
        for row_kind, menu_id, flags in cases:
            with self.subTest(row_kind=row_kind, menu_id=menu_id, flags=flags):
                with self.assertRaises(OriginalPMenuActivationError):
                    resolve_pmenu_row_action(row_kind, menu_id, flags)


if __name__ == "__main__":
    unittest.main()
