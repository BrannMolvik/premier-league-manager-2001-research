"""Fail-closed source contract for the verified original FM2001 startup FMVs.

The authorized disc research proves exact file identity, media geometry and the
startup call order.  This module does not ship the TGQ files, decode them, or
invent skip semantics.  It only validates deliberately supplied original bytes
against the independently recorded source measurements.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable


class OriginalStartupMediaError(ValueError):
    """Supplied startup media differs from the verified original source."""


@dataclass(frozen=True)
class OriginalStartupMediaSpec:
    source_path: str
    source_sha256: str
    size_bytes: int
    startup_callsite_va: int
    playback_wrapper_va: int
    playback_flag_bit0: bool
    video_width: int
    video_height: int
    frame_rate: int
    decoded_video_frames: int
    audio_sample_rate: int
    audio_channels: int

    def __post_init__(self) -> None:
        if not self.source_path.lower().endswith(".tgq"):
            raise OriginalStartupMediaError("Startup media contract requires TGQ source")
        if len(self.source_sha256) != 64:
            raise OriginalStartupMediaError("Startup media SHA-256 must be complete")
        if self.size_bytes <= 0:
            raise OriginalStartupMediaError("Startup media size must be positive")
        if (self.video_width, self.video_height) != (320, 480):
            raise OriginalStartupMediaError(
                "Verified FM2001 startup TGQ video geometry changed"
            )
        if self.frame_rate != 25:
            raise OriginalStartupMediaError("Verified startup TGQ frame rate changed")
        if self.audio_sample_rate != 22050 or self.audio_channels != 2:
            raise OriginalStartupMediaError("Verified startup TGQ audio geometry changed")


EA_SPORTS_STARTUP_MEDIA = OriginalStartupMediaSpec(
    source_path="FMV/easp.tgq",
    source_sha256="73dc078ee8fe7e1d7412b4bcba072c3f8ec85546d5e5b94f90be9732498af97c",
    size_bytes=1_383_304,
    startup_callsite_va=0x530FAE,
    playback_wrapper_va=0x461E20,
    playback_flag_bit0=False,
    video_width=320,
    video_height=480,
    frame_rate=25,
    decoded_video_frames=97,
    audio_sample_rate=22_050,
    audio_channels=2,
)

PREMIER_LEAGUE_INTRO_MEDIA = OriginalStartupMediaSpec(
    source_path="FMV/premintro.tgq",
    source_sha256="a16e64a1c680ce1c7bcf57f76f05dd8e51a77663b5b4a673e681c9da188a0b0d",
    size_bytes=28_434_180,
    startup_callsite_va=0x531175,
    playback_wrapper_va=0x461E20,
    playback_flag_bit0=True,
    video_width=320,
    video_height=480,
    frame_rate=25,
    decoded_video_frames=1_275,
    audio_sample_rate=22_050,
    audio_channels=2,
)

ORIGINAL_STARTUP_MEDIA_SEQUENCE = (
    EA_SPORTS_STARTUP_MEDIA,
    PREMIER_LEAGUE_INTRO_MEDIA,
)


def validate_original_startup_media(
    source_root: Path,
    *,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
) -> tuple[OriginalStartupMediaSpec, ...]:
    """Require exact original TGQ bytes in the proven startup order."""
    root = Path(source_root)
    checked: list[OriginalStartupMediaSpec] = []
    for spec in specs:
        path = root / spec.source_path
        data = path.read_bytes()
        if len(data) != spec.size_bytes:
            raise OriginalStartupMediaError(
                f"Original startup media size mismatch: {spec.source_path}"
            )
        if sha256(data).hexdigest() != spec.source_sha256:
            raise OriginalStartupMediaError(
                f"Original startup media checksum mismatch: {spec.source_path}"
            )
        checked.append(spec)
    return tuple(checked)
