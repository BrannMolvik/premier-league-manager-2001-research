from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class CupTiedEntry:
    """Clean-room representation of the verified CCupTiedPlayer payload."""

    player_id: int
    club_id: int

    def __post_init__(self) -> None:
        for name in ("player_id", "club_id"):
            value = int(getattr(self, name))
            if not 0 <= value <= 0xFFFF:
                raise ValueError(f"{name} must fit the original uint16 field")
            object.__setattr__(self, name, value)


def find_cup_tied_entry(
    entries: Sequence[CupTiedEntry],
    player_id: int,
) -> CupTiedEntry | None:
    """Equivalent of collection helper 0x4E96E0."""
    target = int(player_id)
    for entry in entries:
        if int(entry.player_id) == target:
            return entry
    return None


def is_cup_tied(
    entries: Sequence[CupTiedEntry],
    player_id: int,
    team_id: int,
) -> bool:
    """Exact Boolean behavior of CCupTiedPlayer lookup 0x4E9710."""
    entry = find_cup_tied_entry(entries, player_id)
    if entry is None:
        return False
    return int(entry.club_id) != int(team_id)


class BaseAvailabilityPlayer(Protocol):
    club_id: int
    injured: bool
    suspended: bool
    selection_excluded: bool


def base_lineup_eligible(
    player: BaseAvailabilityPlayer,
    team_club_id: int,
) -> bool:
    """Proven first-stage availability behavior from 0x418050.

    This intentionally stops before competition/context-specific registration
    checks and the separate bit-11 restriction. Those are distinct layers in
    the executable and must not be silently treated as resolved here.
    """
    if int(player.club_id) != int(team_club_id):
        return False
    if bool(player.injured):
        return False
    if bool(player.suspended):
        return False
    if bool(player.selection_excluded):
        return False
    return True


def lineup_eligible_with_cup_tie(
    player: BaseAvailabilityPlayer,
    player_id: int,
    team_club_id: int,
    cup_tied_entries: Sequence[CupTiedEntry],
    *,
    apply_cup_tied_check: bool,
) -> bool:
    """Compose the proven base filter with the verified cup-tied predicate.

    apply_cup_tied_check is explicit because 0x418050 only reaches its
    competition-registration branch under additional runtime/context state
    that is not fully named yet.
    """
    if not base_lineup_eligible(player, team_club_id):
        return False
    if apply_cup_tied_check and is_cup_tied(
        cup_tied_entries,
        player_id,
        team_club_id,
    ):
        return False
    return True
