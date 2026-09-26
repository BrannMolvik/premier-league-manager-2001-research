"""Recovered FM2001 player contract initialization primitives."""

from __future__ import annotations

from datetime import date
from typing import Protocol, Sequence

from match_role_rating import best_preferred_role_rating
from match_schedule import BoundedRng


class AccessSkillFinancialValueSource(Protocol):
    id: int
    weekly_wage_base: int
    weekly_wage_random_range: int


def initial_weekly_wage(
    skills: Sequence[int],
    preferred_positions: Sequence[int],
    financial_values: Sequence[AccessSkillFinancialValueSource],
    country_multiplier_percent: int,
    rng: BoundedRng,
) -> int:
    """Reproduce 0x418E56 -> 0x423A50 -> 0x423990 for starting wage.

    0x41E1D0 selects one of the 100 DBTAccessSkillFinancialValues rows.
    0x423A50 draws within row +0x14 and adds row +0x10. 0x423990 then
    multiplies by DBRCountry +0x30 and 0.01 and truncates toward zero.
    The analyzed executable's 0x6596A0 returns zero, so its alternate x4
    branch is not active for this release.
    """
    rating = best_preferred_role_rating(skills, preferred_positions)
    if not 0 <= rating < len(financial_values):
        raise ValueError(f"financial-value rating {rating} is out of range")
    row = financial_values[rating]
    random_range = int(row.weekly_wage_random_range)
    if random_range <= 0:
        raise ValueError("weekly wage random range must be positive")
    unscaled = int(row.weekly_wage_base) + int(rng.randbelow(random_range))
    multiplier = int(country_multiplier_percent)
    if multiplier < 0:
        raise ValueError("country financial multiplier must not be negative")
    return (unscaled * multiplier) // 100


def contract_expiry_from_month_span(start_date: date, month_span: int) -> date:
    """Reproduce the month-by-month +0xC0 -> +0x154 startup date loop."""
    month_span = int(month_span)
    if month_span < 0:
        raise ValueError("month_span must not be negative")
    year = int(start_date.year)
    month = int(start_date.month)
    for _ in range(month_span):
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1
    return date(year, month, int(start_date.day))
