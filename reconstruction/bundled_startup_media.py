"""Checksum-gated bundled derivatives of the original FM2001 startup TGQs.

The original TGQ bytes are privately verified against the authorized disc
source. The Windows port ships only the modern MP4 derivatives needed for
reliable playback. This loader binds those derivatives back to the exact
source TGQ identities and refuses byte drift, manifest drift, path traversal,
or a partial/reordered startup sequence.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from original_startup_media import (
    DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE,
    ORIGINAL_STARTUP_MEDIA_SEQUENCE,
)
from startup_media_derivatives import VerifiedStartupMediaDerivative


class BundledStartupMediaError(ValueError):
    pass


AUTHORIZED_SOURCE_ARCHIVE_SHA256 = (
    "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
)
BUNDLED_STARTUP_MEDIA_DIRECTORY = (
    Path("original_assets") / "converted" / "FMV"
)
BUNDLED_STARTUP_MEDIA_MANIFEST = (
    BUNDLED_STARTUP_MEDIA_DIRECTORY / "startup-media-manifest.json"
)


@dataclass(frozen=True)
class BundledStartupMediaSpec:
    filename: str
    size_bytes: int
    sha256: str

    def __post_init__(self) -> None:
        if Path(self.filename).name != self.filename or not self.filename:
            raise BundledStartupMediaError(
                "bundled startup-media filename must be one plain filename"
            )
        if type(self.size_bytes) is not int or self.size_bytes <= 0:
            raise BundledStartupMediaError(
                "bundled startup-media byte size must be positive"
            )
        if (
            not isinstance(self.sha256, str)
            or len(self.sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.sha256)
        ):
            raise BundledStartupMediaError(
                "bundled startup-media SHA-256 must be lowercase hexadecimal"
            )


BUNDLED_STARTUP_MEDIA_SPECS = (
    BundledStartupMediaSpec(
        "easp.mp4",
        289_307,
        "8712bca6ee0c8d0cc6d6404243c616b9bbf2ca92ea1b45f1dddf163e14ea0e5b",
    ),
    BundledStartupMediaSpec(
        "premintro.mp4",
        6_929_242,
        "852cb62724f4029744796d414605fda6d707f363eb1de373b7bf6b4ef128b193",
    ),
)


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _expected_profile() -> dict:
    profile = DEFAULT_STARTUP_MEDIA_CONVERSION_PROFILE
    return {
        "container": profile.container_name,
        "video_encoder": profile.ffmpeg_video_encoder,
        "video_codec": profile.probe_video_codec,
        "pixel_format": profile.pixel_format,
        "audio_encoder": profile.ffmpeg_audio_encoder,
        "audio_codec": profile.probe_audio_codec,
    }


def _expected_output(sequence: int) -> dict:
    source = ORIGINAL_STARTUP_MEDIA_SEQUENCE[sequence]
    converted = BUNDLED_STARTUP_MEDIA_SPECS[sequence]
    relative = (BUNDLED_STARTUP_MEDIA_DIRECTORY / converted.filename).as_posix()
    return {
        "sequence": sequence,
        "source_path": source.source_path,
        "source_sha256": source.source_sha256,
        "source_size_bytes": source.size_bytes,
        "startup_callsite_va": f"0x{source.startup_callsite_va:X}",
        "playback_wrapper_va": f"0x{source.playback_wrapper_va:X}",
        "playback_flag_bit0": source.playback_flag_bit0,
        "converted_path": relative,
        "converted_size_bytes": converted.size_bytes,
        "converted_sha256": converted.sha256,
        "container": "mp4",
        "video_codec": "h264",
        "video_width": source.video_width,
        "video_height": source.video_height,
        "frame_rate": source.frame_rate,
        "decoded_video_frames": source.decoded_video_frames,
        "pixel_format": "yuv420p",
        "audio_codec": "aac",
        "audio_sample_rate": source.audio_sample_rate,
        "audio_channels": source.audio_channels,
    }


def expected_bundled_startup_media_manifest() -> dict:
    return {
        "schema_version": 1,
        "audit_kind": "bundled_original_startup_media_derivatives",
        "source_archive_sha256": AUTHORIZED_SOURCE_ARCHIVE_SHA256,
        "profile": _expected_profile(),
        "outputs": [
            _expected_output(index)
            for index in range(len(ORIGINAL_STARTUP_MEDIA_SEQUENCE))
        ],
        "fidelity_boundary": (
            "Exact original TGQ provenance and converted stream/frame/audio "
            "geometry are verified. Native skip input, transition/fade timing, "
            "display treatment and real Windows audibility/visibility remain "
            "separate acceptance evidence."
        ),
        "gate14_complete": False,
    }


def load_bundled_startup_media_derivatives(
    application_root: str | Path,
) -> tuple[VerifiedStartupMediaDerivative, ...]:
    """Load the exact package derivatives in the source-proven startup order."""
    root = Path(application_root).resolve()
    manifest_path = root / BUNDLED_STARTUP_MEDIA_MANIFEST
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BundledStartupMediaError(
            f"bundled startup-media manifest is unavailable: {manifest_path}"
        ) from exc

    expected = expected_bundled_startup_media_manifest()
    if payload != expected:
        raise BundledStartupMediaError(
            "bundled startup-media manifest differs from the verified conversion contract"
        )

    verified = []
    for sequence, (source, converted) in enumerate(
        zip(
            ORIGINAL_STARTUP_MEDIA_SEQUENCE,
            BUNDLED_STARTUP_MEDIA_SPECS,
            strict=True,
        )
    ):
        relative = BUNDLED_STARTUP_MEDIA_DIRECTORY / converted.filename
        path = (root / relative).resolve()
        expected_parent = (root / BUNDLED_STARTUP_MEDIA_DIRECTORY).resolve()
        if path.parent != expected_parent:
            raise BundledStartupMediaError(
                "bundled startup-media path escaped its verified directory"
            )
        try:
            size = path.stat().st_size
        except OSError as exc:
            raise BundledStartupMediaError(
                f"bundled startup-media derivative is unavailable: {relative.as_posix()}"
            ) from exc
        if size != converted.size_bytes:
            raise BundledStartupMediaError(
                f"bundled startup-media size mismatch: {relative.as_posix()}"
            )
        if _sha256_file(path) != converted.sha256:
            raise BundledStartupMediaError(
                f"bundled startup-media checksum mismatch: {relative.as_posix()}"
            )
        verified.append(
            VerifiedStartupMediaDerivative(
                sequence=sequence,
                spec=source,
                path=path,
                converted_sha256=converted.sha256,
                converted_size_bytes=converted.size_bytes,
                container="mp4",
                video_codec="h264",
                pixel_format="yuv420p",
                audio_codec="aac",
            )
        )

    return tuple(verified)


def bundled_startup_media_contract() -> dict:
    return {
        "manifest_path": BUNDLED_STARTUP_MEDIA_MANIFEST.as_posix(),
        "source_archive_sha256": AUTHORIZED_SOURCE_ARCHIVE_SHA256,
        "source_order": tuple(
            item.source_path for item in ORIGINAL_STARTUP_MEDIA_SEQUENCE
        ),
        "converted_sha256": tuple(
            item.sha256 for item in BUNDLED_STARTUP_MEDIA_SPECS
        ),
        "default_package_derivatives_verified": True,
        "windows_playback_verified": False,
        "skip_input_recovered": False,
        "transition_timing_recovered": False,
        "gate14_complete": False,
    }
