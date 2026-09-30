from __future__ import annotations

import argparse
import json
from pathlib import PurePosixPath
import re
from typing import Iterable


def _lower(value: str) -> str:
    return value.replace("\\", "/").lower()


def query_disc_files(
    report: dict,
    *,
    contains: Iterable[str] = (),
    suffixes: Iterable[str] = (),
    regex: str | None = None,
    top_level: Iterable[str] = (),
) -> list[dict]:
    """Filter a Gate-13 source report without re-reading the source image."""

    contains_lower = tuple(_lower(value) for value in contains if value)
    suffixes_lower = tuple(
        value.lower() if value.startswith(".") else f".{value.lower()}"
        for value in suffixes
        if value
    )
    top_lower = {_lower(value).strip("/") for value in top_level if value}
    pattern = re.compile(regex, re.IGNORECASE) if regex else None

    matches = []
    for item in report.get("disc_files", []):
        path = item.get("path")
        if not isinstance(path, str):
            continue
        lowered = _lower(path)
        if contains_lower and not all(term in lowered for term in contains_lower):
            continue
        if suffixes_lower and PurePosixPath(lowered).suffix not in suffixes_lower:
            continue
        if top_lower:
            first = lowered.split("/", 1)[0]
            if first not in top_lower:
                continue
        if pattern is not None and pattern.search(path) is None:
            continue
        matches.append(item)

    return sorted(matches, key=lambda item: _lower(item["path"]))


def query_source_files(
    report: dict,
    *,
    layer: str = "both",
    contains: Iterable[str] = (),
    suffixes: Iterable[str] = (),
    regex: str | None = None,
    top_level: Iterable[str] = (),
) -> list[dict]:
    """Query every source-archive layer; preserve the layer for provenance.

    Original disc and outer ZIP members may share source-relative names.
    Exposing rather than collapsing the layer allows collision detection
    before creating a reusable exact-path staging list.
    """
    if layer not in {"both", "disc", "zip"}:
        raise ValueError(f"Unsupported source catalog layer: {layer}")
    matches: list[dict] = []
    for kind, records in (("disc", "disc_files"), ("zip", "zip_files")):
        if layer not in {"both", kind}:
            continue
        filtered = query_disc_files(
            {"disc_files": report.get(records, [])},
            contains=contains,
            suffixes=suffixes,
            regex=regex,
            top_level=top_level,
        )
        matches.extend({"source_layer": kind, **entry} for entry in filtered)
    return sorted(matches, key=lambda item: (_lower(item["path"]), item["source_layer"]))


def summarize_source_files(report: dict) -> dict:
    """Keep outer-ZIP and nested-disc counts distinct for audit purposes."""
    disc = summarize_disc_files(report)
    zipped = summarize_disc_files({"disc_files": report.get("zip_files", [])})
    return {
        "disc": disc,
        "zip": {
            "zip_file_count": zipped["disc_file_count"],
            "top_level_counts": zipped["top_level_counts"],
            "suffix_counts": zipped["suffix_counts"],
            "nested_disc_image_count": sum(
                bool(item.get("is_disc_image")) for item in report.get("zip_files", [])
            ),
        },
    }


def summarize_disc_files(report: dict) -> dict:
    roots: dict[str, int] = {}
    suffixes: dict[str, int] = {}

    for item in report.get("disc_files", []):
        path = item.get("path")
        if not isinstance(path, str):
            continue
        normalized = path.replace("\\", "/").strip("/")
        if not normalized:
            continue
        root = normalized.split("/", 1)[0]
        roots[root] = roots.get(root, 0) + 1
        suffix = PurePosixPath(normalized).suffix.lower() or "<none>"
        suffixes[suffix] = suffixes.get(suffix, 0) + 1

    return {
        "disc_file_count": len(report.get("disc_files", [])),
        "top_level_counts": dict(sorted(roots.items(), key=lambda item: item[0].lower())),
        "suffix_counts": dict(
            sorted(suffixes.items(), key=lambda item: (-item[1], item[0]))
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Query saved Gate-13 outer-ZIP and nested-disc catalogs without "
            "re-reading or reconverting the authorized source archive."
        )
    )
    parser.add_argument("report")
    parser.add_argument("--contains", action="append", default=[])
    parser.add_argument("--suffix", action="append", default=[])
    parser.add_argument("--regex")
    parser.add_argument("--top-level", action="append", default=[])
    parser.add_argument(
        "--layer",
        choices=("both", "disc", "zip"),
        default="both",
        help="Query the outer ZIP, nested disc, or both catalogs (default).",
    )
    parser.add_argument("--summary", action="store_true")
    parser.add_argument(
        "--paths-only",
        action="store_true",
        help="Print only matching source-relative paths, one per line.",
    )
    args = parser.parse_args()

    with open(args.report, "r", encoding="utf-8") as handle:
        report = json.load(handle)

    if args.summary:
        if args.paths_only:
            parser.error("--paths-only cannot be combined with --summary")
        result = summarize_source_files(report)
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        matches = query_source_files(
            report,
            layer=args.layer,
            contains=args.contains,
            suffixes=args.suffix,
            regex=args.regex,
            top_level=args.top_level,
        )
        if args.paths_only:
            paths = [_lower(item["path"]) for item in matches]
            if len(set(paths)) != len(paths):
                parser.error(
                    "Matching paths occur multiple times across source layers or "
                    "within a layer; disambiguate before exact-path staging."
                )
            for item in matches:
                print(item["path"])
        else:
            print(json.dumps({"matches": matches}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
