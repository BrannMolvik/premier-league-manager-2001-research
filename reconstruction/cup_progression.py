"""Live Cup ClubRef result resolution for Gate 12.

Startup already materializes Cup pairings symbolically. This module supplies
only the source-backed runtime bridge proven by ClubRef::Resolve at 0x4F28E0:
type-0 refs resolve directly, while type-1 refs resolve a referenced match
winner (selector 0) or its opposite/loser (selector != 0).

Score production and class-specific replay/second-leg scheduling deliberately
remain outside this module until their CupMatch subclasses are instruction-closed.
The shared result virtual itself is modeled here so a completed match snapshot
can populate the persistent result-token registry without a manually supplied
winner.
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




@dataclass(frozen=True)
class CupMatchResolutionSnapshot:
    """Minimal state consumed by shared Cup virtual +0x44 at 0x514000.

    score_0/score_1 are the already-composed virtual +0x48/+0x4C totals for
    this match object. A linked previous match uses the opposite participant
    direction, matching Replay/SecondLeg construction.
    """

    participant_0_club_id: int
    participant_1_club_id: int
    score_0: int
    score_1: int
    complete: bool = True
    previous: "CupMatchResolutionSnapshot | None" = None

    def __post_init__(self) -> None:
        if int(self.participant_0_club_id) == int(self.participant_1_club_id):
            raise ValueError("Cup match requires two distinct clubs")
        if int(self.score_0) < 0 or int(self.score_1) < 0:
            raise ValueError("Cup match scores must be non-negative")
        if self.previous is not None:
            current = {
                int(self.participant_0_club_id),
                int(self.participant_1_club_id),
            }
            previous = {
                int(self.previous.participant_0_club_id),
                int(self.previous.participant_1_club_id),
            }
            if current != previous:
                raise ValueError("linked Cup matches must contain the same clubs")

    def result_club_id(self) -> int | None:
        """Reproduce the shared CupMatch virtual +0x44 at 0x514000."""
        if not bool(self.complete):
            return None

        left_total = int(self.score_0)
        right_total = int(self.score_1)
        previous = self.previous
        if previous is not None:
            left_total += int(previous.score_1)
            right_total += int(previous.score_0)

        if left_total > right_total:
            return int(self.participant_0_club_id)
        if left_total < right_total:
            return int(self.participant_1_club_id)

        if previous is None or not bool(previous.complete):
            return None

        # 0x514062..0x51409B compares current +0x4C to previous +0x4C.
        # Because linked match participants are reversed, this is the
        # executable's secondary/away-side comparison on tied aggregate.
        if int(self.score_1) > int(previous.score_1):
            return int(self.participant_1_club_id)
        if int(self.score_1) < int(previous.score_1):
            return int(self.participant_0_club_id)
        return None

@dataclass
class CupResultRegistry:
    """Persistent semantic counterpart of referenced CupMatch result objects."""

    outcomes: dict[CupResultToken, CupKnockoutOutcome] = field(default_factory=dict)

    def record_match_resolution(
        self,
        result_token: CupResultToken,
        snapshot: CupMatchResolutionSnapshot,
    ) -> CupKnockoutOutcome | None:
        """Record a result only when shared Cup virtual +0x44 resolves a club.

        Drawn/incomplete snapshots remain unresolved and deliberately do not
        consume the token, allowing a later Replay/SecondLeg object to supply
        the definitive result for the same pairing.
        """
        winner_club_id = snapshot.result_club_id()
        if winner_club_id is None:
            return None
        return self.record_knockout_outcome(
            result_token,
            snapshot.participant_0_club_id,
            snapshot.participant_1_club_id,
            winner_club_id,
        )

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
