"""Source-observed SupportStart name pairing from original player records.

0x421C00 draws independently from 0x421BA0 twice and passes source
PLAYER first name (+0x08) and PLAYER surname (+0x0C) to CSupportStaff.
Both the filtered-nationality group (>10 eligible players) and global
fallback (<=10) come from the same original PLAYER pool 0x875638.
No original random index is fabricated or drawn here.
"""
from __future__ import annotations
from dataclasses import dataclass
from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute


class OriginalSupportStaffNameSourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalSupportStaffSelectedName:
    first_player_record_position: int
    surname_player_record_position: int
    first_name: str
    surname: str

    @property
    def full_name(self) -> str:
        return self.first_name + " " + self.surname


def source_support_staff_name_from_observed_player_pair(
    source_player_pool: tuple[Player, ...],
    route: OriginalNameGroupCandidateRoute,
    *, original_first_player_position: int,
    original_surname_player_position: int,
) -> OriginalSupportStaffSelectedName:
    """Resolve source-bounded two-choice name only once native draws are known.

    Upstream caller must supply the correct source-derived candidate route.
    A nationality-filtered choice cannot quietly index a record outside the
    permitted source group. Source global fallback includes *all* records,
    including ones filtered from grouped candidate arrays.
    """
    if type(route) is not OriginalNameGroupCandidateRoute:
        raise TypeError("Original name candidate route is required")
    if (type(source_player_pool) is not tuple
            or len(source_player_pool) != route.global_player_count
            or not source_player_pool):
        raise OriginalSupportStaffNameSourceError(
            "Require unchanged original Master.dat source player pool"
        )
    positions=(original_first_player_position, original_surname_player_position)
    if not all(route.eligible_source_player_position(v) for v in positions):
        raise OriginalSupportStaffNameSourceError(
            "Original 0x421BA0 choice not in its eligible player pool"
        )
    selected=(source_player_pool[positions[0]],source_player_pool[positions[1]])
    for position,record in zip(positions,selected):
        if type(record) is not Player or record.index != position:
            raise OriginalSupportStaffNameSourceError(
                "Original source player-record order changed"
            )
    first,last=selected[0].first_name,selected[1].surname
    if type(first) is not str or type(last) is not str or not first or not last:
        raise OriginalSupportStaffNameSourceError(
            "Original player first or surname missing"
        )
    if first == "-":
        raise OriginalSupportStaffNameSourceError(
            "Original 0x4CA660 sentinel first name requires another native draw"
        )
    for value in (first,last):
        if "\x00" in value:
            raise OriginalSupportStaffNameSourceError(
                "Original Core.str source name contains terminator"
            )
        try:
            value.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalSupportStaffNameSourceError(
                "Original Core.str name is not CP1252"
            ) from exc
    return OriginalSupportStaffSelectedName(positions[0],positions[1],first,last)


class BoundedSharedCrtRng:
    """Caller-owned bounded CRT source; this function never seeds or clones it."""

    def randbelow(self, bound: int) -> int: ...


@dataclass(frozen=True)
class OriginalSupportStaffSourceNameReplay:
    selected_name: OriginalSupportStaffSelectedName
    source_name_pairs_attempted: int

    @property
    def bounded_rng_calls(self) -> int:
        """Two original 0x421BA0 choices per attempted pair."""
        return self.source_name_pairs_attempted * 2


def consume_original_supportstaff_name_from_shared_rng(
    rng: BoundedSharedCrtRng,
    source_player_pool: tuple[Player, ...],
    route: OriginalNameGroupCandidateRoute,
) -> OriginalSupportStaffSourceNameReplay:
    """Replay exactly ONE original 0x4CA660 staff name-generation call.

    Original 0x421C00 first draws BOTH player records, then 0x4CA660
    checks the first-name '-' sentinel and retries the ENTIRE two-draw pair.
    The report-setup name helper is different: it retries first choice alone.
    This standalone source primitive requires caller's genuine shared CRT
    at the correct native callsite; it does not establish that seed/state.
    No new private RNG is ever instantiated here, and it is not wired to
    ordinary live GameState until its exact startup stream is reconciled.
    """
    if type(route) is not OriginalNameGroupCandidateRoute:
        raise TypeError("Require original source name-route record")
    if (type(source_player_pool) is not tuple
            or not source_player_pool
            or len(source_player_pool) != route.global_player_count):
        raise OriginalSupportStaffNameSourceError(
            "Require source-ordered original player records"
        )
    if not callable(getattr(rng, "randbelow", None)):
        raise TypeError("Require caller-owned shared CRT RNG")
    if route.candidate_source == "filtered_nationality_players":
        eligible = route.source_record_positions
    elif route.candidate_source == "global_players":
        eligible = tuple(range(route.global_player_count))
    else:
        raise OriginalSupportStaffNameSourceError(
            "Unknown original player-name pool branch"
        )
    if not eligible or len(set(eligible)) != len(eligible):
        raise OriginalSupportStaffNameSourceError("Invalid source name candidate pool")
    if not any(
        route.eligible_source_player_position(position)
        and type(position) is int
        and 0 <= position < len(source_player_pool)
        and type(source_player_pool[position]) is Player
        and source_player_pool[position].index == position
        and source_player_pool[position].first_name != "-"
        for position in eligible
    ):
        raise OriginalSupportStaffNameSourceError(
            "Source nationality/player pool has no non-sentinel first name"
        )

    attempts = 0
    while True:
        first_index = rng.randbelow(len(eligible))
        second_index = rng.randbelow(len(eligible))
        if (type(first_index) is not int or type(second_index) is not int
                or not 0 <= first_index < len(eligible)
                or not 0 <= second_index < len(eligible)):
            raise OriginalSupportStaffNameSourceError(
                "Original shared CRT returned out-of-bounds player choice"
            )
        attempts += 1
        first = eligible[first_index]
        second = eligible[second_index]
        if source_player_pool[first].first_name == "-":
            continue
        return OriginalSupportStaffSourceNameReplay(
            source_support_staff_name_from_observed_player_pair(
                source_player_pool, route,
                original_first_player_position=first,
                original_surname_player_position=second,
            ),
            attempts,
        )
