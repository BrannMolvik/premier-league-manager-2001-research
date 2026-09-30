"""Split authentic source-verified .444 button atlases into their real frames.

The source executable proves the original PStartMenu button_type_1 atlas
169x575 has 169x25 frames; TeamSelect choice_start_anim 150x736 has 150x32
frames. Both have 23 actual frames. The ordering of interaction states within
those 23 frames remains unproven and is intentionally NOT assigned here.

The decoded image is processed in top-to-bottom source order without redrawing.
The source-verifying entry point refuses substituted art by source SHA-256.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import EA444Quantization
from ea444_tables import EA444Tables
from original_front_end_layout import (
    PSTARTMENU_ACTION_ATLAS_PATH,
    PSTARTMENU_ACTION_FRAME_SIZE,
    TEAMSELECT_ACTION_ATLAS_PATH,
    TEAMSELECT_ACTION_FRAME_SIZE,
)


class OriginalButtonAtlasError(ValueError):
    """A button atlas lacks original geometry or the expected source identity."""


@dataclass(frozen=True)
class ButtonAtlasSpec:
    source_path: str
    source_sha256: str
    source_width: int
    source_height: int
    frame_width: int
    frame_height: int

    @property
    def frame_count(self) -> int:
        if (
            self.source_width <= 0
            or self.source_height <= 0
            or self.frame_width != self.source_width
            or self.frame_height <= 0
            or self.source_height % self.frame_height
        ):
            raise OriginalButtonAtlasError("Inconsistent vertical button atlas specification")
        return self.source_height // self.frame_height


PSTARTMENU_BUTTON_ATLAS = ButtonAtlasSpec(
    PSTARTMENU_ACTION_ATLAS_PATH,
    "57ba72fd2a978735cbd4537aee4fa3031f13f10994067fb2ceba6c22c5ef41e3",
    169,
    575,
    *PSTARTMENU_ACTION_FRAME_SIZE,
)

TEAMSELECT_BUTTON_ATLAS = ButtonAtlasSpec(
    TEAMSELECT_ACTION_ATLAS_PATH,
    "d204e7086a15ac15bd9d10377526ba40bb40ffd83b5f02ba39ef8404dd42922d",
    150,
    736,
    *TEAMSELECT_ACTION_FRAME_SIZE,
)


@dataclass(frozen=True)
class OriginalButtonFrame:
    width: int
    height: int
    rgba: bytes

    def __post_init__(self) -> None:
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalButtonAtlasError("Incomplete RGBA button frame")


@dataclass(frozen=True)
class OriginalButtonAtlas:
    spec: ButtonAtlasSpec
    frames: tuple[OriginalButtonFrame, ...]

    def frame(self, source_index: int) -> OriginalButtonFrame:
        """Return by vertical atlas index, NOT by an unproven hover-state ID."""
        if type(source_index) is not int or not 0 <= source_index < len(self.frames):
            raise OriginalButtonAtlasError("Invalid unscaled source button frame index")
        return self.frames[source_index]


def split_original_button_atlas(
    decoded: EA444DecodedImage,
    spec: ButtonAtlasSpec,
) -> OriginalButtonAtlas:
    """Crop source pixels at proven frame dimensions; never interpolate them."""
    count = spec.frame_count
    if (decoded.width, decoded.height) != (spec.source_width, spec.source_height):
        raise OriginalButtonAtlasError("Decoded source dimensions disagree with original atlas")
    stride = spec.source_width * 4
    frame_rows = spec.frame_height
    frames = tuple(
        OriginalButtonFrame(
            spec.frame_width,
            frame_rows,
            decoded.rgba[index * frame_rows * stride:
                         (index + 1) * frame_rows * stride],
        )
        for index in range(count)
    )
    return OriginalButtonAtlas(spec, frames)


def decode_verified_original_button_atlas(
    source: bytes,
    *,
    spec: ButtonAtlasSpec,
    tables: EA444Tables,
    quant: EA444Quantization,
) -> OriginalButtonAtlas:
    """Decode only hash-matched source bytes with the recovered EA444 decoder."""
    if sha256(source).hexdigest() != spec.source_sha256:
        raise OriginalButtonAtlasError(
            "Original button source SHA-256 mismatch; no substitute is accepted"
        )
    return split_original_button_atlas(
        decode_ea444(source, tables=tables, quant=quant), spec
    )
