"""Source-backed supplied-state text binding for PPreMatchPanel.

PPreMatch refresh 0x49A610 builds four dynamic visible strings: fixture header,
date/weather, and the two team identity labels. This module reproduces only
those already source-closed formatting/dataflow rules. It does not rasterize
text, choose a match, or promote complete-frame fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from gate14_fastview_surfaced_picture_selection import (
    FastViewSurfacedResourceSelection,
)
from original_prematch_panel import (
    PREMATCH_DATE_FORMAT,
    PREMATCH_DATE_WEATHER_FORMAT,
    PREMATCH_FIXTURE_HEADER_FORMAT,
    PREMATCH_FRIENDLY_LABEL,
    PREMATCH_VERSUS_LABEL,
    PREMATCH_WEATHER_LABELS,
    PREMATCH_WEATHER_TEMPERATURE_FORMAT,
)


class PrematchTextBindingError(ValueError):
    pass


PREMATCH_REFRESH_VA = 0x49A610
PREMATCH_TEAM_DISPLAY_NAME_GETTER_VA = 0x40DA70
PREMATCH_TEAM_DISPLAY_RUNTIME_OVERRIDE_HELPER_VA = 0x403600
PREMATCH_TEAM_SHORT_NAME_RUNTIME_OFFSET = 0x0C
PREMATCH_STADIUM_DISPLAY_GETTER_VA = 0x514270
PREMATCH_STADIUM_NA_LITERALS = ("N/A", "NA")
PREMATCH_STADIUM_SHORT_NAME_FALLBACK_OFFSET = 0x0C
PREMATCH_DATE_FORMATTER_VA = 0x64D150
PREMATCH_DATE_MONTH_NAME_HELPER_VA = 0x64D140
PREMATCH_DATE_SUFFIX_TABLE_VA = 0x84A024
PREMATCH_DATE_MONTH_TABLE_VA = 0x84A030

# Exact English entries addressed by the native language globals used by
# 0x64D150 for %Df / %Mf. The suffix table order is th, st, nd, rd.
PREMATCH_ORDINAL_SUFFIXES = ("th", "st", "nd", "rd")
PREMATCH_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)


@dataclass(frozen=True)
class BoundPrematchDynamicText:
    fixture_header: str
    date_weather: str
    home_team_identity: str
    versus: str
    away_team_identity: str
    stadium_display_name: str
    competition_display_name: str
    weather_label: str
    source_state_bound: bool = True
    text_pixels_rasterized: bool = False
    complete_prematch_frame: bool = False
    gate14_complete: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "fixture_header",
            "date_weather",
            "home_team_identity",
            "versus",
            "away_team_identity",
            "stadium_display_name",
            "competition_display_name",
            "weather_label",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value:
                raise PrematchTextBindingError(
                    f"{field_name} must be a non-empty source string"
                )
        if self.versus != PREMATCH_VERSUS_LABEL:
            raise PrematchTextBindingError("pre-match versus label drifted")
        if (
            not self.source_state_bound
            or self.text_pixels_rasterized
            or self.complete_prematch_frame
            or self.gate14_complete
        ):
            raise PrematchTextBindingError(
                "dynamic text binding cannot promote raster/frame/gate claims"
            )


def _required_text(obj: object, field: str) -> str:
    value = getattr(obj, field, None)
    if not isinstance(value, str) or not value:
        raise PrematchTextBindingError(
            f"pre-match source object requires non-empty {field}"
        )
    return value


def format_prematch_source_date(value) -> str:
    """Reproduce native %Df %Mf %Yf for the supplied Python date."""
    try:
        day = int(value.day)
        month = int(value.month)
        year = int(value.year)
    except (AttributeError, TypeError, ValueError) as exc:
        raise PrematchTextBindingError("pre-match date must expose day/month/year") from exc
    if not 1 <= month <= 12 or not 1 <= day <= 31:
        raise PrematchTextBindingError("pre-match date fields are outside native bounds")

    last_digit = day % 10
    tens_digit = (day % 100) // 10
    suffix_index = last_digit if last_digit <= 3 and tens_digit != 1 else 0
    suffix = PREMATCH_ORDINAL_SUFFIXES[suffix_index]
    return f"{day}{suffix} {PREMATCH_MONTH_NAMES[month - 1]} {year}"


def source_prematch_stadium_display_name(club: object) -> str:
    """Reproduce 0x514270's stadium string with exact N/A / NA fallback."""
    stadium = _required_text(club, "stadium")
    if stadium in PREMATCH_STADIUM_NA_LITERALS:
        return _required_text(club, "short_name")
    return stadium


def source_prematch_team_display_name(
    club: object,
    *,
    runtime_override: str | None,
) -> str:
    """Reproduce 0x40DA70's ordinary short-name fallback.

    0x40DA70 first asks 0x403600 for a runtime/network display override. The
    clean-room seam requires callers to state that supplied override explicitly;
    None means that helper produced no non-empty override and the native
    DBRClub +0x0C short-name field is used.
    """
    if runtime_override is not None:
        if not isinstance(runtime_override, str) or not runtime_override:
            raise PrematchTextBindingError(
                "team display override must be non-empty string or explicit None"
            )
        return runtime_override
    return _required_text(club, "short_name")


