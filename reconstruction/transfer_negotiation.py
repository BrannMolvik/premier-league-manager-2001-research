"""Evidence-backed player contract counter-offer primitives.

This module isolates the exact proposal mutation performed by
0x4EDB10 -> 0x4EE180. It deliberately does not decide whether the player
accepts, counters, or rejects the whole proposal; that broader policy lives in
DBRPlayer::0x422470 and is being reconstructed separately.

Recovered transform:
- proposal +0x38 stores the submitted wage before revision;
- proposal +0x3C stores the submitted signing-on fee before revision;
- desired wage/signing expectations are compared against 110% of the current
  submitted amount;
- only a desired amount strictly greater than that tolerance replaces the
  submitted amount;
- repeated negotiations use the midpoint between the prior anchor and current
  offer; wage midpoint is floored to at least the player's present wage;
- same-club renewal skips signing-on-fee revision;
- 0x4EE180 always writes contract length (RNG(3)+2)*12 = 24/36/48 months.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

from match_schedule import BoundedRng
from player_contract import (
    live_player_signing_on_fee_expectation,
    live_player_signing_on_fee_floor,
    live_player_wage_expectation,
    live_player_wage_floor,
)
from transfer_state import TransferProposal


COUNTER_OFFER_TOLERANCE = 1.1


@dataclass(frozen=True)
class CounterOfferAdjustment:
    proposal: TransferProposal
    desired_weekly_wage: int
    desired_signing_on_fee: int
    wage_was_raised: bool
    signing_fee_was_raised: bool

    @property
    def money_terms_changed(self) -> bool:
        return self.wage_was_raised or self.signing_fee_was_raised


def _trunc_half(value: int) -> int:
    """Signed integer division by two, truncating toward zero like x86 idiv."""
    value = int(value)
    return value // 2 if value >= 0 else -((-value) // 2)


def _midpoint_anchor(anchor: int, current: int) -> int:
    anchor = int(anchor)
    current = int(current)
    return anchor + _trunc_half(current - anchor)


def _exceeds_ten_percent_tolerance(desired: int, current: int) -> bool:
    """Mirror desired > current * 1.1 from 0x4EDB10."""
    desired = int(desired)
    current = int(current)
    if desired < 0 or current < 0:
        raise ValueError("contract money amounts must not be negative")
    return desired * 10 > current * 11


def adjust_player_counter_offer(
    proposal: TransferProposal,
    *,
    fresh_wage_expectation: int,
    fresh_signing_on_fee_expectation: int,
    current_player_weekly_wage: int,
    renewing_same_club: bool,
    rng: BoundedRng,
) -> CounterOfferAdjustment:
    """Apply 0x4EDB10 + 0x4EE180 to one proposal.

    fresh_wage_expectation and fresh_signing_on_fee_expectation correspond to
    player helpers 0x420180 and 0x4202A0. They remain explicit inputs until
    those source-table helpers are promoted to live runtime adapters.
    """

    current_wage = int(proposal.contract_terms.weekly_wage)
    current_signing = int(proposal.contract_terms.signing_on_fee)
    previous_wage = int(proposal.previous_wage_offer)
    previous_signing = int(proposal.previous_signing_on_fee_offer)
    fresh_wage = int(fresh_wage_expectation)
    fresh_signing = int(fresh_signing_on_fee_expectation)
    player_wage = int(current_player_weekly_wage)

    for name, value in (
        ("weekly wage", current_wage),
        ("signing-on fee", current_signing),
        ("fresh wage expectation", fresh_wage),
        ("fresh signing-on-fee expectation", fresh_signing),
        ("current player wage", player_wage),
    ):
        if value < 0:
            raise ValueError(f"{name} must not be negative")

    if previous_wage == 0:
        desired_wage = fresh_wage
    else:
        desired_wage = max(
            _midpoint_anchor(previous_wage, current_wage),
            player_wage,
        )

    wage_was_raised = _exceeds_ten_percent_tolerance(
        desired_wage,
        current_wage,
    )
    revised_wage = desired_wage if wage_was_raised else current_wage

    desired_signing = current_signing
    signing_was_raised = False
    if not bool(renewing_same_club):
        if previous_signing == 0:
            desired_signing = fresh_signing
        else:
            desired_signing = _midpoint_anchor(
                previous_signing,
                current_signing,
            )
        signing_was_raised = _exceeds_ten_percent_tolerance(
            desired_signing,
            current_signing,
        )

    revised_signing = (
        desired_signing if signing_was_raised else current_signing
    )

    contract_length_months = (int(rng.randbelow(3)) + 2) * 12

    revised_terms = replace(
        proposal.contract_terms,
        weekly_wage=revised_wage,
        signing_on_fee=revised_signing,
        contract_length_months=contract_length_months,
    )
    revised = replace(
        proposal,
        contract_terms=revised_terms,
        previous_wage_offer=current_wage,
        previous_signing_on_fee_offer=current_signing,
    )
    return CounterOfferAdjustment(
        proposal=revised,
        desired_weekly_wage=desired_wage,
        desired_signing_on_fee=desired_signing,
        wage_was_raised=wage_was_raised,
        signing_fee_was_raised=signing_was_raised,
    )


def adjust_live_player_counter_offer(
    state,
    proposal: TransferProposal,
    rng: BoundedRng | None = None,
) -> CounterOfferAdjustment:
    """Apply the exact counter-offer transform from current runtime state.

    Fresh expectations use the proposal's buying club exactly as 0x4EDB10
    passes proposal +0x34 into 0x420180 / 0x4202A0. The present player wage is
    the reconstructed DBRPlayer+0xC4 value.

    The same-club renewal branch is retained for completeness even though the
    Gate-9 human transfer workflow currently rejects bids for a club's own
    player.
    """
    player_id = int(proposal.target_player_id)
    buying_club_id = int(proposal.buying_club_id)
    try:
        player = state.players[player_id]
    except KeyError as exc:
        raise KeyError(f"unknown target player {player_id}") from exc

    if rng is None:
        rng = state._resolve_rng()

    wage = live_player_wage_expectation(
        state,
        player_id,
        buying_club_id,
    )
    signing = live_player_signing_on_fee_expectation(
        state,
        player_id,
        buying_club_id,
    )
    return adjust_player_counter_offer(
        proposal,
        fresh_wage_expectation=wage,
        fresh_signing_on_fee_expectation=signing,
        current_player_weekly_wage=int(player.weekly_wage),
        renewing_same_club=int(player.club_id) == buying_club_id,
        rng=rng,
    )


class OrdinaryMoneyResponse(str, Enum):
    """Recovered outcomes from the money/term slice of DBRPlayer::0x422470."""

    ACCEPTED = "accepted"
    COUNTER_OFFER = "counter_offer"
    LOW_WAGE = "low_wage"
    PLAYER_TERMS_TOO_HIGH = "player_terms_too_high"
    ALREADY_SIGNED_ELSEWHERE = "already_signed_elsewhere"
    DEFER_TO_BROADER_POLICY = "defer_to_broader_policy"
    INVALID_DURATION_COUNTER = "invalid_duration_counter"


@dataclass(frozen=True)
class OrdinaryMoneyResponseResult:
    outcome: OrdinaryMoneyResponse
    proposal: TransferProposal
    response_code: int | None
    wage_floor: int
    signing_fee_floor: int
    rng10_roll: int | None = None
    counter_adjustment: CounterOfferAdjustment | None = None
    requires_clause_adjustment_422070: bool = False
    requires_duration_adjustment_423340: bool = False


def evaluate_ordinary_money_response(
    state,
    proposal: TransferProposal,
    rng: BoundedRng | None = None,
) -> OrdinaryMoneyResponseResult:
    """Reproduce the proven money/term subpath of DBRPlayer::0x422470.

    This stops explicitly when the original reaches one of two still-unmapped
    policy helpers:
    - the broader refusal/status policy at 0x422803;
    - invalid-duration revision helper 0x423340.

    It therefore does not invent reason codes or clause mutations outside the
    disassembled subpath.

    Proven branches:
    - wage < 75% of 0x420210 wage floor -> response code 4;
    - sufficiently strong wage/signing/duration terms -> response code 2
      (Player Accepts);
    - weaker/anchored terms consume RNG(10); rolls 0..6 enter 0x4EDB10;
    - after that counter transform, if revised_wage*0.95 > submitted anchor,
      response code 1 (Counter Offer) is selected after 0x422070;
    - otherwise wage is restored to the submitted anchor and response code 2
      is selected;
    - RNG(10) rolls 7..9 and low-anchor cases continue into 0x422803.
    """

    player_id = int(proposal.target_player_id)
    buying_club_id = int(proposal.buying_club_id)
    try:
        player = state.players[player_id]
    except KeyError as exc:
        raise KeyError(f"unknown target player {player_id}") from exc
    if rng is None:
        rng = state._resolve_rng()

    wage_floor = live_player_wage_floor(
        state,
        player_id,
        buying_club_id,
    )
    signing_floor = live_player_signing_on_fee_floor(
        state,
        player_id,
        buying_club_id,
    )
    submitted_wage = int(proposal.contract_terms.weekly_wage)
    submitted_signing = int(proposal.contract_terms.signing_on_fee)
    duration = int(proposal.contract_terms.contract_length_months)
    history_duration = int(proposal.field_44)
    current_player_wage = int(player.weekly_wage)
    same_club = int(player.club_id) == buying_club_id

    # 0x4224B9: player +0x174 bit 7 means the player has already
    # accepted terms with another club. The normal constructor clears this bit;
    # code-2 acceptance sets it at 0x4227E6, and club assignment clears it at
    # 0x422F70.
    if bool(getattr(player, "signed_for_other_club", False)):
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.ALREADY_SIGNED_ELSEWHERE,
            proposal=proposal,
            response_code=16,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
        )

    # 0x4224A4: an excessive submitted contract length is rejected
    # immediately with response code 18. RTTI on the response event identifies
    # this as EAMChairmanPlayerTermsTooHighsub. This precedes the later
    # 0x423340 repair path, so 85+ months must not be treated as an ordinary
    # duration counter-offer.
    if duration > 84:
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.PLAYER_TERMS_TOO_HIGH,
            proposal=proposal,
            response_code=18,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
        )

    # 0x4226D3: reject only on a strict shortfall below 75%.
    if submitted_wage * 4 < wage_floor * 3:
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.LOW_WAGE,
            proposal=proposal,
            response_code=4,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
        )

    use_randomized_branch = submitted_wage <= current_player_wage
    if not use_randomized_branch:
        if duration < 6 or duration > 72:
            return OrdinaryMoneyResponseResult(
                outcome=OrdinaryMoneyResponse.INVALID_DURATION_COUNTER,
                proposal=proposal,
                response_code=1,
                wage_floor=wage_floor,
                signing_fee_floor=signing_floor,
                requires_duration_adjustment_423340=True,
            )

        if duration <= history_duration:
            use_randomized_branch = True
        elif (not same_club) and submitted_signing < signing_floor:
            use_randomized_branch = True
        elif submitted_wage < wage_floor:
            use_randomized_branch = True
        else:
            # 0x4227E6 sets DBRPlayer+0x174 bit 7 before returning code 2.
            player.signed_for_other_club = True
            return OrdinaryMoneyResponseResult(
                outcome=OrdinaryMoneyResponse.ACCEPTED,
                proposal=proposal,
                response_code=2,
                wage_floor=wage_floor,
                signing_fee_floor=signing_floor,
            )

    # 0x42277C: only 0..6 enter the negotiation transform.
    roll = int(rng.randbelow(10))
    if roll >= 7:
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.DEFER_TO_BROADER_POLICY,
            proposal=proposal,
            response_code=None,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
            rng10_roll=roll,
        )

    adjustment = adjust_live_player_counter_offer(
        state,
        proposal,
        rng,
    )
    anchor_wage = int(adjustment.proposal.previous_wage_offer)

    # 0x4227A8: an anchor below the lower wage floor leaves this proven slice.
    if anchor_wage < wage_floor:
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.DEFER_TO_BROADER_POLICY,
            proposal=adjustment.proposal,
            response_code=None,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
            rng10_roll=roll,
            counter_adjustment=adjustment,
        )

    revised_wage = int(adjustment.proposal.contract_terms.weekly_wage)
    if revised_wage * 95 > anchor_wage * 100:
        return OrdinaryMoneyResponseResult(
            outcome=OrdinaryMoneyResponse.COUNTER_OFFER,
            proposal=adjustment.proposal,
            response_code=1,
            wage_floor=wage_floor,
            signing_fee_floor=signing_floor,
            rng10_roll=roll,
            counter_adjustment=adjustment,
            requires_clause_adjustment_422070=True,
        )

    # 0x4227DD restores the submitted anchor wage before the code-2 path.
    accepted_terms = replace(
        adjustment.proposal.contract_terms,
        weekly_wage=anchor_wage,
    )
    accepted_proposal = replace(
        adjustment.proposal,
        contract_terms=accepted_terms,
    )
    # 0x4227E6 sets DBRPlayer+0x174 bit 7 before returning code 2.
    player.signed_for_other_club = True
    return OrdinaryMoneyResponseResult(
        outcome=OrdinaryMoneyResponse.ACCEPTED,
        proposal=accepted_proposal,
        response_code=2,
        wage_floor=wage_floor,
        signing_fee_floor=signing_floor,
        rng10_roll=roll,
        counter_adjustment=adjustment,
    )
