"""Persistent transfer/contract state reconstructed from FM2001.

This module models the evidence-backed live records without yet inventing the
remaining club/AI decision policy.

Recovered structures:
- 0x50-byte transfer proposal / contract terms;
- CDealInProgress state families 0/1/2 and swap variants 3/4/5;
- CPlayerBidLog keyed by player + bidding club;
- CPlayerMovement completed-transfer history.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


DEAL_PENDING = 0
DEAL_READY = 1
DEAL_PLAYER_REJECTED = 2
DEAL_SWAP_OFFSET = 3


@dataclass(frozen=True)
class ContractTerms:
    weekly_wage: int = 0
    signing_on_fee: int = 0
    promotion_bonus: int = 0
    contract_length_months: int = 0
    appearance_fee: int = 0
    relegation_transfer_request_clause: bool = False
    big_club_offer_clause: bool = False
    big_money_offer_clause: bool = False
    house: bool = False
    car: bool = False

    def __post_init__(self):
        for name in (
            "weekly_wage",
            "signing_on_fee",
            "promotion_bonus",
            "contract_length_months",
            "appearance_fee",
        ):
            if int(getattr(self, name)) < 0:
                raise ValueError(f"{name} must not be negative")


@dataclass(frozen=True)
class TransferProposal:
    target_player_id: int
    buying_club_id: int
    cash_fee: int = 0
    exchange_player_ids: tuple[int, int, int] = (-1, -1, -1)
    negotiation_state_14: int = 0
    negotiation_state_15: int = 0
    contract_terms: ContractTerms = field(default_factory=ContractTerms)
    previous_wage_offer: int = 0
    previous_signing_on_fee_offer: int = 0
    field_40: int = 0
    field_44: int = 0
    previous_total_value: int = 0
    field_4c: int = 0

    def __post_init__(self):
        if len(self.exchange_player_ids) != 3:
            raise ValueError("FM2001 proposals require exactly three exchange slots")
        if int(self.cash_fee) < 0:
            raise ValueError("cash_fee must not be negative")

    @property
    def has_exchange_player(self) -> bool:
        """Exact semantics of proposal helper 0x4F0460."""
        return any(int(player_id) >= 0 for player_id in self.exchange_player_ids)

    @property
    def involved_player_ids(self) -> tuple[int, ...]:
        return (
            int(self.target_player_id),
            *tuple(
                int(player_id)
                for player_id in self.exchange_player_ids
                if int(player_id) >= 0
            ),
        )


@dataclass
class DealInProgress:
    player_id: int
    buying_club_id: int
    selling_club_id: int
    state: int
    contract_terms: ContractTerms
    created_date: date

    @property
    def is_swap_variant(self) -> bool:
        return int(self.state) >= DEAL_SWAP_OFFSET

    @property
    def base_state(self) -> int:
        state = int(self.state)
        return state - DEAL_SWAP_OFFSET if state >= DEAL_SWAP_OFFSET else state

    @property
    def ready_for_execution(self) -> bool:
        return self.base_state == DEAL_READY

    @property
    def player_rejected(self) -> bool:
        return self.base_state == DEAL_PLAYER_REJECTED

    def mark_ready(self) -> None:
        """Reproduce 0x50E5B0 / 0x50E760 family promotion to 1/4."""
        self.state = DEAL_READY + (
            DEAL_SWAP_OFFSET if self.is_swap_variant else 0
        )

    def mark_player_rejected(self) -> None:
        self.state = DEAL_PLAYER_REJECTED + (
            DEAL_SWAP_OFFSET if self.is_swap_variant else 0
        )


@dataclass
class PlayerBidLogEntry:
    player_id: int
    bidding_club_id: int
    bid_value: int
    bid_date: date
    status_counter: int = 0


@dataclass(frozen=True)
class PlayerMovement:
    player_id: int
    from_club_id: int
    to_club_id: int
    consideration: int
    movement_date: date

    @property
    def is_free_transfer(self) -> bool:
        return int(self.consideration) == 1

    @property
    def is_bosman(self) -> bool:
        return int(self.consideration) == 2


@dataclass
class TransferRuntimeState:
    proposals: dict[tuple[int, int], TransferProposal] = field(default_factory=dict)
    deals: dict[int, DealInProgress] = field(default_factory=dict)
    bid_log: dict[tuple[int, int], PlayerBidLogEntry] = field(default_factory=dict)
    movements: list[PlayerMovement] = field(default_factory=list)

    def proposal_key(self, player_id: int, buying_club_id: int) -> tuple[int, int]:
        return (int(player_id), int(buying_club_id))

    def submit_proposal(
        self,
        proposal: TransferProposal,
        *,
        selling_club_id: int,
        current_date: date,
    ) -> None:
        """Create/update proposal, bid log, and exact initial deal states."""
        key = self.proposal_key(
            proposal.target_player_id,
            proposal.buying_club_id,
        )
        self.proposals[key] = proposal

        previous = self.bid_log.get(key)
        if previous is None:
            self.bid_log[key] = PlayerBidLogEntry(
                player_id=int(proposal.target_player_id),
                bidding_club_id=int(proposal.buying_club_id),
                bid_value=int(proposal.cash_fee),
                bid_date=current_date,
                status_counter=0,
            )
        else:
            previous.bid_value = int(proposal.cash_fee)
            previous.bid_date = current_date

        swap = proposal.has_exchange_player
        initial_state = DEAL_PENDING + (DEAL_SWAP_OFFSET if swap else 0)
        self.deals[int(proposal.target_player_id)] = DealInProgress(
            player_id=int(proposal.target_player_id),
            buying_club_id=int(proposal.buying_club_id),
            selling_club_id=int(selling_club_id),
            state=initial_state,
            contract_terms=proposal.contract_terms,
            created_date=current_date,
        )
        for exchange_player_id in proposal.exchange_player_ids:
            exchange_player_id = int(exchange_player_id)
            if exchange_player_id < 0:
                continue
            self.deals[exchange_player_id] = DealInProgress(
                player_id=exchange_player_id,
                buying_club_id=int(selling_club_id),
                selling_club_id=int(proposal.buying_club_id),
                state=DEAL_PENDING + DEAL_SWAP_OFFSET,
                contract_terms=proposal.contract_terms,
                created_date=current_date,
            )

    def record_movement(self, movement: PlayerMovement) -> None:
        self.movements.append(movement)

    def clear_proposal(self, player_id: int, buying_club_id: int) -> None:
        self.proposals.pop(
            self.proposal_key(player_id, buying_club_id),
            None,
        )

    def clear_deals_for(self, proposal: TransferProposal) -> None:
        for player_id in proposal.involved_player_ids:
            self.deals.pop(int(player_id), None)
