"""Fail-closed archive-member audit for Gate-17 minimal FFmpeg link maps."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import shlex


class LinkMapAuditError(RuntimeError):
    """Raised when link-map evidence is incomplete or drifts from the release link."""


TARGETS = ("ffmpeg_g.exe", "ffprobe_g.exe")
MAP_FLAGS = {
    "ffmpeg_g.exe": "-Wl,-Map,ffmpeg-link.map",
    "ffprobe_g.exe": "-Wl,-Map,ffprobe-link.map",
}
_ABS_WINDOWS_RE = re.compile(r"^[A-Za-z]:/")
_ARCHIVE_MEMBER_RE = re.compile(
    r"(?P<archive>[A-Za-z]:[\\/][^()\r\n]*?\.a)\((?P<member>[^()\r\n]+)\)"
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_windows_path(value: str) -> str:
    path = value.strip().replace("\\", "/")
    if not _ABS_WINDOWS_RE.match(path):
        raise LinkMapAuditError(f"not an absolute Windows path: {value!r}")
    normalized = posixpath.normpath(path)
    return normalized.casefold()


def _command_tokens(text: str, target: str) -> list[str]:
    matches: list[list[str]] = []
    for line in text.splitlines():
        if target not in line or " -o " not in f" {line} ":
            continue
        try:
            tokens = shlex.split(line, posix=True)
        except ValueError:
            continue
        try:
            output_index = tokens.index("-o")
        except ValueError:
            continue
        if output_index + 1 < len(tokens) and tokens[output_index + 1] == target:
            matches.append(tokens)
    if len(matches) != 1:
        raise LinkMapAuditError(
            f"expected exactly one final link command for {target}, found {len(matches)}"
        )
    return matches[0]


def _normalize_map_command(tokens: list[str], target: str) -> list[str]:
    flag = MAP_FLAGS[target]
    count = tokens.count(flag)
    if count != 1:
        raise LinkMapAuditError(
            f"{target} map relink must contain exactly one {flag}, found {count}"
        )
    return [token for token in tokens if token != flag]


def _ownership_rows(payload: dict, target: str) -> dict[str, dict]:
    if payload.get("passed") is not True:
        raise LinkMapAuditError("ownership proof did not pass")
    if payload.get("package_lock_ownership_validated") is not True:
        raise LinkMapAuditError("ownership proof did not validate package lock")
    if payload.get("critical_source_family_mapping_validated") is not True:
        raise LinkMapAuditError("ownership proof did not validate source-family mappings")
    target_payload = payload.get("targets", {}).get(target)
    if not isinstance(target_payload, dict):
        raise LinkMapAuditError(f"ownership proof is missing target {target}")
    inputs = target_payload.get("inputs")
    if not isinstance(inputs, list) or not inputs:
        raise LinkMapAuditError(f"ownership proof has no inputs for {target}")

    rows: dict[str, dict] = {}
    for item in inputs:
        if not isinstance(item, dict):
            raise LinkMapAuditError(f"{target} ownership row is not an object")
        trace_path = item.get("trace_path")
        package = item.get("package")
        version = item.get("version")
        source_family = item.get("source_family")
        if not all(isinstance(value, str) and value for value in (
            trace_path, package, version, source_family
        )):
            raise LinkMapAuditError(f"{target} ownership row is incomplete")
        key = _normalize_windows_path(trace_path)
        if key in rows:
            raise LinkMapAuditError(f"duplicate normalized ownership path for {target}: {trace_path}")
        rows[key] = {
            "trace_path": trace_path.replace("\\", "/"),
            "normalized_path": item.get("normalized_path"),
            "package": package,
            "version": version,
            "source_family": source_family,
        }
    return rows


def _map_evidence(text: str) -> tuple[dict[str, set[str]], set[str]]:
    header = "Archive member included to satisfy reference by file (symbol)"
    start = text.find(header)
    if start < 0:
        raise LinkMapAuditError("link map is missing GNU ld archive-member inclusion section")
    section = text[start + len(header):]
    end_positions = [
        position
        for marker in (
            "Allocating common symbols",
            "Discarded input sections",
            "Memory Configuration",
            "Linker script and memory map",
        )
        if (position := section.find(marker)) >= 0
    ]
    if end_positions:
        section = section[: min(end_positions)]

    archive_members: dict[str, set[str]] = {}
    for match in _ARCHIVE_MEMBER_RE.finditer(section):
        archive = match.group("archive").replace("\\", "/")
        member = match.group("member").strip()
        if not member:
            continue
        key = _normalize_windows_path(archive)
        archive_members.setdefault(key, set()).add(member)
    if not archive_members:
        raise LinkMapAuditError("link map archive-member inclusion section is empty")

    direct_objects: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line.startswith("LOAD "):
            continue
        loaded = line[5:].strip().replace("\\", "/")
        if not _ABS_WINDOWS_RE.match(loaded) or not loaded.casefold().endswith(".o"):
            continue
        direct_objects.add(_normalize_windows_path(loaded))
    return archive_members, direct_objects


def _target_receipt(
    *,
    target: str,
    release_log: str,
    map_build_log: str,
    map_text: str,
    ownership: dict,
    release_binary: Path,
    mapped_binary: Path,
) -> dict:
    release_command = _command_tokens(release_log, target)
    map_command = _command_tokens(map_build_log, target)
    if _normalize_map_command(map_command, target) != release_command:
        raise LinkMapAuditError(
            f"{target} map relink drifted from release link beyond {MAP_FLAGS[target]}"
        )

    release_sha = _sha256(release_binary)
    mapped_sha = _sha256(mapped_binary)
    if release_sha != mapped_sha:
        raise LinkMapAuditError(
            f"{target} map relink binary differs from release unstripped binary"
        )

    owner_rows = _ownership_rows(ownership, target)
    expected_archives = {
        path for path in owner_rows if path.endswith(".a")
    }
    expected_objects = {
        path for path in owner_rows if path.endswith(".o")
    }
    if expected_archives | expected_objects != set(owner_rows):
        unsupported = sorted(set(owner_rows) - expected_archives - expected_objects)
        raise LinkMapAuditError(f"{target} ownership proof has unsupported inputs: {unsupported!r}")

    archive_members, direct_objects = _map_evidence(map_text)
    unknown_archives = sorted(set(archive_members) - expected_archives)
    if unknown_archives:
        raise LinkMapAuditError(
            f"{target} map contains unowned external archive members: {unknown_archives!r}"
        )
    missing_objects = sorted(expected_objects - direct_objects)
    extra_objects = sorted(direct_objects - expected_objects)
    if missing_objects or extra_objects:
        raise LinkMapAuditError(
            f"{target} direct-object coverage mismatch: "
            f"missing={missing_objects!r} extra={extra_objects!r}"
        )

    contributing_archives: list[dict] = []
    contributing_packages: dict[tuple[str, str, str], dict] = {}
    for archive_key in sorted(archive_members):
        members = sorted(archive_members[archive_key])
        if not members:
            continue
        owner = owner_rows[archive_key]
        contributing_archives.append({
            "trace_path": owner["trace_path"],
            "package": owner["package"],
            "version": owner["version"],
            "source_family": owner["source_family"],
            "member_count": len(members),
            "members": members,
        })
        package_key = (owner["package"], owner["version"], owner["source_family"])
        contributing_packages[package_key] = {
            "package": owner["package"],
            "version": owner["version"],
            "source_family": owner["source_family"],
        }

    direct_object_rows: list[dict] = []
    for object_key in sorted(direct_objects):
        owner = owner_rows[object_key]
        direct_object_rows.append({
            "trace_path": owner["trace_path"],
            "package": owner["package"],
            "version": owner["version"],
            "source_family": owner["source_family"],
        })
        package_key = (owner["package"], owner["version"], owner["source_family"])
        contributing_packages[package_key] = {
            "package": owner["package"],
            "version": owner["version"],
            "source_family": owner["source_family"],
        }

    noncontributing_archives = [
        owner_rows[path]["trace_path"]
        for path in sorted(expected_archives - set(archive_members))
    ]

    return {
        "release_command_token_count": len(release_command),
        "map_observation_flag": MAP_FLAGS[target],
        "map_command_matches_release_after_removing_observation_flag": True,
        "release_unstripped_sha256": release_sha,
        "mapped_unstripped_sha256": mapped_sha,
        "unstripped_binary_byte_identical": True,
        "traced_external_archive_count": len(expected_archives),
        "contributing_external_archive_count": len(contributing_archives),
        "traced_but_noncontributing_external_archives": noncontributing_archives,
        "contributing_external_archives": contributing_archives,
        "direct_external_object_count": len(direct_object_rows),
        "direct_external_objects": direct_object_rows,
        "contributing_owner_packages": [
            contributing_packages[key] for key in sorted(contributing_packages)
        ],
    }


def audit_link_maps(
    *,
    release_build_log: Path,
    ffmpeg_map_build_log: Path,
    ffprobe_map_build_log: Path,
    ffmpeg_map: Path,
    ffprobe_map: Path,
    ownership_proof: Path,
    release_ffmpeg_unstripped: Path,
    release_ffprobe_unstripped: Path,
    mapped_ffmpeg_unstripped: Path,
    mapped_ffprobe_unstripped: Path,
) -> dict:
    release_log = release_build_log.read_text(encoding="utf-8", errors="replace")
    ownership = json.loads(ownership_proof.read_text(encoding="utf-8"))
    configs = {
        "ffmpeg_g.exe": {
            "map_build_log": ffmpeg_map_build_log,
            "map": ffmpeg_map,
            "release_binary": release_ffmpeg_unstripped,
            "mapped_binary": mapped_ffmpeg_unstripped,
        },
        "ffprobe_g.exe": {
            "map_build_log": ffprobe_map_build_log,
            "map": ffprobe_map,
            "release_binary": release_ffprobe_unstripped,
            "mapped_binary": mapped_ffprobe_unstripped,
        },
    }

    targets: dict[str, dict] = {}
    package_union: dict[tuple[str, str, str], dict] = {}
    for target in TARGETS:
        config = configs[target]
        target_receipt = _target_receipt(
            target=target,
            release_log=release_log,
            map_build_log=config["map_build_log"].read_text(
                encoding="utf-8", errors="replace"
            ),
            map_text=config["map"].read_text(encoding="utf-8", errors="replace"),
            ownership=ownership,
            release_binary=config["release_binary"],
            mapped_binary=config["mapped_binary"],
        )
        targets[target] = target_receipt
        for package in target_receipt["contributing_owner_packages"]:
            key = (
                package["package"],
                package["version"],
                package["source_family"],
            )
            package_union[key] = package

    return {
        "schema_version": 1,
        "passed": True,
        "evidence_scope": (
            "byte-identical observation relink plus GNU ld archive-member/direct-object map"
        ),
        "targets": targets,
        "unique_contributing_owner_package_count": len(package_union),
        "contributing_owner_packages": [
            package_union[key] for key in sorted(package_union)
        ],
        "archive_member_contribution_proof_complete": True,
        "direct_object_contribution_proof_complete": True,
        "static_contributor_attribution_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-build-log", type=Path, required=True)
    parser.add_argument("--ffmpeg-map-build-log", type=Path, required=True)
    parser.add_argument("--ffprobe-map-build-log", type=Path, required=True)
    parser.add_argument("--ffmpeg-map", type=Path, required=True)
    parser.add_argument("--ffprobe-map", type=Path, required=True)
    parser.add_argument("--ownership-proof", type=Path, required=True)
    parser.add_argument("--release-ffmpeg-unstripped", type=Path, required=True)
    parser.add_argument("--release-ffprobe-unstripped", type=Path, required=True)
    parser.add_argument("--mapped-ffmpeg-unstripped", type=Path, required=True)
    parser.add_argument("--mapped-ffprobe-unstripped", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    receipt = audit_link_maps(
        release_build_log=args.release_build_log,
        ffmpeg_map_build_log=args.ffmpeg_map_build_log,
        ffprobe_map_build_log=args.ffprobe_map_build_log,
        ffmpeg_map=args.ffmpeg_map,
        ffprobe_map=args.ffprobe_map,
        ownership_proof=args.ownership_proof,
        release_ffmpeg_unstripped=args.release_ffmpeg_unstripped,
        release_ffprobe_unstripped=args.release_ffprobe_unstripped,
        mapped_ffmpeg_unstripped=args.mapped_ffmpeg_unstripped,
        mapped_ffprobe_unstripped=args.mapped_ffprobe_unstripped,
    )
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
