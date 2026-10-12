"""Source-backed editor staging/rollback: not live UI or original execution."""
import unittest

from original_human_user_name import OriginalHumanUserName, OriginalHumanUserNameError
from original_supportstart_editor_projection import OriginalSupportStartEditorProjection
from original_supportstart_staff_lists import (
    OriginalSupportStartLinkedLists,
    project_original_supportstart_first_human_modal_entry,
)
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

    def test_cancel_does_not_apply_and_preserves_supplied_modal_entry_snapshot(self):
        changed = self.editor.with_edited_name("Ada", "Lovelace")
        changed = changed.with_native_row_event(0, accepted_by_native_gate=True)
        cancel = changed.close(1)
        self.assertEqual(cancel.source_modal_result, 0)
        self.assertFalse(cancel.invoked_original_apply)
        self.assertIs(cancel.original_human_user_name, self.user)
        self.assertIs(cancel.staff_lists, self.prior)
        self.assertEqual(cancel.original_record_flag_bytes, (1,)*6 + (None,))
        self.assertEqual(self.editor.rows[0].parent, 0x183)

    def test_cancel_does_not_invent_undo_of_initial_staff_staging(self):
        # After original 0x4DA4F0 normal first-user stage: types 1..5
        # enter +0x5B8, type13 enters +0x5C4; +0x5D0/0x875600
        # remove their nodes BEFORE PSupportStart opens. This only
        # checks the bounded editor projection, not native teardown.
        staged = OriginalSupportStartLinkedLists(
            inactive_type_1_to_5=self.staff[:5],
            inactive_type_6_to_16=(self.staff[5],),
            current_staff=(),
            global_staff=(),
        )
        editor = OriginalSupportStartEditorProjection.open(
            original_user=self.user,
            source_slots=self.slots,
            prior_staff_lists=staged,
        )
        result = editor.with_edited_name("New", "Manager").close(1)
        self.assertEqual(result.source_modal_result, 0)
        self.assertFalse(result.invoked_original_apply)
        self.assertIs(result.staff_lists, staged)
        self.assertEqual(result.staff_lists.current_staff, ())
        self.assertEqual(result.staff_lists.global_staff, ())
        self.assertEqual(result.staff_lists.inactive_type_1_to_5, self.staff[:5])
        self.assertEqual(result.staff_lists.inactive_type_6_to_16, self.staff[5:])
        self.assertIs(result.original_human_user_name, self.user)

    def test_native_first_human_pre_modal_six_staff_list_order_and_cancel(self):
        fresh = OriginalSupportStartLinkedLists(
            current_staff=self.staff, global_staff=self.staff
        )
        staged = project_original_supportstart_first_human_modal_entry(
            source_slots=self.slots, before=fresh,
        )
        # Native 0x4DA4F0 visits 6..0: slot6 empty, then type13
        # into +0x5C4, and 5,4,3,2,1 into +0x5B8.
        self.assertEqual(
            tuple(s.staff_type for s in staged.inactive_type_1_to_5),
            (5, 4, 3, 2, 1),
        )
        self.assertIs(staged.inactive_type_6_to_16[0], self.staff[5])
        self.assertEqual(staged.current_staff, ())
        self.assertEqual(staged.global_staff, ())
        self.assertIs(fresh.current_staff[0], self.staff[0])
        editor = OriginalSupportStartEditorProjection.open(
            original_user=self.user, source_slots=self.slots,
            prior_staff_lists=staged,
        )
        # Native event1 skips 0x4D0830 Apply; no invented restoration
        # of the six pre-staging list nodes.
        canceled = editor.with_native_row_event(
            0, accepted_by_native_gate=True,
        ).close(1)
        self.assertIs(canceled.staff_lists, staged)
        self.assertIs(canceled.original_human_user_name, self.user)
        self.assertFalse(canceled.invoked_original_apply)

    def test_first_human_staging_requires_exact_source_order_and_unowned_lists(self):
        fresh = OriginalSupportStartLinkedLists(
            current_staff=self.staff, global_staff=self.staff
        )
        wrong_prior = (
            OriginalSupportStartLinkedLists(
                current_staff=self.staff[:5], global_staff=self.staff),
            OriginalSupportStartLinkedLists(
                current_staff=self.staff[::-1], global_staff=self.staff),
            OriginalSupportStartLinkedLists(
                current_staff=self.staff,
                inactive_type_1_to_5=(SupportStaffState(1, 99, 3),),
            ),
        )
        for prior in wrong_prior:
            with self.subTest(prior=prior):
                with self.assertRaises(ValueError):
                    project_original_supportstart_first_human_modal_entry(
                        source_slots=self.slots, before=prior,
                    )
        for slots in (self.slots[:6], self.slots[::-1], (None,) + self.slots[1:]):
            with self.subTest(slots=slots):
                with self.assertRaises(ValueError):
                    project_original_supportstart_first_human_modal_entry(
                        source_slots=slots, before=fresh,
                    )

    def test_initial_first_human_modal_factory_composes_staging_and_apply(self):
        source = OriginalSupportStartLinkedLists(
            current_staff=self.staff, global_staff=self.staff
        )
        modal = OriginalSupportStartEditorProjection.open_initial_first_human_modal(
            original_user=self.user,
            source_slots=self.slots,
            before_native_staging=source,
        )
        self.assertEqual(
            tuple(s.staff_type for s in modal.prior_staff_lists.inactive_type_1_to_5),
            (5, 4, 3, 2, 1),
        )
        self.assertEqual(modal.prior_staff_lists.current_staff, ())
        # Native untouched event2 Apply leaves all six inactive on
        # original source initial bit15=0, selected record flags=1.
        accepted = modal.close(2)
        self.assertEqual(accepted.source_modal_result, 1)
        self.assertTrue(accepted.invoked_original_apply)
        self.assertEqual(accepted.original_record_flag_bytes, (1,)*7)
        self.assertEqual(accepted.staff_lists, modal.prior_staff_lists)
        self.assertEqual(source.current_staff, self.staff)
        # Row0 native-gated toggle instead commits type1 active while
        # preserving the remaining descending inactive pointer order.
        switched = modal.with_native_row_event(
            0, accepted_by_native_gate=True,
        ).close(2)
        self.assertEqual(switched.original_record_flag_bytes[0], 0)
        self.assertEqual(switched.staff_lists.current_staff, (self.staff[0],))
        self.assertEqual(switched.staff_lists.global_staff, (self.staff[0],))
        self.assertEqual(
            tuple(x.staff_type for x in switched.staff_lists.inactive_type_1_to_5),
            (5, 4, 3, 2),
        )
        self.assertIs(accepted.original_human_user_name, self.user)

    def test_initial_first_human_modal_factory_does_not_accept_missing_user(self):
        source = OriginalSupportStartLinkedLists(current_staff=self.staff)
        with self.assertRaises(TypeError):
            OriginalSupportStartEditorProjection.open_initial_first_human_modal(
                original_user=None, source_slots=self.slots,
                before_native_staging=source,
            )

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

    def test_six_original_source_staff_role_labels_and_seventh_null(self):
        from pathlib import Path
        from ea_language_strings import EAStringTable, EAStringIndex
        source = Path(__file__).resolve().parents[1] / "original_assets" / "source"
        strings = EAStringTable.from_bytes((source / "English.str").read_bytes())
        indices = EAStringIndex.from_bytes(
            (source / "English.idx").read_bytes(), strings
        )
        self.assertEqual(self.editor.original_source_role_labels(strings, indices), (
            "ASSISTANT MANAGER", "STADIUM MANAGER",
            "YOUTH TEAM MANAGER", "BUSINESS CONSULTANT",
            "CHIEF SCOUT", "Physiotherapist", None,
        ))
        with self.assertRaises(TypeError):
            self.editor.original_source_role_labels(None, indices)
        with self.assertRaises(TypeError):
            self.editor.original_source_role_labels(strings, None)

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
