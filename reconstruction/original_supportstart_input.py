"""Source-bounded original PSupportStart row bit15 interaction and dispatch flags.

Based on original footballmanager.exe SHA-256 833bf95e...b7cc3.
- Seven native rows, five children registered via 0x5D4580 at 0x4C9486.
- Row +0x98 = 0x5D6200, row +0x6C = 0x5D6270.
- Accepted 0x5D4790 input flips bit15, but physical hit ownership is not proven.
- 0x4D0830 stores the inverse bit15 as the selected-record byte.

This is an isolated native-control transition for a VERIFIED upstream event
result, not a mouse-coordinate predictor, full editor or Apply transaction.
"""
from __future__ import annotations

from dataclasses import dataclass
from support_staff import original_supportstart_flag_after_selector_state

ORIGINAL_ROW_PARENT_VTABLE = 0x7C6780
ORIGINAL_ROW_CHILD_OFFSETS = (0x38, 0x3C, 0x40, 0x44, 0x48)
# Actual final vtables, not initial constructor-base temporary vtable.
ORIGINAL_ROW_CHILD_VTABLES = (0x7BE9BC, 0x7C66C8, 0x7C66C8, 0x7BE530, 0x7BFF14)
ORIGINAL_ROW_REGISTRATION_FLAGS = (0x33, 0x31, 0x31, 0x15, 0x15)
ORIGINAL_ROW_STATE_MASK = 0x8000
ORIGINAL_ROW_CHILD_STATE_FLAG = 0x20
ORIGINAL_ROW_CHILD_INPUT_FLAG = 0x04


def _dword(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 0xFFFFFFFF:
        raise ValueError("Original control flags must be unsigned DWORD")
    return value


@dataclass(frozen=True)
class OriginalSupportStartRowBitState:
    """Native row+five child DWORD bitsets, not presentation geometry."""
    parent: int
    children: tuple[int, int, int, int, int]

    def __post_init__(self) -> None:
        _dword(self.parent)
        if type(self.children) is not tuple or len(self.children) != 5:
            raise ValueError("Original SupportStart row has five registered children")
        for state in self.children:
            _dword(state)

    @property
    def stored_staff_selection_byte_if_applied(self) -> int:
        """Native 0x4D0830 persists inverse row bit15, not child bit15."""
        return original_supportstart_flag_after_selector_state(self.parent)


def original_supportstart_row_set_bit15(
    row: OriginalSupportStartRowBitState, enabled: bool,
) -> OriginalSupportStartRowBitState:
    """Original 0x5D6200 sets/clears parent + ONLY child flags & 0x20.

    Other bits survive. This function simulates a bounded source transition;
    it does not synthesize native redraw callback side effects.
    """
    if type(row) is not OriginalSupportStartRowBitState or type(enabled) is not bool:
        raise TypeError("Require an original row state and explicit Boolean")

    def update(dword: int) -> int:
        return (dword | ORIGINAL_ROW_STATE_MASK if enabled
                else dword & ~ORIGINAL_ROW_STATE_MASK)

    return OriginalSupportStartRowBitState(
        update(row.parent),
        tuple(update(child) if flag & ORIGINAL_ROW_CHILD_STATE_FLAG else child
              for child, flag in zip(row.children, ORIGINAL_ROW_REGISTRATION_FLAGS)),
    )


def original_supportstart_row_refresh(
    row: OriginalSupportStartRowBitState, selected_byte: int,
) -> OriginalSupportStartRowBitState:
    """0x4D0796: source selected_byte == 0 becomes row bit15 set.

    Uninitialized empty record bytes have not been established; forbid None.
    """
    if type(selected_byte) is not int or not 0 <= selected_byte <= 255:
        raise ValueError("Native selected byte must be an initialized byte")
    return original_supportstart_row_set_bit15(row, selected_byte == 0)


def original_supportstart_row_native_event(
    row: OriginalSupportStartRowBitState, accepted_by_native_gate: bool,
) -> OriginalSupportStartRowBitState:
    """0x5D6270 toggles bit15 after a *verified* 0x5D4790 acceptance.

    Caller must establish native input acceptance; it is NOT inferred from
    reconstructed geometry or a hypothetical mouse click.
    """
    if type(row) is not OriginalSupportStartRowBitState or type(accepted_by_native_gate) is not bool:
        raise TypeError("Require an original row and an explicit native-gate result")
    if not accepted_by_native_gate:
        return row
    return original_supportstart_row_set_bit15(
        row, not bool(row.parent & ORIGINAL_ROW_STATE_MASK)
    )
