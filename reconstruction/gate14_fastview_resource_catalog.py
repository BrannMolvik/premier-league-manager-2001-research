"""Resolve source-proven FastView assets against a saved full-disc catalog.

The canonical executable embeds the full original path for every bounded
PossessionFigures/PossessionDiagram asset in this module. The resolver therefore
matches those exact case-insensitive source paths rather than inferring a path
from a basename. This is important for `pitch_normal.444`, whose basename
also exists under `Generic/match_report` on the authorized source disc.

Layout and timing are separate fidelity questions. This module proves resource
identity only.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path, PurePosixPath


CANONICAL_SOURCE_ARCHIVE_SHA256 = (
    "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
)


@dataclass(frozen=True)
class FastViewResourceTarget:
    component: str
    source_path: str
    proven_role: str
    executable_string_va: int
    size_bytes: int
    sha256: str
    width: int
    height: int

    @property
    def basename(self) -> str:
        return PurePosixPath(self.source_path).name


TARGETS = (
    FastViewResourceTarget(
        "PossessionFigures",
        "FM2001_Art/FastView/team_bar_1.444",
        "one of the three source-proven possession percentage bars",
        0x8293D4,
        2344,
        "edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d",
        82,
        16,
    ),
    FastViewResourceTarget(
        "PossessionFigures",
        "FM2001_Art/FastView/blank_bar.444",
        "neutral/contested possession percentage bar family",
        0x8293B0,
        2776,
        "961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a",
        82,
        16,
    ),
    FastViewResourceTarget(
        "PossessionFigures",
        "FM2001_Art/FastView/team_bar_2.444",
        "one of the three source-proven possession percentage bars",
        0x829334,
        2312,
        "4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751",
        82,
        16,
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "FM2001_Art/FastView/pitch_left.444",
        "territorial/pitch-position three-state diagram family",
        0x8298D4,
        9736,
        "bf1cf154f9742b39953771a248c7d1269d8d0394856ab1dc76dd81882b1b29d9",
        125,
        78,
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "FM2001_Art/FastView/pitch_middle.444",
        "territorial/pitch-position three-state diagram family",
        0x8298AC,
        7896,
        "ad53294836bf1f489060e9339da79fa43f2fb70034c890ea93dbff14f5caee77",
        98,
        78,
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "FM2001_Art/FastView/pitch_right.444",
        "territorial/pitch-position three-state diagram family",
        0x829888,
        9408,
        "dedc194dc9410ddc6d606fdabd3fe779a0c1bf0bfdfe85752f9a56d57171e5fd",
        125,
        78,
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "FM2001_Art/FastView/pitch_normal.444",
        "source-proven normal/default pitch diagram family",
        0x8298F8,
        18424,
        "326f484f264630d656e47aee1eb8419970ddbf336fbbc4e47588ff841a346ced",
        294,
        78,
    ),
)


def _normalize(path: str) -> str:
    return path.replace("\\", "/").strip("/")


def _candidate_hashes(report: dict) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for item in report.get("candidates", ()):
        path = item.get("path")
        digest = item.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            continue
        key = _normalize(path).casefold()
        previous = hashes.get(key)
        if previous is not None and previous != digest:
            raise ValueError(
                f"Conflicting source hashes for FastView resource path: {_normalize(path)}"
            )
        hashes[key] = digest.casefold()
    return hashes


def resolve_fastview_resources(report: dict) -> dict:
    """Resolve only the exact source paths embedded by the canonical executable."""
    by_path: dict[str, dict] = {}
    by_basename: dict[str, list[str]] = {}
    for item in report.get("disc_files", ()):
        path = item.get("path")
        if not isinstance(path, str):
            continue
        normalized = _normalize(path)
        key = normalized.casefold()
        if key in by_path:
            raise ValueError(
                f"Duplicate case-insensitive disc path in FastView catalog: {normalized}"
            )
        normalized_item = {**item, "path": normalized}
        by_path[key] = normalized_item
        by_basename.setdefault(PurePosixPath(normalized).name.casefold(), []).append(
            normalized
        )

    hashes = _candidate_hashes(report)
    resources: list[dict] = []
    for target in TARGETS:
        exact = by_path.get(_normalize(target.source_path).casefold())
        basename_matches = sorted(
            by_basename.get(target.basename.casefold(), ()), key=str.casefold
        )
        status = "resolved"
        observed_hash = None
        if exact is None:
            status = "missing"
        elif exact.get("size") != target.size_bytes:
            status = "size_mismatch"
        else:
            observed_hash = hashes.get(exact["path"].casefold())
            if observed_hash is not None and observed_hash != target.sha256:
                status = "hash_mismatch"

        resolved = None
        if status == "resolved":
            resolved = {
                "path": exact["path"],
                "size": target.size_bytes,
                "extent": (
                    exact.get("extent") if isinstance(exact.get("extent"), int) else None
                ),
                "expected_sha256": target.sha256,
                "observed_sha256": observed_hash,
                "width": target.width,
                "height": target.height,
                "executable_string_va": target.executable_string_va,
            }

        resources.append(
            {
                "component": target.component,
                "basename": target.basename,
                "source_path": target.source_path,
                "proven_role": target.proven_role,
                "status": status,
                "resolved": resolved,
                "basename_matches": basename_matches,
            }
        )

    return {
        "schema_version": 2,
        "source_sha256": report.get("source_sha256"),
        "canonical_source_archive_sha256": CANONICAL_SOURCE_ARCHIVE_SHA256,
        "resource_count": len(resources),
        "resolved_count": sum(item["status"] == "resolved" for item in resources),
        "all_paths_source_resolved": all(
            item["status"] == "resolved" for item in resources
        ),
        "resources": resources,
        "fidelity_boundary": {
            "component_ownership_recovered": True,
            "asset_basenames_recovered": True,
            "exact_source_paths_source_proven": True,
            "layout_geometry_recovered": False,
            "side0_screen_orientation_recovered": False,
            "territory_update_cadence_recovered": False,
        },
    }


def require_source_resolved_fastview_resources(catalog: dict) -> None:
    unresolved = [
        f"{item['source_path']}={item['status']}"
        for item in catalog.get("resources", ())
        if item.get("status") != "resolved"
    ]
    if unresolved:
        raise ValueError(
            "FastView resources are not source-resolved: " + ", ".join(unresolved)
        )


def resolved_paths(catalog: dict) -> list[str]:
    require_source_resolved_fastview_resources(catalog)
    return [
        item["resolved"]["path"]
        for item in catalog["resources"]
        if item.get("resolved") is not None
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--require-source-resolved",
        "--require-unique",
        dest="require_source_resolved",
        action="store_true",
        help="Fail unless every source-proven FastView path resolves exactly.",
    )
    parser.add_argument(
        "--paths-only",
        action="store_true",
        help="Print exact resolved source-relative paths; implies source resolution.",
    )
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    catalog = resolve_fastview_resources(report)
    if args.require_source_resolved or args.paths_only:
        require_source_resolved_fastview_resources(catalog)

    if args.paths_only:
        for path in resolved_paths(catalog):
            print(path)
    else:
        print(json.dumps(catalog, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
