"""Audit one exact Windows build of the Gate-17 minimal FFmpeg helper.

This audit proves only that the pinned source commit built into ffmpeg.exe and
ffprobe.exe with the source-contract components and without an unexpected
MinGW/MSYS runtime DLL dependency. It does not prove exact original TGQ
conversion, external Windows 11 playback, source-material completeness, legal
compliance, or production migration readiness.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import shlex
import subprocess
from typing import Iterable

from gate17_ffmpeg_minimal_source_contract import (
    PINNED_FFMPEG_COMMIT,
    audit_source_contract,
    load_contract,
)


class MinimalFfmpegBuildAuditError(RuntimeError):
    pass


FORBIDDEN_CONFIGURATION_FLAGS = (
    "--enable-gpl",
    "--enable-nonfree",
    "--enable-version3",
)
FORBIDDEN_RUNTIME_DLL_PATTERNS = (
    re.compile(r"^libgcc", re.I),
    re.compile(r"^libstdc\+\+", re.I),
    re.compile(r"^libwinpthread", re.I),
    re.compile(r"^libssp", re.I),
    re.compile(r"^msys-", re.I),
)
REQUIRED_DECODERS = {
    "eatgq",
    "adpcm_ea",
    "adpcm_ea_r1",
    "adpcm_ea_r2",
    "adpcm_ea_r3",
    "adpcm_ima_ea_eacs",
    "adpcm_ima_ea_sead",
    "adpcm_psx",
    "pcm_mulaw",
    "pcm_s16le",
    "pcm_s16le_planar",
    "pcm_s8",
    "mp3",
    "h264",
    "aac",
}
REQUIRED_ENCODERS = {"h264_mf", "aac"}
REQUIRED_DEMUXERS = {"ea", "mov"}
REQUIRED_MUXERS = {"mp4", "null"}
REQUIRED_PROTOCOLS = {"file", "pipe"}
REQUIRED_FILTERS = {"aresample", "scale"}
GROUPED_COMPONENT_OPTIONS = {
    "protocol",
    "decoder",
    "encoder",
    "demuxer",
    "muxer",
    "filter",
}


def _normalized_configuration_tokens(args: Iterable[str]) -> set[str]:
    """Normalize FFmpeg's comma-list component syntax.

    FFmpeg's configure parser accepts e.g. --enable-decoder=aac,h264 but its
    generated configuration string may serialize the same request as separate
    --enable-decoder=aac --enable-decoder=h264 tokens. Treat those two spellings
    as equivalent while preserving exact matching for every other option.
    """
    normalized: set[str] = set()
    for arg in args:
        match = re.fullmatch(r"--enable-([a-z0-9_-]+)=([^\s]+)", arg)
        if (
            match is None
            or match.group(1) not in GROUPED_COMPONENT_OPTIONS
            or "," not in match.group(2)
        ):
            normalized.add(arg)
            continue
        option = match.group(1)
        for value in match.group(2).split(","):
            if not value:
                raise MinimalFfmpegBuildAuditError(
                    f"empty value in grouped configure option: {arg}"
                )
            normalized.add(f"--enable-{option}={value}")
    return normalized


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_file(path: str | Path, label: str) -> Path:
    target = Path(path).resolve()
    if not target.is_file() or target.stat().st_size <= 0:
        raise MinimalFfmpegBuildAuditError(f"{label} is missing or empty: {target}")
    return target


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
        raise MinimalFfmpegBuildAuditError(
            f"unable to execute {executable.name}: {exc}"
        ) from exc
    if result.returncode != 0:
        raise MinimalFfmpegBuildAuditError(
            f"{executable.name} {' '.join(args)} failed with exit code "
            f"{result.returncode}: {(result.stdout or '')[-2500:]}"
        )
    return result.stdout or ""


def _version_contract(text: str, *, label: str, configure_args: Iterable[str]) -> dict:
    lines = tuple(line.strip() for line in text.splitlines() if line.strip())
    if not lines or not lines[0].lower().startswith(label.lower() + " version "):
        raise MinimalFfmpegBuildAuditError(f"{label} version line is invalid")
    configuration = next(
        (line for line in lines if line.startswith("configuration:")),
        None,
    )
    if configuration is None:
        raise MinimalFfmpegBuildAuditError(f"{label} configuration line is missing")
    try:
        tokens = set(shlex.split(configuration.split(":", 1)[1].strip(), posix=True))
    except ValueError as exc:
        raise MinimalFfmpegBuildAuditError(
            f"{label} configuration line has invalid shell quoting"
        ) from exc
    normalized_actual = _normalized_configuration_tokens(tokens)
    normalized_expected = _normalized_configuration_tokens(configure_args)
    missing = tuple(sorted(normalized_expected - normalized_actual))
    if missing:
        raise MinimalFfmpegBuildAuditError(
            f"{label} configuration omits source-contract args: {list(missing)}"
        )
    elevated = tuple(
        flag for flag in FORBIDDEN_CONFIGURATION_FLAGS if flag in normalized_actual
    )
    if elevated:
        raise MinimalFfmpegBuildAuditError(
            f"{label} unexpectedly enables elevated license flags: {list(elevated)}"
        )
    external = tuple(
        sorted(
            token
            for token in normalized_actual
            if token.startswith("--enable-lib")
        )
    )
    if external:
        raise MinimalFfmpegBuildAuditError(
            f"{label} unexpectedly enables third-party libraries: {list(external)}"
        )
    return {
        "version_line": lines[0],
        "configuration_line": configuration,
        "third_party_enable_flags": [],
        "elevated_license_flags": [],
    }


def _codec_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\s*[A-Z.]{6}\s+([A-Za-z0-9_]+)(?:\s|$)", line)
        if match is not None:
            names.add(match.group(1))
    return names


def _format_names(text: str) -> set[str]:
    names: set[str] = set()
    for line in text.splitlines():
        match = re.match(r"^\s*[D.E]{1,2}\s+([^\s]+)\s", line)
        if match is None:
            continue
        names.update(part for part in match.group(1).split(",") if part)
    return names


def _simple_names(text: str) -> set[str]:
    names: set[str] = set()
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.endswith(":") or line.startswith("-"):
            continue
        match = re.match(r"^([A-Za-z0-9_]+)(?:\s|$)", line)
        if match is not None:
            names.add(match.group(1))
    return names


def _filter_names(text: str) -> set[str]:
    """Parse the pinned FFmpeg 9 show_filters() two-flag output."""
    names: set[str] = set()
    for raw in text.splitlines():
        match = re.match(r"^\s*[T.][S.]\s+([A-Za-z0-9_]+)(?:\s|$)", raw)
        if match is not None:
            names.add(match.group(1))
    return names


def _require_subset(actual: set[str], expected: set[str], label: str) -> list[str]:
    missing = tuple(sorted(expected - actual))
    if missing:
        raise MinimalFfmpegBuildAuditError(
            f"minimal FFmpeg build is missing required {label}: {list(missing)}"
        )
    return sorted(expected)


def _parse_imports(text: str, *, label: str) -> list[str]:
    imports = sorted(
        {
            match.group(1).strip()
            for match in re.finditer(r"DLL Name:\s*([^\r\n]+)", text, re.I)
        },
        key=str.casefold,
    )
    if not imports:
        raise MinimalFfmpegBuildAuditError(f"{label} import manifest has no DLL names")
    forbidden = [
        name
        for name in imports
        if any(pattern.search(name) for pattern in FORBIDDEN_RUNTIME_DLL_PATTERNS)
    ]
    if forbidden:
        raise MinimalFfmpegBuildAuditError(
            f"{label} depends on unexpected toolchain/runtime DLLs: {forbidden}"
        )
    return imports


def audit_minimal_build(
    *,
    repo_root: str | Path,
    ffmpeg_exe: str | Path,
    ffprobe_exe: str | Path,
    source_commit_file: str | Path,
    source_license_file: str | Path,
    ffmpeg_imports_file: str | Path,
    ffprobe_imports_file: str | Path,
) -> dict:
    contract_audit = audit_source_contract(repo_root)
    contract, _contract_path = load_contract(repo_root)
    minimal = contract["minimal_helper_target"]
    if minimal["production_migration_ready"] is not False:
        raise MinimalFfmpegBuildAuditError(
            "source contract must remain non-production-ready during build proof"
        )

    source_commit_path = _require_file(source_commit_file, "source commit receipt")
    source_commit = source_commit_path.read_text(encoding="utf-8").strip()
    if source_commit != PINNED_FFMPEG_COMMIT:
        raise MinimalFfmpegBuildAuditError(
            f"built source commit drifted: expected {PINNED_FFMPEG_COMMIT}, got {source_commit}"
        )

    ffmpeg = _require_file(ffmpeg_exe, "minimal ffmpeg.exe")
    ffprobe = _require_file(ffprobe_exe, "minimal ffprobe.exe")
    license_path = _require_file(source_license_file, "pinned FFmpeg license")
    if license_path.name != minimal["license_file"]:
        raise MinimalFfmpegBuildAuditError("built source license-file identity drifted")

    configure_args = tuple(minimal["configure_args"])
    ffmpeg_version = _version_contract(
        _run(ffmpeg, "-version"),
        label="ffmpeg",
        configure_args=configure_args,
    )
    ffprobe_version = _version_contract(
        _run(ffprobe, "-version"),
        label="ffprobe",
        configure_args=configure_args,
    )
    if ffmpeg_version["configuration_line"] != ffprobe_version["configuration_line"]:
        raise MinimalFfmpegBuildAuditError(
            "ffmpeg.exe and ffprobe.exe were not built from the same configuration"
        )

    decoders = _require_subset(
        _codec_names(_run(ffmpeg, "-hide_banner", "-decoders")),
        REQUIRED_DECODERS,
        "decoders",
    )
    encoders = _require_subset(
        _codec_names(_run(ffmpeg, "-hide_banner", "-encoders")),
        REQUIRED_ENCODERS,
        "encoders",
    )
    demuxers = _require_subset(
        _format_names(_run(ffmpeg, "-hide_banner", "-demuxers")),
        REQUIRED_DEMUXERS,
        "demuxers",
    )
    muxers = _require_subset(
        _format_names(_run(ffmpeg, "-hide_banner", "-muxers")),
        REQUIRED_MUXERS,
        "muxers",
    )
    protocols = _require_subset(
        _simple_names(_run(ffmpeg, "-hide_banner", "-protocols")),
        REQUIRED_PROTOCOLS,
        "protocols",
    )
    filters = _require_subset(
        _filter_names(_run(ffmpeg, "-hide_banner", "-filters")),
        REQUIRED_FILTERS,
        "filters",
    )

    ffmpeg_imports = _parse_imports(
        _require_file(ffmpeg_imports_file, "ffmpeg import manifest").read_text(
            encoding="utf-8", errors="replace"
        ),
        label="ffmpeg.exe",
    )
    ffprobe_imports = _parse_imports(
        _require_file(ffprobe_imports_file, "ffprobe import manifest").read_text(
            encoding="utf-8", errors="replace"
        ),
        label="ffprobe.exe",
    )

    return {
        "schema_version": 1,
        "audit_kind": "gate17_minimal_ffmpeg_build",
        "passed": True,
        "source_commit": source_commit,
        "source_license_file": minimal["license_file"],
        "source_license_sha256": _sha256_file(license_path),
        "ffmpeg_sha256": _sha256_file(ffmpeg),
        "ffmpeg_size_bytes": ffmpeg.stat().st_size,
        "ffprobe_sha256": _sha256_file(ffprobe),
        "ffprobe_size_bytes": ffprobe.stat().st_size,
        "ffmpeg_version": ffmpeg_version,
        "ffprobe_version": ffprobe_version,
        "required_components": {
            "decoders": decoders,
            "encoders": encoders,
            "demuxers": demuxers,
            "muxers": muxers,
            "protocols": protocols,
            "filters": filters,
        },
        "runtime_imports": {
            "ffmpeg.exe": ffmpeg_imports,
            "ffprobe.exe": ffprobe_imports,
        },
        "source_contract_audit": contract_audit,
        "build_verified": True,
        "synthetic_roundtrip_verified": False,
        "exact_original_tgq_verified": False,
        "external_windows11_playback_verified": False,
        "source_material_complete": False,
        "production_migration_ready": False,
        "legal_compliance_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--ffmpeg", type=Path, required=True)
    parser.add_argument("--ffprobe", type=Path, required=True)
    parser.add_argument("--source-commit-file", type=Path, required=True)
    parser.add_argument("--source-license-file", type=Path, required=True)
    parser.add_argument("--ffmpeg-imports", type=Path, required=True)
    parser.add_argument("--ffprobe-imports", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    result = audit_minimal_build(
        repo_root=args.repo_root,
        ffmpeg_exe=args.ffmpeg,
        ffprobe_exe=args.ffprobe,
        source_commit_file=args.source_commit_file,
        source_license_file=args.source_license_file,
        ffmpeg_imports_file=args.ffmpeg_imports,
        ffprobe_imports_file=args.ffprobe_imports,
    )
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
