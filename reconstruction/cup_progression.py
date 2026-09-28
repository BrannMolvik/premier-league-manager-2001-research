"""Live Cup ClubRef result resolution for Gate 12.

Startup already materializes Cup pairings symbolically. This module supplies
only the source-backed runtime bridge proven by ClubRef::Resolve at 0x4F28E0:
type-0 refs resolve directly, while type-1 refs resolve a referenced match
winner (selector 0) or its opposite/loser (selector != 0).

Score, replay and two-leg aggregate production deliberately remain outside this
module until their CupMatch subclasses are instruction-closed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable

from competition_startup import CupClubRefDescriptor


CupResultToken = tuple


@dataclass(frozen=True)
class CupKnockoutOutcome:
    """Resolved two-club outcome exposed through match virtual +0x44."""

    result_token: CupResultToken
    participant_0_club_id: int
    participant_1_club_id: int
    winner_club_id: int

    def __post_init__(self) -> None:
        participants = {
            int(self.participant_0_club_id),
            int(self.participant_1_club_id),
        }
        if len(participants) != 2:
            raise ValueError("Cup knockout outcome requires two distinct clubs")
        if int(self.winner_club_id) not in participants:
            raise ValueError("Cup winner must be one of the two participants")

    @property
    def loser_club_id(self) -> int:
        if int(self.winner_club_id) == int(self.participant_0_club_id):
            return int(self.participant_1_club_id)
        return int(self.participant_0_club_id)


@dataclass
class CupResultRegistry:
    """Persistent semantic counterpart of referenced CupMatch result objects."""

    outcomes: dict[CupResultToken, CupKnockoutOutcome] = field(default_factory=dict)

    def record_knockout_outcome(
        self,
        result_token: CupResultToken,
        participant_0_club_id: int,
        participant_1_club_id: int,
        winner_club_id: int,
    ) -> CupKnockoutOutcome:
        token = tuple(result_token)
        if len(token) != 4 or token[0] != "cup_result":
            raise ValueError("result token is not a Cup knockout result token")
        if token in self.outcomes:
            raise ValueError("Cup result token has already been recorded")
        outcome = CupKnockoutOutcome(
            result_token=token,
            participant_0_club_id=int(participant_0_club_id),
            participant_1_club_id=int(participant_1_club_id),
            winner_club_id=int(winner_club_id),
        )
        self.outcomes[token] = outcome
        return outcome

    def resolve_club_ref(self, ref: CupClubRefDescriptor) -> int | None:
        """Resolve the instruction-closed type-0/type-1 ClubRef subset.

        Type 1 selector 0 returns the match virtual +0x44 result club. Any
        nonzero selector follows 0x513FB0 and returns the opposite side.

        An unresolved referenced result returns None, matching the fact that
        startup may schedule later rounds before the source match has played.
        Unsupported type tags return None rather than borrowing semantics from
        League-position or MiniLeague resolvers.
        """
        ref_type = int(ref.type_code)
        if ref_type == 0:
            return (
                None
                if ref.direct_club_id is None
                else int(ref.direct_club_id)
            )
        if ref_type != 1:
            return None
        if ref.reference_token is None:
            return None

        outcome = self.outcomes.get(tuple(ref.reference_token))
        if outcome is None:
            return None
        if int(ref.selector) == 0:
            return int(outcome.winner_club_id)
        return int(outcome.loser_club_id)

    def resolve_pair(
        self,
        left_ref: CupClubRefDescriptor,
        right_ref: CupClubRefDescriptor,
    ) -> tuple[int, int] | None:
        left = self.resolve_club_ref(left_ref)
        right = self.resolve_club_ref(right_ref)
        if left is None or right is None:
            return None
        if int(left) == int(right):
            raise ValueError("resolved Cup pairing contains the same club twice")
        return int(left), int(right)
