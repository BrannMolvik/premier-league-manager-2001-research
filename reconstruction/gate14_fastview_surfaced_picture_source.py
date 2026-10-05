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

GAME_DATE_SERIAL_GLOBAL_VA = 0x9847FC
DATE_SPLIT_HELPER_VA = 0x64CCD0
BACKGROUND_MONTH_TABLE_VA = 0x83339C
BACKGROUND_VARIANT_BY_MONTH = (
    None,
    2, 2, 3, 3,
    0, 0, 0, 0,
    1, 1, 1,
    2,
)

MATCH_BACKGROUND_CLUB_OVERRIDE_OFFSET = 0x48
MATCH_BACKGROUND_CLUB_HELPER_VA = 0x514220

BACKGROUND_CLIENT_CACHE_BASE_VA = 0x87AC68
BACKGROUND_CLIENT_CACHE_COUNT = 2
BACKGROUND_CLIENT_CACHE_STRIDE = 0x0C
FASTVIEW_BACKGROUND_CLIENT_CACHE_INDEX = 1

BACKGROUND_RESOURCE_POOL_VA = 0x87AC30
BACKGROUND_RESOURCE_POOL_CAPACITY = 2
BACKGROUND_RESOURCE_SLOT_STRIDE = 0x18
BACKGROUND_RESOURCE_SLOT_ACTIVE_OFFSET = 0x04
BACKGROUND_RESOURCE_SLOT_REFCOUNT_OFFSET = 0x08
BACKGROUND_RESOURCE_SLOT_CLUB_KEY_OFFSET = 0x0C
BACKGROUND_RESOURCE_SLOT_VARIANT_KEY_OFFSET = 0x10
BACKGROUND_RESOURCE_SLOT_OBJECT_OFFSET = 0x18

DBRCLUB_BACKGROUND_TIER_SOURCE_OFFSET = 0x70
COMPACT_CLUB_READER_VA = 0x4022D0
RUNTIME_CLUB_IMPORT_VA = 0x403660
MASTER_CLUB_FAN_BASE_INDEX_OFFSET = 94


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


def background_variant_for_month(month: int) -> int:
    if type(month) is not int or not 1 <= month <= 12:
        raise ValueError("month must be an integer in 1..12")
    value = BACKGROUND_VARIANT_BY_MONTH[month]
    assert value is not None
    return value


def generic_background_tier(raw_club_70: int) -> int:
    """Mirror the signed DBRClub+0x70 fallback thresholds."""
    if type(raw_club_70) is not int:
        raise ValueError("raw DBRClub+0x70 value must be an integer")
    if raw_club_70 > 20:
        return 0
    if raw_club_70 <= 8:
        return 2
    return 1


def background_source_candidates(
    country_graphics_directory: str,
    club_graphics_basename: str,
    month: int,
    raw_club_70: int,
) -> tuple[str, str, str]:
    """Return the exact source-attempt order for the active month."""
    if not country_graphics_directory or not club_graphics_basename:
        raise ValueError("source graphics path components must be non-empty")
    if any(x in country_graphics_directory for x in ("/", "\\")):
        raise ValueError("country graphics directory must be one component")
    if any(x in club_graphics_basename for x in ("/", "\\")):
        raise ValueError("club graphics basename must be one component")

    variant = background_variant_for_month(month)
    tier = generic_background_tier(raw_club_70)
    club_root = (
        f"{TEAM_BACKGROUND_FAMILY_ROOT}\\{country_graphics_directory}\\"
        f"{club_graphics_basename}"
    )
    return (
        f"{club_root}_background{variant}.444",
        f"{club_root}_background.444",
        f"{TEAM_BACKGROUND_FAMILY_ROOT}\\generic{tier}_background{variant}.444",
    )


def background_client_cache_address(client_index: int) -> int:
    if type(client_index) is not int or not 0 <= client_index < BACKGROUND_CLIENT_CACHE_COUNT:
        raise ValueError("background client cache index is outside the source two-entry array")
    return BACKGROUND_CLIENT_CACHE_BASE_VA + (
        client_index * BACKGROUND_CLIENT_CACHE_STRIDE
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
        "full_surface_background_club_rule": "match_plus_0x48_override_else_home_side",
        "full_surface_background_index_source_closed": True,
        "background_variant_by_month": BACKGROUND_VARIANT_BY_MONTH,
        "background_client_cache_index": FASTVIEW_BACKGROUND_CLIENT_CACHE_INDEX,
        "background_client_cache_address": background_client_cache_address(
            FASTVIEW_BACKGROUND_CLIENT_CACHE_INDEX
        ),
        "background_resource_pool_capacity": BACKGROUND_RESOURCE_POOL_CAPACITY,
        "background_cache_key": ("club_identity", "background_variant"),
        "background_cache_reuses_matching_pool_entry": True,
        "background_cache_reference_counted": True,
        "background_club_attempt_order": (
            "backgroundN",
            "background",
            "genericTier_backgroundN",
        ),
        "background_generic_tier_source_offset": DBRCLUB_BACKGROUND_TIER_SOURCE_OFFSET,
        "background_generic_tier_master_offset": MASTER_CLUB_FAN_BASE_INDEX_OFFSET,
        "background_generic_tier_cleanroom_field": "Club.fan_base_index",
        "surfaced_picture_pixels_staged": False,
        "complete_fastview_frame_recovered": False,
        "gate14_complete": False,
    }
