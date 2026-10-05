"""One-time verified conversion cache for original FM2001 startup TGQs.

Normal Windows launch consumes the user's exact original FMV/easp.tgq and
FMV/premintro.tgq. The port converts those source-verified files once to the
existing H.264/AAC compatibility profile, verifies that each video stream
decodes to the source-proven frame count and that the audio stream decodes,
then stores only the modern derivatives plus a checksum receipt in a private
per-user cache.

The cache is not semantic evidence for skip input, fades, display treatment, or
real Windows visibility/audibility.
"""
from __future__ import annotations

from hashlib import sha256
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    OriginalStartupMediaError,
    StartupMediaConversionProfile,
    build_startup_media_conversion_plans,
)
from startup_media_derivatives import VerifiedStartupMediaDerivative


class RuntimeStartupMediaError(RuntimeError):
    pass


CACHE_SCHEMA_VERSION = 1
CACHE_DIRECTORY_NAME = "FM2001-Windows11"
CACHE_MEDIA_DIRECTORY_NAME = "startup-media"
CACHE_RECEIPT_NAME = "startup-media-runtime-receipt.json"
PACKAGED_FFMPEG_RELATIVE_PATH = Path("runtime_tools") / "ffmpeg.exe"


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_startup_media_cache_root() -> Path:
    local = os.environ.get("LOCALAPPDATA")
    if local:
        return Path(local) / CACHE_DIRECTORY_NAME / CACHE_MEDIA_DIRECTORY_NAME
    return Path.home() / "AppData" / "Local" / CACHE_DIRECTORY_NAME / CACHE_MEDIA_DIRECTORY_NAME


def resolve_startup_ffmpeg(
    application_root: str | Path,
    *,
    system_which: Callable[[str], str | None] = shutil.which,
) -> Path:
    """Prefer the release-bundled FFmpeg; allow system FFmpeg for source runs."""
    root = Path(application_root).resolve()
    packaged = root / PACKAGED_FFMPEG_RELATIVE_PATH
    if packaged.is_file():
        return packaged
    system = system_which("ffmpeg")
    if system:
        path = Path(system).resolve()
        if path.is_file():
            return path
    raise RuntimeStartupMediaError(
        "FFmpeg is unavailable. The Windows release must include runtime_tools/ffmpeg.exe."
    )


