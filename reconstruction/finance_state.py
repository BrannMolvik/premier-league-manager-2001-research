"""Gate-10 current-cash/Balance runtime state.

Recovered executable behavior represented here:
- DBRUser owns Balance objects; the active Balance current cash is the qword at
  Balance +0x10.
- debit path 0x5DC650 refuses amounts above current cash and subtracts the
  accepted amount;
- credit path 0x5DC510 adds the supplied amount;
- transfer postings use accounting category 1000 on both buyer and seller
  sides.

The original constructor inputs that establish starting cash are not yet
resolved. Callers therefore initialize current cash explicitly rather than
silently inventing a starting balance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


GATE_VISITING_ACCOUNT_CATEGORY = 1
GATE_HOME_ACCOUNT_CATEGORY = 2
PLAYER_COST_ACCOUNT_CATEGORY = 101
SUPPORT_STAFF_COST_ACCOUNT_CATEGORY = 102
TRANSFER_ACCOUNT_CATEGORY = 1000


@dataclass(frozen=True)
class FinancePosting:
    amount: int
    category: int
    posting_date: date

    def __post_init__(self):
        if int(self.amount) == 0:
            raise ValueError("finance posting amount must be non-zero")


@dataclass
class BalanceRuntimeState:
    """Minimal clean-room slice of the FM2001 Balance object.

    current_cash corresponds to the qword at original Balance +0x10.
    Positive ledger amounts are credits; negative amounts are debits.
    """

    current_cash: int
    ledger: list[FinancePosting] = field(default_factory=list)

    def __post_init__(self):
        self.current_cash = int(self.current_cash)

    def can_afford(self, amount: int) -> bool:
        amount = int(amount)
        if amount < 0:
            raise ValueError("amount must not be negative")
        return self.current_cash >= amount

    def credit(
        self,
        amount: int,
        *,
        category: int,
        posting_date: date,
    ) -> FinancePosting:
        amount = int(amount)
        if amount < 0:
            raise ValueError("credit amount must not be negative")
        if amount == 0:
            raise ValueError("credit amount must be positive")
        self.current_cash += amount
        posting = FinancePosting(
            amount=amount,
            category=int(category),
            posting_date=posting_date,
        )
        self.ledger.append(posting)
        return posting

    def debit(
        self,
        amount: int,
        *,
        category: int,
        posting_date: date,
    ) -> FinancePosting:
        amount = int(amount)
        if amount < 0:
            raise ValueError("debit amount must not be negative")
        if amount == 0:
            raise ValueError("debit amount must be positive")
        if not self.can_afford(amount):
            raise ValueError("insufficient current cash")
        self.current_cash -= amount
        posting = FinancePosting(
            amount=-amount,
            category=int(category),
            posting_date=posting_date,
        )
        self.ledger.append(posting)
        return posting
