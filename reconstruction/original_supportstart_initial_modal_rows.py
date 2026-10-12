"""Native PSupportStart initial seven-row source names/owners, NOT mouse UI.

Original 0x4C9C9E -> 0x617D70 appends six created staff to the
current user's +0x5D0 linked list in source creation order.
Original 0x4DA4F0 walks that same list by source index 6..0,
mapping staff types (1,2,3,4,5,13) into initial slots 0..5
and leaving initial slot 6 empty. 0x4C7B70 -> 0x4C9510
sets the exact seven native layout anchor/owner offsets.

Uses the FINAL native name chosen by second 0x4CA660 call, not
the first (constructor) overwritten name. All source names must
originate from a previously replayed genuine shared-CRT receipt.
No additional CRT draws, user/linked-list mutation, guessed role
labels, star ratings, mouse masks, or modal Apply/Cancel is performed.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_supportstart_layout import (
    SourceSupportStartRowAnchor,
    original_supportstart_row_anchors,
)
from original_supportstart_teamselect_user_birth import (
    SourceOriginalTeamSelectUserBirthReceipt,
)
from support_staff import INITIAL_SUPPORT_STAFF_TYPES, ORIGINAL_SUPPORT_START_SLOT_COUNT


class OriginalSupportStartInitialRowsError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalSupportStartInitialRow:
    source_slot_index: int
    native_anchor: SourceSupportStartRowAnchor
    original_staff_type: int | None
    original_first_name: str | None
    original_surname: str | None
    source_staff_creation_index: int | None

    @property
    def source_has_staff(self) -> bool:
        return self.original_staff_type is not None


def source_supportstart_initial_modal_rows(
    birth: SourceOriginalTeamSelectUserBirthReceipt,
) -> tuple[SourceOriginalSupportStartInitialRow, ...]:
    """Project native list+selector data without changing state or RNG."""
    if type(birth) is not SourceOriginalTeamSelectUserBirthReceipt:
        raise OriginalSupportStartInitialRowsError(
            "Require original source-user/staff birth receipt"
        )
    staff = birth.staff
    if (len(staff) != len(INITIAL_SUPPORT_STAFF_TYPES)
            or tuple(item.staff_type for item in staff)
            != INITIAL_SUPPORT_STAFF_TYPES):
        raise OriginalSupportStartInitialRowsError(
            "Original user staff type/linked-list order is unqualified"
        )
    anchors = original_supportstart_row_anchors()
    if len(anchors) != ORIGINAL_SUPPORT_START_SLOT_COUNT:
        raise OriginalSupportStartInitialRowsError(
            "Original seven-row editor source geometry changed"
        )
    rows=[]
    for index, anchor in enumerate(anchors):
        if anchor.index != index:
            raise OriginalSupportStartInitialRowsError(
                "Original editor row owners reordered"
            )
        if index >= len(staff):
            rows.append(SourceOriginalSupportStartInitialRow(
                index, anchor, None, None, None, None
            ))
            continue
        created=staff[index]
        final=created.final_name
        if (type(final.first_name) is not str or
                type(final.surname) is not str or not final.first_name
                or not final.surname):
            raise OriginalSupportStartInitialRowsError(
                "Native staff final name is absent"
            )
        rows.append(SourceOriginalSupportStartInitialRow(
            source_slot_index=index,
            native_anchor=anchor,
            original_staff_type=created.staff_type,
            original_first_name=final.first_name,
            original_surname=final.surname,
            source_staff_creation_index=index,
        ))
    return tuple(rows)
