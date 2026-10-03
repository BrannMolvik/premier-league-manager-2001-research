"""Fail-closed Gate-17 audit of current human runtime-owner capability.

The source-backed playable-League runtime plan says which runtime owner each
TeamSelect League needs. This module compares that plan with an observed
clean-room controller surface. It reports blockers only; it never materializes
fixtures, changes club membership, widens selection, or simulates a match.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from gate17_playable_league_runtime_plan import (
    PlayableLeagueRuntimePlan,
    RUNTIME_FIXED_PRIMARY,
    RUNTIME_PROCEDURAL_PRIMARY,
    RUNTIME_PROCEDURAL_SECONDARY,
    load_canonical_playable_league_runtime_plan,
)


class Gate17RuntimeOwnerCapabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class HumanRuntimeOwnerSurface:
    selectable_club_ids: tuple[int, ...]
    fixed_primary_competition_ids: tuple[int, ...]
    materialized_primary_procedural_ids: tuple[int, ...]
    materialized_secondary_procedural_ids: tuple[int, ...]
    human_primary_procedural_ids: tuple[int, ...]
    human_secondary_procedural_ids: tuple[int, ...]
    annual_progression_country_ids: tuple[int, ...]


@dataclass(frozen=True)
class RuntimeOwnerCapabilityEntry:
    scope_id: str
    country_id: int
    competition_id: int
    runtime_owner: str
    selection_supported: bool
    runtime_materialized: bool
    human_match_supported: bool
    annual_progression_supported: bool
    blocker_codes: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.blocker_codes

    def as_dict(self) -> dict:
        return {
            "scope_id": self.scope_id,
            "country_id": self.country_id,
            "competition_id": self.competition_id,
            "runtime_owner": self.runtime_owner,
            "selection_supported": self.selection_supported,
            "runtime_materialized": self.runtime_materialized,
            "human_match_supported": self.human_match_supported,
            "annual_progression_supported": self.annual_progression_supported,
            "blocker_codes": list(self.blocker_codes),
            "complete": self.complete,
        }


@dataclass(frozen=True)
class RuntimeOwnerCapabilityAudit:
    catalog_sha256: str
    entries: tuple[RuntimeOwnerCapabilityEntry, ...]

    @property
    def supported_scope_ids(self) -> tuple[str, ...]:
        return tuple(entry.scope_id for entry in self.entries if entry.complete)

    @property
    def blocked_scope_ids(self) -> tuple[str, ...]:
        return tuple(entry.scope_id for entry in self.entries if not entry.complete)

    @property
    def blocker_codes(self) -> tuple[str, ...]:
        output: list[str] = []
        seen: set[str] = set()
        for entry in self.entries:
            for code in entry.blocker_codes:
                if code not in seen:
                    output.append(code)
                    seen.add(code)
        return tuple(output)

    @property
    def complete(self) -> bool:
        return bool(self.entries) and not self.blocked_scope_ids

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "scope_entry_count": len(self.entries),
            "supported_scope_ids": list(self.supported_scope_ids),
            "blocked_scope_ids": list(self.blocked_scope_ids),
            "blocker_codes": list(self.blocker_codes),
            "complete": self.complete,
            "entries": [entry.as_dict() for entry in self.entries],
        }


def _exact_unique_ids(values: Iterable[int], *, label: str) -> tuple[int, ...]:
    output: list[int] = []
    seen: set[int] = set()
    for value in values:
        if type(value) is not int or value < 0:
            raise Gate17RuntimeOwnerCapabilityError(
                f"{label} must contain exact non-negative integers"
            )
        if value in seen:
            raise Gate17RuntimeOwnerCapabilityError(
                f"{label} contains duplicate ID {value}"
            )
        output.append(value)
        seen.add(value)
    return tuple(output)


def normalized_surface(
    *,
    selectable_club_ids: Iterable[int],
    fixed_primary_competition_ids: Iterable[int],
    materialized_primary_procedural_ids: Iterable[int],
    materialized_secondary_procedural_ids: Iterable[int],
    human_primary_procedural_ids: Iterable[int],
    human_secondary_procedural_ids: Iterable[int],
    annual_progression_country_ids: Iterable[int],
) -> HumanRuntimeOwnerSurface:
    return HumanRuntimeOwnerSurface(
        selectable_club_ids=_exact_unique_ids(
            selectable_club_ids, label="selectable club IDs"
        ),
        fixed_primary_competition_ids=_exact_unique_ids(
            fixed_primary_competition_ids, label="fixed primary competition IDs"
        ),
        materialized_primary_procedural_ids=_exact_unique_ids(
            materialized_primary_procedural_ids,
            label="materialized primary procedural IDs",
        ),
        materialized_secondary_procedural_ids=_exact_unique_ids(
            materialized_secondary_procedural_ids,
            label="materialized secondary procedural IDs",
        ),
        human_primary_procedural_ids=_exact_unique_ids(
            human_primary_procedural_ids,
            label="human primary procedural IDs",
        ),
        human_secondary_procedural_ids=_exact_unique_ids(
            human_secondary_procedural_ids,
            label="human secondary procedural IDs",
        ),
        annual_progression_country_ids=_exact_unique_ids(
            annual_progression_country_ids,
            label="annual progression country IDs",
        ),
    )


def audit_runtime_owner_capability(
    plan: PlayableLeagueRuntimePlan,
    surface: HumanRuntimeOwnerSurface,
) -> RuntimeOwnerCapabilityAudit:
    """Compare exact TeamSelect runtime ownership with current runtime surfaces."""
    if type(plan) is not PlayableLeagueRuntimePlan:
        raise Gate17RuntimeOwnerCapabilityError(
            "runtime-owner capability audit requires exact PlayableLeagueRuntimePlan"
        )
    if type(surface) is not HumanRuntimeOwnerSurface:
        raise Gate17RuntimeOwnerCapabilityError(
            "runtime-owner capability audit requires exact HumanRuntimeOwnerSurface"
        )
    if not plan.entries:
        raise Gate17RuntimeOwnerCapabilityError("runtime ownership plan is empty")

    selectable = set(surface.selectable_club_ids)
    fixed = set(surface.fixed_primary_competition_ids)
    primary_live = set(surface.materialized_primary_procedural_ids)
    secondary_live = set(surface.materialized_secondary_procedural_ids)
    primary_human = set(surface.human_primary_procedural_ids)
    secondary_human = set(surface.human_secondary_procedural_ids)
    progression_countries = set(surface.annual_progression_country_ids)

    entries: list[RuntimeOwnerCapabilityEntry] = []
    for planned in plan.entries:
        competition_id = int(planned.competition_id)
        selection_supported = all(
            int(club_id) in selectable for club_id in planned.selectable_club_ids
        )

        if planned.runtime_owner == RUNTIME_FIXED_PRIMARY:
            runtime_materialized = competition_id in fixed
            human_match_supported = competition_id in fixed
        elif planned.runtime_owner == RUNTIME_PROCEDURAL_PRIMARY:
            runtime_materialized = competition_id in primary_live
            human_match_supported = competition_id in primary_human
        elif planned.runtime_owner == RUNTIME_PROCEDURAL_SECONDARY:
            runtime_materialized = competition_id in secondary_live
            human_match_supported = competition_id in secondary_human
        else:
            raise Gate17RuntimeOwnerCapabilityError(
                f"unknown runtime owner {planned.runtime_owner!r}"
            )

        annual_progression_supported = (
            int(planned.country_id) in progression_countries
        )
        blockers: list[str] = []
        if not selection_supported:
            blockers.append("human_selection_unavailable")
        if not runtime_materialized:
            blockers.append("runtime_owner_not_materialized")
        if not human_match_supported:
            blockers.append("human_match_dispatch_missing")
        if not annual_progression_supported:
            blockers.append("annual_progression_country_missing")

        entries.append(
            RuntimeOwnerCapabilityEntry(
                scope_id=str(planned.scope_id),
                country_id=int(planned.country_id),
                competition_id=competition_id,
                runtime_owner=str(planned.runtime_owner),
                selection_supported=selection_supported,
                runtime_materialized=runtime_materialized,
                human_match_supported=human_match_supported,
                annual_progression_supported=annual_progression_supported,
                blocker_codes=tuple(blockers),
            )
        )

    return RuntimeOwnerCapabilityAudit(
        catalog_sha256=str(plan.catalog_sha256),
        entries=tuple(entries),
    )


def run_canonical_runtime_owner_capability(
    game_dir: str | Path,
) -> RuntimeOwnerCapabilityAudit:
    """Measure the current canonical single-human controller without mutation.

    The explicit empty procedural human-dispatch sets mirror the current
    `play_user_primary_match()` implementation: it handles Premier League and
    Cup entry families but has no `procedural_league` human branch. Secondary
    procedural runtime state likewise has no current GameState container.
    Annual LeagueAllocation commit remains the English-only transition path.
    """
    from human_gameplay import HumanGameplayController

    plan = load_canonical_playable_league_runtime_plan(game_dir)
    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=1,
        match_engine_seed=1,
    )
    if controller.state.premier_league is None:
        raise Gate17RuntimeOwnerCapabilityError(
            "canonical controller has no fixed Premier League runtime"
        )

    surface = normalized_surface(
        selectable_club_ids=tuple(
            int(value) for value in controller.state.premier_league.club_ids
        ),
        fixed_primary_competition_ids=(0,),
        materialized_primary_procedural_ids=tuple(
            dict.fromkeys(
                int(competition_id)
                for competition_id, _context in controller.state.procedural_leagues
            )
        ),
        materialized_secondary_procedural_ids=(),
        human_primary_procedural_ids=(),
        human_secondary_procedural_ids=(),
        annual_progression_country_ids=(26,),
    )
    return audit_runtime_owner_capability(plan, surface)
