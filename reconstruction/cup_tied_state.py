"""Exact FM2001 Cup-Tied root-competition state.

Source recovery:
- 0x4F3DC0 walks parent competitions to the root.
- root virtual +0x18 enables Cup/DummyLeague contexts and rejects League roots.
- 0x4E9690 inserts a (player ID, club ID) record only when that player has no
  existing record.
- 0x4E9710 reports tied only when the stored club differs from the queried club.

This module deliberately models that collection separately from RuntimePlayer
status bits.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol


RUNTIME_KIND_LEAGUE = 1
RUNTIME_KIND_CUP = 2
RUNTIME_KIND_DUMMY_LEAGUE = 3


class CompetitionParentSource(Protocol):
    id: int
    runtime_kind_code: int
    parent_competition_id: int | None


@dataclass(frozen=True)
class CupTiedPlayerRecord:
    """One original 0x4E95D0 two-word Cup-Tied record."""

    player_id: int
    club_id: int


@dataclass
class CupTiedPlayerCollection:
    """Root-competition collection with original first-record-wins semantics."""

    records: list[CupTiedPlayerRecord] = field(default_factory=list)

    def record_appearance(self, player_id: int, club_id: int) -> bool:
        """Insert only the first record for a player, matching 0x4E9690.

        Returns True when a record was created and False when the player was
        already present. Existing club identity is never overwritten.
        """
        player_id = int(player_id)
        club_id = int(club_id)
        if any(int(record.player_id) == player_id for record in self.records):
            return False
        self.records.append(
            CupTiedPlayerRecord(player_id=player_id, club_id=club_id)
        )
        return True

    def recorded_club_id(self, player_id: int) -> int | None:
        player_id = int(player_id)
        for record in self.records:
            if int(record.player_id) == player_id:
                return int(record.club_id)
        return None

    def is_cup_tied(self, player_id: int, current_club_id: int) -> bool:
        """Reproduce 0x4E9710: absent/same club false, different club true."""
        recorded_club_id = self.recorded_club_id(int(player_id))
        return bool(
            recorded_club_id is not None
            and int(recorded_club_id) != int(current_club_id)
        )


def root_competition_id(
    competition_id: int,
    competitions: Mapping[int, CompetitionParentSource],
) -> int:
    """Reproduce 0x4F3DC0's parent walk and fail closed on malformed graphs."""
    current_id = int(competition_id)
    seen: set[int] = set()
    while True:
        if current_id in seen:
            raise RuntimeError("competition parent graph contains a cycle")
        seen.add(current_id)
        competition = competitions.get(current_id)
        if competition is None:
            raise KeyError(current_id)
        parent_id = getattr(competition, "parent_competition_id", None)
        if parent_id is None:
            return current_id
        current_id = int(parent_id)


def cup_tied_root_competition_id(
    competition_id: int,
    competitions: Mapping[int, CompetitionParentSource],
) -> int | None:
    """Return the root whose virtual +0x18 enables Cup-Tied state.

    Recovered runtime class mapping:
    League=1 -> false, Cup=2 -> true, DummyLeague=3 -> true.
    """
    root_id = root_competition_id(int(competition_id), competitions)
    root = competitions[root_id]
    if int(getattr(root, "runtime_kind_code")) in (
        RUNTIME_KIND_CUP,
        RUNTIME_KIND_DUMMY_LEAGUE,
    ):
        return root_id
    return None
