"""Source-exact TeamSelect hierarchy data, state, art and presentation.

The canonical executable establishes a 16-row country/competition group and a
24-row club group. This module mirrors recovered filtering, stable native
ordering, row-toggle state and source-frame transforms without embedding any
licensed source bytes in code. The visible club record index used for local row
state is deliberately not promoted to the gameplay backend until the native
selection-record payload identity is re-traced.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from hashlib import sha256
from typing import Iterable, Mapping

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import EA444Quantization
from ea444_tables import EA444Tables
from ea_font import EAFont, EATextMask
from original_button_frames import OriginalButtonFrame
from original_front_end_layout import (
    OriginalRect,
    TEAMSELECT_CLUB_CONTROL_IDS,
    TEAMSELECT_CLUB_ROW_ORIGINS,
    TEAMSELECT_ENGLISH_COUNTRY_ORDER,
    TEAMSELECT_HIERARCHY_CONTROL_IDS,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
)
from original_teamselect_hierarchy_art import OriginalTeamSelectHierarchyArt


TEAMSELECT_CLUB_ANIM_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_anim.444"
)
TEAMSELECT_CLUB_BARS_PATH = (
    "FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_bars.444"
)
TEAMSELECT_CLUB_ANIM_SHA256 = (
    "7f04cbe25499e26d2489781a7aa8c0135454dba5b9096ce4de580cf8bca32b88"
)
TEAMSELECT_CLUB_BARS_SHA256 = (
    "a0fafa8af76c7dd9b873de77814517a2ac20d88a7d70392311e277d7547ff6ac"
)
TEAMSELECT_LEAGUE_FONT_PATH = "Fonts/Zurich_BdXCn_BT_18pixel.fnt"
TEAMSELECT_CLUB_FONT_PATH = "Fonts/Zurich_BdXCn_BT_16pixel.fnt"
TEAMSELECT_LEAGUE_FONT_SHA256 = (
    "4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd"
)
TEAMSELECT_CLUB_FONT_SHA256 = (
    "9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732"
)

LEAGUE_ANIM_FRAME_SIZE = (30, 29)
LEAGUE_BAR_FRAME_SIZE = (168, 29)
CLUB_ANIM_FRAME_SIZE = (30, 19)
CLUB_BAR_FRAME_SIZE = (167, 19)
LEAGUE_GROUP_SIZE = (200, 29)
CLUB_GROUP_SIZE = (199, 19)


class TeamSelectNativeError(ValueError):
    pass


class NativeControlState(IntEnum):
    """Exact internal +0x4A states; names remain deliberately neutral."""

    NORMAL = 0
    ACTIVE = 1
    DISABLED = 2


class HierarchyRowKind(Enum):
    COUNTRY = "country"
    COMPETITION = "competition"


def animation_group_frame_count(state: NativeControlState | int) -> int:
    """Button child vtable +0xA8 (`0x5D62F0`)."""
    value = NativeControlState(int(state))
    return 1 if value is NativeControlState.DISABLED else 11


def bar_group_frame_count(state: NativeControlState | int) -> int:
    """Bar child vtable +0xA8 (`0x4D8D30`)."""
    value = NativeControlState(int(state))
    return 2 if value is NativeControlState.NORMAL else 1


def _source_index(
    state: NativeControlState | int,
    progress: int,
    count,
) -> int:
    value = NativeControlState(int(state))
    if type(progress) is not int or not 0 <= progress < count(value):
        raise TeamSelectNativeError("Native transition progress exceeds its group")
    return sum(count(previous) for previous in NativeControlState if previous < value) + progress


def animation_source_index(
    state: NativeControlState | int, progress: int = 0
) -> int:
    """Shared league/team animation source row (`0x652860` + `0x5D62F0`)."""
    return _source_index(state, progress, animation_group_frame_count)


def club_bar_source_index(
    state: NativeControlState | int, progress: int = 0
) -> int:
    """TeamBtnGrp bar source row (`0x652860` + `0x4D8D30`)."""
    return _source_index(state, progress, bar_group_frame_count)


def league_bar_source_index(
    state: NativeControlState | int,
    *,
    is_country: bool,
    progress: int = 0,
) -> int:
    """LeagueBtnGrp's country/competition-specific `0x4D8B10` transform."""
    value = NativeControlState(int(state))
    if type(progress) is not int or not 0 <= progress < bar_group_frame_count(value):
        raise TeamSelectNativeError("Native league-bar progress exceeds its group")
    if value is NativeControlState.NORMAL:
        return 0 if is_country and progress == 0 else progress + 1
    if value is NativeControlState.ACTIVE:
        return 3
    return 4


