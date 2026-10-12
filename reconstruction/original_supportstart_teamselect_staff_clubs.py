"""Original TeamSelect six-staff source-club candidate array (no RNG).

Native source 0x4D8F75->0x4C9CD0->0x4C9B30 invokes CSupportStaff
vft+0x58 (0x4CB0F0), NOT the distinct reset path vft+0x5C.
At 0x4CB115..0x4CB16B it scans original expanded DBRClubs in
Master.dat source order, matching DBRClub+0x10 competition ID to
the third 0x4C9B30 argument. It stores at most 24 club pointers.

Return only the source eligibility array. Do not select names, consume
shared CRT, manufacture a zero-bound fallback, or create visible staff.
The actual TeamSelect screen+row source group argument still needs
an independently verified normal-player runtime binding.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fm2001_data import Club

ORIGINAL_MASTER_CLUB_COUNT = 1246
ORIGINAL_STAFF_CANDIDATE_CAP = 24


class OriginalTeamSelectStaffClubError(ValueError):
    """Unqualified native club candidate or source group context."""


@dataclass(frozen=True)
class SourceTeamSelectStaffClubCandidates:
    original_group_id: int
    matched_original_club_count: int
    source_club_indices: tuple[int, ...]
    truncated_original_club_count: int

    @property
    def original_random_bound(self) -> int:
        """The actual bounded-CRT parameter passed at 0x4CB1A0."""
        return len(self.source_club_indices)

    def require_nonempty_source_pool(self) -> tuple[int, ...]:
        """Forbid invented player-visible behavior on native RNG(0)."""
        if self.original_random_bound == 0:
            raise OriginalTeamSelectStaffClubError(
                "Original vft+0x58 has no proven safe staff-club choice for this group"
            )
        return self.source_club_indices


def original_teamselect_staff_club_candidates(
    original_clubs: Iterable[Club],
    *,
    group_id: int,
    require_shipped_count: bool = True,
) -> SourceTeamSelectStaffClubCandidates:
    """Bounded native club scan, retaining only the first 24 source matches.

    Native source group is a 32-bit DWORD that must be resolved from the
    real TeamSelect group context. Do not silently substitute club country,
    current club identity, country+0x50 or name-generator nationality.
    """
    if type(group_id) is not int or not 0 <= group_id <= 0xFFFFFFFF:
        raise OriginalTeamSelectStaffClubError("Native staff group must be DWORD")
    clubs = tuple(original_clubs)
    if require_shipped_count and len(clubs) != ORIGINAL_MASTER_CLUB_COUNT:
        raise OriginalTeamSelectStaffClubError(
            "Expected all 1246 original Master.dat clubs in native source order"
        )
    if not clubs:
        raise OriginalTeamSelectStaffClubError("Source club pool is empty")
    for index, club in enumerate(clubs):
        if (type(club) is not Club or type(club.index) is not int
                or club.index != index or type(club.competition_id) is not int
                or not 0 <= club.competition_id <= 0xFFFFFFFF):
            raise OriginalTeamSelectStaffClubError(
                "Source club index/competition ownership mismatch"
            )
    matches = tuple(club.index for club in clubs if club.competition_id == group_id)
    return SourceTeamSelectStaffClubCandidates(
        original_group_id=group_id,
        matched_original_club_count=len(matches),
        source_club_indices=matches[:ORIGINAL_STAFF_CANDIDATE_CAP],
        truncated_original_club_count=max(0, len(matches) - ORIGINAL_STAFF_CANDIDATE_CAP),
    )


def original_teamselect_staff_initial_scalar(
    *, source_group_id: int, selection_context: int
) -> int:
    """Exact deterministic 0x4C9B5C..0x4C9BE0 argument dispatch.

    First original 0x4C9B30 source argument is native staff type.
    Second is TeamSelect's [screen+0x68]-[screen+0x64]-1 context.
    Third is its selected root-league row+0x4C source competition ID.
    The +0x10 native staff scalar has a source group base 4,3,2,1
    for IDs 0,1,2,>=3, incremented once when second argument==1/2.
    This is NOT the other 0x4C9D40 constructor's RNG2 rating.
    No original CRT draw or player-visible staff is created here.
    """
    if (type(source_group_id) is not int
            or not 0 <= source_group_id <= 0xFFFFFFFF
            or type(selection_context) is not int
            or not -0x80000000 <= selection_context <= 0x7FFFFFFF):
        raise OriginalTeamSelectStaffClubError("Unqualified native TeamSelect scalar inputs")
    base = max(1, 4 - source_group_id) if source_group_id <= 3 else 1
    if selection_context in (1, 2):
        base += 1
    return base
