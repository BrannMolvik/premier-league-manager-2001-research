from __future__ import annotations

from typing import Protocol, Sequence, TypeVar


class MatchSelectionPlayer(Protocol):
    club_id: int
    match_active: bool
    match_substitute_available: bool


PlayerT = TypeVar("PlayerT", bound=MatchSelectionPlayer)


def collect_match_participants(
    team_club_id: int,
    ordered_roster: Sequence[PlayerT],
) -> tuple[PlayerT, ...]:
    """Clean-room equivalent of the filtering behavior in 0x510CD0.

    The original walks the team's player-ID array in stored roster order,
    resolves each ID to a DBRPlayer, and includes that player when the
    team-specific active predicate 0x417F50 or substitute predicate 0x417F60
    succeeds. Both predicates first require the player to belong to the team.

    This function intentionally does not choose a lineup. It only materializes
    the participant list from already-established runtime selection flags.
    """
    club_id = int(team_club_id)
    participants: list[PlayerT] = []

    for player in ordered_roster:
        if int(player.club_id) != club_id:
            continue
        if bool(player.match_active) or bool(player.match_substitute_available):
            participants.append(player)

    return tuple(participants)
