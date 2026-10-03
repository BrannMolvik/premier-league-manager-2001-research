"""Aggregate fail-closed Gate-17 full-scope implementation readiness.

This module does not create gameplay capability. It only joins already separate
source-backed audits for:
- human club-selection coverage over the original TeamSelect scope;
- LeagueAllocation ranking endpoint readiness;
- a non-mutating preview of all playable-country allocation exchanges.

All inputs must target the same canonical playable-scope catalog.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate17_allocation_ranking_capability import (
    AllocationRankingCapabilityAudit,
)
from gate17_human_scope_capability import (
    HumanScopeCapabilityAudit,
)
from gate17_playable_allocation_preview import (
    PlayableAllocationPreview,
)


class Gate17FullScopePreflightError(RuntimeError):
    pass


@dataclass(frozen=True)
class FullScopePreflight:
    catalog_sha256: str
    scope_entry_count: int
    human_scope_complete: bool
    progression_rankings_complete: bool
    allocation_preview_complete: bool
    supported_scope_ids: tuple[str, ...]
    unsupported_scope_ids: tuple[str, ...]
    unresolved_allocation_ids: tuple[int, ...]
    unresolved_ranking_endpoint_ids: tuple[int, ...]
    previewed_allocation_ids: tuple[int, ...]
    blocker_codes: tuple[str, ...]

    @property
    def ready_for_full_runtime_validation(self) -> bool:
        return not self.blocker_codes

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "scope_entry_count": self.scope_entry_count,
            "human_scope_complete": self.human_scope_complete,
            "progression_rankings_complete": self.progression_rankings_complete,
            "allocation_preview_complete": self.allocation_preview_complete,
            "supported_scope_ids": list(self.supported_scope_ids),
            "unsupported_scope_ids": list(self.unsupported_scope_ids),
            "unresolved_allocation_ids": list(self.unresolved_allocation_ids),
            "unresolved_ranking_endpoint_ids": list(
                self.unresolved_ranking_endpoint_ids
            ),
            "previewed_allocation_ids": list(self.previewed_allocation_ids),
            "blocker_codes": list(self.blocker_codes),
            "ready_for_full_runtime_validation": self.ready_for_full_runtime_validation,
        }


def build_full_scope_preflight(
    human_scope: HumanScopeCapabilityAudit,
    ranking_capability: AllocationRankingCapabilityAudit,
    allocation_preview: PlayableAllocationPreview | None,
) -> FullScopePreflight:
    """Require all independent full-scope audits to agree fail-closed."""

    if type(human_scope) is not HumanScopeCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact HumanScopeCapabilityAudit"
        )
    if type(ranking_capability) is not AllocationRankingCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact AllocationRankingCapabilityAudit"
        )
    if allocation_preview is not None and type(allocation_preview) is not PlayableAllocationPreview:
        raise Gate17FullScopePreflightError(
            "allocation preview must be exact PlayableAllocationPreview or None"
        )

    catalog_sha = str(human_scope.catalog_sha256)
    if str(ranking_capability.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "human-scope and progression audits target different catalogs"
        )
    if allocation_preview is not None and str(allocation_preview.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "allocation preview targets a different playable-scope catalog"
        )

    if not human_scope.entries:
        raise Gate17FullScopePreflightError(
            "human-scope audit contains no TeamSelect scope entries"
        )

    preview_complete = allocation_preview is not None
    previewed_ids = (
        ()
        if allocation_preview is None
        else tuple(int(value) for value in allocation_preview.assigned_allocation_ids)
    )

    if allocation_preview is not None:
        if allocation_preview.ranking_capability != ranking_capability:
            raise Gate17FullScopePreflightError(
                "allocation preview ranking audit does not match supplied audit"
            )
        if set(previewed_ids) != set(ranking_capability.assigned_allocation_ids):
            raise Gate17FullScopePreflightError(
                "allocation preview does not cover exact assigned allocation set"
            )

    blockers: list[str] = []
    if not human_scope.complete:
        blockers.append("human_scope_incomplete")
    if not ranking_capability.complete:
        blockers.append("progression_rankings_incomplete")
    if allocation_preview is None:
        blockers.append("allocation_preview_missing")

    return FullScopePreflight(
        catalog_sha256=catalog_sha,
        scope_entry_count=len(human_scope.entries),
        human_scope_complete=human_scope.complete,
        progression_rankings_complete=ranking_capability.complete,
        allocation_preview_complete=preview_complete,
        supported_scope_ids=tuple(human_scope.supported_scope_ids),
        unsupported_scope_ids=tuple(human_scope.unsupported_scope_ids),
        unresolved_allocation_ids=tuple(
            ranking_capability.unresolved_allocation_ids
        ),
        unresolved_ranking_endpoint_ids=tuple(
            ranking_capability.unresolved_endpoint_ids
        ),
        previewed_allocation_ids=previewed_ids,
        blocker_codes=tuple(blockers),
    )
