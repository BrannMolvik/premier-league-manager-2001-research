"""Native original SupportStart name-group source and membership, no RNG guesses.

The source 0x421C00 uses the Static.dat country->name-group indirection;
0x421BA0 selects EITHER group-filtered PLAYERS (when count >10) or
the full original PLAYER pool (when <=10). Both are in owner 0x875638,
not owner 0x874B90 (clubs). Native 0x411A10 constructs group arrays
from 30064 player records, applying exact byte tests before membership.
Native 0x411440 separately groups CLUBS by country; it is unrelated to
the 0x874BD0 name candidate arrays.

No source original RNG state or person-name choices are invented. This
byte-exact binary loader audits private source input; for live game
runtime reuse startup_rng.generated_name_source_ids and the same
shared-CRT stream instead of instantiating a parallel RNG owner.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from struct import unpack_from

STATIC_SHA256 = "e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8"
MASTER_SHA256 = "183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8"
CORE_SHA256 = "b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06"
COUNTRY_COUNT = 209
COUNTRY_START = 0x4A
COUNTRY_STRIDE = 43
GROUP_STRIDE = 3
MASTER_CLUB_COUNT = 1246
MASTER_CLUB_STRIDE = 181
MASTER_PLAYER_COUNT = 30064
MASTER_PLAYER_STRIDE = 103
GROUP_SENTINEL = 0xFFFFFFFF
GROUP_SENTINEL_FALLBACK = 26
GROUP_MIN_ELIGIBLE_PLAYERS = 11


class OriginalNameGroupError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalNameGroupTable:
    country_to_group: tuple[int, ...]
    serialized_group_label_ids: tuple[int, ...]
    group_records_offset: int

    def resolved_group(self, country_index: int) -> int:
        if type(country_index) is not int or not 0 <= country_index < COUNTRY_COUNT:
            raise OriginalNameGroupError("Unqualified original country index")
        idx = self.country_to_group[country_index]
        return GROUP_SENTINEL_FALLBACK if idx == GROUP_SENTINEL else idx


@dataclass(frozen=True)
class OriginalEligibleNamePlayerPools:
    """Source 0x411A10 filtered player positions, in original file order."""
    group_players: tuple[tuple[int, ...], ...]
    global_player_count: int

    @property
    def filtered_total(self) -> int:
        return sum(map(len, self.group_players))


@dataclass(frozen=True)
class OriginalNameGroupCandidateRoute:
    country_index: int
    resolved_group_id: int
    original_group_eligible_player_count: int
    candidate_source: str
    source_record_positions: tuple[int, ...]
    global_player_count: int

    def eligible_source_player_position(self, value: int) -> bool:
        if type(value) is not int:
            return False
        if self.candidate_source == "global_players":
            return 0 <= value < self.global_player_count
        return value in self.source_record_positions


def parse_original_static_name_group_tables(
    data: bytes, *, require_original_sha256: bool = True
) -> OriginalNameGroupTable:
    """Country raw+6 name-group map and 209 original three-byte group headers."""
    if type(data) is not bytes:
        raise OriginalNameGroupError("Original Static.dat bytes required")
    if require_original_sha256 and sha256(data).hexdigest() != STATIC_SHA256:
        raise OriginalNameGroupError("Original Static.dat checksum mismatch")
    if len(data) < COUNTRY_START+4 or unpack_from("<I",data,COUNTRY_START)[0] != COUNTRY_COUNT:
        raise OriginalNameGroupError("Static.dat country count mismatch")
    start = COUNTRY_START+4
    next_pos = start + COUNTRY_COUNT*COUNTRY_STRIDE
    if len(data) < next_pos+4 or unpack_from("<I",data,next_pos)[0] != COUNTRY_COUNT:
        raise OriginalNameGroupError("Static.dat name group count mismatch")
    group_start = next_pos+4
    if len(data) < group_start + COUNTRY_COUNT*GROUP_STRIDE:
        raise OriginalNameGroupError("Static.dat name group headers truncated")
    groups = tuple(unpack_from("<I",data,start+i*COUNTRY_STRIDE+6)[0]
                   for i in range(COUNTRY_COUNT))
    if any(v != GROUP_SENTINEL and v >= COUNTRY_COUNT for v in groups):
        raise OriginalNameGroupError("Out-of-bounds country name-group mapping")
    if tuple(data[group_start+i*GROUP_STRIDE] for i in range(COUNTRY_COUNT)) != tuple(range(COUNTRY_COUNT)):
        raise OriginalNameGroupError("Non-source name group ordinal sequence")
    label_ids = tuple(unpack_from("<H",data,group_start+i*GROUP_STRIDE+1)[0]
                      for i in range(COUNTRY_COUNT))
    return OriginalNameGroupTable(groups,label_ids,group_start)


def _native_source_core_offsets(core: bytes) -> tuple[int, ...]:
    if len(core) < 8:
        raise OriginalNameGroupError("Original Core.str header truncated")
    payload_size,count = unpack_from("<II",core,0)
    start = payload_size+8
    if start+count*4 > len(core) or count == 0:
        raise OriginalNameGroupError("Original Core.str index truncated")
    result = tuple(unpack_from("<I",core,start+i*4)[0] for i in range(count))
    if any(v >= payload_size for v in result):
        raise OriginalNameGroupError("Original Core.str offset outside string payload")
    return result


def original_filtered_name_pool_from_master_core(
    master: bytes, core: bytes, *, require_original_sha256: bool = True,
    test_expected_player_count: int | None = None
) -> OriginalEligibleNamePlayerPools:
    """Reproduce original 0x411A10 group counts/arrays with native byte peeks.

    Name filter reads *bytes at offsets* from string pointers, not Python
    decoded substring comparisons. This matters when the source string is
    shorter than 3 bytes and the original executable reads into the next
    NUL-terminated value. Native conditions:
      first_name_ptr[1] != '.'; surname_ptr[0] != 'N';
      surname_ptr[1] != 'o'; surname_ptr[2] != '.'.
    Group bucket is the native player+0x12 nationality u8, from original
    Master.dat serialized player+8. Filter order and input row order are
    preserved. No RNG is consumed while building groups.
    """
    if type(master) is not bytes or type(core) is not bytes:
        raise OriginalNameGroupError("Authentic Master.dat and Core.str bytes required")
    if require_original_sha256 and (
        sha256(master).hexdigest() != MASTER_SHA256
        or sha256(core).hexdigest() != CORE_SHA256
    ):
        raise OriginalNameGroupError("Original Master.dat/Core.str checksum mismatch")
    offsets = _native_source_core_offsets(core)
    if len(master) < 8 or unpack_from("<I",master,0)[0] != MASTER_CLUB_COUNT:
        raise OriginalNameGroupError("Unexpected original Master.dat club stream")
    head = 4+MASTER_CLUB_COUNT*MASTER_CLUB_STRIDE
    if len(master) < head+4:
        raise OriginalNameGroupError("Original player count absent")
    count=unpack_from("<I",master,head)[0]
    expected = (MASTER_PLAYER_COUNT if test_expected_player_count is None
                else test_expected_player_count)
    if type(expected) is not int or count != expected or count < 0:
        raise OriginalNameGroupError("Original Master.dat player count mismatch")
    start=head+4
    if start + count*MASTER_PLAYER_STRIDE > len(master):
        raise OriginalNameGroupError("Original Master.dat players truncated")
    positions=[[] for _ in range(COUNTRY_COUNT)]
    for i in range(count):
        at=start+i*MASTER_PLAYER_STRIDE
        first,last=unpack_from("<HH",master,at+2)
        nat=master[at+8]
        if first>=len(offsets) or last>=len(offsets):
            raise OriginalNameGroupError("Original player Core.str index out of range")
        f=8+offsets[first]
        l=8+offsets[last]
        if f+1>=len(core) or l+2>=len(core):
            raise OriginalNameGroupError("Source name pointer read outside original Core.str")
        if core[f+1]==0x2E or core[l]==0x4E or core[l+1]==0x6F or core[l+2]==0x2E:
            continue
        if nat>=COUNTRY_COUNT:
            raise OriginalNameGroupError("Original eligible player group out of range")
        positions[nat].append(i)
    return OriginalEligibleNamePlayerPools(tuple(map(tuple,positions)),count)


def source_original_name_group_route(
    table: OriginalNameGroupTable,
    pools: OriginalEligibleNamePlayerPools,
    *, country_index: int,
) -> OriginalNameGroupCandidateRoute:
    """Choose source group's **filtered** player pool or global player pool.

    Native 0x421BA0 uses filtered group count strictly >10. The global
    fallback draws over all players, including those rejected for the
    *grouped* pointer table; it does not draw clubs or managers.
    """
    if type(table) is not OriginalNameGroupTable or type(pools) is not OriginalEligibleNamePlayerPools:
        raise TypeError("Require original Static table and native-filtered name pools")
    if len(pools.group_players)!=COUNTRY_COUNT or pools.global_player_count<=0:
        raise OriginalNameGroupError("Original name group pools malformed")
    group = table.resolved_group(country_index)
    group_positions = pools.group_players[group]
    if any(type(v) is not int or not 0<=v<pools.global_player_count for v in group_positions):
        raise OriginalNameGroupError("Original name group positions invalid")
    grouped = len(group_positions)>=GROUP_MIN_ELIGIBLE_PLAYERS
    return OriginalNameGroupCandidateRoute(
        country_index,group,len(group_positions),
        "filtered_nationality_players" if grouped else "global_players",
        group_positions if grouped else (),pools.global_player_count
    )
