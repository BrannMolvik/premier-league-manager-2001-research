"""Source-backed PMenu menu-row chrome and static menu topology.

This module records only executable-proven FM2001 management-shell presentation
facts. Recovery 146 closes the label mapping by following the complete
2,714-entry English.idx loader itself; labels are named only when the exact
loader assignment and original English bytes agree.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from ea_font import EAFont


class OriginalPMenuChromeError(ValueError):
    pass


PMENU_LIST_CLASS = "CMenuList"
PMENU_LIST_TYPE_DESCRIPTOR_VA = 0x81CE98
PMENU_LIST_VFTABLE_VA = 0x7C3E34

PMENU_BASE_ROW_CLASS = "PBaseMenuRow"
PMENU_BASE_ROW_VFTABLE_VA = 0x7C3C50
PMENU_TITLE_ROW_CLASS = "PTitleMenuRow"
PMENU_TITLE_ROW_VFTABLE_VA = 0x7C3A80
PMENU_TITLE_ROW_SETUP_VA = 0x47A7E0
PMENU_CHILD_ROW_CLASS = "PChildMenuRow"
PMENU_CHILD_ROW_VFTABLE_VA = 0x7C3A20
PMENU_CHILD_ROW_SETUP_VA = 0x47A990
PMENU_TITLE_ARROW_CLASS = "MenuTitleArrow"
PMENU_TITLE_ARROW_VFTABLE_VA = 0x7C3B98
PMENU_BACKGROUND_TOGGLE_CLASS = "MenuBackgroundToggle"
PMENU_BACKGROUND_TOGGLE_VFTABLE_VA = 0x7C3AE0
PMENU_TITLE_SELECT_BITMAP_VFTABLE_VA = 0x7C3CB0
PMENU_CHILD_SELECT_BITMAP_VFTABLE_VA = 0x7C3D4C

PMENU_ROW_HEIGHT = 29
PMENU_TEXT_CLASS = "eCText"
PMENU_TEXT_VFTABLE_VA = 0x7BE340
PMENU_BITMAP_CLASS = "eCBitmap"
PMENU_BITMAP_VFTABLE_VA = 0x7BE5D8
PMENU_TEXT_CONTROL_SIZE = (160, 24)
PMENU_TEXT_CONTROL_Y = (0, 24, 48, 72, 96, 120)
PMENU_RUNTIME_FONT_GLOBAL_VA = 0x87BEA0
PMENU_RUNTIME_FONT_OBJECT_VA = 0x9269F0
PMENU_RUNTIME_FONT_WRAPPER_INIT_VA = 0x603640
PMENU_FONT_LOAD_CALL_VA = 0x60429F
PMENU_FONT_PATH_LITERAL_VA = 0x839F24
PMENU_FONT_SOURCE_PATH = "Fonts/Zurich_BdXCn_BT_16pixel.fnt"
PMENU_FONT_SHA256 = "9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732"
PMENU_FONT_BYTE_SIZE = 79722
PMENU_FONT_ATLAS_SIZE = (1526, 17)
PMENU_FONT_NATIVE_LINE_HEIGHT = 18

# PTitleMenuRow::0x47A7E0 and PChildMenuRow::0x47A990 build the same
# two grayscale component triples before the row-background setup call. Since
# every component is equal within each triple, no display-mask channel naming
# assumption is required.
PMENU_ROW_COLOR_COMPONENTS = ((0, 0, 0), (255, 255, 255))

PMENU_BACKGROUND_STATE_METHOD_VA = 0x47AC00
PMENU_ANIMATION_STATE_METHOD_VA = 0x652AE0
PMENU_ANIMATION_TRANSITION_METHOD_VA = 0x652780
PMENU_ANIMATION_STEP_METHOD_VA = 0x6527F0
PMENU_CHILD_ARROW_SOURCE_Y_METHOD_VA = 0x652860
PMENU_CHILD_ARROW_FRAME_COUNT_METHOD_VA = 0x5D62F0
PMENU_TITLE_ARROW_SOURCE_Y_METHOD_VA = 0x4825A0
PMENU_TITLE_ARROW_FRAME_COUNT_METHOD_VA = 0x5D50E0
PMENU_STATE_BIT_1 = 0x2
PMENU_STATE_BIT_3 = 0x8
PMENU_STATE_BIT_15 = 0x8000
PMENU_ANIMATION_STATES = (0, 1, 2)


def pmenu_background_row_index(state_bits: int) -> int:
    """Mirror MenuBackgroundToggle::0x47AC00 as an atlas-row index.

    The three source bits remain deliberately unnamed beyond their bit
    positions. The method itself selects 3/2/1/0 multiples of the source frame
    height in the order below.
    """
    if type(state_bits) is not int or state_bits < 0:
        raise OriginalPMenuChromeError("PMenu state bits must be a non-negative integer")
    if not state_bits & PMENU_STATE_BIT_1:
        return 3
    if state_bits & PMENU_STATE_BIT_15:
        return 2
    if state_bits & PMENU_STATE_BIT_3:
        return 1
    return 0


def pmenu_background_source_y(state_bits: int) -> int:
    return pmenu_background_row_index(state_bits) * PMENU_ROW_HEIGHT

def pmenu_arrow_state_from_bits(state_bits: int) -> int:
    """Mirror the neutral three-state selector at 0x652AE0.

    State names are deliberately not inferred. Bit 1 clear selects state 2;
    otherwise bit 15 selects state 1 and the remaining case is state 0.
    """
    if type(state_bits) is not int or state_bits < 0:
        raise OriginalPMenuChromeError("PMenu state bits must be a non-negative integer")
    if not state_bits & PMENU_STATE_BIT_1:
        return 2
    if state_bits & PMENU_STATE_BIT_15:
        return 1
    return 0


def _require_animation_state(state: int) -> int:
    if type(state) is not int or state not in PMENU_ANIMATION_STATES:
        raise OriginalPMenuChromeError("PMenu arrow state must be 0, 1 or 2")
    return state


def pmenu_child_arrow_frame_count(state: int) -> int:
    """Mirror generic child-arrow frame-count method 0x5D62F0."""
    state = _require_animation_state(state)
    return 1 if state == 2 else 11


def pmenu_title_arrow_frame_count(state: int) -> int:
    """Mirror MenuTitleArrow frame-count override 0x5D50E0."""
    state = _require_animation_state(state)
    return 11 if state == 0 else 1


def pmenu_arrow_transition_frame(
    old_state: int,
    old_frame: int,
    new_state: int,
    *,
    title: bool,
) -> int:
    """Mirror 0x652780's proportional frame carry across state transitions."""
    old_state = _require_animation_state(old_state)
    new_state = _require_animation_state(new_state)
    if type(old_frame) is not int or old_frame < 0:
        raise OriginalPMenuChromeError("PMenu arrow frame must be a non-negative integer")
    count = pmenu_title_arrow_frame_count if title else pmenu_child_arrow_frame_count
    old_count = count(old_state)
    new_count = count(new_state)
    if old_frame >= old_count:
        raise OriginalPMenuChromeError("PMenu arrow frame exceeds source state frame count")
    return (new_count * old_frame) // old_count


