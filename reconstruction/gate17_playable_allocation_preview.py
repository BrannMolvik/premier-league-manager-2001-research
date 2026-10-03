"""Preview all TeamSelect-playable LeagueAllocation exchanges fail-closed.

This module consumes the source-backed playable-country allocation plan plus
already-verified endpoint rankings and delegates the actual membership swaps to
the recovered generic LeagueAllocation executor.

It is deliberately preview-only: callers receive a new membership mapping and
ordered exchange ledger, while the supplied membership state remains untouched.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Protocol

from gate17_allocation_ranking_capability import (
    AllocationRankingCapabilityAudit,
    audit_allocation_ranking_capability,
)
from gate17_country_allocation_scope import PlayableCountryAllocationPlan
from league_transition import (
    LeagueMembershipExchange,
    apply_league_allocation_exchanges,
)


class LeagueAllocationSource(Protocol):
    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int


class Gate17PlayableAllocationPreviewError(RuntimeError):
    pass


@dataclass(frozen=True)
class PlayableCountryExchangeSummary:
    country_id: int
    country_name: str
    allocation_ids: tuple[int, ...]
    exchange_count: int
    exchanged_club_ids: tuple[int, ...]

    def as_dict(self) -> dict:
        return {
            "country_id": self.country_id,
            "country_name": self.country_name,
            "allocation_ids": list(self.allocation_ids),
            "exchange_count": self.exchange_count,
            "exchanged_club_ids": list(self.exchanged_club_ids),
        }


@dataclass(frozen=True)
class PlayableAllocationPreview:
    catalog_sha256: str
    assigned_allocation_ids: tuple[int, ...]
    ranking_capability: AllocationRankingCapabilityAudit
    memberships_before: dict[int, int]
    memberships_after: dict[int, int]
    exchanges: tuple[LeagueMembershipExchange, ...]
    country_summaries: tuple[PlayableCountryExchangeSummary, ...]

    @property
    def changed_club_ids(self) -> tuple[int, ...]:
        return tuple(
            club_id
            for club_id in self.memberships_before
            if self.memberships_after.get(club_id) != self.memberships_before[club_id]
        )

    def as_dict(self) -> dict:
        return {
            "schema_version": 1,
            "catalog_sha256": self.catalog_sha256,
            "assigned_allocation_ids": list(self.assigned_allocation_ids),
            "ranking_capability": self.ranking_capability.as_dict(),
            "memberships_before": {
                str(club_id): competition_id
                for club_id, competition_id in sorted(self.memberships_before.items())
            },
            "memberships_after": {
                str(club_id): competition_id
                for club_id, competition_id in sorted(self.memberships_after.items())
            },
            "changed_club_ids": list(self.changed_club_ids),
            "exchange_count": len(self.exchanges),
            "exchanges": [
                {
                    "allocation_id": exchange.allocation_id,
                    "slot_index": exchange.slot_index,
                    "club_a_id": exchange.club_a_id,
                    "club_b_id": exchange.club_b_id,
                    "membership_a_before": exchange.membership_a_before,
                    "membership_b_before": exchange.membership_b_before,
                }
                for exchange in self.exchanges
            ],
            "countries": [summary.as_dict() for summary in self.country_summaries],
        }


def _normalize_memberships(
    current_memberships: Mapping[int, int],
) -> dict[int, int]:
    if not isinstance(current_memberships, Mapping):
        raise Gate17PlayableAllocationPreviewError(
            "current_memberships must be a mapping"
        )
    normalized: dict[int, int] = {}
    for raw_club_id, raw_competition_id in current_memberships.items():
        if type(raw_club_id) is not int or raw_club_id < 0:
            raise Gate17PlayableAllocationPreviewError(
                "membership club IDs must be non-negative integers"
            )
        if type(raw_competition_id) is not int or raw_competition_id < 0:
            raise Gate17PlayableAllocationPreviewError(
                "membership competition IDs must be non-negative integers"
            )
        normalized[int(raw_club_id)] = int(raw_competition_id)
    return normalized


def preview_playable_allocation_exchanges(
    plan: PlayableCountryAllocationPlan,
    records: Iterable[LeagueAllocationSource],
    rankings_by_competition: Mapping[int, tuple[int, ...] | None],
    current_memberships: Mapping[int, int],
) -> PlayableAllocationPreview:
    """Preview every assigned playable-country source allocation in source order."""

    if type(plan) is not PlayableCountryAllocationPlan:
        raise Gate17PlayableAllocationPreviewError(
            "playable allocation preview requires exact PlayableCountryAllocationPlan"
        )

    rows = tuple(records)
    by_id: dict[int, LeagueAllocationSource] = {}
    source_order: list[int] = []
    for record in rows:
        record_id = int(record.id)
        if record_id in by_id:
            raise Gate17PlayableAllocationPreviewError(
                f"duplicate LeagueAllocation record ID {record_id}"
            )
        by_id[record_id] = record
        source_order.append(record_id)

    assigned_ids = tuple(int(value) for value in plan.assigned_allocation_ids)
    assigned_set = set(assigned_ids)
    if len(assigned_set) != len(assigned_ids):
        raise Gate17PlayableAllocationPreviewError(
            "playable allocation plan has duplicate assigned allocation IDs"
        )

    missing = tuple(value for value in assigned_ids if value not in by_id)
    if missing:
        raise Gate17PlayableAllocationPreviewError(
            f"playable allocation plan references missing rows {missing}"
        )

    source_assigned_order = tuple(
        record_id for record_id in source_order if record_id in assigned_set
    )
    if source_assigned_order != assigned_ids:
        raise Gate17PlayableAllocationPreviewError(
            "playable allocation plan assigned IDs do not preserve source row order"
        )

    ranking_audit = audit_allocation_ranking_capability(
        plan,
        rows,
        rankings_by_competition,
    )
    if not ranking_audit.complete:
        raise Gate17PlayableAllocationPreviewError(
            "playable allocation rankings are incomplete: "
            f"allocations={ranking_audit.unresolved_allocation_ids}, "
            f"endpoints={ranking_audit.unresolved_endpoint_ids}"
        )

    memberships_before = _normalize_memberships(current_memberships)
    ordered_rows = tuple(by_id[value] for value in assigned_ids)

    # The capability audit proved every required endpoint is present and long
    # enough. The executor still owns all exact source slot selection and swap
    # semantics; do not duplicate those rules here.
    usable_rankings = {
        int(competition_id): tuple(int(club_id) for club_id in ranking)
        for competition_id, ranking in rankings_by_competition.items()
        if ranking is not None
    }

    try:
        transition = apply_league_allocation_exchanges(
            ordered_rows,
            usable_rankings,
            memberships_before,
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise Gate17PlayableAllocationPreviewError(
            f"source-backed playable allocation preview failed: {exc}"
        ) from exc

    allocation_country: dict[int, tuple[int, str]] = {}
    for country in plan.countries:
        for allocation_id in country.allocation_ids:
            allocation_id = int(allocation_id)
            if allocation_id in allocation_country:
                raise Gate17PlayableAllocationPreviewError(
                    f"allocation {allocation_id} belongs to multiple countries"
                )
            allocation_country[allocation_id] = (
                int(country.country_id),
                str(country.country_name),
            )
    if set(allocation_country) != assigned_set:
        raise Gate17PlayableAllocationPreviewError(
            "playable allocation country assignment does not match assigned IDs"
        )

    summaries: list[PlayableCountryExchangeSummary] = []
    for country in plan.countries:
        country_allocation_ids = tuple(int(value) for value in country.allocation_ids)
        exchanges = tuple(
            exchange
            for exchange in transition.exchanges
            if int(exchange.allocation_id) in set(country_allocation_ids)
        )
        exchanged_clubs: list[int] = []
        seen_clubs: set[int] = set()
        for exchange in exchanges:
            for club_id in (int(exchange.club_a_id), int(exchange.club_b_id)):
                if club_id not in seen_clubs:
                    exchanged_clubs.append(club_id)
                    seen_clubs.add(club_id)

        summaries.append(
            PlayableCountryExchangeSummary(
                country_id=int(country.country_id),
                country_name=str(country.country_name),
                allocation_ids=country_allocation_ids,
                exchange_count=len(exchanges),
                exchanged_club_ids=tuple(exchanged_clubs),
            )
        )

    return PlayableAllocationPreview(
        catalog_sha256=str(plan.catalog_sha256),
        assigned_allocation_ids=assigned_ids,
        ranking_capability=ranking_audit,
        memberships_before=dict(memberships_before),
        memberships_after=dict(transition.memberships),
        exchanges=tuple(transition.exchanges),
        country_summaries=tuple(summaries),
    )
