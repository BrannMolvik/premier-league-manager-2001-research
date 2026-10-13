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

    def test_native_pressed_bit_blocks_repeated_parent_accept_without_release(self):
        row = original_supportstart_fresh_native_row()
        accepted = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=True,
            observed_parent_acceptance=True,
            observed_child_acceptances=(False, False),
        )
        pressed = accepted.source_after_row_bit15_toggle
        self.assertEqual(pressed.parent, 0x8193)
        # 0x64F7B8 source bit0x10 rejects another press until a real
        # 0x64F860 / vft+0x1C(0) release is observed.
        with self.assertRaises(ValueError):
            project_original_supportstart_row_native_dispatch(
                pressed, native_second_argument_present=True,
                observed_parent_acceptance=True, observed_child_acceptances=(False, False),
            )
        rejected = project_original_supportstart_row_native_dispatch(
            pressed, native_second_argument_present=True,
            observed_parent_acceptance=False, observed_child_acceptances=(),
        )
        self.assertTrue(rejected.early_parent_reject)
        self.assertFalse(rejected.native_handler_accepted)

    def test_native_selector_identity_is_not_inferred_from_equal_flags(self):
        row = original_supportstart_fresh_native_row()
        bound = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=False,
            observed_parent_acceptance=None,
            observed_child_acceptances=(False, False),
            source_row_index=3,
        )
        self.assertEqual(bound.source_row_index, 3)
        unbound = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=False,
            observed_parent_acceptance=None,
            observed_child_acceptances=(False, False),
        )
        self.assertIsNone(unbound.source_row_index)
        for index in (True, -1, 7, 1.0):
            with self.subTest(index=index), self.assertRaises(ValueError):
                project_original_supportstart_row_native_dispatch(
                    row, native_second_argument_present=False,
                    observed_parent_acceptance=None,
                    observed_child_acceptances=(False, False),
                    source_row_index=index,
                )

    def test_true_native_seven_row_callback_identity_and_default_actions(self):
        from original_supportstart_input import (
            original_supportstart_row_callback_contract,
            original_supportstart_native_modal_event_dispatch_va,
        )
        identities = tuple(
            original_supportstart_row_callback_contract(i) for i in range(7)
        )
        self.assertEqual(tuple(r.original_native_control_event_id for r in identities),
                         (8, 9, 10, 11, 12, 13, 14))
        self.assertEqual(tuple(r.source_modal_selector_offset for r in identities),
                         tuple(0x2224 + 0x4C*i for i in range(7)))
        self.assertEqual({r.source_parent_input_callback_va for r in identities},
                         {0x42DE00})
        self.assertEqual({r.source_callback_acceptance_result for r in identities},
                         {1})
        self.assertEqual({r.original_parent_dispatch_va for r in identities},
                         {0x4D0641})
        self.assertEqual(tuple(original_supportstart_native_modal_event_dispatch_va(
            r.original_native_control_event_id) for r in identities),
            (0x4D0641,)*7)

    def test_modal_native_cancel_apply_remain_distinct_from_row_control_ids(self):
        from original_supportstart_input import (
            original_supportstart_native_modal_event_dispatch_va as dispatch,
        )
        self.assertEqual(dispatch(1), 0x4D061F)
        self.assertEqual(dispatch(2), 0x4D0606)
        self.assertEqual(dispatch(3), 0x4D0631)
        self.assertEqual(dispatch(4), 0x4D0641)
        self.assertEqual(dispatch(17), 0x4D0641)
        self.assertEqual([dispatch(n) for n in (18,19,20)], [0x4D063A]*3)
        for event in (0,21,-1,True,1.0,None):
            with self.subTest(event=event), self.assertRaises(ValueError):
                dispatch(event)
        from original_supportstart_input import original_supportstart_row_callback_contract
        for index in (-1,7,True,None,1.0):
            with self.subTest(index=index), self.assertRaises(ValueError):
                original_supportstart_row_callback_contract(index)

    def test_original_release_visits_parent_and_both_input_children_without_hit_test(self):
        from original_supportstart_input import (
            project_original_supportstart_native_row_release,
        )
        row = original_supportstart_fresh_native_row()
        pressed = project_original_supportstart_row_native_dispatch(
            row, native_second_argument_present=True,
            observed_parent_acceptance=True, observed_child_acceptances=(True,True),
            source_row_index=0,
        ).source_after_row_bit15_toggle
        self.assertEqual(pressed.parent, 0x8193)
        self.assertEqual(pressed.children[3:], (0x193, 0x193))
        receipt = project_original_supportstart_native_row_release(
            pressed, source_row_index=0,
            observed_original_release_for_row=True,
        )
        self.assertTrue(receipt.source_parent_was_pressed)
        self.assertEqual(receipt.invoked_child_indices, (3,4))
        self.assertEqual(receipt.source_child_was_pressed, (True,True))
        self.assertEqual(receipt.source_row_after.parent, 0x8183)
        self.assertEqual(receipt.source_row_after.children[3:], (0x183,0x183))
        self.assertEqual(receipt.source_row_after.stored_staff_selection_byte_if_applied, 0)
        # AFTER an actual observed release, a second qualified press may toggle back.
        second = project_original_supportstart_row_native_dispatch(
            receipt.source_row_after, native_second_argument_present=True,
            observed_parent_acceptance=True,
            observed_child_acceptances=(False,False), source_row_index=0,
        )
        self.assertEqual(second.source_after_row_bit15_toggle.parent, 0x193)
        self.assertEqual(second.source_after_row_bit15_toggle.stored_staff_selection_byte_if_applied, 1)

    def test_source_release_can_skip_unregistered_or_disabled_input_children(self):
        from original_supportstart_input import (
            project_original_supportstart_native_row_release,
            original_supportstart_empty_row_after_refresh,
        )
        empty = original_supportstart_empty_row_after_refresh(original_supportstart_fresh_native_row())
        receipt = project_original_supportstart_native_row_release(
            empty, source_row_index=6, observed_original_release_for_row=True,
        )
        # Input child3 still enabled bit0, child4 disabled: release invokes
        # parent and child3, but neither had native pressed bit0x10.
        self.assertEqual(receipt.invoked_child_indices, (3,))
        self.assertEqual(receipt.source_row_after, empty)
        self.assertFalse(receipt.source_parent_was_pressed)
        self.assertEqual(receipt.source_child_was_pressed, (False,))

    def test_native_release_cannot_be_invented_or_rebound_to_wrong_row(self):
        from original_supportstart_input import project_original_supportstart_native_row_release
        row = original_supportstart_fresh_native_row()
        for idx in (-1,7,True,None):
            with self.subTest(index=idx), self.assertRaises(ValueError):
                project_original_supportstart_native_row_release(
                    row, source_row_index=idx,
                    observed_original_release_for_row=True,
                )
        for observed in (1,None,"yes"):
            with self.subTest(observed=observed), self.assertRaises(TypeError):
                project_original_supportstart_native_row_release(
                    row, source_row_index=0,
                    observed_original_release_for_row=observed,
                )
        with self.assertRaises(ValueError):
            project_original_supportstart_native_row_release(
                row, source_row_index=0,
                observed_original_release_for_row=False,
            )

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



    def test_source_modal_row_mouse_down_parent_callback_acceptance(self):
        from original_supportstart_input import (
            original_supportstart_source_window_click_accepts_row as accepts,
        )
        # The authentic modal owner callback vft+0x0C is a constant-1
        # handler (0x42DE00), and native group IDs 8..14 are nonzero.
        # Source viewport 800x600 puts row 0 at (431,281,326,37).
        args = dict(row_index=0, viewport_size=(800,600))
        self.assertTrue(accepts(
            source_screen_point=(431,281),
            native_row_control_dword=0x183, **args))
        self.assertTrue(accepts(
            source_screen_point=(756,317),
            native_row_control_dword=0x183, **args))
        for outside in ((430,281), (757,281), (431,280), (431,318)):
            with self.subTest(outside=outside):
                self.assertFalse(accepts(
                    source_screen_point=outside,
                    native_row_control_dword=0x183, **args))
        for rejected_dword in (0x181, 0x182, 0x193, 0x180, 0x8001):
            with self.subTest(rejected_dword=rejected_dword):
                self.assertFalse(accepts(
                    source_screen_point=(500,300),
                    native_row_control_dword=rejected_dword, **args))
        # Seventh row is a distinct source identity; same callback
        # contract, but empty source state cannot be accepted.
        self.assertTrue(accepts(
            row_index=6, source_screen_point=(431,521),
            viewport_size=(800,600), native_row_control_dword=0x183))
        self.assertFalse(accepts(
            row_index=6, source_screen_point=(431,521),
            viewport_size=(800,600), native_row_control_dword=0x181))
        with self.assertRaises(ValueError):
            accepts(row_index=7, source_screen_point=(500,300),
                    viewport_size=(800,600), native_row_control_dword=0x183)
        with self.assertRaises(ValueError):
            accepts(row_index=0, source_screen_point=(False,281),
                    viewport_size=(800,600), native_row_control_dword=0x183)


    def test_source_native_pointer_down_pressed_release_cycle(self):
        from original_supportstart_input import (
            project_original_supportstart_source_pointer_down as down,
            project_original_supportstart_native_row_release as release,
            original_supportstart_fresh_native_row,
            original_supportstart_empty_row_after_refresh,
        )
        row = original_supportstart_fresh_native_row()
        kw = dict(row_index=0, source_screen_point=(500,300),
                  viewport_size=(800,600))
        first = down(row, **kw)
        self.assertTrue(first.native_handler_accepted)
        self.assertEqual(first.source_row_index, 0)
        self.assertEqual(first.invoked_child_indices,(3,4))
        self.assertEqual(first.observed_child_acceptances,(True,True))
        pressed = first.source_after_row_bit15_toggle
        self.assertEqual(pressed.parent,0x8193)
        self.assertEqual(pressed.children[3],0x193)
        self.assertEqual(pressed.children[4],0x193)
        with self.assertRaises(ValueError):
            down(pressed, **kw)
        lifted = release(
            pressed, source_row_index=0,
            observed_original_release_for_row=True,
        ).source_row_after
        self.assertEqual(lifted.parent,0x8183)
        self.assertEqual(lifted.children[3],0x183)
        self.assertEqual(lifted.children[4],0x183)
        second = down(lifted, **kw)
        self.assertEqual(second.source_after_row_bit15_toggle.parent,0x193)
        # Parent can accept with both child callback candidates absent.
        none_enabled = OriginalSupportStartRowBitState(
            0x183,(0x183,0x183,0x183,0x180,0x180))
        parent_only = down(none_enabled, **kw)
        self.assertEqual(parent_only.invoked_child_indices, ())
        self.assertTrue(parent_only.native_handler_accepted)
        blank = original_supportstart_empty_row_after_refresh(
            original_supportstart_fresh_native_row())
        with self.assertRaises(ValueError):
            down(blank,row_index=6,
                 source_screen_point=(500,540),viewport_size=(800,600))
        with self.assertRaises(ValueError):
            down(row,row_index=0,source_screen_point=(757,300),
                 viewport_size=(800,600))

if __name__ == "__main__":
    unittest.main()
