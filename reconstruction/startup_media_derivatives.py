"""Verify private converted FM2001 startup media before runtime playback.

This module is the immutable handoff between the private conversion receipt and
any future Windows playback surface. It does not play media. It revalidates the
receipt against the canonical TGQ source/metadata contract, rehashes every
converted derivative, requires the proven startup order, and returns only files
that remain outside Git.

The original playback flag is retained neutrally. Skip input, fades,
scaling/interlace treatment and transition behavior remain separate evidence
questions.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Iterable, Mapping

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    OriginalStartupMediaSpec,
    StartupMediaConversionProfile,
)


class StartupMediaDerivativeError(ValueError):
    """A private startup-media receipt or derivative is stale or inconsistent."""


@dataclass(frozen=True)
class VerifiedStartupMediaDerivative:
    sequence: int
    spec: OriginalStartupMediaSpec
    path: Path
    converted_sha256: str
    converted_size_bytes: int
    container: str
    video_codec: str
    pixel_format: str
    audio_codec: str


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_outside_repository(path: Path, repo_root: Path, *, label: str) -> Path:
    target = Path(path).resolve()
    root = Path(repo_root).resolve()
    if target == root or target.is_relative_to(root):
        raise StartupMediaDerivativeError(
            f"{label} must remain outside the Git repository"
        )
    return target


def _require_exact(value: object, expected: object, *, label: str) -> None:
    if value != expected:
        raise StartupMediaDerivativeError(
            f"{label} differs from the verified startup-media contract"
        )


def _require_int(value: object, *, label: str) -> int:
    if isinstance(value, bool):
        raise StartupMediaDerivativeError(f"{label} must be an integer")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise StartupMediaDerivativeError(f"{label} must be an integer") from exc


def load_verified_startup_media_derivatives(
    *,
    receipt_path: Path,
    repo_root: Path,
    specs: Iterable[OriginalStartupMediaSpec] = ORIGINAL_STARTUP_MEDIA_SEQUENCE,
    profile: StartupMediaConversionProfile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
) -> tuple[VerifiedStartupMediaDerivative, ...]:
    """Load only untampered converted files backed by the private receipt.

    The conversion receipt itself is not sufficient: each derivative is
    physically re-sized and re-hashed on every load. This function intentionally
    does not require the original TGQ bytes at playback time because their exact
    identities are bound into the receipt and checked against the canonical specs.
    """
    receipt = _require_outside_repository(
        receipt_path,
        repo_root,
        label="Startup-media conversion receipt",
    )
    if not receipt.is_file():
        raise StartupMediaDerivativeError(
            f"Startup-media conversion receipt does not exist: {receipt}"
        )
    try:
        payload = json.loads(receipt.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise StartupMediaDerivativeError(
            "Startup-media conversion receipt is not readable JSON"
        ) from exc
    if not isinstance(payload, Mapping):
        raise StartupMediaDerivativeError(
            "Startup-media conversion receipt root must be an object"
        )

    _require_exact(payload.get("schema_version"), 1, label="Receipt schema_version")
    _require_exact(payload.get("passed"), True, label="Receipt passed flag")
    _require_exact(
        payload.get("audit_kind"),
        "private_original_startup_media_conversion",
        label="Receipt audit_kind",
    )
    # The receipt is evidence for conversion only. It must never self-promote a
    # roadmap completion claim.
    _require_exact(
        payload.get("gate14_complete"),
        False,
        label="Receipt Gate-14 completion boundary",
    )

    raw_profile = payload.get("profile")
    if not isinstance(raw_profile, Mapping):
        raise StartupMediaDerivativeError("Receipt conversion profile is missing")
    expected_profile = {
        "container": profile.container_name,
        "video_encoder": profile.ffmpeg_video_encoder,
        "video_codec": profile.probe_video_codec,
        "pixel_format": profile.pixel_format,
        "audio_encoder": profile.ffmpeg_audio_encoder,
        "audio_codec": profile.probe_audio_codec,
    }
    if dict(raw_profile) != expected_profile:
        raise StartupMediaDerivativeError(
            "Receipt conversion profile differs from the verified contract"
        )

    ordered_specs = tuple(specs)
    if not ordered_specs:
        raise StartupMediaDerivativeError(
            "Startup-media derivative sequence cannot be empty"
        )
    raw_outputs = payload.get("outputs")
    if not isinstance(raw_outputs, list) or len(raw_outputs) != len(ordered_specs):
        raise StartupMediaDerivativeError(
            "Receipt output count differs from the verified startup sequence"
        )

    verified: list[VerifiedStartupMediaDerivative] = []
    seen_paths: set[Path] = set()
    for sequence, (raw, spec) in enumerate(zip(raw_outputs, ordered_specs, strict=True)):
        if not isinstance(raw, Mapping):
            raise StartupMediaDerivativeError(
                f"Receipt output {sequence} is not an object"
            )
        _require_exact(raw.get("sequence"), sequence, label=f"Output {sequence} sequence")
        _require_exact(
            raw.get("source_path"), spec.source_path,
            label=f"Output {sequence} source_path",
        )
        _require_exact(
            raw.get("source_sha256"), spec.source_sha256,
            label=f"Output {sequence} source_sha256",
        )
        _require_exact(
            _require_int(raw.get("source_size_bytes"), label="source_size_bytes"),
            spec.size_bytes,
            label=f"Output {sequence} source_size_bytes",
        )
        _require_exact(
            raw.get("startup_callsite_va"),
            f"0x{spec.startup_callsite_va:X}",
            label=f"Output {sequence} startup_callsite_va",
        )
        _require_exact(
            raw.get("playback_wrapper_va"),
            f"0x{spec.playback_wrapper_va:X}",
            label=f"Output {sequence} playback_wrapper_va",
        )
        _require_exact(
            raw.get("playback_flag_bit0"),
            spec.playback_flag_bit0,
            label=f"Output {sequence} playback_flag_bit0",
        )

        for key, expected in (
            ("container", profile.container_name),
            ("video_codec", profile.probe_video_codec),
            ("video_width", spec.video_width),
            ("video_height", spec.video_height),
            ("frame_rate", spec.frame_rate),
            ("decoded_video_frames", spec.decoded_video_frames),
            ("pixel_format", profile.pixel_format),
            ("audio_codec", profile.probe_audio_codec),
            ("audio_sample_rate", spec.audio_sample_rate),
            ("audio_channels", spec.audio_channels),
        ):
            actual = raw.get(key)
            if isinstance(expected, int):
                actual = _require_int(actual, label=f"Output {sequence} {key}")
            _require_exact(
                actual,
                expected,
                label=f"Output {sequence} {key}",
            )

        raw_path = raw.get("converted_path")
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise StartupMediaDerivativeError(
                f"Output {sequence} converted_path is missing"
            )
        path = _require_outside_repository(
            Path(raw_path),
            repo_root,
            label=f"Output {sequence} converted media",
        )
        if path in seen_paths:
            raise StartupMediaDerivativeError(
                "Receipt reuses one converted path for multiple startup items"
            )
        seen_paths.add(path)
        if not path.is_file():
            raise StartupMediaDerivativeError(
                f"Converted startup media does not exist: {path}"
            )

        expected_size = _require_int(
            raw.get("converted_size_bytes"),
            label=f"Output {sequence} converted_size_bytes",
        )
        if expected_size <= 0 or path.stat().st_size != expected_size:
            raise StartupMediaDerivativeError(
                f"Output {sequence} converted size differs from receipt"
            )
        expected_digest = raw.get("converted_sha256")
        if not isinstance(expected_digest, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_digest
        ):
            raise StartupMediaDerivativeError(
                f"Output {sequence} converted_sha256 is invalid"
            )
        if _sha256_file(path) != expected_digest:
            raise StartupMediaDerivativeError(
                f"Output {sequence} converted bytes differ from receipt"
            )

        verified.append(
            VerifiedStartupMediaDerivative(
                sequence=sequence,
                spec=spec,
                path=path,
                converted_sha256=expected_digest,
                converted_size_bytes=expected_size,
                container=profile.container_name,
                video_codec=profile.probe_video_codec,
                pixel_format=profile.pixel_format,
                audio_codec=profile.probe_audio_codec,
            )
        )

    return tuple(verified)
