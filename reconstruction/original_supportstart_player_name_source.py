"""Original SupportStart candidate name projection from a source-observed pair.

Original 0x50D630 loads master.dat player pool at 0x875638; its 0x4218C0
stream reader creates 0x250-byte runtime objects from 103-byte Master.dat
player records. Native 0x421C00 makes TWO selections through 0x421BA0
for first and surname respectively and 0x4CA6E0 joins them with ' '.

Only use TWO source-observed *player pool positions* in native
country-group count<=10 global-PLAYER fallback, not an invented name.
Groups with >10 CLUB entries select from the CLUB source pool instead. The original nationality-group filters, shared CRT
seed, alternate draw paths and name retry still need qualification.
This function is NOT a generator and it draws zero random numbers.
"""
from __future__ import annotations

from dataclasses import dataclass
from fm2001_data import Player


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
        """Native 0x4CA6E0 joining string, if source indices are verified."""
        return self.first_name + " " + self.surname


def source_support_staff_name_from_observed_player_pair(
    source_player_pool: tuple[Player, ...],
    *, original_first_player_position: int,
    original_surname_player_position: int,
    source_group_club_count: int,
) -> OriginalSupportStaffSelectedName:
    """Native name retrieval once upstream source choices are established.

    Neither the modern Match RNG nor daily RNG is consumed; each index must
    come from an independently source-qualified original 0x421BA0 selection.
    Caller must supply the original full Master.dat player array unchanged.
    The source group must have <=10 clubs, or native 0x421BA0 selects
    from original CLUB records rather than global PLAYER fallback.
    The function cannot prove those upstream group/seed choices by itself.
    """
    if (type(source_group_club_count) is not int or
            not 0 <= source_group_club_count <= 10):
        raise OriginalSupportStaffNameSourceError(
            "Original source group must use global player fallback (<=10 clubs)"
        )
    if type(source_player_pool) is not tuple or not source_player_pool:
        raise OriginalSupportStaffNameSourceError(
            "Require original Master.dat ordered player records"
        )
    for index in (original_first_player_position, original_surname_player_position):
        if type(index) is not int or not 0 <= index < len(source_player_pool):
            raise OriginalSupportStaffNameSourceError(
                "Unqualified original 0x421BA0 player-pool position"
            )
    first = source_player_pool[original_first_player_position]
    last = source_player_pool[original_surname_player_position]
    if type(first) is not Player or first.index != original_first_player_position:
        raise OriginalSupportStaffNameSourceError(
            "Original first-name source player record order changed"
        )
    if type(last) is not Player or last.index != original_surname_player_position:
        raise OriginalSupportStaffNameSourceError(
            "Original surname source player record order changed"
        )
    a, b = first.first_name, last.surname
    if type(a) is not str or type(b) is not str or not a or not b:
        raise OriginalSupportStaffNameSourceError(
            "No original Core.str first/surname value"
        )
    if a == "-":
        raise OriginalSupportStaffNameSourceError(
            "Original 0x4CA660 rejects first name '-' and retries its source draw"
        )
    for value in (a, b):
        if "\x00" in value:
            raise OriginalSupportStaffNameSourceError(
                "Original name contains an embedded source terminator"
            )
        try:
            value.encode("cp1252")
        except UnicodeEncodeError as exc:
            raise OriginalSupportStaffNameSourceError(
                "Original name must decode from Core.str CP1252"
            ) from exc
    return OriginalSupportStaffSelectedName(
        original_first_player_position,
        original_surname_player_position,
        a, b,
    )
