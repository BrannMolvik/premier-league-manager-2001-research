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

Fresh controlled-club starting cash is sourced from the original Master.dat
club float64 at packed +165, copied to DBRClub +0xD0/+0xD4 and then written
to active Balance +0x10 during DBRUser startup.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import math
from typing import Protocol


Money = int | float

GATE_VISITING_ACCOUNT_CATEGORY = 1
GATE_HOME_ACCOUNT_CATEGORY = 2
PLAYER_COST_ACCOUNT_CATEGORY = 101
SUPPORT_STAFF_COST_ACCOUNT_CATEGORY = 102
TRANSFER_ACCOUNT_CATEGORY = 1000
CREDIT_SECONDARY_DEBIT_ACCOUNT_CATEGORY = 1600
CREDIT_SECONDARY_DEBIT_RATE = 0.002
CHAIRMAN_PERCENT_BUDGET_MISS = 95

OBJECTIVE_STARTING_PERCENT = {
    1: 155, 2: 135, 3: 100, 4: 135, 5: 125, 6: 100,
    7: 125, 8: 125, 9: 100, 10: 200, 11: 190, 12: 180,
    13: 170, 14: 165, 15: 145, 16: 150, 17: 100,
}
OBJECTIVE_TARGET_PERCENT = {
    1: 170, 2: 150, 3: 110, 4: 155, 5: 135, 6: 110,
    7: 150, 8: 135, 9: 110, 10: 220, 11: 205, 12: 195,
    13: 185, 14: 180, 15: 155, 16: 180, 17: 105,
}


def _money(value: Money) -> Money:
    """Keep exact integer-looking values compact while preserving fractions."""
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("finance amount must be finite")
    if number.is_integer():
        return int(number)
    return number


class ObjectiveCandidateRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


def fresh_financial_objective_requires_rng(
    fan_base_rank_count: int,
    league_team_count: int,
    *,
    first_hierarchy_class: bool,
    promotion_playoff_position_count: int,
) -> bool:
    """Return whether fresh-state 0x5DFD30 must consume RNG(100).

    For objective state +0x9C == 0, only two branch families are random:
    - first hierarchy class with high-half fan-base rank (slot 1: 2/15);
    - any non-first class with one or more promotion-playoff status-2
      positions (slot 1 or 2: 5/8).

    All other fresh branches are fully deterministic and may be materialized
    without knowing the caller's shared CRT state.
    """
    rank_count = int(fan_base_rank_count)
    team_count = int(league_team_count)
    playoff_count = int(promotion_playoff_position_count)
    if team_count <= 0:
        raise ValueError("league_team_count must be positive")
    if not 0 <= rank_count <= team_count:
        raise ValueError("fan_base_rank_count must be in 0..league_team_count")
    if playoff_count < 0:
        raise ValueError("promotion_playoff_position_count must be non-negative")

    high_rank = rank_count >= team_count // 2
    if bool(first_hierarchy_class):
        return high_rank
    return playoff_count > 0


def fresh_financial_objective_candidates(
    fan_base_rank_count: int,
    league_team_count: int,
    *,
    first_hierarchy_class: bool,
    last_hierarchy_class_equal: bool,
    promotion_playoff_position_count: int,
    rng: ObjectiveCandidateRng,
) -> tuple[int, int, int]:
    """Reproduce fresh-state (objective +0x9C == 0) 0x5DFD30.

    The three calls use slot arguments 0, 1 and 2. 0x4FA570 supplies the
    first-class predicate; 0x4FA590 compares the current 0x4FA520 class with
    the last DBRCountry +0x48 League/DummyLeague subset entry. The second
    0x4F88C0 output is the count of table positions marked status 2 by
    promotion-playoff child ClubRefs.

    Random branches call 0x64D540(100) and select the lower-numbered branch
    when the returned integer is <= 50. Because 0x64D540 returns 0..99, this
    deliberately preserves the original inclusive 51/49 split.
    """
    rank_count = int(fan_base_rank_count)
    team_count = int(league_team_count)
    playoff_count = int(promotion_playoff_position_count)
    if team_count <= 0:
        raise ValueError("league_team_count must be positive")
    if not 0 <= rank_count <= team_count:
        raise ValueError("fan_base_rank_count must be in 0..league_team_count")
    if playoff_count < 0:
        raise ValueError("promotion_playoff_position_count must be non-negative")
    if rng is None or not callable(getattr(rng, "randbelow", None)):
        raise TypeError("fresh objective candidates require bounded RNG")

    high_rank = rank_count >= team_count // 2

    def coin(low: int, high: int) -> int:
        return int(low) if int(rng.randbelow(100)) <= 50 else int(high)

    if bool(first_hierarchy_class):
        if high_rank:
            return (1, coin(2, 15), 3)
        return (4, 5, 6)

    if high_rank:
        return (
            13,
            1,
            5 if playoff_count <= 0 else coin(5, 8),
        )

    return (
        1,
        5 if playoff_count <= 0 else coin(5, 8),
        9 if bool(last_hierarchy_class_equal) else 6,
    )


