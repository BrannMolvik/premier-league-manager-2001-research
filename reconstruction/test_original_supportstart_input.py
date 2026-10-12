"""Source-routine tests; no original Win11 GUI or mouse-input claim."""
import unittest

from original_supportstart_input import (
    ORIGINAL_ROW_PARENT_VTABLE, ORIGINAL_ROW_CHILD_OFFSETS,
    ORIGINAL_ROW_CHILD_VTABLES, ORIGINAL_ROW_REGISTRATION_FLAGS,
    ORIGINAL_ROW_STATE_MASK, ORIGINAL_ROW_CHILD_INPUT_FLAG,
    ORIGINAL_ROW_CHILD_STATE_FLAG, OriginalSupportStartRowBitState,
    original_supportstart_row_refresh, original_supportstart_row_native_event,
    original_supportstart_fifth_child_native_rect,
    original_supportstart_teamselect_modal_entry,
    original_supportstart_source_dispatch_candidates,
    project_original_supportstart_row_native_dispatch,
    original_supportstart_teamselect_event_outcome,
    original_supportstart_fresh_native_row,
    SOURCE_ORIGINAL_CONTROL_INIT_DWORD,
)


class OriginalSupportStartInputTests(unittest.TestCase):
    def test_native_constructor_has_five_registered_children_with_split_flags(self):
        self.assertEqual(ORIGINAL_ROW_PARENT_VTABLE, 0x7c6780)
        self.assertEqual(ORIGINAL_ROW_CHILD_OFFSETS, (0x38, 0x3c, 0x40, 0x44, 0x48))
        self.assertEqual(ORIGINAL_ROW_CHILD_VTABLES, (
            0x7be9bc, 0x7c66c8, 0x7c66c8, 0x7be530, 0x7bff14))
        self.assertEqual(ORIGINAL_ROW_REGISTRATION_FLAGS, (0x33, 0x31, 0x31, 0x15, 0x15))
        self.assertEqual(tuple(bool(f & ORIGINAL_ROW_CHILD_STATE_FLAG)
                               for f in ORIGINAL_ROW_REGISTRATION_FLAGS),
                         (True, True, True, False, False))
        self.assertEqual(tuple(bool(f & ORIGINAL_ROW_CHILD_INPUT_FLAG)
                               for f in ORIGINAL_ROW_REGISTRATION_FLAGS),
                         (False, False, False, True, True))

    def test_original_refresh_byte_zero_sets_parent_and_first_three_only(self):
        row = OriginalSupportStartRowBitState(0x24, (0x55, 0x56, 0x57, 0x58, 0x59))
        result = original_supportstart_row_refresh(row, 0)
        self.assertEqual(result.parent, 0x8024)
        self.assertEqual(result.children, (0x8055, 0x8056, 0x8057, 0x58, 0x59))
        self.assertEqual(result.stored_staff_selection_byte_if_applied, 0)
        reverse = original_supportstart_row_refresh(result, 1)
        self.assertEqual(reverse, row)
        self.assertEqual(reverse.stored_staff_selection_byte_if_applied, 1)

    def test_accepted_original_input_toggles_and_rejected_input_is_noop(self):
        row = original_supportstart_row_refresh(
            OriginalSupportStartRowBitState(0x2, (0x2, 0x2, 0x2, 0x2, 0x2)), 1
        )
        self.assertEqual(row.stored_staff_selection_byte_if_applied, 1)
        self.assertIs(original_supportstart_row_native_event(row, False), row)
        clicked = original_supportstart_row_native_event(row, True)
        self.assertEqual(clicked.parent, 0x8002)
        self.assertEqual(clicked.children, (0x8002, 0x8002, 0x8002, 0x2, 0x2))
        self.assertEqual(clicked.stored_staff_selection_byte_if_applied, 0)
        self.assertEqual(original_supportstart_row_native_event(clicked, True), row)

    def test_fifth_text_control_geometry_from_native_rectangle_setup(self):
        self.assertEqual(original_supportstart_fifth_child_native_rect(0),
                         (621, 202, 95, 15))
        self.assertEqual(original_supportstart_fifth_child_native_rect(6),
                         (621, 442, 95, 15))
        for bad in (-1, 7, None, True, 1.0):
            with self.subTest(row=bad):
                with self.assertRaises(ValueError):
                    original_supportstart_fifth_child_native_rect(bad)


    def test_teamselect_modal_requires_native_accept_and_selected_bit(self):
        self.assertFalse(original_supportstart_teamselect_modal_entry(0, False))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8000, False))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8000, True))
        self.assertTrue(original_supportstart_teamselect_modal_entry(0x8002, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8022, True))
        self.assertFalse(original_supportstart_teamselect_modal_entry(0x8002, False))
        with self.assertRaises(TypeError):
            original_supportstart_teamselect_modal_entry(0x8000, 1)
        with self.assertRaises(ValueError):
            original_supportstart_teamselect_modal_entry(-1, True)


    def test_original_child_prefilter_does_not_fabricate_hit_acceptance(self):
        # Only fourth/fifth children are registered for native input.
        row = OriginalSupportStartRowBitState(
            0x2, (0x3, 0x3, 0x3, 0x3, 0x3)
        )
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), (3, 4))
        # 0x64F570 bit1, 0x64F7A0 bit2 and NOT bit0x10 are necessary.
        row = OriginalSupportStartRowBitState(
            0x2, (0x3, 0x3, 0x3, 0x13, 0x2)
        )
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), ())
        row = OriginalSupportStartRowBitState(
            0x2, (0x3, 0x3, 0x3, 0x3, 0x13)
        )
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), (3,))
        with self.assertRaises(TypeError):
            original_supportstart_source_dispatch_candidates(None)

    def test_original_parent_can_accept_row_even_when_no_child_is_eligible(self):
        # Parent 0x5D47A5 accepts before child virtual+0x6C loop;
        # accumulator EBP begins as parent result 1.
        row = OriginalSupportStartRowBitState(
            0x183, (0x183, 0x183, 0x183, 0x180, 0x180)
        )
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), ())
        result = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=True,
            observed_parent_acceptance=True, observed_child_acceptances=(),
        )
        self.assertTrue(result.parent_invoked)
        self.assertTrue(result.native_handler_accepted)
        self.assertEqual(result.source_post_virtual_gate_row.parent, 0x193)
        self.assertEqual(result.invoked_child_indices, ())
        applied = original_supportstart_row_native_event(
            row, accepted_by_native_gate=result.native_handler_accepted,
        )
        self.assertEqual(applied.stored_staff_selection_byte_if_applied, 0)
        self.assertEqual(result.source_after_row_bit15_toggle.parent, 0x8193)

    def test_parent_rejection_returns_without_eligible_child_dispatch(self):
        row = original_supportstart_fresh_native_row()
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), (3, 4))
        result = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=True,
            observed_parent_acceptance=False, observed_child_acceptances=(),
        )
        self.assertTrue(result.early_parent_reject)
        self.assertEqual(result.invoked_child_indices, ())
        self.assertFalse(result.native_handler_accepted)
        self.assertIs(original_supportstart_row_native_event(row, False), row)

    def test_no_second_event_argument_skips_parent_but_dispatches_children(self):
        row = original_supportstart_fresh_native_row()
        result = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=False,
            observed_parent_acceptance=None, observed_child_acceptances=(False, True),
        )
        self.assertFalse(result.parent_invoked)
        self.assertIsNone(result.parent_accepted)
        self.assertEqual(result.invoked_child_indices, (3, 4))
        self.assertTrue(result.native_handler_accepted)
        self.assertEqual(result.source_post_virtual_gate_row.parent, 0x183)
        self.assertEqual(result.source_post_virtual_gate_row.children[3], 0x183)
        self.assertEqual(result.source_post_virtual_gate_row.children[4], 0x193)
        self.assertEqual(result.source_after_row_bit15_toggle.parent, 0x8183)
        result2 = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=True,
            observed_parent_acceptance=True, observed_child_acceptances=(False, False),
        )
        self.assertTrue(result2.native_handler_accepted)
        self.assertEqual(result2.invoked_child_indices, (3, 4))
        self.assertEqual(result2.observed_child_acceptances, (False, False))

    def test_source_empty_row_and_closed_child_flags_cannot_invent_events(self):
        from original_supportstart_input import original_supportstart_empty_row_after_refresh
        empty = original_supportstart_empty_row_after_refresh(original_supportstart_fresh_native_row())
        result = project_original_supportstart_row_native_dispatch(
            empty, native_second_argument_present=False,
            observed_parent_acceptance=None, observed_child_acceptances=(False,),
        )
        # Empty refresh leaves fourth child bit0 set but clears bit1:
        # vft+0x6C is invoked and necessarily returns zero.
        self.assertEqual(result.invoked_child_indices, (3,))
        self.assertFalse(result.native_handler_accepted)
        with self.assertRaises(ValueError):
            project_original_supportstart_row_native_dispatch(
                empty, native_second_argument_present=True,
                observed_parent_acceptance=True, observed_child_acceptances=(),
            )
        closed = OriginalSupportStartRowBitState(
            0x183, (0x183, 0x183, 0x183, 0x183, 0x193)
        )
        # Both child virtuals are INVOKED if their bit0 is set, but
        # source 0x64F7A0 rejects the final child whose bit0x10 is set.
        with self.assertRaises(ValueError):
            project_original_supportstart_row_native_dispatch(
                closed, native_second_argument_present=False,
                observed_parent_acceptance=None, observed_child_acceptances=(False, True),
            )
        legal = project_original_supportstart_row_native_dispatch(
            closed, native_second_argument_present=False,
            observed_parent_acceptance=None, observed_child_acceptances=(True, False),
        )
        self.assertEqual(legal.invoked_child_indices, (3, 4))
        self.assertTrue(legal.native_handler_accepted)

    def test_native_dispatch_observation_requires_exact_callback_arity(self):
        row = original_supportstart_fresh_native_row()
        for kw in (
            dict(native_second_argument_present=1,
                 observed_parent_acceptance=None, observed_child_acceptances=(False, False)),
            dict(native_second_argument_present=True,
                 observed_parent_acceptance=None, observed_child_acceptances=(False, False)),
            dict(native_second_argument_present=False,
                 observed_parent_acceptance=None, observed_child_acceptances=(0, False)),
        ):
            with self.subTest(kw=kw), self.assertRaises(TypeError):
                project_original_supportstart_row_native_dispatch(row, **kw)
        for kw in (
            dict(native_second_argument_present=False,
                 observed_parent_acceptance=False, observed_child_acceptances=(False, False)),
            dict(native_second_argument_present=False,
                 observed_parent_acceptance=None, observed_child_acceptances=(True,)),
            dict(native_second_argument_present=True,
                 observed_parent_acceptance=False, observed_child_acceptances=(False, False)),
        ):
            with self.subTest(kw=kw), self.assertRaises(ValueError):
                project_original_supportstart_row_native_dispatch(row, **kw)

    def test_native_teamselect_dialog_cancel_still_returns_handled_event(self):
        # 0x4D922C returns EBX from 0x64F960, overwriting EAX from 0x450BB0.
        cancel = original_supportstart_teamselect_event_outcome(True, 0x8002, 0)
        apply = original_supportstart_teamselect_event_outcome(True, 0x8002, 1)
        self.assertTrue(cancel.modal_called)
        self.assertEqual(cancel.native_handler_return, 1)
        self.assertEqual(cancel.modal_result_byte, 0)
        self.assertEqual(apply.native_handler_return, 1)
        self.assertEqual(apply.modal_result_byte, 1)
        accepted_without_modal = original_supportstart_teamselect_event_outcome(
            True, 0x2, None
        )
        self.assertEqual(accepted_without_modal.native_handler_return, 1)
        self.assertFalse(accepted_without_modal.modal_called)
        denied = original_supportstart_teamselect_event_outcome(False, 0x8002, None)
        self.assertEqual(denied.native_handler_return, 0)
        self.assertFalse(denied.modal_called)
        with self.assertRaises(ValueError):
            original_supportstart_teamselect_event_outcome(True, 0x8002, None)
        with self.assertRaises(ValueError):
            original_supportstart_teamselect_event_outcome(True, 0x8022, 0)
        with self.assertRaises(ValueError):
            original_supportstart_teamselect_event_outcome(False, 0x8002, 0)
        with self.assertRaises(TypeError):
            original_supportstart_teamselect_event_outcome(1, 0x8002, None)


    def test_constructor_all_six_native_control_dwords_start_0x183(self):
        self.assertEqual(SOURCE_ORIGINAL_CONTROL_INIT_DWORD, 0x183)
        row = original_supportstart_fresh_native_row()
        self.assertEqual(row.parent, 0x183)
        self.assertEqual(row.children, (0x183,) * 5)
        self.assertEqual(original_supportstart_source_dispatch_candidates(row), (3, 4))
        self.assertEqual(row.stored_staff_selection_byte_if_applied, 1)
        toggled = original_supportstart_row_native_event(row, True)
        self.assertEqual(toggled.parent, 0x8183)
        self.assertEqual(toggled.children, (0x8183, 0x8183, 0x8183, 0x183, 0x183))
        self.assertEqual(toggled.stored_staff_selection_byte_if_applied, 0)


    def test_empty_source_row_disables_fifth_text_and_all_six_native_flags(self):
        from original_supportstart_input import (
            original_supportstart_empty_row_after_refresh,
            original_supportstart_initial_seven_rows,
        )
        fresh = original_supportstart_fresh_native_row()
        empty = original_supportstart_empty_row_after_refresh(fresh)
        self.assertEqual(empty.parent, 0x181)
        self.assertEqual(empty.children, (0x181, 0x181, 0x181, 0x181, 0x180))
        self.assertEqual(original_supportstart_source_dispatch_candidates(empty), ())
        self.assertIs(original_supportstart_row_native_event(empty, False), empty)
        # The normal native handler must never report accepted input for a
        # disabled source row, but the lower-level accepted-event function
        # is intentionally not a mouse-acceptance predictor.
        from support_staff import SupportStaffState, original_teamselect_support_slots
        staff = tuple(SupportStaffState(n, 32, 3) for n in (1, 2, 3, 4, 5, 13))
        rows = original_supportstart_initial_seven_rows(
            original_teamselect_support_slots(staff)
        )
        self.assertEqual(len(rows), 7)
        self.assertEqual([row.parent for row in rows], [0x183]*6 + [0x181])
        self.assertEqual(rows[6], empty)

    def test_zero_staff_seven_empty_rows_disable_without_reading_unknown_flags(self):
        from original_supportstart_input import original_supportstart_initial_seven_rows
        from support_staff import original_teamselect_support_slots
        rows = original_supportstart_initial_seven_rows(
            original_teamselect_support_slots(())
        )
        self.assertEqual([r.parent for r in rows], [0x181]*7)
        self.assertEqual([r.children[-1] for r in rows], [0x180]*7)
        with self.assertRaises(ValueError):
            original_supportstart_initial_seven_rows(())
        with self.assertRaises(ValueError):
            original_supportstart_initial_seven_rows([])


    def test_original_native_teamselect_control_to_private_staff_record_stride(self):
        from original_supportstart_input import (
            original_teamselect_native_private_staff_record_address,
        )
        owner = 0x00400000
        first_control = owner + 0x2EE4
        self.assertEqual(
            original_teamselect_native_private_staff_record_address(
                teamselect_owner_va=owner,
                pressed_control_va=first_control,
                source_group_start=0, source_group_end=0,
            ), owner - 0x310
        )
        for i in range(7):
            with self.subTest(row=i):
                self.assertEqual(
                    original_teamselect_native_private_staff_record_address(
                        teamselect_owner_va=owner,
                        pressed_control_va=first_control + 0x40*i,
                        source_group_start=0, source_group_end=0,
                    ), owner - 0x310 + 0x30*i
                )
        self.assertEqual(
            original_teamselect_native_private_staff_record_address(
                teamselect_owner_va=owner,
                pressed_control_va=first_control + 0x40,
                source_group_start=2, source_group_end=3,
            ), owner - 0x310 + 0x30*25
        )

    def test_teamselect_native_private_record_rejects_unqualified_controls(self):
        from original_supportstart_input import (
            original_teamselect_native_private_staff_record_address as resolve
        )
        o = 0x400000
        for c in (o+0x2EE3, o+0x2EE5, o+0x2EE4+63):
            with self.subTest(control=c):
                with self.assertRaises(ValueError):
                    resolve(teamselect_owner_va=o,pressed_control_va=c,
                            source_group_start=0,source_group_end=0)
        with self.assertRaises(ValueError):
            resolve(teamselect_owner_va=o,pressed_control_va=o+0x2EE4,
                    source_group_start=3,source_group_end=2)
        with self.assertRaises(ValueError):
            resolve(teamselect_owner_va=True,pressed_control_va=o+0x2EE4,
                    source_group_start=0,source_group_end=0)

    def test_empty_unknown_source_flags_are_not_invented(self):
        row = OriginalSupportStartRowBitState(0, (0, 0, 0, 0, 0))
        for invalid in (None, True, -1, 256, 1.0):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    original_supportstart_row_refresh(row, invalid)

    def test_input_requires_explicit_gate_and_unsigned_native_dwords(self):
        row = OriginalSupportStartRowBitState(0, (0, 0, 0, 0, 0))
        for gate in (None, 0, 1, "clicked"):
            with self.subTest(gate=gate):
                with self.assertRaises(TypeError):
                    original_supportstart_row_native_event(row, gate)
        for bad in (True, -1, 0x100000000):
            with self.subTest(state=bad):
                with self.assertRaises(ValueError):
                    OriginalSupportStartRowBitState(bad, (0, 0, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
