"""Extract and audit license/declaration evidence from pinned Gate-17 source packages."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

from gate17_source_material_bundle import CONTRACT_PATH, SourceBundleError, audit_source_bundle_contract


class LicenseMaterialError(RuntimeError):
    """Raised when exact license/declaration material cannot be reproduced."""


EXPECTED_FAMILIES = (
    "mingw-w64-gcc",
    "mingw-w64-crt",
    "mingw-w64-winpthreads",
    "mingw-w64-windows-default-manifest",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_bytes(args: list[str]) -> bytes:
    proc = subprocess.run(args, check=False, capture_output=True)
    if proc.returncode != 0:
        raise LicenseMaterialError(
            f"command failed ({proc.returncode}): {args!r}: "
            f"{proc.stderr.decode('utf-8', errors='replace')}"
        )
    return proc.stdout


def _verify_bytes(data: bytes, spec: dict, label: str) -> None:
    digest = _sha256(data)
    if digest != spec.get("sha256"):
        raise LicenseMaterialError(
            f"{label} SHA-256 drifted: {digest} != {spec.get('sha256')}"
        )
    if len(data) != spec.get("size_bytes"):
        raise LicenseMaterialError(
            f"{label} size drifted: {len(data)} != {spec.get('size_bytes')}"
        )


def _load_contract(repo_root: Path) -> dict:
    return json.loads((repo_root / CONTRACT_PATH).read_text(encoding="utf-8"))


def audit_license_material_contract(repo_root: str | Path) -> dict:
    repo_root = Path(repo_root)
    source_scope = audit_source_bundle_contract(repo_root)
    if not source_scope["source_package_bundle_assembled"]:
        raise LicenseMaterialError("source-package bundle is not assembled")
    if not source_scope["source_package_hashes_pinned"]:
        raise LicenseMaterialError("source-package hashes are not pinned")

    contract = _load_contract(repo_root)
    scope = contract["static_contributor_source_material"]
    license_scope = scope.get("license_material")
    if not isinstance(license_scope, dict):
        raise LicenseMaterialError("license_material contract is missing")
    for field in ("license_material_assembled", "license_material_hashes_pinned"):
        if license_scope.get(field) is not True:
            raise LicenseMaterialError(f"{field} must be true")
    for field in (
        "license_notice_material_complete",
        "source_material_complete",
        "legal_compliance_claimed",
    ):
        if license_scope.get(field) is not False:
            raise LicenseMaterialError(f"{field} must remain false")

    rows = []
    for family in EXPECTED_FAMILIES:
        key = family.replace("-", "_").replace("mingw_w64_", "mingw_w64_")
        # Contract keys are explicit to keep source-family names distinct from Python names.
        key_map = {
            "mingw-w64-gcc": "mingw_w64_gcc",
            "mingw-w64-crt": "mingw_w64_crt",
            "mingw-w64-winpthreads": "mingw_w64_winpthreads",
            "mingw-w64-windows-default-manifest": "mingw_w64_windows_default_manifest",
        }
        row = license_scope.get(key_map[family])
        if not isinstance(row, dict) or row.get("source_family") != family:
            raise LicenseMaterialError(f"missing license-material row for {family}")
        files = row.get("files")
        if not isinstance(files, list) or not files:
            raise LicenseMaterialError(f"{family} license-material files are missing")
        for spec in files:
            if not isinstance(spec, dict):
                raise LicenseMaterialError(f"{family} has malformed file spec")
            sha = spec.get("sha256")
            size = spec.get("size_bytes")
            if (
                not isinstance(sha, str)
                or len(sha) != 64
                or any(ch not in "0123456789abcdef" for ch in sha)
            ):
                raise LicenseMaterialError(f"{family} has invalid pinned file SHA-256")
            if not isinstance(size, int) or size <= 0:
                raise LicenseMaterialError(f"{family} has invalid pinned file size")
            if not spec.get("source_path") or not spec.get("output_name"):
                raise LicenseMaterialError(f"{family} file path mapping is incomplete")
        rows.append(row)

    return {
        "schema_version": 1,
        "passed": True,
        "source_family_count": len(rows),
        "file_count": sum(len(row["files"]) for row in rows),
        "license_material_assembled": True,
        "license_material_hashes_pinned": True,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def _extract_package(source_archive: Path, work_root: Path) -> Path:
    subprocess.run(
        ["tar", "--zstd", "-xf", str(source_archive), "-C", str(work_root)],
        check=True,
    )
    stem = source_archive.name.removesuffix(".src.tar.zst")
    # MSYS2 source package top directory omits the version suffix.
    candidates = [p for p in work_root.iterdir() if p.is_dir()]
    if len(candidates) != 1:
        raise LicenseMaterialError(
            f"expected one extracted package root for {source_archive.name}, got {candidates}"
        )
    return candidates[0]


def _write_verified(output_root: Path, spec: dict, data: bytes, label: str) -> dict:
    _verify_bytes(data, spec, label)
    destination = output_root / spec["output_name"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return {
        "source_path": spec["source_path"],
        "output_name": spec["output_name"],
        "sha256": spec["sha256"],
        "size_bytes": spec["size_bytes"],
    }


def extract_license_material(
    *,
    repo_root: str | Path,
    source_packages_dir: str | Path,
    output_dir: str | Path,
) -> dict:
    repo_root = Path(repo_root)
    source_packages_dir = Path(source_packages_dir)
    output_dir = Path(output_dir)
    audit_license_material_contract(repo_root)
    contract = _load_contract(repo_root)
    scope = contract["static_contributor_source_material"]["license_material"]
    source_rows = {
        item["source_family"]: item
        for item in audit_source_bundle_contract(repo_root)["entries"]
    }

    output_rows = []
    with tempfile.TemporaryDirectory(prefix="fm2001-gate17-license-") as temp:
        temp_root = Path(temp)
        extracted = {}
        for family in EXPECTED_FAMILIES:
            source_row = source_rows[family]
            archive = source_packages_dir / source_row["filename"]
            if not archive.is_file():
                raise LicenseMaterialError(f"missing pinned source package: {archive}")
            family_work = temp_root / family
            family_work.mkdir()
            extracted[family] = _extract_package(archive, family_work)

        gcc = scope["mingw_w64_gcc"]
        gcc_root = extracted["mingw-w64-gcc"]
        gcc_pkgbuild = (gcc_root / "PKGBUILD").read_text(encoding="utf-8")
        for required in ("package_gcc()", "_install_RLE", "COPYING3", "COPYING.RUNTIME"):
            if required not in gcc_pkgbuild:
                raise LicenseMaterialError(f"GCC PKGBUILD lost recipe evidence: {required}")
        nested = gcc_root / gcc["nested_source_archive"]
        for spec in gcc["files"]:
            data = _run_bytes(["tar", "-xOf", str(nested), spec["source_path"]])
            output_rows.append(
                {"source_family": "mingw-w64-gcc", **_write_verified(output_dir, spec, data, "GCC "+spec["source_path"])}
            )

        for family, key in (
            ("mingw-w64-crt", "mingw_w64_crt"),
            ("mingw-w64-winpthreads", "mingw_w64_winpthreads"),
        ):
            row = scope[key]
            pkg_root = extracted[family]
            repo = pkg_root / "mingw-w64"
            head = _run_bytes(["git", f"--git-dir={repo}", "rev-parse", "HEAD"]).decode().strip()
            if head != row["source_git_head"]:
                raise LicenseMaterialError(
                    f"{family} source Git HEAD drifted: {head} != {row['source_git_head']}"
                )
            pkgbuild = (pkg_root / "PKGBUILD").read_text(encoding="utf-8")
            if family == "mingw-w64-crt":
                required = ("COPYING.MinGW-w64.txt", "COPYING.MinGW-w64-runtime.txt")
            else:
                required = ("_install_licenses", "mingw-w64-libraries/winpthreads/COPYING")
            for token in required:
                if token not in pkgbuild:
                    raise LicenseMaterialError(f"{family} PKGBUILD lost recipe evidence: {token}")
            for spec in row["files"]:
                data = _run_bytes(["git", f"--git-dir={repo}", "show", "HEAD:"+spec["source_path"]])
                output_rows.append(
                    {"source_family": family, **_write_verified(output_dir, spec, data, family+" "+spec["source_path"])}
                )

        manifest = scope["mingw_w64_windows_default_manifest"]
        manifest_root = extracted["mingw-w64-windows-default-manifest"]
        pkgbuild = (manifest_root / "PKGBUILD").read_text(encoding="utf-8")
        srcinfo = (manifest_root / ".SRCINFO").read_text(encoding="utf-8")
        if "license=('custom:Public Domain')" not in pkgbuild:
            raise LicenseMaterialError("default-manifest PKGBUILD lost Public Domain declaration")
        if "license = custom:Public Domain" not in srcinfo:
            raise LicenseMaterialError("default-manifest .SRCINFO lost Public Domain declaration")
        for spec in manifest["files"]:
            data = (manifest_root / spec["source_path"]).read_bytes()
            output_rows.append(
                {"source_family": "mingw-w64-windows-default-manifest", **_write_verified(output_dir, spec, data, "manifest "+spec["source_path"])}
            )

    receipt = {
        "schema_version": 1,
        "passed": True,
        "evidence_scope": "package-recipe license/declaration evidence for proven static toolchain contributors",
        "evidence_file_count": len(output_rows),
        "files": sorted(output_rows, key=lambda row: (row["source_family"], row["output_name"])),
        "default_manifest_dedicated_license_text_present": False,
        "license_material_assembled": True,
        "license_material_hashes_pinned": True,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "license-material-manifest.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--source-packages-dir")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    if args.preflight_only:
        result = audit_license_material_contract(args.repo_root)
    else:
        if not args.source_packages_dir:
            raise LicenseMaterialError("--source-packages-dir is required")
        result = extract_license_material(
            repo_root=args.repo_root,
            source_packages_dir=args.source_packages_dir,
            output_dir=args.output_dir,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
