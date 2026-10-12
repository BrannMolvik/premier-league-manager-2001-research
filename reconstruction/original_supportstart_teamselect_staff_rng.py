"""Source-bounded actual TeamSelect six-staff CRT draw receipt.

Normal first-human source: 0x4D8F75 -> 0x4C9CD0 -> 0x4C9B30
for types (1,2,3,4,5,13). This is NOT the distinct 0x4C9D40
RNG25/RNG2 staff-reset path. The native source selects two independent
player names TWICE, then vft+0x2C twice (RNG20), vft+0x30 RNG30
and vft+0x58 RNG3 plus three draws per 1-3 associated clubs.

This projection requires a caller-owned, already-correct shared CRT. It
does not seed or clone an RNG, attach to live GameState, generate staff
linked lists, model the original +0x08 scaling, format assignment text,
or claim actual on-screen SupportStart, original execution or Win11 GUI.
"""
from __future__ import annotations

from dataclasses import dataclass

from fm2001_data import Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_player_name_source import (
    BoundedSharedCrtRng,
    OriginalSupportStaffSelectedName,
    consume_original_supportstaff_name_from_shared_rng,
)
from original_supportstart_teamselect_staff_clubs import (
    OriginalTeamSelectStaffClubError,
    SourceTeamSelectStaffClubCandidates,
    original_teamselect_staff_initial_scalar,
)
from support_staff import INITIAL_SUPPORT_STAFF_TYPES


class OriginalTeamSelectStaffRngError(ValueError):
    """Native source-bound caller input or RNG output is unqualified."""


@dataclass(frozen=True)
class SourceOriginalStaffClubAssignmentDraw:
    original_club_id: int
    original_club_pointer_slot: int
    first_three_way_value: int
    second_three_way_value: int


@dataclass(frozen=True)
class SourceOriginalTeamSelectStaffRngReceipt:
    staff_type: int
    age_like: int
    constructor_base_scalar: int
    constructor_name: OriginalSupportStaffSelectedName
    final_name: OriginalSupportStaffSelectedName
    first_name_attempts: int
    second_name_attempts: int
    first_twenty_draw: int
    thirty_draw: int
    club_assignments: tuple[SourceOriginalStaffClubAssignmentDraw, ...]
    second_twenty_draw: int

    @property
    def direct_source_rng_call_count(self) -> int:
        return (
            1  # RNG25
            + (self.first_name_attempts + self.second_name_attempts) * 2
            + 1  # first RNG20
            + 1  # RNG30
            + 1  # RNG3 count
            + 3 * len(self.club_assignments)  # 1 club + two RNG3 each
            + 1  # second RNG20
        )


def _source_draw(rng: BoundedSharedCrtRng, bound: int) -> int:
    result = rng.randbelow(bound)
    if type(result) is not int or not 0 <= result < bound:
        raise OriginalTeamSelectStaffRngError(
            "Caller-owned CRT returned unqualified bounded selection"
        )
    return result


