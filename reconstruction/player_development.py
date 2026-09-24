from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

SKILL_COUNT = 17
PEAK_PERIOD_DEFAULT = 5
MINIMUM_RAW_SKILL = 9
TRAINING_STEP = 8

SKILL_NAMES = (
    "Speed", "Strength", "Stamina", "Determination", "Injury Proneness",
    "Passing", "Shooting", "Tackling", "Heading", "Control", "Technique",
    "Awareness", "Agility", "Goalkeeping", "Confidence", "Leadership", "Set Piece",
)

# Exact bytes initialized by footballmanager.exe routine 0x4EAA00.
# Stored source order: attacking, defensive, midfield, goalkeeper, rest, fitness, technique.
_PROFILE_ATTACKING = (25, 0, 0, 0, 0, 0, 25, 0, 25, 25, 0, 0, 0, 0, 0, 0, 0)
_PROFILE_DEFENSIVE = (0, 0, 0, 25, 0, 0, 0, 25, 25, 0, 0, 12, 0, 0, 0, 0, 13)
_PROFILE_MIDFIELD = (0, 0, 25, 0, 0, 25, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 25)
_PROFILE_GOALKEEPER = (0, 0, 0, 0, 0, 12, 0, 0, 0, 25, 0, 0, 25, 25, 0, 0, 13)
_PROFILE_REST = (0,) * 17
_PROFILE_FITNESS = (25, 25, 25, 9, 0, 0, 0, 0, 0, 0, 0, 8, 8, 0, 0, 0, 0)
_PROFILE_TECHNIQUE = (0, 0, 0, 0, 0, 0, 0, 0, 25, 0, 25, 0, 0, 0, 12, 13, 25)

TRAINING_METHOD_NAMES = (
    "Rest / recovery",
    "Attacking",
    "Midfield",
    "Defensive",
    "Goalkeeper",
    "Fitness",
    "Technique",
)

# Method-ID mapping proven by selector 0x4EA9A0.
TRAINING_PROFILES = (
    _PROFILE_REST,
    _PROFILE_ATTACKING,
    _PROFILE_MIDFIELD,
    _PROFILE_DEFENSIVE,
    _PROFILE_GOALKEEPER,
    _PROFILE_FITNESS,
    _PROFILE_TECHNIQUE,
)

YOUTH_TEAM_COACH_MULTIPLIER = {
    1: 1.25,
    2: 1.30,
    3: 1.35,
    4: 1.40,
    5: 1.45,
}


@dataclass(frozen=True)
class PeakAges:
    physical: int
    skill: int
    late: int

    def for_skill(self, slot: int) -> int:
        if not 0 <= slot < SKILL_COUNT:
            raise IndexError(slot)
        if slot <= 4:
            return self.physical
        if slot <= 8:
            return self.skill
        return self.late


@dataclass(frozen=True)
class DevelopmentState:
    baseline_age: int
    baseline_raw: tuple[int, ...]
    target_raw: tuple[int, ...]
    peak_ages: PeakAges

    def __post_init__(self) -> None:
        if len(self.baseline_raw) != SKILL_COUNT or len(self.target_raw) != SKILL_COUNT:
            raise ValueError("FM2001 development state requires exactly 17 skills")


def displayed_skill(raw: int) -> int:
    """Exact FM2001 raw-byte -> displayed 0..30 conversion."""
    return (30 * int(raw) + 128) // 255


def enforce_minimum_display_rating(raw: int) -> int:
    """FM2001 forces any sub-1 displayed skill to raw 9 (display rating 1)."""
    raw = max(0, min(255, int(raw)))
    return MINIMUM_RAW_SKILL if displayed_skill(raw) < 1 else raw


def development_value(
    current_age: int,
    baseline_age: int,
    baseline_raw: int,
    target_raw: int,
    peak_age: int,
    peak_period: int = PEAK_PERIOD_DEFAULT,
) -> int:
    """Reconstruct one skill using the verified 0x41EAD0 age curve.

    The original uses x87 rounding-toward-zero when converting the positive
    floating result to an integer, equivalent to int(value) here.
    """
    A = int(current_age)
    L = int(baseline_age)
    B = float(baseline_raw)
    T = float(target_raw)
    P = int(peak_age)
    D = int(peak_period)

    if L <= P:
        if A <= L:
            value = B * 0.5 * (1.0 + (A - 10) / (L - 10))
        elif A <= P:
            value = B + (T - B) * (A - L) / (P - L)
        elif A <= P + D:
            value = T
        else:
            value = T * (60 - A) / (60 - P)
    else:
        if A <= P:
            value = T * 0.5 * (1.0 + (A - 10) / (P - 10))
        elif A <= L:
            value = B + (T - B) * (L - A) / (L - P)
        else:
            value = B * (60 - A) / (60 - L)

    return max(0, min(255, int(value)))


