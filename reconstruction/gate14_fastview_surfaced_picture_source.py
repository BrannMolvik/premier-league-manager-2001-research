"""Source contract for the three outer FastView surfaced controls."""
from __future__ import annotations

from dataclasses import dataclass

SURFACED_PICTURE_CONSTRUCTOR_VA = 0x526940
FULL_SURFACE_OWNER_CALLSITE_VA = 0x51FD31
HOME_BADGE_OWNER_CALLSITE_VA = 0x520642
AWAY_BADGE_OWNER_CALLSITE_VA = 0x520697

FULL_SURFACE_RECT = (0, 0, 800, 600)
HOME_BADGE_RECT = (38, 1, 173, 94)
AWAY_BADGE_RECT = (627, 1, 762, 94)

MATCH_HOME_SIDE_OFFSET = 0x14
MATCH_AWAY_SIDE_OFFSET = 0x28
REAL_FIXTURE_HOME_CLUB_OFFSET = 0x0C
REAL_FIXTURE_AWAY_CLUB_OFFSET = 0x10

CLUB_ART_SELECTOR_VA = 0x40C850
CLUB_GRAPHICS_BASENAME_GETTER_VA = 0x40DA90
CLUB_GRAPHICS_BASENAME_OFFSET = 0xE0
COUNTRY_GRAPHICS_DIRECTORY_GETTER_VA = 0x411610
COUNTRY_GRAPHICS_DIRECTORY_OFFSET = 0x34

BADGE_FAMILY_ROOT = r"FM2001_Art\Generic\Team_badge_stills"
BADGE_VARIANT = "badge_2"
BADGE_GENERIC_FALLBACK = r"fm2001_art\generic\team_badge_stills\generic.444"

CLUB_BACKGROUND_SURFACE_FACTORY_VA = 0x5D3490
CLUB_BACKGROUND_SURFACE_BUILDER_VA = 0x5D3560
CLUB_BACKGROUND_SURFACE_GETTER_VA = 0x5D3510
TEAM_BACKGROUND_FAMILY_ROOT = r"FM2001_Art\Generic\Team_backgrounds"
TEAM_BACKGROUND_GENERIC_FALLBACK = r"fm2001_art\generic\Team_backgrounds\generic.444"


@dataclass(frozen=True)
class SurfacedControl:
    semantic: str
    rect: tuple[int, int, int, int]
    owner_callsite_va: int
    match_side_offset: int | None


SURFACED_CONTROLS = (
    SurfacedControl("match_club_background_surface", FULL_SURFACE_RECT,
                    FULL_SURFACE_OWNER_CALLSITE_VA, None),
    SurfacedControl("home_club_badge", HOME_BADGE_RECT,
                    HOME_BADGE_OWNER_CALLSITE_VA, MATCH_HOME_SIDE_OFFSET),
    SurfacedControl("away_club_badge", AWAY_BADGE_RECT,
                    AWAY_BADGE_OWNER_CALLSITE_VA, MATCH_AWAY_SIDE_OFFSET),
)


def badge_source_path(country_graphics_directory: str,
                      club_graphics_basename: str) -> str:
    if not country_graphics_directory or not club_graphics_basename:
        raise ValueError("source graphics path components must be non-empty")
    if any(x in country_graphics_directory for x in ("/", "\\")):
        raise ValueError("country graphics directory must be one component")
    if any(x in club_graphics_basename for x in ("/", "\\")):
        raise ValueError("club graphics basename must be one component")
    return (
        f"{BADGE_FAMILY_ROOT}\\{country_graphics_directory}\\"
        f"{club_graphics_basename}_{BADGE_VARIANT}.444"
    )


def surfaced_picture_source_contract() -> dict:
    return {
        "controls": SURFACED_CONTROLS,
        "fixture_home_club_offset": REAL_FIXTURE_HOME_CLUB_OFFSET,
        "fixture_away_club_offset": REAL_FIXTURE_AWAY_CLUB_OFFSET,
        "match_home_side_offset": MATCH_HOME_SIDE_OFFSET,
        "match_away_side_offset": MATCH_AWAY_SIDE_OFFSET,
        "badge_variant_source_closed": True,
        "badge_home_away_orientation_source_closed": True,
        "full_surface_club_background_ownership_source_closed": True,
        "full_surface_background_index_source_closed": False,
        "surfaced_picture_pixels_staged": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