def pmenu_arrow_update(
    state: int,
    frame: int,
    state_bits: int,
    *,
    title: bool,
) -> tuple[int, int]:
    """Mirror state remap + one 0x6527F0 animation tick.

    Bit 3 controls whether the current frame advances toward the end of the
    selected state's frame range or retreats toward frame zero. The bit remains
    deliberately unnamed beyond its source position.
    """
    state = _require_animation_state(state)
    if type(frame) is not int or frame < 0:
        raise OriginalPMenuChromeError("PMenu arrow frame must be a non-negative integer")
    if type(state_bits) is not int or state_bits < 0:
        raise OriginalPMenuChromeError("PMenu state bits must be a non-negative integer")
    count = pmenu_title_arrow_frame_count if title else pmenu_child_arrow_frame_count
    if frame >= count(state):
        raise OriginalPMenuChromeError("PMenu arrow frame exceeds source state frame count")

    target = pmenu_arrow_state_from_bits(state_bits)
    if target != state:
        frame = pmenu_arrow_transition_frame(state, frame, target, title=title)
        state = target

    if state_bits & PMENU_STATE_BIT_3:
        if frame + 1 < count(state):
            frame += 1
    elif frame:
        frame -= 1
    return state, frame


def pmenu_child_arrow_source_row(state: int, frame: int) -> int:
    """Mirror generic source-offset method 0x652860 as a row index."""
    state = _require_animation_state(state)
    if type(frame) is not int or frame < 0 or frame >= pmenu_child_arrow_frame_count(state):
        raise OriginalPMenuChromeError("PMenu child-arrow frame is outside its state")
    return sum(pmenu_child_arrow_frame_count(value) for value in range(state)) + frame


