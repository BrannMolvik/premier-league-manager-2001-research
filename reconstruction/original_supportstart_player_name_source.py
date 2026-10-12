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
