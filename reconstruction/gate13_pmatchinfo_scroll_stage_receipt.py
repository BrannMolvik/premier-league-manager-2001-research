"""Private Gate-13 PMatchInfo scroll staging receipt validator.

This tool validates one exact-path source-inventory report and the staged bytes
for the three still-pending PMatchInfo vertical-scroll assets. It records byte
identity and raw EA444 header geometry only. It does not infer how the original
renderer composes, positions, clips, repeats, drags, or animates those assets.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Mapping

from ea444_header import parse_ea444_header
from gate13_button_source_trace import require_private_output_path
from gate13_source_inventory import normalize_member
from original_pmatchinfo_scroll_readiness import (
    PMATCHINFO_SCROLL_EXACT_PATH_FILE,
    pending_pmatchinfo_scroll_source_paths,
    validate_pmatchinfo_scroll_exact_path_contract,
)


class PMatchInfoScrollStageReceiptError(RuntimeError):
    pass


_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_EXTRACTED_LAYERS = {
    "zip-extracted",
    "iso9660-extracted",
    "disc-image-extracted",
}


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_pmatchinfo_scroll_stage_receipt(
    *,
    repo_root: str | Path,
    inventory_report: str | Path,
    staging_root: str | Path,
) -> dict:
    """Validate all pending scroll assets against one complete hashed selection."""
    root = Path(repo_root).resolve()
    expected = validate_pmatchinfo_scroll_exact_path_contract(root)
    expected_set = set(expected)

    report_path = Path(inventory_report).resolve()
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll inventory report is not readable JSON"
        ) from exc
    if not isinstance(report, Mapping):
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll inventory report root must be an object"
        )
    if report.get("only_explicit") is not True:
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging requires only_explicit=true"
        )
    if report.get("unresolved_explicit_paths") != []:
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging report has unresolved exact paths"
        )
    source_sha = report.get("source_sha256")
    if not isinstance(source_sha, str) or not _HEX64.fullmatch(source_sha):
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging report requires a hashed source archive"
        )

    raw_explicit = report.get("explicit_paths")
    if not isinstance(raw_explicit, list) or any(
        not isinstance(value, str) for value in raw_explicit
    ):
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging report explicit_paths is invalid"
        )
    explicit = {normalize_member(value) for value in raw_explicit}
    if explicit != expected_set:
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging report exact-path set differs from contract"
        )

    raw_candidates = report.get("candidates")
    if not isinstance(raw_candidates, list):
        raise PMatchInfoScrollStageReceiptError(
            "PMatchInfo scroll staging report candidates is invalid"
        )
    candidate_by_path: dict[str, Mapping[str, object]] = {}
    for item in raw_candidates:
        if not isinstance(item, Mapping) or not isinstance(item.get("path"), str):
            continue
        path = normalize_member(str(item["path"]))
        if path not in expected_set:
            continue
        if path in candidate_by_path:
            raise PMatchInfoScrollStageReceiptError(
                f"duplicate extracted candidate for {path}"
            )
        candidate_by_path[path] = item
    if set(candidate_by_path) != expected_set:
        missing = sorted(expected_set - set(candidate_by_path))
        raise PMatchInfoScrollStageReceiptError(
            f"PMatchInfo scroll staging report is missing candidates: {missing}"
        )

    stage = Path(staging_root).resolve()
    assets: list[dict] = []
    for source_path in expected:
        item = candidate_by_path[source_path]
        if item.get("candidate_reason") != "explicit-path":
            raise PMatchInfoScrollStageReceiptError(
                f"{source_path} is not an explicit-path candidate"
            )
        if item.get("source_layer") not in _ALLOWED_EXTRACTED_LAYERS:
            raise PMatchInfoScrollStageReceiptError(
                f"{source_path} does not prove extracted source bytes"
            )
        candidate_sha = item.get("sha256")
        candidate_size = item.get("size")
        if (
            not isinstance(candidate_sha, str)
            or not _HEX64.fullmatch(candidate_sha)
            or type(candidate_size) is not int
            or candidate_size <= 0
        ):
            raise PMatchInfoScrollStageReceiptError(
                f"{source_path} candidate identity is incomplete"
            )

        staged = stage.joinpath(*source_path.split("/")).resolve()
        try:
            staged.relative_to(stage)
        except ValueError as exc:
            raise PMatchInfoScrollStageReceiptError(
                f"staged path escapes staging root: {source_path}"
            ) from exc
        if not staged.is_file():
            raise PMatchInfoScrollStageReceiptError(
                f"staged PMatchInfo scroll asset is missing: {source_path}"
            )
        actual_size = staged.stat().st_size
        actual_sha = _sha256_file(staged)
        if actual_size != candidate_size or actual_sha != candidate_sha:
            raise PMatchInfoScrollStageReceiptError(
                f"staged PMatchInfo scroll asset differs from inventory: {source_path}"
            )

        try:
            header = parse_ea444_header(staged.read_bytes())
        except Exception as exc:
            raise PMatchInfoScrollStageReceiptError(
                f"staged PMatchInfo scroll asset has invalid EA444 header: {source_path}"
            ) from exc
        assets.append(
            {
                "source_path": source_path,
                "sha256": actual_sha,
                "size_bytes": actual_size,
                "source_layer": item.get("source_layer"),
                "header_width": int(header.width),
                "header_height": int(header.height),
            }
        )

    return {
        "schema_version": 1,
        "passed": True,
        "source_sha256": source_sha,
        "exact_path_contract": str(PMATCHINFO_SCROLL_EXACT_PATH_FILE),
        "asset_count": len(assets),
        "assets": assets,
        "ready_for_provenance_import": True,
        "native_scroll_behavior_recovered": False,
        "renderer_geometry_recovered": False,
        "evidence_limit": (
            "This receipt proves exact selected source bytes and raw EA444 header "
            "dimensions only. It does not prove PMatchInfo bar/thumb composition, "
            "placement, clipping, range arithmetic, hover, held-repeat, wheel, "
            "drag, or animation behavior."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--inventory-report", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require_private_output_path(args.output, repository_root=args.repo_root)
    receipt = validate_pmatchinfo_scroll_stage_receipt(
        repo_root=args.repo_root,
        inventory_report=args.inventory_report,
        staging_root=args.staging_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"Private PMatchInfo scroll staging receipt saved to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