def pmenu_title_arrow_source_row(state: int, frame: int) -> int:
    """Mirror MenuTitleArrow source-offset override 0x4825A0."""
    state = _require_animation_state(state)
    if type(frame) is not int or frame < 0 or frame >= pmenu_title_arrow_frame_count(state):
        raise OriginalPMenuChromeError("PMenu title-arrow frame is outside its state")
    if state == 0:
        return frame
    if state == 1:
        return pmenu_title_arrow_frame_count(0) - 1
    return 0



@dataclass(frozen=True)
class OriginalPMenuResource:
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    frame_height: int
    path_literal_va: int
    raw_handle_va: int
    wrapper_va: int
    owner_class: str
    setup_va: int

    @property
    def frame_count(self) -> int:
        width, height = self.size
        del width
        if type(self.frame_height) is not int or self.frame_height <= 0:
            raise OriginalPMenuChromeError(
                f"{self.source_path} has an invalid native frame height"
            )
        if height % self.frame_height:
            raise OriginalPMenuChromeError(
                f"{self.source_path} height is not a whole native frame stack"
            )
        return height // self.frame_height


PMENU_TITLE_ARROW_RESOURCE = OriginalPMenuResource(
    "FM2001_Art/Generic/menu_popup/menu_arrow_anim.444",
    "45d34aea3d4ae3f85a171fe3e6eb1b28ea960f5f500f123d98bcbbab52d22006",
    26248,
    (30, 638),
    58,
    0x837C4C,
    0x943870,
    0x943850,
    PMENU_TITLE_ROW_CLASS,
    PMENU_TITLE_ROW_SETUP_VA,
)
PMENU_TITLE_BOX_RESOURCE = OriginalPMenuResource(
    "FM2001_Art/Generic/menu_popup/submenu_main_box.444",
    "37bc920cb734cde0ac8891d240341f06319c4d1827cdd03a9c4ef8137e30791c",
    5700,
    (168, 87),
    29,
    0x837C80,
    0x943830,
    0x943810,
    PMENU_TITLE_ROW_CLASS,
    PMENU_TITLE_ROW_SETUP_VA,
)
PMENU_CHILD_ARROW_RESOURCE = OriginalPMenuResource(
    "FM2001_Art/Generic/menu_popup/menu_anim.444",
    "de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22",
    22768,
    (30, 667),
    29,
    0x837C20,
    0x9438B0,
    0x943890,
    PMENU_CHILD_ROW_CLASS,
    PMENU_CHILD_ROW_SETUP_VA,
)
PMENU_CHILD_BOX_RESOURCE = OriginalPMenuResource(
    "FM2001_Art/Generic/menu_popup/menu_main_box.444",
    "4cc1becee669f1f55749a58051eca8833ed582b1f45754c18485366dd6715007",
    6864,
    (168, 116),
    29,
    0x837CB4,
    0x9437F0,
    0x9437D0,
    PMENU_CHILD_ROW_CLASS,
    PMENU_CHILD_ROW_SETUP_VA,
)

PMENU_RESOURCES = (
    PMENU_TITLE_ARROW_RESOURCE,
    PMENU_TITLE_BOX_RESOURCE,
    PMENU_CHILD_ARROW_RESOURCE,
    PMENU_CHILD_BOX_RESOURCE,
)


@dataclass(frozen=True)
class OriginalPMenuNode:
    menu_id: int
    label_global_va: int
    aux_global_va: int | None
    children_array_va: int | None
    english_index: int | None = None
    original_text: str | None = None

    def require_original_text(self) -> str:
        if self.english_index is None or self.original_text is None:
            raise OriginalPMenuChromeError(
                f"PMenu node {self.menu_id:#x} label global "
                f"{self.label_global_va:#x} is not language-correlated"
            )
        return self.original_text


# Exact PMenu-related assignments recovered from the 2,714-entry English.idx
# loader at 0x635F30..0x64C7D4. Early entries happen to occupy a descending
# 0x9847F8 array, but later menu labels are deliberately stored in other
# globals, so a global arithmetic formula would be false beyond that prefix.
PMENU_ENGLISH_ENTRY_GLOBALS = {
    39: 0x98475C,
    43: 0x98474C,
    44: 0x984748,
    47: 0x98473C,
    48: 0x984738,
    51: 0x98472C,
    52: 0x984728,
    53: 0x984724,
    54: 0x984720,
    59: 0x98470C,
    60: 0x984708,
    62: 0x984700,
    63: 0x9846FC,
    67: 0x9846EC,
    68: 0x9846E8,
    69: 0x9846E4,
    71: 0x9846DC,
    72: 0x9846D8,
    661: 0x983DA4,
    738: 0x983C70,
    1847: 0x982B1C,
    1872: 0x982AB8,
    1976: 0x982918,
    1977: 0x982914,
    2391: 0x98229C,
    2392: 0x982298,
    2393: 0x982294,
    2394: 0x982290,
    2396: 0x982288,
    2432: 0x9821F8,
    2482: 0x982130,
    2516: 0x9820A8,
    2517: 0x9820A4,
    2518: 0x9820A0,
    2519: 0x98209C,
    2520: 0x982098,
    2521: 0x982094,
    2522: 0x982090,
}


