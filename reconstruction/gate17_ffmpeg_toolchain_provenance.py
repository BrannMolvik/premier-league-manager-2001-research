"""Audit the UCRT64 toolchain provenance for the minimal FFmpeg build."""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path


class MinimalFfmpegToolchainError(RuntimeError):
    pass


CONTRACT_PATH = Path("third_party/ffmpeg-lgpl-candidate/TOOLCHAIN-CONTRACT.json")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_contract(repo_root: str | Path) -> tuple[dict, Path]:
    path = Path(repo_root).resolve() / CONTRACT_PATH
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise MinimalFfmpegToolchainError("toolchain contract is unreadable") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise MinimalFfmpegToolchainError("toolchain contract schema is invalid")
    return payload, path


def parse_package_list(text: str) -> dict[str, str]:
    packages: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = line.split(None, 1)
        if len(parts) != 2 or not all(parts):
            raise MinimalFfmpegToolchainError(
                f"invalid pacman package-list row: {raw!r}"
            )
        name, version = parts
        if name in packages:
            raise MinimalFfmpegToolchainError(f"duplicate package row: {name}")
        packages[name] = version
    if not packages:
        raise MinimalFfmpegToolchainError("pacman package list is empty")
    return packages


def audit_critical_source_material(contract: dict) -> dict:
    """Validate the bounded source-material plan without promoting completeness."""
    required = contract.get("required_package_versions")
    if not isinstance(required, dict) or not required:
        raise MinimalFfmpegToolchainError("required toolchain package map is missing")

    plan = contract.get("critical_package_source_material")
    if not isinstance(plan, dict):
        raise MinimalFfmpegToolchainError("critical source-material plan is missing")
    for flag in ("complete_package_lock", "source_material_complete", "legal_compliance_claimed"):
        if plan.get(flag) is not False:
            raise MinimalFfmpegToolchainError(
                f"critical source-material plan must keep {flag}=false"
            )

    mapping = plan.get("package_to_source_family")
    families = plan.get("source_families")
    if not isinstance(mapping, dict) or not isinstance(families, dict) or not families:
        raise MinimalFfmpegToolchainError("critical source-material family map is invalid")
    if set(mapping) != set(required):
        missing = sorted(set(required) - set(mapping))
        extra = sorted(set(mapping) - set(required))
        raise MinimalFfmpegToolchainError(
            "critical source-material package coverage drifted: "
            + json.dumps({"missing": missing, "extra": extra}, sort_keys=True)
        )

    verified = 0
    for package, family_name in mapping.items():
        family = families.get(family_name)
        if not isinstance(family, dict):
            raise MinimalFfmpegToolchainError(
                f"source-material family is missing for {package}: {family_name}"
            )
        expected_version = required[package]
        if family.get("binary_version") != expected_version:
            raise MinimalFfmpegToolchainError(
                f"source-material family version drifted for {package}: "
                f"expected {expected_version}, got {family.get('binary_version')}"
            )

    for family_name, family in families.items():
        if not isinstance(family, dict):
            raise MinimalFfmpegToolchainError(
                f"source-material family row is invalid: {family_name}"
            )
        metadata_url = family.get("metadata_url")
        if (
            not isinstance(metadata_url, str)
            or not metadata_url.startswith("https://packages.msys2.org/")
        ):
            raise MinimalFfmpegToolchainError(
                f"source-material metadata URL is invalid: {family_name}"
            )
        licenses = family.get("license_metadata")
        if (
            not isinstance(licenses, list)
            or not licenses
            or any(not isinstance(value, str) or not value for value in licenses)
        ):
            raise MinimalFfmpegToolchainError(
                f"source-material license metadata is invalid: {family_name}"
            )
        verified_flag = family.get("source_tarball_metadata_verified")
        if type(verified_flag) is not bool:
            raise MinimalFfmpegToolchainError(
                f"source-material verification flag is invalid: {family_name}"
            )
        tarball = family.get("source_only_tarball")
        if verified_flag:
            if (
                not isinstance(tarball, str)
                or not tarball.startswith("https://mirror.msys2.org/")
                or family.get("binary_version") not in tarball
                or not tarball.endswith(".src.tar.zst")
            ):
                raise MinimalFfmpegToolchainError(
                    f"verified source-only tarball identity is invalid: {family_name}"
                )
            verified += 1
        else:
            if tarball is not None:
                raise MinimalFfmpegToolchainError(
                    f"unverified source family must not publish a tarball URL: {family_name}"
                )
            if not isinstance(family.get("note"), str) or not family["note"].strip():
                raise MinimalFfmpegToolchainError(
                    f"unverified source family needs an explicit blocker note: {family_name}"
                )

    declared_verified = plan.get("verified_source_family_count")
    declared_total = plan.get("total_source_family_count")
    if declared_verified != verified or declared_total != len(families):
        raise MinimalFfmpegToolchainError(
            "source-material family counts drifted"
        )
    unresolved = plan.get("unresolved")
    if (
        not isinstance(unresolved, list)
        or not unresolved
        or any(not isinstance(value, str) or not value for value in unresolved)
    ):
        raise MinimalFfmpegToolchainError(
            "critical source-material plan must retain explicit unresolved work"
        )

    return {
        "critical_package_count": len(required),
        "source_family_count": len(families),
        "verified_source_family_count": verified,
        "unverified_source_families": sorted(
            name
            for name, family in families.items()
            if family.get("source_tarball_metadata_verified") is False
        ),
        "complete_package_lock": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def audit_toolchain(
    *,
    repo_root: str | Path,
    package_list: str | Path,
) -> dict:
    contract, contract_path = load_contract(repo_root)
    if contract.get("source_material_complete") is not False:
        raise MinimalFfmpegToolchainError(
            "toolchain provenance checkpoint must remain source-material incomplete"
        )
    if contract.get("legal_compliance_claimed") is not False:
        raise MinimalFfmpegToolchainError(
            "toolchain provenance checkpoint cannot claim legal compliance"
        )
    if contract.get("complete_package_lock") is not False:
        raise MinimalFfmpegToolchainError(
            "critical-package audit must not masquerade as a complete package lock"
        )

    package_path = Path(package_list).resolve()
    if not package_path.is_file() or package_path.stat().st_size <= 0:
        raise MinimalFfmpegToolchainError("pacman package list is missing or empty")
    packages = parse_package_list(package_path.read_text(encoding="utf-8"))
    required = contract.get("required_package_versions")
    if not isinstance(required, dict) or not required:
        raise MinimalFfmpegToolchainError("required toolchain package map is missing")

    mismatches = []
    for name, expected in required.items():
        actual = packages.get(name)
        if actual != expected:
            mismatches.append({"package": name, "expected": expected, "actual": actual})
    if mismatches:
        raise MinimalFfmpegToolchainError(
            "UCRT64 toolchain package versions drifted: "
            + json.dumps(mismatches, sort_keys=True)
        )

    source_material = audit_critical_source_material(contract)

    actions = contract.get("pinned_actions")
    if not isinstance(actions, dict) or any(
        not isinstance(value, str) or len(value) != 40
        for value in actions.values()
    ):
        raise MinimalFfmpegToolchainError("pinned action commit map is invalid")

    return {
        "schema_version": 1,
        "audit_kind": "gate17_minimal_ffmpeg_toolchain_provenance",
        "passed": True,
        "toolchain_contract_sha256": _sha256_file(contract_path),
        "package_list_sha256": _sha256_file(package_path),
        "required_package_versions": dict(sorted(required.items())),
        "pinned_actions": dict(sorted(actions.items())),
        "critical_source_material": source_material,
        "complete_package_lock": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--package-list", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()
    result = audit_toolchain(repo_root=args.repo_root, package_list=args.package_list)
    args.output_receipt.parent.mkdir(parents=True, exist_ok=True)
    args.output_receipt.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
