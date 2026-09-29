"""Live Cup ClubRef result resolution for Gate 12.

Startup already materializes Cup pairings symbolically. This module supplies
the source-backed runtime bridges proven by ClubRef::Resolve at 0x4F28E0:
type-0 refs resolve directly, type-1 refs resolve a referenced match winner
(selector 0) or its opposite/loser (selector != 0), and type-2 refs resolve a
ranked position from a referenced competition/context once that ranking exists.

The shared result virtual and the class-specific NormalRound Replay /
FirstLeg / SecondLeg completion lifecycle are instruction-closed and modeled
here. Calendar insertion remains outside this module until Gate-12 GameState
integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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



CUP_MATCH_NORMAL = 2
CUP_MATCH_REPLAY = 3
CUP_MATCH_FIRST_LEG = 4
CUP_MATCH_SECOND_LEG = 5
_CUP_MATCH_KINDS = {
    CUP_MATCH_NORMAL,
    CUP_MATCH_REPLAY,
    CUP_MATCH_FIRST_LEG,
    CUP_MATCH_SECOND_LEG,
}


@dataclass
class CupMatchRuntimeState:
    """Clean-room state for the recovered CupMatch subclass lifecycle.

    extra_time_capable is constructor bit 0x2. decisive_tiebreak is constructor
    bit 0x4. For a type-2 normal CupMatch the executable suppresses the
    120-minute engine path while decisive_tiebreak is clear, preserving
    replay-eligible 90-minute first ties.

    prior_match is the semantically previous match used by the decisive
    Replay/SecondLeg result calculation. following_match mirrors the
    executable's reverse +0x54 link without creating recursive snapshots.
    """

    result_token: CupResultToken
    match_kind: int
    participant_0_club_id: int
    participant_1_club_id: int
    extra_time_capable: bool = False
    decisive_tiebreak: bool = False
    auxiliary_flag: bool = False
    prior_match: "CupMatchRuntimeState | None" = None
    following_match: "CupMatchRuntimeState | None" = None
    base_score_0: int = 0
    base_score_1: int = 0
    decisive_score_0: int = 0
    decisive_score_1: int = 0
    complete: bool = False

    def __post_init__(self) -> None:
        token = tuple(self.result_token)
        if len(token) != 4 or token[0] != "cup_result":
            raise ValueError("result token is not a Cup knockout result token")
        self.result_token = token
        self.match_kind = int(self.match_kind)
        self.participant_0_club_id = int(self.participant_0_club_id)
        self.participant_1_club_id = int(self.participant_1_club_id)
        if self.match_kind not in _CUP_MATCH_KINDS:
            raise ValueError("unsupported Cup match kind")
        if self.participant_0_club_id == self.participant_1_club_id:
            raise ValueError("Cup match requires two distinct clubs")
        for value in (
            self.base_score_0,
            self.base_score_1,
            self.decisive_score_0,
            self.decisive_score_1,
        ):
            if int(value) < 0:
                raise ValueError("Cup match scores must be non-negative")

    @property
    def uses_extra_time(self) -> bool:
        """MatchEngine+0xD0C behavior from 0x510DC2..0x510DE7."""
        if self.match_kind == CUP_MATCH_NORMAL and not self.decisive_tiebreak:
            return False
        return bool(self.extra_time_capable)

    @property
    def composed_score_0(self) -> int:
        return int(self.base_score_0) + int(self.decisive_score_0)

    @property
    def composed_score_1(self) -> int:
        return int(self.base_score_1) + int(self.decisive_score_1)

    def resolution_snapshot(self) -> CupMatchResolutionSnapshot:
        previous = (
            None
            if self.prior_match is None
            else self.prior_match.resolution_snapshot()
        )
        return CupMatchResolutionSnapshot(
            participant_0_club_id=self.participant_0_club_id,
            participant_1_club_id=self.participant_1_club_id,
            score_0=self.composed_score_0,
            score_1=self.composed_score_1,
            complete=bool(self.complete),
            previous=previous,
        )

    @classmethod
    def normal(
        cls,
        result_token: CupResultToken,
        participant_0_club_id: int,
        participant_1_club_id: int,
        *,
        extra_time_capable: bool,
        decisive_tiebreak: bool,
        auxiliary_flag: bool = False,
    ) -> "CupMatchRuntimeState":
        return cls(
            result_token=tuple(result_token),
            match_kind=CUP_MATCH_NORMAL,
            participant_0_club_id=int(participant_0_club_id),
            participant_1_club_id=int(participant_1_club_id),
            extra_time_capable=bool(extra_time_capable),
            decisive_tiebreak=bool(decisive_tiebreak),
            auxiliary_flag=bool(auxiliary_flag),
        )

    @classmethod
    def replay_from(
        cls,
        original: "CupMatchRuntimeState",
    ) -> "CupMatchRuntimeState":
        """Reproduce live 0x51399E -> CupMatchReplay::CupMatchReplay."""
        if original.match_kind != CUP_MATCH_NORMAL:
            raise ValueError("Cup replay can only follow a normal CupMatch")
        if not original.complete:
            raise ValueError("Cup replay requires a completed first match")
        if original.decisive_tiebreak:
            raise ValueError("decisive normal CupMatch must not spawn a replay")
        if original.resolution_snapshot().result_club_id() is not None:
            raise ValueError("resolved normal CupMatch must not spawn a replay")

        replay = cls(
            result_token=original.result_token,
            match_kind=CUP_MATCH_REPLAY,
            participant_0_club_id=original.participant_1_club_id,
            participant_1_club_id=original.participant_0_club_id,
            extra_time_capable=True,
            decisive_tiebreak=True,
            auxiliary_flag=bool(original.auxiliary_flag),
            prior_match=original,
        )
        original.following_match = replay
        return replay

    @classmethod
    def two_leg_pair(
        cls,
        result_token: CupResultToken,
        participant_0_club_id: int,
        participant_1_club_id: int,
        *,
        second_leg_extra_time_capable: bool,
        second_leg_auxiliary_flag: bool = False,
    ) -> tuple["CupMatchRuntimeState", "CupMatchRuntimeState"]:
        """Reproduce 0x4F6A02/0x4F6A64 FirstLeg/SecondLeg construction."""
        first = cls(
            result_token=tuple(result_token),
            match_kind=CUP_MATCH_FIRST_LEG,
            participant_0_club_id=int(participant_0_club_id),
            participant_1_club_id=int(participant_1_club_id),
        )
        second = cls(
            result_token=tuple(result_token),
            match_kind=CUP_MATCH_SECOND_LEG,
            participant_0_club_id=int(participant_1_club_id),
            participant_1_club_id=int(participant_0_club_id),
            extra_time_capable=bool(second_leg_extra_time_capable),
            decisive_tiebreak=True,
            auxiliary_flag=bool(second_leg_auxiliary_flag),
            prior_match=first,
        )
        first.following_match = second
        return first, second


@dataclass(frozen=True)
class CupMatchCompletion:
    outcome: CupKnockoutOutcome | None
    replay: CupMatchRuntimeState | None
    used_rng_tiebreak_fallback: bool


def _completion_snapshot(
    match: CupMatchRuntimeState,
    base_score_0: int,
    base_score_1: int,
    decisive_score_0: int,
    decisive_score_1: int,
) -> CupMatchResolutionSnapshot:
    previous = (
        None
        if match.prior_match is None
        else match.prior_match.resolution_snapshot()
    )
    return CupMatchResolutionSnapshot(
        participant_0_club_id=match.participant_0_club_id,
        participant_1_club_id=match.participant_1_club_id,
        score_0=int(base_score_0) + int(decisive_score_0),
        score_1=int(base_score_1) + int(decisive_score_1),
        complete=True,
        previous=previous,
    )


def complete_cup_match(
    match: CupMatchRuntimeState,
    registry: "CupResultRegistry",
    score_0: int,
    score_1: int,
    *,
    rng=None,
    decisive_event_score_0: int = 0,
    decisive_event_score_1: int = 0,
) -> CupMatchCompletion:
    """Complete one CupMatch using the recovered 0x5136E0 lifecycle.

    Event-derived decisive scores correspond to the penalty/tie-break events
    accumulated into +0x5A/+0x5B. If the shared result virtual still returns
    null, the exact 0x513697 fallback consumes RNG(2): nonzero increments side
    0, zero increments side 1.

    A replay-eligible type-2 draw creates a reversed, linked CupMatchReplay
    without consuming that RNG. FirstLeg completion never finalizes the result
    token; SecondLeg and Replay completion can.
    """
    if match.complete:
        raise ValueError("Cup match has already been completed")

    score_0 = int(score_0)
    score_1 = int(score_1)
    tiebreak_0 = int(decisive_event_score_0)
    tiebreak_1 = int(decisive_event_score_1)
    if min(score_0, score_1, tiebreak_0, tiebreak_1) < 0:
        raise ValueError("Cup match scores must be non-negative")
    if (tiebreak_0 or tiebreak_1) and not match.decisive_tiebreak:
        raise ValueError("non-decisive Cup match cannot contain tie-break scores")
    if match.match_kind in (CUP_MATCH_REPLAY, CUP_MATCH_SECOND_LEG):
        if match.prior_match is None or not match.prior_match.complete:
            raise ValueError("linked decisive Cup match requires completed prior match")

    provisional = _completion_snapshot(
        match,
        score_0,
        score_1,
        tiebreak_0,
        tiebreak_1,
    )
    used_fallback = False
    previous = provisional.previous
    left_total = int(provisional.score_0)
    right_total = int(provisional.score_1)
    if previous is not None:
        left_total += int(previous.score_1)
        right_total += int(previous.score_0)

    needs_decisive_fallback = (
        bool(match.decisive_tiebreak)
        and left_total == right_total
    )
    if (
        needs_decisive_fallback
        and match.match_kind == CUP_MATCH_SECOND_LEG
        and previous is not None
        and int(provisional.score_1) != int(previous.score_1)
    ):
        # 0x51367D..0x513695: SecondLegMatch alone lets the recovered
        # away-goal comparison settle a tied aggregate before the fallback.
        needs_decisive_fallback = False

    if needs_decisive_fallback:
        if rng is None:
            raise ValueError("unresolved decisive Cup tie requires RNG(2)")
        draw = int(rng.randbelow(2))
        if draw < 0 or draw >= 2:
            raise ValueError("Cup tie-break RNG returned value outside bound")
        used_fallback = True
        if draw:
            tiebreak_0 += 1
        else:
            tiebreak_1 += 1
        provisional = _completion_snapshot(
            match,
            score_0,
            score_1,
            tiebreak_0,
            tiebreak_1,
        )

    match.base_score_0 = score_0
    match.base_score_1 = score_1
    match.decisive_score_0 = tiebreak_0
    match.decisive_score_1 = tiebreak_1
    match.complete = True

    if match.match_kind == CUP_MATCH_FIRST_LEG:
        return CupMatchCompletion(
            outcome=None,
            replay=None,
            used_rng_tiebreak_fallback=used_fallback,
        )

    winner_club_id = provisional.result_club_id()
    if winner_club_id is None:
        if match.match_kind == CUP_MATCH_NORMAL and not match.decisive_tiebreak:
            replay = CupMatchRuntimeState.replay_from(match)
            return CupMatchCompletion(
                outcome=None,
                replay=replay,
                used_rng_tiebreak_fallback=used_fallback,
            )
        raise ValueError("completed decisive Cup match did not resolve a club")

    outcome = registry.record_match_resolution(
        match.result_token,
        match.resolution_snapshot(),
    )
    if outcome is None:
        raise ValueError("resolved Cup match failed to populate result registry")
    return CupMatchCompletion(
        outcome=outcome,
        replay=None,
        used_rng_tiebreak_fallback=used_fallback,
    )


@dataclass
class CupResultRegistry:
    """Persistent semantic result/position state consumed by Cup ClubRefs."""

    outcomes: dict[CupResultToken, CupKnockoutOutcome] = field(default_factory=dict)
    competition_rankings: dict[tuple[int, int], tuple[int, ...]] = field(
        default_factory=dict
    )
    group_position_rankings: dict[tuple[int, int], tuple[int, ...]] = field(
        default_factory=dict
    )

    def record_competition_ranking(
        self,
        competition_id: int,
        club_ids,
        *,
        competition_context: int = 0,
    ) -> tuple[int, ...]:
        """Persist the sorted eligible ranking consumed by ClubRef type 2.

        The selector stored in the 16-byte ClubRef is a zero-based index into
        the referenced runtime competition/context ranking. The ranking owner
        remains responsible for applying that competition's original sorting
        and eligibility rules before publishing it here.
        """
        key = (int(competition_id), int(competition_context))
        ranking = tuple(int(club_id) for club_id in club_ids)
        if len(ranking) != len(set(ranking)):
            raise ValueError("competition ranking contains duplicate clubs")
        if key in self.competition_rankings:
            raise ValueError("competition ranking has already been recorded")
        self.competition_rankings[key] = ranking
        return ranking

    def replace_competition_ranking(
        self,
        competition_id: int,
        club_ids,
        *,
        competition_context: int = 0,
    ) -> tuple[int, ...]:
        """Refresh a live competition ranking after its table changes."""
        key = (int(competition_id), int(competition_context))
        ranking = tuple(int(club_id) for club_id in club_ids)
        if len(ranking) != len(set(ranking)):
            raise ValueError("competition ranking contains duplicate clubs")
        self.competition_rankings[key] = ranking
        return ranking

    def clear_competition_ranking(
        self,
        competition_id: int,
        *,
        competition_context: int = 0,
    ) -> tuple[int, ...] | None:
        """Withdraw a ranking when the proven live sort keys are ambiguous."""
        return self.competition_rankings.pop(
            (int(competition_id), int(competition_context)),
            None,
        )

    def replace_group_position_ranking(
        self,
        competition_id: int,
        position_index: int,
        club_ids,
    ) -> tuple[int, ...]:
        """Publish the globally sorted ClubRef type-3 candidate pool.

        The executable encodes type 3 as instance_count * position + ordinal,
        then takes that position from every sibling League instance, sorts the
        cross-group candidates, and selects by ordinal.  The clean descriptor
        already stores position in selector and ordinal in competition_context.
        """
        key = (int(competition_id), int(position_index))
        ranking = tuple(int(club_id) for club_id in club_ids)
        if len(ranking) != len(set(ranking)):
            raise ValueError("group-position ranking contains duplicate clubs")
        self.group_position_rankings[key] = ranking
        return ranking

    def clear_group_position_ranking(
        self,
        competition_id: int,
        position_index: int,
    ) -> tuple[int, ...] | None:
        return self.group_position_rankings.pop(
            (int(competition_id), int(position_index)),
            None,
        )

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
        """Resolve the instruction-backed type-0/type-1/type-2/type-3 subset.

        Type 1 selector 0 returns the match virtual +0x44 result club. Any
        nonzero selector follows 0x513FB0 and returns the opposite side.

        Type 2 references one runtime competition/context ranking directly.

        Type 3 is different: selector is the same table position taken from
        every sibling League instance and competition_context is the ordinal
        into the globally sorted cross-group candidate pool published here.

        Type 4 Scottish scheduling references remain unsupported.
        """
        ref_type = int(ref.type_code)
        if ref_type == 0:
            return (
                None
                if ref.direct_club_id is None
                else int(ref.direct_club_id)
            )

        if ref_type == 1:
            if ref.reference_token is None:
                return None
            outcome = self.outcomes.get(tuple(ref.reference_token))
            if outcome is None:
                return None
            if int(ref.selector) == 0:
                return int(outcome.winner_club_id)
            return int(outcome.loser_club_id)

        if ref_type == 2:
            if ref.competition_id is None:
                return None
            ranking = self.competition_rankings.get(
                (int(ref.competition_id), int(ref.competition_context))
            )
            selector = int(ref.selector)
            if ranking is None or selector < 0 or selector >= len(ranking):
                return None
            return int(ranking[selector])

        if ref_type == 3:
            if ref.competition_id is None:
                return None
            position_index = int(ref.selector)
            ordinal = int(ref.competition_context)
            ranking = self.group_position_rankings.get(
                (int(ref.competition_id), position_index)
            )
            if ranking is None or ordinal < 0 or ordinal >= len(ranking):
                return None
            return int(ranking[ordinal])

        return None

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
