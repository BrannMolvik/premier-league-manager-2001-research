"""Source-closed FM2001 Squad status icon atlas.

The canonical executable binds fm2001_art\\generic\\status.png to the
status-icon resource global and slices the exact 18x196 RGB PNG into fourteen
vertical 18x14 frames. This module also exposes the exact PSCFRow direct-return statuses 0..2
(Injured, Banned, International), because those return before the later native
override helper can replace them. Lower-priority statuses remain fail-closed
until all override state, especially Cup-Tied and special Non-EU registration
state, is represented exactly by the clean-room runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct
import zlib


class OriginalSquadStatusError(ValueError):
    """The original Squad status atlas is absent or changed."""


SOURCE_PATH = "FM2001_Art/Generic/status.png"
SOURCE_SHA256 = "59cd053c93ea789a010d813f46f650c2e4c16ea46163c63ae01209f69e4f5b1b"
SOURCE_SIZE = 4_015
SOURCE_DIMENSIONS = (18, 196)
FRAME_SIZE = (18, 14)
FRAME_COUNT = 14
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

STATUS_RESOURCE_PATH_VA = 0x835D98
STATUS_RESOURCE_GLOBAL_VA = 0x946110
STATUS_RESOURCE_INITIALIZER_VA = 0x603940
STATUS_ENTRY_TABLE_VA = 0x87BBF0
STATUS_ENTRY_SIZE = 0x20

STATUS_TABLE_STATIC_OFFSET = 0x26F2
STATUS_TABLE_RUNTIME_GLOBAL_VA = 0x874B40
STATUS_TABLE_READER_VA = 0x401310
STATUS_TABLE_SCAN_VA = 0x401DE0
STATUS_RESOLVER_VA = 0x418330
STATUS_OVERRIDE_VA = 0x418360
PSCF_ROW_UPDATE_VA = 0x48B8A0

STATUS_DEFINITION_TEXT = (
    "Injured",
    "Banned",
    "International",
    "Cup Tied",
    "First Team",
    "Subsitute",
    "On loan",
    "Out of contract",
    "Transfer listed",
    "Bid in",
    "Wanted",
    "Non EU",
)

ORDINARY_STATUS_FRAME_COUNT = len(STATUS_DEFINITION_TEXT)
NON_EU_ALTERNATE_FRAME_INDEX = 12
ON_LOAN_ALTERNATE_FRAME_INDEX = 13

# 0x401DE0 scans status bits in index order. In PSCFRow context the call's
# nonzero filter argument suppresses indices 4/5 and the scanner always
# suppresses index 3. 0x418330 returns scan results <=5 immediately, so the
# only status frames provably immune to later 0x418360 overrides are 0..2.
DIRECT_STATUS_FRAME_INDICES = (0, 1, 2)
DIRECT_STATUS_TEXT = STATUS_DEFINITION_TEXT[:3]
# Additional frames that can now be published without completing every
# 0x418360 negative branch. Frame 13 is the exact higher-priority loan
# override. Frame 12 is exact when bit 11 is active and its synchronized
# registration cutoff (live contract expiry) is past. Frame 3 is safe from a
# positively proven current-match Cup-Tied collection hit whenever frame 12
# does not win.
SOURCE_QUALIFIED_STATUS_FRAME_INDICES = (0, 1, 2, 3, 12, 13)
STATUS_SCAN_ALWAYS_SKIP_INDEX = 3
STATUS_SCAN_CONTEXT_SKIP_INDICES = (4, 5)
STATUS_OVERRIDE_BIT15_FRAME_INDEX = 10
STATUS_OVERRIDE_BIT12_FRAME_INDEX = 6


SQUAD_SCF_LIST_LOCAL_X = 239
SQUAD_STATUS_RECT = (1, 1, 18, 14)


@dataclass(frozen=True)
class OriginalSquadStatusAtlas:
    path: Path
    sha256: str
    width: int
    height: int
    frame_width: int
    frame_height: int
    frame_count: int

    @property
    def frame_rectangles(self) -> tuple[tuple[int, int, int, int], ...]:
        return tuple(
            (
                0,
                index * self.frame_height,
                self.frame_width,
                (index + 1) * self.frame_height,
            )
            for index in range(self.frame_count)
        )


@dataclass(frozen=True)
class OriginalSquadStatusFrame:
    index: int
    width: int
    height: int
    rgba: bytes

    def __post_init__(self) -> None:
        if type(self.index) is not int or not 0 <= self.index < FRAME_COUNT:
            raise OriginalSquadStatusError("Invalid Squad status frame index")
        if (self.width, self.height) != FRAME_SIZE:
            raise OriginalSquadStatusError("Squad status frame geometry drifted")
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalSquadStatusError("Incomplete Squad status frame RGBA")


@dataclass(frozen=True)
class OriginalSquadStatusOverlay:
    frame_index: int
    x: int
    y: int
    width: int
    height: int
    rgba: bytes

    def __post_init__(self) -> None:
        if (
            type(self.frame_index) is not int
            or self.frame_index not in SOURCE_QUALIFIED_STATUS_FRAME_INDICES
        ):
            raise OriginalSquadStatusError(
                "Unsafe or invalid source-qualified Squad status frame"
            )
        if (self.width, self.height) != FRAME_SIZE:
            raise OriginalSquadStatusError("Direct Squad status overlay geometry drifted")
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalSquadStatusError("Incomplete direct Squad status overlay RGBA")


@dataclass(frozen=True)
class OriginalSquadStatusResources:
    atlas: OriginalSquadStatusAtlas
    frames: tuple[OriginalSquadStatusFrame, ...]

    def __post_init__(self) -> None:
        if len(self.frames) != FRAME_COUNT:
            raise OriginalSquadStatusError("Missing Squad status frames")
        if tuple(frame.index for frame in self.frames) != tuple(range(FRAME_COUNT)):
            raise OriginalSquadStatusError("Squad status frame order drifted")

    def frame(self, index: int) -> OriginalSquadStatusFrame:
        if type(index) is not int or not 0 <= index < FRAME_COUNT:
            raise OriginalSquadStatusError("Invalid Squad status frame index")
        return self.frames[index]


def direct_squad_status_frame_index(
    *,
    injured: bool,
    banned: bool,
    international: bool,
) -> int | None:
    """Return only PSCFRow statuses that bypass every later native override.

    In the nonzero PSCFRow scan context, 0x401DE0 tests status bits 0, 1, 2,
    skips Cup-Tied index 3 and selection indices 4/5, then proceeds to lower
    priority statuses. 0x418330 returns 0..2 immediately and invokes 0x418360
    for every later result (or -1). Therefore Injured/Banned/International are
    the only status choices currently safe without materializing Cup-Tied,
    special Non-EU registration and the remaining override state.
    """
    states = (injured, banned, international)
    if any(type(value) is not bool for value in states):
        raise OriginalSquadStatusError(
            "Direct Squad status states must be booleans"
        )
    if injured:
        return 0
    if banned:
        return 1
    if international:
        return 2
    return None


def source_qualified_squad_status_frame_index(
    *,
    injured: bool,
    banned: bool,
    international: bool,
    alternate_on_loan: bool,
    non_eu: bool,
    non_eu_registration_expired: bool | None,
    cup_tied_positive: bool,
) -> int | None:
    """Resolve only PSCF statuses whose native priority outcome is proven.

    0x418330 returns frames 0..2 before the override helper. 0x418360 then
    prioritizes alternate On-loan frame 13, special Non-EU frame 12, and
    Cup-Tied frame 3. Recovery 342/344 source-closes frame 12 as bit 11 plus a
    registration record whose +0x14 cutoff is synchronized to DBRPlayer +0x154
    contract expiry. The mode-1 Cup-Tied negative transfer-history cutoff
    remains unresolved.

    Consequently:
    - direct 0/1/2 are always safe;
    - exact active-loan mismatch is safely frame 13;
    - bit 11 plus an expired registration/contract cutoff is exactly frame 12;
    - unresolved bit-11 cutoff state fails closed;
    - a current bit-11 cutoff that has not expired allows the lower Cup-Tied
      predicate to run, matching native override priority;
    - every other lower result remains unresolved rather than guessed.
    """
    states = (
        injured,
        banned,
        international,
        alternate_on_loan,
        non_eu,
        cup_tied_positive,
    )
    if any(type(value) is not bool for value in states):
        raise OriginalSquadStatusError(
            "Source-qualified Squad status states must be booleans"
        )
    if (
        non_eu_registration_expired is not None
        and type(non_eu_registration_expired) is not bool
    ):
        raise OriginalSquadStatusError(
            "Non-EU registration cutoff state must be boolean or unresolved"
        )
    if not non_eu and non_eu_registration_expired is True:
        raise OriginalSquadStatusError(
            "Non-EU registration cutoff cannot expire without active bit 11"
        )

    direct = direct_squad_status_frame_index(
        injured=injured,
        banned=banned,
        international=international,
    )
    if direct is not None:
        return direct
    if alternate_on_loan:
        return ON_LOAN_ALTERNATE_FRAME_INDEX
    if non_eu:
        if non_eu_registration_expired is None:
            return None
        if non_eu_registration_expired:
            return NON_EU_ALTERNATE_FRAME_INDEX
    if cup_tied_positive:
        return 3
    return None


def _paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def _decode_exact_rgb_png(raw: bytes) -> bytes:
    """Decode the pinned non-interlaced RGB8 PNG with standard filters only."""
    pos = len(PNG_SIGNATURE)
    compressed = bytearray()
    while pos + 12 <= len(raw):
        length = struct.unpack_from(">I", raw, pos)[0]
        kind = raw[pos + 4:pos + 8]
        start = pos + 8
        end = start + length
        if end + 4 > len(raw):
            raise OriginalSquadStatusError("Truncated Squad status PNG chunk")
        if kind == b"IDAT":
            compressed.extend(raw[start:end])
        pos = end + 4
        if kind == b"IEND":
            break

    try:
        filtered = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise OriginalSquadStatusError("Squad status PNG IDAT decode failed") from exc

    width, height = SOURCE_DIMENSIONS
    bytes_per_pixel = 3
    row_width = width * bytes_per_pixel
    expected = height * (row_width + 1)
    if len(filtered) != expected:
        raise OriginalSquadStatusError("Squad status PNG scanline size drifted")

    decoded = bytearray(width * height * bytes_per_pixel)
    previous = bytearray(row_width)
    source = 0
    target = 0
    for _row in range(height):
        filter_type = filtered[source]
        source += 1
        raw_row = filtered[source:source + row_width]
        source += row_width
        current = bytearray(row_width)
        for index, value in enumerate(raw_row):
            left = current[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = previous[index]
            upper_left = (
                previous[index - bytes_per_pixel]
                if index >= bytes_per_pixel
                else 0
            )
            if filter_type == 0:
                recon = value
            elif filter_type == 1:
                recon = value + left
            elif filter_type == 2:
                recon = value + above
            elif filter_type == 3:
                recon = value + ((left + above) // 2)
            elif filter_type == 4:
                recon = value + _paeth(left, above, upper_left)
            else:
                raise OriginalSquadStatusError(
                    f"Unsupported Squad status PNG filter {filter_type}"
                )
            current[index] = recon & 0xFF
        decoded[target:target + row_width] = current
        target += row_width
        previous = current

    rgba = bytearray(width * height * 4)
    for pixel in range(width * height):
        src = pixel * 3
        dst = pixel * 4
        rgba[dst:dst + 4] = bytes(
            (decoded[src], decoded[src + 1], decoded[src + 2], 255)
        )
    return bytes(rgba)


def load_verified_squad_status_resources(
    source_root: str | Path,
) -> OriginalSquadStatusResources:
    atlas = validate_original_squad_status_atlas(source_root)
    raw = atlas.path.read_bytes()
    rgba = _decode_exact_rgb_png(raw)
    stride = atlas.width * 4
    rows_per_frame = atlas.frame_height
    frames = tuple(
        OriginalSquadStatusFrame(
            index=index,
            width=atlas.frame_width,
            height=atlas.frame_height,
            rgba=rgba[
                index * rows_per_frame * stride:
                (index + 1) * rows_per_frame * stride
            ],
        )
        for index in range(atlas.frame_count)
    )
    return OriginalSquadStatusResources(atlas=atlas, frames=frames)


def build_first_roster_direct_status_overlays(
    rows,
    resources: OriginalSquadStatusResources,
) -> tuple[OriginalSquadStatusOverlay, ...]:
    """Place only direct-return PSCFRow status frames on the first roster."""
    if not isinstance(resources, OriginalSquadStatusResources):
        raise OriginalSquadStatusError(
            "Direct Squad status rendering requires verified original status resources"
        )
    from original_squad_resources import SQUAD_FIRST_ROSTER_RECT, SQUAD_PANEL_RECT

    panel_x, panel_y, _panel_width, _panel_height = SQUAD_PANEL_RECT
    local_x, local_y, width, height = SQUAD_STATUS_RECT
    overlays: list[OriginalSquadStatusOverlay] = []
    for row in tuple(rows):
        row_y = getattr(row, "y", None)
        frame_index = getattr(row, "native_status_frame_index", None)
        if type(row_y) is not int:
            raise OriginalSquadStatusError("Squad row y must be an integer")
        if frame_index is None:
            continue
        if (
            type(frame_index) is not int
            or frame_index not in SOURCE_QUALIFIED_STATUS_FRAME_INDICES
        ):
            raise OriginalSquadStatusError(
                "Squad status frame is not source-qualified for rendering"
            )
        frame = resources.frame(frame_index)
        overlays.append(
            OriginalSquadStatusOverlay(
                frame_index=frame_index,
                x=panel_x + SQUAD_FIRST_ROSTER_RECT.x + SQUAD_SCF_LIST_LOCAL_X + local_x,
                y=panel_y + SQUAD_FIRST_ROSTER_RECT.y + row_y + local_y,
                width=width,
                height=height,
                rgba=frame.rgba,
            )
        )
    return tuple(overlays)


def validate_original_squad_status_atlas(
    source_root: str | Path,
) -> OriginalSquadStatusAtlas:
    """Fail closed unless the byte-identical original status atlas is present."""
    root = Path(source_root)
    path = root / SOURCE_PATH
    try:
        raw = path.read_bytes()
    except FileNotFoundError as exc:
        raise OriginalSquadStatusError(
            f"Missing exact Squad status atlas: {SOURCE_PATH}"
        ) from exc

    if len(raw) != SOURCE_SIZE:
        raise OriginalSquadStatusError("Squad status atlas byte-size mismatch")
    digest = sha256(raw).hexdigest()
    if digest != SOURCE_SHA256:
        raise OriginalSquadStatusError("Squad status atlas checksum mismatch")
    if raw[:8] != PNG_SIGNATURE or len(raw) < 33:
        raise OriginalSquadStatusError("Squad status atlas is not a PNG")

    chunk_length = struct.unpack_from(">I", raw, 8)[0]
    chunk_name = raw[12:16]
    width, height, depth, color_type, compression, filtering, interlace = (
        struct.unpack_from(">IIBBBBB", raw, 16)
    )
    if (
        chunk_name != b"IHDR"
        or chunk_length != 13
        or (width, height) != SOURCE_DIMENSIONS
        or (depth, color_type, compression, filtering, interlace)
        != (8, 2, 0, 0, 0)
    ):
        raise OriginalSquadStatusError(
            "Squad status atlas PNG header/geometry drifted"
        )
    if height != FRAME_COUNT * FRAME_SIZE[1] or width != FRAME_SIZE[0]:
        raise OriginalSquadStatusError("Squad status frame geometry drifted")

    return OriginalSquadStatusAtlas(
        path=path,
        sha256=digest,
        width=width,
        height=height,
        frame_width=FRAME_SIZE[0],
        frame_height=FRAME_SIZE[1],
        frame_count=FRAME_COUNT,
    )