def main_english_global_va(index: int) -> int:
    """Return the exact loader-assigned global for a source-proven menu entry."""
    if type(index) is not int or index < 0:
        raise OriginalPMenuChromeError("English index must be a non-negative integer")
    try:
        return PMENU_ENGLISH_ENTRY_GLOBALS[index]
    except KeyError as exc:
        raise OriginalPMenuChromeError(
            f"English entry {index} is not mapped for PMenu"
        ) from exc


def _node(
    menu_id: int,
    label_global_va: int,
    aux_global_va: int | None,
    children_array_va: int | None,
    english_index: int | None = None,
    original_text: str | None = None,
) -> OriginalPMenuNode:
    if (english_index is None) != (original_text is None):
        raise OriginalPMenuChromeError(
            "PMenu language identity requires both index and exact original text"
        )
    if english_index is not None and main_english_global_va(english_index) != label_global_va:
        raise OriginalPMenuChromeError(
            f"PMenu English/global mismatch for node {menu_id:#x}"
        )
    return OriginalPMenuNode(
        menu_id,
        label_global_va,
        aux_global_va,
        children_array_va,
        english_index,
        original_text,
    )


# Root array 0x947638, preserved in executable construction order.
PMENU_ROOT_NODES = (
    _node(2, 0x98475C, 0x9832CC, 0x9479C8, 39, "Team"),
    _node(3, 0x982298, 0x9832C8, 0x947968, 2392, "Transfers"),
    _node(0x259, 0x982B1C, 0x9836E8, 0x947728, 1847, "Calendar"),
    _node(6, 0x982098, None, 0x947830, 2520, "TABLES"),
    _node(7, 0x98474C, 0x9832BC, 0x9477D0, 43, "Analysis"),
    _node(4, 0x982094, None, 0x9478D8, 2521, "ADMIN"),
    _node(5, 0x98209C, None, 0x947878, 2519, "ACCOUNTS"),
    _node(1, 0x984748, 0x9832B8, 0x947A70, 44, "EAMail"),
    _node(8, 0x9820A0, None, 0x947770, 2518, "GAME OPTIONS"),
)

PMENU_TEAM_CHILDREN = (
    _node(0xCE, 0x982918, 0x983714, None, 1976, "Squad"),
    _node(0xCA, 0x984738, 0x983710, None, 48, "Stats"),
    _node(0xCB, 0x98229C, 0x983708, None, 2391, "Indiv. Orders"),
    _node(0xCC, 0x984724, 0x983704, None, 53, "Team Orders"),
    _node(0xCD, 0x984720, 0x983700, None, 54, "Training"),
    _node(0xCF, 0x98470C, 0x9836EC, None, 59, "Youth Team"),
)
PMENU_TRANSFER_CHILDREN = (
    _node(0x12D, 0x982294, 0x9836FC, None, 2393, "Transfer List"),
    _node(0x12E, 0x982290, 0x9836F4, None, 2394, "Scouts"),
    _node(0x12F, 0x982130, None, None, 2482, "Player/Club Search"),
)
PMENU_DIRECT_259_CHILDREN = (
    _node(0x259, 0x982B1C, 0x9836E8, None, 1847, "Calendar"),
    _node(0x25C, 0x9821F8, 0x9836E4, None, 2432, "League Fixtures"),
)
PMENU_TABLES_CHILDREN = (
    _node(0x25A, 0x9846DC, 0x9836E0, None, 71, "League Tables"),
    _node(0x25B, 0x9846D8, 0x9836DC, None, 72, "Cup Tables"),
)
PMENU_ANALYSIS_CHILDREN = (
    _node(0x2BD, 0x983C70, 0x9836D8, None, 738, "Charts"),
    _node(0x2BE, 0x983DA4, 0x9836D4, None, 661, "RATINGS"),
    _node(0x2BF, 0x982288, 0x9836D0, None, 2396, "Trophy Cupboard"),
)
PMENU_ADMIN_FAMILY_CHILDREN = (
    _node(0x191, 0x982914, 0x983290, None, 1977, "Overview"),
    _node(0x192, 0x982AB8, 0x982A5C, None, 1872, "Support Staff"),
    _node(0x193, 0x9846EC, 0x983290, None, 67, "Stadium"),
    _node(0x194, 0x9846E8, 0x98328C, None, 68, "Development"),
    _node(0x195, 0x9846E4, 0x983288, None, 69, "Maintenance"),
)
PMENU_FINANCE_FAMILY_CHILDREN = (
    _node(0x1F5, 0x984708, 0x9832AC, None, 60, "Cash Flow"),
    _node(0x1F6, 0x984700, 0x9832A4, None, 62, "Tickets"),
    _node(0x1F7, 0x9846FC, 0x98329C, None, 63, "Contracts"),
)
PMENU_EAMAIL_CHILDREN = (
    _node(0x65, 0x984748, 0x9836C8, None, 44, "EAMail"),
)
PMENU_SYSTEM_CHILDREN = (
    _node(0x321, 0x9820A8, None, None, 2516, "SAVE GAME"),
    _node(0x322, 0x9820A4, None, None, 2517, "SETTINGS"),
    _node(0x323, 0x982090, None, None, 2522, "RETURN TO MAIN MENU"),
)

