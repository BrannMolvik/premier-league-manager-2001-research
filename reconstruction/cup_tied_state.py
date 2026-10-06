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
from datetime import date, timedelta
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


@dataclass
class CupTiedTransferWindowState:
    """Global DBRGame Cup-Tied transfer-date window state.

    Recovery 357 identifies DBRGame+0x9D8/+0x9DC/+0x9E0 as the selector and
    two date cutoffs consumed only by the Cup runtime +0x34 mode-1 fallback.
    0x413A20 initializes selector 0 and derives the cutoffs from the current
    game date as +60 and +207 days. Daily 0x4138E0 changes the selector to 1
    on August 30 and to 2 on January 30; all other dates preserve its value.
    """

    selector: int
    cutoff_1: date
    cutoff_2: date

    @classmethod
    def initialize(cls, current_date: date) -> "CupTiedTransferWindowState":
        if not isinstance(current_date, date):
            raise TypeError("current_date must be a date")
        return cls(
            selector=0,
            cutoff_1=current_date + timedelta(days=60),
            cutoff_2=current_date + timedelta(days=207),
        )

    def advance_day(self, on_date: date) -> int:
        """Apply the exact daily selector transitions from DBRGame::0x4138E0."""
        if not isinstance(on_date, date):
            raise TypeError("on_date must be a date")
        if (on_date.month, on_date.day) == (8, 30):
            self.selector = 1
        elif (on_date.month, on_date.day) == (1, 30):
            self.selector = 2
        return int(self.selector)

    def selected_cutoff(self) -> date | None:
        """Return the cutoff selected by +0x9D8, or None for selector 0/other."""
        if int(self.selector) == 1:
            return self.cutoff_1
        if int(self.selector) == 2:
            return self.cutoff_2
        return None

    def transfer_history_is_tied(
        self,
        *,
        history_club_id: int | None,
        transfer_date: date | None,
    ) -> bool:
        """Reproduce the collection-miss date branch of 0x418480.

        Native 0x419350 exposes CPlayerTransferHistory+0x18 only when +0x08
        is greater than -1. The selected transfer date must be strictly later
        than the global cutoff. Missing history, selector 0/unknown, equality,
        and earlier dates all fail closed.
        """
        if history_club_id is None or int(history_club_id) < 0:
            return False
        if not isinstance(transfer_date, date):
            return False
        cutoff = self.selected_cutoff()
        return bool(cutoff is not None and transfer_date > cutoff)


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
    """Return a source-qualified root whose virtual +0x18 enables Cup-Tied state.

    Recovered runtime class mapping:
    League=1 -> false, Cup=2 -> true, DummyLeague=3 -> true.

    Lightweight tests and partial callers can carry competition stand-ins that
    predate recovery of the runtime class/parent fields. Missing source metadata
    is unresolved and therefore returns None rather than guessing a Cup root.
    The strict root_competition_id helper remains available for malformed
    parent-graph diagnostics.
    """
    try:
        root_id = root_competition_id(int(competition_id), competitions)
        root = competitions[root_id]
    except (KeyError, AttributeError, TypeError, ValueError):
        return None
    runtime_kind = getattr(root, "runtime_kind_code", None)
    if runtime_kind is None:
        return None
    if int(runtime_kind) in (
        RUNTIME_KIND_CUP,
        RUNTIME_KIND_DUMMY_LEAGUE,
    ):
        return root_id
    return None
