"""Fail-closed first-screen provenance check before importing licensed art.

The source selection is the limited, executable-correlated Gate 13 slice, not
an original full-disc dump. The authorized ZIP, individual resource identities,
extraction layer and staged source bytes must all match previously recovered
first-hand evidence before the existing gate13_asset_import tool is invoked.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

from gate13_source_inventory import normalize_member


CANONICAL_ARCHIVE_SHA256 = (
    "677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4"
)
CANONICAL_ARCHIVE_SIZE = 511121336


class FirstScreenSelectionError(ValueError):
    pass


@dataclass(frozen=True)
class ExpectedSource:
    path: str
    sha256: str


FIRST_SCREEN_ORIGINALS = (
    ExpectedSource(
        "FM2001_Art/Generic/bground.444",
        "9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/main_menu/main_menu_bground.444",
        "297b54dbee7d7d31a081b1459ed497b251c2bf1aa00092976557d5b8065e7e4b",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/team_choice/background.444",
        "7927bc3baf35f2ee906f6ea714c77d0e51282ee5316ec43220edb95ed358694b",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444",
        "57ba72fd2a978735cbd4537aee4fa3031f13f10994067fb2ceba6c22c5ef41e3",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444",
        "d204e7086a15ac15bd9d10377526ba40bb40ffd83b5f02ba39ef8404dd42922d",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444",
        "de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22",
    ),
    ExpectedSource(
        "FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444",
        "bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa",
    ),
    ExpectedSource(
        "Fonts/Zurich_BdXCn_BT_20pixel.fnt",
        "47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166",
    ),
    ExpectedSource(
        "English.str",
        "aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601",
    ),
    ExpectedSource(
        "English.idx",
        "98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1",
    ),
)


def source_selection_file() -> Path:
    return Path(__file__).resolve().parent.parent / (
        "research/GATE13_FIRST_SCREEN_EXACT_PATHS.txt"
    )


def read_selection_paths(path: Path) -> tuple[str, ...]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return tuple(
        normalize_member(line.strip())
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    )


def assert_canonical_selection_file(path: Path) -> None:
    if read_selection_paths(path) != tuple(a.path for a in FIRST_SCREEN_ORIGINALS):
        raise FirstScreenSelectionError(
            "Extraction path list differs from proven first-screen source inventory"
        )


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_first_screen_selection(
    report: dict,
    staged_root: Path,
    *,
    expected_assets: tuple[ExpectedSource, ...] = FIRST_SCREEN_ORIGINALS,
    expected_archive_sha: str = CANONICAL_ARCHIVE_SHA256,
    expected_archive_size: int = CANONICAL_ARCHIVE_SIZE,
) -> tuple[str, ...]:
    """Return exact verified paths only if all ten independent receipts match.

    Tests may inject tiny synthetic fixture assets/archive identity; production
    CLI uses the pinned first-hand original inventory with no overrides.
    """
    expected_names = tuple(a.path for a in expected_assets)
    if len(expected_names) != len(set(name.casefold() for name in expected_names)):
        raise FirstScreenSelectionError("Ambiguous planned source paths")
    if (
        report.get("source_sha256") != expected_archive_sha
        or report.get("source_size") != expected_archive_size
    ):
        raise FirstScreenSelectionError("Inventory is not from the canonical source ZIP")
    if report.get("unresolved_explicit_paths"):
        raise FirstScreenSelectionError("Original inventory has unresolved exact paths")
    if report.get("only_explicit") is not True:
        raise FirstScreenSelectionError("Refusing broad uncontrolled source extraction")

    expected_casefold = {x.casefold() for x in expected_names}
    explicit = report.get("explicit_paths")
    if not isinstance(explicit, list) or {
        normalize_member(name).casefold() for name in explicit
    } != expected_casefold or len(explicit) != len(expected_names):
        raise FirstScreenSelectionError("Explicit source-selection receipt differs")

    candidates = report.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != len(expected_names):
        raise FirstScreenSelectionError("Expected exactly one extracted copy per asset")
    by_name = {}
    for record in candidates:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise FirstScreenSelectionError("Malformed source-inventory candidate")
        path = normalize_member(record["path"]).casefold()
        if path in by_name or path not in expected_casefold:
            raise FirstScreenSelectionError("Duplicate or unrelated asset in receipt")
        if record.get("source_layer") not in {
            "iso9660-extracted", "disc-image-extracted"
        }:
            raise FirstScreenSelectionError("Candidate is not extracted original disc data")
        by_name[path] = record

    root = Path(staged_root).resolve()
    for asset in expected_assets:
        member = PurePosixPath(asset.path)
        if member.is_absolute() or ".." in member.parts:
            raise FirstScreenSelectionError("Unsafe original source path")
        item = (root / Path(*member.parts)).resolve()
        try:
            item.relative_to(root)
        except ValueError as exc:
            raise FirstScreenSelectionError("Staging path escapes selected source root") from exc
        if not item.is_file():
            raise FirstScreenSelectionError(f"Selected original was not staged: {asset.path}")
        record = by_name[asset.path.casefold()]
        if (
            record.get("sha256") != asset.sha256
            or record.get("size") != item.stat().st_size
            or _hash_file(item) != asset.sha256
        ):
            raise FirstScreenSelectionError(
                f"Staged bytes disagree with independent source receipt: {asset.path}"
            )
    return expected_names


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify only the pinned original FM2001 first-screen source slice"
    )
    parser.add_argument("selected_inventory_json", type=Path)
    parser.add_argument("staging_root", type=Path)
    args = parser.parse_args()
    assert_canonical_selection_file(source_selection_file())
    report = json.loads(args.selected_inventory_json.read_text(encoding="utf-8"))
    paths = verify_first_screen_selection(report, args.staging_root)
    print(
        f"Verified {len(paths)} exact original first-screen resources "
        "against the canonical ZIP and per-asset hashes. Import individually "
        "with gate13_asset_import.py and its original inventory report."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
