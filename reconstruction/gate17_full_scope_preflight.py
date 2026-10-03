"""Aggregate fail-closed Gate-17 full-scope implementation readiness.

This module creates no gameplay capability. It joins the canonical human-control
scope audit with the read-only runtime progression audit. Both inputs must target
the same source-backed TeamSelect playable-scope catalog.
"""
from __future__ import annotations

from dataclasses import dataclass

from gate17_human_scope_capability import HumanScopeCapabilityAudit
from gate17_runtime_progression_audit import RuntimeProgressionAudit


class Gate17FullScopePreflightError(RuntimeError):
    pass


@dataclass(frozen=True)
class FullScopePreflight:
    catalog_sha256: str
    scope_entry_count: int
    human_scope_complete: bool
    progression_runtime_complete: bool
    progression_rankings_complete: bool
    allocation_preview_complete: bool
    runtime_memberships_unchanged: bool
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
            "progression_runtime_complete": self.progression_runtime_complete,
            "progression_rankings_complete": self.progression_rankings_complete,
            "allocation_preview_complete": self.allocation_preview_complete,
            "runtime_memberships_unchanged": self.runtime_memberships_unchanged,
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
    progression: RuntimeProgressionAudit,
) -> FullScopePreflight:
    """Join independent capability audits without mutating runtime state."""

    if type(human_scope) is not HumanScopeCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact HumanScopeCapabilityAudit"
        )
    if type(progression) is not RuntimeProgressionAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact RuntimeProgressionAudit"
        )
    if not human_scope.entries:
        raise Gate17FullScopePreflightError(
            "human-scope audit contains no TeamSelect scope entries"
        )

    catalog_sha = str(human_scope.catalog_sha256)
    if str(progression.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "human-scope and progression audits target different catalogs"
        )
    if str(progression.ranking_capability.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "runtime ranking capability targets a different playable-scope catalog"
        )

    preview = progression.allocation_preview
    if preview is not None:
        if str(preview.catalog_sha256) != catalog_sha:
            raise Gate17FullScopePreflightError(
                "runtime allocation preview targets a different playable-scope catalog"
            )
        if preview.ranking_capability != progression.ranking_capability:
            raise Gate17FullScopePreflightError(
                "runtime allocation preview ranking audit does not match runtime audit"
            )

        previewed_ids = tuple(int(value) for value in preview.assigned_allocation_ids)
        if len(set(previewed_ids)) != len(previewed_ids):
            raise Gate17FullScopePreflightError(
                "runtime allocation preview contains duplicate assigned allocation IDs"
            )
        expected_allocation_set = set(
            progression.ranking_capability.assigned_allocation_ids
        )
        if set(previewed_ids) != expected_allocation_set:
            raise Gate17FullScopePreflightError(
                "runtime allocation preview does not cover exact assigned allocation set"
            )
        if set(preview.memberships_before) != set(preview.memberships_after):
            raise Gate17FullScopePreflightError(
                "runtime allocation preview membership key set changed"
            )
    else:
        previewed_ids = ()

    blockers: list[str] = []
    if not human_scope.complete:
        blockers.append("human_scope_incomplete")
    if not progression.ranking_capability.complete:
        blockers.append("progression_rankings_incomplete")
    if preview is None:
        blockers.append("allocation_preview_missing")
    if not progression.runtime_memberships_unchanged:
        blockers.append("runtime_membership_mutation")
    if not progression.complete and not blockers:
        blockers.append("runtime_progression_incomplete")

    return FullScopePreflight(
        catalog_sha256=catalog_sha,
        scope_entry_count=len(human_scope.entries),
        human_scope_complete=human_scope.complete,
        progression_runtime_complete=progression.complete,
        progression_rankings_complete=progression.ranking_capability.complete,
        allocation_preview_complete=preview is not None,
        runtime_memberships_unchanged=progression.runtime_memberships_unchanged,
        supported_scope_ids=tuple(human_scope.supported_scope_ids),
        unsupported_scope_ids=tuple(human_scope.unsupported_scope_ids),
        unresolved_allocation_ids=tuple(
            progression.ranking_capability.unresolved_allocation_ids
        ),
        unresolved_ranking_endpoint_ids=tuple(
            progression.ranking_capability.unresolved_endpoint_ids
        ),
        previewed_allocation_ids=previewed_ids,
        blocker_codes=tuple(blockers),
    )
