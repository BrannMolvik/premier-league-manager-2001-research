"""Fail-closed contract for the four executable-correlated Squad resources.

The names alone are not ownership evidence.  The canonical executable binds
each exact path to a resource handle and its RTTI-backed presentation methods
establish the owners recorded below.  In particular, ``blue_toggle.444`` is a
shared control resource and is not evidence of PSquadScreen ownership.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from ea_language_strings import parse_language_pair


@dataclass(frozen=True)
class OriginalSquadResource:
    source_path: str
    sha256: str
    size: tuple[int, int]
    path_literal_va: int
    raw_handle_va: int
    wrapper_va: int
    native_owners: tuple[str, ...]


SQUAD_BUTTON_ORIGINS = ((37, 92), (113, 92), (189, 92))
SQUAD_SCREEN_CLASS = "PSquadScreen"
SQUAD_SCREEN_TYPE_DESCRIPTOR_VA = 0x819D48
SQUAD_SCREEN_VFTABLE_VA = 0x7C5CA4
SQUAD_SCREEN_SETUP_VA = 0x4B5720
SQUAD_PANEL_FACTORY_VA = 0x47AEC0
SQUAD_PANEL_FACTORY_BRANCH_VA = 0x47AF2D
SQUAD_PANEL_LAYOUT_CALL_VA = 0x47AF80
SQUAD_PANEL_RECT = (0, 79, 800, 520)


@dataclass(frozen=True)
class OriginalSquadButton:
    control_id: int
    object_offset: int
    label_global_va: int
    language_index: int
    original_text: str
    origin: tuple[int, int]


@dataclass(frozen=True)
class OriginalSquadRect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class OriginalSquadListColumn:
    name: str
    x: int
    width: int | None
    source: str


@dataclass(frozen=True)
class OriginalFormationTextRow:
    index: int
    form_control_id: int
    bar_control_id: int
    form_object_offset: int
    bar_object_offset: int
    form_rect: OriginalSquadRect
    bar_rect: OriginalSquadRect


@dataclass(frozen=True)
class OriginalSquadViewTransition:
    control_id: int
    original_text: str
    left_roster: str
    second_roster_mask1: bool
    pitch_mask1: bool
    pitch_team_index: int | None


# PSquadScreen::0x4B5720 registers these controls through vtable slot +8
# (0x64F3C0), which stores the numeric ID and owner. The language loader's
# sequential 16-bit reads bind English.idx entries 2490..2492 to the globals.
# The first control receives a distinct setup flag, but its semantic name and
# all atlas-frame meanings remain deliberately unresolved.
SQUAD_BUTTONS = (
    OriginalSquadButton(3, 0x37A4, 0x982110, 2490, "1ST & RES", (37, 92)),
    OriginalSquadButton(4, 0x37F8, 0x98210C, 2491, "1ST FORM", (113, 92)),
    OriginalSquadButton(5, 0x384C, 0x982108, 2492, "RES. FORM", (189, 92)),
)

CBASE_PLAYER_LIST_CLASS = "CBasePlayerList"
CBASE_PLAYER_LIST_TYPE_DESCRIPTOR_VA = 0x81DCB8
CBASE_PLAYER_LIST_VFTABLE_VA = 0x7C5BC8
PSQUAD_LIST_CLASS = "PSquadList"
PSQUAD_LIST_TYPE_DESCRIPTOR_VA = 0x81DC60
PSQUAD_LIST_VFTABLE_VA = 0x7C5864
PSQUAD_LIST_SETUP_VA = 0x4B4FE0
CSQUAD_PLAYER_LIST_CLASS = "CSquadPlayerList"
CSQUAD_PLAYER_LIST_TYPE_DESCRIPTOR_VA = 0x81DD00
CSQUAD_PLAYER_LIST_VFTABLE_VA = 0x7C5AF4
CSQUAD_SCF_LIST_CLASS = "CSquadSCFList"
CSQUAD_SCF_LIST_TYPE_DESCRIPTOR_VA = 0x81DC98
CSQUAD_SCF_LIST_VFTABLE_VA = 0x7C5968
PSQUAD_PLAYER_ROW_CLASS = "PSquadPlayerRow"
PSQUAD_PLAYER_ROW_TYPE_DESCRIPTOR_VA = 0x81DBE0
PSQUAD_PLAYER_ROW_VFTABLE_VA = 0x7C57BC
PSQUAD_PLAYER_ROW_SETUP_VA = 0x489530
PSCF_ROW_CLASS = "PSCFRow"
PSCF_ROW_TYPE_DESCRIPTOR_VA = 0x81D348
PSCF_ROW_VFTABLE_VA = 0x7C4720
PSCF_ROW_SETUP_VA = 0x489B40
PPLAYER_EMPTY_ROW_CLASS = "PPlayerEmptyRow"
PPLAYER_EMPTY_ROW_TYPE_DESCRIPTOR_VA = 0x81D2B0
PPLAYER_EMPTY_ROW_VFTABLE_VA = 0x7C46CC
PSCF_EMPTY_ROW_CLASS = "PSCFEmptyRow"
PSCF_EMPTY_ROW_TYPE_DESCRIPTOR_VA = 0x81DC40
PSCF_EMPTY_ROW_VFTABLE_VA = 0x7C5810
SQUAD_VISIBLE_ROW_COUNT = 20
SQUAD_VISIBLE_ROW_Y_ORIGINS = tuple(154 + 17 * index for index in range(20))
SQUAD_PLAYER_COLUMNS = (
    OriginalSquadListColumn(
        "club_relative_assignment", 1, 22, "DBRPlayer +0x70/+0x76 selector"
    ),
    OriginalSquadListColumn(
        "assigned_role", 28, 38, "current position code and role table +0x0C"
    ),
    OriginalSquadListColumn(
        "display_name", 76, 144, "first-name + surname formatter"
    ),
)
SQUAD_SCF_COLUMNS = (
    OriginalSquadListColumn(
        "native_status_icon", 1, None, "0x418330 result / 0x87BBF0 table"
    ),
    OriginalSquadListColumn("condition", 24, 19, "DBRPlayer +0x77"),
    OriginalSquadListColumn(
        "recent_form_average", 47, 19, "six-byte recent-rating history"
    ),
    OriginalSquadListColumn(
        "current_role_rating", 70, 19, "current assigned-role rating"
    ),
)
SQUAD_STATUS_FILTER_CODE_BY_MASK = ((0x1, 3), (0x2, 0), (0x4, 1), (0x8, 2))
SQUAD_FIRST_ROSTER_OFFSET = 0x130
SQUAD_RESERVE_ROSTER_OFFSET = 0x1030
SQUAD_PITCH_OFFSET = 0x1F30
SQUAD_FIRST_ROSTER_RECT = OriginalSquadRect(37, 0, 228, 520)
SQUAD_RESERVE_ROSTER_RECT = OriginalSquadRect(418, 0, 228, 520)
SQUAD_PITCH_RECT = OriginalSquadRect(388, 92, 412, 432)
SQUAD_SCREEN_EVENT_HANDLER_VA = 0x4B8E70

SQUAD_VIEW_TRANSITIONS = (
    OriginalSquadViewTransition(3, "1ST & RES", "first", True, False, None),
    OriginalSquadViewTransition(4, "1ST FORM", "first", False, True, 0),
    OriginalSquadViewTransition(5, "RES. FORM", "reserve", False, True, 1),
)

SQUAD_PITCH_CLASS = "PSquadPitch"
SQUAD_PITCH_TYPE_DESCRIPTOR_VA = 0x81DB30
SQUAD_PITCH_VFTABLE_VA = 0x7C54A8
SQUAD_PITCH_SETUP_VA = 0x4B3C80
FORMATION_TEXT_CLASS = "FormationText"
FORMATION_TEXT_TYPE_DESCRIPTOR_VA = 0x81DBC0
FORMATION_TEXT_VFTABLE_VA = 0x7C5700
FORMATION_TEXT_FORM_SETUP_VA = 0x4B6C30
FORMATION_TEXT_BAR_SETUP_VA = 0x4B6B60
FORMATION_TEXT_FORM_FRAME_SIZE = (23, 16)
FORMATION_TEXT_BAR_FRAME_SIZE = (81, 16)
FORMATION_TEXT_GROUP_LENGTH_VA = 0x4D8D30
FORMATION_TEXT_GROUP_SELECTOR_VA = 0x652AE0
FORMATION_TEXT_SOURCE_OFFSET_VA = 0x5D4D70
FORMATION_TEXT_GROUP_LENGTHS = (2, 1, 1)
FORMATION_TEXT_ENABLED_MASK = 0x2
FORMATION_TEXT_POINTER_INSIDE_MASK = 0x8
FORMATION_TEXT_COMPLETE_MASK = 0x8000
SQUAD_PITCH_FORMATION_STATE_REFRESH_VA = 0x4B6910

FORMATION_TEXT_ROWS = tuple(
    OriginalFormationTextRow(
        index=index,
        form_control_id=12 + index * 2,
        bar_control_id=13 + index * 2,
        form_object_offset=0x8C0 + index * 0x58,
        bar_object_offset=0x1050 + index * 0x58,
        form_rect=OriginalSquadRect(279, 25 + index * 17, 23, 16),
        bar_rect=OriginalSquadRect(303, 25 + index * 17, 81, 16),
    )
    for index in range(22)
)

SQUAD_RESOURCES = (
    OriginalSquadResource(
        "FM2001_Art/Coaching/squad/blue_toggle.444",
        "3fe515f5a4a2d798a8f62917a45047b274e08bd3e68147a4fe0e25dfbd1d3343",
        (22, 17),
        0x83827C,
        0x943070,
        0x943050,
        ("PFormation2k", "PSCFTitle", "PTraining", "PYouthTeam"),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_bars.444",
        "c0ba37cc991e5449830af3e550f14dc7d9444cc545e91fa7936dc38508c6110b",
        (81, 64),
        0x8394B8,
        0x941750,
        0x941730,
        ("FormationText",),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_but_anim.444",
        "6a5180d9212fe50418537fa181c44ba075bc0317c5bb55aed8b9c6a9e0fc0632",
        (73, 575),
        0x83943C,
        0x9417D0,
        0x9417B0,
        (SQUAD_SCREEN_CLASS,),
    ),
    OriginalSquadResource(
        "FM2001_Art/Generic/GenericButtonsAndBars/squad_form_anim.444",
        "e4bcc6981cc99fde44b093696791a05f91100752559b0b2f12dc0c0177392828",
        (23, 368),
        0x839478,
        0x941790,
        0x941770,
        ("FormationText",),
    ),
)


class OriginalSquadResourceError(ValueError):
    pass


def formation_text_source_row(
    *, enabled: bool, complete: bool, subframe: int = 0
) -> int:
    """Apply FormationText's native state-group transform without naming art."""
    group = 2 if not enabled else 1 if complete else 0
    if not 0 <= subframe < FORMATION_TEXT_GROUP_LENGTHS[group]:
        raise OriginalSquadResourceError(
            f"FormationText subframe {subframe} is outside native group {group}"
        )
    return (
        subframe if group == 0 else 2 + subframe if group == 1 else 4 + subframe
    )


