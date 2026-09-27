"""Gate-10 current-cash/Balance runtime state.

Recovered executable behavior represented here:
- DBRUser owns Balance objects; the active Balance current cash is the qword at
  Balance +0x10.
- debit path 0x5DC650 refuses ordinary amounts above current cash and subtracts
  accepted amounts;
- credit path 0x5DC510 adds the supplied amount and immediately creates the
  recovered category-1600 secondary debit at exact amount * 0.01 * 0.2;
- transfer postings use accounting category 1000 on both buyer and seller
  sides.

The original constructor inputs that establish starting cash are not yet
resolved. Callers therefore initialize current cash explicitly rather than
silently inventing a starting balance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import math


Money = int | float

GATE_VISITING_ACCOUNT_CATEGORY = 1
GATE_HOME_ACCOUNT_CATEGORY = 2
PLAYER_COST_ACCOUNT_CATEGORY = 101
SUPPORT_STAFF_COST_ACCOUNT_CATEGORY = 102
TRANSFER_ACCOUNT_CATEGORY = 1000
CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY = 1600
CREDIT_SECONDARY_DEBIT_RATE = 0.002


def _money(value: Money) -> Money:
    """Keep exact integer-looking values compact while preserving fractions."""
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("finance amount must be finite")
    if number.is_integer():
        return int(number)
    return number


@dataclass(frozen=True)
class FinancePosting:
    amount: Money
    category: int
    posting_date: date

    def __post_init__(self):
        object.__setattr__(self, "amount", _money(self.amount))
        if float(self.amount) == 0.0:
            raise ValueError("finance posting amount must be non-zero")


@dataclass
class BalanceRuntimeState:
    """Minimal clean-room slice of the FM2001 Balance object.

    current_cash corresponds to the qword at original Balance +0x10.
    Positive ledger amounts are credits; negative amounts are debits.

    The original stores finance values as doubles. Most recovered gameplay
    postings are integral, but Balance::credit also generates a fractional
    category-1600 debit, so this slice must preserve non-integral values.
    """

    current_cash: Money
    ledger: list[FinancePosting] = field(default_factory=list)

    def __post_init__(self):
        self.current_cash = _money(self.current_cash)

    def can_afford(self, amount: Money) -> bool:
        amount = _money(amount)
        if float(amount) < 0.0:
            raise ValueError("amount must not be negative")
        return float(self.current_cash) >= float(amount)

    def credit(
        self,
        amount: Money,
        *,
        category: int,
        posting_date: date,
    ) -> FinancePosting:
        """Apply original 0x5DC510 credit plus its category-1600 debit.

        The executable converts the incoming finance value to a double, adds the
        full amount to current cash, then multiplies that same double by literal
        0.01 and literal 0.2. It constructs a second finance value with
        conversion flags zero and sends it through Balance::debit as category
        1600 / flag 1. There is no integer conversion on this path.
        """
        amount = _money(amount)
        if float(amount) < 0.0:
            raise ValueError("credit amount must not be negative")
        if float(amount) == 0.0:
            raise ValueError("credit amount must be positive")

        self.current_cash = _money(float(self.current_cash) + float(amount))

        secondary = _money(float(amount) * 0.01 * 0.2)
        if float(secondary) != 0.0:
            # 0x5DC510 invokes the secondary debit before appending its own
            # primary-credit transaction. Preserve that observable ledger order.
            self.current_cash = _money(float(self.current_cash) - float(secondary))
            self.ledger.append(
                FinancePosting(
                    amount=_money(-float(secondary)),
                    category=CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY,
                    posting_date=posting_date,
                )
            )

        posting = FinancePosting(
            amount=amount,
            category=int(category),
            posting_date=posting_date,
        )
        self.ledger.append(posting)
        return posting

    def debit(
        self,
        amount: Money,
        *,
        category: int,
        posting_date: date,
    ) -> FinancePosting:
        amount = _money(amount)
        if float(amount) < 0.0:
            raise ValueError("debit amount must not be negative")
        if float(amount) == 0.0:
            raise ValueError("debit amount must be positive")
        if not self.can_afford(amount):
            raise ValueError("insufficient current cash")
        self.current_cash = _money(float(self.current_cash) - float(amount))
        posting = FinancePosting(
            amount=_money(-float(amount)),
            category=int(category),
            posting_date=posting_date,
        )
        self.ledger.append(posting)
        return posting
