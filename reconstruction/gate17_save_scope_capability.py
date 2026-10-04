"""Fail-closed Gate-17 audit of per-scope internal save/reload capability.

This module does not create save compatibility or execute private canonical
continuation runs. It compares the source-backed TeamSelect runtime ownership
plan with the clean-room save/continuation surfaces that currently exist.

Fixed-primary and procedural-primary owners already have dedicated internal
save/reload continuation harnesses. Procedural-secondary owners do not yet have
an independent live runtime container, serialization path, or post-load human
continuation route and must therefore remain explicitly blocked.
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


class Gate17SaveScopeCapabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class SaveScopeCapabilitySurface:
    fixed_primary_serialized_scope_ids: tuple[str, ...]
    fixed_primary_continuation_scope_ids: tuple[str, ...]
    procedural_primary_serialized_scope_ids: tuple[str, ...]
    procedural_primary_continuation_scope_ids: tuple[str, ...]
    procedural_secondary_serialized_scope_ids: tuple[str, ...]
    procedural_secondary_continuation_scope_ids: tuple[str, ...]


@dataclass(frozen=True)
class SaveScopeCapabilityEntry:
    scope_id: str
    competition_id: int
    runtime_owner: str
    serialization_supported: bool
    continuation_supported: bool
    blocker_codes: tuple[str, ...]

    @property
    def complete(self) -> bool:
        return not self.blocker_codes

    def as_dict(self) -> dict:
        return {
            "scope_id": self.scope_id,
            "competition_id": self.competition_id,
            "runtime_owner": self.runtime_owner,
            "serialization_supported": self.serialization_supported,
            "continuation_supported": self.continuation_supported,
            "blocker_codes": list(self.blocker_codes),
            "complete": self.complete,
        }


@dataclass(frozen=True)
class SaveScopeCapabilityAudit:
    catalog_sha256: str
    entries: tuple[SaveScopeCapabilityEntry, ...]

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


def _exact_unique_scope_ids(
    values: Iterable[str],
    *,
    label: str,
) -> tuple[str, ...]:
    output: list[str] = []
    seen: set[str] = set()
    for raw in values:
        if type(raw) is not str:
            raise Gate17SaveScopeCapabilityError(
                f"{label} must contain exact strings"
            )
        value = raw.strip()
        if not value or value != raw:
            raise Gate17SaveScopeCapabilityError(
                f"{label} must contain non-empty canonical scope IDs"
            )
        if value in seen:
            raise Gate17SaveScopeCapabilityError(
                f"{label} contains duplicate scope ID {value}"
            )
        output.append(value)
        seen.add(value)
    return tuple(output)


def normalized_surface(
    *,
    fixed_primary_serialized_scope_ids: Iterable[str],
    fixed_primary_continuation_scope_ids: Iterable[str],
    procedural_primary_serialized_scope_ids: Iterable[str],
    procedural_primary_continuation_scope_ids: Iterable[str],
    procedural_secondary_serialized_scope_ids: Iterable[str],
    procedural_secondary_continuation_scope_ids: Iterable[str],
) -> SaveScopeCapabilitySurface:
    values = {
        "fixed_primary_serialized_scope_ids": _exact_unique_scope_ids(
            fixed_primary_serialized_scope_ids,
            label="fixed primary serialized scope IDs",
        ),
        "fixed_primary_continuation_scope_ids": _exact_unique_scope_ids(
            fixed_primary_continuation_scope_ids,
            label="fixed primary continuation scope IDs",
        ),
        "procedural_primary_serialized_scope_ids": _exact_unique_scope_ids(
            procedural_primary_serialized_scope_ids,
            label="procedural primary serialized scope IDs",
        ),
        "procedural_primary_continuation_scope_ids": _exact_unique_scope_ids(
            procedural_primary_continuation_scope_ids,
            label="procedural primary continuation scope IDs",
        ),
        "procedural_secondary_serialized_scope_ids": _exact_unique_scope_ids(
            procedural_secondary_serialized_scope_ids,
            label="procedural secondary serialized scope IDs",
        ),
        "procedural_secondary_continuation_scope_ids": _exact_unique_scope_ids(
            procedural_secondary_continuation_scope_ids,
            label="procedural secondary continuation scope IDs",
        ),
    }

    owner_sets = (
        set(values["fixed_primary_serialized_scope_ids"])
        | set(values["fixed_primary_continuation_scope_ids"]),
        set(values["procedural_primary_serialized_scope_ids"])
        | set(values["procedural_primary_continuation_scope_ids"]),
        set(values["procedural_secondary_serialized_scope_ids"])
        | set(values["procedural_secondary_continuation_scope_ids"]),
    )
    if (
        owner_sets[0] & owner_sets[1]
        or owner_sets[0] & owner_sets[2]
        or owner_sets[1] & owner_sets[2]
    ):
        raise Gate17SaveScopeCapabilityError(
            "save capability scope IDs overlap across runtime owners"
        )
    return SaveScopeCapabilitySurface(**values)


def audit_save_scope_capability(
    plan: PlayableLeagueRuntimePlan,
    surface: SaveScopeCapabilitySurface,
) -> SaveScopeCapabilityAudit:
    """Compare exact TeamSelect scopes with available save/continuation surfaces."""
    if type(plan) is not PlayableLeagueRuntimePlan:
        raise Gate17SaveScopeCapabilityError(
            "save-scope capability audit requires exact PlayableLeagueRuntimePlan"
        )
    if type(surface) is not SaveScopeCapabilitySurface:
        raise Gate17SaveScopeCapabilityError(
            "save-scope capability audit requires exact SaveScopeCapabilitySurface"
        )
    if not plan.entries:
        raise Gate17SaveScopeCapabilityError("runtime ownership plan is empty")

    fixed_serialized = set(surface.fixed_primary_serialized_scope_ids)
    fixed_continuation = set(surface.fixed_primary_continuation_scope_ids)
    primary_serialized = set(surface.procedural_primary_serialized_scope_ids)
    primary_continuation = set(surface.procedural_primary_continuation_scope_ids)
    secondary_serialized = set(surface.procedural_secondary_serialized_scope_ids)
    secondary_continuation = set(surface.procedural_secondary_continuation_scope_ids)
    all_surface_ids = (
        fixed_serialized
        | fixed_continuation
        | primary_serialized
        | primary_continuation
        | secondary_serialized
        | secondary_continuation
    )
    known_scope_ids = {str(entry.scope_id) for entry in plan.entries}
    outside = all_surface_ids - known_scope_ids
    if outside:
        raise Gate17SaveScopeCapabilityError(
            f"save capability references scopes outside TeamSelect catalog: {sorted(outside)}"
        )

    entries: list[SaveScopeCapabilityEntry] = []
    for planned in plan.entries:
        scope_id = str(planned.scope_id)
        owner = str(planned.runtime_owner)
        if owner == RUNTIME_FIXED_PRIMARY:
            serialization_supported = scope_id in fixed_serialized
            continuation_supported = scope_id in fixed_continuation
        elif owner == RUNTIME_PROCEDURAL_PRIMARY:
            serialization_supported = scope_id in primary_serialized
            continuation_supported = scope_id in primary_continuation
        elif owner == RUNTIME_PROCEDURAL_SECONDARY:
            serialization_supported = scope_id in secondary_serialized
            continuation_supported = scope_id in secondary_continuation
        else:
            raise Gate17SaveScopeCapabilityError(
                f"unknown runtime owner {owner!r}"
            )

        blockers: list[str] = []
        if not serialization_supported:
            blockers.append("save_serialization_missing")
        if not continuation_supported:
            blockers.append("save_reload_continuation_missing")
        entries.append(
            SaveScopeCapabilityEntry(
                scope_id=scope_id,
                competition_id=int(planned.competition_id),
                runtime_owner=owner,
                serialization_supported=serialization_supported,
                continuation_supported=continuation_supported,
                blocker_codes=tuple(blockers),
            )
        )

    return SaveScopeCapabilityAudit(
        catalog_sha256=str(plan.catalog_sha256),
        entries=tuple(entries),
    )


def run_canonical_save_scope_capability(
    game_dir: str | Path,
) -> SaveScopeCapabilityAudit:
    """Report the current source-backed save-capability boundary.

    This is implementation/tooling readiness only. It does not claim that the
    private canonical primary-container sweep or any final Windows receipt has
    been executed.
    """
    plan = load_canonical_playable_league_runtime_plan(game_dir)
    surface = normalized_surface(
        fixed_primary_serialized_scope_ids=plan.fixed_primary_scope_ids,
        fixed_primary_continuation_scope_ids=plan.fixed_primary_scope_ids,
        procedural_primary_serialized_scope_ids=plan.procedural_primary_scope_ids,
        procedural_primary_continuation_scope_ids=plan.procedural_primary_scope_ids,
        procedural_secondary_serialized_scope_ids=(),
        procedural_secondary_continuation_scope_ids=(),
    )
    return audit_save_scope_capability(plan, surface)
