"""Fail-closed Gate-17 audit of human-control coverage over TeamSelect scope.

This module does not widen gameplay support. It compares the exact source-backed
TeamSelect catalog with the club IDs that the current human selection backend
actually accepts and reports complete/partial/unsupported League targets.

The canonical runner derives the catalog from hash-verified original data and
uses the same HumanGameplayController canonical constructor as the existing
Gate-7 gameplay audit. No original game bytes are embedded.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from gate17_full_scope_catalog import (
    OriginalPlayableScope,
    load_canonical_original_playable_scope,
)


class Gate17HumanScopeCapabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class HumanScopeCapabilityEntry:
    scope_id: str
    country_id: int
    country_name: str
    competition_id: int
    competition_name: str
    selectable_club_ids: tuple[int, ...]
    supported_club_ids: tuple[int, ...]
    unsupported_club_ids: tuple[int, ...]
    fully_supported: bool

    def as_dict(self) -> dict:
        return {
            "scope_id": self.scope_id,
            "country_id": self.country_id,
            "country_name": self.country_name,
            "competition_id": self.competition_id,
            "competition_name": self.competition_name,
            "selectable_club_ids": list(self.selectable_club_ids),
            "supported_club_ids": list(self.supported_club_ids),
            "unsupported_club_ids": list(self.unsupported_club_ids),
            "fully_supported": self.fully_supported,
        }


@dataclass(frozen=True)
class HumanScopeCapabilityAudit:
    catalog_sha256: str
    backend_selectable_club_ids: tuple[int, ...]
    catalog_selectable_club_ids: tuple[int, ...]
    backend_club_ids_outside_catalog: tuple[int, ...]
    entries: tuple[HumanScopeCapabilityEntry, ...]

    @property
    def supported_scope_ids(self) -> tuple[str, ...]:
        return tuple(entry.scope_id for entry in self.entries if entry.fully_supported)

    @property
    def unsupported_scope_ids(self) -> tuple[str, ...]:
        return tuple(entry.scope_id for entry in self.entries if not entry.fully_supported)

    @property
    def complete(self) -> bool:
        return bool(self.entries) and not self.unsupported_scope_ids

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "backend_selectable_club_ids": list(self.backend_selectable_club_ids),
            "catalog_selectable_club_ids": list(self.catalog_selectable_club_ids),
            "backend_club_ids_outside_catalog": list(
                self.backend_club_ids_outside_catalog
            ),
            "scope_entry_count": len(self.entries),
            "supported_scope_ids": list(self.supported_scope_ids),
            "unsupported_scope_ids": list(self.unsupported_scope_ids),
            "complete": self.complete,
            "entries": [entry.as_dict() for entry in self.entries],
        }


def _normalized_unique_club_ids(values: Iterable[int]) -> tuple[int, ...]:
    output: list[int] = []
    seen: set[int] = set()
    for raw in values:
        if type(raw) is not int:
            raise Gate17HumanScopeCapabilityError(
                "backend selectable club IDs must be exact integers"
            )
        value = int(raw)
        if value < 0:
            raise Gate17HumanScopeCapabilityError(
                "backend selectable club IDs must be non-negative"
            )
        if value in seen:
            raise Gate17HumanScopeCapabilityError(
                f"backend selectable club ID {value} is duplicated"
            )
        output.append(value)
        seen.add(value)
    return tuple(output)


def audit_human_selection_scope(
    scope: OriginalPlayableScope,
    backend_selectable_club_ids: Iterable[int],
) -> HumanScopeCapabilityAudit:
    """Compare current club-selection capability with exact TeamSelect scope."""
    if type(scope) is not OriginalPlayableScope:
        raise Gate17HumanScopeCapabilityError(
            "human scope audit requires exact OriginalPlayableScope"
        )

    backend_ids = _normalized_unique_club_ids(backend_selectable_club_ids)
    backend_set = set(backend_ids)
    entries: list[HumanScopeCapabilityEntry] = []
    catalog_ids: list[int] = []
    catalog_seen: set[int] = set()

    for country in scope.countries:
        for league in country.leagues:
            selectable = tuple(int(value) for value in league.selectable_club_ids)
            if not selectable:
                raise Gate17HumanScopeCapabilityError(
                    f"catalog scope {country.country_id}:{league.competition_id} "
                    "contains no selectable clubs"
                )
            for club_id in selectable:
                if club_id in catalog_seen:
                    raise Gate17HumanScopeCapabilityError(
                        f"catalog selectable club ID {club_id} appears in multiple scopes"
                    )
                catalog_seen.add(club_id)
                catalog_ids.append(club_id)

            supported = tuple(value for value in selectable if value in backend_set)
            unsupported = tuple(value for value in selectable if value not in backend_set)
            entries.append(
                HumanScopeCapabilityEntry(
                    scope_id=f"{int(country.country_id)}:{int(league.competition_id)}",
                    country_id=int(country.country_id),
                    country_name=str(country.name),
                    competition_id=int(league.competition_id),
                    competition_name=str(league.name),
                    selectable_club_ids=selectable,
                    supported_club_ids=supported,
                    unsupported_club_ids=unsupported,
                    fully_supported=not unsupported,
                )
            )

    if not entries:
        raise Gate17HumanScopeCapabilityError(
            "canonical TeamSelect scope contains no selectable League entries"
        )

    return HumanScopeCapabilityAudit(
        catalog_sha256=scope.catalog_sha256,
        backend_selectable_club_ids=backend_ids,
        catalog_selectable_club_ids=tuple(catalog_ids),
        backend_club_ids_outside_catalog=tuple(
            value for value in backend_ids if value not in catalog_seen
        ),
        entries=tuple(entries),
    )


def run_canonical_human_scope_capability(game_dir: str | Path) -> HumanScopeCapabilityAudit:
    """Audit the actual canonical controller's current club-selection surface."""
    from human_gameplay import HumanGameplayController

    game_dir = Path(game_dir)
    scope = load_canonical_original_playable_scope(game_dir)
    controller = HumanGameplayController.from_canonical_game_dir(
        game_dir,
        player_seed=1,
        match_engine_seed=1,
    )
    league = controller.state.premier_league
    if league is None:
        raise Gate17HumanScopeCapabilityError(
            "canonical human controller has no Premier League selection backend"
        )
    return audit_human_selection_scope(
        scope,
        tuple(int(value) for value in league.club_ids),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    audit = run_canonical_human_scope_capability(args.game_dir)
    payload = audit.as_dict()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output is None:
        print(text, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    return 0 if audit.complete else 2


if __name__ == "__main__":
    raise SystemExit(main())
