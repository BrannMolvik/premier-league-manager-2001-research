"""Recovered FM2001 Gate-10 match-day attendance primitives.

These functions mirror the instruction-locked numeric body of 0x5DA2F0.
They deliberately accept source-state inputs explicitly; club/competition
adapters belong in the runtime integration layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PREMIER_LEAGUE_TIER_FACTOR = 0.9
PREMIER_LEAGUE_SEATING_REFERENCE = 30.0
PREMIER_LEAGUE_TERRACE_REFERENCE = 22.5
FRESH_CONTROLLED_FACILITY_FACTOR = 0.9
CUP_FINAL_ATTENDANCE_BOOST = 30
CUP_SEMIFINAL_ATTENDANCE_BOOST = 20
CUP_QUARTERFINAL_ATTENDANCE_BOOST = 15
CUP_ATTENDANCE_DIVISOR = 10


@dataclass(frozen=True)
class GateAttendanceCell:
    demand: float
    price_response: float
    random_span: int
    count: int


ENGLISH_DIVISION_SEATING_REFERENCES = (30.0, 20.0, 16.0, 12.0, 9.0)


@dataclass(frozen=True)
class DomesticCupGatePolicyInputs:
    """Instruction-closed non-stadium inputs for the English Cup gate branch."""

    tier_factor: float
    round_attendance_modifier: float
    seating_reference: float
    terrace_reference: float


def english_ticket_reference_prices(
    valuation_division_category: int,
) -> tuple[float, float]:
    """Reproduce England's 0x40CBC0 division-category price table.

    The English branch indexes the owning club competition's 0x4FA520 value.
    Categories 0..4 select EP-style seating references 30/20/16/12/9. Terrace
    reference is the exact executable 0.75 multiple.
    """
    category = int(valuation_division_category)
    if not 0 <= category < len(ENGLISH_DIVISION_SEATING_REFERENCES):
        raise ValueError("English division valuation category must be 0..4")
    seating = ENGLISH_DIVISION_SEATING_REFERENCES[category]
    return seating, seating * 0.75


def english_domestic_cup_gate_policy_inputs(
    *,
    root_competition_index: int,
    host_valuation_division_category: int,
    total_round_count: int,
    zero_based_round_index: int,
) -> DomesticCupGatePolicyInputs:
    """Compose the source-backed English Cup gate policy inputs.

    0x5DA2F0 resolves the host club's registered competition through club +0x10
    and its country through club +0x14, then 0x410FF0 selects that competition's
    index in DBRCountry +0x48/+0x4C (the League/DummyLeague root subset).
    0x40CBC0's English branch independently selects reference prices from the
    host club competition's valuation/division category. The Cup round
    relationship supplies the separately recovered round attendance modifier.
    """
    seating, terrace = english_ticket_reference_prices(
        int(host_valuation_division_category)
    )
    return DomesticCupGatePolicyInputs(
        tier_factor=fan_factor_for_root_competition_index(
            int(root_competition_index)
        ),
        round_attendance_modifier=cup_round_attendance_modifier(
            total_round_count=int(total_round_count),
            zero_based_round_index=int(zero_based_round_index),
        ),
        seating_reference=seating,
        terrace_reference=terrace,
    )


def fan_factor_for_root_competition_index(index: int) -> float:
    """Exact 0x5DA2F0 FanFactor1..5 selection by country league-root index.

    0x410FF0 supplies the owning club competition's stored index in its
    DBRCountry +0x48/+0x4C League/DummyLeague root subset. Indices 0..3
    select 0.9/0.8/0.7/0.6; index 4 and every later/default case use 0.5.
    """
    index = int(index)
    if index < 0:
        raise ValueError("root competition index must be non-negative")
    if index == 0:
        return 0.9
    if index == 1:
        return 0.8
    if index == 2:
        return 0.7
    if index == 3:
        return 0.6
    return 0.5


def cup_round_attendance_modifier(
    *,
    total_round_count: int,
    zero_based_round_index: int,
) -> float:
    """Reproduce the Cup branch at 0x5DA5FF..0x5DA744.

    The executable compares Cup+0x3C (total runtime rounds) with match virtual
    +0x60 (zero-based current round index). Remaining-round values 1/2/3 use
    ATTCupFianlBoost / ATTCupSemiFinalBoost / ATTCupQuarterFinalBoot.
    Earlier rounds use quarter-final boost minus one. All are divided by
    ATTCupDiv.

    Shipped tuning values are 30 / 20 / 15 / 10 respectively.
    """
    total_round_count = int(total_round_count)
    zero_based_round_index = int(zero_based_round_index)
    if total_round_count <= 0:
        raise ValueError("total_round_count must be positive")
    if not 0 <= zero_based_round_index < total_round_count:
        raise ValueError("zero_based_round_index is outside the Cup")

    rounds_from_final = total_round_count - zero_based_round_index
    if rounds_from_final == 1:
        boost = CUP_FINAL_ATTENDANCE_BOOST
    elif rounds_from_final == 2:
        boost = CUP_SEMIFINAL_ATTENDANCE_BOOST
    elif rounds_from_final == 3:
        boost = CUP_QUARTERFINAL_ATTENDANCE_BOOST
    else:
        boost = CUP_QUARTERFINAL_ATTENDANCE_BOOST - 1
    return float(boost) / float(CUP_ATTENDANCE_DIVISOR)


def signed_trunc_division(numerator: int, denominator: int) -> int:
    """C/C++ signed integer division toward zero for a positive denominator."""
    numerator = int(numerator)
    denominator = int(denominator)
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    quotient = abs(numerator) // denominator
    return -quotient if numerator < 0 else quotient


def league_importance_factor(
    *,
    current_runtime_order: int,
    first_runtime_order: int,
    competition_count: int,
) -> float:
    """Reproduce 0x4FA670 after its country-root competition lookup."""
    quotient = signed_trunc_division(
        int(first_runtime_order) - int(current_runtime_order),
        int(competition_count),
    )
    return 1.0 - float(quotient)


def league_position_factor(
    *,
    table_index: int,
    team_count: int,
    games_played: int,
    games_remaining: int,
) -> float:
    """Exact 0x5DBA60 league-position component."""
    table_index = int(table_index)
    team_count = int(team_count)
    games_played = int(games_played)
    games_remaining = int(games_remaining)
    if team_count <= 0:
        raise ValueError("team_count must be positive")
    if not 0 <= table_index < team_count:
        raise ValueError("table_index must reference the current league table")
    if games_remaining < 4 or games_played < 5:
        return 1.0
    return 1.0 - float(table_index) / float(team_count)


def league_end_play_factor(
    *,
    games_remaining: int,
    objective_gaps: Iterable[tuple[bool, int, float]],
    threshold: int = 5,
) -> float:
    """Apply the 0x5DBA60 ordered late-season objective test.

    objective_gaps entries are (enabled, positive-points-gap, factor), already
    ordered as the executable's win/promotion/playoff/relegation/playoff cases.
    """
    games_remaining = int(games_remaining)
    if games_remaining <= 0 or games_remaining >= int(threshold):
        return 0.0
    for enabled, gap, factor in objective_gaps:
        gap = int(gap)
        if not bool(enabled) or gap <= 0:
            continue
        if float(gap) / float(games_remaining) <= 3.0:
            return float(factor)
    return 0.0


def first_xi_rating_factor(overall_ratings: Iterable[int]) -> float:
    """Exact 0x5DBA60 first-11 overall-rating scale: sum * 0.00125."""
    ratings = tuple(int(value) for value in overall_ratings)
    if len(ratings) != 11:
        raise ValueError("FM2001 gate prestige input requires exactly 11 ratings")
    return float(sum(ratings)) * 0.00125


def ordinary_league_side_modifier(
    *,
    first_xi_ratings: Iterable[int],
    end_play_factor: float,
    position_factor: float,
    importance_factor: float,
    prestige_weight: int = 10,
    end_play_weight: int = 10,
    position_weight: int = 10,
    importance_weight: int = 10,
) -> float:
    """Exact weighted-average return shape of 0x5DBA60."""
    xi = first_xi_rating_factor(first_xi_ratings)
    weights = (
        int(prestige_weight),
        int(end_play_weight),
        int(position_weight),
        int(importance_weight),
    )
    denominator = sum(weights)
    if denominator == 0:
        raise ValueError("attendance side-modifier weights must not sum to zero")
    numerator = (
        float(weights[0]) * xi
        + float(weights[1]) * float(end_play_factor)
        + float(weights[2]) * float(position_factor)
        + float(weights[3]) * float(importance_factor)
    )
    return numerator / float(denominator)


def ticket_price_response(delta: float, reference: float) -> float:
    """Exact piecewise response from 0x5DA250."""
    a = float(delta)
    b = float(reference)
    if b <= 0.0:
        raise ValueError("reference ticket price must be positive")
    if a > b:
        return 0.1
    if a > 0.0:
        return max(0.1, 1.0 - a / b)
    if a > -0.5 * b:
        return 1.0 - a / (2.0 * b)
    if a > -b:
        return 1.5 - a / (4.0 * b)
    return 2.0


def capped_gate_demand(
    *,
    fan_base_raw: float,
    tier_factor: float,
    side_modifier: float,
    price_response: float,
    capacity: int,
    facility_factor: float = 1.0,
    cup_special: bool = False,
) -> float:
    """Calculate the recovered floating demand before integerization."""
    fan_base = max(0.0, float(fan_base_raw))
    tier = float(tier_factor)
    modifier = float(side_modifier)
    response = float(price_response)
    facility = float(facility_factor)
    physical_capacity = max(0, int(capacity))

    demand = (
        fan_base
        * tier
        * (2.0 - tier)
        * modifier
        * response
        * facility
    )
    if not cup_special:
        demand = min(demand, fan_base)
    return min(demand, float(physical_capacity))


def randomized_gate_count(
    demand: float,
    price_response: float,
    rand15: int,
) -> GateAttendanceCell:
    """Apply exact truncation/span/subtraction with one 15-bit RNG value."""
    d = max(0.0, float(demand))
    p = float(price_response)
    r = int(rand15)
    if not 0 <= r <= 0x7FFF:
        raise ValueError("rand15 must be in 0..32767")

    if p > 1.0:
        span_float = d / (100.0 + 1000.0 * (p - 1.0))
    else:
        span_float = d * 0.01

    # All recovered values here are non-negative, so Python int() is the same
    # x87 round-toward-zero conversion used by 0x668350.
    span = max(1, int(span_float))
    base_count = int(d)
    subtraction = (r * span) // 32768
    return GateAttendanceCell(
        demand=d,
        price_response=p,
        random_span=span,
        count=base_count - subtraction,
    )


def calculate_gate_cell(
    *,
    fan_base_raw: float,
    tier_factor: float,
    side_modifier: float,
    price_delta: float,
    reference_price: float,
    capacity: int,
    rand15: int,
    facility_factor: float = 1.0,
    cup_special: bool = False,
) -> GateAttendanceCell:
    response = ticket_price_response(price_delta, reference_price)
    demand = capped_gate_demand(
        fan_base_raw=fan_base_raw,
        tier_factor=tier_factor,
        side_modifier=side_modifier,
        price_response=response,
        capacity=capacity,
        facility_factor=facility_factor,
        cup_special=cup_special,
    )
    return randomized_gate_count(demand, response, rand15)



@dataclass(frozen=True)
class GateReceiptResult:
    """Four recovered attendance cells plus the category-1/2 posting amounts."""

    home_seating: GateAttendanceCell
    visiting_seating: GateAttendanceCell
    home_terrace: GateAttendanceCell
    visiting_terrace: GateAttendanceCell
    home_revenue: int
    visiting_revenue: int
    season_ticket_quantity: int = 0

    @property
    def ordinary_home_attendance(self) -> int:
        return int(self.home_seating.count) + int(self.home_terrace.count)

    @property
    def visiting_attendance(self) -> int:
        return int(self.visiting_seating.count) + int(self.visiting_terrace.count)

    @property
    def home_attendance(self) -> int:
        return self.ordinary_home_attendance + max(0, int(self.season_ticket_quantity))

    @property
    def total_attendance(self) -> int:
        return self.home_attendance + self.visiting_attendance


def calculate_matchday_gate_receipts(
    *,
    home_fan_base_raw: float,
    visiting_fan_base_raw: float,
    home_tier_factor: float,
    visiting_tier_factor: float,
    home_side_modifier: float,
    visiting_side_modifier: float,
    seating_reference: float,
    terrace_reference: float,
    home_seating_price_delta: float,
    visiting_seating_price_delta: float,
    home_terrace_price_delta: float,
    visiting_terrace_price_delta: float,
    home_seating_capacity: int,
    visiting_seating_capacity: int,
    home_terrace_capacity: int,
    visiting_terrace_capacity: int,
    host_seating_price: int,
    host_terrace_price: int,
    rand15_values: tuple[int, int, int, int],
    home_facility_factor: float = 1.0,
    visiting_facility_factor: float = 1.0,
    season_ticket_quantity: int = 0,
    cup_special: bool = False,
) -> GateReceiptResult:
    """Run the four-cell gate body in original RNG order.

    The executable consumes RNG in this order:
    home seating -> visiting seating -> home terrace -> visiting terrace.
    Category 1 is visiting-supporter ordinary ticket revenue; category 2 is
    home-supporter ordinary ticket revenue. Season-ticket holders are appended
    only to the home attendance output after category-2 revenue is determined.
    """
    if len(rand15_values) != 4:
        raise ValueError("rand15_values must contain exactly four values")

    home_seating = calculate_gate_cell(
        fan_base_raw=home_fan_base_raw,
        tier_factor=home_tier_factor,
        side_modifier=home_side_modifier,
        price_delta=home_seating_price_delta,
        reference_price=seating_reference,
        capacity=home_seating_capacity,
        rand15=rand15_values[0],
        facility_factor=home_facility_factor,
        cup_special=cup_special,
    )
    visiting_seating = calculate_gate_cell(
        fan_base_raw=visiting_fan_base_raw,
        tier_factor=visiting_tier_factor,
        side_modifier=visiting_side_modifier,
        price_delta=visiting_seating_price_delta,
        reference_price=seating_reference,
        capacity=visiting_seating_capacity,
        rand15=rand15_values[1],
        facility_factor=visiting_facility_factor,
        cup_special=cup_special,
    )
    home_terrace = calculate_gate_cell(
        fan_base_raw=home_fan_base_raw,
        tier_factor=home_tier_factor,
        side_modifier=home_side_modifier,
        price_delta=home_terrace_price_delta,
        reference_price=terrace_reference,
        capacity=home_terrace_capacity,
        rand15=rand15_values[2],
        facility_factor=home_facility_factor,
        cup_special=cup_special,
    )
    visiting_terrace = calculate_gate_cell(
        fan_base_raw=visiting_fan_base_raw,
        tier_factor=visiting_tier_factor,
        side_modifier=visiting_side_modifier,
        price_delta=visiting_terrace_price_delta,
        reference_price=terrace_reference,
        capacity=visiting_terrace_capacity,
        rand15=rand15_values[3],
        facility_factor=visiting_facility_factor,
        cup_special=cup_special,
    )

    home_revenue = (
        int(host_seating_price) * int(home_seating.count)
        + int(host_terrace_price) * int(home_terrace.count)
    )
    visiting_revenue = (
        int(host_seating_price) * int(visiting_seating.count)
        + int(host_terrace_price) * int(visiting_terrace.count)
    )
    return GateReceiptResult(
        home_seating=home_seating,
        visiting_seating=visiting_seating,
        home_terrace=home_terrace,
        visiting_terrace=visiting_terrace,
        home_revenue=home_revenue,
        visiting_revenue=visiting_revenue,
        season_ticket_quantity=max(0, int(season_ticket_quantity)),
    )
