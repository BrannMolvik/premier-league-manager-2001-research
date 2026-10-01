"""Decode and select authentic source-verified Button@ease atlas frames.

The source executable proves the original PStartMenu button_type_1 atlas
169x575 has 169x25 frames; TeamSelect choice_start_anim 150x736 has 150x32
frames. Both have 23 actual frames. Direct tracing of the canonical executable
now proves three groups: 0..10 for enabled/non-alternate, 11..21 for the
enabled mask-4 alternate group, and frame 22 when disabled. Pointer-inside
mask 8 advances the current group subframe; clearing it retreats to zero.

The executable does not yet prove a user-facing name such as "pressed" for
mask 4, so this module deliberately calls it ``alternate``.

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


# Canonical Button@ease_2001 vftable 0x7BF4CC:
# 0x653040 chooses group 2 when mask 2 is clear, group 1 when mask 4 is set,
# otherwise group 0. 0x5D62F0 returns lengths 11, 11 and 1. 0x652860 sums
# earlier group lengths and the current subframe at +0x48.
BUTTON_ENABLED_MASK = 0x2
BUTTON_ALTERNATE_MASK = 0x4
BUTTON_ADVANCE_MASK = 0x8
BUTTON_INITIAL_FLAGS = 0x183
BUTTON_GROUP_LENGTHS = (11, 11, 1)


def button_group_subframe_for_source_index(source_index: int) -> tuple[int, int]:
    """Invert the proven 0x652860 source-frame calculation exactly."""
    if (
        type(source_index) is not int
        or not 0 <= source_index < sum(BUTTON_GROUP_LENGTHS)
    ):
        raise OriginalButtonAtlasError("Invalid native Button@ease source frame index")
    offset = source_index
    for group, length in enumerate(BUTTON_GROUP_LENGTHS):
        if offset < length:
            return group, offset
        offset -= length
    raise OriginalButtonAtlasError("Unreachable native Button@ease source frame")


@dataclass
class OriginalButtonState:
    """Exact native group/subframe state without guessing mask-4 semantics."""

    flags: int = BUTTON_INITIAL_FLAGS
    group: int = 0
    subframe: int = 0

    @staticmethod
    def group_for_flags(flags: int) -> int:
        if not flags & BUTTON_ENABLED_MASK:
            return 2
        return 1 if flags & BUTTON_ALTERNATE_MASK else 0

    def set_enabled(self, enabled: bool) -> None:
        self._set_mask(BUTTON_ENABLED_MASK, enabled)

    def set_alternate(self, alternate: bool) -> None:
        self._set_mask(BUTTON_ALTERNATE_MASK, alternate)

    def set_pointer_inside(self, inside: bool) -> None:
        """Mirror 0x64FBE0 -> slot 6: mask 8 follows pointer containment."""
        self._set_mask(BUTTON_ADVANCE_MASK, inside)

    def _set_mask(self, mask: int, value: bool) -> None:
        if value:
            self.flags |= mask
        else:
            self.flags &= ~mask

    def _select_group(self) -> bool:
        """Mirror 0x652780 proportional progress when 0x653040 changes group."""
        target = self.group_for_flags(self.flags)
        if target == self.group:
            return False
        if not 0 <= self.group < len(BUTTON_GROUP_LENGTHS):
            raise OriginalButtonAtlasError("Invalid native Button@ease group")
        old_length = BUTTON_GROUP_LENGTHS[self.group]
        new_length = BUTTON_GROUP_LENGTHS[target]
        self.subframe = new_length * self.subframe // old_length
        self.group = target
        return True

    def update(self) -> bool:
        """Run one native 0x6527F0 update and report whether pixels changed."""
        changed = self._select_group()
        length = BUTTON_GROUP_LENGTHS[self.group]
        if self.flags & BUTTON_ADVANCE_MASK:
            if self.subframe + 1 < length:
                self.subframe += 1
                return True
        elif self.subframe:
            self.subframe -= 1
            return True
        return changed

    @property
    def source_frame_index(self) -> int:
        if not 0 <= self.group < len(BUTTON_GROUP_LENGTHS):
            raise OriginalButtonAtlasError("Invalid native Button@ease group")
        length = BUTTON_GROUP_LENGTHS[self.group]
        if not 0 <= self.subframe < length:
            raise OriginalButtonAtlasError("Invalid native Button@ease subframe")
        return sum(BUTTON_GROUP_LENGTHS[:self.group]) + self.subframe


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
        """Return by the exact vertical atlas index."""
        if type(source_index) is not int or not 0 <= source_index < len(self.frames):
            raise OriginalButtonAtlasError("Invalid unscaled source button frame index")
        return self.frames[source_index]

    def frame_for_state(self, state: OriginalButtonState) -> OriginalButtonFrame:
        """Select the frame computed by the recovered native group mapping."""
        if len(self.frames) != sum(BUTTON_GROUP_LENGTHS):
            raise OriginalButtonAtlasError(
                "Native Button@ease mapping requires the canonical 23-frame atlas"
            )
        return self.frame(state.source_frame_index)


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
