"""Bridge a validated original-runtime Windows pixel receipt into PPreMatch.

This is the provenance boundary between the generic native16 compositor and
one actually observed original FM2001 DirectDraw surface layout. It accepts the
existing strict receipt validator, constructs the exact mask triplet, and emits
the source-order packed-16 PPreMatch framebuffer.

Modern RGBA expansion and complete Gate-14 presentation remain separate.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Mapping

from gate14_font_blend_source_trace import Native16PixelMasks
from gate14_prematch_child_rasters import PrematchChildRasterLedger
from gate14_prematch_native16_compositor import (
    PrematchNative16Frame,
    compose_prematch_native16_frame,
)
from gate14_windows_pixel_format_receipt import validate_windows_pixel_format_receipt


class PrematchRuntimeNative16Error(ValueError):
    pass


@dataclass(frozen=True)
class PrematchObservedNative16Frame:
    frame: PrematchNative16Frame
    source_executable_sha256: str
    bit_count: int
    native_color_key: int
    windows_runtime_surface_observation_accepted: bool = True
    runtime_rgb_mask_values_recovered: bool = True
    native_color_channel_layout_recovered: bool = True
    flattened_native16_frame_available: bool = True
    packed16_to_modern_rgba_recovered: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        if type(self.frame) is not PrematchNative16Frame:
            raise PrematchRuntimeNative16Error(
                "observed PPreMatch frame requires exact native16 frame"
            )
        if (
            not isinstance(self.source_executable_sha256, str)
            or len(self.source_executable_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.source_executable_sha256)
        ):
            raise PrematchRuntimeNative16Error(
                "source executable identity must be lowercase SHA-256"
            )
        if self.bit_count != 16:
            raise PrematchRuntimeNative16Error(
                "observed original PPreMatch framebuffer must remain 16-bit"
            )
        if self.native_color_key != self.frame.masks.color_key:
            raise PrematchRuntimeNative16Error(
                "observed native color key differs from validated masks"
            )
        if not (
            self.windows_runtime_surface_observation_accepted
            and self.runtime_rgb_mask_values_recovered
            and self.native_color_channel_layout_recovered
            and self.flattened_native16_frame_available
        ):
            raise PrematchRuntimeNative16Error(
                "observed native16 frame cannot weaken receipt provenance"
            )
        if (
            self.packed16_to_modern_rgba_recovered
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchRuntimeNative16Error(
                "modern display and Gate 14 remain unresolved"
            )


def compose_prematch_native16_from_windows_receipt(
    ledger: PrematchChildRasterLedger,
    *,
    receipt: Mapping[str, object],
    original_executable: bytes,
) -> PrematchObservedNative16Frame:
    """Validate original-runtime masks, then flatten the native child ledger."""
    if type(ledger) is not PrematchChildRasterLedger:
        raise PrematchRuntimeNative16Error(
            "receipt bridge requires exact PrematchChildRasterLedger"
        )
    if not isinstance(original_executable, bytes):
        raise PrematchRuntimeNative16Error(
            "receipt bridge requires canonical executable bytes"
        )

    try:
        validation = validate_windows_pixel_format_receipt(
            receipt,
            original_executable,
        )
        masks = Native16PixelMasks(
            red=validation["red_mask"],
            green=validation["green_mask"],
            blue=validation["blue_mask"],
        )
        frame = compose_prematch_native16_frame(
            ledger,
            masks=masks,
        )
    except Exception as exc:
        raise PrematchRuntimeNative16Error(
            "validated Windows pixel-format receipt could not drive PPreMatch"
        ) from exc

    if not validation.get("windows_runtime_surface_observation_accepted"):
        raise PrematchRuntimeNative16Error(
            "receipt did not accept an original Windows runtime surface"
        )
    if not validation.get("runtime_rgb_mask_values_recovered"):
        raise PrematchRuntimeNative16Error(
            "receipt did not recover runtime RGB masks"
        )
    if not validation.get("native_color_channel_layout_recovered"):
        raise PrematchRuntimeNative16Error(
            "receipt did not recover native channel layout"
        )

    return PrematchObservedNative16Frame(
        frame=frame,
        source_executable_sha256=sha256(original_executable).hexdigest(),
        bit_count=validation["bit_count"],
        native_color_key=validation["native_color_key"],
    )


def prematch_runtime_native16_contract() -> dict:
    return {
        "strict_windows_receipt_reused": True,
        "canonical_executable_required": True,
        "runtime_rgb_masks_feed_native16_compositor": True,
        "flattened_native16_frame_available_after_receipt": True,
        "packed16_to_modern_rgba_recovered": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
