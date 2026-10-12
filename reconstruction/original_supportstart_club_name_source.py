"""Original native 0x421BA0 country-CLUB name candidate branch.

For groups with >10 source clubs, 0x421BA0 uses the country group
+0x0C array of pointers into 0x874B90 (expanded CLUB records).
Native 0x421C00 fetches +0x08 string from one selected club and
+0x0C string from a second, independently selected club. The
original club parser 0x4022D0 resolves those from original
Master.dat name and short-name English.str IDs.

No source-random selection occurs here. Caller supplies the two
independently verified real source club positions AND country route.
Do not pretend the output is a player's first/surname from Core.str.
"""
from __future__ import annotations
from dataclasses import dataclass

from fm2001_data import Club
from original_supportstart_name_group_source import OriginalNameGroupCandidateRoute


class OriginalSupportStaffClubNameError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalSupportStaffSelectedClubName:
    first_source_club_position: int
    second_source_club_position: int
    source_first_text: str
    source_second_text: str

    @property
    def full_name(self) -> str:
        """Original 0x4CA6E0 joins the returned source strings with space."""
        return self.source_first_text + " " + self.source_second_text


def project_original_supportstart_observed_club_name(
    source_clubs: tuple[Club, ...],
    route: OriginalNameGroupCandidateRoute,
    *, original_first_club_position: int,
    original_second_club_position: int,
) -> OriginalSupportStaffSelectedClubName:
    """Source native group>10 path; never fabricate the original RNG draws."""
    if type(route) is not OriginalNameGroupCandidateRoute or (
        route.candidate_source != "country_clubs"
        or route.original_group_club_count <= 10
    ):
        raise OriginalSupportStaffClubNameError(
            "Original name group has no qualified club-pointer branch"
        )
    if type(source_clubs) is not tuple or len(source_clubs) != 1246:
        raise OriginalSupportStaffClubNameError(
            "Require unchanged 1246-source-club Master.dat array"
        )
    ids = (original_first_club_position, original_second_club_position)
    allowed = set(route.source_record_positions)
    for index in ids:
        if (type(index) is not int or index not in allowed
            or index < 0 or index >= len(source_clubs)
            or type(source_clubs[index]) is not Club
            or source_clubs[index].index != index
            or source_clubs[index].country_id != route.resolved_group_id):
            raise OriginalSupportStaffClubNameError(
                "Original group selected an unqualified source club record"
            )
    first=source_clubs[ids[0]].name
    second=source_clubs[ids[1]].short_name
    if type(first) is not str or type(second) is not str or not first or not second:
        raise OriginalSupportStaffClubNameError("Missing original club string resource")
    if first == "-":
        raise OriginalSupportStaffClubNameError(
            "Original 0x4CA660 must retry first-string sentinel '-'"
        )
    for value in (first,second):
        if "\x00" in value:
            raise OriginalSupportStaffClubNameError("Source text contains terminator")
        try:
            value.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalSupportStaffClubNameError(
                "Original localized club text must decode from CP1252"
            ) from exc
    return OriginalSupportStaffSelectedClubName(ids[0],ids[1],first,second)
