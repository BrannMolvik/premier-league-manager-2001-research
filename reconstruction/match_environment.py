from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol


class BoundedRng(Protocol):
    def randbelow(self, bound: int) -> int: ...


WEATHER_GLOBAL_MIN_TEMP = -5
WEATHER_GLOBAL_MAX_TEMP = 35
WEATHER_WEEKDAY_EVENING_DROP = 5

# Exact initialized defaults loaded by Weather_TempJan .. Weather_TempDec.
WEATHER_MONTHLY_TEMPERATURES = (
    0,   # Jan
    5,   # Feb
    10,  # Mar
    15,  # Apr
    20,  # May
    25,  # Jun
    30,  # Jul
    25,  # Aug
    20,  # Sep
    15,  # Oct
    10,  # Nov
    5,   # Dec
)

WEATHER_CODE_RAIN = 2

PITCH_RECOVER = 2
PITCH_WEAR = 16
RAIN_PITCH_WEAR = 32
MAX_PITCH_WEAR = 192


@dataclass(frozen=True)
class MatchEnvironment:
    """Exact pre-match temperature/weather state built by 0x6314E0/0x631630."""

    temperature_c: int
    weather_code: int
    weekday_evening: bool

    @property
    def raining(self) -> bool:
        return int(self.weather_code) == WEATHER_CODE_RAIN


def weekday_evening_flag(on_date: date) -> bool:
    """Exact OLE-date weekday test used by match setup.

    The executable computes (OLE_date + 5) % 7 and treats values 5/6 as the
    weekend branch. This is equivalent to Monday-Friday=True,
    Saturday-Sunday=False for the game's Gregorian dates.
    """
    return int(on_date.weekday()) < 5


def generate_match_environment(
    on_date: date,
    rng: BoundedRng,
) -> MatchEnvironment:
    """Reconstruct 0x6314E0 -> 0x631630 using shipped weather defaults."""
    base = int(WEATHER_MONTHLY_TEMPERATURES[int(on_date.month) - 1])
    evening = weekday_evening_flag(on_date)
    if evening:
        base -= WEATHER_WEEKDAY_EVENING_DROP

    # 0x631595: RNG(6) - 3 gives -3..+2.
    temperature = base + int(rng.randbelow(6)) - 3
    temperature = max(
        WEATHER_GLOBAL_MIN_TEMP,
        min(WEATHER_GLOBAL_MAX_TEMP, temperature),
    )

    if temperature <= 0:
        # 0x63163D: RNG(2) == 0 -> code 4, nonzero -> code 3.
        weather_code = 4 if int(rng.randbelow(2)) == 0 else 3
    elif temperature >= 22:
        # Hot branch has no weather RNG draw.
        weather_code = 1
    else:
        # 0x631666: RNG(4) == 0 -> code 2 (rain), otherwise code 0.
        weather_code = 2 if int(rng.randbelow(4)) == 0 else 0

    return MatchEnvironment(
        temperature_c=int(temperature),
        weather_code=int(weather_code),
        weekday_evening=bool(evening),
    )


def pitch_wear_after_match(
    current_wear: int,
    weather_code: int,
) -> int:
    """Exact home-pitch wear increment from the post-match DBRTeam path."""
    current = int(current_wear)
    if not 0 <= current <= 255:
        raise ValueError("Pitch Wear must be a byte value")
    increment = (
        RAIN_PITCH_WEAR
        if int(weather_code) == WEATHER_CODE_RAIN
        else PITCH_WEAR
    )
    return min(MAX_PITCH_WEAR, current + increment)


def recover_ai_pitch_wear(current_wear: int) -> int:
    """Exact daily base recovery for a non-user-controlled club pitch."""
    current = int(current_wear)
    if not 0 <= current <= 255:
        raise ValueError("Pitch Wear must be a byte value")
    return max(0, current - PITCH_RECOVER)
