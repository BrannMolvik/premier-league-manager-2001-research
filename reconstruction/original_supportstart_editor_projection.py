"""Source-bounded SupportStart seven-row editor transaction projection.

Original executable SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3

This combines verified original 0x4D06B0 row construction, 0x5D6270
accepted selection event, 0x4D05E0 event1 Cancel/event2 Apply and original
0x4D0830 source staff/list/name writes. It does not drive Tk, infer native
mouse hits, launch the original program, or mutate GameState.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from original_human_user_name import OriginalHumanUserName
from original_supportstart_input import (
    OriginalSupportStartRowBitState,
    original_supportstart_initial_seven_rows,
    original_supportstart_row_native_event,
)
from original_supportstart_staff_lists import (
    OriginalSupportStartLinkedLists,
    OriginalSupportStartProjectedApply,
    project_original_supportstart_first_human_modal_entry,
    project_original_supportstart_staff_apply,
)
from support_staff import OriginalSupportStartSourceSlot


@dataclass(frozen=True)
class OriginalSupportStartCloseProjection:
    """Source modal result and non-mutating post-close user/list projection."""

    source_modal_result: int
    original_human_user_name: OriginalHumanUserName
    staff_lists: OriginalSupportStartLinkedLists
    original_record_flag_bytes: tuple[int | None, ...]
    invoked_original_apply: bool


@dataclass(frozen=True)
class OriginalSupportStartEditorProjection:
    """Single verified selected user's seven staged source slots.

    Empty rows are disabled using the native source flag path. UI events
    are fed only after source input acceptance has been established by
    the caller; a coordinate alone is never proof of native selection.
    """

    original_user: OriginalHumanUserName
    source_slots: tuple[OriginalSupportStartSourceSlot, ...]
    # Supplied state is an already source-qualified snapshot at modal entry.
    # On the normal first human path, 0x4DA4F0 stages staff BEFORE the modal;
    # it is not permission to recreate the pre-staging lists on Cancel.
    prior_staff_lists: OriginalSupportStartLinkedLists
    rows: tuple[OriginalSupportStartRowBitState, ...]
    draft_first_name: str
    draft_surname: str

    @classmethod
    def open(
        cls,
        *,
        original_user: OriginalHumanUserName,
        source_slots: tuple[OriginalSupportStartSourceSlot, ...],
        prior_staff_lists: OriginalSupportStartLinkedLists,
    ) -> "OriginalSupportStartEditorProjection":
        if type(original_user) is not OriginalHumanUserName:
            raise TypeError("Require original source human user name")
        if type(prior_staff_lists) is not OriginalSupportStartLinkedLists:
            raise TypeError("Require source-qualified selected-user staff lists")
        rows = original_supportstart_initial_seven_rows(source_slots)
        return cls(
            original_user=original_user,
            source_slots=source_slots,
            prior_staff_lists=prior_staff_lists,
            rows=rows,
            draft_first_name=original_user.first_name,
            draft_surname=original_user.surname,
        )

    @classmethod
    def open_initial_first_human_modal(
        cls,
        *,
        original_user: OriginalHumanUserName,
        source_slots: tuple[OriginalSupportStartSourceSlot, ...],
        before_native_staging: OriginalSupportStartLinkedLists,
    ) -> "OriginalSupportStartEditorProjection":
        """Compose source first-human staff staging BEFORE modal construction.

        The original 0x4D8F7F -> 0x4DA4F0 performs the list transfer
        before 0x4D9224 -> 0x450BB0 opens the editor. This bounded
        factory requires the original six pointers, native owner flags
        already reset and an explicit genuine user; it does not create
        users, advance shared CRT, post native messages, or open Tk.
        """
        if type(original_user) is not OriginalHumanUserName:
            raise TypeError("Require original source-registered human")
        staged = project_original_supportstart_first_human_modal_entry(
            source_slots=source_slots, before=before_native_staging
        )
        return cls.open(
            original_user=original_user,
            source_slots=source_slots,
            prior_staff_lists=staged,
        )

    def original_source_role_labels(self, strings, indices) -> tuple[str | None, ...]:
        """Read the original, per-row role labels from the verified EA files.

        CSupportStaff type at +0x04 is returned unchanged by native
        0x42CB40 vft+0x14, then 0x4D0725 invokes 0x4CDCD0 label switch.
        A source null pointer renders the original EMPTY row, not a
        fabricated seventh role or localized staff name. Actual unique
        staff personal names remain unavailable without original RNG
        name-pool initialization; do not imply they were reconstructed.
        """
        from original_supportstart_staff_labels import (
            original_supportstart_staff_type_label,
        )
        from ea_language_strings import EAStringTable, EAStringIndex
        if type(strings) is not EAStringTable or type(indices) is not EAStringIndex:
            raise TypeError("Require authentic validated original English language resources")
        return tuple(
            None if row.staff is None
            else original_supportstart_staff_type_label(row.staff, strings, indices)
            for row in self.source_slots
        )

    def with_edited_name(self, first_name: str, surname: str) -> "OriginalSupportStartEditorProjection":
        # Retained original user object supplies CP1252 and source-name bounds.
        replace(self.original_user, first_name=first_name, surname=surname)
        return replace(self, draft_first_name=first_name, draft_surname=surname)

    def with_native_row_event(
        self, index: int, *, accepted_by_native_gate: bool
    ) -> "OriginalSupportStartEditorProjection":
        if type(index) is not int or not 0 <= index < 7:
            raise ValueError("Original source editor row index must be 0..6")
        if type(accepted_by_native_gate) is not bool:
            raise TypeError("Native event acceptance must be an explicit Boolean")
        if self.source_slots[index].staff is None and accepted_by_native_gate:
            raise ValueError("Original disabled empty staff row cannot accept input")
        changed = list(self.rows)
        changed[index] = original_supportstart_row_native_event(
            changed[index], accepted_by_native_gate
        )
        return replace(self, rows=tuple(changed))

    def close(self, native_event: int) -> OriginalSupportStartCloseProjection:
        """Original 0x4D05E0 event1 cancel or event2 full source Apply.

        This prepares output data without GameState writes. Other native
        events have different owners and cannot be treated as Apply/Cancel.
        """
        if type(native_event) is not int or native_event not in (1, 2):
            raise ValueError("Only source Exit(event1) and Tick(event2) close this modal")
        if native_event == 1:
            # Source event1 skips Apply. Preserve only the caller-supplied
            # modal-entry snapshot; native teardown/outer event follow-on
            # still requires separate verification. No synthetic rollback.
            return OriginalSupportStartCloseProjection(
                0, self.original_user, self.prior_staff_lists,
                tuple(slot.original_selected_byte for slot in self.source_slots),
                False,
            )
        # Validate BOTH source-name bounds and staff-list input before
        # emitting the atomic projection; don't partially update a user.
        edited_name = replace(
            self.original_user,
            first_name=self.draft_first_name,
            surname=self.draft_surname,
        )
        applied: OriginalSupportStartProjectedApply = project_original_supportstart_staff_apply(
            source_slots=self.source_slots,
            control_dwords=tuple(row.parent for row in self.rows),
            prior=self.prior_staff_lists,
        )
        return OriginalSupportStartCloseProjection(
            1, edited_name, applied.lists,
            applied.original_record_flag_bytes, True,
        )
