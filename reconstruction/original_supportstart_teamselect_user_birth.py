"""Bounded native TeamSelect user-birth direct-CRT transaction (not live GUI).

The source-verified ordinary selected-human path calls 0x413BB0 ->
0x4258D0 -> 0x42C400 (13 independent first/surname pairs), then
0x4C9CD0 -> six 0x4C9B30 staff factory calls in type order 1,2,3,4,5,13.
This module composes the independently recovered DIRECT draw components
against ONE caller-owned, already-positioned shared CRT instance.

Neither a new seed nor an alternate RNG stream is ever introduced.
The complete original seed-to-click checkpoint, indirect constructor draws,
user registration/rollback, staff list pointer writes, actual editor mouse
acceptance and Windows GUI remain separate, unresolved integration work.
Do not call this a full native user constructor or wire it to GameState
before source-confirming every intervening indirect CRT consumer.
"""
from __future__ import annotations

from dataclasses import dataclass

from fm2001_data import Club, CompetitionDefinition, Player
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute
from original_supportstart_teamselect_staff_clubs import (
    OriginalTeamSelectStaffClubError,
    original_teamselect_staff_club_candidates,
    original_teamselect_staff_initial_scalar,
)
from original_supportstart_teamselect_staff_rng import (
    SourceOriginalTeamSelectStaffRngReceipt,
    replay_original_teamselect_staff_crt_draws,
)
from original_supportstart_user_creation_rng import (
    SourceOriginalUserBirthNameReceipt,
    consume_original_user_birth_name_pairs,
)
from support_staff import INITIAL_SUPPORT_STAFF_TYPES


class OriginalTeamSelectUserBirthError(ValueError):
    """Original user construction cannot be replayed at this source boundary."""


@dataclass(frozen=True)
class SourceOriginalTeamSelectUserBirthReceipt:
    selected_club_id: int
    selected_root_league_id: int
    selection_context: int
    birth_names: SourceOriginalUserBirthNameReceipt
    staff: tuple[SourceOriginalTeamSelectStaffRngReceipt, ...]

    @property
    def direct_source_rng_call_count(self) -> int:
        """Count ONLY the verified user-name and staff callsites."""
        return (
            self.birth_names.direct_source_rng_call_count
            + sum(item.direct_source_rng_call_count for item in self.staff)
        )


def replay_original_teamselect_user_birth_direct_rng(
    rng,
    *,
    original_clubs: tuple[Club, ...],
    original_players: tuple[Player, ...],
    original_root_league: CompetitionDefinition,
    selected_club_id: int,
    name_route: OriginalNameGroupCandidateRoute,
    selection_context: int,
    require_shipped_club_count: bool = True,
) -> SourceOriginalTeamSelectUserBirthReceipt:
    """Replay source 13 name pairs and six staff on ONE shared CRT.

    The input league comes from the *actual selected native TeamSelect
    row+0x4C*, not club nationality, a synthetic index, or an imported
    country's default top division. Selected club must be in that root
    league; its COUNTRY determines the independent name-candidate route.

    Checks stable source inputs before touching rng. If the caller's
    original CRT unexpectedly fails DURING a draw, the caller must treat
    its whole process state as unqualified; there is no fake rollback
    of the original random stream.
    """
    if not callable(getattr(rng, "randbelow", None)):
        raise OriginalTeamSelectUserBirthError("Require caller-owned shared CRT")
    if type(selected_club_id) is not int or selected_club_id < 0:
        raise OriginalTeamSelectUserBirthError("Invalid original clicked club ID")
    if type(original_clubs) is not tuple or type(original_players) is not tuple:
        raise OriginalTeamSelectUserBirthError("Original source arrays required")
    if (type(original_root_league) is not CompetitionDefinition
            or original_root_league.runtime_kind_code != 1
            or original_root_league.parent_competition_id is not None):
        raise OriginalTeamSelectUserBirthError("Selected row is not native root league")
    if (type(name_route) is not OriginalNameGroupCandidateRoute
            or not 0 <= selected_club_id < len(original_clubs)
            or type(original_clubs[selected_club_id]) is not Club
            or original_clubs[selected_club_id].index != selected_club_id):
        raise OriginalTeamSelectUserBirthError("Clicked source club not qualified")
    club = original_clubs[selected_club_id]
    if (club.competition_id != original_root_league.id
            or name_route.country_index != club.country_id):
        raise OriginalTeamSelectUserBirthError(
            "Selected TeamSelect league or original club-country name route differs"
        )
    try:
        original_teamselect_staff_initial_scalar(
            source_group_id=original_root_league.id,
            selection_context=selection_context,
        )
        candidates = original_teamselect_staff_club_candidates(
            original_clubs,
            group_id=original_root_league.id,
            require_shipped_count=require_shipped_club_count,
        )
        candidates.require_nonempty_source_pool()
    except OriginalTeamSelectStaffClubError as exc:
        raise OriginalTeamSelectUserBirthError(str(exc)) from exc
    if (len(original_players) != name_route.global_player_count
            or not original_players
            or any(type(p) is not Player or p.index != i
                   for i, p in enumerate(original_players))):
        raise OriginalTeamSelectUserBirthError("Original player source order changed")
    if name_route.candidate_source == "filtered_nationality_players":
        eligible = name_route.source_record_positions
    elif name_route.candidate_source == "global_players":
        eligible = tuple(range(len(original_players)))
    else:
        raise OriginalTeamSelectUserBirthError("Unknown original name-pool branch")
    if (not eligible or len(set(eligible)) != len(eligible)
            or any(type(i) is not int or not 0 <= i < len(original_players)
                   or not name_route.eligible_source_player_position(i)
                   for i in eligible)):
        raise OriginalTeamSelectUserBirthError("Original name pool inconsistent")
    for i in eligible:
        p = original_players[i]
        if (type(p.first_name) is not str or type(p.surname) is not str
                or not p.first_name or not p.surname
                or "\x00" in p.first_name or "\x00" in p.surname):
            raise OriginalTeamSelectUserBirthError("Invalid original player name text")
        try:
            p.first_name.encode("cp1252")
            p.surname.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalTeamSelectUserBirthError(
                "Original player name cannot be encoded CP1252"
            ) from exc
    if all(original_players[i].first_name == "-" for i in eligible):
        raise OriginalTeamSelectUserBirthError("Native staff name sentinel never exits")

    birth_names = consume_original_user_birth_name_pairs(
        rng, original_players, name_route
    )
    staff = tuple(
        replay_original_teamselect_staff_crt_draws(
            rng,
            original_players,
            name_route,
            candidates,
            staff_type=type_id,
            source_group_id=original_root_league.id,
            selection_context=selection_context,
        )
        for type_id in INITIAL_SUPPORT_STAFF_TYPES
    )
    return SourceOriginalTeamSelectUserBirthReceipt(
        selected_club_id=selected_club_id,
        selected_root_league_id=original_root_league.id,
        selection_context=selection_context,
        birth_names=birth_names,
        staff=staff,
    )
