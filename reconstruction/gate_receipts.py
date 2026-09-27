"""Recovered FM2001 Gate-10 match-day attendance primitives.

These functions mirror the instruction-locked numeric body of 0x5DA2F0.
They deliberately accept source-state inputs explicitly; club/competition
adapters belong in the runtime integration layer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateAttendanceCell:
    demand: float
    price_response: float
    random_span: int
    count: int


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
