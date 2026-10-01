"""Source-backed PMenu management-shell routing after TeamSelect.

The original executable does not enter a distinct generic "Manager Home" panel
on a fresh new game. TeamSelect Start finishes new-game construction, creates
PMenu, and PMenu selects an actual content-panel code from one neutral user
route-state dword. Fresh users initialize that dword to zero, which routes to
PSquadScreen.

This module records only the recovered route identities. It does not claim that
the complete PMenu chrome or target panels are visually reconstructed.
"""
from __future__ import annotations

from dataclasses import dataclass


class OriginalManagementShellError(ValueError):
    pass


PMENU_CLASS = "PMenu"
PMENU_TYPE_DESCRIPTOR_VA = 0x81CE80
PMENU_VFTABLE_VA = 0x7C3DE8
PMENU_CONSTRUCTOR_VA = 0x482830
PMENU_ROUTE_METHOD_VA = 0x482960
MANAGEMENT_PANEL_FACTORY_VA = 0x47AEC0

USER_ROUTE_STATE_OFFSET = 0x10E8
USER_ROUTE_STATE_GETTER_VA = 0x42C6A0
USER_ROUTE_STATE_SETTER_VA = 0x42C6B0
FRESH_USER_ROUTE_STATE_INITIALIZER_CALL_VA = 0x424F45
FRESH_USER_ROUTE_STATE = 0

SQUAD_PANEL_CODE = 0xCE
SQUAD_MENU_NODE_ID = 2
SQUAD_FACTORY_CASE_VA = 0x47AF2D
SQUAD_CONSTRUCTOR_VA = 0x4B8240
SQUAD_PANEL_CLASS = "PSquadScreen"
SQUAD_PANEL_TYPE_DESCRIPTOR_VA = 0x819D48
SQUAD_PANEL_VFTABLE_VA = 0x7C5CA4

LEAGUE_TABLE_PANEL_CODE = 0x25A
LEAGUE_TABLE_MENU_NODE_ID = 6
LEAGUE_TABLE_FACTORY_CASE_VA = 0x47C6D1
LEAGUE_TABLE_CONSTRUCTOR_VA = 0x448640
LEAGUE_TABLE_PANEL_CLASS = "PLeagueTables"
LEAGUE_TABLE_PANEL_TYPE_DESCRIPTOR_VA = 0x81B458
LEAGUE_TABLE_PANEL_VFTABLE_VA = 0x7C00C8


@dataclass(frozen=True)
class OriginalManagementRoute:
    user_route_state: int
    panel_code: int
    menu_node_id: int
    panel_class: str
    constructor_va: int
    vftable_va: int
    factory_case_va: int
    resets_user_route_state_to_zero: bool


def management_route_for_user_state(state: int) -> OriginalManagementRoute:
    """Mirror the source branch in PMenu::0x482960 without naming state meaning."""
    if type(state) is not int:
        raise OriginalManagementShellError("PMenu user route state must be an integer")

    if state == 1:
        return OriginalManagementRoute(
            state,
            LEAGUE_TABLE_PANEL_CODE,
            LEAGUE_TABLE_MENU_NODE_ID,
            LEAGUE_TABLE_PANEL_CLASS,
            LEAGUE_TABLE_CONSTRUCTOR_VA,
            LEAGUE_TABLE_PANEL_VFTABLE_VA,
            LEAGUE_TABLE_FACTORY_CASE_VA,
            True,
        )

    return OriginalManagementRoute(
        state,
        SQUAD_PANEL_CODE,
        SQUAD_MENU_NODE_ID,
        SQUAD_PANEL_CLASS,
        SQUAD_CONSTRUCTOR_VA,
        SQUAD_PANEL_VFTABLE_VA,
        SQUAD_FACTORY_CASE_VA,
        state != 0,
    )


def fresh_new_game_management_route() -> OriginalManagementRoute:
    """Return the source-proven first content panel for a newly created user."""
    return management_route_for_user_state(FRESH_USER_ROUTE_STATE)
