"""Fail-closed final release-readiness audit for the FM2001 Windows 11 port.

This tool is intentionally stricter than ordinary development CI. A final
release receipt is created only when repository hygiene, canonical source-data
verification, the full automated suite, external Windows 11 smoke receipts,
release-archive identity, and limitations documentation all agree on one clean
repository commit.

The external receipts are deliberately separate from this repository. They are
expected to come from the clean-install / gameplay smoke procedures performed
on the actual Windows 11 release candidate. This module does not create those
facts or turn missing evidence into a pass.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from typing import Mapping


class ReleaseReadinessError(RuntimeError):
    """A Gate-17 release criterion is missing, stale or inconsistent."""


REQUIRED_PREREQUISITE_GATES = tuple(range(1, 17))
FULL_SCOPE_CATALOG_PATH = "research/GATE17_ORIGINAL_SCOPE_CATALOG.json"

REQUIRED_EXTERNAL_RECEIPTS = {
    "clean_windows_install": (
        "windows_11",
        "outside_development_environment",
    ),
    "new_game_management_loop": (
        "new_game",
        "management_loop",
    ),
    "season_progression": (
        "season_progression",
    ),
    "save_reload": (
        "save_reload",
    ),
    "full_original_scope": (
        "full_original_scope",
        "all_original_playable_leagues",
        "all_original_playable_countries",
        "human_career_flow",
        "competition_progression",
        "original_management_gameplay_subsystems",
    ),
}


@dataclass(frozen=True)
class ExternalReceiptSpec:
    path: str
    sha256: str


@dataclass(frozen=True)
class ReleaseArchiveSpec:
    sha256: str
    size_bytes: int


@dataclass(frozen=True)
class ReleaseEvidence:
    release_version: str
    repository_commit: str
    limitations_path: str
    external_receipts: dict[str, ExternalReceiptSpec]
    archive: ReleaseArchiveSpec


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_hex_digest(value: object, *, label: str) -> str:
    text = str(value)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise ReleaseReadinessError(f"{label} must be a lowercase SHA-256")
    return text


def _require_commit(value: object) -> str:
    text = str(value)
    if not re.fullmatch(r"[0-9a-f]{40}", text):
        raise ReleaseReadinessError(
            "repository_commit must be one complete lowercase Git commit SHA"
        )
    return text


def parse_release_evidence(payload: Mapping[str, object]) -> ReleaseEvidence:
    """Parse the final evidence contract without accepting partial criteria."""
    if int(payload.get("schema_version", 0)) != 2:
        raise ReleaseReadinessError("release evidence schema_version must be 2")

    release_version = str(payload.get("release_version", "")).strip()
    if not release_version:
        raise ReleaseReadinessError("release_version is required")

    repository_commit = _require_commit(payload.get("repository_commit", ""))
    limitations_path = str(payload.get("limitations_path", "")).strip()
    if limitations_path != "research/RELEASE_LIMITATIONS.md":
        raise ReleaseReadinessError(
            "limitations_path must be research/RELEASE_LIMITATIONS.md"
        )

    raw_receipts = payload.get("external_receipts")
    if not isinstance(raw_receipts, Mapping):
        raise ReleaseReadinessError("external_receipts must be an object")
    if set(raw_receipts) != set(REQUIRED_EXTERNAL_RECEIPTS):
        missing = sorted(set(REQUIRED_EXTERNAL_RECEIPTS) - set(raw_receipts))
        extra = sorted(set(raw_receipts) - set(REQUIRED_EXTERNAL_RECEIPTS))
        raise ReleaseReadinessError(
            f"external receipt set mismatch: missing={missing}, extra={extra}"
        )

    receipts: dict[str, ExternalReceiptSpec] = {}
    for name in REQUIRED_EXTERNAL_RECEIPTS:
        raw = raw_receipts[name]
        if not isinstance(raw, Mapping):
            raise ReleaseReadinessError(f"{name} receipt descriptor must be an object")
        path = str(raw.get("path", "")).strip()
        if not path:
            raise ReleaseReadinessError(f"{name} receipt path is required")
        receipts[name] = ExternalReceiptSpec(
            path=path,
            sha256=_require_hex_digest(
                raw.get("sha256", ""),
                label=f"{name} receipt sha256",
            ),
        )

    raw_archive = payload.get("archive")
    if not isinstance(raw_archive, Mapping):
        raise ReleaseReadinessError("archive must be an object")
    size_bytes = int(raw_archive.get("size_bytes", 0))
    if size_bytes <= 0:
        raise ReleaseReadinessError("archive size_bytes must be positive")
    archive = ReleaseArchiveSpec(
        sha256=_require_hex_digest(
            raw_archive.get("sha256", ""),
            label="release archive sha256",
        ),
        size_bytes=size_bytes,
    )

    return ReleaseEvidence(
        release_version=release_version,
        repository_commit=repository_commit,
        limitations_path=limitations_path,
        external_receipts=receipts,
        archive=archive,
    )


def require_path_outside_repo(path: Path, repo_root: Path, *, label: str) -> Path:
    target = Path(path).resolve()
    root = Path(repo_root).resolve()
    if target == root or target.is_relative_to(root):
        raise ReleaseReadinessError(f"{label} must remain outside the Git repository")
    return target


def validate_full_scope_catalog(repo_root: Path) -> dict:
    """Require a complete, source-backed catalog of original playable scope."""
    root = Path(repo_root).resolve()
    path = (root / FULL_SCOPE_CATALOG_PATH).resolve()
    if not path.is_relative_to(root):
        raise ReleaseReadinessError("full-scope catalog escaped repository root")
    if not path.is_file():
        raise ReleaseReadinessError(
            f"full-scope catalog is missing: {FULL_SCOPE_CATALOG_PATH}"
        )
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseReadinessError(
            "full-scope catalog is not readable JSON"
        ) from exc
    if not isinstance(payload, dict):
        raise ReleaseReadinessError("full-scope catalog root must be an object")
    if int(payload.get("schema_version", 0)) != 1:
        raise ReleaseReadinessError("full-scope catalog schema_version must be 1")
    if payload.get("status") != "source_backed_complete":
        raise ReleaseReadinessError(
            "full-scope catalog is not source_backed_complete"
        )
    try:
        expected_count = int(payload.get("expected_entry_count", 0))
    except (TypeError, ValueError) as exc:
        raise ReleaseReadinessError(
            "full-scope catalog expected_entry_count is invalid"
        ) from exc
    if expected_count <= 0:
        raise ReleaseReadinessError(
            "full-scope catalog expected_entry_count must be positive"
        )
    source_evidence = payload.get("source_evidence")
    if (
        not isinstance(source_evidence, list)
        or not source_evidence
        or any(not isinstance(item, str) or not item.strip() for item in source_evidence)
    ):
        raise ReleaseReadinessError(
            "full-scope catalog requires non-empty source_evidence"
        )
    entries = payload.get("entries")
    if not isinstance(entries, list) or len(entries) != expected_count:
        actual = len(entries) if isinstance(entries, list) else "invalid"
        raise ReleaseReadinessError(
            "full-scope catalog entry count mismatch: "
            f"expected {expected_count}, got {actual}"
        )

    scope_ids: list[str] = []
    target_keys: list[tuple[str, str]] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, Mapping):
            raise ReleaseReadinessError(
                f"full-scope catalog entry {index} must be an object"
            )
        fields = {}
        for field in ("scope_id", "country", "competition", "source_reference"):
            value = raw.get(field)
            if not isinstance(value, str) or not value.strip():
                raise ReleaseReadinessError(
                    f"full-scope catalog entry {index} requires {field}"
                )
            fields[field] = value.strip()
        if raw.get("originally_playable") is not True:
            raise ReleaseReadinessError(
                f"full-scope catalog entry {index} must prove originally_playable=true"
            )
        scope_ids.append(fields["scope_id"])
        target_keys.append((fields["country"], fields["competition"]))

    if len(set(scope_ids)) != len(scope_ids):
        raise ReleaseReadinessError("full-scope catalog has duplicate scope_id values")
    if len(set(target_keys)) != len(target_keys):
        raise ReleaseReadinessError(
            "full-scope catalog has duplicate country/competition targets"
        )

    return {
        "path": FULL_SCOPE_CATALOG_PATH,
        "sha256": _sha256_file(path),
        "entry_count": expected_count,
        "scope_ids": tuple(scope_ids),
        "source_evidence": tuple(item.strip() for item in source_evidence),
    }


def validate_external_receipts(
    evidence: ReleaseEvidence,
    repo_root: Path,
) -> dict[str, dict]:
    """Hash and inspect every externally produced Windows release receipt."""
    checked: dict[str, dict] = {}
    root = Path(repo_root).resolve()
    full_scope_catalog = validate_full_scope_catalog(root)
    used_paths: dict[Path, str] = {}

    for name, required_flags in REQUIRED_EXTERNAL_RECEIPTS.items():
        spec = evidence.external_receipts[name]
        path = require_path_outside_repo(
            Path(spec.path),
            root,
            label=f"{name} receipt",
        )
        previous_name = used_paths.get(path)
        if previous_name is not None:
            raise ReleaseReadinessError(
                f"{name} receipt reuses the same evidence file as {previous_name}"
            )
        used_paths[path] = name
        if not path.is_file():
            raise ReleaseReadinessError(f"{name} receipt does not exist: {path}")
        actual_sha = _sha256_file(path)
        if actual_sha != spec.sha256:
            raise ReleaseReadinessError(
                f"{name} receipt checksum mismatch: expected {spec.sha256}, "
                f"got {actual_sha}"
            )
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ReleaseReadinessError(
                f"{name} receipt is not readable JSON"
            ) from exc
        if not isinstance(payload, dict) or payload.get("passed") is not True:
            raise ReleaseReadinessError(f"{name} receipt does not declare passed=true")
        if payload.get("repository_commit") != evidence.repository_commit:
            raise ReleaseReadinessError(
                f"{name} receipt was produced for a different repository commit"
            )
        if payload.get("release_version") != evidence.release_version:
            raise ReleaseReadinessError(
                f"{name} receipt was produced for a different release version"
            )
        if payload.get("release_archive_sha256") != evidence.archive.sha256:
            raise ReleaseReadinessError(
                f"{name} receipt was produced for a different release archive"
            )

        # Independently validate the host facts recorded by every external
        # producer. Do not trust a receipt merely because its producer is
        # currently guarded: old, copied or hand-edited evidence must fail too.
        if payload.get("windows_11") is not True:
            raise ReleaseReadinessError(
                f"{name} receipt does not prove Windows 11 execution"
            )
        try:
            windows_build = int(payload.get("windows_build", 0))
        except (TypeError, ValueError) as exc:
            raise ReleaseReadinessError(
                f"{name} receipt has an invalid Windows build"
            ) from exc
        if windows_build < 22000:
            raise ReleaseReadinessError(
                f"{name} receipt Windows build {windows_build} is older than Windows 11"
            )
        try:
            product_type = int(payload.get("windows_product_type", -1))
        except (TypeError, ValueError) as exc:
            raise ReleaseReadinessError(
                f"{name} receipt has an invalid Windows product type"
            ) from exc
        if product_type != 1:
            raise ReleaseReadinessError(
                f"{name} receipt does not prove a Windows client workstation"
            )

        for flag in required_flags:
            if payload.get(flag) is not True:
                raise ReleaseReadinessError(
                    f"{name} receipt is missing required true flag {flag}"
                )

        if name == "full_original_scope":
            if payload.get("scope_catalog_sha256") != full_scope_catalog["sha256"]:
                raise ReleaseReadinessError(
                    "full_original_scope receipt was produced for a different "
                    "original-scope catalog"
                )
            try:
                scope_entry_count = int(payload.get("scope_entry_count", 0))
                verified_scope_entry_count = int(
                    payload.get("verified_scope_entry_count", 0)
                )
            except (TypeError, ValueError) as exc:
                raise ReleaseReadinessError(
                    "full_original_scope receipt has invalid scope counts"
                ) from exc
            if scope_entry_count != full_scope_catalog["entry_count"]:
                raise ReleaseReadinessError(
                    "full_original_scope receipt scope_entry_count does not match "
                    "the source-backed catalog"
                )
            if verified_scope_entry_count != scope_entry_count:
                raise ReleaseReadinessError(
                    "full_original_scope receipt did not verify every scope entry"
                )
            verified_ids = payload.get("verified_scope_ids")
            if (
                not isinstance(verified_ids, list)
                or tuple(verified_ids) != full_scope_catalog["scope_ids"]
            ):
                raise ReleaseReadinessError(
                    "full_original_scope receipt verified_scope_ids do not exactly "
                    "match the source-backed catalog"
                )
            if payload.get("missing_scope_ids") != []:
                raise ReleaseReadinessError(
                    "full_original_scope receipt still has missing_scope_ids"
                )
            if payload.get("failed_scope_ids") != []:
                raise ReleaseReadinessError(
                    "full_original_scope receipt still has failed_scope_ids"
                )

        checked[name] = {
            "path": str(path),
            "sha256": actual_sha,
            "required_flags": list(required_flags),
            "windows_build": windows_build,
            "windows_product_type": product_type,
        }

    return checked


def validate_release_archive(
    archive_path: Path,
    spec: ReleaseArchiveSpec,
    repo_root: Path,
) -> dict:
    path = require_path_outside_repo(
        archive_path,
        repo_root,
        label="release archive",
    )
    if not path.is_file():
        raise ReleaseReadinessError(f"release archive does not exist: {path}")
    actual_size = path.stat().st_size
    if actual_size != spec.size_bytes:
        raise ReleaseReadinessError(
            f"release archive size mismatch: expected {spec.size_bytes}, "
            f"got {actual_size}"
        )
    actual_sha = _sha256_file(path)
    if actual_sha != spec.sha256:
        raise ReleaseReadinessError(
            f"release archive checksum mismatch: expected {spec.sha256}, "
            f"got {actual_sha}"
        )
    return {
        "path": str(path),
        "size_bytes": actual_size,
        "sha256": actual_sha,
    }


def validate_limitations_document(
    repo_root: Path,
    limitations_path: str,
) -> dict:
    path = (Path(repo_root) / limitations_path).resolve()
    root = Path(repo_root).resolve()
    if not path.is_relative_to(root):
        raise ReleaseReadinessError("limitations document escaped repository root")
    if not path.is_file():
        raise ReleaseReadinessError(f"limitations document is missing: {path}")
    text = path.read_text(encoding="utf-8").strip()
    if len(text) < 200:
        raise ReleaseReadinessError(
            "limitations document is too small to be a meaningful release disclosure"
        )
    if "pre-release" in text.lower():
        raise ReleaseReadinessError(
            "limitations document still identifies itself as pre-release"
        )
    return {
        "path": limitations_path,
        "sha256": sha256(text.encode("utf-8")).hexdigest(),
        "characters": len(text),
    }


def validate_roadmap_prerequisites(repo_root: Path) -> dict:
    """Require every Gate 1-16 completion criterion to be checked.

    Gate 17 itself is intentionally excluded because this final audit is one of
    its completion criteria. Missing gate sections, gates without checkbox
    criteria, and any unchecked prerequisite criterion all fail closed.
    """
    path = (Path(repo_root) / "ROADMAP.md").resolve()
    root = Path(repo_root).resolve()
    if not path.is_relative_to(root):
        raise ReleaseReadinessError("ROADMAP.md escaped repository root")
    if not path.is_file():
        raise ReleaseReadinessError("ROADMAP.md is missing")

    gate_heading = re.compile(r"^## Gate (\d+)\b")
    checkbox = re.compile(r"^- \[([ xX])\]")
    counts = {
        gate: {"checked": 0, "unchecked": 0}
        for gate in REQUIRED_PREREQUISITE_GATES
    }
    seen: set[int] = set()
    current_gate: int | None = None

    for line in path.read_text(encoding="utf-8").splitlines():
        heading = gate_heading.match(line)
        if heading is not None:
            current_gate = int(heading.group(1))
            if current_gate in counts:
                seen.add(current_gate)
            continue
        if current_gate not in counts:
            continue
        item = checkbox.match(line)
        if item is None:
            continue
        if item.group(1).lower() == "x":
            counts[current_gate]["checked"] += 1
        else:
            counts[current_gate]["unchecked"] += 1

    missing = [
        gate for gate in REQUIRED_PREREQUISITE_GATES
        if gate not in seen
    ]
    empty = [
        gate for gate in REQUIRED_PREREQUISITE_GATES
        if gate in seen
        and counts[gate]["checked"] + counts[gate]["unchecked"] == 0
    ]
    open_gates = [
        gate for gate in REQUIRED_PREREQUISITE_GATES
        if counts[gate]["unchecked"] > 0
    ]

    if missing:
        raise ReleaseReadinessError(
            f"ROADMAP.md is missing prerequisite gate sections: {missing}"
        )
    if empty:
        raise ReleaseReadinessError(
            f"prerequisite gates have no completion criteria: {empty}"
        )
    if open_gates:
        details = ", ".join(
            f"Gate {gate} ({counts[gate]['unchecked']} unchecked)"
            for gate in open_gates
        )
        raise ReleaseReadinessError(
            "Gate 17 release audit requires Gates 1-16 to be complete: "
            + details
        )

    return {
        "path": "ROADMAP.md",
        "required_gates": list(REQUIRED_PREREQUISITE_GATES),
        "all_prerequisites_complete": True,
        "criteria": {
            str(gate): dict(counts[gate])
            for gate in REQUIRED_PREREQUISITE_GATES
        },
    }


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip()


def validate_clean_repository(repo_root: Path, expected_commit: str) -> dict:
    try:
        head = _git(repo_root, "rev-parse", "HEAD")
        status = _git(repo_root, "status", "--porcelain")
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ReleaseReadinessError("unable to inspect Git release state") from exc
    if head != expected_commit:
        raise ReleaseReadinessError(
            f"release evidence commit {expected_commit} does not match HEAD {head}"
        )
    if status:
        raise ReleaseReadinessError(
            "final release audit requires a clean Git working tree"
        )
    return {"head": head, "working_tree_clean": True}


def require_windows_11() -> dict:
    """Require the Windows 11 build family without asserting host provenance."""
    if platform.system() != "Windows":
        raise ReleaseReadinessError(
            "final Gate-17 release audit must run on Windows 11"
        )
    try:
        version = sys.getwindowsversion()
        build = int(version.build)
    except Exception as exc:
        raise ReleaseReadinessError(
            "unable to read Windows build number"
        ) from exc
    if build < 22000:
        raise ReleaseReadinessError(
            f"Windows build {build} is older than Windows 11"
        )
    return {
        "platform": platform.platform(),
        "windows_build": build,
    }


def require_external_windows_11_workstation() -> dict:
    """Require real Windows 11 client evidence, never hosted/server CI.

    Gate-17 external receipts and the final audit must be produced on a client
    Windows workstation. A Windows Server host can share a modern build number,
    so build >= 22000 alone is insufficient. GitHub Actions is rejected
    explicitly even if a future hosted runner reports a client product type.
    """
    windows = require_windows_11()
    if str(os.environ.get("GITHUB_ACTIONS", "")).casefold() == "true":
        raise ReleaseReadinessError(
            "Gate-17 external Windows evidence cannot be produced under GitHub Actions"
        )
    try:
        product_type = int(sys.getwindowsversion().product_type)
    except Exception as exc:
        raise ReleaseReadinessError(
            "unable to verify Windows workstation product type"
        ) from exc
    if product_type != 1:
        raise ReleaseReadinessError(
            "Gate-17 external Windows evidence requires a Windows client "
            f"workstation, not product_type {product_type}"
        )
    return {
        **windows,
        "windows_11": True,
        "windows_product_type": product_type,
    }


def run_repository_command(
    command: list[str],
    *,
    cwd: Path,
    label: str,
) -> dict:
    result = subprocess.run(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if result.returncode != 0:
        tail = result.stdout[-4000:]
        raise ReleaseReadinessError(
            f"{label} failed with exit code {result.returncode}:\\n{tail}"
        )
    return {
        "command": command,
        "returncode": result.returncode,
        "output_tail": result.stdout[-2000:],
    }


def run_final_release_audit(
    *,
    repo_root: Path,
    evidence_path: Path,
    release_archive: Path,
    canonical_game_dir: Path,
) -> dict:
    """Execute all locally reproducible Gate-17 checks on one Windows 11 commit."""
    root = Path(repo_root).resolve()
    evidence_file = require_path_outside_repo(
        evidence_path,
        root,
        label="release evidence",
    )
    try:
        payload = json.loads(evidence_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReleaseReadinessError("release evidence is not readable JSON") from exc
    if not isinstance(payload, dict):
        raise ReleaseReadinessError("release evidence root must be an object")
    evidence = parse_release_evidence(payload)

    windows = require_external_windows_11_workstation()
    repository = validate_clean_repository(root, evidence.repository_commit)
    roadmap_prerequisites = validate_roadmap_prerequisites(root)
    receipts = validate_external_receipts(evidence, root)
    archive = validate_release_archive(release_archive, evidence.archive, root)
    limitations = validate_limitations_document(root, evidence.limitations_path)

    asset_policy = run_repository_command(
        [sys.executable, "tools/check_repository_assets.py"],
        cwd=root,
        label="repository asset policy",
    )
    canonical = run_repository_command(
        [
            sys.executable,
            "reconstruction/verify.py",
            str(Path(canonical_game_dir).resolve()),
        ],
        cwd=root,
        label="canonical FM2001 source verification",
    )
    full_suite = run_repository_command(
        [sys.executable, "-m", "unittest", "discover", "-v"],
        cwd=root / "reconstruction",
        label="full reconstruction test suite",
    )

    return {
        "schema_version": 1,
        "passed": True,
        "release_version": evidence.release_version,
        "repository_commit": evidence.repository_commit,
        "windows": windows,
        "repository": repository,
        "roadmap_prerequisites": roadmap_prerequisites,
        "external_receipts": receipts,
        "release_archive": archive,
        "limitations": limitations,
        "asset_policy": asset_policy,
        "canonical_source_verification": canonical,
        "full_automated_suite": full_suite,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--canonical-game-dir", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    output = require_path_outside_repo(
        args.output_receipt,
        args.repo_root,
        label="final release receipt",
    )
    if output.exists():
        raise ReleaseReadinessError(
            "final release receipt path already exists; do not overwrite evidence"
        )
    receipt = run_final_release_audit(
        repo_root=args.repo_root,
        evidence_path=args.evidence,
        release_archive=args.release_archive,
        canonical_game_dir=args.canonical_game_dir,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\\n",
        encoding="utf-8",
    )
    print(f"Gate 17 release readiness audit passed: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
