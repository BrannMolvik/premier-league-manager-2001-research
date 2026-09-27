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

from player_valuation import live_player_transfer_value
from transfer_decision import (
    SellingClubBidInputs,
    SellingClubDecision,
    eligible_selling_squad_count,
    evaluate_selling_club_bid,
    higher_rated_squadmate_count,
)
from transfer_state import ContractTerms, TransferProposal


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