@dataclass(frozen=True)
class OriginalClubHierarchyStrip:
    path: str
    source_height: int
    frame_width: int
    frame_height: int
    frames: tuple[OriginalButtonFrame, ...]
    trailing_source_rows: int = 0

    def __post_init__(self) -> None:
        if self.source_height != len(self.frames) * self.frame_height + self.trailing_source_rows:
            raise TeamSelectNativeError("Club hierarchy strip height is inconsistent")
        if any(
            (frame.width, frame.height) != (self.frame_width, self.frame_height)
            for frame in self.frames
        ):
            raise TeamSelectNativeError("Club hierarchy frame geometry differs")

    def source_frame(self, index: int) -> OriginalButtonFrame:
        if type(index) is not int or not 0 <= index < len(self.frames):
            raise TeamSelectNativeError("Unknown club hierarchy source frame")
        return self.frames[index]


@dataclass(frozen=True)
class OriginalTeamSelectNativeInputs:
    club_animation: OriginalClubHierarchyStrip
    club_bars: OriginalClubHierarchyStrip
    league_font: EAFont
    club_font: EAFont

    def __post_init__(self) -> None:
        if len(self.club_animation.frames) != 23:
            raise TeamSelectNativeError("Team animation must expose 23 runtime frames")
        if len(self.club_bars.frames) != 4:
            raise TeamSelectNativeError("Team bars must expose four runtime frames")


def _split_club_strip(
    decoded: EA444DecodedImage,
    *,
    path: str,
    frame_size: tuple[int, int],
    frame_count: int,
    trailing_rows: int,
) -> OriginalClubHierarchyStrip:
    width, height = frame_size
    if decoded.width != width or decoded.height != height * frame_count + trailing_rows:
        raise TeamSelectNativeError(f"Original source geometry differs: {path}")
    frame_bytes = width * height * 4
    frames = tuple(
        OriginalButtonFrame(width, height, decoded.rgba[offset:offset + frame_bytes])
        for offset in range(0, frame_bytes * frame_count, frame_bytes)
    )
    return OriginalClubHierarchyStrip(
        path, decoded.height, width, height, frames, trailing_rows
    )


def decode_verified_teamselect_native_inputs(
    club_animation_source: bytes,
    club_bars_source: bytes,
    league_font_source: bytes,
    club_font_source: bytes,
    *,
    tables: EA444Tables,
    quant: EA444Quantization,
) -> OriginalTeamSelectNativeInputs:
    expected = (
        (club_animation_source, TEAMSELECT_CLUB_ANIM_SHA256, TEAMSELECT_CLUB_ANIM_PATH),
        (club_bars_source, TEAMSELECT_CLUB_BARS_SHA256, TEAMSELECT_CLUB_BARS_PATH),
        (league_font_source, TEAMSELECT_LEAGUE_FONT_SHA256, TEAMSELECT_LEAGUE_FONT_PATH),
        (club_font_source, TEAMSELECT_CLUB_FONT_SHA256, TEAMSELECT_CLUB_FONT_PATH),
    )
    for source, digest, path in expected:
        if sha256(source).hexdigest() != digest:
            raise TeamSelectNativeError(f"Original TeamSelect source checksum mismatch: {path}")
    return OriginalTeamSelectNativeInputs(
        club_animation=_split_club_strip(
            decode_ea444(club_animation_source, tables=tables, quant=quant),
            path=TEAMSELECT_CLUB_ANIM_PATH,
            frame_size=CLUB_ANIM_FRAME_SIZE,
            frame_count=23,
            # The original 30x438 source has one final scanline beyond the
            # 23*19 runtime-addressable region. No recovered state reads it.
            trailing_rows=1,
        ),
        club_bars=_split_club_strip(
            decode_ea444(club_bars_source, tables=tables, quant=quant),
            path=TEAMSELECT_CLUB_BARS_PATH,
            frame_size=CLUB_BAR_FRAME_SIZE,
            frame_count=4,
            trailing_rows=0,
        ),
        league_font=EAFont.from_bytes(league_font_source),
        club_font=EAFont.from_bytes(club_font_source),
    )


@dataclass(frozen=True)
class TeamSelectHierarchyRow:
    visible_index: int
    control_id: int
    rect: OriginalRect
    kind: HierarchyRowKind
    source_id: int
    text: str
    state: NativeControlState


@dataclass(frozen=True)
class TeamSelectClubRow:
    visible_index: int
    control_id: int
    rect: OriginalRect
    club_id: int
    text: str
    state: NativeControlState


def _cp1252_key(value: str) -> bytes:
    try:
        return value.encode("cp1252", errors="strict")
    except UnicodeEncodeError as exc:
        raise TeamSelectNativeError("Canonical visible name is not CP1252") from exc


