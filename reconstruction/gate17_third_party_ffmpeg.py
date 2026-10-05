"""Fail-closed third-party FFmpeg provenance boundary for Gate 17.

The Windows candidate intentionally bundles an FFmpeg executable because the
startup-media conversion path needs it. This module does not decide legal
compliance. It preserves the selected binary identity, produces a hash-bound
build attestation, and prevents a final release audit from passing until the
repository explicitly records complete license/source distribution material
and the exact material is present in the release archive.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import zipfile
from typing import Mapping


class ThirdPartyFFmpegError(RuntimeError):
    pass


PROVENANCE_PATH = Path("third_party/ffmpeg/PROVENANCE.json")
ATTESTATION_ARCHIVE_SUFFIX = "/runtime_tools/ffmpeg.provenance.json"
BINARY_ARCHIVE_SUFFIX = "/runtime_tools/ffmpeg.exe"
PROVENANCE_ARCHIVE_SUFFIX = "/third_party/ffmpeg/PROVENANCE.json"


def _sha256_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_digest(value: object, *, label: str) -> str:
    if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ThirdPartyFFmpegError(f"{label} must be a lowercase SHA-256 string")
    return value


def _require_mapping(value: object, *, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ThirdPartyFFmpegError(f"{label} must be an object")
    return value


def load_ffmpeg_provenance(repo_root: str | Path) -> tuple[dict, Path]:
    root = Path(repo_root).resolve()
    path = (root / PROVENANCE_PATH).resolve()
    if not path.is_relative_to(root):
        raise ThirdPartyFFmpegError("FFmpeg provenance escaped repository root")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ThirdPartyFFmpegError("FFmpeg provenance is unreadable") from exc
    if not isinstance(payload, dict):
        raise ThirdPartyFFmpegError("FFmpeg provenance root must be an object")
    if payload.get("schema_version") != 1:
        raise ThirdPartyFFmpegError("unsupported FFmpeg provenance schema")
    if payload.get("component") != "FFmpeg":
        raise ThirdPartyFFmpegError("FFmpeg provenance component drifted")
    if payload.get("bundled_binary_path") != "runtime_tools/ffmpeg.exe":
        raise ThirdPartyFFmpegError("FFmpeg bundled binary path drifted")

    provider = _require_mapping(payload.get("provider_package"), label="provider_package")
    if provider.get("name") != "imageio-ffmpeg" or provider.get("version") != "0.6.0":
        raise ThirdPartyFFmpegError(
            "FFmpeg provider must remain pinned to imageio-ffmpeg 0.6.0 until "
            "provenance is intentionally refreshed"
        )

    identity = _require_mapping(payload.get("binary_identity"), label="binary_identity")
    for field in ("version_line", "compiler_line"):
        value = identity.get(field)
        if type(value) is not str or not value.strip():
            raise ThirdPartyFFmpegError(f"binary_identity.{field} must be non-empty")
    flags = identity.get("required_configuration_flags")
    if (
        not isinstance(flags, list)
        or not flags
        or any(type(flag) is not str or not flag.startswith("--") for flag in flags)
        or len(set(flags)) != len(flags)
    ):
        raise ThirdPartyFFmpegError(
            "binary_identity.required_configuration_flags must be unique flags"
        )
    libraries = _require_mapping(
        identity.get("library_versions"),
        label="binary_identity.library_versions",
    )
    if not libraries:
        raise ThirdPartyFFmpegError("FFmpeg library version set must be non-empty")
    for name, version in libraries.items():
        if type(name) is not str or type(version) is not str or not version.strip():
            raise ThirdPartyFFmpegError("FFmpeg library version entries must be text")

    materials = _require_mapping(payload.get("release_materials"), label="release_materials")
    for field in (
        "release_ready",
        "license_material_complete",
        "source_material_complete",
    ):
        if type(materials.get(field)) is not bool:
            raise ThirdPartyFFmpegError(f"release_materials.{field} must be boolean")
    required = materials.get("required_files")
    if (
        not isinstance(required, list)
        or not required
        or any(type(item) is not str or not item.startswith("third_party/ffmpeg/") for item in required)
        or len(set(required)) != len(required)
    ):
        raise ThirdPartyFFmpegError(
            "release_materials.required_files must be unique FFmpeg third-party paths"
        )
    hashes = _require_mapping(materials.get("sha256"), label="release_materials.sha256")
    for rel, digest in hashes.items():
        if rel not in required:
            raise ThirdPartyFFmpegError(
                f"release material hash exists for unexpected path: {rel}"
            )
        _require_digest(digest, label=f"release material {rel} sha256")
    return payload, path


def validate_ffmpeg_version_output(text: str, provenance: Mapping[str, object]) -> dict:
    if type(text) is not str or not text.strip():
        raise ThirdPartyFFmpegError("FFmpeg -version output is empty")
    identity = _require_mapping(provenance.get("binary_identity"), label="binary_identity")
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines or lines[0] != identity["version_line"]:
        raise ThirdPartyFFmpegError("bundled FFmpeg version line does not match provenance")
    if len(lines) < 3 or lines[1] != identity["compiler_line"]:
        raise ThirdPartyFFmpegError("bundled FFmpeg compiler line does not match provenance")
    configuration = next(
        (line for line in lines if line.startswith("configuration:")),
        None,
    )
    if configuration is None:
        raise ThirdPartyFFmpegError("bundled FFmpeg output lacks configuration line")
    missing_flags = [
        flag
        for flag in identity["required_configuration_flags"]
        if flag not in configuration.split()
    ]
    if missing_flags:
        raise ThirdPartyFFmpegError(
            "bundled FFmpeg configuration lost required flags: "
            + ", ".join(missing_flags)
        )

    missing_libraries = []
    for name, version in identity["library_versions"].items():
        if not any(line.startswith(name) and version in line for line in lines):
            missing_libraries.append(name)
    if missing_libraries:
        raise ThirdPartyFFmpegError(
            "bundled FFmpeg library versions drifted: "
            + ", ".join(missing_libraries)
        )
    return {
        "version_line": lines[0],
        "compiler_line": lines[1],
        "configuration_line": configuration,
        "required_configuration_flags": list(identity["required_configuration_flags"]),
        "library_versions": dict(identity["library_versions"]),
    }


def create_binary_attestation(
    *,
    ffmpeg_exe: str | Path,
    repo_root: str | Path,
    output_path: str | Path,
) -> dict:
    provenance, provenance_path = load_ffmpeg_provenance(repo_root)
    executable = Path(ffmpeg_exe).resolve()
    if not executable.is_file() or executable.stat().st_size <= 0:
        raise ThirdPartyFFmpegError(f"bundled FFmpeg executable is missing: {executable}")
    try:
        result = subprocess.run(
            [str(executable), "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ThirdPartyFFmpegError("unable to execute bundled FFmpeg") from exc
    if result.returncode != 0:
        raise ThirdPartyFFmpegError(
            f"bundled FFmpeg -version failed with exit code {result.returncode}"
        )
    identity = validate_ffmpeg_version_output(result.stdout, provenance)
    provider = provenance["provider_package"]
    attestation = {
        "schema_version": 1,
        "component": "FFmpeg",
        "binary_path": "runtime_tools/ffmpeg.exe",
        "binary_sha256": _sha256_file(executable),
        "binary_size_bytes": executable.stat().st_size,
        "repository_provenance_path": PROVENANCE_PATH.as_posix(),
        "repository_provenance_sha256": _sha256_file(provenance_path),
        "provider_package": {
            "name": provider["name"],
            "version": provider["version"],
        },
        **identity,
    }
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(attestation, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return attestation


def _unique_member(names: tuple[str, ...], suffix: str, *, label: str) -> str:
    matches = tuple(name for name in names if name.replace("\\", "/").endswith(suffix))
    if len(matches) != 1:
        raise ThirdPartyFFmpegError(
            f"release archive must contain exactly one {label}; found {len(matches)}"
        )
    return matches[0]


def validate_release_archive_ffmpeg(
    *,
    repo_root: str | Path,
    release_archive: str | Path,
) -> dict:
    provenance, provenance_path = load_ffmpeg_provenance(repo_root)
    materials = provenance["release_materials"]
    if (
        materials["release_ready"] is not True
        or materials["license_material_complete"] is not True
        or materials["source_material_complete"] is not True
    ):
        raise ThirdPartyFFmpegError(
            "bundled FFmpeg release materials are not declared complete; "
            "final Gate-17 release remains blocked"
        )

    expected_hashes = materials["sha256"]
    required_files = tuple(materials["required_files"])
    if set(expected_hashes) != set(required_files):
        raise ThirdPartyFFmpegError(
            "completed FFmpeg release materials require a SHA-256 for every required file"
        )

    archive_path = Path(release_archive).resolve()
    if not archive_path.is_file():
        raise ThirdPartyFFmpegError(f"release archive is missing: {archive_path}")
    try:
        with zipfile.ZipFile(archive_path) as zf:
            names = tuple(zf.namelist())
            binary_member = _unique_member(
                names, BINARY_ARCHIVE_SUFFIX, label="runtime_tools/ffmpeg.exe"
            )
            attestation_member = _unique_member(
                names,
                ATTESTATION_ARCHIVE_SUFFIX,
                label="runtime_tools/ffmpeg.provenance.json",
            )
            provenance_member = _unique_member(
                names,
                PROVENANCE_ARCHIVE_SUFFIX,
                label="third_party/ffmpeg/PROVENANCE.json",
            )
            archive_provenance = zf.read(provenance_member)
            repository_provenance = provenance_path.read_bytes()
            if _sha256_bytes(archive_provenance) != _sha256_bytes(repository_provenance):
                raise ThirdPartyFFmpegError(
                    "release FFmpeg provenance does not match repository provenance"
                )

            try:
                attestation = json.loads(zf.read(attestation_member).decode("utf-8"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ThirdPartyFFmpegError(
                    "release FFmpeg binary attestation is unreadable"
                ) from exc
            if not isinstance(attestation, dict) or attestation.get("schema_version") != 1:
                raise ThirdPartyFFmpegError("release FFmpeg binary attestation schema drifted")
            binary_bytes = zf.read(binary_member)
            if attestation.get("binary_sha256") != _sha256_bytes(binary_bytes):
                raise ThirdPartyFFmpegError(
                    "release FFmpeg binary hash does not match its attestation"
                )
            if attestation.get("binary_size_bytes") != len(binary_bytes):
                raise ThirdPartyFFmpegError(
                    "release FFmpeg binary size does not match its attestation"
                )
            if attestation.get("repository_provenance_sha256") != _sha256_file(provenance_path):
                raise ThirdPartyFFmpegError(
                    "release FFmpeg attestation is bound to different provenance"
                )
            provider = provenance["provider_package"]
            if attestation.get("provider_package") != {
                "name": provider["name"],
                "version": provider["version"],
            }:
                raise ThirdPartyFFmpegError(
                    "release FFmpeg provider package does not match provenance"
                )

            checked_materials = {}
            for relative in required_files:
                member = _unique_member(
                    names,
                    "/" + relative,
                    label=relative,
                )
                data = zf.read(member)
                expected = _require_digest(
                    expected_hashes[relative],
                    label=f"release material {relative} sha256",
                )
                actual = _sha256_bytes(data)
                if actual != expected:
                    raise ThirdPartyFFmpegError(
                        f"release material hash mismatch for {relative}"
                    )
                checked_materials[relative] = actual
    except zipfile.BadZipFile as exc:
        raise ThirdPartyFFmpegError("release archive is not a readable ZIP") from exc

    return {
        "component": "FFmpeg",
        "provider_package": dict(provenance["provider_package"]),
        "repository_provenance_path": PROVENANCE_PATH.as_posix(),
        "repository_provenance_sha256": _sha256_file(provenance_path),
        "binary_sha256": attestation["binary_sha256"],
        "binary_size_bytes": attestation["binary_size_bytes"],
        "release_materials_complete": True,
        "release_material_sha256": checked_materials,
        "legal_compliance_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ffmpeg-exe", type=Path, required=True)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--output-attestation", type=Path, required=True)
    args = parser.parse_args()
    result = create_binary_attestation(
        ffmpeg_exe=args.ffmpeg_exe,
        repo_root=args.repo_root,
        output_path=args.output_attestation,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