def formation_text_source_y(
    *, enabled: bool, complete: bool, subframe: int = 0
) -> int:
    return formation_text_source_row(
        enabled=enabled, complete=complete, subframe=subframe
    ) * FORMATION_TEXT_FORM_FRAME_SIZE[1]


def validate_imported_original_squad_resources(
    source_root: Path,
) -> tuple[OriginalSquadResource, ...]:
    """Require the four exact imported bytes and their native header geometry."""
    root = Path(source_root)
    for resource in SQUAD_RESOURCES:
        data = (root / resource.source_path).read_bytes()
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalSquadResourceError(
                f"Original Squad resource checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalSquadResourceError(
                f"Original Squad resource geometry mismatch: {resource.source_path}"
            )
    return SQUAD_RESOURCES


def validate_original_squad_button_labels(
    english_str: Path, english_idx: Path
) -> tuple[OriginalSquadButton, ...]:
    """Resolve the three executable-bound labels from the original language pair."""
    strings, index = parse_language_pair(
        Path(english_str).read_bytes(), Path(english_idx).read_bytes()
    )
    for button in SQUAD_BUTTONS:
        if index.resolve(strings, button.language_index) != button.original_text:
            raise OriginalSquadResourceError(
                f"Original Squad label mismatch at English.idx {button.language_index}"
            )
    return SQUAD_BUTTONS