def build_prematch_dynamic_text(
    selection: FastViewSurfacedResourceSelection,
    *,
    clubs: Mapping[int, object],
    competition_name: str | None,
    weather_code: int,
    temperature_c: int,
    home_team_name_override: str | None,
    away_team_name_override: str | None,
) -> BoundPrematchDynamicText:
    """Bind PPreMatch's four dynamic text controls from supplied match state."""
    if type(selection) is not FastViewSurfacedResourceSelection:
        raise PrematchTextBindingError(
            "dynamic text binding requires exact surfaced-resource selection"
        )
    if type(weather_code) is not int or isinstance(weather_code, bool):
        raise PrematchTextBindingError("weather code must be exact integer")
    if not 0 <= weather_code < len(PREMATCH_WEATHER_LABELS):
        raise PrematchTextBindingError("weather code must be in native 0..4 range")
    if type(temperature_c) is not int or isinstance(temperature_c, bool):
        raise PrematchTextBindingError("temperature must be exact signed integer")
    if not -128 <= temperature_c <= 127:
        raise PrematchTextBindingError("temperature must fit native signed byte")

    try:
        home = clubs[selection.home.club_id]
        away = clubs[selection.away.club_id]
        stadium_club = clubs[selection.background.club_id]
    except (KeyError, TypeError) as exc:
        raise PrematchTextBindingError(
            "pre-match text binding is missing a source club"
        ) from exc

    if competition_name is None:
        competition_display = PREMATCH_FRIENDLY_LABEL
    elif isinstance(competition_name, str) and competition_name:
        competition_display = competition_name
    else:
        raise PrematchTextBindingError(
            "competition name must be non-empty string or explicit None for Friendly"
        )

    stadium_display = source_prematch_stadium_display_name(stadium_club)
    weather_label = PREMATCH_WEATHER_LABELS[weather_code]
    date_text = format_prematch_source_date(selection.match_date)
    weather_temperature = f"{weather_label} {temperature_c}°C"

    fixture_header = PREMATCH_FIXTURE_HEADER_FORMAT.replace(
        "%s", "{}", 1
    ).replace("%s", "{}", 1).format(
        competition_display,
        stadium_display,
    )
    date_weather = PREMATCH_DATE_WEATHER_FORMAT.replace(
        "%s", "{}", 1
    ).replace("%s", "{}", 1).format(
        date_text,
        weather_temperature,
    )

    return BoundPrematchDynamicText(
        fixture_header=fixture_header,
        date_weather=date_weather,
        home_team_identity=source_prematch_team_display_name(
            home,
            runtime_override=home_team_name_override,
        ),
        versus=PREMATCH_VERSUS_LABEL,
        away_team_identity=source_prematch_team_display_name(
            away,
            runtime_override=away_team_name_override,
        ),
        stadium_display_name=stadium_display,
        competition_display_name=competition_display,
        weather_label=weather_label,
    )


def prematch_text_binding_contract() -> dict:
    return {
        "refresh_va": PREMATCH_REFRESH_VA,
        "fixture_header_format": PREMATCH_FIXTURE_HEADER_FORMAT,
        "date_format": PREMATCH_DATE_FORMAT,
        "weather_temperature_format": PREMATCH_WEATHER_TEMPERATURE_FORMAT,
        "date_weather_format": PREMATCH_DATE_WEATHER_FORMAT,
        "team_display_name_getter_va": PREMATCH_TEAM_DISPLAY_NAME_GETTER_VA,
        "team_runtime_override_helper_va": PREMATCH_TEAM_DISPLAY_RUNTIME_OVERRIDE_HELPER_VA,
        "team_short_name_runtime_offset": PREMATCH_TEAM_SHORT_NAME_RUNTIME_OFFSET,
        "stadium_display_getter_va": PREMATCH_STADIUM_DISPLAY_GETTER_VA,
        "stadium_na_literals": PREMATCH_STADIUM_NA_LITERALS,
        "stadium_short_name_fallback_offset": PREMATCH_STADIUM_SHORT_NAME_FALLBACK_OFFSET,
        "date_formatter_va": PREMATCH_DATE_FORMATTER_VA,
        "date_month_name_helper_va": PREMATCH_DATE_MONTH_NAME_HELPER_VA,
        "date_suffix_table_va": PREMATCH_DATE_SUFFIX_TABLE_VA,
        "date_month_table_va": PREMATCH_DATE_MONTH_TABLE_VA,
        "ordinal_suffixes": PREMATCH_ORDINAL_SUFFIXES,
        "month_names": PREMATCH_MONTH_NAMES,
        "weather_labels": PREMATCH_WEATHER_LABELS,
        "dynamic_text_state_binding_available": True,
        "text_pixels_rasterized": False,
        "complete_prematch_frame": False,
        "gate14_complete": False,
    }
