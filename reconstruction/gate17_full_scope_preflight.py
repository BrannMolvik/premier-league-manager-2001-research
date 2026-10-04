"""Aggregate fail-closed Gate-17 full-scope implementation readiness.

This module creates no gameplay capability. It joins the canonical human-control
scope audit, the current runtime-owner capability audit, the source-proven
multi-human capability audit, the per-scope save/reload capability audit, and
the read-only runtime progression audit. Catalog-bound inputs must target the
same source-backed TeamSelect playable-scope catalog.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

from gate17_human_scope_capability import (
    HumanScopeCapabilityAudit,
    run_canonical_human_scope_capability,
)
from gate17_multi_human_capability import (
    MultiHumanCapabilityAudit,
    ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS,
    run_current_multi_human_capability,
)
from gate17_runtime_owner_capability import (
    RuntimeOwnerCapabilityAudit,
    run_canonical_runtime_owner_capability,
)
from gate17_save_scope_capability import (
    SaveScopeCapabilityAudit,
    run_canonical_save_scope_capability,
)
from gate17_runtime_progression_audit import (
    RuntimeProgressionAudit,
    audit_runtime_playable_progression,
)


class Gate17FullScopePreflightError(RuntimeError):
    pass


@dataclass(frozen=True)
class FullScopePreflight:
    catalog_sha256: str
    scope_entry_count: int
    human_scope_complete: bool
    runtime_owner_complete: bool
    save_scope_complete: bool
    save_scope_supported_scope_ids: tuple[str, ...]
    save_scope_blocked_scope_ids: tuple[str, ...]
    save_scope_blocker_codes: tuple[str, ...]
    multi_human_complete: bool
    multi_human_required_users: int
    multi_human_gameplay_users_supported: int
    multi_human_blocker_codes: tuple[str, ...]
    progression_runtime_complete: bool
    progression_rankings_complete: bool
    allocation_preview_complete: bool
    runtime_memberships_unchanged: bool
    supported_scope_ids: tuple[str, ...]
    unsupported_scope_ids: tuple[str, ...]
    runtime_owner_supported_scope_ids: tuple[str, ...]
    runtime_owner_blocked_scope_ids: tuple[str, ...]
    runtime_owner_blocker_codes: tuple[str, ...]
    unresolved_allocation_ids: tuple[int, ...]
    unresolved_ranking_endpoint_ids: tuple[int, ...]
    previewed_allocation_ids: tuple[int, ...]
    blocker_codes: tuple[str, ...]

    @property
    def ready_for_full_runtime_validation(self) -> bool:
        return not self.blocker_codes

    def as_dict(self) -> dict:
        return {
            "schema_version": 4,
            "catalog_sha256": self.catalog_sha256,
            "scope_entry_count": self.scope_entry_count,
            "human_scope_complete": self.human_scope_complete,
            "runtime_owner_complete": self.runtime_owner_complete,
            "save_scope_complete": self.save_scope_complete,
            "save_scope_supported_scope_ids": list(
                self.save_scope_supported_scope_ids
            ),
            "save_scope_blocked_scope_ids": list(
                self.save_scope_blocked_scope_ids
            ),
            "save_scope_blocker_codes": list(self.save_scope_blocker_codes),
            "multi_human_complete": self.multi_human_complete,
            "multi_human_required_users": self.multi_human_required_users,
            "multi_human_gameplay_users_supported": (
                self.multi_human_gameplay_users_supported
            ),
            "multi_human_blocker_codes": list(self.multi_human_blocker_codes),
            "progression_runtime_complete": self.progression_runtime_complete,
            "progression_rankings_complete": self.progression_rankings_complete,
            "allocation_preview_complete": self.allocation_preview_complete,
            "runtime_memberships_unchanged": self.runtime_memberships_unchanged,
            "supported_scope_ids": list(self.supported_scope_ids),
            "unsupported_scope_ids": list(self.unsupported_scope_ids),
            "runtime_owner_supported_scope_ids": list(
                self.runtime_owner_supported_scope_ids
            ),
            "runtime_owner_blocked_scope_ids": list(
                self.runtime_owner_blocked_scope_ids
            ),
            "runtime_owner_blocker_codes": list(self.runtime_owner_blocker_codes),
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
    runtime_owner: RuntimeOwnerCapabilityAudit,
    save_scope: SaveScopeCapabilityAudit,
    multi_human: MultiHumanCapabilityAudit,
    progression: RuntimeProgressionAudit,
) -> FullScopePreflight:
    """Join independent capability audits without mutating runtime state."""

    if type(human_scope) is not HumanScopeCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact HumanScopeCapabilityAudit"
        )
    if type(runtime_owner) is not RuntimeOwnerCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact RuntimeOwnerCapabilityAudit"
        )
    if type(save_scope) is not SaveScopeCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact SaveScopeCapabilityAudit"
        )
    if type(multi_human) is not MultiHumanCapabilityAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact MultiHumanCapabilityAudit"
        )
    if type(progression) is not RuntimeProgressionAudit:
        raise Gate17FullScopePreflightError(
            "preflight requires exact RuntimeProgressionAudit"
        )
    if (
        int(multi_human.required_simultaneous_users)
        != ORIGINAL_MAX_SIMULTANEOUS_HUMAN_USERS
    ):
        raise Gate17FullScopePreflightError(
            "multi-human audit required user count differs from source-proven six-user contract"
        )
    if not human_scope.entries:
        raise Gate17FullScopePreflightError(
            "human-scope audit contains no TeamSelect scope entries"
        )
    if not runtime_owner.entries:
        raise Gate17FullScopePreflightError(
            "runtime-owner audit contains no TeamSelect scope entries"
        )
    if not save_scope.entries:
        raise Gate17FullScopePreflightError(
            "save-scope audit contains no TeamSelect scope entries"
        )

    catalog_sha = str(human_scope.catalog_sha256)
    if str(runtime_owner.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "human-scope and runtime-owner audits target different catalogs"
        )
    if str(save_scope.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "human-scope and save-scope audits target different catalogs"
        )
    if str(progression.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "human-scope and progression audits target different catalogs"
        )
    if str(progression.ranking_capability.catalog_sha256) != catalog_sha:
        raise Gate17FullScopePreflightError(
            "runtime ranking capability targets a different playable-scope catalog"
        )

    human_scope_ids = tuple(str(entry.scope_id) for entry in human_scope.entries)
    runtime_owner_scope_ids = tuple(
        str(entry.scope_id) for entry in runtime_owner.entries
    )
    if runtime_owner_scope_ids != human_scope_ids:
        raise Gate17FullScopePreflightError(
            "runtime-owner audit scope IDs do not exactly match human-scope audit"
        )
    save_scope_ids = tuple(str(entry.scope_id) for entry in save_scope.entries)
    if save_scope_ids != human_scope_ids:
        raise Gate17FullScopePreflightError(
            "save-scope audit scope IDs do not exactly match human-scope audit"
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
    if not runtime_owner.complete:
        blockers.append("runtime_owner_capability_incomplete")
    if not save_scope.complete:
        blockers.append("save_scope_capability_incomplete")
    if not multi_human.complete:
        blockers.append("multi_human_capability_incomplete")
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
        runtime_owner_complete=runtime_owner.complete,
        save_scope_complete=save_scope.complete,
        save_scope_supported_scope_ids=tuple(save_scope.supported_scope_ids),
        save_scope_blocked_scope_ids=tuple(save_scope.blocked_scope_ids),
        save_scope_blocker_codes=tuple(save_scope.blocker_codes),
        multi_human_complete=multi_human.complete,
        multi_human_required_users=int(multi_human.required_simultaneous_users),
        multi_human_gameplay_users_supported=int(
            multi_human.gameplay_simultaneous_users_supported
        ),
        multi_human_blocker_codes=tuple(multi_human.blocker_codes),
        progression_runtime_complete=progression.complete,
        progression_rankings_complete=progression.ranking_capability.complete,
        allocation_preview_complete=preview is not None,
        runtime_memberships_unchanged=progression.runtime_memberships_unchanged,
        supported_scope_ids=tuple(human_scope.supported_scope_ids),
        unsupported_scope_ids=tuple(human_scope.unsupported_scope_ids),
        runtime_owner_supported_scope_ids=tuple(runtime_owner.supported_scope_ids),
        runtime_owner_blocked_scope_ids=tuple(runtime_owner.blocked_scope_ids),
        runtime_owner_blocker_codes=tuple(runtime_owner.blocker_codes),
        unresolved_allocation_ids=tuple(
            progression.ranking_capability.unresolved_allocation_ids
        ),
        unresolved_ranking_endpoint_ids=tuple(
            progression.ranking_capability.unresolved_endpoint_ids
        ),
        previewed_allocation_ids=previewed_ids,
        blocker_codes=tuple(blockers),
    )

def run_canonical_full_scope_preflight(
    game_dir: str | Path,
    *,
    player_seed: int = 1,
    max_days: int = 420,
) -> FullScopePreflight:
    """Assemble the current canonical Gate-17 blocker snapshot.

    Capability audits are joined with a disposable canonical controller that is
    advanced only through the shared primary AI scheduler until the progression
    audit has a completed-season ranking surface or the bounded day limit is
    exhausted. The progression audit itself remains read-only and no previewed
    LeagueAllocation exchange is committed.
    """
    from human_gameplay import HumanGameplayController

    if type(max_days) is not int or max_days < 0:
        raise ValueError("max_days must be an exact non-negative integer")

    game_dir = Path(game_dir)
    human_scope = run_canonical_human_scope_capability(game_dir)
    runtime_owner = run_canonical_runtime_owner_capability(game_dir)
    save_scope = run_canonical_save_scope_capability(game_dir)
    multi_human = run_current_multi_human_capability()

    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=int(player_seed),
        match_engine_seed=1,
    )
    plan = controller.playable_country_allocation_plan
    if plan is None:
        raise Gate17FullScopePreflightError(
            "canonical controller has no playable-country allocation plan"
        )
    progression = None
    for day_index in range(max_days + 1):
        progression = audit_runtime_playable_progression(plan, controller.state)
        if progression.complete:
            break
        if day_index == max_days:
            break
        controller.state.advance_one_day_with_primary_ai_matches(
            controller.attack_matrix,
            controller.defence_matrix,
            controller.match_rng,
            match_engine_rng=controller.match_engine_rng,
        )
    if progression is None:  # pragma: no cover - range always executes once
        raise AssertionError("canonical progression preflight produced no audit")

    return build_full_scope_preflight(
        human_scope,
        runtime_owner,
        save_scope,
        multi_human,
        progression,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--player-seed", type=int, default=1)
    parser.add_argument("--max-days", type=int, default=420)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    audit = run_canonical_full_scope_preflight(
        args.game_dir,
        player_seed=args.player_seed,
        max_days=args.max_days,
    )
    text = json.dumps(audit.as_dict(), indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return 0 if audit.ready_for_full_runtime_validation else 2


if __name__ == "__main__":
    raise SystemExit(main())

