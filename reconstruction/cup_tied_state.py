"""Exact clean-room projection of FM2001 CCupTiedPlayer lookup semantics.

The canonical executable stores Cup-Tied state separately from DBRPlayer flags.
Each CCupTiedPlayer record carries a player ID and the club/team ID for which
that player is tied. Lookup 0x4E9710 returns true only when a record exists for
that player and the stored tied-club ID differs from the team currently asking
whether the player may be fielded.

This module intentionally contains only that proven record/lookup contract.
Record creation/removal lifecycle and competition ownership are separate
source-recovery tasks and must not be inferred here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CUP_TIED_LOOKUP_VA = 0x4E9710
COMPETITION_CUP_TIED_LOOKUP_VA = 0x4F8E40


class CupTiedStateError(ValueError):
    """The recovered Cup-Tied record contract cannot be represented safely."""


@dataclass(frozen=True)
class CupTiedPlayerRecord:
    player_id: int
    tied_club_id: int

    def __post_init__(self) -> None:
        if type(self.player_id) is not int:
            raise CupTiedStateError("Cup-Tied player ID must be an integer")
        if type(self.tied_club_id) is not int:
            raise CupTiedStateError("Cup-Tied club ID must be an integer")


def player_is_cup_tied(
    records: Iterable[CupTiedPlayerRecord],
    *,
    player_id: int,
    team_id: int,
) -> bool:
    """Mirror 0x4E9710's recovered player/team comparison.

    A matching record tied to the same team does not block that team. A
    matching record tied to a different team does. No matching record means
    the player is not Cup-Tied for this lookup.
    """
    if type(player_id) is not int or type(team_id) is not int:
        raise CupTiedStateError("Cup-Tied lookup IDs must be integers")

    for record in tuple(records):
        if not isinstance(record, CupTiedPlayerRecord):
            raise CupTiedStateError(
                "Cup-Tied lookup requires recovered CupTiedPlayerRecord values"
            )
        if record.player_id == player_id:
            return record.tied_club_id != team_id
    return False
