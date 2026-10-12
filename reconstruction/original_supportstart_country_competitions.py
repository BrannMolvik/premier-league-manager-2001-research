"""Source-bounded country competition candidates for SupportStart's staff creator.

The original Static.dat competition table is ALREADY decoded by fm2001_data.
Native 0x4F70E0 -> 0x4F3BE0 gives source root competitions a NULL
runtime parent pointer, and 0x4F7380 groups them by source country.
Country+0x48 includes only vft+0x24 kind 1 (league) or 3 (dummy).
The native qsort comparator 0x4F79D0 orders league before dummy, then
by source initialization order ASCENDING (runtime +0x18 is its negative).
Equal comparator keys DO NOT establish qsort tie order.

This module consumes NO RNG, constructs NO new competitions/staff, and never
claims actual runtime scheduling or native selected-pointer order for ties.
It does not synthesize an unknown full-staff constructor, country+0x50,
SupportStart modal, or GUI acceptance.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable

from fm2001_data import CompetitionDefinition

ORIGINAL_COUNTRY_COUNT = 209
ORIGINAL_STATIC_COMPETITION_COUNT = 193
ORIGINAL_COMPETITION_KIND_LEAGUE = 1
ORIGINAL_COMPETITION_KIND_CUP = 2
ORIGINAL_COMPETITION_KIND_DUMMY = 3


class OriginalCompetitionPoolError(ValueError):
    """A source static competition candidate cannot be reconstructed safely."""


class OriginalCompetitionNativeTieError(OriginalCompetitionPoolError):
    """MSVC qsort tie order has not been proven by the shipped original."""


@dataclass(frozen=True)
class SourceCompetitionCandidateTie:
    native_kind: int
    source_initialization_order: int
    competition_ids: tuple[int, ...]


@dataclass(frozen=True)
class SourceCountryCompetitionCandidates:
    country_index: int
    # Source file order, *not* native post-qsort pointer order.
    all_root_competition_ids: tuple[int, ...]
    root_league_dummy_ids: tuple[int, ...]
    # None means pointer order is UNKNOWN due to source comparator ties.
    strict_eligible_order_ids: tuple[int, ...] | None
    unresolved_ties: tuple[SourceCompetitionCandidateTie, ...]

    def require_native_eligible_order(self) -> tuple[int, ...]:
        """Fail closed rather than use Python's stable sort as original qsort."""
        if self.strict_eligible_order_ids is None:
            raise OriginalCompetitionNativeTieError(
                "Original country competition pointer order is tied and unresolved"
            )
        return self.strict_eligible_order_ids


def source_country_competition_candidates(
    competitions: Iterable[CompetitionDefinition],
    *,
    require_shipped_count: bool = True,
    country_count: int = ORIGINAL_COUNTRY_COUNT,
) -> tuple[SourceCountryCompetitionCandidates, ...]:
    """Project source 0x4F7380 root-country membership without random draws.

    The caller provides original decoded Static.dat definitions. The
    source object+0x04 is the resolved parent pointer; NULL iff the
    serialized source parent ID was -1. Source runtime object+0x18 is
    -signed_int16(initialization_order_value).

    The exact selected active competition state and the relative order
    of equal-comparator entries are explicitly NOT recovered here.
    """
    if type(country_count) is not int or not 1 <= country_count <= 209:
        raise OriginalCompetitionPoolError("Invalid source country array size")
    defs = tuple(competitions)
    if require_shipped_count and len(defs) != ORIGINAL_STATIC_COMPETITION_COUNT:
        raise OriginalCompetitionPoolError("Original Static.dat requires 193 competitions")
    if not defs:
        raise OriginalCompetitionPoolError("Empty original competition definitions")
    for position, item in enumerate(defs):
        if type(item) is not CompetitionDefinition or type(item.id) is not int or item.id != position:
            raise OriginalCompetitionPoolError("Source competition id/index mismatch")
        if type(item.country_region_id) is not int or not 0 <= item.country_region_id < country_count:
            raise OriginalCompetitionPoolError("Unqualified source country index")
        if type(item.runtime_kind_code) is not int or item.runtime_kind_code not in (1, 2, 3):
            raise OriginalCompetitionPoolError("Unsupported native competition kind")
        if (type(item.initialization_order_value) is not int
                or not -32768 <= item.initialization_order_value <= 32767):
            raise OriginalCompetitionPoolError("Original initialization order is signed int16")
        parent = item.parent_competition_id
        if parent is not None and (
            type(parent) is not int or not 0 <= parent < len(defs) or parent == item.id
        ):
            raise OriginalCompetitionPoolError("Invalid original competition parent reference")

    roots: dict[int, list[CompetitionDefinition]] = defaultdict(list)
    for item in defs:
        if item.parent_competition_id is None:
            roots[item.country_region_id].append(item)

    groups = []
    for country in range(country_count):
        root = roots[country]
        eligible = [item for item in root if item.runtime_kind_code in (1, 3)]
        # The *membership* and strict comparator ordering are original-proven.
        sorted_eligible = sorted(
            eligible,
            key=lambda item: (
                0 if item.runtime_kind_code == ORIGINAL_COMPETITION_KIND_LEAGUE else 1,
                item.initialization_order_value,
            ),
        )
        ties = []
        for i, item in enumerate(sorted_eligible):
            key = (item.runtime_kind_code, item.initialization_order_value)
            if i > 0 and (
                sorted_eligible[i - 1].runtime_kind_code,
                sorted_eligible[i - 1].initialization_order_value,
            ) == key:
                continue
            tied = tuple(v.id for v in sorted_eligible if (
                v.runtime_kind_code, v.initialization_order_value
            ) == key)
            if len(tied) > 1:
                ties.append(SourceCompetitionCandidateTie(*key, tied))
        groups.append(SourceCountryCompetitionCandidates(
            country_index=country,
            all_root_competition_ids=tuple(item.id for item in root),
            root_league_dummy_ids=tuple(item.id for item in eligible),
            strict_eligible_order_ids=(
                None if ties else tuple(item.id for item in sorted_eligible)
            ),
            unresolved_ties=tuple(ties),
        ))
    return tuple(groups)