def replay_original_teamselect_staff_crt_draws(
    rng: BoundedSharedCrtRng,
    players: tuple[Player, ...],
    original_name_route: OriginalNameGroupCandidateRoute,
    original_club_candidates: SourceTeamSelectStaffClubCandidates,
    *,
    staff_type: int,
    source_group_id: int,
    selection_context: int,
) -> SourceOriginalTeamSelectStaffRngReceipt:
    """Replay direct native CRT call order for ONE actual first-human staff.

    The names are original source names only if caller supplies the exact
    live shared CRT state, source name group, player file and selected
    TeamSelect root-league context. The receipt does not reproduce the
    indirect native runtime structures. Caller must not use it as live
    startup RNG without independently reconciling previous consumers.
    """
    if type(staff_type) is not int or staff_type not in INITIAL_SUPPORT_STAFF_TYPES:
        raise OriginalTeamSelectStaffRngError("Not a native six-type TeamSelect staff")
    if (type(original_club_candidates) is not SourceTeamSelectStaffClubCandidates
            or original_club_candidates.original_group_id != source_group_id):
        raise OriginalTeamSelectStaffRngError("Club pool is not selected TeamSelect group")
    if (type(original_name_route) is not OriginalNameGroupCandidateRoute
            or type(players) is not tuple or not players):
        raise OriginalTeamSelectStaffRngError("Missing native player/name source")
    if not callable(getattr(rng, "randbelow", None)):
        raise OriginalTeamSelectStaffRngError("Require existing shared CRT RNG owner")
    # Validate group and empty pool BEFORE advancing any source RNG state.
    try:
        scalar = original_teamselect_staff_initial_scalar(
            source_group_id=source_group_id, selection_context=selection_context
        )
        club_ids = original_club_candidates.require_nonempty_source_pool()
    except OriginalTeamSelectStaffClubError as exc:
        raise OriginalTeamSelectStaffRngError(str(exc)) from exc
    if (len(set(club_ids)) != len(club_ids) or
            any(type(i) is not int or i < 0 for i in club_ids)):
        raise OriginalTeamSelectStaffRngError("Malformed native club pointer array")
    if len(players) != original_name_route.global_player_count:
        raise OriginalTeamSelectStaffRngError("Native player record array count changed")
    if any(type(p) is not Player or p.index != i for i, p in enumerate(players)):
        raise OriginalTeamSelectStaffRngError("Native player record order changed")
    # Name pair preflight, including no live native all-sentinel source pool.
    eligible = (original_name_route.source_record_positions
                if original_name_route.candidate_source == "filtered_nationality_players"
                else tuple(range(len(players)))
                if original_name_route.candidate_source == "global_players" else ())
    if not eligible or len(set(eligible)) != len(eligible):
        raise OriginalTeamSelectStaffRngError("Missing or duplicate native name candidates")
    if any(
        type(i) is not int or not 0 <= i < len(players)
        or not original_name_route.eligible_source_player_position(i)
        for i in eligible
    ):
        raise OriginalTeamSelectStaffRngError("Invalid native player-name candidate index")
    for i in eligible:
        row = players[i]
        if (
            type(row.first_name) is not str or type(row.surname) is not str
            or not row.first_name or not row.surname
            or "\x00" in row.first_name or "\x00" in row.surname
        ):
            raise OriginalTeamSelectStaffRngError("Missing original source name text")
        try:
            row.first_name.encode("cp1252")
            row.surname.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalTeamSelectStaffRngError(
                "Original source name cannot be encoded as CP1252"
            ) from exc
    if all(players[i].first_name == "-" for i in eligible):
        raise OriginalTeamSelectStaffRngError(
            "Native name candidate pool cannot exit '-' retry"
        )

    age_like = _source_draw(rng, 25) + 25
    initial_name = consume_original_supportstaff_name_from_shared_rng(
        rng, players, original_name_route
    )
    final_name = consume_original_supportstaff_name_from_shared_rng(
        rng, players, original_name_route
    )
    first_twenty = _source_draw(rng, 20)
    thirty = _source_draw(rng, 30)
    count = _source_draw(rng, 3) + 1
    assignments = []
    for _ in range(count):
        slot = _source_draw(rng, len(club_ids))
        a = _source_draw(rng, 3)
        b = _source_draw(rng, 3)
        assignments.append(SourceOriginalStaffClubAssignmentDraw(
            club_ids[slot], slot, a, b
        ))
    second_twenty = _source_draw(rng, 20)
    return SourceOriginalTeamSelectStaffRngReceipt(
        staff_type=staff_type,
        age_like=age_like,
        constructor_base_scalar=scalar,
        constructor_name=initial_name.selected_name,
        final_name=final_name.selected_name,
        first_name_attempts=initial_name.source_name_pairs_attempted,
        second_name_attempts=final_name.source_name_pairs_attempted,
        first_twenty_draw=first_twenty,
        thirty_draw=thirty,
        club_assignments=tuple(assignments),
        second_twenty_draw=second_twenty,
    )
