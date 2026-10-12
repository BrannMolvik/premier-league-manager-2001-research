"""Source-backed editor staging/rollback: not live UI or original execution."""
import unittest

from original_human_user_name import OriginalHumanUserName, OriginalHumanUserNameError
from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_staff_lists import OriginalSupportStartLinkedLists
from support_staff import SupportStaffState, original_teamselect_support_slots


class SupportStartEditorProjectionTests(unittest.TestCase):
    def setUp(self):
        self.staff = tuple(
            SupportStaffState(n, 31 + i, 3) for i, n in enumerate((1, 2, 3, 4, 5, 13))
        )
        self.slots = original_teamselect_support_slots(self.staff)
        self.prior = OriginalSupportStartLinkedLists(
            current_staff=self.staff, global_staff=self.staff
        )
        self.user = OriginalHumanUserName(1, 0, "Old", "Manager")
        self.editor = OriginalSupportStartEditorProjection.open(
            original_user=self.user,
            source_slots=self.slots,
            prior_staff_lists=self.prior,
        )

    def test_source_six_staff_and_disabled_seventh_row(self):
        self.assertEqual(len(self.editor.rows), 7)
        self.assertEqual([r.parent for r in self.editor.rows], [0x183]*6 + [0x181])
        self.assertEqual(self.editor.rows[6].children, (0x181,)*4 + (0x180,))

    def test_cancel_rolls_back_name_and_all_staff_flags_and_list_identity(self):
        changed = self.editor.with_edited_name("Ada", "Lovelace")
        changed = changed.with_native_row_event(0, accepted_by_native_gate=True)
        cancel = changed.close(1)
        self.assertEqual(cancel.source_modal_result, 0)
        self.assertFalse(cancel.invoked_original_apply)
        self.assertIs(cancel.original_human_user_name, self.user)
        self.assertIs(cancel.staff_lists, self.prior)
        self.assertEqual(cancel.original_record_flag_bytes, (1,)*6 + (None,))
        self.assertEqual(self.editor.rows[0].parent, 0x183)

    def test_apply_uses_true_source_flag_inversion_and_staged_human_name(self):
        changed = self.editor.with_edited_name("Ada", "Lovelace")
        changed = changed.with_native_row_event(0, accepted_by_native_gate=True)
        apply = changed.close(2)
        self.assertEqual(apply.source_modal_result, 1)
        self.assertTrue(apply.invoked_original_apply)
        self.assertEqual(apply.original_human_user_name.source_manager_name(), "Ada Lovelace")
        self.assertEqual(apply.original_record_flag_bytes, (0,) + (1,)*6)
        self.assertIs(self.editor.original_user, self.user)
        self.assertIs(self.editor.prior_staff_lists, self.prior)
        self.assertIsNot(apply.staff_lists, self.prior)

    def test_rejected_native_input_and_disabled_empty_row_never_toggle(self):
        rejected = self.editor.with_native_row_event(0, accepted_by_native_gate=False)
        self.assertEqual(rejected.rows, self.editor.rows)
        with self.assertRaisesRegex(ValueError, "disabled empty"):
            self.editor.with_native_row_event(6, accepted_by_native_gate=True)
        self.assertEqual(
            self.editor.with_native_row_event(6, accepted_by_native_gate=False).rows,
            self.editor.rows,
        )
        changed = self.editor.with_native_row_event(0, accepted_by_native_gate=True)
        changed = changed.with_native_row_event(0, accepted_by_native_gate=True)
        self.assertEqual(changed.rows, self.editor.rows)

    def test_transaction_guards_unknown_users_invalid_rows_and_non_source_events(self):
        with self.assertRaises(TypeError):
            OriginalSupportStartEditorProjection.open(
                original_user=None,
                source_slots=self.slots,
                prior_staff_lists=self.prior,
            )
        with self.assertRaises(ValueError):
            OriginalSupportStartEditorProjection.open(
                original_user=self.user,
                source_slots=(),
                prior_staff_lists=self.prior,
            )
        with self.assertRaises(OriginalHumanUserNameError):
            self.editor.with_edited_name("A"*32, "Manager")
        for index in (-1, 7, None, True):
            with self.assertRaises(ValueError):
                self.editor.with_native_row_event(index, accepted_by_native_gate=True)
        with self.assertRaises(TypeError):
            self.editor.with_native_row_event(0, accepted_by_native_gate=1)
        for event in (0, 3, 18, True, None):
            with self.assertRaises(ValueError):
                self.editor.close(event)


if __name__ == "__main__":
    unittest.main()
