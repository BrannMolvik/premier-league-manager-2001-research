"""Resolve the optional Gate-17 minimal-FFmpeg package-candidate profile.

The ordinary production package contains no profile marker and therefore keeps
using DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE (libx264). A separately built
Gate-17 candidate may include runtime_tools/startup-media-profile.json. That
marker is accepted only when it is fail-closed, bound to the exact bundled
ffmpeg.exe hash, and explicitly remains non-production.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE,
    StartupMediaConversionProfile,
)


class PackagedStartupMediaProfileError(RuntimeError):
    """Raised when an optional packaged startup-media profile is invalid."""


PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH = (
    Path("runtime_tools") / "startup-media-profile.json"
)
CANDIDATE_PROFILE_AUDIT_KIND = "gate17_minimal_ffmpeg_package_candidate"
CANDIDATE_PROFILE_NAME = "windows_media_foundation_h264_mf"
CANDIDATE_PROFILE_SCHEMA_VERSION = 1


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_digest(value: object, *, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise PackagedStartupMediaProfileError(
            f"{label} must be a lowercase SHA-256 string"
        )
    return value


def candidate_profile_contract() -> dict:
    profile = WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE
    return {
        "profile_name": CANDIDATE_PROFILE_NAME,
        "video_encoder": profile.ffmpeg_video_encoder,
        "audio_encoder": profile.ffmpeg_audio_encoder,
        "video_codec": profile.probe_video_codec,
        "audio_codec": profile.probe_audio_codec,
        "pixel_format": profile.pixel_format,
        "container": profile.container_name,
        "video_filter": profile.video_filter,
        "output_width": profile.output_width,
        "output_height": profile.output_height,
    }


def candidate_profile_marker_payload(
    *,
    ffmpeg_sha256: str,
    build_proof_sha256: str,
    roundtrip_proof_sha256: str,
    source_commit: str,
) -> dict:
    """Create the only marker shape accepted by the runtime candidate path."""
    return {
        "schema_version": CANDIDATE_PROFILE_SCHEMA_VERSION,
        "audit_kind": CANDIDATE_PROFILE_AUDIT_KIND,
        "candidate_only": True,
        "profile": candidate_profile_contract(),
        "source_commit": str(source_commit),
        "ffmpeg_sha256": _require_digest(ffmpeg_sha256, label="ffmpeg_sha256"),
        "build_proof_sha256": _require_digest(
            build_proof_sha256, label="build_proof_sha256"
        ),
        "roundtrip_proof_sha256": _require_digest(
            roundtrip_proof_sha256, label="roundtrip_proof_sha256"
        ),
        "build_verified": True,
        "synthetic_roundtrip_verified": True,
        "exact_original_tgq_verified": False,
        "external_windows11_playback_verified": False,
        "source_material_complete": False,
        "production_migration_ready": False,
        "production_runtime_switched": False,
        "legal_compliance_claimed": False,
    }


def validate_candidate_profile_marker(
    marker_path: str | Path,
    ffmpeg_executable: str | Path,
) -> dict:
    marker = Path(marker_path)
    ffmpeg = Path(ffmpeg_executable)
    if not marker.is_file():
        raise PackagedStartupMediaProfileError(
            f"startup-media candidate profile marker is missing: {marker}"
        )
    if not ffmpeg.is_file():
        raise PackagedStartupMediaProfileError(
            f"candidate FFmpeg executable is missing: {ffmpeg}"
        )
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PackagedStartupMediaProfileError(
            "startup-media candidate profile marker is unreadable"
        ) from exc
    if not isinstance(payload, Mapping):
        raise PackagedStartupMediaProfileError(
            "startup-media candidate profile marker root must be an object"
        )

    if payload.get("schema_version") != CANDIDATE_PROFILE_SCHEMA_VERSION:
        raise PackagedStartupMediaProfileError(
            "startup-media candidate profile schema drifted"
        )
    if payload.get("audit_kind") != CANDIDATE_PROFILE_AUDIT_KIND:
        raise PackagedStartupMediaProfileError(
            "startup-media candidate profile audit kind drifted"
        )
    if payload.get("candidate_only") is not True:
        raise PackagedStartupMediaProfileError(
            "startup-media candidate profile must remain candidate-only"
        )
    if payload.get("profile") != candidate_profile_contract():
        raise PackagedStartupMediaProfileError(
            "startup-media candidate conversion profile drifted"
        )

    expected_ffmpeg = _require_digest(
        payload.get("ffmpeg_sha256"), label="ffmpeg_sha256"
    )
    if _sha256_file(ffmpeg) != expected_ffmpeg:
        raise PackagedStartupMediaProfileError(
            "bundled ffmpeg.exe differs from candidate profile marker"
        )
    _require_digest(payload.get("build_proof_sha256"), label="build_proof_sha256")
    _require_digest(
        payload.get("roundtrip_proof_sha256"),
        label="roundtrip_proof_sha256",
    )
    source_commit = payload.get("source_commit")
    if (
        not isinstance(source_commit, str)
        or len(source_commit) != 40
        or any(ch not in "0123456789abcdef" for ch in source_commit)
    ):
        raise PackagedStartupMediaProfileError(
            "candidate profile source_commit must be a complete lowercase Git SHA"
        )

    required_true = ("build_verified", "synthetic_roundtrip_verified")
    for field in required_true:
        if payload.get(field) is not True:
            raise PackagedStartupMediaProfileError(
                f"startup-media candidate marker requires {field}=true"
            )
    required_false = (
        "exact_original_tgq_verified",
        "external_windows11_playback_verified",
        "source_material_complete",
        "production_migration_ready",
        "production_runtime_switched",
        "legal_compliance_claimed",
    )
    for field in required_false:
        if payload.get(field) is not False:
            raise PackagedStartupMediaProfileError(
                f"startup-media candidate marker requires {field}=false"
            )
    return dict(payload)


def resolve_packaged_startup_media_profile(
    application_root: str | Path,
    ffmpeg_executable: str | Path,
) -> tuple[StartupMediaConversionProfile, dict | None]:
    """Return production default unless an exact non-production marker is present."""
    root = Path(application_root)
    marker = root / PACKAGED_STARTUP_MEDIA_PROFILE_RELATIVE_PATH
    if not marker.exists():
        return DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE, None
    payload = validate_candidate_profile_marker(marker, ffmpeg_executable)
    return WINDOWS_MEDIA_FOUNDATION_STARTUP_MEDIA_CONVERSION_PROFILE, payload
