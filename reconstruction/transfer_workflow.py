"""Live Gate-9 human transfer-bid workflow.

This layer composes already-recovered transfer primitives without inventing
later contract-negotiation or finance policy.

For the ordinary cash-only proposal path, canonical setup calls
0x4EFE80(0, 0). Under that exact mode:
- 0x6596A0 contributes zero to 0x4EFA20;
- 0x4F0E00 contributes zero when all three exchange slots are empty;
- 0x4EFE10 selects multiplier row 0 from {0,5,10,20,...}, contributing zero;
- therefore 0x4EFA20 equals proposal cash field +0x10 exactly.

The proposal/deal/bid-log records are created before the seller-chairman
response, matching the original lifecycle around 0x4EE23A / 0x4EFA80.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from player_contract import contract_expiry_from_month_span
from player_valuation import live_player_transfer_value
from transfer_decision import (
    SellingClubBidInputs,
    SellingClubDecision,
    eligible_selling_squad_count,
    evaluate_selling_club_bid,
    higher_rated_squadmate_count,
)
from transfer_state import (
    ContractTerms,
    PlayerMovement,
    ScheduledTransfer,
    TransferProposal,
)


@dataclass(frozen=True)
class LiveCashBidEvaluation:
    proposal: TransferProposal
    selling_club_id: int
    proposal_total_value: float
    player_value: float
    decision: SellingClubDecision
    inputs: SellingClubBidInputs


def cash_only_proposal_total_value(proposal: TransferProposal) -> float:
    """Reproduce 0x4EFA20 for the ordinary cash-only mode.

    This helper intentionally accepts only the proven default human-cash path:
    no exchange players and proposal +0x14 == 0. Other +0x14 modes add a
    recovered percentage term through 0x4EFE10 and must be modeled separately.
    """

    if proposal.has_exchange_player:
        raise ValueError(
            "cash-only proposal total does not accept exchange players"
        )
    if int(proposal.negotiation_state_14) != 0:
        raise ValueError(
            "cash-only proposal total is proven only for +0x14 mode 0"
        )
    return float(int(proposal.cash_fee))


def evaluate_live_cash_bid(
    state,
    proposal: TransferProposal,
    *,
    appearance_count: int = 0,
    recent_ratings=(),
) -> LiveCashBidEvaluation:
    """Evaluate one ordinary cash bid from current runtime state."""

    player_id = int(proposal.target_player_id)
    try:
        player = state.players[player_id]
    except KeyError as exc:
        raise KeyError(f"unknown target player {player_id}") from exc

    selling_club_id = int(player.club_id)
    buying_club_id = int(proposal.buying_club_id)
    if buying_club_id == selling_club_id:
        raise ValueError("buying club already owns the target player")
    if buying_club_id not in state.clubs:
        raise ValueError(f"unknown buying club {buying_club_id}")
    if selling_club_id not in state.clubs:
        raise ValueError(f"unknown selling club {selling_club_id}")

    age = player.age(state.calendar.current_date)
    if age is None:
        raise ValueError(f"player {player_id} has no usable date of birth")

    proposal_total = cash_only_proposal_total_value(proposal)
    player_value = live_player_transfer_value(
        state,
        player_id,
        appearance_count=int(appearance_count),
        recent_ratings=recent_ratings,
    )
    inputs = SellingClubBidInputs(
        proposal_total_value=proposal_total,
        player_value=player_value,
        target_age=int(age),
        higher_rated_squadmates=higher_rated_squadmate_count(
            state,
            player_id,
        ),
        eligible_squad_count=eligible_selling_squad_count(
            state,
            selling_club_id,
        ),
    )
    return LiveCashBidEvaluation(
        proposal=proposal,
        selling_club_id=selling_club_id,
        proposal_total_value=proposal_total,
        player_value=player_value,
        decision=evaluate_selling_club_bid(inputs),
        inputs=inputs,
    )


def submit_live_cash_bid(
    state,
    *,
    target_player_id: int,
    buying_club_id: int,
    cash_fee: int,
    contract_terms: ContractTerms | None = None,
    appearance_count: int = 0,
    recent_ratings=(),
) -> LiveCashBidEvaluation:
    """Create/log one cash proposal, then evaluate the seller response.

    Original proposal/deal/bid-log construction happens before the later
    seller-chairman response. This function preserves that order.

    Accepted bids remain DEAL_PENDING here. Player contract response,
    deal-state promotion, medical/completion, and cash posting are subsequent
    Gate-9 steps and are intentionally not invented by this function.
    """

    proposal = TransferProposal(
        target_player_id=int(target_player_id),
        buying_club_id=int(buying_club_id),
        cash_fee=int(cash_fee),
        negotiation_state_14=0,
        negotiation_state_15=0,
        contract_terms=contract_terms or ContractTerms(),
    )

    player_id = int(proposal.target_player_id)
    if player_id not in state.players:
        raise KeyError(f"unknown target player {player_id}")
    selling_club_id = int(state.players[player_id].club_id)
    if int(proposal.buying_club_id) == selling_club_id:
        raise ValueError("buying club already owns the target player")

    state.transfers.submit_proposal(
        proposal,
        selling_club_id=selling_club_id,
        current_date=state.calendar.current_date,
    )
    return evaluate_live_cash_bid(
        state,
        proposal,
        appearance_count=int(appearance_count),
        recent_ratings=recent_ratings,
    )


class ScheduledTransferOutcome(str, Enum):
    COMPLETED = "completed"
    RESCHEDULED_SQUAD_FULL = "rescheduled_squad_full"
    BLOCKED_SQUAD_FULL = "blocked_squad_full"
    INSUFFICIENT_FUNDS = "insufficient_funds"


@dataclass(frozen=True)
class ScheduledTransferExecution:
    scheduled: ScheduledTransfer
    outcome: ScheduledTransferOutcome
    movement: PlayerMovement | None = None


def schedule_ordinary_cash_transfer(
    state,
    proposal: TransferProposal,
    *,
    mode: int = 0,
) -> ScheduledTransfer:
    """Schedule the recovered MPMTransferPlayer ordinary-cash handoff.

    0x61B270 schedules mode 0 at current date + 1. 0x61B300 schedules mode 1
    at current date + 7. Both preserve the proposal and set DBRPlayer+0x174
    bit 7 (already signed elsewhere).
    """
    if proposal.has_exchange_player:
        raise ValueError("ordinary cash scheduler does not accept exchange players")
    player_id = int(proposal.target_player_id)
    if player_id not in state.players:
        raise KeyError(f"unknown target player {player_id}")
    buyer_id = int(proposal.buying_club_id)
    if buyer_id not in state.clubs:
        raise ValueError(f"unknown buying club {buyer_id}")

    mode = int(mode)
    if mode not in (0, 1):
        raise ValueError("MPMTransferPlayer mode must be 0 or 1")
    delay = 1 if mode == 0 else 7
    scheduled = ScheduledTransfer(
        proposal=proposal,
        due_date=state.calendar.current_date + timedelta(days=delay),
        mode=mode,
    )
    state.players[player_id].signed_for_other_club = True
    state.transfers.schedule_transfer(scheduled)
    return scheduled


def _complete_ordinary_cash_transfer(state, proposal: TransferProposal) -> PlayerMovement:
    """Apply the recovered 0x4229B0 -> 0x422AA0/0x422F70 core state changes.

    Finance posting remains outside this helper until Gate 10 supplies the live
    Balance subsystem. The caller must perform/authorize the controlled-buyer
    affordability check before entering here.
    """
    if proposal.has_exchange_player:
        raise ValueError("ordinary cash completion does not accept exchange players")

    player_id = int(proposal.target_player_id)
    buyer_id = int(proposal.buying_club_id)
    player = state.players[player_id]
    seller_id = int(player.club_id)
    if seller_id == buyer_id:
        raise ValueError("target player already belongs to buying club")

    old_roster = state.club_roster_order.setdefault(seller_id, [])
    new_roster = state.club_roster_order.setdefault(buyer_id, [])
    if old_roster.count(player_id) != 1:
        raise RuntimeError(
            f"seller roster must contain player {player_id} exactly once"
        )
    if player_id in new_roster:
        raise RuntimeError(
            f"buyer roster already contains player {player_id}"
        )

    # 0x404B30/0x404BB0 post the completed-transfer amount through the active
    # Balance before/alongside the club switch. Only materialized controlled
    # club Balances are mutated; AI clubs follow the original bypass.
    if hasattr(state, "post_transfer_cash"):
        state.post_transfer_cash(
            buyer_club_id=buyer_id,
            seller_club_id=seller_id,
            amount=int(proposal.cash_fee),
        )

    movement = PlayerMovement(
        player_id=player_id,
        from_club_id=seller_id,
        to_club_id=buyer_id,
        consideration=int(proposal.cash_fee),
        movement_date=state.calendar.current_date,
    )
    state.transfers.record_movement(movement)

    old_roster.remove(player_id)
    new_roster.append(player_id)
    player.club_id = buyer_id
    player.current_club_join_date = state.calendar.current_date
    player.signed_for_other_club = False
    player.transfer_listed = False
    player.loan_club_id = None

    terms = proposal.contract_terms
    player.weekly_wage = int(terms.weekly_wage)
    player.contract_expiry_date = contract_expiry_from_month_span(
        state.calendar.current_date,
        int(terms.contract_length_months),
    )
    player.promotion_bonus = int(terms.promotion_bonus)
    player.appearance_fee = int(terms.appearance_fee)
    player.relegation_transfer_request_clause = bool(
        terms.relegation_transfer_request_clause
    )
    player.big_club_offer_clause = bool(terms.big_club_offer_clause)
    player.big_money_offer_clause = bool(terms.big_money_offer_clause)
    player.house = bool(terms.house)
    player.car = bool(terms.car)
    if hasattr(player, "clear_match_selection"):
        player.clear_match_selection(reset_position=True)

    state.transfers.clear_deals_for(proposal)
    state.transfers.clear_proposal(player_id, buyer_id)
    return movement


def execute_due_ordinary_cash_transfers(
    state,
    *,
    user_controlled_club_id: int | None = None,
) -> tuple[ScheduledTransferExecution, ...]:
    """Execute due MPMTransferPlayer mode-0/1 objects.

    Exact recovered behavior represented here:
    - buyer roster count >= 40: mode 0 is rescheduled +7 days as mode 1;
    - buyer roster count >= 40 in mode 1 ends negotiations;
    - otherwise the normal completion path can run;
    - a user-controlled buyer must pass the live Balance current-cash gate.

    AI/non-user buyers follow the executable bypass. Starting current cash is
    not guessed: a controlled club must have a materialized Balance state.
    """
    now = state.calendar.current_date
    remaining = []
    results = []

    for scheduled in tuple(state.transfers.scheduled_transfers):
        if scheduled.due_date > now:
            remaining.append(scheduled)
            continue

        proposal = scheduled.proposal
        buyer_id = int(proposal.buying_club_id)
        buyer_roster = state.club_roster_order.setdefault(buyer_id, [])

        if len(buyer_roster) >= 40:
            if int(scheduled.mode) == 0:
                retry = ScheduledTransfer(
                    proposal=proposal,
                    due_date=now + timedelta(days=7),
                    mode=1,
                )
                remaining.append(retry)
                results.append(
                    ScheduledTransferExecution(
                        scheduled=retry,
                        outcome=ScheduledTransferOutcome.RESCHEDULED_SQUAD_FULL,
                    )
                )
            else:
                state.transfers.clear_deals_for(proposal)
                state.transfers.clear_proposal(
                    proposal.target_player_id,
                    proposal.buying_club_id,
                )
                results.append(
                    ScheduledTransferExecution(
                        scheduled=scheduled,
                        outcome=ScheduledTransferOutcome.BLOCKED_SQUAD_FULL,
                    )
                )
            continue

        if (
            user_controlled_club_id is not None
            and buyer_id == int(user_controlled_club_id)
        ):
            if not hasattr(state, "can_afford_current_cash"):
                raise RuntimeError(
                    "controlled-buyer transfer execution requires live "
                    "Balance current cash"
                )
            if not bool(
                state.can_afford_current_cash(
                    buyer_id,
                    int(proposal.cash_fee),
                )
            ):
                remaining.append(scheduled)
                results.append(
                    ScheduledTransferExecution(
                        scheduled=scheduled,
                        outcome=ScheduledTransferOutcome.INSUFFICIENT_FUNDS,
                    )
                )
                continue

        movement = _complete_ordinary_cash_transfer(state, proposal)
        results.append(
            ScheduledTransferExecution(
                scheduled=scheduled,
                outcome=ScheduledTransferOutcome.COMPLETED,
                movement=movement,
            )
        )

    state.transfers.scheduled_transfers[:] = remaining
    return tuple(results)
