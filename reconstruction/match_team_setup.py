from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class ManagerFormationSource(Protocol):
    formation_default: int
    formation_class3: int
    formation_class1: int


@dataclass(frozen=True)
class ManagerFormationPreferences:
    """Three persisted manager formation IDs consumed by 0x409B50."""

    default: int
    class3: int
    class1: int

    @classmethod
    def from_manager(cls, manager: ManagerFormationSource) -> "ManagerFormationPreferences":
        return cls(
            int(manager.formation_default),
            int(manager.formation_class3),
            int(manager.formation_class1),
        )

    def __post_init__(self) -> None:
        if not 0 <= int(self.default) <= 20:
            raise ValueError("default formation must be in 0..20")
        if not (0 <= int(self.class3) <= 20 or int(self.class3) == 0xFF):
            raise ValueError("class3 formation must be in 0..20 or 0xFF")
        if not 0 <= int(self.class1) <= 20:
            raise ValueError("class1 formation must be in 0..20")


def manager_formation_for_selection_class(
    preferences: ManagerFormationPreferences | ManagerFormationSource,
    selection_class: int,
) -> int:
    """Exact 0x409B50 mapping from 0x409500 class to manager formation byte.

    Numeric class names are intentionally preserved until the remaining
    0x409500 match-context branches are fully assigned football semantics.
    """
    if not isinstance(preferences, ManagerFormationPreferences):
        preferences = ManagerFormationPreferences.from_manager(preferences)

    selection_class = int(selection_class)
    if selection_class == 0 or selection_class == 2:
        formation = preferences.default
    elif selection_class == 1:
        formation = preferences.class1
    elif selection_class == 3:
        formation = preferences.class3
    else:
        raise ValueError("selection_class must be in 0..3")

    if formation == 0xFF:
        raise ValueError(
            "selected manager alternate formation is 0xFF; original fallback "
            "behavior must be traced before substituting another formation"
        )
    return formation


DEFAULT_SUBSTITUTE_QUOTA = 5


def resolved_substitute_quota(context_quota: int | None) -> int:
    """0x408500 fallback behavior after current-match/context resolution."""
    if context_quota is None:
        return DEFAULT_SUBSTITUTE_QUOTA
    quota = int(context_quota)
    if quota < 0:
        raise ValueError("substitute quota must be non-negative")
    return quota