def _run(
    runner: Callable[..., object],
    command: tuple[str, ...],
    *,
    label: str,
) -> object:
    try:
        result = runner(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise RuntimeStartupMediaError(f"{label} could not start: {exc}") from exc
    if getattr(result, "returncode", None) != 0:
        stderr = str(getattr(result, "stderr", "") or "")
        raise RuntimeStartupMediaError(
            f"{label} failed: {stderr[-3000:].strip()}"
        )
    return result


def _ffmpeg_version(
    ffmpeg: Path,
    runner: Callable[..., object],
) -> str:
    result = _run(
        runner,
        (str(ffmpeg), "-version"),
        label="FFmpeg version probe",
    )
    stdout = str(getattr(result, "stdout", "") or "")
    first = stdout.splitlines()[0].strip() if stdout.splitlines() else ""
    if not first.lower().startswith("ffmpeg version "):
        raise RuntimeStartupMediaError("FFmpeg version output is invalid")
    return first


def _validate_derivative_decode(
    path: Path,
    *,
    expected_frames: int,
    ffmpeg: Path,
    runner: Callable[..., object],
) -> None:
    video = _run(
        runner,
        (
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:v:0",
            "-an",
            "-f",
            "null",
            "-",
            "-progress",
            "pipe:1",
            "-nostats",
        ),
        label=f"startup video decode verification for {path.name}",
    )
    values = {}
    for raw in str(getattr(video, "stdout", "") or "").splitlines():
        if "=" in raw:
            key, value = raw.split("=", 1)
            values[key.strip()] = value.strip()
    try:
        frames = int(values.get("frame", ""))
    except ValueError as exc:
        raise RuntimeStartupMediaError(
            f"startup video frame count is missing for {path.name}"
        ) from exc
    if frames != expected_frames or values.get("progress") != "end":
        raise RuntimeStartupMediaError(
            f"startup video frame count differs from source contract for {path.name}"
        )

    _run(
        runner,
        (
            str(ffmpeg),
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostdin",
            "-i",
            str(path),
            "-map",
            "0:a:0",
            "-vn",
            "-f",
            "null",
            "-",
        ),
        label=f"startup audio decode verification for {path.name}",
    )


def _profile_receipt(
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> dict:
    return {
        "container": profile.container_name,
        "video_encoder": profile.ffmpeg_video_encoder,
        "video_codec": profile.probe_video_codec,
        "pixel_format": profile.pixel_format,
        "audio_encoder": profile.ffmpeg_audio_encoder,
        "audio_codec": profile.probe_audio_codec,
    }


def _source_receipt(sequence: int) -> dict:
    spec = ORIGINAL_STARTUP_MEDIA_SEQUENCE[sequence]
    return {
        "sequence": sequence,
        "source_path": spec.source_path,
        "source_sha256": spec.source_sha256,
        "source_size_bytes": spec.size_bytes,
        "startup_callsite_va": f"0x{spec.startup_callsite_va:X}",
        "playback_wrapper_va": f"0x{spec.playback_wrapper_va:X}",
        "playback_flag_bit0": spec.playback_flag_bit0,
        "video_width": spec.video_width,
        "video_height": spec.video_height,
        "frame_rate": spec.frame_rate,
        "decoded_video_frames": spec.decoded_video_frames,
        "audio_sample_rate": spec.audio_sample_rate,
        "audio_channels": spec.audio_channels,
    }


def _load_cache(
    cache_root: Path,
    *,
    ffmpeg_sha256: str,
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> tuple[VerifiedStartupMediaDerivative, ...] | None:
    receipt = cache_root / CACHE_RECEIPT_NAME
    if not receipt.is_file():
        return None
    try:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    if (
        payload.get("schema_version") != CACHE_SCHEMA_VERSION
        or payload.get("audit_kind") != "runtime_original_startup_media_conversion"
        or payload.get("profile") != _profile_receipt(profile)
        or payload.get("ffmpeg_sha256") != ffmpeg_sha256
        or payload.get("gate14_complete") is not False
    ):
        return None
    outputs = payload.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != len(ORIGINAL_STARTUP_MEDIA_SEQUENCE):
        return None

    verified = []
    for sequence, raw in enumerate(outputs):
        if not isinstance(raw, dict):
            return None
        source = _source_receipt(sequence)
        for key, value in source.items():
            if raw.get(key) != value:
                return None
        expected_name = Path(ORIGINAL_STARTUP_MEDIA_SEQUENCE[sequence].source_path).stem + ".mp4"
        if raw.get("filename") != expected_name:
            return None
        size = raw.get("converted_size_bytes")
        digest = raw.get("converted_sha256")
        if type(size) is not int or size <= 0:
            return None
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(ch not in "0123456789abcdef" for ch in digest)
        ):
            return None
        path = (cache_root / expected_name).resolve()
        if path.parent != cache_root.resolve() or not path.is_file():
            return None
        if path.stat().st_size != size or _sha256_file(path) != digest:
            return None
        spec = ORIGINAL_STARTUP_MEDIA_SEQUENCE[sequence]
        verified.append(
            VerifiedStartupMediaDerivative(
                sequence=sequence,
                spec=spec,
                path=path,
                converted_sha256=digest,
                converted_size_bytes=size,
                container="mp4",
                video_codec="h264",
                pixel_format="yuv420p",
                audio_codec="aac",
            )
        )
    return tuple(verified)


def prepare_runtime_startup_media(
    game_dir: str | Path,
    application_root: str | Path,
    *,
    cache_root: str | Path | None = None,
    ffmpeg_executable: str | Path | None = None,
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    runner: Callable[..., object] = subprocess.run,
) -> tuple[VerifiedStartupMediaDerivative, ...]:
    """Return cached verified derivatives, converting exact originals if needed."""
    source = Path(game_dir).resolve()
    cache = (
        default_startup_media_cache_root()
        if cache_root is None
        else Path(cache_root).resolve()
    )
    ffmpeg = (
        resolve_startup_ffmpeg(application_root)
        if ffmpeg_executable is None
        else Path(ffmpeg_executable).resolve()
    )
    if not ffmpeg.is_file():
        raise RuntimeStartupMediaError(f"FFmpeg executable is unavailable: {ffmpeg}")

    try:
        plans_probe = build_startup_media_conversion_plans(
            source,
            cache / ".source-contract-probe",
            ffmpeg_executable=str(ffmpeg),
            profile=profile,
        )
    except (OSError, OriginalStartupMediaError) as exc:
        raise RuntimeStartupMediaError(
            "Original FM2001 startup TGQs are missing or do not match the verified source. "
            "Expected FMV/easp.tgq and FMV/premintro.tgq in the selected game folder."
        ) from exc
    # The probe is pure: build_startup_media_conversion_plans validates source
    # bytes and returns commands without creating output.
    if len(plans_probe) != len(ORIGINAL_STARTUP_MEDIA_SEQUENCE):
        raise RuntimeStartupMediaError("startup source sequence is incomplete")

    ffmpeg_digest = _sha256_file(ffmpeg)
    cached = _load_cache(cache, ffmpeg_sha256=ffmpeg_digest, profile=profile)
    if cached is not None:
        return cached

    cache.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="startup-build-",
        dir=cache.parent,
    ) as temp:
        staging = Path(temp)
        plans = build_startup_media_conversion_plans(
            source,
            staging,
            ffmpeg_executable=str(ffmpeg),
            profile=profile,
        )
        outputs = []
        for sequence, plan in enumerate(plans):
            _run(
                runner,
                plan.ffmpeg_args,
                label=f"startup conversion for {plan.spec.source_path}",
            )
            path = plan.output_path
            if not path.is_file() or path.stat().st_size <= 0:
                raise RuntimeStartupMediaError(
                    f"startup conversion did not produce {path.name}"
                )
            _validate_derivative_decode(
                path,
                expected_frames=plan.spec.decoded_video_frames,
                ffmpeg=ffmpeg,
                runner=runner,
            )
            outputs.append(
                {
                    **_source_receipt(sequence),
                    "filename": path.name,
                    "converted_size_bytes": path.stat().st_size,
                    "converted_sha256": _sha256_file(path),
                    "container": profile.container_name,
                    "video_codec": profile.probe_video_codec,
                    "pixel_format": profile.pixel_format,
                    "audio_codec": profile.probe_audio_codec,
                    "audio_geometry_enforced_by_conversion": True,
                    "video_decode_verified": True,
                    "audio_decode_verified": True,
                }
            )

        cache.mkdir(parents=True, exist_ok=True)
        for output in outputs:
            src = staging / output["filename"]
            dst = cache / output["filename"]
            os.replace(src, dst)

    receipt_payload = {
        "schema_version": CACHE_SCHEMA_VERSION,
        "audit_kind": "runtime_original_startup_media_conversion",
        "ffmpeg_path": str(ffmpeg),
        "ffmpeg_sha256": ffmpeg_digest,
        "ffmpeg_version": _ffmpeg_version(ffmpeg, runner),
        "profile": _profile_receipt(profile),
        "outputs": outputs,
        "fidelity_boundary": (
            "Cache proves exact source TGQ identity, deterministic conversion "
            "command geometry, decoded source frame counts and decodable audio. "
            "It does not prove native skip input, fade/transition timing, display "
            "treatment, or human-visible/audible Windows playback."
        ),
        "gate14_complete": False,
    }
    (cache / CACHE_RECEIPT_NAME).write_text(
        json.dumps(receipt_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    loaded = _load_cache(cache, ffmpeg_sha256=ffmpeg_digest, profile=profile)
    if loaded is None:
        raise RuntimeStartupMediaError(
            "fresh startup-media conversion cache failed self-verification"
        )
    return loaded


def runtime_startup_media_contract(
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> dict:
    return {
        "source_paths": tuple(
            item.source_path for item in ORIGINAL_STARTUP_MEDIA_SEQUENCE
        ),
        "conversion_profile": _profile_receipt(profile),
        "packaged_ffmpeg_relative_path": PACKAGED_FFMPEG_RELATIVE_PATH.as_posix(),
        "one_time_private_cache": True,
        "source_hash_reverified_before_cache_use": True,
        "cached_output_hash_reverified": True,
        "decoded_video_frame_count_reverified_on_conversion": True,
        "audio_stream_decode_reverified_on_conversion": True,
        "windows_playback_verified": False,
        "skip_input_recovered": False,
        "transition_timing_recovered": False,
        "gate14_complete": False,
    }
