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