def native_competitions_for_country(
    competitions: Iterable[object], country_id: int
) -> tuple[object, ...]:
    """Mirror `0x4D9DFF..0x4DA086` and its stable small-range sort."""
    selected = [
        item
        for item in competitions
        if int(getattr(item, "runtime_kind_code")) == 1
        and int(getattr(item, "country_region_id")) == int(country_id)
        and getattr(item, "parent_competition_id") is None
    ]
    # 0x4DA0B0 compares only signed +0x16. 0x4DA980 leaves equal keys in
    # source-table order, as Python's stable sort does here.
    return tuple(sorted(selected, key=lambda item: int(item.initialization_order_value)))


def native_clubs_for_competition(
    clubs: Iterable[object], competition_id: int
) -> tuple[object, ...]:
    """Mirror `0x4DA12A..0x4DA231`: membership then stable raw-name sort."""
    selected = [
        item for item in clubs
        if int(getattr(item, "competition_id")) == int(competition_id)
    ]
    return tuple(sorted(selected, key=lambda item: _cp1252_key(str(item.name))))


@dataclass
class TeamSelectHierarchyModel:
    countries: Mapping[int, object]
    competitions: tuple[object, ...]
    clubs: tuple[object, ...]
    selected_country_id: int = 26
    selected_competition_id: int | None = None
    # Reconstruction record index for visible row state only. The interrupted
    # trace's claimed native payload identity conflicts with an earlier verified
    # DBRClub+0x40 manager-ID mapping, so this is not yet a source-exact backend ID.
    selected_club_id: int | None = None

    def __post_init__(self) -> None:
        expected = tuple(country_id for country_id, _ in TEAMSELECT_ENGLISH_COUNTRY_ORDER)
        if any(country_id not in self.countries for country_id in expected):
            raise TeamSelectNativeError("Canonical TeamSelect country record is missing")
        if self.selected_competition_id is None:
            available = native_competitions_for_country(
                self.competitions, self.selected_country_id
            )
            if not available:
                raise TeamSelectNativeError("Default TeamSelect country has no native league")
            self.selected_competition_id = int(available[0].id)

    @classmethod
    def from_game_state(cls, state) -> "TeamSelectHierarchyModel":
        return cls(
            countries=dict(state.countries),
            competitions=tuple(state.competitions.values()),
            clubs=tuple(state.clubs.values()),
        )

    def hierarchy_rows(self) -> tuple[TeamSelectHierarchyRow, ...]:
        rows: list[tuple[HierarchyRowKind, object]] = []
        for country_id, expected_name in TEAMSELECT_ENGLISH_COUNTRY_ORDER:
            country = self.countries[country_id]
            if str(country.name) != expected_name:
                raise TeamSelectNativeError("Canonical TeamSelect country name changed")
            rows.append((HierarchyRowKind.COUNTRY, country))
            if country_id == self.selected_country_id:
                rows.extend(
                    (HierarchyRowKind.COMPETITION, item)
                    for item in native_competitions_for_country(
                        self.competitions, country_id
                    )
                )
        if len(rows) > len(TEAMSELECT_HIERARCHY_ROW_ORIGINS):
            rows = rows[:len(TEAMSELECT_HIERARCHY_ROW_ORIGINS)]
        result = []
        for index, (kind, item) in enumerate(rows):
            source_id = int(item.id)
            active = (
                kind is HierarchyRowKind.COMPETITION
                and source_id == self.selected_competition_id
            ) or (
                kind is HierarchyRowKind.COUNTRY
                and source_id == self.selected_country_id
                and self.selected_competition_id is None
            )
            x, y = TEAMSELECT_HIERARCHY_ROW_ORIGINS[index]
            result.append(
                TeamSelectHierarchyRow(
                    index,
                    TEAMSELECT_HIERARCHY_CONTROL_IDS[index],
                    OriginalRect(x, y, *LEAGUE_GROUP_SIZE),
                    kind,
                    source_id,
                    str(item.name),
                    NativeControlState.ACTIVE if active else NativeControlState.NORMAL,
                )
            )
        return tuple(result)

    def club_rows(self) -> tuple[TeamSelectClubRow, ...]:
        if self.selected_competition_id is None:
            return ()
        clubs = native_clubs_for_competition(
            self.clubs, self.selected_competition_id
        )[:len(TEAMSELECT_CLUB_ROW_ORIGINS)]
        result = []
        for index, club in enumerate(clubs):
            club_id = int(club.index)
            x, y = TEAMSELECT_CLUB_ROW_ORIGINS[index]
            result.append(
                TeamSelectClubRow(
                    index,
                    TEAMSELECT_CLUB_CONTROL_IDS[index],
                    OriginalRect(x, y, *CLUB_GROUP_SIZE),
                    club_id,
                    str(club.name),
                    NativeControlState.ACTIVE
                    if club_id == self.selected_club_id
                    else NativeControlState.NORMAL,
                )
            )
        return tuple(result)

    def activate_hierarchy_row(self, visible_index: int) -> TeamSelectHierarchyRow:
        rows = self.hierarchy_rows()
        if type(visible_index) is not int or not 0 <= visible_index < len(rows):
            raise TeamSelectNativeError("Unknown visible hierarchy row")
        row = rows[visible_index]
        self.selected_club_id = None
        if row.kind is HierarchyRowKind.COUNTRY:
            self.selected_country_id = row.source_id
            self.selected_competition_id = None
        else:
            self.selected_competition_id = row.source_id
        return row

    def toggle_club_row(self, visible_index: int) -> TeamSelectClubRow:
        rows = self.club_rows()
        if type(visible_index) is not int or not 0 <= visible_index < len(rows):
            raise TeamSelectNativeError("Unknown visible club row")
        row = rows[visible_index]
        self.selected_club_id = (
            None if self.selected_club_id == row.club_id else row.club_id
        )
        return row


