"""Original FM2001 PEAMail grid assets and bounded native list event contract.

Historical original PE source receipts are pinned in
research/GATE13_EAMAIL_NATIVE_ROW_CONTROL_PIXELS_EVENTS_AUDIT_RECOVERY450.md
and research/GATE13_EAMAIL_NATIVE_ROW_DETAIL_AUDIT_RECOVERY439.md.
No user-visible Inbox, native input mapping, sort/filter, record body, text
formatting, message mutation or delivery readiness is inferred here.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import TypeVar

from ea444_header import parse_ea444_header


class OriginalEAMailSourceError(ValueError):
    """The bounded native EAMail source contract is not satisfied."""


ORIGINAL_EAMAIL_CLASS = "PEAMail"
ORIGINAL_EAMAIL_VFTABLE_VA = 0x7C2950
ORIGINAL_EAMAIL_CONSTRUCTOR_VA = 0x474B10
ORIGINAL_EAMAIL_FACTORY_VA = 0x47B1D0
ORIGINAL_EAMAIL_MENU_CHILD_ID = 0x65
ORIGINAL_EAMAIL_CURRENT_USER_VA = 0x4139D0
ORIGINAL_EAMAIL_USER_MAILBOX_OFFSET = 0x6B4
ORIGINAL_EAMAIL_FILTERED_ARRAY_OFFSET = 0x68
ORIGINAL_EAMAIL_FILTERED_COUNT_OFFSET = 0x6C

# 0x47F2B0 -> 0x653320, PMenu factory 0x47B1D0.
# These are native panel-owner coordinates, not screen hit-test acceptance.
ORIGINAL_EAMAIL_PANEL_RECT = (0, 148, 800, 530)
# PEAMail 0x46F511..0x46F557 -> 0x6510F0; panel-local.
ORIGINAL_EAMAIL_LIST_RECT = (233, 30, 545, 160)
ORIGINAL_EAMAIL_LIST_CONTROL_ID = 0x11
ORIGINAL_EAMAIL_LIST_OBJECT_OFFSET = 0xF58
ORIGINAL_EAMAIL_LIST_CLASS = "CMessageList"
ORIGINAL_EAMAIL_LIST_VFTABLE_VA = 0x7C2A50
ORIGINAL_EAMAIL_VISIBLE_ROWS = 8
ORIGINAL_EAMAIL_ROW_PITCH = 20
ORIGINAL_EAMAIL_ROW_CLASS = "PMessageRow"
ORIGINAL_EAMAIL_ROW_VFTABLE_VA = 0x7C266C
ORIGINAL_EAMAIL_ROW_RECT = (0, 0, 532, 18)
ORIGINAL_EAMAIL_ROW_SOURCE_POINTER_OFFSET = 0x70
ORIGINAL_EAMAIL_SELECTED_ROW_POINTER_VA = 0x87675C
ORIGINAL_EAMAIL_ROW_NEUTRAL_CALLBACK_VA = 0x471B80
ORIGINAL_EAMAIL_DETAIL_OPEN_VA = 0x471270
ORIGINAL_EAMAIL_DETAIL_CLASS = "PEAMMessage"
ORIGINAL_EAMAIL_DETAIL_VFTABLE_VA = 0x7C2714

# Native row-child IDs from 0x46E680, coordinates relative to row.
# These do not establish clickable final screen coordinates.
ORIGINAL_EAMAIL_TEXT_CHILDREN = (
    (2, (38, 0, 215, 16), 0x174),
    (3, (256, 0, 215, 16), 0x74),
    (0, (474, 0, 71, 16), 0x274),
)
ORIGINAL_EAMAIL_DECORATIVE_ICON_ORIGINS = ((15, 3), (15, 3), (2, 4))


@dataclass(frozen=True)
class OriginalEAMailGridResource:
    name: str
    source_path: str
    byte_size: int
    sha256: str
    dimensions: tuple[int, int]
    iso_lba: int
    source_literal_va: int
    source_loader_va: int
    source_wrapper_va: int


# Original disc byte sizes/hashes and literal/static-loader owners are from
# verified Recovery450 original source. The fourth graphics loader's detailed
# wrapper completion is intentionally left unknown.
ORIGINAL_EAMAIL_GRID_RESOURCES = (
    OriginalEAMailGridResource(
        "normal", "FM2001_Art/Generic/EAMail/text_grid_nor.444", 8124,
        "74676dce75532b781551cab6e8598f805fa4698b2e1b828c9f4ef15b3ff0816d",
        (532, 18), 105652, 0x836024, 0x5F5580, 0x945E30,
    ),
    OriginalEAMailGridResource(
        "selected", "FM2001_Art/Generic/EAMail/text_grid_sel.444", 7504,
        "6b6ff7ce36b3c507df2d590ba7ad48b9253409757844acf4ec93204807bad556",
        (532, 18), 105656, 0x836050, 0x5F5620, 0x945DF0,
    ),
    OriginalEAMailGridResource(
        "highlight", "FM2001_Art/Generic/EAMail/text_grid_high.444", 6856,
        "a13b413d13b5fa9c5f6a7b36f632c60342898de72bcff2ee73025bc92fdb68c8",
        (532, 18), 105648, 0x83607C, 0x5F56C0, 0x945DB0,
    ),
    OriginalEAMailGridResource(
        "disabled", "FM2001_Art/Generic/EAMail/text_grid_des.444", 7184,
        "cb1fb08a99dfe204ea9b485f5102e808ab758f80aec96f69e17e9537d8eb2f70",
        (532, 18), 105644, 0x8360AC, 0x5F5760, 0x945D70,
    ),
)


def validate_original_eamail_grid_resources(
    source_root: Path,
) -> tuple[OriginalEAMailGridResource, ...]:
    """Require the four source-identical row strips before any native raster use.

    Does not invent a substitute when a resource is absent or corrupted.
    Paths are relative to the intentionally staged original-assets/source tree.
    """
    root = Path(source_root)
    for resource in ORIGINAL_EAMAIL_GRID_RESOURCES:
        path = root / resource.source_path
        try:
            raw = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalEAMailSourceError(
                f"Missing original EAMail art: {resource.source_path}"
            ) from exc
        if len(raw) != resource.byte_size:
            raise OriginalEAMailSourceError(
                f"Original EAMail art byte size differs: {resource.source_path}"
            )
        if sha256(raw).hexdigest() != resource.sha256:
            raise OriginalEAMailSourceError(
                f"Original EAMail art SHA-256 differs: {resource.source_path}"
            )
        try:
            header = parse_ea444_header(raw)
        except ValueError as exc:
            raise OriginalEAMailSourceError(
                f"Original EAMail art header is invalid: {resource.source_path}"
            ) from exc
        if (header.width, header.height) != resource.dimensions:
            raise OriginalEAMailSourceError(
                f"Original EAMail art geometry differs: {resource.source_path}"
            )
    return ORIGINAL_EAMAIL_GRID_RESOURCES


_T = TypeVar("_T")


@dataclass(frozen=True)
class OriginalEAMailFilteredWindow:
    """Only a caller-supplied *native-qualified* PEAMail+0x68 ordering.

    This must NOT accept the DBRUser+0x6B4 insertion list or global
    MPM 0x947AA8 pending queue as a substitute. We intentionally do not
    implement the still unresolved original five sort/filter controls.
    """
    original_filtered_rows: tuple[object, ...]
    scroll_offset: int
    max_scroll_offset: int
    visible_rows: tuple[object, ...]


def original_eamail_filtered_window(
    original_filtered_array: tuple[_T, ...],
    scroll_offset: int,
    *,
    native_filtered_array_qualified: bool,
) -> OriginalEAMailFilteredWindow:
    """Original 0x472B4F: scroll maximum max(0,count-8); 0x6512A0 view.

    No sorting, filtering, status interpretation or implicit scrolling.
    """
    if type(native_filtered_array_qualified) is not bool or not native_filtered_array_qualified:
        raise OriginalEAMailSourceError(
            "Native PEAMail+0x68 filtered/sorted array not source-qualified"
        )
    if type(original_filtered_array) is not tuple:
        raise OriginalEAMailSourceError("Native filtered array must be an immutable tuple")
    if type(scroll_offset) is not int:
        raise OriginalEAMailSourceError("Native EAMail scroll offset must be an integer")
    maximum = max(0, len(original_filtered_array) - ORIGINAL_EAMAIL_VISIBLE_ROWS)
    if not 0 <= scroll_offset <= maximum:
        raise OriginalEAMailSourceError("EAMail offset outside native eight-row scroll range")
    return OriginalEAMailFilteredWindow(
        original_filtered_rows=original_filtered_array,
        scroll_offset=scroll_offset,
        max_scroll_offset=maximum,
        visible_rows=original_filtered_array[
            scroll_offset:scroll_offset + ORIGINAL_EAMAIL_VISIBLE_ROWS
        ],
    )


@dataclass(frozen=True)
class OriginalEAMailNeutralRowDispatch:
    """Source virtual +0x10 / event argument zero; no physical click assumed."""
    kind: str
    selected_row_token: object
    requires_native_record_action: bool


def original_eamail_neutral_row_dispatch(
    *,
    row_token: object,
    currently_selected_row_token: object | None,
    native_event_argument: int,
) -> OriginalEAMailNeutralRowDispatch:
    """0x471B80 first selection vs reactivation of the same *row object*.

    Tokens stand in for native row control pointer identity, not delivered
    message serials, displayed text, or a Windows click gesture. This function
    never itself clears record status or fabricates a PEAMMessage detail modal.
    """
    if row_token is None:
        raise OriginalEAMailSourceError("Original row control identity is required")
    if type(native_event_argument) is not int or native_event_argument != 0:
        raise OriginalEAMailSourceError(
            "Only source-proven neutral PMessageRow event argument zero is handled"
        )
    if row_token is currently_selected_row_token:
        return OriginalEAMailNeutralRowDispatch(
            "request_native_detail", row_token, True
        )
    return OriginalEAMailNeutralRowDispatch(
        "select_native_preview", row_token, False
    )
