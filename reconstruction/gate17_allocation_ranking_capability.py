"""Fail-closed Gate-17 audit of LeagueAllocation ranking readiness.

The source-backed country allocation plan already identifies which
LeagueAllocation rows belong to each TeamSelect-playable country. This module
checks only whether a supplied runtime ranking resolver can satisfy every exact
source ranking position those rows consume.

It performs no membership exchange, applies no promotion/relegation policy and
does not widen gameplay support.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Protocol

from gate17_country_allocation_scope import (
    PlayableCountryAllocationPlan,
)


class LeagueAllocationSource(Protocol):
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


class Gate17AllocationRankingCapabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class AllocationEndpointRequirement:
    competition_id: int
    required_positions: tuple[int, ...]
    ranking_length: int | None
    resolved: bool
    failure_reason: str | None

    def as_dict(self) -> dict:
        return {
            "competition_id": self.competition_id,
            "required_positions": list(self.required_positions),
            "ranking_length": self.ranking_length,
            "resolved": self.resolved,
            "failure_reason": self.failure_reason,
        }


@dataclass(frozen=True)
class AllocationRankingCapabilityEntry:
    allocation_id: int
    country_id: int
    country_name: str
    endpoint_a: AllocationEndpointRequirement
    endpoint_b: AllocationEndpointRequirement

    @property
    def complete(self) -> bool:
        return self.endpoint_a.resolved and self.endpoint_b.resolved

    def as_dict(self) -> dict:
        return {
            "allocation_id": self.allocation_id,
            "country_id": self.country_id,
            "country_name": self.country_name,
            "complete": self.complete,
            "endpoint_a": self.endpoint_a.as_dict(),
            "endpoint_b": self.endpoint_b.as_dict(),
        }


@dataclass(frozen=True)
class AllocationRankingCapabilityAudit:
    catalog_sha256: str
    assigned_allocation_ids: tuple[int, ...]
    resolved_allocation_ids: tuple[int, ...]
    unresolved_allocation_ids: tuple[int, ...]
    required_endpoint_ids: tuple[int, ...]
    resolved_endpoint_ids: tuple[int, ...]
    unresolved_endpoint_ids: tuple[int, ...]
    entries: tuple[AllocationRankingCapabilityEntry, ...]

    @property
    def complete(self) -> bool:
        return (
            bool(self.entries)
            and not self.unresolved_allocation_ids
            and not self.unresolved_endpoint_ids
        )

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "assigned_allocation_ids": list(self.assigned_allocation_ids),
            "resolved_allocation_ids": list(self.resolved_allocation_ids),
            "unresolved_allocation_ids": list(self.unresolved_allocation_ids),
            "required_endpoint_ids": list(self.required_endpoint_ids),
            "resolved_endpoint_ids": list(self.resolved_endpoint_ids),
            "unresolved_endpoint_ids": list(self.unresolved_endpoint_ids),
            "complete": self.complete,
            "entries": [entry.as_dict() for entry in self.entries],
        }


def _inclusive_positions(start: int, end: int) -> tuple[int, ...]:
    start = int(start)
    end = int(end)
    step = 1 if end >= start else -1
    return tuple(range(start, end + step, step))


def _normalize_rankings(
    rankings_by_competition: Mapping[int, tuple[int, ...] | None],
) -> dict[int, tuple[int, ...] | None]:
    if not isinstance(rankings_by_competition, Mapping):
        raise Gate17AllocationRankingCapabilityError(
            "rankings_by_competition must be a mapping"
        )

    normalized: dict[int, tuple[int, ...] | None] = {}
    for raw_id, raw_ranking in rankings_by_competition.items():
        if type(raw_id) is not int or raw_id < 0:
            raise Gate17AllocationRankingCapabilityError(
                "ranking competition IDs must be non-negative integers"
            )
        if raw_id in normalized:
            raise Gate17AllocationRankingCapabilityError(
                f"duplicate ranking competition ID {raw_id}"
            )
        if raw_ranking is None:
            normalized[raw_id] = None
            continue
        if type(raw_ranking) is not tuple:
            raise Gate17AllocationRankingCapabilityError(
                f"ranking {raw_id} must be an immutable tuple or None"
            )
        values: list[int] = []
        seen: set[int] = set()
        for raw_club_id in raw_ranking:
            if type(raw_club_id) is not int or raw_club_id < 0:
                raise Gate17AllocationRankingCapabilityError(
                    f"ranking {raw_id} contains an invalid club ID"
                )
            club_id = int(raw_club_id)
            if club_id in seen:
                raise Gate17AllocationRankingCapabilityError(
                    f"ranking {raw_id} contains duplicate club ID {club_id}"
                )
            values.append(club_id)
            seen.add(club_id)
        normalized[raw_id] = tuple(values)
    return normalized


def _endpoint_requirement(
    competition_id: int,
    positions: tuple[int, ...],
    rankings: Mapping[int, tuple[int, ...] | None],
) -> AllocationEndpointRequirement:
    competition_id = int(competition_id)
    if any(position < 0 for position in positions):
        return AllocationEndpointRequirement(
            competition_id=competition_id,
            required_positions=positions,
            ranking_length=(
                None
                if rankings.get(competition_id) is None
                else len(rankings[competition_id] or ())
            ),
            resolved=False,
            failure_reason="source allocation references a negative ranking position",
        )

    ranking = rankings.get(competition_id)
    if ranking is None:
        return AllocationEndpointRequirement(
            competition_id=competition_id,
            required_positions=positions,
            ranking_length=None,
            resolved=False,
            failure_reason="ranking endpoint is unavailable",
        )

    required_max = max(positions) if positions else -1
    if required_max >= len(ranking):
        return AllocationEndpointRequirement(
            competition_id=competition_id,
            required_positions=positions,
            ranking_length=len(ranking),
            resolved=False,
            failure_reason=(
                f"ranking length {len(ranking)} does not cover required "
                f"position {required_max}"
            ),
        )

    return AllocationEndpointRequirement(
        competition_id=competition_id,
        required_positions=positions,
        ranking_length=len(ranking),
        resolved=True,
        failure_reason=None,
    )


def audit_allocation_ranking_capability(
    plan: PlayableCountryAllocationPlan,
    records: Iterable[LeagueAllocationSource],
    rankings_by_competition: Mapping[int, tuple[int, ...] | None],
) -> AllocationRankingCapabilityAudit:
    """Check exact source allocation positions against available rankings."""

    if type(plan) is not PlayableCountryAllocationPlan:
        raise Gate17AllocationRankingCapabilityError(
            "ranking capability audit requires exact PlayableCountryAllocationPlan"
        )

    rows = tuple(records)
    by_id: dict[int, LeagueAllocationSource] = {}
    for record in rows:
        record_id = int(record.id)
        if record_id in by_id:
            raise Gate17AllocationRankingCapabilityError(
                f"duplicate LeagueAllocation record ID {record_id}"
            )
        by_id[record_id] = record

    planned_ids = tuple(int(value) for value in plan.assigned_allocation_ids)
    if len(set(planned_ids)) != len(planned_ids):
        raise Gate17AllocationRankingCapabilityError(
            "country allocation plan contains duplicate assigned allocation IDs"
        )

    missing_rows = tuple(value for value in planned_ids if value not in by_id)
    if missing_rows:
        raise Gate17AllocationRankingCapabilityError(
            f"country allocation plan references missing rows {missing_rows}"
        )

    country_for_allocation: dict[int, tuple[int, str]] = {}
    for country in plan.countries:
        for allocation_id in country.allocation_ids:
            allocation_id = int(allocation_id)
            if allocation_id in country_for_allocation:
                raise Gate17AllocationRankingCapabilityError(
                    f"allocation {allocation_id} belongs to multiple country plans"
                )
            country_for_allocation[allocation_id] = (
                int(country.country_id),
                str(country.country_name),
            )

    if set(country_for_allocation) != set(planned_ids):
        missing = tuple(
            value for value in planned_ids if value not in country_for_allocation
        )
        extra = tuple(
            value for value in country_for_allocation if value not in set(planned_ids)
        )
        raise Gate17AllocationRankingCapabilityError(
            "country allocation plan assignment mismatch: "
            f"missing={missing}, extra={extra}"
        )

    rankings = _normalize_rankings(rankings_by_competition)

    entries: list[AllocationRankingCapabilityEntry] = []
    endpoint_order: list[int] = []
    endpoint_seen: set[int] = set()

    for allocation_id in planned_ids:
        record = by_id[allocation_id]
        country_id, country_name = country_for_allocation[allocation_id]
        a_id = int(record.competition_a_id)
        b_id = int(record.competition_b_id)

        for endpoint_id in (a_id, b_id):
            if endpoint_id not in endpoint_seen:
                endpoint_order.append(endpoint_id)
                endpoint_seen.add(endpoint_id)

        endpoint_a = _endpoint_requirement(
            a_id,
            _inclusive_positions(
                int(record.competition_a_start),
                int(record.competition_a_end),
            ),
            rankings,
        )
        endpoint_b = _endpoint_requirement(
            b_id,
            _inclusive_positions(
                int(record.competition_b_start),
                int(record.competition_b_end),
            ),
            rankings,
        )

        entries.append(
            AllocationRankingCapabilityEntry(
                allocation_id=allocation_id,
                country_id=country_id,
                country_name=country_name,
                endpoint_a=endpoint_a,
                endpoint_b=endpoint_b,
            )
        )

    resolved_endpoint_ids: list[int] = []
    unresolved_endpoint_ids: list[int] = []
    for endpoint_id in endpoint_order:
        requirements = tuple(
            requirement
            for entry in entries
            for requirement in (entry.endpoint_a, entry.endpoint_b)
            if requirement.competition_id == endpoint_id
        )
        if requirements and all(item.resolved for item in requirements):
            resolved_endpoint_ids.append(endpoint_id)
        else:
            unresolved_endpoint_ids.append(endpoint_id)

    resolved_allocation_ids = tuple(
        entry.allocation_id for entry in entries if entry.complete
    )
    unresolved_allocation_ids = tuple(
        entry.allocation_id for entry in entries if not entry.complete
    )

    return AllocationRankingCapabilityAudit(
        catalog_sha256=str(plan.catalog_sha256),
        assigned_allocation_ids=planned_ids,
        resolved_allocation_ids=resolved_allocation_ids,
        unresolved_allocation_ids=unresolved_allocation_ids,
        required_endpoint_ids=tuple(endpoint_order),
        resolved_endpoint_ids=tuple(resolved_endpoint_ids),
        unresolved_endpoint_ids=tuple(unresolved_endpoint_ids),
        entries=tuple(entries),
    )


def audit_allocation_ranking_resolver(
    plan: PlayableCountryAllocationPlan,
    records: Iterable[LeagueAllocationSource],
    resolver: Callable[[int], tuple[int, ...] | None],
) -> AllocationRankingCapabilityAudit:
    """Call one runtime resolver exactly once per required endpoint."""

    if not callable(resolver):
        raise Gate17AllocationRankingCapabilityError(
            "ranking resolver must be callable"
        )

    endpoint_ids: list[int] = []
    seen: set[int] = set()
    for country in plan.countries:
        for endpoint_id in country.ranking_endpoint_ids:
            endpoint_id = int(endpoint_id)
            if endpoint_id not in seen:
                endpoint_ids.append(endpoint_id)
                seen.add(endpoint_id)

    rankings = {
        endpoint_id: resolver(endpoint_id)
        for endpoint_id in endpoint_ids
    }
    return audit_allocation_ranking_capability(
        plan,
        records,
        rankings,
    )
