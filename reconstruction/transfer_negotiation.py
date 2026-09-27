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

from match_schedule import BoundedRng
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
