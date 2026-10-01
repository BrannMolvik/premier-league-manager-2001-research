"""Recovered FM2001 player contract initialization primitives."""

from __future__ import annotations

from calendar import monthrange
from datetime import date
import math
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
    """Advance by the recovered calendar-month span without invalid dates.

    The executable-backed behavior proves the month count and that the contract
    path advances in calendar months. The exact original normalization when the
    source day does not exist in the target month is not yet instruction-locked.
    The modern runtime therefore keeps the source day when valid and uses a
    documented compatibility clamp to the target month's final day otherwise.
    """
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
    day = min(int(start_date.day), monthrange(year, month)[1])
    return date(year, month, day)


def _scaled_financial_value(
    raw_value: int,
    country_multiplier_percent: int,
) -> int:
    """Reproduce 0x423990 with the shipped x4 developer branch inactive."""
    raw_value = int(raw_value)
    multiplier = int(country_multiplier_percent)
    if raw_value < 0 or multiplier < 0:
        raise ValueError("financial values/multipliers must not be negative")
    return (raw_value * multiplier) // 100


def _round_positive_significant(value: float, digits: int) -> float:
    """Reproduce 0x5E4830 for positive values using x87 truncation."""
    value = float(value)
    digits = int(digits)
    if value <= 0.0:
        return value
    exponent = math.trunc(math.log10(value))
    if exponent >= digits:
        scale = 10.0 ** (exponent - digits + 1)
        return math.trunc(value / scale + 0.5) * scale
    if exponent < digits - 1:
        scale = 10.0 ** (digits - exponent - 1)
        return math.trunc(scale * value + 0.5) / scale
    return float(math.trunc(value + 0.5))


def round_transfer_wage_amount(value: int | float) -> int:
    """Reproduce money mode -1 used by 0x420180/0x420210.

    The canonical executable initializes the active money factor 0x87AD88 to
    1.0 (0x6596A0 returns currency mode 0), then mode -1 rounds to one
    significant digit below 1,000, two below 100,000, and three thereafter.
    """
    value = float(value)
    if value <= 0.0:
        return int(value)
    digits = 1 if value < 1_000.0 else (2 if value < 100_000.0 else 3)
    return int(_round_positive_significant(value, digits))


def round_transfer_signing_fee_amount(value: int | float) -> int:
    """Reproduce money mode -2 used by 0x4202A0.

    This is the exact positive-value ladder in 0x5E44F0..0x5E4821.
    The 20..100 branch intentionally preserves the executable's observed
    quotient result rather than "fixing" it into a multiple-of-five amount.
    """
    value = float(value)
    if value <= 0.0:
        return int(value)
    if value < 20.0:
        return int(math.floor(value + 0.5))
    if value < 100.0:
        return int((value + 2.5) * 0.2)
    if value < 250.0:
        return int((value + 5.0) * 0.1) * 10
    if value < 500.0:
        return int((value + 12.5) * 0.04) * 25
    if value < 10_000.0:
        return int((value + 25.0) * 0.02) * 50
    if value < 100_000.0:
        return int((value + 50.0) * 0.01) * 100
    if value < 1_000_000.0:
        return int((value + 250.0) * 0.002) * 500
    if value < 5_000_000.0:
        return int((value + 2_500.0) * 0.0002) * 5_000
    if value < 10_000_000.0:
        return int((value + 25_000.0) * 0.00002) * 50_000
    return int((value + 125_000.0) * 0.000004) * 250_000


def _live_financial_contract_inputs(state, player_id: int, buying_club_id: int):
    player_id = int(player_id)
    buying_club_id = int(buying_club_id)
    try:
        player = state.players[player_id]
    except KeyError as exc:
        raise KeyError(f"unknown player {player_id}") from exc
    try:
        club = state.clubs[buying_club_id]
    except KeyError as exc:
        raise KeyError(f"unknown buying club {buying_club_id}") from exc
    try:
        country = state.countries[int(club.country_id)]
    except KeyError as exc:
        raise ValueError(
            f"buying club {buying_club_id} has no resolved country"
        ) from exc

    rating = best_preferred_role_rating(
        player.current_raw,
        player.positions,
    )
    rows = tuple(state.access_skill_financial_values)
    if not 0 <= rating < len(rows):
        raise ValueError(
            f"financial-value row {rating} is unavailable for player {player_id}"
        )
    row = rows[rating]
    if int(getattr(row, "id", rating)) != rating:
        raise ValueError("financial-value table is not rating-indexed")
    multiplier = int(
        getattr(country, "financial_multiplier_percent", 100)
    )
    return player, row, multiplier


def live_player_wage_expectation(
    state,
    player_id: int,
    buying_club_id: int,
) -> int:
    """Reproduce DBRPlayer::0x420180 for the canonical currency mode."""
    _player, row, multiplier = _live_financial_contract_inputs(
        state, player_id, buying_club_id
    )
    raw = int(row.weekly_wage_base) + int(row.weekly_wage_random_range)
    scaled = _scaled_financial_value(raw, multiplier)
    return round_transfer_wage_amount(scaled)


def live_player_wage_floor(
    state,
    player_id: int,
    buying_club_id: int,
) -> int:
    """Reproduce DBRPlayer::0x420210 for the canonical currency mode."""
    _player, row, multiplier = _live_financial_contract_inputs(
        state, player_id, buying_club_id
    )
    scaled = _scaled_financial_value(
        int(row.weekly_wage_base),
        multiplier,
    )
    return round_transfer_wage_amount(scaled)


def signing_fee_doubling_eligible(state, player_id: int) -> bool:
    """Reproduce 0x41E5C0 exactly from live RuntimePlayer state.

    Predicate:
    - age >= 24;
    - compact/runtime +0x6C code == 2 (EU/exempt path);
    - contract expiry <= current game date.
    """
    player = state.players[int(player_id)]
    age = player.age(state.calendar.current_date)
    return bool(
        age is not None
        and int(age) >= 24
        and int(player.eu_status_code) == 2
        and player.contract_expiry_date is not None
        and player.contract_expiry_date <= state.calendar.current_date
    )


def live_player_signing_on_fee_expectation(
    state,
    player_id: int,
    buying_club_id: int,
) -> int:
    """Reproduce DBRPlayer::0x4202A0 for the canonical currency mode."""
    player, row, multiplier = _live_financial_contract_inputs(
        state, player_id, buying_club_id
    )
    raw = int(row.field_18) + int(row.field_1c)
    scaled = _scaled_financial_value(raw, multiplier)
    if signing_fee_doubling_eligible(state, int(player.index)):
        scaled *= 2
    return round_transfer_signing_fee_amount(scaled)


def live_player_signing_on_fee_floor(
    state,
    player_id: int,
    buying_club_id: int,
) -> int:
    """Reproduce DBRPlayer::0x420340 for the canonical currency mode.

    This uses AccessSkillFinancialValues +0x18 only (0x423AB0), applies the
    same expired-EU doubling predicate as 0x4202A0, then the exact -2 money
    rounding ladder.
    """
    player, row, multiplier = _live_financial_contract_inputs(
        state, player_id, buying_club_id
    )
    scaled = _scaled_financial_value(int(row.field_18), multiplier)
    if signing_fee_doubling_eligible(state, int(player.index)):
        scaled *= 2
    return round_transfer_signing_fee_amount(scaled)
