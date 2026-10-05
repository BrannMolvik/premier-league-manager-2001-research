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
            license_files = tuple(name for name in names if name.endswith("/LICENSE.txt"))
            if len(exe) != 1:
                raise LgplFfmpegCandidateError(
                    f"candidate archive must contain one bin/ffmpeg.exe; found {len(exe)}"
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
            member = identity["ffmpeg_member"]
            executable = temp_root / "ffmpeg.exe"
            executable.write_bytes(zf.read(member))
        version = validate_version_output(_run(executable, "-version"))
        codecs = validate_codec_capabilities(
            decoders_text=_run(executable, "-hide_banner", "-decoders"),
            encoders_text=_run(executable, "-hide_banner", "-encoders"),
        )
        executable_sha256 = _sha256_file(executable)
        executable_size_bytes = executable.stat().st_size

    report = {
        "schema_version": 1,
        "audit_kind": "gate17_lgpl_ffmpeg_candidate",
        "release_tag": RELEASE_TAG,
        "archive_url": ARCHIVE_URL,
        **identity,
        **version,
        **codecs,
        "ffmpeg_executable_sha256": executable_sha256,
        "ffmpeg_executable_size_bytes": executable_size_bytes,
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
