"""Assemble one fail-closed Gate-17 third-party redistribution-material bundle."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from gate17_ffmpeg_source_snapshot import audit_snapshot_contract, build_snapshot
from gate17_source_license_material import (
    audit_license_material_contract,
    extract_license_material,
)
from gate17_source_material_bundle import (
    audit_source_bundle_contract,
    materialize_source_bundle,
)


class RedistributionMaterialError(RuntimeError):
    """Raised when the integrated redistribution-material boundary drifts."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_redistribution_material_contract(repo_root: str | Path) -> dict:
    root = Path(repo_root)
    source = audit_source_bundle_contract(root)
    licenses = audit_license_material_contract(root)
    ffmpeg = audit_snapshot_contract(root)

    if source["bundle_scope_count"] != 4:
        raise RedistributionMaterialError("expected exactly four proven toolchain source families")
    if licenses["source_family_count"] != 4 or licenses["file_count"] != 9:
        raise RedistributionMaterialError("toolchain license-material scope drifted")
    if ffmpeg.get("assembled") is not True or ffmpeg.get("hashes_pinned") is not True:
        raise RedistributionMaterialError("FFmpeg source snapshot is not assembled and pinned")

    for result, label in (
        (source, "toolchain source"),
        (licenses, "toolchain license"),
        (ffmpeg, "FFmpeg source"),
    ):
        for field in ("source_material_complete", "legal_compliance_claimed"):
            if result.get(field) is not False:
                raise RedistributionMaterialError(
                    f"{label} boundary attempted to promote {field}"
                )

    if source.get("license_notice_material_complete") is not False:
        raise RedistributionMaterialError(
            "toolchain source boundary attempted to promote license_notice_material_complete"
        )
    if licenses.get("license_notice_material_complete") is not False:
        raise RedistributionMaterialError(
            "toolchain license boundary attempted to promote license_notice_material_complete"
        )

    return {
        "schema_version": 1,
        "passed": True,
        "toolchain_source_family_count": source["bundle_scope_count"],
        "toolchain_license_evidence_file_count": licenses["file_count"],
        "ffmpeg_source_snapshot_assembled": True,
        "redistribution_material_bundle_assembled": False,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }


def _technical_inventory(repo_root: Path) -> str:
    toolchain = json.loads(
        (
            repo_root
            / "third_party/ffmpeg-lgpl-candidate/TOOLCHAIN-CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    source = json.loads(
        (
            repo_root
            / "third_party/ffmpeg-lgpl-candidate/SOURCE-CONTRACT.json"
        ).read_text(encoding="utf-8")
    )
    static_scope = toolchain["static_contributor_source_material"]
    critical = toolchain["critical_package_source_material"]
    target = source["minimal_helper_target"]

    lines = [
        "FM2001 Windows 11 port - third-party material inventory",
        "",
        "Technical provenance inventory only. This file is not a legal-compliance declaration.",
        "",
        "FFmpeg",
        f"  source repository: {target['source_repository']}",
        f"  source commit: {target['source_commit']}",
        f"  license file: {target['license_file']}",
        f"  source archive: {target['source_snapshot']['archive_filename']}",
        "",
        "Proven static toolchain contributors",
    ]
    required_versions = toolchain["required_package_versions"]
    for package, family in zip(
        static_scope["contributing_packages"],
        static_scope["contributing_source_families"],
        strict=True,
    ):
        family_row = critical["source_families"][family]
        licenses = ", ".join(family_row["license_metadata"])
        lines.extend(
            [
                f"  {package} {required_versions[package]}",
                f"    source family: {family}",
                f"    source archive: {Path(family_row['source_only_tarball']).name}",
                f"    declared license metadata: {licenses}",
            ]
        )

    lines.extend(
        [
            "",
            "Boundary",
            "  The bundle preserves exact source and package-recipe license/declaration",
            "  evidence for the currently proven redistributed third-party code.",
            "  license_notice_material_complete=false",
            "  source_material_complete=false",
            "  legal_compliance_claimed=false",
            "",
        ]
    )
    return "\n".join(lines)


def assemble_redistribution_material_bundle(
    *,
    repo_root: str | Path,
    ffmpeg_source: str | Path,
    output_dir: str | Path,
) -> dict:
    root = Path(repo_root)
    ffmpeg_source = Path(ffmpeg_source)
    output = Path(output_dir)
    audit_redistribution_material_contract(root)

    toolchain_root = output / "toolchain"
    toolchain_source = materialize_source_bundle(
        repo_root=root,
        output_dir=toolchain_root,
    )
    license_result = extract_license_material(
        repo_root=root,
        source_packages_dir=toolchain_root / "source-packages",
        output_dir=toolchain_root / "license-material",
    )
    ffmpeg_result = build_snapshot(
        repo_root=root,
        ffmpeg_source=ffmpeg_source,
        output_dir=output / "ffmpeg",
    )

    if toolchain_source.get("source_package_count") != 4:
        raise RedistributionMaterialError("integrated bundle did not materialize four source packages")
    if license_result.get("evidence_file_count") != 9:
        raise RedistributionMaterialError("integrated bundle did not materialize nine license files")
    if ffmpeg_result.get("assembled") is not True:
        raise RedistributionMaterialError("integrated bundle did not materialize FFmpeg source")

    output.mkdir(parents=True, exist_ok=True)
    (output / "THIRD-PARTY-MATERIALS.txt").write_text(
        _technical_inventory(root),
        encoding="utf-8",
        newline="\n",
    )

    files = []
    for path in sorted(p for p in output.rglob("*") if p.is_file()):
        relative = path.relative_to(output).as_posix()
        if relative == "redistribution-material-manifest.json":
            continue
        files.append(
            {
                "path": relative,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
            }
        )

    if not files:
        raise RedistributionMaterialError("integrated redistribution bundle is empty")

    manifest = {
        "schema_version": 1,
        "passed": True,
        "bundle_scope": (
            "exact FFmpeg source snapshot plus exact source/license evidence for the "
            "four proven static toolchain contributor families"
        ),
        "file_count": len(files),
        "files": files,
        "toolchain_source_family_count": 4,
        "toolchain_source_package_count": 4,
        "toolchain_license_evidence_file_count": 9,
        "ffmpeg_source_snapshot_assembled": True,
        "redistribution_material_bundle_assembled": True,
        "license_notice_material_complete": False,
        "source_material_complete": False,
        "legal_compliance_claimed": False,
    }
    (output / "redistribution-material-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--ffmpeg-source")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()

    if args.preflight_only:
        result = audit_redistribution_material_contract(args.repo_root)
    else:
        if not args.ffmpeg_source:
            raise RedistributionMaterialError("--ffmpeg-source is required")
        result = assemble_redistribution_material_bundle(
            repo_root=args.repo_root,
            ffmpeg_source=args.ffmpeg_source,
            output_dir=args.output_dir,
        )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
