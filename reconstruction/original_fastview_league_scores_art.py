"""Exact placement seam for source-closed FastViewLeagueScores grid pixels."""
from __future__ import annotations

from dataclasses import dataclass

from ea444_decoder import EA444DecodedImage
from gate14_fastview_league_scores import CURRENT_FIX_GRID_1


class OriginalFastViewLeagueScoresArtError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalFastViewLeagueScoresPlacement:
    resource_name: str
    source_path: str
    owner_local_rect: tuple[int, int, int, int]
    rgba: bytes


@dataclass(frozen=True)
class OriginalFastViewLeagueScoresArt:
    current_fixture_grid: OriginalFastViewLeagueScoresPlacement
    screen_absolute_rect_recovered: bool = False
    score_composite_grid2_geometry_recovered: bool = False


def build_current_fixture_grid_art(
    decoded: EA444DecodedImage,
) -> OriginalFastViewLeagueScoresArt:
    if not isinstance(decoded, EA444DecodedImage):
        raise OriginalFastViewLeagueScoresArtError(
            "current fixture grid must be an EA444DecodedImage"
        )
    if (decoded.width, decoded.height) != CURRENT_FIX_GRID_1.size:
        raise OriginalFastViewLeagueScoresArtError(
            "current fixture grid decoded geometry mismatch"
        )
    if len(decoded.rgba) != decoded.width * decoded.height * 4:
        raise OriginalFastViewLeagueScoresArtError(
            "current fixture grid RGBA payload incomplete"
        )
    rect = CURRENT_FIX_GRID_1.owner_local_rect
    if rect is None:
        raise OriginalFastViewLeagueScoresArtError(
            "current fixture grid owner-local rectangle is unresolved"
        )
    return OriginalFastViewLeagueScoresArt(
        current_fixture_grid=OriginalFastViewLeagueScoresPlacement(
            resource_name=CURRENT_FIX_GRID_1.name,
            source_path=CURRENT_FIX_GRID_1.source_path,
            owner_local_rect=rect,
            rgba=decoded.rgba,
        )
    )