def apply_monthly_training_modifier(current_raw: int, target_raw: int, modifier: int) -> int:
    """Apply the verified post-age-recalculation training-record byte.

    This deliberately preserves FM2001's unusual overshoot branch:
        if current + m <= target: current += m
        else:                    current = target - m
    """
    current = int(current_raw)
    target = int(target_raw)
    m = int(modifier)
    if current + m <= target:
        value = current + m
    else:
        value = target - m
    return max(0, min(255, value))


def recalculate_monthly_skills(
    current_age: int,
    state: DevelopmentState,
    training_modifiers: Sequence[int] | None = None,
    peak_period: int = PEAK_PERIOD_DEFAULT,
) -> tuple[int, ...]:
    """Apply FM2001's monthly age/development reconstruction to all 17 skills."""
    if training_modifiers is None:
        training_modifiers = (0,) * SKILL_COUNT
    if len(training_modifiers) != SKILL_COUNT:
        raise ValueError("training_modifiers must contain exactly 17 bytes")

    out: list[int] = []
    for slot in range(SKILL_COUNT):
        value = development_value(
            current_age=current_age,
            baseline_age=state.baseline_age,
            baseline_raw=state.baseline_raw[slot],
            target_raw=state.target_raw[slot],
            peak_age=state.peak_ages.for_skill(slot),
            peak_period=peak_period,
        )
        value = apply_monthly_training_modifier(
            value,
            state.target_raw[slot],
            training_modifiers[slot],
        )
        out.append(enforce_minimum_display_rating(value))
    return tuple(out)


def training_quality_multiplier(
    youth_team_coach_rating: int | None = None,
    assistant_manager_present: bool = False,
    training_centre_present: bool = False,
) -> float:
    """Quality multiplier Q from active-training routine 0x4EACE0."""
    if youth_team_coach_rating is not None:
        try:
            quality = YOUTH_TEAM_COACH_MULTIPLIER[int(youth_team_coach_rating)]
        except KeyError as exc:
            raise ValueError("Youth Team Coach rating must be 1..5") from exc
    elif assistant_manager_present:
        quality = 1.25
    else:
        quality = 1.0

    if training_centre_present:
        quality += 0.25
    return quality


def training_success_threshold(profile_weight: int, quality_multiplier: float) -> float:
    """Exact active-training threshold: profile_weight * Q * 0.5."""
    return int(profile_weight) * float(quality_multiplier) * 0.5


def training_roll_succeeds(profile_weight: int, quality_multiplier: float, roll_0_to_99: int) -> bool:
    roll = int(roll_0_to_99)
    if not 0 <= roll <= 99:
        raise ValueError("roll must be in 0..99")
    return training_success_threshold(profile_weight, quality_multiplier) > roll


def active_training_step(current_raw: int, target_raw: int) -> int:
    """Exact +8 raw-skill step from player routine 0x41A870.

    The original only applies the step when current+8 is strictly below both
    255 and the development target. Equality with target does *not* step.
    """
    current = int(current_raw)
    target = int(target_raw)
    candidate = current + TRAINING_STEP
    if candidate < 255 and candidate < target:
        return candidate
    return current


def reverse_training_step(current_raw: int) -> int:
    """Exact -8 reversal from 0x41A9A0 (only when current > 8)."""
    current = int(current_raw)
    return current - TRAINING_STEP if current > TRAINING_STEP else current


def choose_peak_age(current_age: int, low: int, high: int, randrange: Callable[[int], int]) -> int:
    """Reproduce the initializer's high-exclusive peak selection.

    FM2001 calls its bounded RNG with (high-low), so the configured high value
    is exclusive in the shipped implementation. If the selected peak equals
    current age, it is incremented by one.
    """
    width = int(high) - int(low)
    if width <= 0:
        raise ValueError("peak range must have high > low")
    peak = int(low) + int(randrange(width))
    if peak == int(current_age):
        peak += 1
    return peak
