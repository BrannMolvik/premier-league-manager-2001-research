"""Source-verified TeamSelect hierarchy image strips, without invented states.

Original TeamSelect constructor 0x4D7D82..0x4D80BF creates 16 rows through
0x4D8C60. Its source bindings and per-frame widths/heights are already
verified in original_front_end_layout. Neither the original executable's
frame-to-mouse-state mapping nor hierarchy row contents are recovered yet.

This module preserves all actual pixels and top-to-bottom source frame
indices from the two separately SHA-pinned EA444 resources. Source atlas
height/frame count are *read from decoded original bytes*, never guessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import EA444Quantization
from ea444_tables import EA444Tables
from original_button_frames import OriginalButtonFrame
from original_front_end_layout import (
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    TEAMSELECT_HIERARCHY_BARS_PATH,
    TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
    TEAMSELECT_HIERARCHY_FRAME_SIZE,
)


class OriginalHierarchyStripError(ValueError):
    """Missing/mismatched original source identity or impossible frame geometry."""


@dataclass(frozen=True)
class OriginalHierarchyStripSpec:
    path: str
    source_sha256: str
    frame_width: int
    frame_height: int

    def __post_init__(self) -> None:
        if self.frame_width <= 0 or self.frame_height <= 0:
            raise OriginalHierarchyStripError("Hierarchy frame dimensions must be positive")


HIERARCHY_ANIM_SPEC = OriginalHierarchyStripSpec(
    TEAMSELECT_HIERARCHY_ANIM_PATH,
    "de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22",
    *TEAMSELECT_HIERARCHY_FRAME_SIZE,
)
HIERARCHY_BARS_SPEC = OriginalHierarchyStripSpec(
    TEAMSELECT_HIERARCHY_BARS_PATH,
    "bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa",
    *TEAMSELECT_HIERARCHY_BARS_FRAME_SIZE,
)


@dataclass(frozen=True)
class OriginalHierarchyStrip:
    """All source-ordered RGBA frames of one exact original resource."""
    spec: OriginalHierarchyStripSpec
    source_height: int
    frames: tuple[OriginalButtonFrame, ...]

    def __post_init__(self) -> None:
        if (
            self.source_height <= 0
            or self.source_height % self.spec.frame_height
            or len(self.frames) != self.source_height // self.spec.frame_height
        ):
            raise OriginalHierarchyStripError("Hierarchy strip source row count is inconsistent")
        if any(
            (frame.width, frame.height) !=
            (self.spec.frame_width, self.spec.frame_height)
            for frame in self.frames
        ):
            raise OriginalHierarchyStripError("Hierarchy strip frame geometry is inconsistent")

    def source_frame(self, source_index: int) -> OriginalButtonFrame:
        """Numeric original atlas index only; not an inferred selection state."""
        if type(source_index) is not int or not 0 <= source_index < len(self.frames):
            raise OriginalHierarchyStripError("Unknown hierarchy source frame index")
        return self.frames[source_index]


@dataclass(frozen=True)
class OriginalTeamSelectHierarchyArt:
    """The two source-bound hierarchy graphic families, kept distinct."""
    animation: OriginalHierarchyStrip
    bars: OriginalHierarchyStrip

    def __post_init__(self) -> None:
        if self.animation.spec != HIERARCHY_ANIM_SPEC or self.bars.spec != HIERARCHY_BARS_SPEC:
            raise OriginalHierarchyStripError("Wrong original TeamSelect hierarchy art")


def split_hierarchy_source_strip(
    decoded: EA444DecodedImage, spec: OriginalHierarchyStripSpec
) -> OriginalHierarchyStrip:
    """Slice one SHA-verified source's recovered frame dimensions losslessly.

    This operation accepts any integral number of original source frames;
    the native animation-state ordering has NOT been recovered.
    """
    if decoded.width != spec.frame_width:
        raise OriginalHierarchyStripError("Original source atlas width differs from runtime frame")
    if decoded.height <= 0 or decoded.height % spec.frame_height:
        raise OriginalHierarchyStripError("Original source atlas height is not integral frames")
    frame_bytes = spec.frame_width * spec.frame_height * 4
    if len(decoded.rgba) != frame_bytes * (decoded.height // spec.frame_height):
        raise OriginalHierarchyStripError("Decoded original RGBA payload is incomplete")
    frames = tuple(
        OriginalButtonFrame(
            spec.frame_width, spec.frame_height,
            decoded.rgba[offset:offset + frame_bytes],
        )
        for offset in range(0, len(decoded.rgba), frame_bytes)
    )
    return OriginalHierarchyStrip(spec, decoded.height, frames)


def decode_verified_hierarchy_strip(
    source: bytes, *,
    spec: OriginalHierarchyStripSpec,
    tables: EA444Tables,
    quant: EA444Quantization,
) -> OriginalHierarchyStrip:
    if sha256(source).hexdigest() != spec.source_sha256:
        raise OriginalHierarchyStripError(
            f"Original hierarchy source checksum mismatch: {spec.path}"
        )
    return split_hierarchy_source_strip(
        decode_ea444(source, tables=tables, quant=quant), spec
    )


def decode_verified_hierarchy_art(
    animation_source: bytes, bars_source: bytes, *,
    tables: EA444Tables, quant: EA444Quantization,
) -> OriginalTeamSelectHierarchyArt:
    return OriginalTeamSelectHierarchyArt(
        animation=decode_verified_hierarchy_strip(
            animation_source, spec=HIERARCHY_ANIM_SPEC, tables=tables, quant=quant
        ),
        bars=decode_verified_hierarchy_strip(
            bars_source, spec=HIERARCHY_BARS_SPEC, tables=tables, quant=quant
        ),
    )
