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
class ManagerTacticalSource(Protocol):
    ai_play_style_source: int
    ai_aggression_source: int
    ai_with_ball_source: int
    ai_without_ball_source: int


@dataclass(frozen=True)
class ManagerTacticalSources:
    """Persisted DBRManager +0x30..+0x33 inputs consumed by 0x40D860.

    These are deliberately source values rather than final MatchCalculator
    tactic codes. The pre-match packet applies the exact transforms below
    before the TacticsCommand visitor consumes them.
    """

    play_style_source: int
    aggression_source: int
    with_ball_source: int
    without_ball_source: int

    @classmethod
    def from_manager(cls, manager: ManagerTacticalSource) -> "ManagerTacticalSources":
        return cls(
            int(manager.ai_play_style_source),
            int(manager.ai_aggression_source),
            int(manager.ai_with_ball_source),
            int(manager.ai_without_ball_source),
        )

    def __post_init__(self) -> None:
        for name in (
            "play_style_source",
            "aggression_source",
            "with_ball_source",
            "without_ball_source",
        ):
            value = int(getattr(self, name))
            if not 0 <= value <= 255:
                raise ValueError(f"{name} must be in 0..255")


@dataclass(frozen=True)
class TacticsPacketFields:
    """Four compact values written into the 0x40D860 pre-match packet."""

    strategy_code: int
    aggression_code: int
    with_ball_code: int
    without_ball_code: int


def play_style_to_strategy_code(play_style: int) -> int:
    """Exact switch in 0x4035E0.

    The helper is used both for live team Play style and the AI manager's
    persisted source byte. Unknown values take the executable's Normal fallback.
    """
    value = int(play_style)
    if value == 0:
        return 3
    if value == 1:
        return 2
    if value == 2:
        return 1
    return 2


def manager_tactics_packet_fields(
    sources: ManagerTacticalSources | ManagerTacticalSource,
) -> TacticsPacketFields:
    """Exact AI-side bit-field inputs built by 0x40D860.

    Do not reinterpret the returned codes as final team +0x1B4..+0x1B7 values
    until the concrete TacticsCommand visitor has been mapped.
    """
    if not isinstance(sources, ManagerTacticalSources):
        sources = ManagerTacticalSources.from_manager(sources)

    return TacticsPacketFields(
        strategy_code=play_style_to_strategy_code(sources.play_style_source),
        aggression_code=(int(sources.aggression_source) // 6) & 0x0F,
        with_ball_code=int(sources.with_ball_source) & 0x03,
        without_ball_code=int(sources.without_ball_source) & 0x03,
    )


@dataclass(frozen=True)
class TeamTacticalState:
    """Exact normal team tactical defaults from the team constructor.

    Runtime team fields:
    +0x1B4 Play style, +0x1B5 Without Ball, +0x1B6 With Ball,
    +0x1B7 Aggression.
    """

    play_style: int = 1
    without_ball_style: int = 0
    with_ball_style: int = 0
    aggression: int = 5

    def __post_init__(self) -> None:
        if not 0 <= int(self.play_style) <= 2:
            raise ValueError("play_style must be in 0..2")
        if not 0 <= int(self.without_ball_style) <= 3:
            raise ValueError("without_ball_style must be in 0..3")
        if not 0 <= int(self.with_ball_style) <= 3:
            raise ValueError("with_ball_style must be in 0..3")
        if not 0 <= int(self.aggression) <= 9:
            raise ValueError("aggression must be in 0..9")


def team_tactics_packet_fields(state: TeamTacticalState) -> TacticsPacketFields:
    """Exact user-controlled 0x40D860 packet packing inputs."""
    return TacticsPacketFields(
        strategy_code=play_style_to_strategy_code(state.play_style),
        aggression_code=int(state.aggression) & 0x0F,
        with_ball_code=int(state.with_ball_style) & 0x03,
        without_ball_code=int(state.without_ball_style) & 0x03,
    )
