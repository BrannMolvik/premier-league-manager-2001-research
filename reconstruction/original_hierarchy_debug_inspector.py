"""Private off-canvas inspector for verified original TeamSelect hierarchy art.

The original executable proves sixteen row *construction origins* and binds
two SHA-pinned resources, but has not yet established per-row sprite positions,
country/league/club contents, native hover/selected atlas frames, animation
timing or mouse events. This diagnostic deliberately keeps each manually
selected original source frame OUTSIDE the native 800x600 canvas and outside
the actual game's interaction model.

A frame is a lossless RGBA8 PNG derived from already-decoded, exact-original
resource bundles. Nothing is positioned or labeled as native UI.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256

from front_end_state import FrontEndScreen
from gate13_original_pixel_preview import encode_rgba_png
from original_first_screen_presenter import OriginalFirstScreenSnapshot
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC,
    OriginalHierarchyStrip,
    OriginalTeamSelectHierarchyArt,
)


class OriginalHierarchyDebugError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalHierarchySourceDiagnostic:
    """One manually chosen original source frame, never a native state."""
    original_source_path: str
    original_source_sha256: str
    source_frame_index_only: int
    source_frame_count: int
    width: int
    height: int
    source_frame_rgba_sha256: str
    source_frame_png: bytes
    native_screen_placement: None = None
    native_mouse_state: None = None
    native_row_label_or_club: None = None


@dataclass(frozen=True)
class OriginalHierarchyDebugBundle:
    animation: OriginalHierarchySourceDiagnostic
    bars: OriginalHierarchySourceDiagnostic
    proven_row_construction_origins_only: tuple[tuple[int, int], ...]
    native_row_hit_behavior_recovered: bool = False


def _selected_frame(
    strip: OriginalHierarchyStrip, index: int
) -> OriginalHierarchySourceDiagnostic:
    if type(index) is not int or not 0 <= index < len(strip.frames):
        raise OriginalHierarchyDebugError(
            f"Original hierarchy {strip.spec.path} source index is out of range"
        )
    frame = strip.source_frame(index)
    return OriginalHierarchySourceDiagnostic(
        original_source_path=strip.spec.path,
        original_source_sha256=strip.spec.source_sha256,
        source_frame_index_only=index,
        source_frame_count=len(strip.frames),
        width=frame.width,
        height=frame.height,
        source_frame_rgba_sha256=sha256(frame.rgba).hexdigest(),
        source_frame_png=encode_rgba_png(frame.width, frame.height, frame.rgba),
    )


def inspect_original_hierarchy_source_frames(
    snapshot: OriginalFirstScreenSnapshot,
    *,
    animation_source_index: int = 0,
    bars_source_index: int = 0,
) -> OriginalHierarchyDebugBundle | None:
    """Only inspect both distinct real strips when TeamSelect art is present.

    Different animation/bar strips may contain different numbers of source
    frames; indexes are independent. This operation NEVER composites either
    strip at unverified in-game positions.
    """
    if snapshot.screen is not FrontEndScreen.TEAM_SELECT:
        return None
    art = snapshot.hierarchy_art
    if art is None:
        return None
    if not isinstance(art, OriginalTeamSelectHierarchyArt):
        raise OriginalHierarchyDebugError("Unverified TeamSelect hierarchy art")
    if art.animation.spec != HIERARCHY_ANIM_SPEC or art.bars.spec != HIERARCHY_BARS_SPEC:
        raise OriginalHierarchyDebugError("Hierarchy source spec differs")
    return OriginalHierarchyDebugBundle(
        animation=_selected_frame(art.animation, animation_source_index),
        bars=_selected_frame(art.bars, bars_source_index),
        proven_row_construction_origins_only=snapshot.hierarchy_row_origins,
    )
