"""Source-bounded PSupportStart staff linked-list ownership / apply projection.

Private original footballmanager.exe SHA-256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.

Original 0x617D70 appends a 0xC-byte node to list [+4 head,+8 tail].
Original 0x42CBF0 unlinks, and 0x4D1880 consults list [+0] to decide
whether to dispose of staff payload on removal. Original 0x4D0830 writes
ZERO to these [+0] ownership flags BEFORE transferring staff. It does
not wipe [+4] head or [+8] tail. No global game state is mutated here.

This is a non-mutating source-list projection for one registered selected
user and 7 original source row pointers, not the original staff GUI,
editor click mechanics, a reconstruction save format, or a complete
native implementation of every branch of 0x4D0830.
"""
from __future__ import annotations

from dataclasses import dataclass

from support_staff import (
    OriginalSupportStartSourceSlot,
    SupportStaffState,
    original_staff_inactive_link_owner_offset,
    original_supportstart_flag_after_selector_state,
)

SOURCE_STAFF_LINK_OWNERS = (0x875600, 0x5B8, 0x5C4, 0x5D0)


def _has(records: list[SupportStaffState], staff: SupportStaffState) -> bool:
    return any(entry is staff for entry in records)


def _remove(records: list[SupportStaffState], staff: SupportStaffState) -> None:
    records[:] = [entry for entry in records if entry is not staff]


def _validate_list(records: tuple[SupportStaffState, ...], name: str) -> None:
    if type(records) is not tuple or any(type(x) is not SupportStaffState for x in records):
        raise ValueError(f"Native {name} must be explicit original support pointers")
    if len({id(x) for x in records}) != len(records):
        raise ValueError(f"Duplicate pointer in native {name} list")


@dataclass(frozen=True)
class OriginalSupportStartLinkedLists:
    """Selected DBRUser's +0x5B8,+0x5C4,+0x5D0 and shared global 0x875600.

    Each tuple is in SOURCE list order, preserving original pointer identity.
    Names refer to membership, not necessarily a user-visible employment label.
    """

    inactive_type_1_to_5: tuple[SupportStaffState, ...] = ()
    inactive_type_6_to_16: tuple[SupportStaffState, ...] = ()
    current_staff: tuple[SupportStaffState, ...] = ()
    global_staff: tuple[SupportStaffState, ...] = ()

    def __post_init__(self) -> None:
        for field in ("inactive_type_1_to_5", "inactive_type_6_to_16",
                      "current_staff", "global_staff"):
            _validate_list(getattr(self, field), field)
        assigned = self.inactive_type_1_to_5 + self.inactive_type_6_to_16 + self.current_staff
        if len({id(x) for x in assigned}) != len(assigned):
            raise ValueError("A selected human staff pointer cannot occupy two user lists")
        for staff in self.inactive_type_1_to_5:
            if original_staff_inactive_link_owner_offset(staff.staff_type) != 0x5B8:
                raise ValueError("Invalid source type in original user+0x5B8")
        for staff in self.inactive_type_6_to_16:
            if original_staff_inactive_link_owner_offset(staff.staff_type) != 0x5C4:
                raise ValueError("Invalid source type in original user+0x5C4")


@dataclass(frozen=True)
class OriginalSupportStartProjectedApply:
    lists: OriginalSupportStartLinkedLists
    original_record_flag_bytes: tuple[int, ...]
    # Original 0x4D0844..0x4D086F resets only four list OWNER flags.
    list_payload_deletion_flags: tuple[int, int, int, int] = (0, 0, 0, 0)


def project_original_supportstart_staff_apply(
    *, source_slots: tuple[OriginalSupportStartSourceSlot, ...],
    control_dwords: tuple[int, ...],
    prior: OriginalSupportStartLinkedLists,
) -> OriginalSupportStartProjectedApply:
    """Bounded identity-preserving 0x4D0830 seven-pointer transfer.

    The caller supplies genuine original-ordered selected-user linked lists,
    shared global list and exact 7 control DWORD values. The native routine
    iterates i=6..0, stores inverse bit15 to the original record flag,
    and moves actual staff pointers between source list owners. It is not
    permission to wire a partial PSupportStart Apply to the live controller.
    """
    if (type(source_slots) is not tuple or len(source_slots) != 7
            or any(type(s) is not OriginalSupportStartSourceSlot
                   or s.index != i for i, s in enumerate(source_slots))):
        raise ValueError("Require exactly seven ordered original source selector slots")
    if type(control_dwords) is not tuple or len(control_dwords) != 7:
        raise ValueError("Require exactly seven original selector DWORDs")
    if type(prior) is not OriginalSupportStartLinkedLists:
        raise ValueError("Explicit original selected-user staff list state required")

    # Validate ALL inputs before source-list projection changes any copy.
    flags = tuple(original_supportstart_flag_after_selector_state(x)
                  for x in control_dwords)
    pointers = [row.staff for row in source_slots if row.staff is not None]
    if len({id(x) for x in pointers}) != len(pointers):
        raise ValueError("A source staff pointer cannot occur in two source slots")

    primary = list(prior.inactive_type_1_to_5)
    secondary = list(prior.inactive_type_6_to_16)
    current = list(prior.current_staff)
    global_list = list(prior.global_staff)

    for index in range(6, -1, -1):
        staff = source_slots[index].staff
        if staff is None:
            continue
        if flags[index]:
            # Original +0x5BC and +0x5C8 duplicate guards skip this branch
            # when the pointer already belongs to either inactive list.
            if _has(primary, staff) or _has(secondary, staff):
                continue
            owner = original_staff_inactive_link_owner_offset(staff.staff_type)
            (primary if owner == 0x5B8 else secondary).append(staff)
            _remove(current, staff)
        else:
            _remove(primary, staff)
            _remove(secondary, staff)
            if not _has(current, staff):
                current.append(staff)
            if not _has(global_list, staff):
                global_list.append(staff)

    result = OriginalSupportStartLinkedLists(
        inactive_type_1_to_5=tuple(primary),
        inactive_type_6_to_16=tuple(secondary),
        current_staff=tuple(current),
        global_staff=tuple(global_list),
    )
    return OriginalSupportStartProjectedApply(result, flags)
