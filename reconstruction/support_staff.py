"""Minimum recovered support-staff state needed by Gate-11 training.

This module deliberately stops at the source-backed boundary. It reproduces the
fixed fresh-user staff generator and the training-quality lookup semantics, but
it does not attach those draws to GameState startup until the exact shared CRT
state after the secondary schedule/support-pool startup work is reconstructed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


INITIAL_SUPPORT_STAFF_TYPES = (1, 2, 3, 4, 5, 13)
ASSISTANT_MANAGER_TYPE = 2
YOUTH_TEAM_COACH_TYPE = 3
# Original TeamSelect 0x4DA4F0 -> PSupportStart 0x4CF2EF/0x4D06B0.
# Seven UI selector records are distinct from six fixed initial staff.
ORIGINAL_SUPPORT_START_SLOT_COUNT = 7


@dataclass(frozen=True)
class SupportStaffState:
    """Training-relevant subset of the original 0x218-byte CSupportStaff."""

    staff_type: int
    age_like: int
    rating: int
    status: int = 1

    @property
    def effective_training_rating(self) -> int:
        """Original virtual +0x40 behavior used by active training."""
        if int(self.status) == 2:
            return 1
        return int(self.rating)



@dataclass(frozen=True)
class OriginalSupportStartSourceSlot:
    """One original TeamSelect selection record, NOT a new staff creation.

    0x4DA4F0 populates record +0x0C+4*i and sets +0x28+i = 1 for
    each existing DBRUser+0x5D4 staff node; PSupportStart 0x4CF124 reads
    those addresses, and 0x4D06B0 renders seven cells.  For a missing
    staff node the original code writes a NULL pointer but does not
    establish its flag's initialized value, so preserve None as unknown.
    """

    index: int
    staff: SupportStaffState | None
    original_selected_byte: int | None

    def __post_init__(self) -> None:
        if type(self.index) is not int or not 0 <= self.index < ORIGINAL_SUPPORT_START_SLOT_COUNT:
            raise ValueError("Original support slot index outside 0..6")
        if self.staff is None:
            if self.original_selected_byte is not None:
                raise ValueError("Unknown empty original support flag must stay unqualified")
        elif (type(self.staff) is not SupportStaffState
              or type(self.original_selected_byte) is not int
              or self.original_selected_byte != 1):
            raise ValueError("Original filled support slot needs a source staff and byte 1")


def original_teamselect_support_slots(
    selected_user_staff_in_native_list_order: Iterable[SupportStaffState],
) -> tuple[OriginalSupportStartSourceSlot, ...]:
    """Stage only original 0x4DA4F0's seven pointers/flags, without RNG.

    The caller must already hold source-ordered registered user+0x5D4 staff;
    this function does not generate staff, pick a row action, edit its flag,
    commit user linked lists, create UI images or qualify original GUI.
    It explicitly does NOT infer how shared-CRT startup initialized that list.
    """
    items = tuple(selected_user_staff_in_native_list_order)
    if len(items) > ORIGINAL_SUPPORT_START_SLOT_COUNT:
        raise ValueError("Native PSupportStart has exactly seven pointer slots")
    if any(type(item) is not SupportStaffState for item in items):
        raise TypeError("Original support slot requires native-list staff records")
    if len({id(item) for item in items}) != len(items):
        raise ValueError("Source staff pointer cannot occupy multiple selector positions")
    return tuple(
        OriginalSupportStartSourceSlot(
            index=index,
            staff=items[index] if index < len(items) else None,
            original_selected_byte=1 if index < len(items) else None,
        )
        for index in range(ORIGINAL_SUPPORT_START_SLOT_COUNT)
    )



def original_staff_inactive_link_owner_offset(staff_type: int) -> int:
    """Native PSupportStart Apply 0x4D0900 -> 0x4CA070 type dispatch.

    Original 0x4CA070 checks 1..16 and uses exact byte table 0x4CA0D8:
    first 5 types go to selected DBRUser+0x5B8; next 11 to +0x5C4.
    This is a bounded source mapping, not a linked-list mutation, GUI,
    user selection claim or authorization to advance the shared RNG.
    """
    if type(staff_type) is not int or not 1 <= staff_type <= 16:
        raise ValueError("Native inactive staff type must be 1..16")
    return 0x5B8 if staff_type <= 5 else 0x5C4


def initial_staff_rating_base(competition_context: int) -> int:
    """Map the 0x4FA520 context to the base used by 0x4C9D40.

    Context cases 0/1/2 use bases 4/3/2. Case 3 and every later/default
    context use base 1. Premier League competition 0 is in the default family.
    """

    context = int(competition_context)
    if context == 0:
        return 4
    if context == 1:
        return 3
    if context == 2:
        return 2
    return 1


def generate_fixed_initial_staff(
    rng: BoundedRng,
    staff_type: int,
    competition_context: int,
) -> SupportStaffState:
    """Reproduce one 0x4C9D40(type) fixed fresh-user staff creation.

    Exact bounded draws, in order:
      RNG(25)+25 -> age-like field
      RNG(2)+tier_base -> rating

    Types 1..5 take the default-success compatibility path and therefore enter
    fresh user state with status 1. The only Gate-11 training staff are types
    2 and 3, both inside that range.
    """

    staff_type = int(staff_type)
    if staff_type <= 0:
        raise ValueError("staff_type must be positive")
    age_like = int(rng.randbelow(25)) + 25
    rating = int(rng.randbelow(2)) + initial_staff_rating_base(
        competition_context
    )
    return SupportStaffState(
        staff_type=staff_type,
        age_like=age_like,
        rating=rating,
        status=1,
    )


def generate_fresh_user_support_staff(
    rng: BoundedRng,
    competition_context: int,
) -> tuple[SupportStaffState, ...]:
    """Create the six fixed staff generated by 0x4D1760 in original order."""

    return tuple(
        generate_fixed_initial_staff(rng, staff_type, competition_context)
        for staff_type in INITIAL_SUPPORT_STAFF_TYPES
    )


def training_quality_multiplier(
    staff: Iterable[SupportStaffState],
    *,
    has_training_centre: bool = False,
) -> float:
    """Return the exact source-backed quality multiplier used by 0x4EACE0.

    Youth Team Coach (type 3) takes precedence. Its effective 1..5 rating maps
    to 1.25/1.30/1.35/1.40/1.45. If no youth coach exists but an Assistant
    Manager (type 2) does, the fallback is 1.25. Training Centre feature ID 5
    then adds exactly +0.25.
    """

    staff = tuple(staff)
    youth = next(
        (item for item in staff if int(item.staff_type) == YOUTH_TEAM_COACH_TYPE),
        None,
    )
    if youth is not None:
        rating = max(1, min(5, int(youth.effective_training_rating)))
        quality = 1.20 + 0.05 * rating
    else:
        assistant = next(
            (
                item
                for item in staff
                if int(item.staff_type) == ASSISTANT_MANAGER_TYPE
            ),
            None,
        )
        quality = 1.25 if assistant is not None else 1.0

    if has_training_centre:
        quality += 0.25
    return quality
