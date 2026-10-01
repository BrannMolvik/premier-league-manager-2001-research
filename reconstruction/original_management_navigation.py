"""Source-backed PMenu Calendar/Tables navigation panel identities.

These mappings come from the canonical executable's management panel factory
at 0x47AEC0 plus MSVC RTTI on each constructed panel. They identify concrete
original presentation classes and constructors; they do not claim complete
screen layout/resource fidelity.
"""
from __future__ import annotations

from dataclasses import dataclass


class OriginalManagementNavigationError(ValueError):
    pass


MANAGEMENT_PANEL_FACTORY_VA = 0x47AEC0
MANAGEMENT_PANEL_HIGH_DISPATCH_BYTE_TABLE_VA = 0x47CB14
MANAGEMENT_PANEL_HIGH_DISPATCH_TARGET_TABLE_VA = 0x47CAF4


@dataclass(frozen=True)
class OriginalManagementPanelIdentity:
    menu_id: int
    original_caption: str
    factory_case_va: int
    constructor_va: int
    panel_class: str
    type_descriptor_va: int
    vftable_va: int


CALENDAR_PANEL = OriginalManagementPanelIdentity(
    0x259,
    "Calendar",
    0x47C62B,
    0x47CCB0,
    "PCalendar2k",
    0x81CA18,
    0x7C2F04,
)
LEAGUE_TABLES_PANEL = OriginalManagementPanelIdentity(
    0x25A,
    "League Tables",
    0x47C6D1,
    0x448640,
    "PLeagueTables",
    0x81B458,
    0x7C00C8,
)
CUP_TABLES_PANEL = OriginalManagementPanelIdentity(
    0x25B,
    "Cup Tables",
    0x47C67E,
    0x44EC80,
    "PCupTable2000",
    0x81BA30,
    0x7C0A78,
)
LEAGUE_FIXTURES_PANEL = OriginalManagementPanelIdentity(
    0x25C,
    "League Fixtures",
    0x47C724,
    0x46D470,
    "PLeagueFixtures",
    0x81C550,
    0x7C24B8,
)

CALENDAR_TABLES_PANEL_IDENTITIES = (
    CALENDAR_PANEL,
    LEAGUE_TABLES_PANEL,
    CUP_TABLES_PANEL,
    LEAGUE_FIXTURES_PANEL,
)
_CALENDAR_TABLES_BY_MENU_ID = {
    panel.menu_id: panel for panel in CALENDAR_TABLES_PANEL_IDENTITIES
}


def calendar_tables_panel_identity(menu_id: int) -> OriginalManagementPanelIdentity:
    """Return only a source-proven panel identity for the requested PMenu ID."""
    if type(menu_id) is not int:
        raise OriginalManagementNavigationError("PMenu panel ID must be an integer")
    try:
        return _CALENDAR_TABLES_BY_MENU_ID[menu_id]
    except KeyError as exc:
        raise OriginalManagementNavigationError(
            f"PMenu panel ID {menu_id:#x} is not mapped in this recovered family"
        ) from exc