@dataclass(frozen=True)
class TeamSelectRowPresentation:
    rect: OriginalRect
    animation_rect: OriginalRect
    bar_rect: OriginalRect
    text: str
    state: NativeControlState
    animation_source_index: int
    bar_source_index: int
    animation_frame: OriginalButtonFrame
    bar_frame: OriginalButtonFrame
    glyph_mask: EATextMask
    line_origin_x: int
    line_origin_y: int
    native_color_16: int
    row_kind: str
    source_id: int


def _presentation(
    *,
    rect: OriginalRect,
    text: str,
    state: NativeControlState,
    source_id: int,
    row_kind: str,
    animation_frames,
    bar_frames,
    animation_size: tuple[int, int],
    bar_size: tuple[int, int],
    font: EAFont,
    bar_index: int,
) -> TeamSelectRowPresentation:
    animation_index = animation_source_index(state, 0)
    animation = animation_frames[animation_index]
    bar = bar_frames[bar_index]
    animation_rect = OriginalRect(rect.x, rect.y, *animation_size)
    bar_rect = OriginalRect(rect.x + animation_size[0] + 2, rect.y, *bar_size)
    mask = font.render_text_alpha(text)
    line_x = bar_rect.x + (bar_rect.width - font.measure_text(text)) // 2
    line_y = bar_rect.y + (bar_rect.height - font.native_line_height()) // 2
    if line_x < bar_rect.x or line_y < bar_rect.y:
        raise TeamSelectNativeError("Native hierarchy caption exceeds its bar")
    return TeamSelectRowPresentation(
        rect, animation_rect, bar_rect, text, state,
        animation_index, bar_index, animation, bar, mask,
        line_x, line_y,
        0x0000 if state is NativeControlState.ACTIVE else 0xFFFF,
        row_kind, source_id,
    )


def build_teamselect_presentations(
    model: TeamSelectHierarchyModel,
    league_art: OriginalTeamSelectHierarchyArt,
    native: OriginalTeamSelectNativeInputs,
) -> tuple[tuple[TeamSelectRowPresentation, ...], tuple[TeamSelectRowPresentation, ...]]:
    hierarchy = tuple(
        _presentation(
            rect=row.rect,
            text=row.text,
            state=row.state,
            source_id=row.source_id,
            row_kind=row.kind.value,
            animation_frames=league_art.animation.frames,
            bar_frames=league_art.bars.frames,
            animation_size=LEAGUE_ANIM_FRAME_SIZE,
            bar_size=LEAGUE_BAR_FRAME_SIZE,
            font=native.league_font,
            bar_index=league_bar_source_index(
                row.state,
                is_country=row.kind is HierarchyRowKind.COUNTRY,
            ),
        )
        for row in model.hierarchy_rows()
    )
    clubs = tuple(
        _presentation(
            rect=row.rect,
            text=row.text,
            state=row.state,
            source_id=row.club_id,
            row_kind="club",
            animation_frames=native.club_animation.frames,
            bar_frames=native.club_bars.frames,
            animation_size=CLUB_ANIM_FRAME_SIZE,
            bar_size=CLUB_BAR_FRAME_SIZE,
            font=native.club_font,
            bar_index=club_bar_source_index(row.state),
        )
        for row in model.club_rows()
    )
    return hierarchy, clubs


def row_at_pointer(rows: Iterable[object], x: int, y: int):
    for row in rows:
        rect = row.rect
        if rect.x <= x < rect.right and rect.y <= y < rect.bottom:
            return row
    return None
