"""Fail-closed firsthand audit of the private original FM2001 opening screens.

This tool is run *only after* extracting the authorized source ZIP to private
staging. It independently hashes the actual archive and verified executable,
rechecks the ten selected file bytes against the canonical Joliet inventory,
decodes BOTH original screen resource bundles, then compares the resulting
native source-background pixel digests and Zurich glyph masks with previously
recorded firsthand evidence.

Unlike synthetic CI, successful execution with the real source files provides
a durable original-byte regression receipt. It still does NOT verify the native
Button@ease interaction-state mapping, caption placement/color, or hierarchy
behavior. Only a small private JSON receipt is written, never original pixels
or executable disassembly. The original binaries never enter Git.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from ea444_tables import CANONICAL_EXE_SHA256
from gate13_button_source_trace import OriginalPE32, require_private_output_path
from gate13_first_screen_selection import (
    CANONICAL_ARCHIVE_SHA256,
    CANONICAL_ARCHIVE_SIZE,
    FIRST_SCREEN_ORIGINALS,
    verify_first_screen_selection,
)
from gate13_source_inventory import sha256_file
from original_button_frames import (
    PSTARTMENU_BUTTON_ATLAS,
    TEAMSELECT_BUTTON_ATLAS,
)
from original_pstartmenu_resources import (
    COMPOSED_BACKGROUND_RGBA_SHA256,
    ENGLISH_ACTION_TEXTS,
    OriginalPStartMenuResources,
    load_verified_english_pstartmenu_inputs,
)
from original_teamselect_hierarchy_art import HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC
from original_teamselect_resources import (
    TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256,
    OriginalTeamSelectResources,
    load_verified_original_teamselect_inputs,
)


class OriginalFirsthandAuditError(ValueError):
    pass


# Firsthand 20px Zurich glyph-alpha digests from the canonical source font.
# These MUST remain masks only: original native text color/origin is unknown.
EXPECTED_CAPTIONS = (
    (1, 0, "Continue", 63, 19,
     "6af205e0d5ee04c063770438919a3418b18cd8e91ab615bdc8bb21a7e9137ae2"),
    (2, 1, "Start New Game", 117, 19,
     "2fa38f32908de0f08b66c7c6d7f0f900ab9ba141cac4ae38abc3e7236134378a"),
    (3, 2, "Load Game", 81, 19,
     "5f5b62250acce9bce3a46ee101db3b9357b8b8f6a139940e06ba5e43cd7312ea"),
    (4, 6, "Quit to Windows", 120, 19,
     "6f0030a88479d55ece7b77ac5b32f99b699ceff748be890e04614c22e5bb2140"),
)


def assert_archive_and_receipt_identity(
    original_zip: Path,
    inventory_report: dict,
    *,
    expected_sha: str = CANONICAL_ARCHIVE_SHA256,
    expected_size: int = CANONICAL_ARCHIVE_SIZE,
) -> str:
    """Hash actual source ZIP, not just the inventory report's claimed digest.

    The overridable expected parameters exist for tiny synthetic regression
    fixtures. The command-line production entry point never overrides them.
    """
    archive = Path(original_zip).resolve()
    if not archive.is_file() or archive.stat().st_size != expected_size:
        raise OriginalFirsthandAuditError("Original ZIP absent or wrong physical size")
    actual = sha256_file(archive)
    if actual != expected_sha:
        raise OriginalFirsthandAuditError("Original ZIP bytes do not match canonical SHA")
    raw_inventory_path = inventory_report.get("source")
    if not isinstance(raw_inventory_path, str) or Path(raw_inventory_path).resolve() != archive:
        raise OriginalFirsthandAuditError("Inventory report belongs to another ZIP path")
    if (
        inventory_report.get("source_sha256") != actual
        or inventory_report.get("source_size") != expected_size
    ):
        raise OriginalFirsthandAuditError(
            "Inventory receipt differs from the freshly verified original ZIP"
        )
    return actual


def describe_loaded_first_screen_bytes(
    menu: OriginalPStartMenuResources,
    team: OriginalTeamSelectResources,
) -> dict:
    """Measure already loaded images/masks, without claiming their provenance.

    The source verification claim is made only by the full CLI, which calls
    strict ZIP, per-file, executable and loader validators before this step.
    """
    art = team.hierarchy_art
    return {
        "pstartmenu_background_rgba_sha256": sha256(menu.background_rgba).hexdigest(),
        "teamselect_background_rgba_sha256": sha256(team.background_rgba).hexdigest(),
        "pstartmenu_atlas_source_sha256": menu.button_atlas.spec.source_sha256,
        "teamselect_action_atlas_source_sha256": team.action_atlas.spec.source_sha256,
        "pstartmenu_original_source_frame_count": len(menu.button_atlas.frames),
        "teamselect_original_source_frame_count": len(team.action_atlas.frames),
        "captions": [
            {
                "event": item.event,
                "idx": item.source_idx_position,
                "text": item.original_text,
                "alpha_width": item.glyph_mask.width,
                "alpha_height": item.glyph_mask.height,
                "glyph_alpha_sha256": sha256(item.glyph_mask.alpha).hexdigest(),
            }
            for item in menu.captions
        ],
        "hierarchy_art": (
            {
                "animation_source_sha256": art.animation.spec.source_sha256,
                "bars_source_sha256": art.bars.spec.source_sha256,
                "animation_source_frame_count": len(art.animation.frames),
                "bars_source_frame_count": len(art.bars.frames),
            }
            if art is not None else None
        ),
        "native_button_frame_state_mapping": None,
        "native_caption_alignment_or_color": None,
        "native_teamselect_hierarchy_item_mapping": None,
    }


def require_exact_firsthand_pixel_metrics(summary: dict) -> None:
    """Reject incomplete decoded assets and changed independently known bytes."""
    if (
        summary.get("pstartmenu_background_rgba_sha256")
        != COMPOSED_BACKGROUND_RGBA_SHA256
        or summary.get("teamselect_background_rgba_sha256")
        != TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256
    ):
        raise OriginalFirsthandAuditError("Original screen background pixels changed")
    if (
        summary.get("pstartmenu_atlas_source_sha256")
        != PSTARTMENU_BUTTON_ATLAS.source_sha256
        or summary.get("teamselect_action_atlas_source_sha256")
        != TEAMSELECT_BUTTON_ATLAS.source_sha256
        or summary.get("pstartmenu_original_source_frame_count")
        != PSTARTMENU_BUTTON_ATLAS.frame_count
        or summary.get("teamselect_original_source_frame_count")
        != TEAMSELECT_BUTTON_ATLAS.frame_count
    ):
        raise OriginalFirsthandAuditError("Original action atlas identity/frame count changed")
    actual = summary.get("captions")
    expected = [
        {
            "event": event, "idx": idx, "text": text,
            "alpha_width": width, "alpha_height": height,
            "glyph_alpha_sha256": digest,
        }
        for event, idx, text, width, height, digest in EXPECTED_CAPTIONS
    ]
    if actual != expected or tuple(c["text"] for c in actual) != ENGLISH_ACTION_TEXTS:
        raise OriginalFirsthandAuditError(
            "Original English language or Zurich glyph-mask regression"
        )
    art = summary.get("hierarchy_art")
    if not isinstance(art, dict) or (
        art.get("animation_source_sha256") != HIERARCHY_ANIM_SPEC.source_sha256
        or art.get("bars_source_sha256") != HIERARCHY_BARS_SPEC.source_sha256
        or type(art.get("animation_source_frame_count")) is not int
        or art["animation_source_frame_count"] < 1
        or type(art.get("bars_source_frame_count")) is not int
        or art["bars_source_frame_count"] < 1
    ):
        raise OriginalFirsthandAuditError(
            "Verified original hierarchy art is absent or inconsistent"
        )
    if any(summary.get(key) is not None for key in (
        "native_button_frame_state_mapping",
        "native_caption_alignment_or_color",
        "native_teamselect_hierarchy_item_mapping",
    )):
        raise OriginalFirsthandAuditError(
            "Native interaction/rendering semantics require separate executable proof"
        )


def firsthand_source_audit(
    *,
    original_zip: Path,
    inventory_report_path: Path,
    staging_root: Path,
    original_executable: Path,
    output_receipt: Path,
) -> dict:
    """Generate a private real-byte receipt only after all validation passes."""
    require_private_output_path(output_receipt)
    output_receipt = Path(output_receipt).resolve()
    if output_receipt.exists():
        raise OriginalFirsthandAuditError("Refusing to replace existing audit receipt")
    report = json.loads(Path(inventory_report_path).read_text(encoding="utf-8"))
    archive_digest = assert_archive_and_receipt_identity(original_zip, report)
    selected = verify_first_screen_selection(report, staging_root)
    if selected != tuple(asset.path for asset in FIRST_SCREEN_ORIGINALS):
        raise OriginalFirsthandAuditError("Original source selection order changed")

    executable = Path(original_executable)
    canonical = OriginalPE32.parse(executable.read_bytes())
    if canonical.sha256 != CANONICAL_EXE_SHA256:
        raise OriginalFirsthandAuditError("Canonical executable identity changed")
    root = Path(staging_root)
    menu = load_verified_english_pstartmenu_inputs(
        original_art_dir=root / "FM2001_Art",
        original_language_dir=root,
        original_zurich_font20=root / "Fonts/Zurich_BdXCn_BT_20pixel.fnt",
        original_executable=executable,
    )
    team = load_verified_original_teamselect_inputs(
        original_art_dir=root / "FM2001_Art",
        original_executable=executable,
    )
    metrics = describe_loaded_first_screen_bytes(menu, team)
    require_exact_firsthand_pixel_metrics(metrics)
    result = {
        "audit": "FM2001 private canonical original first-screen bytes",
        "source_archive_sha256": archive_digest,
        "original_executable_sha256": canonical.sha256,
        "verified_original_source_paths": selected,
        "verification": (
            "Canonical physical ZIP SHA/size checked; one SHA-matched Joliet "
            "candidate and staged file per path; canonical executable PE/hash "
            "checked; both original loaders decoded and original RGBA/Zurich "
            "metrics independently matched source-era expected values."
        ),
        "fidelity_boundary": (
            "This receipt is not a native FM2001 button hover/pressed state, "
            "caption placement, hierarchy, full manager UI or Windows 11 release audit."
        ),
        "measurements": metrics,
    }
    output_receipt.parent.mkdir(parents=True, exist_ok=True)
    output_receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-zip", type=Path, required=True)
    parser.add_argument("--selection-report", type=Path, required=True)
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--original-exe", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()
    result = firsthand_source_audit(
        original_zip=args.original_zip,
        inventory_report_path=args.selection_report,
        staging_root=args.staging_root,
        original_executable=args.original_exe,
        output_receipt=args.output_receipt,
    )
    print("Verified private original FM2001 first-screen source bytes:")
    print(json.dumps({
        "source_archive_sha256": result["source_archive_sha256"],
        "original_executable_sha256": result["original_executable_sha256"],
        "pstartmenu_background_rgba_sha256":
            result["measurements"]["pstartmenu_background_rgba_sha256"],
        "teamselect_background_rgba_sha256":
            result["measurements"]["teamselect_background_rgba_sha256"],
        "native_button_state_mapping_verified": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
