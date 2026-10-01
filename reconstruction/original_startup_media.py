"""Fail-closed source and conversion contracts for original FM2001 startup FMVs.

The authorized disc research proves exact TGQ identity, media geometry and
startup call order. This module never ships the TGQ files and never invents
skip semantics. It validates deliberately supplied original bytes, constructs a
modern FFmpeg conversion plan, and validates the resulting media metadata
before a future playback layer may consume it.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Iterable, Mapping, Sequence


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


@dataclass(frozen=True)
class StartupMediaConversionProfile:
    """Modern compatibility target, separate from original interaction semantics."""

    output_suffix: str = ".mp4"
    ffmpeg_video_encoder: str = "libx264"
    probe_video_codec: str = "h264"
    pixel_format: str = "yuv420p"
    ffmpeg_audio_encoder: str = "aac"
    probe_audio_codec: str = "aac"
    container_name: str = "mp4"

    def __post_init__(self) -> None:
        if self.output_suffix != ".mp4":
            raise OriginalStartupMediaError("Startup conversion target must remain MP4")
        if not all((
            self.ffmpeg_video_encoder,
            self.probe_video_codec,
            self.pixel_format,
            self.ffmpeg_audio_encoder,
            self.probe_audio_codec,
            self.container_name,
        )):
            raise OriginalStartupMediaError("Startup conversion profile is incomplete")


DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE = StartupMediaConversionProfile()


@dataclass(frozen=True)
class StartupMediaConversionPlan:
    """One exact-source TGQ to modern-container conversion invocation."""

    spec: OriginalStartupMediaSpec
    source_path: Path
    output_path: Path
    ffmpeg_args: tuple[str, ...]


@dataclass(frozen=True)
class VerifiedStartupMediaConversion:
    """Metadata proof for a converted derivative of one exact original TGQ."""

    spec: OriginalStartupMediaSpec
    container_name: str
    video_codec: str
    video_frames: int
    pixel_format: str
    audio_codec: str
    audio_sample_rate: int
    audio_channels: int


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


def build_startup_media_conversion_plans(
    source_root: Path,
    output_root: Path,
    *,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    ffmpeg_executable: str = "ffmpeg",
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> tuple[StartupMediaConversionPlan, ...]:
    """Validate exact TGQs and return deterministic, non-overwriting FFmpeg plans.

    This function deliberately does not launch FFmpeg. A caller must execute the
    returned arguments, then validate each output with
    validate_startup_media_probe() before treating it as a usable derivative.
    """
    ordered_specs = validate_original_startup_media(source_root, specs=tuple(specs))
    source_base = Path(source_root)
    output_base = Path(output_root)
    if not ffmpeg_executable:
        raise OriginalStartupMediaError("FFmpeg executable must be named explicitly")

    plans: list[StartupMediaConversionPlan] = []
    for spec in ordered_specs:
        source = source_base / spec.source_path
        output = output_base / (Path(spec.source_path).stem + profile.output_suffix)
        if source.resolve() == output.resolve():
            raise OriginalStartupMediaError("Conversion output must differ from TGQ source")
        args = (
            ffmpeg_executable,
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-n",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-c:v",
            profile.ffmpeg_video_encoder,
            "-pix_fmt",
            profile.pixel_format,
            "-fps_mode",
            "passthrough",
            "-c:a",
            profile.ffmpeg_audio_encoder,
            "-ar",
            str(spec.audio_sample_rate),
            "-ac",
            str(spec.audio_channels),
            "-movflags",
            "+faststart",
            str(output),
        )
        plans.append(
            StartupMediaConversionPlan(
                spec=spec,
                source_path=source,
                output_path=output,
                ffmpeg_args=args,
            )
        )
    return tuple(plans)


def build_startup_media_ffprobe_args(
    output_path: Path,
    *,
    ffprobe_executable: str = "ffprobe",
) -> tuple[str, ...]:
    """Return the metadata probe required by validate_startup_media_probe()."""
    if not ffprobe_executable:
        raise OriginalStartupMediaError("FFprobe executable must be named explicitly")
    return (
        ffprobe_executable,
        "-v",
        "error",
        "-count_frames",
        "-show_streams",
        "-show_format",
        "-of",
        "json",
        str(Path(output_path)),
    )


def _require_int(value: object, *, label: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise OriginalStartupMediaError(
            f"Converted startup media {label} is missing or invalid"
        ) from exc


def _require_frame_rate(stream: Mapping[str, object], expected: int) -> None:
    raw = stream.get("avg_frame_rate") or stream.get("r_frame_rate")
    if not isinstance(raw, str) or "/" not in raw:
        raise OriginalStartupMediaError(
            "Converted startup media frame rate is missing or invalid"
        )
    numerator, denominator = raw.split("/", 1)
    num = _require_int(numerator, label="frame-rate numerator")
    den = _require_int(denominator, label="frame-rate denominator")
    if den == 0 or num != expected * den:
        raise OriginalStartupMediaError(
            "Converted startup media frame rate differs from original"
        )


def _require_frame_count(stream: Mapping[str, object], expected: int) -> int:
    raw = stream.get("nb_read_frames")
    if raw in (None, "N/A"):
        raw = stream.get("nb_frames")
    count = _require_int(raw, label="decoded video frame count")
    if count != expected:
        raise OriginalStartupMediaError(
            "Converted startup media video frame count differs from original"
        )
    return count


def validate_startup_media_probe(
    spec: OriginalStartupMediaSpec,
    probe: Mapping[str, object],
    *,
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> VerifiedStartupMediaConversion:
    """Fail closed unless FFprobe metadata matches the intended derivative contract.

    This validates stream/container structure only. The derivative itself is not
    considered bit-identical to the TGQ, and exact original provenance continues
    to come from spec.source_sha256 plus the pre-conversion source validation.
    """
    raw_streams = probe.get("streams")
    if not isinstance(raw_streams, Sequence) or isinstance(raw_streams, (str, bytes)):
        raise OriginalStartupMediaError("Converted startup media streams are missing")
    streams = [item for item in raw_streams if isinstance(item, Mapping)]
    videos = [item for item in streams if item.get("codec_type") == "video"]
    audios = [item for item in streams if item.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1 or len(streams) != 2:
        raise OriginalStartupMediaError(
            "Converted startup media must contain exactly one video and one audio stream"
        )

    video = videos[0]
    audio = audios[0]
    if video.get("codec_name") != profile.probe_video_codec:
        raise OriginalStartupMediaError("Converted startup video codec differs from target")
    if audio.get("codec_name") != profile.probe_audio_codec:
        raise OriginalStartupMediaError("Converted startup audio codec differs from target")
    if video.get("pix_fmt") != profile.pixel_format:
        raise OriginalStartupMediaError(
            "Converted startup pixel format differs from compatibility target"
        )
    if (
        _require_int(video.get("width"), label="video width") != spec.video_width
        or _require_int(video.get("height"), label="video height") != spec.video_height
    ):
        raise OriginalStartupMediaError(
            "Converted startup video geometry differs from original"
        )
    _require_frame_rate(video, spec.frame_rate)
    frame_count = _require_frame_count(video, spec.decoded_video_frames)

    sample_rate = _require_int(audio.get("sample_rate"), label="audio sample rate")
    channels = _require_int(audio.get("channels"), label="audio channel count")
    if sample_rate != spec.audio_sample_rate or channels != spec.audio_channels:
        raise OriginalStartupMediaError(
            "Converted startup audio geometry differs from original"
        )

    raw_format = probe.get("format")
    if not isinstance(raw_format, Mapping):
        raise OriginalStartupMediaError("Converted startup container metadata is missing")
    format_name = raw_format.get("format_name")
    if not isinstance(format_name, str):
        raise OriginalStartupMediaError("Converted startup container name is missing")
    format_tokens = {part.strip() for part in format_name.split(",") if part.strip()}
    if profile.container_name not in format_tokens:
        raise OriginalStartupMediaError(
            "Converted startup container differs from compatibility target"
        )

    return VerifiedStartupMediaConversion(
        spec=spec,
        container_name=profile.container_name,
        video_codec=profile.probe_video_codec,
        video_frames=frame_count,
        pixel_format=profile.pixel_format,
        audio_codec=profile.probe_audio_codec,
        audio_sample_rate=sample_rate,
        audio_channels=channels,
    )
