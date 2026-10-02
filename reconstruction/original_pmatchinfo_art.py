"""Source-proven screen placement for the PMatchInfo popup background.

The PMatchInfo presenter exposes several owner-local child resources. Their
nested owner transforms are not all recovered, so this module deliberately
promotes only the exact 760x500 info_popup background to screen coordinates.
Its parent origin uses the recovered PLeagueFixtures pointer clamp.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_MATCH_INFO_SIZE,
    league_fixtures_match_info_origin,
)
from original_pmatchinfo_presenter import (
    OriginalPMatchInfoStaticSnapshot,
    load_staged_pmatchinfo_snapshot,
)


class OriginalPMatchInfoArtError(ValueError):
    """The globally placeable PMatchInfo popup art is incomplete or ambiguous."""


@dataclass(frozen=True)
class OriginalPMatchInfoPopupArt:
    x: int
    y: int
    width: int
    height: int
    rgba: bytes

    def __post_init__(self) -> None:
        if (self.width, self.height) != LEAGUE_FIXTURES_MATCH_INFO_SIZE:
            raise OriginalPMatchInfoArtError(
                "PMatchInfo popup art must preserve the exact 760x500 dialog size"
            )
        if len(self.rgba) != self.width * self.height * 4:
            raise OriginalPMatchInfoArtError(
                "PMatchInfo popup RGBA payload does not match dialog geometry"
            )


def build_pmatchinfo_popup_art(
    snapshot: OriginalPMatchInfoStaticSnapshot,
    *,
    pointer_x: int,
    pointer_y: int,
) -> OriginalPMatchInfoPopupArt:
    """Project only source-global info_popup pixels into the 800x600 host."""
    if not isinstance(snapshot, OriginalPMatchInfoStaticSnapshot):
        raise OriginalPMatchInfoArtError(
            "PMatchInfo popup rendering requires a source-backed static snapshot"
        )
    if snapshot.dialog_size != LEAGUE_FIXTURES_MATCH_INFO_SIZE:
        raise OriginalPMatchInfoArtError(
            "PMatchInfo snapshot dialog size drifted from the recovered constructor"
        )
    if not snapshot.complete_dialog_background_available:
        raise OriginalPMatchInfoArtError(
            "PMatchInfo popup requires the exact info_popup.444 background"
        )

    matches = tuple(item for item in snapshot.art if item.resource_name == "info_popup")
    if len(matches) != 1:
        raise OriginalPMatchInfoArtError(
            "PMatchInfo snapshot must contain exactly one info_popup placement"
        )
    popup = matches[0]
    if popup.rect != (0, 0, *LEAGUE_FIXTURES_MATCH_INFO_SIZE):
        raise OriginalPMatchInfoArtError(
            "PMatchInfo info_popup placement drifted from its source-local rectangle"
        )
    if popup.source_size != LEAGUE_FIXTURES_MATCH_INFO_SIZE:
        raise OriginalPMatchInfoArtError(
            "PMatchInfo info_popup source size drifted from the recovered resource"
        )

    x, y = league_fixtures_match_info_origin(pointer_x, pointer_y)
    return OriginalPMatchInfoPopupArt(
        x=x,
        y=y,
        width=popup.rect[2],
        height=popup.rect[3],
        rgba=popup.rgba,
    )


def load_verified_pmatchinfo_popup_art(
    repo_root: str | Path,
    original_executable: str | Path,
    *,
    pointer_x: int,
    pointer_y: int,
) -> OriginalPMatchInfoPopupArt:
    """Decode verified staged PMatchInfo assets and return only the global popup."""
    snapshot = load_staged_pmatchinfo_snapshot(
        Path(repo_root),
        Path(original_executable),
        require_complete_dialog=True,
    )
    return build_pmatchinfo_popup_art(
        snapshot,
        pointer_x=pointer_x,
        pointer_y=pointer_y,
    )
