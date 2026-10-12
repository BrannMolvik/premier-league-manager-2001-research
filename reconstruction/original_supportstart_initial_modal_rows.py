"""Native PSupportStart initial seven-row source names/owners, NOT mouse UI.

Original 0x4C9C9E -> 0x617D70 appends six created staff to the
current user's +0x5D0 linked list in source creation order.
Original 0x4DA4F0 walks that same list by source index 6..0,
mapping staff types (1,2,3,4,5,13) into initial slots 0..5
and leaving initial slot 6 empty. IMPORTANT: 0x4DA4F0 also calls
0x4CA070 to append to type-specific +0x5B8/+0x5C4 lists and 0x4D1880
to unlink the chosen node from the +0x5D0 source list while staging.
This pure projection does NOT implement those native ownership changes,
so it cannot be used as proof that Cancel restores the pre-modal lists.
0x4C7B70 -> 0x4C9510
sets the exact seven native layout anchor/owner offsets.

0x4D06B0 writes role LABEL from 0x4CDCD0 to first +0x70 buffer and\nwhole STAFF FULL NAME from vft+0x08 to second +0x4F0 buffer.\nThe actual localized role text is not guessed here.\nUses the FINAL native name chosen by second 0x4CA660 call, not
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
    # Actual 0x4D06B0 reads a localized ROLE label via 0x4CDCD0 and
    # copies it to anchor first buffer +0x70+0x80*i. Its exact decoded
    # text is not recovered here. Never render a first name there.
    source_role_label: str | None = None

    @property
    def source_has_staff(self) -> bool:
        return self.original_staff_type is not None

    @property
    def source_staff_full_name(self) -> str | None:
        # vft+0x08 yields FULL "First Last" copied to native second
        # text buffer +0x4F0+0x80*i. Do not split across both buffers.
        if not self.source_has_staff:
            return None
        return self.original_first_name + " " + self.original_surname

    @property
    def source_role_label_owner_offset(self) -> int:
        return self.native_anchor.display_text_first_owner_offset

    @property
    def source_staff_full_name_owner_offset(self) -> int:
        return self.native_anchor.display_text_second_owner_offset


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


@dataclass(frozen=True)
class SourceOriginalSupportStartStagingTransfer:
    """One original 0x4DA4F0 move, not a committed GameState mutation."""

    source_slot_index: int
    source_staff_creation_index: int
    original_staff_type: int
    from_user_list_offset: int
    to_user_inactive_list_offset: int
    source_checks_global_staff_list_for_removal: bool


def source_supportstart_native_staging_transfers(
    rows: tuple[SourceOriginalSupportStartInitialRow, ...],
) -> tuple[SourceOriginalSupportStartStagingTransfer, ...]:
    """The actual *order* of source linked-list moves while staging seven rows.

    Original 0x4DA4F0 initializes EBP=6 and descends to zero.
    Slot6 is null for the newly created six-element source list.
    At each filled slot, 0x4CA070 appends to the corresponding inactive
    staff type list (+0x5B8 or +0x5C4), then native 0x4D1880 removes
    that staff from +0x5D0 and conditionally removes it from global
    0x875600 if found. This happens before the editor's Apply/Cancel.
    It does NOT prove what Cancel cleanup eventually restores.
    """
    if (type(rows) is not tuple or
            len(rows) != ORIGINAL_SUPPORT_START_SLOT_COUNT):
        raise OriginalSupportStartInitialRowsError("Require seven native source rows")
    if any(
        type(row) is not SourceOriginalSupportStartInitialRow
        or row.source_slot_index != index
        for index, row in enumerate(rows)
    ):
        raise OriginalSupportStartInitialRowsError("Source row owners inconsistent")
    if tuple(row.original_staff_type for row in rows) != (
        INITIAL_SUPPORT_STAFF_TYPES + (None,)
    ):
        raise OriginalSupportStartInitialRowsError(
            "Only normal six-staff source creation is qualified"
        )
    if any(row.source_staff_creation_index != i for i, row in enumerate(rows[:6])):
        raise OriginalSupportStartInitialRowsError(
            "Original source-list identity changed during staging"
        )
    # Reverse slots, omitting source-empty index6. This is the actual
    # predecessor-safe removal order of the original index-decrement loop.
    return tuple(
        SourceOriginalSupportStartStagingTransfer(
            source_slot_index=i,
            source_staff_creation_index=i,
            original_staff_type=rows[i].original_staff_type,
            from_user_list_offset=0x5D0,
            to_user_inactive_list_offset=(
                0x5B8 if rows[i].original_staff_type <= 5 else 0x5C4
            ),
            source_checks_global_staff_list_for_removal=True,
        )
        for i in range(5, -1, -1)
    )
