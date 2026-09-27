"""Original FM2001 stadium/ticket source-state materialization for Gate 10.

This module intentionally implements only the source state consumed by the
recovered ticket/attendance path. It does not reconstruct the stadium renderer.

Source evidence:
- per-club MAP files begin with b"FM\\0";
- the map contains 0x1A0 bytes of header/state, a 40x40 dword building grid,
  one flag byte per instantiated building, and 0x10 trailing bytes;
- global Buildings.dat contains 3000 serialized 0xD0-byte records whose live
  first layer is 0x74 bytes and whose second 0x5C bytes overwrite live +0x08;
- runtime building +0x1C terrace and +0x28 seating correspond to serialized
  live-layer offsets +0x14 and +0x20 because the original global object base
  precedes the loader destination by eight bytes;
- 26 fixed section anchors are assigned by a descending 26..0 pass. Index 26
  comes from the first two dwords of the MAP's 0x1A0-byte state block and is not
  part of the persisted 26-entry ticket-state array.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import struct
from typing import Iterable, Sequence


BUILDING_SERIALIZED_RECORD_SIZE = 0xD0
BUILDING_LIVE_RECORD_SIZE = 0x74
BUILDING_COUNT = 3000
MAP_HEADER_SIZE = 0x1A0
MAP_GRID_WIDTH = 40
MAP_GRID_HEIGHT = 40
MAP_GRID_DWORDS = MAP_GRID_WIDTH * MAP_GRID_HEIGHT
MAP_GRID_SIZE = MAP_GRID_DWORDS * 4
MAP_TRAILING_SIZE = 0x10
EMPTY_MAP_CELL = 0xFFFFFFFF

SECTION_ANCHORS: tuple[tuple[int, int], ...] = (
    (21, 15), (20, 15), (19, 15), (18, 15), (17, 16), (17, 17),
    (17, 18), (17, 19), (17, 20), (17, 21), (17, 22), (18, 23),
    (19, 23), (20, 23), (21, 23), (22, 22), (22, 21), (22, 20),
    (22, 19), (22, 18), (22, 17), (22, 16), (22, 15), (17, 15),
    (17, 23), (22, 23),
)

SEASON_TICKET_SECTION_ORDER: tuple[int, ...] = (
    22, 21, 20, 19, 18, 17, 16, 15, 25, 14, 13, 12, 11,
    24, 10, 9, 8, 7, 6, 5, 4, 23, 3, 2, 1, 0,
)

VISITING_SECTION_ORDER: tuple[int, ...] = (
    24, 10, 9, 8, 7, 6, 5, 4, 23, 3, 2, 1, 0,
    22, 21, 19, 18, 17, 16, 15, 25, 14, 13, 12, 11, 24,
)



@dataclass(frozen=True)
class StadiumBuildingDefinition:
    building_id: int
    first_extent: int
    second_extent: int
    terrace_capacity: int
    auxiliary_capacity: int
    seating_capacity: int


@dataclass
class StadiumBuildingInstance:
    first_min: int
    second_min: int
    first_max: int
    second_max: int
    building_id: int
    rotation: int
    flags: int
    section_index: int = -1

    def contains(self, first: int, second: int) -> bool:
        return (
            self.first_min <= int(first) < self.first_max
            and self.second_min <= int(second) < self.second_max
        )


@dataclass(frozen=True)
class StadiumSectionCapacity:
    terrace: int = 0
    seating: int = 0

    @property
    def total(self) -> int:
        return int(self.terrace) + int(self.seating)


@dataclass
class StadiumSourceState:
    buildings: tuple[StadiumBuildingDefinition, ...]
    instances: list[StadiumBuildingInstance]
    section_instances: tuple[StadiumBuildingInstance | None, ...]
    initial_section_states: tuple[int, ...]
    map_state: bytes
    trailing_state: bytes

    def __post_init__(self) -> None:
        if len(self.section_instances) != 26:
            raise ValueError("FM2001 stadiums require exactly 26 ticket sections")
        if len(self.initial_section_states) != 26:
            raise ValueError("FM2001 ticket state requires exactly 26 section states")

    def capacity_for_section_state(
        self,
        section_states: Sequence[int],
        selector: int,
    ) -> StadiumSectionCapacity:
        if len(section_states) != 26:
            raise ValueError("section_states must contain exactly 26 values")
        terrace = 0
        seating = 0
        for section_index, state in enumerate(section_states):
            if int(state) != int(selector):
                continue
            instance = self.section_instances[section_index]
            if instance is None or (int(instance.flags) & 0x02):
                continue
            definition = self.buildings[int(instance.building_id)]
            terrace += int(definition.terrace_capacity)
            seating += int(definition.seating_capacity)
        return StadiumSectionCapacity(terrace=terrace, seating=seating)

    @property
    def initial_home_capacity(self) -> StadiumSectionCapacity:
        return self.capacity_for_section_state(self.initial_section_states, 0)


@dataclass
class TicketRuntimeState:
    """Minimum recovered DBRUser +0x694 ticket state needed by Gate 10."""

    season_ticket_quantity: int = 0
    season_ticket_price: int = 0
    terrace_price: int = 0
    seating_price: int = 0
    auxiliary: int = 0
    section_states: list[int] | None = None

    def __post_init__(self) -> None:
        if self.section_states is None:
            self.section_states = [0] * 26
        else:
            self.section_states = [int(value) for value in self.section_states]
        if len(self.section_states) != 26:
            raise ValueError("ticket section state must contain exactly 26 values")

    @classmethod
    def from_stadium(cls, stadium: StadiumSourceState) -> "TicketRuntimeState":
        return cls(section_states=list(stadium.initial_section_states))

    def allocate_visiting_sections(
        self,
        stadium: StadiumSourceState,
        club_stadium_capacity: int,
    ) -> int:
        """Reproduce 0x618A20's mandatory visiting-supporter allocation.

        Existing state-1 sections are first cleared to zero. State -1 and
        season-ticket state 2 are skipped. The executable then walks its fixed
        26-entry order and assigns state 1 until accumulated terrace+seating
        capacity reaches 10 * floor(club_capacity / 100).
        """
        for index, state in enumerate(self.section_states):
            if state == 1:
                self.section_states[index] = 0

        target = 10 * (max(0, int(club_stadium_capacity)) // 100)
        accumulated = 0
        if target <= 0:
            return 0

        for section_index in VISITING_SECTION_ORDER:
            if accumulated >= target:
                break
            state = int(self.section_states[section_index])
            if state in (-1, 2):
                continue
            instance = stadium.section_instances[section_index]
            if instance is None or (int(instance.flags) & 0x02):
                continue
            definition = stadium.buildings[int(instance.building_id)]
            capacity = (
                int(definition.terrace_capacity)
                + int(definition.seating_capacity)
            )
            accumulated += capacity
            self.section_states[section_index] = 1
            if accumulated >= target:
                break
        return accumulated

    def capacity(
        self,
        stadium: StadiumSourceState,
        selector: int,
    ) -> StadiumSectionCapacity:
        return stadium.capacity_for_section_state(self.section_states, selector)

    def initialize_ordinary_prices(
        self,
        *,
        seating_reference: float,
        terrace_reference: float,
        fan_base_rank_count: int,
        league_team_count: int,
    ) -> tuple[int, int]:
        """Reproduce lazy 0x5DE160 ordinary-price initialization.

        The two reference inputs are the already converted outputs from the
        original 0x40CBC0 -> money-conversion path. Existing nonzero user-set
        prices are preserved exactly.
        """
        team_count = int(league_team_count)
        rank_count = int(fan_base_rank_count)
        if team_count <= 0:
            raise ValueError("league_team_count must be positive")
        if not 0 <= rank_count <= team_count:
            raise ValueError("fan_base_rank_count must be in 0..league_team_count")

        if rank_count <= team_count // 2:
            multiplier = 0.90
        elif rank_count < team_count - 5:
            multiplier = 0.95
        else:
            multiplier = 1.00

        if self.seating_price == 0:
            self.seating_price = int(float(seating_reference) * multiplier)
        if self.terrace_price == 0:
            self.terrace_price = int(float(terrace_reference) * multiplier)
        return self.terrace_price, self.seating_price


def parse_buildings_dat(
    source: bytes | bytearray | memoryview | str | Path,
    *,
    require_canonical_count: bool = False,
) -> tuple[StadiumBuildingDefinition, ...]:
    data = _read_source(source)
    if len(data) % BUILDING_SERIALIZED_RECORD_SIZE:
        raise ValueError(
            "Buildings.dat size is not a multiple of the 0xD0 serialized record size"
        )
    count = len(data) // BUILDING_SERIALIZED_RECORD_SIZE
    if require_canonical_count and count != BUILDING_COUNT:
        raise ValueError(f"expected {BUILDING_COUNT} building records, got {count}")

    records: list[StadiumBuildingDefinition] = []
    for building_id in range(count):
        start = building_id * BUILDING_SERIALIZED_RECORD_SIZE
        serialized = data[start:start + BUILDING_SERIALIZED_RECORD_SIZE]
        live = serialized[:BUILDING_LIVE_RECORD_SIZE]
        overlay = serialized[BUILDING_LIVE_RECORD_SIZE:]
        if overlay != live[0x08:0x64]:
            raise ValueError(
                f"building {building_id} does not match the recovered 0x74+0x5C layout"
            )
        first_extent, second_extent = struct.unpack_from("<II", live, 0)
        # Original helpers address global live fields at class offsets +0x1C
        # and +0x28. The loader destination begins eight bytes into the class,
        # hence serialized live-layer offsets +0x14 and +0x20.
        terrace_capacity = struct.unpack_from("<I", live, 0x14)[0]
        auxiliary_capacity = struct.unpack_from("<I", live, 0x18)[0]
        seating_capacity = struct.unpack_from("<I", live, 0x20)[0]
        records.append(
            StadiumBuildingDefinition(
                building_id=building_id,
                first_extent=int(first_extent),
                second_extent=int(second_extent),
                terrace_capacity=int(terrace_capacity),
                auxiliary_capacity=int(auxiliary_capacity),
                seating_capacity=int(seating_capacity),
            )
        )
    return tuple(records)


def parse_stadium_map(
    source: bytes | bytearray | memoryview | str | Path,
    buildings: Sequence[StadiumBuildingDefinition],
) -> StadiumSourceState:
    data = _read_source(source)
    minimum = 3 + MAP_HEADER_SIZE + MAP_GRID_SIZE + MAP_TRAILING_SIZE
    if len(data) < minimum or data[:3] != b"FM\0":
        raise ValueError("invalid FM2001 stadium MAP")

    map_state_start = 3
    map_state_end = map_state_start + MAP_HEADER_SIZE
    grid_start = map_state_end
    grid_end = grid_start + MAP_GRID_SIZE
    map_state = data[map_state_start:map_state_end]
    grid = struct.unpack_from(f"<{MAP_GRID_DWORDS}I", data, grid_start)

    nonempty_count = sum(int(value) != EMPTY_MAP_CELL for value in grid)
    flag_start = grid_end
    flag_end = flag_start + nonempty_count
    trailing_end = flag_end + MAP_TRAILING_SIZE
    if trailing_end != len(data):
        raise ValueError(
            "MAP length does not match FM header/grid/per-instance-flags/trailer layout"
        )
    flags = data[flag_start:flag_end]
    trailing = data[flag_end:trailing_end]

    instances: list[StadiumBuildingInstance] = []
    flag_index = 0
    for first in range(MAP_GRID_HEIGHT):
        for second in range(MAP_GRID_WIDTH):
            packed = int(grid[first * MAP_GRID_WIDTH + second])
            if packed == EMPTY_MAP_CELL:
                continue
            building_id = packed & 0x3FFF
            rotation = (packed >> 14) & 3
            if not 0 <= building_id < len(buildings):
                raise ValueError(f"MAP references missing building {building_id}")
            definition = buildings[building_id]
            first_extent = int(definition.first_extent)
            second_extent = int(definition.second_extent)
            if rotation in (1, 3):
                first_extent, second_extent = second_extent, first_extent
            instances.append(
                StadiumBuildingInstance(
                    first_min=first,
                    second_min=second,
                    first_max=first + first_extent,
                    second_max=second + second_extent,
                    building_id=building_id,
                    rotation=rotation,
                    flags=int(flags[flag_index]),
                )
            )
            flag_index += 1

    # Original 0x65CE40 runs section index 0x1A down through zero. The
    # 26 persisted ticket anchors are fixed; index 26 uses the MAP state's
    # first two dwords. Reassigning the same large stand instance is intentional
    # and means only the last (lowest) section index remains attached.
    dynamic_anchor = struct.unpack_from("<II", map_state, 0)
    anchors = SECTION_ANCHORS + ((int(dynamic_anchor[0]), int(dynamic_anchor[1])),)
    for section_index in range(26, -1, -1):
        first, second = anchors[section_index]
        for instance in instances:
            if instance.contains(first, second):
                instance.section_index = section_index
                break

    section_instances: list[StadiumBuildingInstance | None] = []
    section_states: list[int] = []
    for section_index in range(26):
        instance = next(
            (
                candidate
                for candidate in instances
                if int(candidate.section_index) == section_index
            ),
            None,
        )
        section_instances.append(instance)
        # 0x6187E0 starts from zeroed section state. Missing sections remain
        # zero; mapped sections become -1 only when instance flag bit 0x02 is set.
        section_states.append(
            -1 if instance is not None and (int(instance.flags) & 0x02) else 0
        )

    return StadiumSourceState(
        buildings=tuple(buildings),
        instances=instances,
        section_instances=tuple(section_instances),
        initial_section_states=tuple(section_states),
        map_state=bytes(map_state),
        trailing_state=bytes(trailing),
    )


def _read_source(source: bytes | bytearray | memoryview | str | Path) -> bytes:
    if isinstance(source, (bytes, bytearray, memoryview)):
        return bytes(source)
    return Path(source).read_bytes()
