"""Resolve persisted FastView asset basenames against a saved full-disc catalog.

The executable evidence already identifies a minimal PossessionFigures /
PossessionDiagram resource family by basename. This module turns that evidence
into exact source paths only when the saved Gate-13 disc inventory proves a
unique match. It deliberately does not infer layout, side orientation, image
geometry, or any other presentation behavior from filenames.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class FastViewResourceTarget:
    component: str
    basename: str
    proven_role: str


TARGETS = (
    FastViewResourceTarget(
        "PossessionFigures",
        "team_bar_1.444",
        "one of the three source-proven possession percentage bars",
    ),
    FastViewResourceTarget(
        "PossessionFigures",
        "blank_bar.444",
        "neutral/contested possession percentage bar family",
    ),
    FastViewResourceTarget(
        "PossessionFigures",
        "team_bar_2.444",
        "one of the three source-proven possession percentage bars",
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "pitch_left.444",
        "territorial/pitch-position three-state diagram family",
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "pitch_middle.444",
        "territorial/pitch-position three-state diagram family",
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "pitch_right.444",
        "territorial/pitch-position three-state diagram family",
    ),
    FastViewResourceTarget(
        "PossessionDiagram",
        "pitch_normal.444",
        "source-proven normal/default pitch diagram family",
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
        hashes[key] = digest
    return hashes


def resolve_fastview_resources(report: dict) -> dict:
    """Resolve exact source paths only when a target basename is unique."""
    by_basename: dict[str, list[dict]] = {}
    seen_paths: set[str] = set()
    for item in report.get("disc_files", ()):
        path = item.get("path")
        if not isinstance(path, str):
            continue
        normalized = _normalize(path)
        key = normalized.casefold()
        if key in seen_paths:
            raise ValueError(
                f"Duplicate case-insensitive disc path in FastView catalog: {normalized}"
            )
        seen_paths.add(key)
        basename = PurePosixPath(normalized).name.casefold()
        by_basename.setdefault(basename, []).append({**item, "path": normalized})

    hashes = _candidate_hashes(report)
    resources: list[dict] = []
    for target in TARGETS:
        matches = sorted(
            by_basename.get(target.basename.casefold(), ()),
            key=lambda item: item["path"].casefold(),
        )
        if not matches:
            status = "missing"
        elif len(matches) == 1:
            status = "resolved"
        else:
            status = "ambiguous"

        resolved = None
        if status == "resolved":
            item = matches[0]
            resolved = {
                "path": item["path"],
                "size": item.get("size") if isinstance(item.get("size"), int) else None,
                "extent": (
                    item.get("extent") if isinstance(item.get("extent"), int) else None
                ),
                "sha256": hashes.get(item["path"].casefold()),
            }

        resources.append(
            {
                "component": target.component,
                "basename": target.basename,
                "proven_role": target.proven_role,
                "status": status,
                "resolved": resolved,
                "matches": [item["path"] for item in matches],
            }
        )

    return {
        "schema_version": 1,
        "source_sha256": report.get("source_sha256"),
        "resource_count": len(resources),
        "resolved_count": sum(item["status"] == "resolved" for item in resources),
        "all_paths_uniquely_resolved": all(
            item["status"] == "resolved" for item in resources
        ),
        "resources": resources,
        "fidelity_boundary": {
            "component_ownership_recovered": True,
            "asset_basenames_recovered": True,
            "exact_source_paths_require_unique_catalog_match": True,
            "layout_geometry_recovered": False,
            "side0_screen_orientation_recovered": False,
            "territory_thresholds_recovered": False,
        },
    }


def require_unique_fastview_resources(catalog: dict) -> None:
    unresolved = [
        f"{item['basename']}={item['status']}"
        for item in catalog.get("resources", ())
        if item.get("status") != "resolved"
    ]
    if unresolved:
        raise ValueError(
            "FastView resources are not uniquely source-resolved: "
            + ", ".join(unresolved)
        )


def resolved_paths(catalog: dict) -> list[str]:
    require_unique_fastview_resources(catalog)
    return [
        item["resolved"]["path"]
        for item in catalog["resources"]
        if item.get("resolved") is not None
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument(
        "--require-unique",
        action="store_true",
        help="Fail unless every persisted FastView target basename resolves once.",
    )
    parser.add_argument(
        "--paths-only",
        action="store_true",
        help="Print exact resolved source-relative paths; implies --require-unique.",
    )
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    catalog = resolve_fastview_resources(report)
    if args.require_unique or args.paths_only:
        require_unique_fastview_resources(catalog)

    if args.paths_only:
        for path in resolved_paths(catalog):
            print(path)
    else:
        print(json.dumps(catalog, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
