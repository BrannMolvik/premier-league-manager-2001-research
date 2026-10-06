"""Source-closed FM2001 Squad status icon atlas.

The canonical executable binds fm2001_art\\generic\\status.png to the
status-icon resource global and slices the exact 18x196 RGB PNG into fourteen
vertical 18x14 frames. This module intentionally stops at that source-backed
asset/frame contract. Native PSCFRow status-priority resolution is kept
separate until all override state, especially Cup-Tied and special Non-EU
registration state, is represented exactly by the clean-room runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import struct


class OriginalSquadStatusError(ValueError):
    """The original Squad status atlas is absent or changed."""


SOURCE_PATH = "FM2001_Art/Generic/status.png"
SOURCE_SHA256 = "59cd053c93ea789a010d813f46f650c2e4c16ea46163c63ae01209f69e4f5b1b"
SOURCE_SIZE = 4_015
SOURCE_DIMENSIONS = (18, 196)
FRAME_SIZE = (18, 14)
FRAME_COUNT = 14
PNG_SIGNATURE = b"\\x89PNG\\r\\n\\x1a\\n"

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
