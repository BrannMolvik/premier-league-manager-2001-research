"""Build the confirmed original TeamSelect background and action resources.

This binds the exact source backgrounds, TeamSelect 23-frame Back/Start atlas,
16 original hierarchy-row origins, and proven Back/Start control geometry.
It does not invent the hierarchy's country/league/club row mapping, button
source-frame interaction states, fonts, or placement of untraced sprites.
Those remain dependent on source-backed executable research.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_button_frames import (
    OriginalButtonAtlas,
    TEAMSELECT_BUTTON_ATLAS,
    decode_verified_original_button_atlas,
)
from original_teamselect_hierarchy_art import (
    HIERARCHY_ANIM_SPEC,
    HIERARCHY_BARS_SPEC,
    OriginalTeamSelectHierarchyArt,
    decode_verified_hierarchy_art,
)
from original_front_end_layout import (
    GLOBAL_BACKGROUND_PATH,
    TEAMSELECT_BACKGROUND_PATH,
    TEAMSELECT_HIERARCHY_ROW_ORIGINS,
    SCREEN_SIZE,
    compose_teamselect_background,
    TEAMSELECT_BACK_RECT,
    TEAMSELECT_START_RECT,
    TEAMSELECT_BACK_EVENT,
    TEAMSELECT_START_EVENT,
)


GLOBAL_BACKGROUND_SHA256 = (
    "9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9"
)
TEAMSELECT_BACKGROUND_SHA256 = (
    "7927bc3baf35f2ee906f6ea714c77d0e51282ee5316ec43220edb95ed358694b"
)
# Independently measured exact overlay of the real original 800x600 and
# 800x558 decoded .444 images; actions and text are deliberately absent.
TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256 = (
    "6a438ab60e96a3b53667fd1373ad24442d4272d50475a7c89108ac45dbe5f501"
)


class OriginalTeamSelectResourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalTeamSelectResources:
    background_rgba: bytes
    action_atlas: OriginalButtonAtlas
    hierarchy_row_origins: tuple[tuple[int, int], ...]
    hierarchy_art: OriginalTeamSelectHierarchyArt | None = None

    def __post_init__(self) -> None:
        if len(self.background_rgba) != SCREEN_SIZE[0] * SCREEN_SIZE[1] * 4:
            raise OriginalTeamSelectResourceError("TeamSelect requires 800x600 RGBA")
        if self.action_atlas.spec != TEAMSELECT_BUTTON_ATLAS:
            raise OriginalTeamSelectResourceError("Wrong original TeamSelect atlas")
        if len(self.action_atlas.frames) != TEAMSELECT_BUTTON_ATLAS.frame_count:
            raise OriginalTeamSelectResourceError("Missing original TeamSelect frames")
        if any(
            (f.width, f.height) != (
                TEAMSELECT_BUTTON_ATLAS.frame_width,
                TEAMSELECT_BUTTON_ATLAS.frame_height,
            )
            for f in self.action_atlas.frames
        ):
            raise OriginalTeamSelectResourceError(
                "Original TeamSelect frame geometry differs"
            )
        if self.hierarchy_row_origins != TEAMSELECT_HIERARCHY_ROW_ORIGINS:
            raise OriginalTeamSelectResourceError(
                "TeamSelect hierarchy row origins differ from executable"
            )
        if self.hierarchy_art is not None and not isinstance(
            self.hierarchy_art, OriginalTeamSelectHierarchyArt
        ):
            raise OriginalTeamSelectResourceError("Unverified hierarchy source art")

    @property
    def proven_actions(self) -> tuple[tuple[int, object], ...]:
        return (
            (TEAMSELECT_BACK_EVENT, TEAMSELECT_BACK_RECT),
            (TEAMSELECT_START_EVENT, TEAMSELECT_START_RECT),
        )


def assemble_original_teamselect_inputs(
    global_background: EA444DecodedImage,
    team_background: EA444DecodedImage,
    action_atlas: OriginalButtonAtlas,
    hierarchy_art: OriginalTeamSelectHierarchyArt | None = None,
) -> OriginalTeamSelectResources:
    """Compose only the two proven background layers and original atlas."""
    return OriginalTeamSelectResources(
        compose_teamselect_background(global_background, team_background),
        action_atlas,
        TEAMSELECT_HIERARCHY_ROW_ORIGINS,
        hierarchy_art,
    )


def _read_verified_art(
    original_art_dir: Path,
    source_path: str,
    expected_sha256: str,
) -> bytes:
    path = Path(original_art_dir) / source_path.removeprefix("FM2001_Art/")
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected_sha256:
        raise OriginalTeamSelectResourceError(
            f"Original TeamSelect resource checksum mismatch: {source_path}"
        )
    return data


def load_verified_original_teamselect_inputs(
    *, original_art_dir: Path, original_executable: Path
) -> OriginalTeamSelectResources:
    """Load actual original bytes; exact native action-frame states stay unknown."""
    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    base = decode_ea444(
        _read_verified_art(
            original_art_dir, GLOBAL_BACKGROUND_PATH, GLOBAL_BACKGROUND_SHA256
        ),
        tables=tables, quant=quant,
    )
    team = decode_ea444(
        _read_verified_art(
            original_art_dir,
            TEAMSELECT_BACKGROUND_PATH,
            TEAMSELECT_BACKGROUND_SHA256,
        ),
        tables=tables, quant=quant,
    )
    buttons = decode_verified_original_button_atlas(
        _read_verified_art(
            original_art_dir,
            TEAMSELECT_BUTTON_ATLAS.source_path,
            TEAMSELECT_BUTTON_ATLAS.source_sha256,
        ),
        spec=TEAMSELECT_BUTTON_ATLAS,
        tables=tables,
        quant=quant,
    )
    hierarchy_art = decode_verified_hierarchy_art(
        _read_verified_art(
            original_art_dir, HIERARCHY_ANIM_SPEC.path,
            HIERARCHY_ANIM_SPEC.source_sha256,
        ),
        _read_verified_art(
            original_art_dir, HIERARCHY_BARS_SPEC.path,
            HIERARCHY_BARS_SPEC.source_sha256,
        ),
        tables=tables,
        quant=quant,
    )
    result = assemble_original_teamselect_inputs(
        base, team, buttons, hierarchy_art,
    )
    if sha256(result.background_rgba).hexdigest() != (
        TEAMSELECT_COMPOSED_BACKGROUND_RGBA_SHA256
    ):
        raise OriginalTeamSelectResourceError(
            "Source-backed original TeamSelect background RGBA regression"
        )
    return result
