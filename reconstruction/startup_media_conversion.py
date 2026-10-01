"""Fail-closed lossless conversion path for verified original FM2001 startup TGQ.

Gate 14 must preserve the authorized original presentation material wherever
practical. FFmpeg can decode the EA TGQ/TQI family used by the verified FM2001
startup movies, but the modern port should not make runtime playback depend on
the legacy TGQ container. This module therefore converts only checksum-gated
source files to a lossless Matroska intermediate:

- FFV1 video;
- PCM signed 16-bit little-endian audio.

The converter validates the original source contract first, validates the
converted streams with ffprobe before promotion, refuses to overwrite existing
outputs, and emits a machine-readable provenance receipt. It deliberately does
not claim a final Windows playback implementation, skip-input semantics, or
original match-presentation behavior.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Callable, Iterable, Sequence

from original_startup_media import (
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    OriginalStartupMediaError,
    OriginalStartupMediaSpec,
    validate_original_startup_media,
)


class StartupMediaConversionError(RuntimeError):
    """The requested conversion cannot be proven source-faithful."""


CommandRunner = Callable[[Sequence[str]], str]


@dataclass(frozen=True)
class ConvertedStartupMedia:
    source_path: str
    source_sha256: str
    output_path: str
    output_sha256: str
    output_size_bytes: int
    video_codec: str
    video_width: int
    video_height: int
    frame_rate: str
    decoded_video_frames: int
    audio_codec: str
    audio_sample_rate: int
    audio_channels: int
    conversion_command: tuple[str, ...]


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_command(command: Sequence[str]) -> str:
    try:
        result = subprocess.run(
            list(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise StartupMediaConversionError(
            f"Unable to launch conversion tool: {command[0]}"
        ) from exc
    if result.returncode != 0:
        tail = result.stdout[-4000:]
        raise StartupMediaConversionError(
            f"Conversion command failed with exit code {result.returncode}: "
            f"{command[0]}\n{tail}"
        )
    return result.stdout


def _safe_relative_path(source_path: str) -> PurePosixPath:
    relative = PurePosixPath(source_path)
    if (
        not source_path
        or relative.is_absolute()
        or ".." in relative.parts
        or "." in relative.parts
    ):
        raise StartupMediaConversionError(
            "Startup media source path must stay inside the supplied source root"
        )
    return relative


def _output_relative_path(spec: OriginalStartupMediaSpec) -> PurePosixPath:
    source = _safe_relative_path(spec.source_path)
    return source.with_suffix(".mkv")


def _tool_version(
    executable: str,
    runner: CommandRunner,
) -> str:
    output = runner((executable, "-version"))
    first = next((line.strip() for line in output.splitlines() if line.strip()), "")
    if not first:
        raise StartupMediaConversionError(
            f"{executable} did not report a version string"
        )
    return first


def _require_single_stream(
    streams: list[dict],
    codec_type: str,
) -> dict:
    matches = [stream for stream in streams if stream.get("codec_type") == codec_type]
    if len(matches) != 1:
        raise StartupMediaConversionError(
            f"Converted startup media must contain exactly one {codec_type} stream"
        )
    return matches[0]


def _int_field(stream: dict, field: str) -> int:
    try:
        return int(stream[field])
    except (KeyError, TypeError, ValueError) as exc:
        raise StartupMediaConversionError(
            f"Converted stream is missing integer field {field}"
        ) from exc


def _probe_converted(
    path: Path,
    spec: OriginalStartupMediaSpec,
    *,
    ffprobe: str,
    runner: CommandRunner,
) -> dict:
    raw = runner(
        (
            ffprobe,
            "-v",
            "error",
            "-count_frames",
            "-show_entries",
            (
                "stream=index,codec_type,codec_name,width,height,r_frame_rate,"
                "sample_rate,channels,nb_read_frames"
            ),
            "-of",
            "json",
            str(path),
        )
    )
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StartupMediaConversionError(
            "ffprobe did not return valid JSON for converted startup media"
        ) from exc
    streams = payload.get("streams")
    if not isinstance(streams, list):
        raise StartupMediaConversionError("ffprobe JSON has no stream list")

    video = _require_single_stream(streams, "video")
    audio = _require_single_stream(streams, "audio")
    if len(streams) != 2:
        raise StartupMediaConversionError(
            "Converted startup media contains unexpected additional streams"
        )

    if video.get("codec_name") != "ffv1":
        raise StartupMediaConversionError("Converted video is not FFV1")
    if (
        _int_field(video, "width") != spec.video_width
        or _int_field(video, "height") != spec.video_height
    ):
        raise StartupMediaConversionError(
            "Converted video geometry differs from the verified original"
        )
    try:
        rate = Fraction(str(video["r_frame_rate"]))
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        raise StartupMediaConversionError(
            "Converted video frame rate is missing or invalid"
        ) from exc
    if rate != Fraction(spec.frame_rate, 1):
        raise StartupMediaConversionError(
            "Converted video frame rate differs from the verified original"
        )
    if _int_field(video, "nb_read_frames") != spec.decoded_video_frames:
        raise StartupMediaConversionError(
            "Converted video frame count differs from the verified original"
        )

    if audio.get("codec_name") != "pcm_s16le":
        raise StartupMediaConversionError("Converted audio is not PCM s16le")
    if _int_field(audio, "sample_rate") != spec.audio_sample_rate:
        raise StartupMediaConversionError(
            "Converted audio sample rate differs from the verified original"
        )
    if _int_field(audio, "channels") != spec.audio_channels:
        raise StartupMediaConversionError(
            "Converted audio channel count differs from the verified original"
        )

    return {
        "video_codec": "ffv1",
        "video_width": spec.video_width,
        "video_height": spec.video_height,
        "frame_rate": f"{rate.numerator}/{rate.denominator}",
        "decoded_video_frames": spec.decoded_video_frames,
        "audio_codec": "pcm_s16le",
        "audio_sample_rate": spec.audio_sample_rate,
        "audio_channels": spec.audio_channels,
    }


def _ffmpeg_command(
    ffmpeg: str,
    source: Path,
    target: Path,
) -> tuple[str, ...]:
    return (
        ffmpeg,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-n",
        "-i",
        str(source),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-c:v",
        "ffv1",
        "-level",
        "3",
        "-g",
        "1",
        "-c:a",
        "pcm_s16le",
        str(target),
    )


def _receipt_command(
    ffmpeg: str,
    source_relative: str,
    output_relative: str,
) -> tuple[str, ...]:
    """Return provenance arguments without embedding machine-specific roots."""
    return (
        Path(ffmpeg).name,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-n",
        "-i",
        source_relative,
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-c:v",
        "ffv1",
        "-level",
        "3",
        "-g",
        "1",
        "-c:a",
        "pcm_s16le",
        output_relative,
    )


def convert_verified_startup_media(
    source_root: Path,
    output_root: Path,
    *,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    ffmpeg: str = "ffmpeg",
    ffprobe: str = "ffprobe",
    runner: CommandRunner = _run_command,
    receipt_name: str = "startup_media_conversion_receipt.json",
) -> tuple[ConvertedStartupMedia, ...]:
    """Create provenance-tracked lossless intermediates from exact TGQ sources.

    All source files are checksum-validated before any conversion begins. All
    converted files are written to temporary .tmp.mkv paths and probed before
    any final output is promoted. Existing outputs or receipts are never
    overwritten.
    """
    source_root = Path(source_root).resolve()
    output_root = Path(output_root).resolve()
    spec_list = tuple(specs)
    if not spec_list:
        raise StartupMediaConversionError("At least one startup media spec is required")

    for spec in spec_list:
        _safe_relative_path(spec.source_path)
    try:
        validate_original_startup_media(source_root, specs=spec_list)
    except (OSError, OriginalStartupMediaError) as exc:
        raise StartupMediaConversionError(
            "Startup media source validation failed"
        ) from exc

    receipt_relative = PurePosixPath(receipt_name)
    if (
        receipt_relative.is_absolute()
        or ".." in receipt_relative.parts
        or len(receipt_relative.parts) != 1
    ):
        raise StartupMediaConversionError(
            "Conversion receipt name must be one file inside the output root"
        )
    receipt = output_root / receipt_relative.name
    if receipt.exists():
        raise StartupMediaConversionError(
            f"Conversion receipt already exists: {receipt}"
        )

    planned: list[tuple[OriginalStartupMediaSpec, Path, Path, PurePosixPath]] = []
    seen_outputs: set[PurePosixPath] = set()
    for spec in spec_list:
        relative = _output_relative_path(spec)
        if relative in seen_outputs:
            raise StartupMediaConversionError(
                f"Duplicate converted output path: {relative.as_posix()}"
            )
        seen_outputs.add(relative)
        final_path = output_root.joinpath(*relative.parts)
        temp_path = final_path.with_name(f"{final_path.stem}.tmp{final_path.suffix}")
        if final_path.exists() or temp_path.exists():
            raise StartupMediaConversionError(
                f"Converted output already exists: {final_path}"
            )
        planned.append((spec, final_path, temp_path, relative))

    ffmpeg_version = _tool_version(ffmpeg, runner)
    ffprobe_version = _tool_version(ffprobe, runner)

    converted: list[ConvertedStartupMedia] = []
    temp_paths = [item[2] for item in planned]
    promoted: list[Path] = []
    receipt_tmp = receipt.with_name(f"{receipt.stem}.tmp{receipt.suffix}")
    if receipt_tmp.exists():
        raise StartupMediaConversionError(
            f"Temporary conversion receipt already exists: {receipt_tmp}"
        )

    try:
        for spec, final_path, temp_path, relative in planned:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            source_relative = _safe_relative_path(spec.source_path)
            source = source_root.joinpath(*source_relative.parts)
            command = _ffmpeg_command(ffmpeg, source, temp_path)
            runner(command)
            if not temp_path.is_file() or temp_path.stat().st_size <= 0:
                raise StartupMediaConversionError(
                    f"FFmpeg did not create converted output: {relative.as_posix()}"
                )
            probe = _probe_converted(
                temp_path,
                spec,
                ffprobe=ffprobe,
                runner=runner,
            )
            converted.append(
                ConvertedStartupMedia(
                    source_path=spec.source_path,
                    source_sha256=spec.source_sha256,
                    output_path=relative.as_posix(),
                    output_sha256=_sha256_file(temp_path),
                    output_size_bytes=temp_path.stat().st_size,
                    conversion_command=_receipt_command(
                        ffmpeg,
                        spec.source_path,
                        relative.as_posix(),
                    ),
                    **probe,
                )
            )

        receipt_payload = {
            "schema_version": 1,
            "purpose": "FM2001 Gate 14 lossless startup-media conversion intermediate",
            "container": "matroska",
            "video_codec": "ffv1",
            "audio_codec": "pcm_s16le",
            "ffmpeg_version": ffmpeg_version,
            "ffprobe_version": ffprobe_version,
            "source_validation": "exact size and SHA-256 before conversion",
            "post_conversion_validation": (
                "ffprobe codec/geometry/frame-rate/frame-count/audio geometry"
            ),
            "final_playback_claimed": False,
            "files": [asdict(item) for item in converted],
        }
        output_root.mkdir(parents=True, exist_ok=True)
        receipt_tmp.write_text(
            json.dumps(receipt_payload, indent=2) + "\n",
            encoding="utf-8",
        )

        for _spec, final_path, temp_path, _relative in planned:
            temp_path.replace(final_path)
            promoted.append(final_path)
        receipt_tmp.replace(receipt)
    except Exception:
        for path in temp_paths:
            path.unlink(missing_ok=True)
        receipt_tmp.unlink(missing_ok=True)
        for path in promoted:
            path.unlink(missing_ok=True)
        raise

    return tuple(converted)
