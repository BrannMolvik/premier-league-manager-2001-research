from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from random import Random
from typing import Protocol, Sequence

from player_development import (
    DevelopmentState,
    PeakAges,
    choose_peak_age,
    displayed_skill,
    recalculate_monthly_skills,
)


class PlayerSource(Protocol):
    index: int
    first_name: str
    surname: str
    club_id: int
    nationality_id: int
    date_of_birth: date | None
    shirt_number: int
    height_cm: int
    weight_kg: int
    positions: tuple[int, int, int]
    current_raw: tuple[int, ...]
    target_raw: tuple[int, ...]


PHYSICAL_PEAK_RANGE = (25, 26)
SKILL_PEAK_RANGE = (27, 29)
LATE_PEAK_RANGE = (30, 32)


def age_on(date_of_birth: date, on_date: date) -> int:
    """Whole-year football age used by the reconstruction runtime.

    The original executable age accessor is known, but its calendar helper has
    not yet been instruction-mapped. Keeping this in one function makes the
    convention easy to replace if a later trace exposes an edge-case difference.
    """
    if on_date < date_of_birth:
        raise ValueError("on_date precedes date_of_birth")
    return on_date.year - date_of_birth.year - (
        (on_date.month, on_date.day) < (date_of_birth.month, date_of_birth.day)
    )


@dataclass
class RuntimePlayer:
    index: int
    first_name: str
    surname: str
    club_id: int
    nationality_id: int
    date_of_birth: date | None
    shirt_number: int
    height_cm: int
    weight_kg: int
    positions: tuple[int, int, int]
    current_raw: list[int]
    target_raw: tuple[int, ...]
    development: DevelopmentState | None
    training_modifiers: list[int] = field(default_factory=lambda: [0] * 17)

    @classmethod
    def from_database_player(
        cls,
        source: PlayerSource,
        as_of: date,
        rng: Random,
    ) -> "RuntimePlayer":
        current = list(source.current_raw)
        target = tuple(source.target_raw)
        development: DevelopmentState | None = None

        if source.date_of_birth is not None:
            actual_age = age_on(source.date_of_birth, as_of)
            peaks = PeakAges(
                choose_peak_age(actual_age, *PHYSICAL_PEAK_RANGE, rng.randrange),
                choose_peak_age(actual_age, *SKILL_PEAK_RANGE, rng.randrange),
                choose_peak_age(actual_age, *LATE_PEAK_RANGE, rng.randrange),
            )
            # 0x41E970 clamps only the stored working baseline age.
            baseline_age = min(50, max(15, actual_age))
            development = DevelopmentState(
                baseline_age=baseline_age,
                baseline_raw=tuple(current),
                target_raw=target,
                peak_ages=peaks,
            )

        return cls(
            index=source.index,
            first_name=source.first_name,
            surname=source.surname,
            club_id=source.club_id,
            nationality_id=source.nationality_id,
            date_of_birth=source.date_of_birth,
            shirt_number=source.shirt_number,
            height_cm=source.height_cm,
            weight_kg=source.weight_kg,
            positions=source.positions,
            current_raw=current,
            target_raw=target,
            development=development,
        )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.surname}".strip()

    @property
    def displayed_skills(self) -> tuple[int, ...]:
        return tuple(displayed_skill(v) for v in self.current_raw)

    def age(self, on_date: date) -> int | None:
        return None if self.date_of_birth is None else age_on(self.date_of_birth, on_date)

    def set_training_modifiers(self, values: Sequence[int]) -> None:
        if len(values) != 17:
            raise ValueError("FM2001 training modifiers require exactly 17 values")
        self.training_modifiers[:] = [max(0, min(255, int(v))) for v in values]

    def monthly_development_update(self, on_date: date) -> bool:
        """Run the verified first-of-month 17-skill development reconstruction.

        Returns False only for records without a usable date of birth/development
        baseline. Otherwise current_raw is mutated in place and True is returned.
        """
        if self.development is None or self.date_of_birth is None:
            return False
        age = age_on(self.date_of_birth, on_date)
        self.current_raw[:] = recalculate_monthly_skills(
            current_age=age,
            state=self.development,
            training_modifiers=self.training_modifiers,
        )
        return True
