"""Pure source-backed selection of FastView surfaced picture resources.

This layer maps one already-known match date and source club identities to the
three original surfaced-resource families. It does not read original bytes,
decode EA444, simulate a match, or infer the original Match +0x48 override.
Callers must supply that override state explicitly: None means the source
sentinel was absent and therefore the home club is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping

from gate14_fastview_surfaced_picture_source import (
    BADGE_GENERIC_FALLBACK,
    MASTER_CLUB_FAN_BASE_INDEX_OFFSET,
    badge_source_path,
    background_source_candidates,
    background_variant_for_month,
)


class FastViewSurfacedSelectionError(ValueError):
    pass


@dataclass(frozen=True)
class FastViewSurfacedClubArtSource:
    club_id: int
    country_id: int
    graphics_basename: str
    country_graphics_directory: str
    fan_base_index: int

    def __post_init__(self) -> None:
        if type(self.club_id) is not int or self.club_id < 0:
            raise FastViewSurfacedSelectionError("club_id must be non-negative integer")
        if type(self.country_id) is not int or self.country_id < 0:
            raise FastViewSurfacedSelectionError(
                "country_id must be non-negative integer"
            )
        if (
            not isinstance(self.graphics_basename, str)
            or not self.graphics_basename
            or "/" in self.graphics_basename
            or "\\" in self.graphics_basename
        ):
            raise FastViewSurfacedSelectionError(
                "club graphics basename must be one non-empty source component"
            )
        if (
            not isinstance(self.country_graphics_directory, str)
            or not self.country_graphics_directory
            or "/" in self.country_graphics_directory
            or "\\" in self.country_graphics_directory
        ):
            raise FastViewSurfacedSelectionError(
                "country graphics directory must be one non-empty source component"
            )
        if type(self.fan_base_index) is not int:
            raise FastViewSurfacedSelectionError(
                "fan_base_index must preserve the signed source integer"
            )


@dataclass(frozen=True)
class FastViewSurfacedResourceSelection:
    match_date: date
    home: FastViewSurfacedClubArtSource
    away: FastViewSurfacedClubArtSource
    background: FastViewSurfacedClubArtSource
    background_override_club_id: int | None
    background_variant: int
    background_source_candidates: tuple[str, str, str]
    home_badge_source_candidates: tuple[str, str]
    away_badge_source_candidates: tuple[str, str]
    background_terminal_fallback_recovered: bool = False
    source_bytes_loaded: bool = False
    ea444_decoded: bool = False
    complete_fastview_frame_recovered: bool = False

    def __post_init__(self) -> None:
        if type(self.match_date) is not date:
            raise FastViewSurfacedSelectionError("match_date must be exact date")
        if self.background.club_id != (
            self.home.club_id
            if self.background_override_club_id is None
            else self.background_override_club_id
        ):
            raise FastViewSurfacedSelectionError(
                "background club does not match explicit override-or-home rule"
            )
        if self.background_variant != background_variant_for_month(
            self.match_date.month
        ):
            raise FastViewSurfacedSelectionError(
                "background variant does not match source month table"
            )
        if len(self.background_source_candidates) != 3:
            raise FastViewSurfacedSelectionError(
                "background selection requires the three source attempts"
            )
        if (
            len(self.home_badge_source_candidates) != 2
            or len(self.away_badge_source_candidates) != 2
        ):
            raise FastViewSurfacedSelectionError(
                "badge selection requires exact club path plus generic fallback"
            )
        if (
            self.background_terminal_fallback_recovered
            or self.source_bytes_loaded
            or self.ea444_decoded
            or self.complete_fastview_frame_recovered
        ):
            raise FastViewSurfacedSelectionError(
                "resource selection cannot promote unresolved loading/frame fidelity"
            )


def _club_art_source(
    clubs: Mapping[int, object],
    countries: Mapping[int, object],
    club_id: int,
) -> FastViewSurfacedClubArtSource:
    if type(club_id) is not int or club_id < 0:
        raise FastViewSurfacedSelectionError(
            "club resource selection requires non-negative integer club id"
        )
    try:
        club = clubs[club_id]
    except (KeyError, TypeError) as exc:
        raise FastViewSurfacedSelectionError(
            f"club {club_id} is unavailable to surfaced-resource selection"
        ) from exc

    country_id = getattr(club, "country_id", None)
    if type(country_id) is not int or country_id < 0:
        raise FastViewSurfacedSelectionError(
            f"club {club_id} has no source-backed country id"
        )
    try:
        country = countries[country_id]
    except (KeyError, TypeError) as exc:
        raise FastViewSurfacedSelectionError(
            f"country {country_id} is unavailable to surfaced-resource selection"
        ) from exc

    basename = getattr(club, "graphics_basename", None)
    directory = getattr(country, "graphics_directory", None)
    fan_base_index = getattr(club, "fan_base_index", None)

    try:
        return FastViewSurfacedClubArtSource(
            club_id=club_id,
            country_id=country_id,
            graphics_basename=basename,
            country_graphics_directory=directory,
            fan_base_index=fan_base_index,
        )
    except FastViewSurfacedSelectionError as exc:
        raise FastViewSurfacedSelectionError(
            f"club {club_id} lacks exact original art-selection fields"
        ) from exc


def _badge_candidates(source: FastViewSurfacedClubArtSource) -> tuple[str, str]:
    return (
        badge_source_path(
            source.country_graphics_directory,
            source.graphics_basename,
        ),
        BADGE_GENERIC_FALLBACK,
    )


def build_fastview_surfaced_resource_selection(
    *,
    match_date: date,
    clubs: Mapping[int, object],
    countries: Mapping[int, object],
    home_club_id: int,
    away_club_id: int,
    background_club_override_id: int | None,
) -> FastViewSurfacedResourceSelection:
    """Resolve exact resource attempts from already-reconstructed match state.

    background_club_override_id is intentionally required. Passing None means
    the caller knows the original-equivalent override is absent, so 0x514220's
    source fallback selects the home side. Omitting/guessing that state is not
    permitted by this seam.
    """
    if type(match_date) is not date:
        raise FastViewSurfacedSelectionError("match_date must be exact date")
    if background_club_override_id is not None and (
        type(background_club_override_id) is not int
        or background_club_override_id < 0
    ):
        raise FastViewSurfacedSelectionError(
            "background override must be non-negative integer or explicit None"
        )

    home = _club_art_source(clubs, countries, int(home_club_id))
    away = _club_art_source(clubs, countries, int(away_club_id))
    background_id = (
        home.club_id
        if background_club_override_id is None
        else int(background_club_override_id)
    )
    background = _club_art_source(clubs, countries, background_id)
    variant = background_variant_for_month(match_date.month)

    return FastViewSurfacedResourceSelection(
        match_date=match_date,
        home=home,
        away=away,
        background=background,
        background_override_club_id=background_club_override_id,
        background_variant=variant,
        background_source_candidates=background_source_candidates(
            background.country_graphics_directory,
            background.graphics_basename,
            match_date.month,
            background.fan_base_index,
        ),
        home_badge_source_candidates=_badge_candidates(home),
        away_badge_source_candidates=_badge_candidates(away),
    )


def surfaced_resource_selection_contract() -> dict:
    return {
        "master_fan_base_index_offset": MASTER_CLUB_FAN_BASE_INDEX_OFFSET,
        "cleanroom_fan_base_field": "Club.fan_base_index",
        "match_date_required": True,
        "home_club_required": True,
        "away_club_required": True,
        "background_override_state_required": True,
        "background_none_means_source_override_absent": True,
        "background_selector_bound_to_cleanroom_state": True,
        "badge_selector_bound_to_cleanroom_state": True,
        "source_bytes_loaded": False,
        "ea444_decoded": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
