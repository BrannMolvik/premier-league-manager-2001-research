"""Materialize and audit the exact Gate-17 static-contributor source bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.parse
import urllib.request


class SourceBundleError(RuntimeError):
    """Raised when source-bundle scope or downloaded material fails closed."""


CONTRACT_PATH = Path("third_party/ffmpeg-lgpl-candidate/TOOLCHAIN-CONTRACT.json")
ALLOWED_HOST = "mirror.msys2.org"


def _contract(repo_root: Path) -> dict:
    path = repo_root / CONTRACT_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def audit_source_bundle_contract(repo_root: str | Path) -> dict:
    repo_root = Path(repo_root)
    contract = _contract(repo_root)
    scope = contract.get("static_contributor_source_material")
    if not isinstance(scope, dict):
        raise SourceBundleError("static contributor source-material scope is missing")

    packages = scope.get("contributing_packages")
    families = scope.get("contributing_source_families")
    if not isinstance(packages, list) or not packages:
        raise SourceBundleError("contributing_packages must be a non-empty list")
    if not isinstance(families, list) or not families:
        raise SourceBundleError("contributing_source_families must be a non-empty list")
    if len(set(packages)) != len(packages):
        raise SourceBundleError("contributing_packages contains duplicates")
    if len(set(families)) != len(families):
        raise SourceBundleError("contributing_source_families contains duplicates")
    if scope.get("static_contributor_attribution_complete") is not True:
        raise SourceBundleError("static contributor attribution is not complete")
    if scope.get("source_package_bundle_assembled") is not True:
        raise SourceBundleError("source_package_bundle_assembled must be true")
    if scope.get("source_package_hashes_pinned") is not True:
        raise SourceBundleError("source_package_hashes_pinned must be true")
    for field in (
        "license_notice_material_complete",
        "source_material_complete",
        "legal_compliance_claimed",
    ):
        if scope.get(field) is not False:
            raise SourceBundleError(f"{field} must remain false")

    critical = contract.get("critical_package_source_material", {})
    package_to_family = critical.get("package_to_source_family", {})
    source_families = critical.get("source_families", {})
    required_versions = contract.get("required_package_versions", {})

    resolved = []
    mapped_families = []
    for package in packages:
        family_name = package_to_family.get(package)
        if not family_name:
            raise SourceBundleError(f"{package} has no source-family mapping")
        mapped_families.append(family_name)
        family = source_families.get(family_name)
        if not isinstance(family, dict):
            raise SourceBundleError(f"missing source-family row: {family_name}")
        version = required_versions.get(package)
        if not version:
            raise SourceBundleError(f"{package} has no required package version")
        if family.get("binary_version") != version:
            raise SourceBundleError(
                f"{package} version does not match source family {family_name}"
            )
        if family.get("source_tarball_metadata_verified") is not True:
            raise SourceBundleError(f"{family_name} source tarball is not verified")
        url = family.get("source_only_tarball")
        if not isinstance(url, str):
            raise SourceBundleError(f"{family_name} source tarball URL is missing")
        parsed = urllib.parse.urlparse(url)
        if (
            parsed.scheme != "https"
            or parsed.hostname != ALLOWED_HOST
            or not parsed.path.endswith(".src.tar.zst")
        ):
            raise SourceBundleError(
                f"{family_name} source tarball URL is outside the verified MSYS2 source mirror"
            )
        filename = Path(parsed.path).name
        if not filename:
            raise SourceBundleError(f"{family_name} source tarball filename is empty")
        licenses = family.get("license_metadata")
        if not isinstance(licenses, list) or not licenses:
            raise SourceBundleError(f"{family_name} license metadata is empty")
        expected_sha256 = family.get("source_tarball_sha256")
        expected_size = family.get("source_tarball_size_bytes")
        if (
            not isinstance(expected_sha256, str)
            or len(expected_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in expected_sha256)
        ):
            raise SourceBundleError(f"{family_name} pinned source SHA-256 is invalid")
        if not isinstance(expected_size, int) or expected_size <= 0:
            raise SourceBundleError(f"{family_name} pinned source size is invalid")
        resolved.append(
            {
                "package": package,
                "version": version,
                "source_family": family_name,
                "source_url": url,
                "filename": filename,
                "license_metadata": list(licenses),
                "expected_sha256": expected_sha256,
                "expected_size_bytes": expected_size,
            }
        )

    if mapped_families != families:
        raise SourceBundleError(
            "contributing_source_families does not exactly match package mappings"
        )

    return {
        "schema_version": 1,
        "passed": True,
        "bundle_scope_count": len(resolved),
        "entries": resolved,
        "static_contributor_attribution_complete": True,
        "source_package_bundle_assembled": True,
        "source_package_hashes_pinned": True,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def _download(url: str, destination: Path) -> tuple[str, int]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "FM2001-Gate17-source-bundle/1"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        status = getattr(response, "status", 200)
        if status != 200:
            raise SourceBundleError(f"source download returned HTTP {status}: {url}")
        with destination.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
                digest.update(chunk)
                size += len(chunk)
    if size <= 0:
        raise SourceBundleError(f"source download was empty: {url}")
    return digest.hexdigest(), size


def materialize_source_bundle(
    *,
    repo_root: str | Path,
    output_dir: str | Path,
) -> dict:
    preflight = audit_source_bundle_contract(repo_root)
    output_dir = Path(output_dir)
    packages_dir = output_dir / "source-packages"
    manifest_entries = []
    seen_filenames: set[str] = set()

    for entry in preflight["entries"]:
        filename = entry["filename"]
        if filename in seen_filenames:
            raise SourceBundleError(f"duplicate source package filename: {filename}")
        seen_filenames.add(filename)
        destination = packages_dir / filename
        sha256, size = _download(entry["source_url"], destination)
        if sha256 != entry["expected_sha256"]:
            raise SourceBundleError(
                f"{entry['source_family']} source SHA-256 drifted: {sha256}"
            )
        if size != entry["expected_size_bytes"]:
            raise SourceBundleError(
                f"{entry['source_family']} source size drifted: {size}"
            )
        manifest_entries.append(
            {
                **entry,
                "sha256": sha256,
                "size_bytes": size,
            }
        )

    manifest = {
        "schema_version": 1,
        "passed": True,
        "bundle_scope": "exact proven static-contributor MSYS2 source packages",
        "source_package_count": len(manifest_entries),
        "source_packages": manifest_entries,
        "static_contributor_attribution_complete": True,
        "source_package_bundle_assembled": True,
        "source_package_hashes_pinned": True,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "source-package-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    if args.preflight_only:
        result = audit_source_bundle_contract(args.repo_root)
    else:
        result = materialize_source_bundle(
            repo_root=args.repo_root,
            output_dir=args.output_dir,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
