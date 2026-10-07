"""Source-qualified application-owned FM2001 management header.

The canonical executable constructs the event-2 compound at (599,0), size
100x95, with the 30x95 back_4_anim child, the 70x95 back_4 child and the
Zurich 24px MENU caption.  The native state selector/update chain is shared
with the already-qualified Gate-13 bitmap controls; the two child overrides
below are the management-header-specific group/source-row methods.

No wall-clock animation rate is invented here.  The host advances this state
once per eligible serialized UI/idle pass, matching the Gate-13 Button timing
boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_header import parse_ea444_header
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from ea_font import EAFont


class OriginalManagementHeaderError(ValueError):
    """The final management-header source contract is incomplete or invalid."""


HEADER_COMPOUND_RECT = (599, 0, 100, 95)
HEADER_LEFT_RECT = (599, 0, 30, 95)
HEADER_RIGHT_RECT = (629, 0, 70, 95)
HEADER_CAPTION_RECT = (631, 62, 70, 30)
HEADER_CAPTION_STYLE = 10
HEADER_FRAME_HEIGHT = 95

HEADER_ENABLED_MASK = 0x2
HEADER_ADVANCE_MASK = 0x8
HEADER_SELECTED_MASK = 0x8000
HEADER_STATE_SELECTOR_VA = 0x652AE0
HEADER_STATE_TRANSITION_VA = 0x652780
HEADER_UPDATE_VA = 0x6527F0
HEADER_LEFT_GROUP_LENGTH_VA = 0x4314D0
HEADER_LEFT_SOURCE_ROW_VA = 0x431500
HEADER_RIGHT_GROUP_LENGTH_VA = 0x431570

# 0x4314D0 returns 26,1,0 for state groups 0,1,2.
# 0x431570 returns 2,1,1 for the companion four-frame control.
HEADER_LEFT_GROUP_LENGTHS = (26, 1, 0)
HEADER_RIGHT_GROUP_LENGTHS = (2, 1, 1)


@dataclass(frozen=True)
class OriginalManagementHeaderResource:
    role: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    destination_rect: tuple[int, int, int, int]

    @property
    def frame_count(self) -> int:
        width, height = self.size
        del width
        if height % HEADER_FRAME_HEIGHT:
            raise OriginalManagementHeaderError(
                f"{self.source_path} is not a whole 95px source-frame stack"
            )
        return height // HEADER_FRAME_HEIGHT


HEADER_LEFT_RESOURCE = OriginalManagementHeaderResource(
    role="left_anim",
    source_path="FM2001_Art/Generic/Background_buttons/back_4_anim.444",
    sha256="867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69",
    byte_size=99968,
    size=(30, 4845),
    destination_rect=HEADER_LEFT_RECT,
)
HEADER_RIGHT_RESOURCE = OriginalManagementHeaderResource(
    role="right_state",
    source_path="FM2001_Art/Generic/Background_buttons/back_4.444",
    sha256="710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb",
    byte_size=5476,
    size=(70, 380),
    destination_rect=HEADER_RIGHT_RECT,
)
HEADER_RESOURCES = (HEADER_LEFT_RESOURCE, HEADER_RIGHT_RESOURCE)

HEADER_FONT_SOURCE_PATH = "Fonts/Zurich_XCn_BT_24pixel.fnt"
HEADER_FONT_SHA256 = "f165d39423a9f20532132d2bd9a3c53aba4244531aa3291a73502fa956a46405"
HEADER_FONT_BYTE_SIZE = 95276
HEADER_FONT_OBJECT_VA = 0x8B0760
HEADER_CAPTION_GLOBAL_VA = 0x9820F4
HEADER_CAPTION_ENGLISH_INDEX = 2497
HEADER_CAPTION_TEXT = "MENU"
HEADER_CAPTION_NATIVE_COLOR_16 = 0xFFFF

# Recovery 396/398 source-closed central management date control.  The two
# y=34/y=51 match lines remain intentionally absent until 0x615D10/0x615DA0
# filtering is semantically closed.
HEADER_MATCH_COMPETITION_RECT = (172, 34, 378, 16)
HEADER_MATCHUP_RECT = (172, 51, 378, 16)
HEADER_DATE_RECT = (172, 68, 378, 16)
HEADER_CENTRAL_TEXT_RAW_STYLE = 0x2102
HEADER_CENTRAL_TEXT_NATIVE_COLOR_16 = 0xFFFF
HEADER_DATE_REFRESH_VA = 0x432710
HEADER_DATE_FORMATTER_VA = 0x64D150
HEADER_DATE_TEMPLATE_GLOBAL_VA = 0x983FE4
HEADER_DATE_ENGLISH_INDEX = 517
HEADER_DATE_TEMPLATE = "Today is %D %M %Yf"
HEADER_DATE_FONT_OBJECT_VA = 0x8CAB80
HEADER_DATE_FONT_SOURCE_PATH = "Fonts/Zurich_XCn_BT_18pixel.fnt"
HEADER_DATE_FONT_SHA256 = (
    "968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a"
)
HEADER_DATE_FONT_BYTE_SIZE = 79_734
HEADER_DATE_FONT_ATLAS_SIZE = (1366, 19)
HEADER_DATE_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


@dataclass(frozen=True)
class OriginalManagementHeaderResources:
    left_anim: EA444DecodedImage
    right_state: EA444DecodedImage
    font: EAFont
    date_font: EAFont

    def __post_init__(self) -> None:
        if (self.left_anim.width, self.left_anim.height) != HEADER_LEFT_RESOURCE.size:
            raise OriginalManagementHeaderError("back_4_anim decoded geometry mismatch")
        if (self.right_state.width, self.right_state.height) != HEADER_RIGHT_RESOURCE.size:
            raise OriginalManagementHeaderError("back_4 decoded geometry mismatch")
        if (self.date_font.atlas_width, self.date_font.atlas_height) != HEADER_DATE_FONT_ATLAS_SIZE:
            raise OriginalManagementHeaderError("Central date font atlas geometry mismatch")


@dataclass(frozen=True)
class OriginalManagementHeaderFrame:
    """One source-qualified physical frame pair.

    The left control's disabled group has native length zero, so None means
    the source contributes no left bitmap in that state.
    """

    left_source_row: int | None
    right_source_row: int

    def __post_init__(self) -> None:
        if (
            self.left_source_row is not None
            and (
                type(self.left_source_row) is not int
                or not 0 <= self.left_source_row < HEADER_LEFT_RESOURCE.frame_count
            )
        ):
            raise OriginalManagementHeaderError(
                "left management-header source row is outside back_4_anim"
            )
        if (
            type(self.right_source_row) is not int
            or not 0 <= self.right_source_row < HEADER_RIGHT_RESOURCE.frame_count
        ):
            raise OriginalManagementHeaderError(
                "right management-header source row is outside back_4"
            )


@dataclass(frozen=True)
class OriginalManagementHeaderOverlay:
    role: str
    source_path: str
    source_row: int
    x: int
    y: int
    width: int
    height: int
    rgba: bytes


@dataclass(frozen=True)
class OriginalManagementHeaderCaptionOverlay:
    text: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    native_color_16: int = HEADER_CAPTION_NATIVE_COLOR_16


@dataclass(frozen=True)
class OriginalManagementHeaderDateOverlay:
    text: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    control_rect: tuple[int, int, int, int] = HEADER_DATE_RECT
    raw_style: int = HEADER_CENTRAL_TEXT_RAW_STYLE
    native_color_16: int = HEADER_CENTRAL_TEXT_NATIVE_COLOR_16
    font_source_path: str = HEADER_DATE_FONT_SOURCE_PATH


@dataclass(frozen=True)
class OriginalManagementHeaderMatchOverlay:
    role: str
    text: str
    x: int
    y: int
    width: int
    height: int
    rgba: bytes
    control_rect: tuple[int, int, int, int]
    raw_style: int = HEADER_CENTRAL_TEXT_RAW_STYLE
    native_color_16: int = HEADER_CENTRAL_TEXT_NATIVE_COLOR_16
    font_source_path: str = HEADER_DATE_FONT_SOURCE_PATH


def _validate_source_file(root: Path, resource: OriginalManagementHeaderResource) -> bytes:
    path = root / resource.source_path
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementHeaderError(
            f"Missing exact original management-header resource: {resource.source_path}"
        ) from exc
    if len(raw) != resource.byte_size:
        raise OriginalManagementHeaderError(
            f"Management-header byte-size mismatch: {resource.source_path}"
        )
    if sha256(raw).hexdigest() != resource.sha256:
        raise OriginalManagementHeaderError(
            f"Management-header checksum mismatch: {resource.source_path}"
        )
    header = parse_ea444_header(raw)
    if (header.width, header.height) != resource.size:
        raise OriginalManagementHeaderError(
            f"Management-header geometry mismatch: {resource.source_path}"
        )
    return raw


def validate_management_header_font(source_root: str | Path) -> EAFont:
    root = Path(source_root)
    path = root / HEADER_FONT_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementHeaderError(
            f"Missing exact original management-header font: {HEADER_FONT_SOURCE_PATH}"
        ) from exc
    if len(raw) != HEADER_FONT_BYTE_SIZE:
        raise OriginalManagementHeaderError("Management-header font byte-size mismatch")
    if sha256(raw).hexdigest() != HEADER_FONT_SHA256:
        raise OriginalManagementHeaderError("Management-header font checksum mismatch")
    return EAFont.from_bytes(raw)


def validate_management_header_date_font(source_root: str | Path) -> EAFont:
    root = Path(source_root)
    path = root / HEADER_DATE_FONT_SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalManagementHeaderError(
            f"Missing exact original central-date font: {HEADER_DATE_FONT_SOURCE_PATH}"
        ) from exc
    if len(raw) != HEADER_DATE_FONT_BYTE_SIZE:
        raise OriginalManagementHeaderError("Central-date font byte-size mismatch")
    if sha256(raw).hexdigest() != HEADER_DATE_FONT_SHA256:
        raise OriginalManagementHeaderError("Central-date font checksum mismatch")
    font = EAFont.from_bytes(raw)
    if (font.atlas_width, font.atlas_height) != HEADER_DATE_FONT_ATLAS_SIZE:
        raise OriginalManagementHeaderError("Central-date font atlas geometry mismatch")
    return font


def load_verified_management_header_resources(
    source_root: str | Path,
    original_executable: str | Path,
) -> OriginalManagementHeaderResources:
    """Checksum-gate and decode only the exact source-qualified header family."""
    root = Path(source_root)
    left_raw = _validate_source_file(root, HEADER_LEFT_RESOURCE)
    right_raw = _validate_source_file(root, HEADER_RIGHT_RESOURCE)
    font = validate_management_header_font(root)
    date_font = validate_management_header_date_font(root)

    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    left = decode_ea444(left_raw, tables=tables, quant=quant)
    right = decode_ea444(right_raw, tables=tables, quant=quant)
    return OriginalManagementHeaderResources(left, right, font, date_font)


def _crop_frame(image: EA444DecodedImage, source_row: int) -> bytes:
    if type(source_row) is not int or source_row < 0:
        raise OriginalManagementHeaderError(
            "Management-header source row must be a non-negative integer"
        )
    if image.height % HEADER_FRAME_HEIGHT:
        raise OriginalManagementHeaderError(
            "Decoded management-header atlas has non-native frame height"
        )
    frame_count = image.height // HEADER_FRAME_HEIGHT
    if source_row >= frame_count:
        raise OriginalManagementHeaderError(
            "Management-header source row exceeds decoded atlas"
        )
    stride = image.width * 4
    start = source_row * HEADER_FRAME_HEIGHT * stride
    end = start + HEADER_FRAME_HEIGHT * stride
    return image.rgba[start:end]


def management_header_group_for_flags(flags: int) -> int:
    """Mirror shared state selector 0x652AE0."""
    if type(flags) is not int or flags < 0:
        raise OriginalManagementHeaderError("Management-header flags must be non-negative")
    if not flags & HEADER_ENABLED_MASK:
        return 2
    if flags & HEADER_SELECTED_MASK:
        return 1
    return 0


def _transition_subframe(
    old_group: int,
    old_subframe: int,
    new_group: int,
    lengths: tuple[int, int, int],
) -> int:
    if not 0 <= old_group < 3 or not 0 <= new_group < 3:
        raise OriginalManagementHeaderError("Management-header group is outside 0..2")
    old_length = lengths[old_group]
    new_length = lengths[new_group]
    if old_length <= 0 or new_length <= 0:
        return 0
    if not 0 <= old_subframe < old_length:
        raise OriginalManagementHeaderError(
            "Management-header subframe exceeds source group"
        )
    return new_length * old_subframe // old_length


def _update_control(
    group: int,
    subframe: int,
    flags: int,
    lengths: tuple[int, int, int],
) -> tuple[int, int, bool]:
    target = management_header_group_for_flags(flags)
    changed = False
    if target != group:
        subframe = _transition_subframe(group, subframe, target, lengths)
        group = target
        changed = True

    length = lengths[group]
    if length <= 0:
        return group, 0, changed
    if not 0 <= subframe < length:
        raise OriginalManagementHeaderError(
            "Management-header subframe exceeds source group"
        )
    if flags & HEADER_ADVANCE_MASK:
        if subframe + 1 < length:
            subframe += 1
            changed = True
    elif subframe:
        subframe -= 1
        changed = True
    return group, subframe, changed


def management_header_left_source_row(group: int, subframe: int) -> int | None:
    """Mirror the 0x431500 physical-row mapping for back_4_anim."""
    if type(group) is not int or not 0 <= group < 3:
        raise OriginalManagementHeaderError("Left management-header group is invalid")
    length = HEADER_LEFT_GROUP_LENGTHS[group]
    if length == 0:
        return None
    if type(subframe) is not int or not 0 <= subframe < length:
        raise OriginalManagementHeaderError("Left management-header subframe is invalid")
    if group == 0:
        return subframe
    if group == 1:
        return 50
    raise OriginalManagementHeaderError("Unreachable left management-header group")


def management_header_right_source_row(group: int, subframe: int) -> int:
    """Map the 2/1/1 companion groups contiguously onto back_4 rows 0..3."""
    if type(group) is not int or not 0 <= group < 3:
        raise OriginalManagementHeaderError("Right management-header group is invalid")
    length = HEADER_RIGHT_GROUP_LENGTHS[group]
    if type(subframe) is not int or not 0 <= subframe < length:
        raise OriginalManagementHeaderError("Right management-header subframe is invalid")
    return sum(HEADER_RIGHT_GROUP_LENGTHS[:group]) + subframe


@dataclass
class OriginalManagementHeaderState:
    """Live state adapter driven by the recovered shared update path."""

    flags: int = HEADER_ENABLED_MASK
    left_group: int = 0
    left_subframe: int = 0
    right_group: int = 0
    right_subframe: int = 0

    def set_pointer_inside(self, inside: bool) -> None:
        if type(inside) is not bool:
            raise OriginalManagementHeaderError("Header pointer state must be boolean")
        if inside:
            self.flags |= HEADER_ADVANCE_MASK
        else:
            self.flags &= ~HEADER_ADVANCE_MASK

    def set_selected(self, selected: bool) -> None:
        if type(selected) is not bool:
            raise OriginalManagementHeaderError("Header selected state must be boolean")
        if selected:
            self.flags |= HEADER_SELECTED_MASK
        else:
            self.flags &= ~HEADER_SELECTED_MASK

    def set_enabled(self, enabled: bool) -> None:
        if type(enabled) is not bool:
            raise OriginalManagementHeaderError("Header enabled state must be boolean")
        if enabled:
            self.flags |= HEADER_ENABLED_MASK
        else:
            self.flags &= ~HEADER_ENABLED_MASK

    def pending(self) -> bool:
        target = management_header_group_for_flags(self.flags)
        for group, subframe, lengths in (
            (self.left_group, self.left_subframe, HEADER_LEFT_GROUP_LENGTHS),
            (self.right_group, self.right_subframe, HEADER_RIGHT_GROUP_LENGTHS),
        ):
            if target != group:
                return True
            length = lengths[group]
            if length > 0:
                if self.flags & HEADER_ADVANCE_MASK:
                    if subframe + 1 < length:
                        return True
                elif subframe:
                    return True
        return False

    def update(self) -> bool:
        self.left_group, self.left_subframe, left_changed = _update_control(
            self.left_group,
            self.left_subframe,
            self.flags,
            HEADER_LEFT_GROUP_LENGTHS,
        )
        self.right_group, self.right_subframe, right_changed = _update_control(
            self.right_group,
            self.right_subframe,
            self.flags,
            HEADER_RIGHT_GROUP_LENGTHS,
        )
        return left_changed or right_changed

    def source_frame(self) -> OriginalManagementHeaderFrame:
        return OriginalManagementHeaderFrame(
            management_header_left_source_row(self.left_group, self.left_subframe),
            management_header_right_source_row(self.right_group, self.right_subframe),
        )


def management_header_overlays(
    resources: OriginalManagementHeaderResources,
    frame: OriginalManagementHeaderFrame,
) -> tuple[OriginalManagementHeaderOverlay, ...]:
    """Crop the already-qualified native source rows for host composition."""
    if not isinstance(resources, OriginalManagementHeaderResources):
        raise OriginalManagementHeaderError(
            "Header overlay rendering requires verified source resources"
        )
    if not isinstance(frame, OriginalManagementHeaderFrame):
        raise OriginalManagementHeaderError(
            "Header overlay rendering requires a qualified source frame"
        )

    overlays: list[OriginalManagementHeaderOverlay] = []
    if frame.left_source_row is not None:
        left_rgba = _crop_frame(resources.left_anim, frame.left_source_row)
        lx, ly, lw, lh = HEADER_LEFT_RECT
        overlays.append(
            OriginalManagementHeaderOverlay(
                "left_anim",
                HEADER_LEFT_RESOURCE.source_path,
                frame.left_source_row,
                lx,
                ly,
                lw,
                lh,
                left_rgba,
            )
        )

    right_rgba = _crop_frame(resources.right_state, frame.right_source_row)
    rx, ry, rw, rh = HEADER_RIGHT_RECT
    overlays.append(
        OriginalManagementHeaderOverlay(
            "right_state",
            HEADER_RIGHT_RESOURCE.source_path,
            frame.right_source_row,
            rx,
            ry,
            rw,
            rh,
            right_rgba,
        )
    )
    return tuple(overlays)


def _clip_alpha(
    alpha: bytes,
    mask_width: int,
    mask_height: int,
    *,
    line_x: int,
    line_y: int,
    rect: tuple[int, int, int, int],
) -> tuple[int, int, int, int, bytes] | None:
    x, y, width, height = rect
    left = max(x, line_x)
    top = max(y, line_y)
    right = min(x + width, line_x + mask_width)
    bottom = min(y + height, line_y + mask_height)
    if left >= right or top >= bottom:
        return None

    out_width = right - left
    out_height = bottom - top
    src_x = left - line_x
    src_y = top - line_y
    clipped = bytearray(out_width * out_height)
    for row in range(out_height):
        src = (src_y + row) * mask_width + src_x
        dst = row * out_width
        clipped[dst:dst + out_width] = alpha[src:src + out_width]
    return left, top, out_width, out_height, bytes(clipped)


def management_header_caption_overlay(
    resources: OriginalManagementHeaderResources,
    *,
    text: str = HEADER_CAPTION_TEXT,
) -> OriginalManagementHeaderCaptionOverlay:
    """Rasterize the exact shipped MENU caption at the recovered text control."""
    if not isinstance(resources, OriginalManagementHeaderResources):
        raise OriginalManagementHeaderError(
            "Header caption rendering requires verified source resources"
        )
    if text != HEADER_CAPTION_TEXT:
        raise OriginalManagementHeaderError(
            "Management-header caption must be exact shipped MENU"
        )
    if HEADER_CAPTION_STYLE != 10:
        raise OriginalManagementHeaderError("Unexpected management-header text style")

    font = resources.font
    mask = font.render_text_alpha(text)
    x, y, width, _height = HEADER_CAPTION_RECT

    # Shared eCText draw semantics: style bit value 2 right-aligns. Style 10
    # contains no recovered vertical bottom/centre bit, so the line starts at y.
    line_x = x + width - font.measure_text(text)
    line_y = y
    clipped = _clip_alpha(
        mask.alpha,
        mask.width,
        mask.height,
        line_x=line_x,
        line_y=line_y,
        rect=HEADER_CAPTION_RECT,
    )
    if clipped is None:
        raise OriginalManagementHeaderError("MENU caption clips to no source pixels")
    out_x, out_y, out_width, out_height, alpha = clipped

    rgba = bytearray(len(alpha) * 4)
    for index, value in enumerate(alpha):
        pos = index * 4
        rgba[pos:pos + 4] = bytes((255, 255, 255, value))
    return OriginalManagementHeaderCaptionOverlay(
        text=text,
        x=out_x,
        y=out_y,
        width=out_width,
        height=out_height,
        rgba=bytes(rgba),
    )


def _central_text_rgba(
    resources: OriginalManagementHeaderResources,
    text: str,
    rect: tuple[int, int, int, int],
) -> tuple[int, int, int, int, bytes]:
    font = resources.date_font
    mask = font.render_text_alpha(text)
    x, y, width, height = rect
    line_x = x + width - font.measure_text(text)
    line_y = y + height // 2 - font.native_line_height() // 2
    clipped = _clip_alpha(
        mask.alpha,
        mask.width,
        mask.height,
        line_x=line_x,
        line_y=line_y,
        rect=rect,
    )
    if clipped is None:
        raise OriginalManagementHeaderError(
            "Central management text clips to no source pixels"
        )
    out_x, out_y, out_width, out_height, alpha = clipped
    rgba = bytearray(len(alpha) * 4)
    for index, value in enumerate(alpha):
        pos = index * 4
        rgba[pos:pos + 4] = bytes((255, 255, 255, value))
    return out_x, out_y, out_width, out_height, bytes(rgba)


def format_management_header_fixed_league_competition(competition_name: str) -> str:
    """Resolve %C %Rf{ Round} %Lf{ Leg} for ordinary fixed LeagueMatch.

    Recovery 402 closes the ordinary League virtual branches used by the
    formatter: %Rf contributes no suffix and LeagueMatch leg code is outside
    the first/second-leg cases, so the exact line is the competition name.
    """
    if not isinstance(competition_name, str) or not competition_name:
        raise OriginalManagementHeaderError(
            "Management header competition requires a source name"
        )
    return competition_name


def format_management_header_matchup(
    home_short_name: str,
    away_short_name: str,
    scheduled_date: date,
) -> str:
    """Apply the fixed-League %1s Vs %2s %D{%D %M %Y} expansion."""
    if (
        not isinstance(home_short_name, str)
        or not isinstance(away_short_name, str)
        or not home_short_name
        or not away_short_name
    ):
        raise OriginalManagementHeaderError(
            "Management header matchup requires source short club names"
        )
    if not isinstance(scheduled_date, date):
        raise OriginalManagementHeaderError(
            "Management header matchup requires a calendar date"
        )
    month = HEADER_DATE_MONTH_NAMES[scheduled_date.month - 1][:3]
    return (
        f"{home_short_name} Vs {away_short_name} "
        f"{scheduled_date.day} {month} {scheduled_date.year % 100:02d}"
    )


def management_header_match_overlays(
    resources: OriginalManagementHeaderResources,
    *,
    competition_name: str,
    home_short_name: str,
    away_short_name: str,
    scheduled_date: date,
) -> tuple[OriginalManagementHeaderMatchOverlay, OriginalManagementHeaderMatchOverlay]:
    """Rasterize the two source-closed conditional management match lines."""
    if not isinstance(resources, OriginalManagementHeaderResources):
        raise OriginalManagementHeaderError(
            "Match-line rendering requires verified management-header resources"
        )
    lines = (
        (
            "competition",
            format_management_header_fixed_league_competition(competition_name),
            HEADER_MATCH_COMPETITION_RECT,
        ),
        (
            "matchup",
            format_management_header_matchup(
                home_short_name,
                away_short_name,
                scheduled_date,
            ),
            HEADER_MATCHUP_RECT,
        ),
    )
    overlays = []
    for role, text, rect in lines:
        out_x, out_y, out_width, out_height, rgba = _central_text_rgba(
            resources, text, rect
        )
        overlays.append(OriginalManagementHeaderMatchOverlay(
            role=role,
            text=text,
            x=out_x,
            y=out_y,
            width=out_width,
            height=out_height,
            rgba=rgba,
            control_rect=rect,
        ))
    return tuple(overlays)


def format_management_header_date(value: date) -> str:
    """Apply the recovered English 0x64D150 %D %M %Yf expansion.

    %D is the unpadded numeric day, %M is the first three CP1252 bytes of the
    localized month string, and %Yf is the full four-digit year.
    """
    if not isinstance(value, date):
        raise OriginalManagementHeaderError("Management date must be a calendar date")
    month = HEADER_DATE_MONTH_NAMES[value.month - 1][:3]
    return f"Today is {value.day} {month} {value.year}"


def management_header_date_overlay(
    resources: OriginalManagementHeaderResources,
    current_date: date,
) -> OriginalManagementHeaderDateOverlay:
    """Rasterize the independently refreshed y=68 central date control."""
    if not isinstance(resources, OriginalManagementHeaderResources):
        raise OriginalManagementHeaderError(
            "Central date rendering requires verified management-header resources"
        )
    text = format_management_header_date(current_date)
    out_x, out_y, out_width, out_height, rgba = _central_text_rgba(
        resources,
        text,
        HEADER_DATE_RECT,
    )
    return OriginalManagementHeaderDateOverlay(
        text=text,
        x=out_x,
        y=out_y,
        width=out_width,
        height=out_height,
        rgba=rgba,
    )
