"""Recovered FM2001 Gate-10 match-day attendance primitives.

These functions mirror the instruction-locked numeric body of 0x5DA2F0.
They deliberately accept source-state inputs explicitly; club/competition
adapters belong in the runtime integration layer.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


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
