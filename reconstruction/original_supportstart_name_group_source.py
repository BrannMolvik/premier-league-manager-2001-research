"""Original SupportStart nationality and source-name group routing.

Static.dat country raw +6 is the 32-bit runtime country+0x0C
mapping at original 0x410640/0x411740. Native 0x421C00 reads that
group, maps 0xffffffff to group26, and calls 0x421BA0 twice.

The 209 serialized group headers follow 209 country records. Each
group header is exactly 3 bytes: original group ID u8, localized
text ID u16; 0x410480 deserializes them into 0x14-byte runtime rows.

At 0x411440, original source builds group member counts and source
pointer arrays from the 0x874B90 CLUB records (0x2A8 stride), not
from the 0x875638 player pool. 0x421BA0 uses group pointers only
when count >10. Otherwise it uses 0x875638 global PLAYER pool
(0x250 stride). Original CRT random draws are NOT implemented here.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
from struct import unpack_from

from fm2001_data import Club

ORIGINAL_STATIC_SHA256 = "e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8"
ORIGINAL_COUNTRY_COUNT = 209
ORIGINAL_COUNTRY_SECTION_OFFSET = 0x4A
ORIGINAL_COUNTRY_SERIALIZED_STRIDE = 43
ORIGINAL_COUNTRY_NAME_GROUP_RELATIVE_OFFSET = 6
ORIGINAL_NAME_GROUP_SERIALIZED_STRIDE = 3
ORIGINAL_NAME_GROUP_FALLBACK = 26
ORIGINAL_NAME_GROUP_SENTINEL = 0xFFFFFFFF
ORIGINAL_NAME_GROUP_MINIMUM_FOR_CLUBS = 11
ORIGINAL_SOURCE_MASTER_CLUB_COUNT = 1246
ORIGINAL_SOURCE_MASTER_PLAYER_COUNT = 30064


class OriginalNameGroupError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalNameGroupTable:
    """Immutable native country->group and serialized per-group identities."""
    country_to_group: tuple[int, ...]
    serialized_group_labels: tuple[int, ...]
    group_records_offset: int

    def resolved_name_group(self, country_index: int) -> int:
        if type(country_index) is not int or not 0 <= country_index < ORIGINAL_COUNTRY_COUNT:
            raise OriginalNameGroupError("Native source country index out of range")
        value = self.country_to_group[country_index]
        return ORIGINAL_NAME_GROUP_FALLBACK if value == ORIGINAL_NAME_GROUP_SENTINEL else value


@dataclass(frozen=True)
class OriginalNameGroupCandidateRoute:
    country_index: int
    resolved_group_id: int
    original_group_club_count: int
    candidate_source: str
    source_record_positions: tuple[int, ...]
    global_player_count: int


def parse_original_static_name_group_tables(
    data: bytes, *, require_original_sha256: bool = True
) -> OriginalNameGroupTable:
    """Parse exact original Static.dat offsets; SHA checks default ON.

    Tests may use a SOURCE-SHAPED minimal fixture with sha validation
    explicitly disabled. No synthetic fixture qualifies live game data.
    """
    if type(data) is not bytes:
        raise OriginalNameGroupError("Expected original Static.dat bytes")
    if require_original_sha256 and sha256(data).hexdigest() != ORIGINAL_STATIC_SHA256:
        raise OriginalNameGroupError("Original Static.dat source checksum mismatch")
    pos = ORIGINAL_COUNTRY_SECTION_OFFSET
    if len(data) < pos+4 or unpack_from("<I",data,pos)[0] != ORIGINAL_COUNTRY_COUNT:
        raise OriginalNameGroupError("Original Static.dat country count mismatch")
    start=pos+4
    next_pos=start+ORIGINAL_COUNTRY_COUNT*ORIGINAL_COUNTRY_SERIALIZED_STRIDE
    if len(data) < next_pos+4 or unpack_from("<I",data,next_pos)[0] != ORIGINAL_COUNTRY_COUNT:
        raise OriginalNameGroupError("Original Static.dat group count mismatch")
    group_start=next_pos+4
    end=group_start+ORIGINAL_COUNTRY_COUNT*ORIGINAL_NAME_GROUP_SERIALIZED_STRIDE
    if len(data) < end:
        raise OriginalNameGroupError("Original Static.dat group headers truncated")
    countries=tuple(
        unpack_from("<I",data,start+i*ORIGINAL_COUNTRY_SERIALIZED_STRIDE
                    +ORIGINAL_COUNTRY_NAME_GROUP_RELATIVE_OFFSET)[0]
        for i in range(ORIGINAL_COUNTRY_COUNT)
    )
    for group in countries:
        if group != ORIGINAL_NAME_GROUP_SENTINEL and group >= ORIGINAL_COUNTRY_COUNT:
            raise OriginalNameGroupError("Country refers to unavailable native group")
    group_ids = tuple(data[group_start+i*ORIGINAL_NAME_GROUP_SERIALIZED_STRIDE]
                      for i in range(ORIGINAL_COUNTRY_COUNT))
    if group_ids != tuple(range(ORIGINAL_COUNTRY_COUNT)):
        raise OriginalNameGroupError("Original group label IDs are not a 0..208 sequence")
    labels = tuple(unpack_from("<H",data,group_start+i*ORIGINAL_NAME_GROUP_SERIALIZED_STRIDE+1)[0]
                   for i in range(ORIGINAL_COUNTRY_COUNT))
    return OriginalNameGroupTable(countries,labels,group_start)


def source_original_name_group_route(
    table: OriginalNameGroupTable,
    *,
    country_index: int,
    source_clubs: tuple[Club, ...],
    original_global_player_count: int,
) -> OriginalNameGroupCandidateRoute:
    """Only determine original selection *bucket*, never RNG-selected name.

    The caller must provide the unchanged Master.dat ordered source clubs,
    not a filtered or sorted subset. The original 0x411440 iterates native
    0x874B90 in that order, builds per-group counts and arrays. The fallback
    population comes from the independent 0x875638 PLAYER owner.
    """
    if type(table) is not OriginalNameGroupTable:
        raise TypeError("Require original source nationality/group table")
    if (type(source_clubs) is not tuple or len(source_clubs)!=ORIGINAL_SOURCE_MASTER_CLUB_COUNT
            or any(type(club) is not Club or club.index!=i
                   for i,club in enumerate(source_clubs))):
        raise OriginalNameGroupError("Require unchanged original 1246 Master.dat club records")
    if type(original_global_player_count) is not int or original_global_player_count!=ORIGINAL_SOURCE_MASTER_PLAYER_COUNT:
        raise OriginalNameGroupError("Require original 30064-player global fallback pool")
    group=table.resolved_name_group(country_index)
    indices=tuple(club.index for club in source_clubs if club.country_id==group)
    if len(indices)>10:
        source="country_clubs"
    else:
        source="global_players"
        indices=()
    return OriginalNameGroupCandidateRoute(
        country_index,group,
        sum(1 for club in source_clubs if club.country_id==group),
        source,indices,original_global_player_count
    )
