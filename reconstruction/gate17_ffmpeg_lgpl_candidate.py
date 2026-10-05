"""Verify a pinned LGPL FFmpeg Windows candidate before any production migration.

This probe is deliberately independent from the currently bundled
imageio-ffmpeg/Gyan executable. It proves only that one exact upstream archive
has a non-GPL FFmpeg configuration and the codec capabilities required by the
existing startup-media architecture. It does not switch the runtime, prove
Windows 11 playback, or declare license compliance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import tempfile
import zipfile


class LgplFfmpegCandidateError(RuntimeError):
    pass


RELEASE_TAG = "autobuild-2026-10-03-18-14"
ARCHIVE_NAME = "ffmpeg-n9.0.2-22-g46d8f462ee-win64-lgpl-9.0.zip"
ARCHIVE_SHA256 = "3fc85bae9f9643a03d15c2d2de12fb017dcd9fdabe819bfb1a94f54fea108714"
ARCHIVE_URL = (
    "https://github.com/BtbN/FFmpeg-Builds/releases/download/"
    + RELEASE_TAG
    + "/"
    + ARCHIVE_NAME
)
EXPECTED_VERSION_TOKEN = "n9.0.2-22-g46d8f462ee"
REQUIRED_DECODERS = ("eatgq",)
REQUIRED_ENCODERS = ("h264_mf", "aac")
FORBIDDEN_CONFIGURATION_FLAGS = (
    "--enable-gpl",
    "--enable-nonfree",
    "--enable-libx264",
    "--enable-libx265",
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_archive_identity(path: str | Path) -> dict:
    archive = Path(path).resolve()
    if not archive.is_file():
        raise LgplFfmpegCandidateError(f"candidate archive is missing: {archive}")
    digest = _sha256_file(archive)
    if digest != ARCHIVE_SHA256:
        raise LgplFfmpegCandidateError(
            f"candidate archive SHA-256 mismatch: expected {ARCHIVE_SHA256}, got {digest}"
        )
    try:
        with zipfile.ZipFile(archive) as zf:
            names = tuple(name.replace("\\", "/") for name in zf.namelist())
            exe = tuple(name for name in names if name.endswith("/bin/ffmpeg.exe"))
            probe = tuple(name for name in names if name.endswith("/bin/ffprobe.exe"))
            license_files = tuple(name for name in names if name.endswith("/LICENSE.txt"))
            if len(exe) != 1:
                raise LgplFfmpegCandidateError(
                    f"candidate archive must contain one bin/ffmpeg.exe; found {len(exe)}"
                )
            if len(probe) != 1:
                raise LgplFfmpegCandidateError(
                    f"candidate archive must contain one bin/ffprobe.exe; found {len(probe)}"
                )
            if len(license_files) != 1:
                raise LgplFfmpegCandidateError(
                    f"candidate archive must contain one LICENSE.txt; found {len(license_files)}"
                )
            license_bytes = zf.read(license_files[0])
            if len(license_bytes) < 100:
                raise LgplFfmpegCandidateError("candidate LICENSE.txt is unexpectedly small")
    except zipfile.BadZipFile as exc:
        raise LgplFfmpegCandidateError("candidate archive is not a readable ZIP") from exc
    return {
        "archive_name": ARCHIVE_NAME,
        "archive_sha256": digest,
        "ffmpeg_member": exe[0],
        "ffprobe_member": probe[0],
        "license_member": license_files[0],
        "license_sha256": sha256(license_bytes).hexdigest(),
        "license_size_bytes": len(license_bytes),
    }


def validate_version_output(text: str) -> dict:
    if type(text) is not str or not text.strip():
        raise LgplFfmpegCandidateError("candidate FFmpeg -version output is empty")
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines or EXPECTED_VERSION_TOKEN not in lines[0]:
        raise LgplFfmpegCandidateError(
            "candidate FFmpeg version does not match the pinned source revision"
        )
    configuration = next(
        (line for line in lines if line.startswith("configuration:")),
        None,
    )
    if configuration is None:
        raise LgplFfmpegCandidateError("candidate FFmpeg configuration line is missing")
    tokens = set(configuration.split())
    forbidden = tuple(flag for flag in FORBIDDEN_CONFIGURATION_FLAGS if flag in tokens)
    if forbidden:
        raise LgplFfmpegCandidateError(
            "candidate FFmpeg unexpectedly enables GPL/nonfree codec flags: "
            + ", ".join(forbidden)
        )
    return {
        "version_line": lines[0],
        "configuration_line": configuration,
        "forbidden_configuration_flags_present": list(forbidden),
    }


def validate_ffprobe_version_output(text: str) -> dict:
    if type(text) is not str or not text.strip():
        raise LgplFfmpegCandidateError("candidate FFprobe -version output is empty")
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines or not lines[0].lower().startswith("ffprobe version "):
        raise LgplFfmpegCandidateError("candidate FFprobe version line is invalid")
    if EXPECTED_VERSION_TOKEN not in lines[0]:
        raise LgplFfmpegCandidateError(
            "candidate FFprobe version does not match the pinned source revision"
        )
    return {"ffprobe_version_line": lines[0]}


def validate_synthetic_probe_output(text: str) -> dict:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LgplFfmpegCandidateError(
            "candidate FFprobe returned invalid synthetic-output JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise LgplFfmpegCandidateError(
            "candidate FFprobe synthetic-output root must be an object"
        )
    streams = payload.get("streams")
    if not isinstance(streams, list) or len(streams) != 2:
        raise LgplFfmpegCandidateError(
            "synthetic candidate MP4 must contain exactly two streams"
        )
    videos = [stream for stream in streams if stream.get("codec_type") == "video"]
    audios = [stream for stream in streams if stream.get("codec_type") == "audio"]
    if len(videos) != 1 or len(audios) != 1:
        raise LgplFfmpegCandidateError(
            "synthetic candidate MP4 must contain one video and one audio stream"
        )
    video = videos[0]
    audio = audios[0]
    if (
        video.get("codec_name") != "h264"
        or video.get("pix_fmt") != "yuv420p"
        or video.get("width") != 320
        or video.get("height") != 480
        or video.get("avg_frame_rate") != "25/1"
    ):
        raise LgplFfmpegCandidateError(
            "synthetic candidate video geometry/codec differs from startup contract"
        )
    if (
        audio.get("codec_name") != "aac"
        or str(audio.get("sample_rate")) != "22050"
        or audio.get("channels") != 2
    ):
        raise LgplFfmpegCandidateError(
            "synthetic candidate audio geometry/codec differs from startup contract"
        )
    raw_format = payload.get("format")
    if not isinstance(raw_format, dict):
        raise LgplFfmpegCandidateError(
            "synthetic candidate container metadata is missing"
        )
    format_names = {
        item.strip().lower()
        for item in str(raw_format.get("format_name", "")).split(",")
        if item.strip()
    }
    if "mp4" not in format_names:
        raise LgplFfmpegCandidateError("synthetic candidate container is not MP4")
    return {
        "synthetic_probe_verified": True,
        "synthetic_probe_video_codec": "h264",
        "synthetic_probe_pixel_format": "yuv420p",
        "synthetic_probe_audio_codec": "aac",
        "synthetic_probe_container": "mp4",
    }


def _codec_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\s*[A-Z.]{6}\s+([A-Za-z0-9_]+)\s", line)
        if match is not None:
            names.add(match.group(1))
    return names


def validate_codec_capabilities(*, decoders_text: str, encoders_text: str) -> dict:
    decoders = _codec_names(decoders_text)
    encoders = _codec_names(encoders_text)
    missing_decoders = tuple(name for name in REQUIRED_DECODERS if name not in decoders)
    missing_encoders = tuple(name for name in REQUIRED_ENCODERS if name not in encoders)
    if missing_decoders or missing_encoders:
        raise LgplFfmpegCandidateError(
            "candidate FFmpeg lacks required startup-media codecs: "
            f"decoders={list(missing_decoders)}, encoders={list(missing_encoders)}"
        )
    return {
        "required_decoders": list(REQUIRED_DECODERS),
        "required_encoders": list(REQUIRED_ENCODERS),
        "all_required_codecs_present": True,
    }


def _run(executable: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            [str(executable), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise LgplFfmpegCandidateError(
            f"candidate FFmpeg could not execute: {exc}"
        ) from exc
    if result.returncode != 0:
        raise LgplFfmpegCandidateError(
            f"candidate FFmpeg {' '.join(args)} failed with exit code {result.returncode}"
        )
    return result.stdout


def validate_synthetic_h264_aac_roundtrip(
    executable: Path,
    ffprobe: Path,
    work_root: Path,
) -> dict:
    """Exercise exact startup output options and probe/decode the resulting MP4."""
    output = work_root / "candidate-roundtrip.mp4"
    _run(
        executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-f",
        "lavfi",
        "-i",
        "color=c=black:s=320x480:r=25:d=1",
        "-f",
        "lavfi",
        "-i",
        "anullsrc=r=22050:cl=stereo:d=1",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "h264_mf",
        "-pix_fmt",
        "yuv420p",
        "-fps_mode",
        "passthrough",
        "-c:a",
        "aac",
        "-ar",
        "22050",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        "-shortest",
        "-y",
        str(output),
    )
    if not output.is_file() or output.stat().st_size <= 0:
        raise LgplFfmpegCandidateError(
            "candidate h264_mf/AAC roundtrip did not create an MP4"
        )
    probe = validate_synthetic_probe_output(
        _run(
            ffprobe,
            "-v",
            "error",
            "-count_frames",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(output),
        )
    )
    _run(
        executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        str(output),
        "-map",
        "0:v:0",
        "-an",
        "-f",
        "null",
        "-",
    )
    _run(
        executable,
        "-hide_banner",
        "-loglevel",
        "error",
        "-nostdin",
        "-i",
        str(output),
        "-map",
        "0:a:0",
        "-vn",
        "-f",
        "null",
        "-",
    )
    return {
        "synthetic_h264_aac_encode_decode_verified": True,
        **probe,
        "synthetic_fps_mode": "passthrough",
        "synthetic_geometry": {
            "width": 320,
            "height": 480,
            "frame_rate": 25,
            "audio_sample_rate": 22050,
            "audio_channels": 2,
        },
        "synthetic_video_encoder": "h264_mf",
        "synthetic_audio_encoder": "aac",
        "synthetic_output_sha256": _sha256_file(output),
        "synthetic_output_size_bytes": output.stat().st_size,
    }


def audit_candidate_archive(
    archive_path: str | Path,
    *,
    output_receipt: str | Path | None = None,
) -> dict:
    identity = validate_archive_identity(archive_path)
    archive = Path(archive_path).resolve()
    with tempfile.TemporaryDirectory(prefix="fm2001-lgpl-ffmpeg-") as temp:
        temp_root = Path(temp)
        with zipfile.ZipFile(archive) as zf:
            ffmpeg_member = identity["ffmpeg_member"]
            ffprobe_member = identity["ffprobe_member"]
            executable = temp_root / "ffmpeg.exe"
            ffprobe = temp_root / "ffprobe.exe"
            executable.write_bytes(zf.read(ffmpeg_member))
            ffprobe.write_bytes(zf.read(ffprobe_member))
        version = validate_version_output(_run(executable, "-version"))
        probe_version = validate_ffprobe_version_output(_run(ffprobe, "-version"))
        codecs = validate_codec_capabilities(
            decoders_text=_run(executable, "-hide_banner", "-decoders"),
            encoders_text=_run(executable, "-hide_banner", "-encoders"),
        )
        roundtrip = validate_synthetic_h264_aac_roundtrip(
            executable,
            ffprobe,
            temp_root,
        )
        executable_sha256 = _sha256_file(executable)
        executable_size_bytes = executable.stat().st_size
        ffprobe_sha256 = _sha256_file(ffprobe)
        ffprobe_size_bytes = ffprobe.stat().st_size

    report = {
        "schema_version": 1,
        "audit_kind": "gate17_lgpl_ffmpeg_candidate",
        "release_tag": RELEASE_TAG,
        "archive_url": ARCHIVE_URL,
        **identity,
        **version,
        **probe_version,
        **codecs,
        **roundtrip,
        "ffmpeg_executable_sha256": executable_sha256,
        "ffmpeg_executable_size_bytes": executable_size_bytes,
        "ffprobe_executable_sha256": ffprobe_sha256,
        "ffprobe_executable_size_bytes": ffprobe_size_bytes,
        "proposed_startup_video_encoder": "h264_mf",
        "existing_startup_audio_encoder": "aac",
        "production_runtime_switched": False,
        "windows11_conversion_verified": False,
        "windows11_playback_verified": False,
        "license_compliance_claimed": False,
    }
    if output_receipt is not None:
        output = Path(output_receipt)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path)
    args = parser.parse_args()
    report = audit_candidate_archive(
        args.archive,
        output_receipt=args.output_receipt,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
