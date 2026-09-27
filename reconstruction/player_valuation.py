"""FM2001 player transfer valuation reconstructed from 0x4205A0/0x4205F0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class PlayerValuationTuning:
    """Shipped executable defaults loaded by the named tuning-key system."""

    goalkeeper_value: float = 0.55       # GKVALUE
    defender_value: float = 1.05         # DEFVALUE
    midfielder_value: float = 0.95       # MIDVALUE
    attacker_value: float = 1.20         # ATTVALUE

    old_age: float = 31.0                # OLD_AGE
    young_age: float = 18.0              # YOUNG_AGE

    division_values: tuple[float, ...] = (
        2.00, 1.75, 1.50, 1.25, 1.10, 1.10
    )                                    # DIV1VALUE..DIV6VALUE

    defender_old_age_value: float = 0.75
    midfielder_old_age_value: float = 0.65
    attacker_old_age_value: float = 0.60
    goalkeeper_old_age_value: float = 0.85

    defender_young_age_value: float = 0.75
    midfielder_young_age_value: float = 0.75
    attacker_young_age_value: float = 0.75
    goalkeeper_young_age_value: float = 0.75

    non_eu_fee_percentage: float = 0.70  # NonEUFeePercentage

    @property
    def position_values(self) -> tuple[float, ...]:
        # 0x4EA310 category order from the Position table:
        # 0 defender, 1 midfielder, 2 attacker, 3 goalkeeper.
        return (
            self.defender_value,
            self.midfielder_value,
            self.attacker_value,
            self.goalkeeper_value,
        )

    @property
    def old_age_values(self) -> tuple[float, ...]:
        return (
            self.defender_old_age_value,
            self.midfielder_old_age_value,
            self.attacker_old_age_value,
            self.goalkeeper_old_age_value,
        )

    @property
    def young_age_values(self) -> tuple[float, ...]:
        return (
            self.defender_young_age_value,
            self.midfielder_young_age_value,
            self.attacker_young_age_value,
            self.goalkeeper_young_age_value,
        )


DEFAULT_PLAYER_VALUATION_TUNING = PlayerValuationTuning()


def access_financial_base_value(financial_row) -> int:
    """Reproduce DBRAccessSkillFinancialValue helper 0x423980."""

    return int(financial_row.field_08) + (int(financial_row.field_0c) >> 1)


def recent_rating_value_multiplier(recent_ratings: Sequence[int]) -> float:
    """Reproduce the 0x41FB60 -> 0x42084D recent-rating adjustment.

    0x41F9C0 maintains a six-entry circular byte history. Once the caller's
    appearance/count gate has passed, 0x41FB60 averages the populated entries.

    Shipped piecewise behavior:
    - average <= 0: neutral;
    - below 7: -10% per rating point below 7;
    - exactly 7: neutral;
    - above 7: +20% per rating point above 7.

    The executable also contains a lower clamp path at transformed value -2;
    ordinary positive 1..10 match ratings never reach it, but the exact branch
    is preserved here.
    """

    values = tuple(int(value) for value in recent_ratings)
    if not values:
        return 1.0
    if len(values) > 6:
        raise ValueError("FM2001 recent-rating history contains at most six values")
    if any(value < 0 or value > 255 for value in values):
        raise ValueError("recent ratings must fit the original byte history")

    average = sum(values) / len(values)
    if average <= 0.0:
        return 1.0

    transformed = (average - 7.0) * 0.2
    if transformed > 0.0:
        return 1.0 + transformed
    if transformed >= -2.0:
        return 1.0 + transformed * 0.5
    return 0.0


def player_transfer_value(
    financial_row,
    *,
    position_group: int,
    age: int,
    division_category: int,
    club_country_eu_status_flag: int,
    appearance_count: int = 0,
    recent_ratings: Sequence[int] = (),
    tuning: PlayerValuationTuning = DEFAULT_PLAYER_VALUATION_TUNING,
) -> float:
    """Reproduce the numeric path of DBRPlayer::0x4205A0 / 0x4205F0.

    The caller supplies the AccessSkillFinancialValues row selected by
    0x41E1D0 (max preferred-role rating), the Position-table broad group from
    0x4EA310, and the current competition's 0x405500 division category.

    The country factor follows the executable exactly: DBRCountry+0x18 == 1
    uses 1.0; all other club countries use NonEUFeePercentage (0.7 shipped).
    This is based on the *club country's* EU-status flag, not the player's
    nationality.
    """

    position_group = int(position_group)
    division_category = int(division_category)
    age = int(age)
    appearance_count = int(appearance_count)

    if not 0 <= position_group < 4:
        raise ValueError("position_group must be 0 defender, 1 midfielder, 2 attacker, or 3 goalkeeper")
    if not 0 <= division_category < len(tuning.division_values):
        raise ValueError("division_category must be in 0..5")
    if appearance_count < 0:
        raise ValueError("appearance_count must not be negative")

    value = float(access_financial_base_value(financial_row))

    if age < tuning.young_age:
        value *= tuning.young_age_values[position_group]
    elif age > tuning.old_age:
        value *= tuning.old_age_values[position_group]

    value *= tuning.division_values[division_category]

    if appearance_count > 4:
        value *= recent_rating_value_multiplier(recent_ratings)

    country_factor = (
        1.0
        if int(club_country_eu_status_flag) == 1
        else tuning.non_eu_fee_percentage
    )

    value *= country_factor
    value *= tuning.position_values[position_group]
    return value