@dataclass(frozen=True)
class FinancePosting:
    amount: Money
    category: int
    posting_date: date

    def __post_init__(self):
        object.__setattr__(self, "amount", _money(self.amount))
        if float(self.amount) == 0.0:
            raise ValueError("finance posting amount must be non-zero")


@dataclass(frozen=True)
class FinancialObjectiveEvaluation:
    """Result of the recovered three-year chairman objective check."""

    outcome: str
    sacking_reason: int | None = None


@dataclass
class FinancialObjectiveState:
    """Recovered Balance+0x30 chairman financial-objective slice.

    The original object carries additional bookkeeping fields. This slice keeps
    the source-backed fresh objective candidate set plus the selected
    three-year evaluation lifecycle.
    """

    base_cash: Money
    candidate_ids: tuple[int, int, int]
    selected_objective_id: int = 0
    starting_funds: Money = 0
    target_cash: Money = 0
    starting_funds_snapshot: Money = 0
    selected_on: date | None = None
    deadline: date | None = None
    active: bool = False
    progression_gate_reached: bool = False  # original relative +0x68 == 1
    progression_state: int = 0  # original byte +0x9C

    def __post_init__(self):
        self.base_cash = _money(self.base_cash)
        self.candidate_ids = tuple(int(value) for value in self.candidate_ids)
        if len(self.candidate_ids) != 3:
            raise ValueError("financial objective requires exactly three candidates")
        for objective_id in self.candidate_ids:
            if objective_id not in OBJECTIVE_STARTING_PERCENT:
                raise ValueError(f"unknown financial objective ID {objective_id}")
        self.starting_funds = _money(self.starting_funds)
        self.target_cash = _money(self.target_cash)
        self.starting_funds_snapshot = _money(self.starting_funds_snapshot)

    @staticmethod
    def premier_league_candidates(
        fan_base_rank_count: int,
        league_team_count: int,
    ) -> tuple[int, int, int]:
        """Compatibility wrapper for the no-RNG fresh Premier League branch."""

        class _NoRngExpected:
            def randbelow(self, bound: int) -> int:
                raise AssertionError("Premier League fresh objective consumed RNG")

        return fresh_financial_objective_candidates(
            fan_base_rank_count,
            league_team_count,
            first_hierarchy_class=False,
            last_hierarchy_class_equal=False,
            promotion_playoff_position_count=0,
            rng=_NoRngExpected(),
        )

    def select(self, candidate_index: int, selected_on: date) -> Money:
        """Apply 0x5DFB90 selection and return the replacement current cash."""
        index = int(candidate_index)
        if not 0 <= index < 3:
            raise ValueError("candidate_index must be 0, 1, or 2")
        objective_id = int(self.candidate_ids[index])
        start_percent = OBJECTIVE_STARTING_PERCENT[objective_id]
        target_percent = OBJECTIVE_TARGET_PERCENT[objective_id]
        self.selected_objective_id = objective_id
        self.starting_funds = _money(float(self.base_cash) * start_percent * 0.01)
        self.target_cash = _money(float(self.base_cash) * target_percent * 0.01)
        self.starting_funds_snapshot = self.starting_funds
        self.selected_on = selected_on
        try:
            self.deadline = selected_on.replace(year=selected_on.year + 3)
        except ValueError:
            # OLE date conversion keeps the three-year calendar intent for the
            # only awkward Gregorian edge (29 February).
            self.deadline = selected_on.replace(year=selected_on.year + 3, day=28)
        self.active = True
        # 0x5DFB90 resets +0x68; later season/competition progression sets it.
        self.progression_gate_reached = False
        return self.starting_funds

    def evaluate(self, current_cash: Money, on_date: date) -> FinancialObjectiveEvaluation | None:
        """Reproduce the 0x5E1D90 year-gated objective outcome.

        The original routine compares decoded years, not the full deadline date.
        If the later progression gate (+0x68) has not been reached, the same
        branch produces sacking reason 4. The finance-target path uses reason 5.
        """
        if not self.active or self.selected_objective_id == 0 or self.deadline is None:
            return None
        if int(on_date.year) != int(self.deadline.year):
            return None
        if not self.progression_gate_reached:
            return FinancialObjectiveEvaluation("dismissed", 4)

        cash = float(_money(current_cash))
        target = float(self.target_cash)
        if cash > target:
            return FinancialObjectiveEvaluation("success", None)
        tolerance = target * CHAIRMAN_PERCENT_BUDGET_MISS * 0.01
        if cash > tolerance:
            return FinancialObjectiveEvaluation("near_miss", None)
        return FinancialObjectiveEvaluation("dismissed", 5)


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
    financial_objective: FinancialObjectiveState | None = None

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