PMENU_CHILDREN_BY_ARRAY_VA = {
    0x9479C8: PMENU_TEAM_CHILDREN,
    0x947968: PMENU_TRANSFER_CHILDREN,
    0x947728: PMENU_DIRECT_259_CHILDREN,
    0x947830: PMENU_TABLES_CHILDREN,
    0x9477D0: PMENU_ANALYSIS_CHILDREN,
    0x9478D8: PMENU_ADMIN_FAMILY_CHILDREN,
    0x947878: PMENU_FINANCE_FAMILY_CHILDREN,
    0x947A70: PMENU_EAMAIL_CHILDREN,
    0x947770: PMENU_SYSTEM_CHILDREN,
}

# This separate array is source-proven but is not promoted to the main root tree
# until its owning navigation path is traced.
PMENU_SEPARATE_TEAM_ORDER_ARRAY_VA = 0x9475A0
PMENU_SEPARATE_TEAM_ORDER_NODES = (
    _node(0x3E9, 0x98473C, 0x983714, None, 47, "Formation"),
    _node(0x3EA, 0x984738, 0x983710, None, 48, "Stats"),
    _node(0x3EB, 0x98472C, None, None, 51, "Ind Orders"),
    _node(0x3EC, 0x984728, 0x983708, None, 52, "Specific Roles"),
    _node(0x3ED, 0x984724, 0x983704, None, 53, "Team Orders"),
)


def validate_original_pmenu_resources(
    source_root: Path,
) -> tuple[OriginalPMenuResource, ...]:
    """Require the four exact source-bound PMenu row assets."""
    root = Path(source_root)
    for resource in PMENU_RESOURCES:
        path = root / resource.source_path
        data = path.read_bytes()
        if len(data) != resource.byte_size:
            raise OriginalPMenuChromeError(
                f"Original PMenu resource byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalPMenuChromeError(
                f"Original PMenu resource checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalPMenuChromeError(
                f"Original PMenu resource geometry mismatch: {resource.source_path}"
            )
        resource.frame_count
    return PMENU_RESOURCES


def validate_original_pmenu_font(source_root: Path) -> EAFont:
    """Require the exact source-proven PMenu Zurich 16px font."""
    path = Path(source_root) / PMENU_FONT_SOURCE_PATH
    data = path.read_bytes()
    if len(data) != PMENU_FONT_BYTE_SIZE:
        raise OriginalPMenuChromeError("Original PMenu font byte-size mismatch")
    if sha256(data).hexdigest() != PMENU_FONT_SHA256:
        raise OriginalPMenuChromeError("Original PMenu font checksum mismatch")
    font = EAFont.from_bytes(data)
    if (font.atlas_width, font.atlas_height) != PMENU_FONT_ATLAS_SIZE:
        raise OriginalPMenuChromeError("Original PMenu font atlas geometry mismatch")
    if font.native_line_height() != PMENU_FONT_NATIVE_LINE_HEIGHT:
        raise OriginalPMenuChromeError("Original PMenu font line-height mismatch")
    return font
