"""Read-only Gate-17 audit of playable-country annual progression readiness.

This module connects the source-backed allocation plan to an already-completed
runtime state without modifying GameState. It resolves each required ranking
endpoint exactly once, verifies the runtime membership map did not change during
resolution, audits ranking readiness, and only then previews all playable-country
LeagueAllocation exchanges through the recovered generic executor.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gate17_allocation_ranking_capability import (
    AllocationRankingCapabilityAudit,
    Gate17AllocationRankingCapabilityError,
    audit_allocation_ranking_capability,
)
from gate17_country_allocation_scope import PlayableCountryAllocationPlan
from gate17_playable_allocation_preview import (
    Gate17PlayableAllocationPreviewError,
    PlayableAllocationPreview,
    preview_playable_allocation_exchanges,
)


class ProgressionRuntimeState(Protocol):
    league_allocation_records: tuple[object, ...]
    club_competition_membership: dict[int, int]

    def season_transition_ranking(
        self,
        competition_id: int,
    ) -> tuple[int, ...] | None:
        ...


class Gate17RuntimeProgressionAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeProgressionAudit:
    catalog_sha256: str
    required_endpoint_ids: tuple[int, ...]
    resolved_rankings: dict[int, tuple[int, ...] | None]
    ranking_capability: AllocationRankingCapabilityAudit
    allocation_preview: PlayableAllocationPreview | None
    runtime_memberships_unchanged: bool

    @property
    def complete(self) -> bool:
        return (
            self.runtime_memberships_unchanged
            and self.ranking_capability.complete
            and self.allocation_preview is not None
        )

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "required_endpoint_ids": list(self.required_endpoint_ids),
            "resolved_rankings": {
                str(competition_id): (
                    None if ranking is None else list(ranking)
                )
                for competition_id, ranking in self.resolved_rankings.items()
            },
            "ranking_capability": self.ranking_capability.as_dict(),
            "allocation_preview": (
                None
                if self.allocation_preview is None
                else self.allocation_preview.as_dict()
            ),
            "runtime_memberships_unchanged": self.runtime_memberships_unchanged,
            "complete": self.complete,
        }


def _snapshot_memberships(values) -> dict[int, int]:
    if not isinstance(values, dict):
        raise Gate17RuntimeProgressionAuditError(
            "runtime club_competition_membership must be a dict"
        )
    output: dict[int, int] = {}
    for club_id, competition_id in values.items():
        if type(club_id) is not int or club_id < 0:
            raise Gate17RuntimeProgressionAuditError(
                "runtime membership club IDs must be non-negative integers"
            )
        if type(competition_id) is not int or competition_id < 0:
            raise Gate17RuntimeProgressionAuditError(
                "runtime membership competition IDs must be non-negative integers"
            )
        output[club_id] = competition_id
    return output


def _required_endpoint_ids(
    plan: PlayableCountryAllocationPlan,
) -> tuple[int, ...]:
    endpoint_ids: list[int] = []
    seen: set[int] = set()
    for country in plan.countries:
        for raw_id in country.ranking_endpoint_ids:
            if type(raw_id) is not int or raw_id < 0:
                raise Gate17RuntimeProgressionAuditError(
                    "country allocation plan contains invalid ranking endpoint ID"
                )
            endpoint_id = int(raw_id)
            if endpoint_id not in seen:
                endpoint_ids.append(endpoint_id)
                seen.add(endpoint_id)
    return tuple(endpoint_ids)


def audit_runtime_playable_progression(
    plan: PlayableCountryAllocationPlan,
    state: ProgressionRuntimeState,
) -> RuntimeProgressionAudit:
    """Audit one runtime state without committing any annual membership change."""

    if type(plan) is not PlayableCountryAllocationPlan:
        raise Gate17RuntimeProgressionAuditError(
            "runtime progression audit requires exact PlayableCountryAllocationPlan"
        )
    if state is None:
        raise Gate17RuntimeProgressionAuditError(
            "runtime progression audit requires a state object"
        )

    try:
        records = tuple(state.league_allocation_records)
        membership_source = state.club_competition_membership
        resolver = state.season_transition_ranking
    except AttributeError as exc:
        raise Gate17RuntimeProgressionAuditError(
            "runtime state lacks allocation records, memberships or ranking resolver"
        ) from exc

    if not callable(resolver):
        raise Gate17RuntimeProgressionAuditError(
            "runtime season_transition_ranking must be callable"
        )

    before = _snapshot_memberships(membership_source)
    endpoint_ids = _required_endpoint_ids(plan)

    rankings: dict[int, tuple[int, ...] | None] = {}
    for endpoint_id in endpoint_ids:
        raw = resolver(endpoint_id)
        if raw is None:
            rankings[endpoint_id] = None
        else:
            if type(raw) is not tuple:
                raise Gate17RuntimeProgressionAuditError(
                    f"runtime ranking {endpoint_id} must be an immutable tuple or None"
                )
            rankings[endpoint_id] = tuple(raw)

    after_resolution = _snapshot_memberships(state.club_competition_membership)
    if after_resolution != before:
        raise Gate17RuntimeProgressionAuditError(
            "ranking resolution mutated runtime club competition memberships"
        )

    try:
        ranking_capability = audit_allocation_ranking_capability(
            plan,
            records,
            rankings,
        )
    except Gate17AllocationRankingCapabilityError as exc:
        raise Gate17RuntimeProgressionAuditError(
            f"runtime ranking capability audit failed: {exc}"
        ) from exc

    preview = None
    if ranking_capability.complete:
        try:
            preview = preview_playable_allocation_exchanges(
                plan,
                records,
                rankings,
                before,
            )
        except Gate17PlayableAllocationPreviewError as exc:
            raise Gate17RuntimeProgressionAuditError(
                f"runtime playable allocation preview failed: {exc}"
            ) from exc

    final_memberships = _snapshot_memberships(state.club_competition_membership)
    if final_memberships != before:
        raise Gate17RuntimeProgressionAuditError(
            "playable progression audit mutated runtime memberships"
        )

    return RuntimeProgressionAudit(
        catalog_sha256=str(plan.catalog_sha256),
        required_endpoint_ids=endpoint_ids,
        resolved_rankings=rankings,
        ranking_capability=ranking_capability,
        allocation_preview=preview,
        runtime_memberships_unchanged=True,
    )
