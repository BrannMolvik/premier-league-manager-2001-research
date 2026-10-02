"""Source-backed PLeagueTables selector and table-header shell.

Recovery 161 starts the League Tables presentation recovery from the canonical
FM2001 executable.  This module records only bounded source facts from
PLeagueTables::0x446F00 / 0x448640 / 0x448C40 and the complete English loader.
It does not yet claim secondary-selector semantics, row composition, sorting,
or original graphic-resource ownership.
"""
from __future__ import annotations

from dataclasses import dataclass

from original_management_navigation import LEAGUE_TABLES_PANEL


class OriginalLeagueTablesError(ValueError):
    pass


LEAGUE_TABLES_CLASS = "PLeagueTables"
LEAGUE_TABLES_CONSTRUCTOR_VA = 0x448640
LEAGUE_TABLES_SETUP_VA = 0x446F00
LEAGUE_TABLES_EVENT_VA = 0x448C40
LEAGUE_TABLES_VFTABLE_VA = 0x7C00C8
LEAGUE_TABLES_TYPE_DESCRIPTOR_VA = 0x81B458

LEAGUE_TABLES_SELECTOR_CLASS = "fmRadioTextSm@fm2001_ctrls"
LEAGUE_TABLES_SELECTOR_CONSTRUCTOR_VA = 0x5D4B50
LEAGUE_TABLES_SELECTOR_SETUP_VA = 0x5D4C70
LEAGUE_TABLES_SELECTOR_STRIDE = 0x4C

LEAGUE_TABLES_ACTIVE_COUNTRY_INDEX_OFFSET = 0x64
LEAGUE_TABLES_COUNTRY_ID_BASE_OFFSET = 0x1D4
LEAGUE_TABLES_COUNTRY_CONTROL_BASE_OFFSET = 0x23C
LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT = 8
LEAGUE_TABLES_COUNTRY_EVENT_FIRST = 1

# Constructor writes these eight literal country identities in this exact
# source order at object+0x1D4..+0x1F0.
LEAGUE_TABLES_COUNTRY_IDS = (26, 33, 40, 73, 66, 31, 24, 9)
LEAGUE_TABLES_COUNTRY_NAMES = (
    "England",
    "Germany",
    "Italy",
    "Spain",
    "Scotland",
    "France",
    "Holland",
    "Belgium",
)
LEAGUE_TABLES_COUNTRY_SETUP_CALLS = (
    0x446FE5,
    0x447044,
    0x4470A5,
    0x447103,
    0x447164,
    0x4471C4,
    0x447227,
    0x44728F,
)

# The same constructor allocates two additional fmRadioTextSm families.  Keep
# them neutral until their data producers/event meanings are independently
# traced.
LEAGUE_TABLES_SECONDARY_SELECTOR_BASE_OFFSET = 0x4E4
LEAGUE_TABLES_SECONDARY_SELECTOR_COUNT = 5
LEAGUE_TABLES_SECONDARY_SETUP_CALLS = (
    0x447306,
    0x447353,
    0x4473A1,
    0x4473F2,
    0x447440,
)
LEAGUE_TABLES_TERTIARY_SELECTOR_BASE_OFFSET = 0x6A8
LEAGUE_TABLES_TERTIARY_SELECTOR_COUNT = 2
LEAGUE_TABLES_TERTIARY_SETUP_CALLS = (0x4474B5, 0x447501)

LEAGUE_TABLES_COUNTRY_HEADER_CONTROL_OFFSET = 0x1F4
LEAGUE_TABLES_COUNTRY_HEADER_SETUP_VA = 0x5D6090
LEAGUE_TABLES_COUNTRY_HEADER_CALL_VA = 0x446F92
LEAGUE_TABLES_COUNTRY_HEADER_X = 27
LEAGUE_TABLES_COUNTRY_HEADER_WIDTH = 150
LEAGUE_TABLES_COUNTRY_HEADER_GLOBAL_VA = 0x982670
LEAGUE_TABLES_COUNTRY_HEADER_ENGLISH_INDEX = 2146
LEAGUE_TABLES_COUNTRY_HEADER_TEXT = "Country"

LEAGUE_TABLES_TEXT_SETUP_VA = 0x6503F0
LEAGUE_TABLES_HEADER_Y = 152
LEAGUE_TABLES_HEADER_HEIGHT = 19


@dataclass(frozen=True)
class OriginalLeagueTablesHeaderText:
    label: str | None
    english_global_va: int | None
    english_index: int | None
    setup_call_va: int
    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self) -> tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)


LEAGUE_TABLES_HEADER_TEXTS = (
    OriginalLeagueTablesHeaderText(
        None, None, None, 0x447594, 316, 152, 214, 19
    ),
    OriginalLeagueTablesHeaderText(
        "P", 0x9830F4, 1473, 0x4475D7, 532, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "W", 0x9830F0, 1474, 0x44761A, 561, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "D", 0x9830EC, 1475, 0x44765D, 590, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "L", 0x9830E8, 1476, 0x4476A0, 619, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "F", 0x9830E4, 1477, 0x4476E3, 648, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "A", 0x9830E0, 1478, 0x447726, 677, 152, 27, 19
    ),
    OriginalLeagueTablesHeaderText(
        "Pts", 0x9830DC, 1479, 0x447769, 706, 152, 27, 19
    ),
)


def league_tables_country_event_index(event_id: int) -> int:
    """Map only source-proven country events 1..8 to selector indices."""
    if type(event_id) is not int:
        raise OriginalLeagueTablesError("League Tables event ID must be an integer")
    index = event_id - LEAGUE_TABLES_COUNTRY_EVENT_FIRST
    if not 0 <= index < LEAGUE_TABLES_COUNTRY_SELECTOR_COUNT:
        raise OriginalLeagueTablesError(
            f"League Tables event {event_id} is not a recovered country selector"
        )
    return index


def league_tables_country_identity(event_id: int) -> tuple[int, str]:
    index = league_tables_country_event_index(event_id)
    return LEAGUE_TABLES_COUNTRY_IDS[index], LEAGUE_TABLES_COUNTRY_NAMES[index]


def assert_league_tables_identity_contract() -> None:
    if (
        LEAGUE_TABLES_PANEL.panel_class != LEAGUE_TABLES_CLASS
        or LEAGUE_TABLES_PANEL.constructor_va != LEAGUE_TABLES_CONSTRUCTOR_VA
        or LEAGUE_TABLES_PANEL.type_descriptor_va != LEAGUE_TABLES_TYPE_DESCRIPTOR_VA
        or LEAGUE_TABLES_PANEL.vftable_va != LEAGUE_TABLES_VFTABLE_VA
    ):
        raise OriginalLeagueTablesError(
            "League Tables shell requires the source-proven PLeagueTables identity"
        )
