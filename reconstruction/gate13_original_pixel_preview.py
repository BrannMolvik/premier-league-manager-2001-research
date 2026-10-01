"""Export exact decoded FM2001 first-screen pixels for private diagnostics.

This tool writes source-backed *backgrounds* and individually numbered
source-atlas frames for comparison against the original game. The manifest
records the executable-proven Button group/subframe mapping and PStartMenu
Zurich line origins/native 16-bit color values. It does not guess a semantic
name for mask-4 group 1, invent hierarchy row contents, or substitute themed
UI. Original language glyph alpha is exported separately as raw lossless PGM.
Only the exact hash-checked original loaders may claim source verification.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import zlib

from original_button_frames import (
    BUTTON_GROUP_LENGTHS, OriginalButtonAtlas, OriginalButtonFrame,
)
from original_front_end_layout import SCREEN_SIZE
from original_pstartmenu_resources import (
    OriginalPStartMenuResources, load_verified_english_pstartmenu_inputs,
)
from original_teamselect_hierarchy_art import OriginalHierarchyStrip
from original_teamselect_resources import (
    OriginalTeamSelectResources, load_verified_original_teamselect_inputs,
)


class OriginalPreviewError(ValueError):
    pass


_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data)) + kind + data +
        struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def encode_rgba_png(width: int, height: int, rgba: bytes) -> bytes:
    """Lossless PNG RGBA8, filter 0; exact source RGBA preserved."""
    if (
        type(width) is not int or type(height) is not int
        or width <= 0 or height <= 0
        or len(rgba) != width * height * 4
    ):
        raise OriginalPreviewError("Invalid source RGBA geometry/pixel count")
    row_bytes = width * 4
    scanlines = b"".join(
        b"\x00" + rgba[y * row_bytes:(y + 1) * row_bytes]
        for y in range(height)
    )
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        _PNG_SIGNATURE + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(scanlines, level=6))
        + _chunk(b"IEND", b"")
    )


def encode_alpha_pgm(width: int, height: int, alpha: bytes) -> bytes:
    """Uncolored glyph alpha; never invent the native FM2001 font color."""
    if (
        type(width) is not int or type(height) is not int
        or width <= 0 or height <= 0 or len(alpha) != width * height
    ):
        raise OriginalPreviewError("Invalid original glyph alpha dimensions")
    return f"P5\n{width} {height}\n255\n".encode("ascii") + alpha


def _source_frame_manifest(
    root: Path, name: str,
    frames: tuple[OriginalButtonFrame, ...],
) -> list[dict]:
    out = []
    target = root / name
    target.mkdir()
    for source_index, frame in enumerate(frames):
        filename = f"source_{source_index:03d}.png"
        (target / filename).write_bytes(
            encode_rgba_png(frame.width, frame.height, frame.rgba)
        )
        if source_index < BUTTON_GROUP_LENGTHS[0]:
            group, subframe = 0, source_index
        elif source_index < sum(BUTTON_GROUP_LENGTHS[:2]):
            group, subframe = 1, source_index - BUTTON_GROUP_LENGTHS[0]
        else:
            group, subframe = 2, 0
        out.append({
            "source_index_only": source_index, "file": f"{name}/{filename}",
            "width": frame.width, "height": frame.height,
            "rgba_sha256": sha256(frame.rgba).hexdigest(),
            "native_group": group,
            "native_subframe": subframe,
            "native_group_semantics": (
                "disabled" if group == 2 else
                "enabled_mask4_clear" if group == 0 else
                "enabled_mask4_set_semantic_name_unproven"
            ),
        })
    return out


def _write_atlas(
    root: Path, name: str, atlas: OriginalButtonAtlas
) -> dict:
    return {
        "original_source_path": atlas.spec.source_path,
        "original_source_sha256": atlas.spec.source_sha256,
        "frame_width": atlas.spec.frame_width,
        "frame_height": atlas.spec.frame_height,
        "frames": _source_frame_manifest(root, name, atlas.frames),
    }


def _write_hierarchy_strip(
    root: Path, name: str, strip: OriginalHierarchyStrip
) -> dict:
    return {
        "original_source_path": strip.spec.path,
        "original_source_sha256": strip.spec.source_sha256,
        "decoded_source_height": strip.source_height,
        "frames": _source_frame_manifest(root, name, strip.frames),
    }


def _require_private_directory(
    destination: Path, *, repository_root: Path | None = None
) -> Path:
    root = Path(__file__).resolve().parent.parent if repository_root is None else Path(repository_root)
    dest = Path(destination).resolve()
    if dest.is_relative_to(root.resolve()):
        raise OriginalPreviewError(
            "Export original pixel diagnostics only outside the tracked repository"
        )
    if dest.exists():
        raise OriginalPreviewError(
            "Use a new output directory; do not overwrite existing source diagnostics"
        )
    return dest


def export_first_screen_source_pixels(
    menu: OriginalPStartMenuResources,
    team: OriginalTeamSelectResources,
    destination: Path,
    *, source_verification: str = "caller-supplied-debug-data",
    repository_root: Path | None = None,
) -> dict:
    """Export source-order pixels without visual-state or text-placement guesses.

    source_verification='canonical-loaders-verified' must only be used by the
    CLI after both source-hash-pinned original loaders have returned.
    """
    dest = _require_private_directory(destination, repository_root=repository_root)
    dest.mkdir(parents=True)
    w, h = SCREEN_SIZE
    for filename, rgba in (
        ("pstartmenu_background_only.png", menu.background_rgba),
        ("teamselect_background_only.png", team.background_rgba),
    ):
        (dest / filename).write_bytes(encode_rgba_png(w, h, rgba))

    controls = []
    caption_dir = dest / "caption_alpha"
    caption_dir.mkdir()
    for item in menu.captions:
        mask = item.glyph_mask
        label_file = None
        if mask.width > 0 and mask.height > 0:
            label_file = f"caption_alpha/event_{item.event}.pgm"
            (dest / label_file).write_bytes(
                encode_alpha_pgm(mask.width, mask.height, mask.alpha)
            )
        controls.append({
            "event": item.event,
            "original_idx_position": item.source_idx_position,
            "original_text": item.original_text,
            "rect": vars(item.control_rect),
            "uncolored_source_glyph_alpha_file": label_file,
            "glyph_alpha_sha256": sha256(mask.alpha).hexdigest(),
            "native_line_origin": {
                "x": item.line_origin_x, "y": item.line_origin_y,
            },
            "native_clip_rect": vars(item.clip_rect),
            "native_style": item.native_style,
            "native_color_16_by_group": {
                "0": item.native_color_for_group(0),
                "1": item.native_color_for_group(1),
                "2": item.native_color_for_group(2),
            },
        })

    manifest = {
        "purpose": "private original-source pixel diagnosis, NOT finished FM2001 UI",
        "source_verification": source_verification,
        "proven_rgba_backgrounds": {
            "pstartmenu_background_only.png":
                sha256(menu.background_rgba).hexdigest(),
            "teamselect_background_only.png":
                sha256(team.background_rgba).hexdigest(),
        },
        "menu_controls": controls,
        "button_atlases": {
            "pstartmenu": _write_atlas(
                dest, "pstartmenu_button_source_frames", menu.button_atlas
            ),
            "teamselect": _write_atlas(
                dest, "teamselect_action_source_frames", team.action_atlas
            ),
        },
        "hierarchy_art": None,
        "native_button_mapping": {
            "group_lengths": list(BUTTON_GROUP_LENGTHS),
            "pointer_inside_mask_8_advances_subframe": True,
            "pointer_outside_retreats_subframe": True,
            "mask_4_user_facing_semantic_name": None,
            "screen_update_tick_duration": None,
        },
    }
    if team.hierarchy_art is not None:
        manifest["hierarchy_art"] = {
            "animation": _write_hierarchy_strip(
                dest, "teamselect_hierarchy_animation_source_frames",
                team.hierarchy_art.animation,
            ),
            "bars": _write_hierarchy_strip(
                dest, "teamselect_hierarchy_bars_source_frames",
                team.hierarchy_art.bars,
            ),
        }
    (dest / "source_pixel_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original-exe", type=Path, required=True)
    parser.add_argument("--original-art-root", type=Path, required=True)
    parser.add_argument("--original-language-root", type=Path, required=True)
    parser.add_argument("--original-font20", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    _require_private_directory(args.output_dir)
    menu = load_verified_english_pstartmenu_inputs(
        original_art_dir=args.original_art_root,
        original_language_dir=args.original_language_root,
        original_zurich_font20=args.original_font20,
        original_executable=args.original_exe,
    )
    team = load_verified_original_teamselect_inputs(
        original_art_dir=args.original_art_root,
        original_executable=args.original_exe,
    )
    result = export_first_screen_source_pixels(
        menu, team, args.output_dir,
        source_verification="canonical-loaders-verified",
    )
    print(
        "Wrote private original background, source-frame and glyph-alpha "
        "diagnostics with native group and PStartMenu caption metadata."
    )
    print(json.dumps({
        "source_verification": result["source_verification"],
        "output_directory": str(args.output_dir),
        "original_background_rgba_sha256": result["proven_rgba_backgrounds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
