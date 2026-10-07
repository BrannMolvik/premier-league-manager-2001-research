"""Fail-closed ownership audit for external inputs resolved by the Gate-17 link."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re


class LinkInputOwnershipError(RuntimeError):
    """Raised when linker-input ownership evidence is incomplete or inconsistent."""


TARGETS = ("ffmpeg_g.exe", "ffprobe_g.exe")
_EXTERNAL_INPUT_RE = re.compile(r"^[A-Za-z]:/.*\.(?:a|o)$")


def _external_inputs(trace_text: str) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for raw_line in trace_text.splitlines():
        line = raw_line.strip().replace("\\", "/")
        if not _EXTERNAL_INPUT_RE.fullmatch(line):
            continue
        if line not in seen:
            seen.add(line)
            ordered.append(line)
    if not ordered:
        raise LinkInputOwnershipError("trace contained no absolute external .a/.o inputs")
    return ordered


def _read_lock(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            package, version = line.split(" ", 1)
        except ValueError as exc:
            raise LinkInputOwnershipError(
                f"invalid package-lock row {line_number}: {raw!r}"
            ) from exc
        if package in rows:
            raise LinkInputOwnershipError(f"duplicate package-lock row: {package}")
        rows[package] = version
    if not rows:
        raise LinkInputOwnershipError("package lock is empty")
    return rows


def _read_owner_rows(path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) != 5:
            raise LinkInputOwnershipError(
                f"owner row {line_number} must have five tab-separated fields"
            )
        target, trace_path, normalized_path, package, version = parts
        if target not in TARGETS:
            raise LinkInputOwnershipError(
                f"owner row {line_number} has unknown target {target!r}"
            )
        trace_path = trace_path.replace("\\", "/")
        if not _EXTERNAL_INPUT_RE.fullmatch(trace_path):
            raise LinkInputOwnershipError(
                f"owner row {line_number} is not an absolute external .a/.o input"
            )
        if not normalized_path.startswith("/"):
            raise LinkInputOwnershipError(
                f"owner row {line_number} normalized path is not absolute"
            )
        if not package or not version:
            raise LinkInputOwnershipError(
                f"owner row {line_number} has empty package/version"
            )
        key = (target, trace_path)
        if key in rows:
            raise LinkInputOwnershipError(
                f"duplicate ownership row for {target}: {trace_path}"
            )
        rows[key] = {
            "normalized_path": normalized_path,
            "package": package,
            "version": version,
        }
    if not rows:
        raise LinkInputOwnershipError("ownership evidence is empty")
    return rows


def audit_link_input_ownership(
    *,
    ffmpeg_trace_log: Path,
    ffprobe_trace_log: Path,
    owner_rows: Path,
    package_lock: Path,
    toolchain_contract: Path,
) -> dict:
    expected = {
        "ffmpeg_g.exe": _external_inputs(
            ffmpeg_trace_log.read_text(encoding="utf-8", errors="replace")
        ),
        "ffprobe_g.exe": _external_inputs(
            ffprobe_trace_log.read_text(encoding="utf-8", errors="replace")
        ),
    }
    owners = _read_owner_rows(owner_rows)
    lock = _read_lock(package_lock)
    contract = json.loads(toolchain_contract.read_text(encoding="utf-8"))
    critical = contract.get("critical_package_source_material", {})
    package_to_source = critical.get("package_to_source_family", {})
    source_families = critical.get("source_families", {})
    required_versions = contract.get("required_package_versions", {})

    expected_keys = {
        (target, trace_path)
        for target, paths in expected.items()
        for trace_path in paths
    }
    actual_keys = set(owners)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing or extra:
        raise LinkInputOwnershipError(
            f"ownership coverage mismatch: missing={missing!r} extra={extra!r}"
        )

    package_rows: dict[str, dict[str, str]] = {}
    target_receipts: dict[str, dict] = {}
    for target in TARGETS:
        target_inputs: list[dict[str, str]] = []
        for trace_path in expected[target]:
            row = owners[(target, trace_path)]
            package = row["package"]
            version = row["version"]

            locked_version = lock.get(package)
            if locked_version is None:
                raise LinkInputOwnershipError(
                    f"{target} input {trace_path} owner {package} is absent from package lock"
                )
            if locked_version != version:
                raise LinkInputOwnershipError(
                    f"{package} owner version {version} != locked {locked_version}"
                )

            required_version = required_versions.get(package)
            if required_version is None:
                raise LinkInputOwnershipError(
                    f"{package} is not in required_package_versions"
                )
            if required_version != version:
                raise LinkInputOwnershipError(
                    f"{package} owner version {version} != contract {required_version}"
                )

            source_family = package_to_source.get(package)
            if not source_family:
                raise LinkInputOwnershipError(
                    f"{package} has no critical source-family mapping"
                )
            family = source_families.get(source_family)
            if not isinstance(family, dict):
                raise LinkInputOwnershipError(
                    f"{package} maps to missing source family {source_family}"
                )
            family_version = family.get("binary_version")
            if family_version != version:
                raise LinkInputOwnershipError(
                    f"{package} owner version {version} != source-family version "
                    f"{family_version!r}"
                )
            if family.get("source_tarball_metadata_verified") is not True:
                raise LinkInputOwnershipError(
                    f"{source_family} source tarball metadata is not verified"
                )

            package_rows[package] = {
                "version": version,
                "source_family": source_family,
            }
            target_inputs.append(
                {
                    "trace_path": trace_path,
                    "normalized_path": row["normalized_path"],
                    "package": package,
                    "version": version,
                    "source_family": source_family,
                }
            )
        target_receipts[target] = {
            "external_input_count": len(target_inputs),
            "inputs": target_inputs,
        }

    packages = [
        {"package": package, **package_rows[package]}
        for package in sorted(package_rows)
    ]
    return {
        "schema_version": 1,
        "passed": True,
        "evidence_scope": "direct package ownership of absolute external .a/.o final-link inputs",
        "targets": target_receipts,
        "unique_owner_package_count": len(packages),
        "owner_packages": packages,
        "package_lock_ownership_validated": True,
        "critical_source_family_mapping_validated": True,
        "archive_member_contribution_proof_complete": False,
        "static_contributor_attribution_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg-trace-log", type=Path, required=True)
    parser.add_argument("--ffprobe-trace-log", type=Path, required=True)
    parser.add_argument("--owner-rows", type=Path, required=True)
    parser.add_argument("--package-lock", type=Path, required=True)
    parser.add_argument("--toolchain-contract", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()

    receipt = audit_link_input_ownership(
        ffmpeg_trace_log=args.ffmpeg_trace_log,
        ffprobe_trace_log=args.ffprobe_trace_log,
        owner_rows=args.owner_rows,
        package_lock=args.package_lock,
        toolchain_contract=args.toolchain_contract,
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
