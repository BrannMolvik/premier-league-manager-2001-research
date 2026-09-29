from __future__ import annotations
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import struct

CLUB_RECORD_SIZE = 181
PLAYER_RECORD_SIZE = 103
MANAGER_RECORD_SIZE = 43
PLAYER_SKILLS = (
    'Speed','Strength','Stamina','Determination','Injury Proneness',
    'Passing','Shooting','Tackling','Heading','Control','Technique',
    'Awareness','Agility','Goalkeeping','Confidence','Leadership','Set Piece'
)
OLE_EPOCH = date(1899, 12, 30)
COUNTRY_TABLE_OFFSET = 0x004A
COUNTRY_RECORD_SIZE = 43
COMPETITION_TABLE_OFFSET = 0x2726
COMPETITION_RECORD_SIZE = 53
ROUND_TABLE_OFFSET = 0x4F1F
ROUND_RECORD_SIZE = 36
CUP_ALLOCATION_TABLE_OFFSET = 0xE337
CUP_ALLOCATION_RECORD_SIZE = 28
LEAGUE_ALLOCATION_TABLE_OFFSET = 0xFD43
LEAGUE_ALLOCATION_RECORD_SIZE = 28
REAL_FIXTURE_TABLE_OFFSET = 0x10057
REAL_FIXTURE_RECORD_SIZE = 16
INTERNATIONAL_FIXTURE_TABLE_OFFSET = 0x1181B
INTERNATIONAL_FIXTURE_RECORD_SIZE = 16
ACCESS_FAN_BASE_TABLE_OFFSET = 0x13C95
ACCESS_FAN_BASE_RECORD_SIZE = 78
ACCESS_SKILL_FINANCIAL_TABLE_OFFSET = 0x14965
ACCESS_SKILL_FINANCIAL_RECORD_SIZE = 26

class StringTable:
    def __init__(self, path: Path):
        data = path.read_bytes()
        if len(data) < 8:
            raise ValueError(f'Invalid STR file: {path}')
        table_offset, count = struct.unpack_from('<II', data, 0)
        index_start = table_offset + 8
        index_end = index_start + count * 4
        if index_end > len(data):
            raise ValueError(f'Invalid STR index: {path}')
        offsets = struct.unpack_from(f'<{count}I', data, index_start)
        vals = []
        for rel in offsets:
            pos = 8 + rel
            if pos >= table_offset + 8:
                vals.append('')
                continue
            end = data.find(b'\0', pos, table_offset + 8)
            if end < 0:
                end = table_offset + 8
            vals.append(data[pos:end].decode('cp1252', errors='replace'))
        self.values = vals

    def get(self, idx: int) -> str:
        return self.values[idx] if 0 <= idx < len(self.values) else f'<str:{idx}>'

def ole_date(serial: int) -> date | None:
    if not 10000 <= serial <= 70000:
        return None
    try:
        return OLE_EPOCH + timedelta(days=serial)
    except OverflowError:
        return None

def displayed_skill(raw: int) -> int:
    return (30 * raw + 128) // 255

@dataclass(frozen=True)
class Club:
    index: int
    name: str
    short_name: str
    stadium: str
    manager_id: int
    competition_id: int = 0
    country_id: int = 0
    runtime_value_1c_source: int = 0
    team_category_code: int = 0
    historical_competition_id: int = 0
    historical_slot_index: int = 0
    fan_base_index: int = 0
    related_club_id_0: int = -1
    related_club_id_1: int = -1
    related_club_id_2: int = -1
    map_file: str = ""
    starting_cash: float = 0.0

@dataclass(frozen=True)
class Player:
    index: int
    first_name: str
    surname: str
    club_id: int
    nationality_id: int
    date_of_birth: date | None
    shirt_number: int
    height_cm: int
    weight_kg: int
    positions: tuple[int, int, int]
    current_raw: tuple[int, ...]
    target_raw: tuple[int, ...]
    eu_status_code: int = 2
    initial_flags: int = 0
    joined_current_club_date: date | None = None

    @property
    def full_name(self):
        return f'{self.first_name} {self.surname}'.strip()

    @property
    def current(self):
        return dict(zip(PLAYER_SKILLS, map(displayed_skill, self.current_raw)))

    @property
    def target(self):
        return dict(zip(PLAYER_SKILLS, map(displayed_skill, self.target_raw)))

@dataclass(frozen=True)
class Manager:
    index: int
    first_name: str
    surname: str
    date_of_birth: date | None
    joined: date | None
    club_id: int | None
    formation_default: int
    formation_class3: int
    formation_class1: int
    ai_play_style_source: int = 2
    ai_aggression_source: int = 50
    ai_with_ball_source: int = 1
    ai_without_ball_source: int = 1

    @property
    def full_name(self):
        return f'{self.first_name} {self.surname}'.strip()

@dataclass(frozen=True)
class CountryDefinition:
    id: int
    name: str
    nationality_id: int
    european_index: int
    eu_status_flag: int
    continent_id: int
    financial_multiplier_percent: int = 100

@dataclass(frozen=True)
class AccessFanBase:
    id: int
    values: tuple[int, ...]

    @property
    def field_48(self) -> int:
        # Runtime DBRAccessFanBase +0x48 is packed dword #17, i.e. file +66.
        return int(self.values[16])


@dataclass(frozen=True)
class AccessSkillFinancialValue:
    id: int
    field_08: int
    field_0c: int
    weekly_wage_base: int
    weekly_wage_random_range: int
    field_18: int
    field_1c: int

@dataclass(frozen=True)
class Position:
    id: int
    name: str
    abbreviation: str
    lineup_order: int = 255
    lineup_group: int = 255

@dataclass(frozen=True)
class CompetitionDefinition:
    id: int
    name: str
    substitute_quota: int
    max_non_eu_players: int
    schedule_container_code: int = 0
    runtime_kind_code: int = 0
    parent_competition_id: int | None = None
    initialization_order_value: int = 0
    country_region_id: int = 0
    enumerated_club_reference_0: int = -1
    enumerated_club_reference_1: int = -1
    runtime_instance_count: int = 1
    scheduled_matchday_count: int = 0
    valuation_division_category: int = 5

    @property
    def runtime_kind(self) -> str:
        """Runtime class selected by competition construction at 0x4F70F0."""
        if int(self.runtime_kind_code) == 1:
            return "scot_premier_league" if int(self.id) == 27 else "league"
        if int(self.runtime_kind_code) == 2:
            return "cup"
        if int(self.runtime_kind_code) == 3:
            return "dummy_league"
        return "unknown"

    @property
    def is_root_competition(self) -> bool:
        return self.parent_competition_id is None

    @property
    def uses_secondary_schedule_container(self) -> bool:
        """Exact 0x4F3B70 predicate over DBRCompetition+0x38."""
        return int(self.schedule_container_code) in (2, 3)

@dataclass(frozen=True)
class RoundDefinition:
    id: int
    type_code: int
    competition_id: int
    round_number: int
    name: str
    scheduled_week: int
    scheduled_weekday: int
    replay_week: int
    replay_weekday: int
    team_count: int
    new_entrants: int
    source_competition_reference: int = 0xFFFFFFFF
    cup_extra_time_flag: int = 0
    cup_auxiliary_flag: int = 0
    cup_decisive_flag: int = 0

    @property
    def cup_extra_time_capable(self) -> bool:
        """Constructor bit 0x2 source recovered through 0x4F5420/0x510520."""
        return bool(int(self.cup_extra_time_flag) | int(self.cup_auxiliary_flag))

    @property
    def cup_decisive_tiebreak(self) -> bool:
        """Constructor bit 0x4 source recovered through 0x4F5420/0x510520."""
        return bool(int(self.cup_decisive_flag))

    @property
    def source_competition_id(self) -> int | None:
        value = int(self.source_competition_reference) & 0xFFFF
        return None if value == 0xFFFF else value

    @property
    def source_child_code(self) -> int:
        return (int(self.source_competition_reference) >> 16) & 0xFFFF

@dataclass(frozen=True)
class CupAllocationInstruction:
    id: int
    destination_competition_id: int
    sequence_index: int
    instruction_type: int
    source_reference: int
    quantity: int
    auxiliary: int


@dataclass(frozen=True)
class LeagueAllocationRecord:
    """Packed DBRLeagueAllocation season-transition slot exchange.

    Static.dat stores seven dwords. Runtime construction inserts the vtable
    before them, so executable offsets +0x08/+0x14 are the two competition
    endpoints and +0x0C..+0x10 / +0x18..+0x1C are inclusive zero-based
    ranking ranges. Season finalization at 0x4F948F -> 0x4F4BD0 exchanges
    the paired clubs one slot at a time.
    """

    id: int
    competition_a_id: int
    competition_a_start: int
    competition_a_end: int
    competition_b_id: int
    competition_b_start: int
    competition_b_end: int

    @property
    def exchange_count(self) -> int:
        """0x4F83D0: smaller inclusive endpoint range length."""
        a_count = abs(int(self.competition_a_end) - int(self.competition_a_start)) + 1
        b_count = abs(int(self.competition_b_end) - int(self.competition_b_start)) + 1
        return min(a_count, b_count)


@dataclass(frozen=True)
class RealFixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int


@dataclass(frozen=True)
class InternationalFixture:
    """Packed DBRInternationalFixture fields consumed by secondary scheduling."""

    id: int
    scheduled_week: int
    scheduled_weekday: int
    competition_id: int
    dummy_league_id: int


class FM2001Database:
    def __init__(self, game_dir: str | Path):
        self.game_dir = Path(game_dir)
        self.english = StringTable(self.game_dir / 'English.str')
        self.core = StringTable(self.game_dir / 'Core.str')
        self.master = (self.game_dir / 'Master.dat').read_bytes()
        static_path = self.game_dir / 'Static.dat'
        self.static = static_path.read_bytes() if static_path.exists() else b''
        self.clubs = []
        self.players = []
        self.managers = []
        self.countries = []
        self.positions = []
        self.competitions = []
        self.rounds = []
        self.cup_allocation_instructions = []
        self.league_allocation_records = []
        self.real_fixtures = []
        self.international_fixtures = []
        self.access_fan_bases = []
        self.access_skill_financial_values = []
        self._parse_master()
        if self.static:
            self._parse_countries()
            self._parse_positions()
            self._parse_competitions()
            self._parse_rounds()
            self._parse_cup_allocation_instructions()
            self._parse_league_allocation_records()
            self._parse_real_fixtures()
            self._parse_international_fixtures()
            self._parse_access_fan_bases()
            self._parse_access_skill_financial_values()

    def _parse_master(self):
        d = self.master
        club_count = struct.unpack_from('<I', d, 0)[0]
        club_start = 4
        club_end = club_start + club_count * CLUB_RECORD_SIZE

        for i in range(club_count):
            r = d[club_start + i * CLUB_RECORD_SIZE: club_start + (i + 1) * CLUB_RECORD_SIZE]
            name_id, short_id = struct.unpack_from('<HH', r, 4)
            competition_id = struct.unpack_from('<I', r, 8)[0]
            country_id = struct.unpack_from('<I', r, 12)[0]
            map_file_id = struct.unpack_from('<H', r, 16)[0]
            runtime_value_1c_source = struct.unpack_from('<I', r, 18)[0]
            stadium_id = struct.unpack_from('<H', r, 30)[0]
            historical_competition_id = struct.unpack_from('<i', r, 32)[0]
            historical_slot_index = struct.unpack_from('<i', r, 36)[0]
            manager_id = struct.unpack_from('<I', r, 48)[0]
            fan_base_index = struct.unpack_from('<I', r, 94)[0]
            team_category_code = r[98]
            related_club_id_0 = struct.unpack_from('<i', r, 99)[0]
            related_club_id_1 = struct.unpack_from('<i', r, 103)[0]
            related_club_id_2 = struct.unpack_from('<i', r, 107)[0]
            starting_cash = struct.unpack_from('<d', r, 165)[0]
            self.clubs.append(Club(
                i,
                self.english.get(name_id),
                self.english.get(short_id),
                self.english.get(stadium_id),
                manager_id,
                competition_id,
                country_id,
                runtime_value_1c_source,
                team_category_code,
                historical_competition_id,
                historical_slot_index,
                fan_base_index,
                related_club_id_0,
                related_club_id_1,
                related_club_id_2,
                self.english.get(map_file_id),
                starting_cash,
            ))

        player_count = struct.unpack_from('<I', d, club_end)[0]
        player_start = club_end + 4
        player_end = player_start + player_count * PLAYER_RECORD_SIZE

        for i in range(player_count):
            r = d[player_start + i * PLAYER_RECORD_SIZE: player_start + (i + 1) * PLAYER_RECORD_SIZE]
            player_id, first_id, last_id, club_id = struct.unpack_from('<HHHH', r, 0)
            nationality = r[8]
            initial_flags = struct.unpack_from('<I', r, 10)[0]
            dob = ole_date(struct.unpack_from('<I', r, 14)[0])
            shirt = r[18]
            height = r[19]
            weight = r[20]
            positions = tuple(r[21:24])
            current = tuple(r[24:41])
            target = tuple(r[41:58])
            joined_current_club_date = ole_date(
                struct.unpack_from('<I', r, 76)[0]
            )
            eu_status_code = r[96]
            self.players.append(Player(
                player_id,
                self.core.get(first_id),
                self.core.get(last_id),
                club_id,
                nationality,
                dob,
                shirt,
                height,
                weight,
                positions,
                current,
                target,
                eu_status_code,
                initial_flags,
                joined_current_club_date,
            ))

        manager_count = struct.unpack_from('<I', d, player_end)[0]
        manager_start = player_end + 4
        manager_end = manager_start + manager_count * MANAGER_RECORD_SIZE
        if manager_end != len(d):
            raise ValueError(f'Unexpected Master.dat tail: manager_end={manager_end}, file={len(d)}')

        for i in range(manager_count):
            r = d[manager_start + i * MANAGER_RECORD_SIZE: manager_start + (i + 1) * MANAGER_RECORD_SIZE]
            first_id, last_id = struct.unpack_from('<HH', r, 4)
            dob = ole_date(struct.unpack_from('<I', r, 8)[0])
            joined = ole_date(struct.unpack_from('<I', r, 20)[0])
            formation_default = r[24]
            formation_class3 = r[25]
            formation_class1 = r[26]
            club_raw = struct.unpack_from('<I', r, 27)[0]
            ai_play_style_source = r[39]
            ai_aggression_source = r[40]
            ai_with_ball_source = r[41]
            ai_without_ball_source = r[42]
            club_id = None if club_raw == 0xffffffff else club_raw
            self.managers.append(Manager(
                i,
                self.core.get(first_id),
                self.core.get(last_id),
                dob,
                joined,
                club_id,
                formation_default,
                formation_class3,
                formation_class1,
                ai_play_style_source,
                ai_aggression_source,
                ai_with_ball_source,
                ai_without_ball_source,
            ))

    def _parse_countries(self):
        off = COUNTRY_TABLE_OFFSET
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * COUNTRY_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat country table exceeds file size')
        for i in range(count):
            r = self.static[
                base + i * COUNTRY_RECORD_SIZE:
                base + (i + 1) * COUNTRY_RECORD_SIZE
            ]
            self.countries.append(CountryDefinition(
                id=struct.unpack_from('<I', r, 0)[0],
                name=self.english.get(struct.unpack_from('<H', r, 4)[0]),
                nationality_id=struct.unpack_from('<I', r, 6)[0],
                european_index=struct.unpack_from('<H', r, 14)[0],
                eu_status_flag=struct.unpack_from('<H', r, 16)[0],
                continent_id=struct.unpack_from('<I', r, 24)[0],
                financial_multiplier_percent=struct.unpack_from('<I', r, 37)[0],
            ))

    def country_for_nationality(self, nationality_id: int) -> CountryDefinition | None:
        target = int(nationality_id)
        for country in self.countries:
            if int(country.nationality_id) == target:
                return country
        return None

    def _parse_positions(self):
        off = 0x25E0
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        for i in range(count):
            r = self.static[base + i * 7: base + (i + 1) * 7]
            pid = r[0]
            name_id, abbr_id = struct.unpack_from('<HH', r, 1)
            self.positions.append(Position(
                pid,
                self.english.get(name_id),
                self.english.get(abbr_id),
                lineup_order=r[5],
                lineup_group=r[6],
            ))

    def _parse_competitions(self):
        off = COMPETITION_TABLE_OFFSET
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * COMPETITION_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat competition table exceeds file size')
        for i in range(count):
            r = self.static[
                base + i * COMPETITION_RECORD_SIZE:
                base + (i + 1) * COMPETITION_RECORD_SIZE
            ]
            self.competitions.append(CompetitionDefinition(
                id=struct.unpack_from('<I', r, 0)[0],
                name=self.english.get(struct.unpack_from('<H', r, 12)[0]),
                substitute_quota=r[17],
                max_non_eu_players=r[34],
                schedule_container_code=struct.unpack_from('<I', r, 45)[0],
                runtime_kind_code=r[14],
                parent_competition_id=(
                    None
                    if struct.unpack_from('<i', r, 4)[0] < 0
                    else struct.unpack_from('<i', r, 4)[0]
                ),
                initialization_order_value=struct.unpack_from('<h', r, 15)[0],
                country_region_id=struct.unpack_from('<I', r, 27)[0],
                enumerated_club_reference_0=struct.unpack_from('<i', r, 19)[0],
                enumerated_club_reference_1=struct.unpack_from('<i', r, 23)[0],
                runtime_instance_count=struct.unpack_from('<I', r, 8)[0],
                scheduled_matchday_count=r[18],
                valuation_division_category=r[31],
            ))

    def _parse_rounds(self):
        off = ROUND_TABLE_OFFSET
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * ROUND_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat round table exceeds file size')
        for i in range(count):
            r = self.static[base + i * ROUND_RECORD_SIZE: base + (i + 1) * ROUND_RECORD_SIZE]
            self.rounds.append(RoundDefinition(
                id=struct.unpack_from('<I', r, 0)[0],
                type_code=struct.unpack_from('<H', r, 4)[0],
                competition_id=struct.unpack_from('<H', r, 6)[0],
                round_number=struct.unpack_from('<H', r, 10)[0],
                name=self.english.get(struct.unpack_from('<H', r, 14)[0]),
                scheduled_week=r[16],
                scheduled_weekday=r[17],
                replay_week=r[18],
                replay_weekday=r[19],
                team_count=struct.unpack_from('<H', r, 24)[0],
                new_entrants=struct.unpack_from('<H', r, 26)[0],
                source_competition_reference=struct.unpack_from('<I', r, 20)[0],
                # DBRRound expands these packed fields to +0x24/+0x26/+0x27.
                # Runtime Round construction at 0x4F5420 ORs the first two
                # into +0x30 and carries the latter two to +0x34/+0x32.
                cup_extra_time_flag=struct.unpack_from('<H', r, 28)[0],
                cup_auxiliary_flag=r[30],
                cup_decisive_flag=r[31],
            ))

    def _parse_cup_allocation_instructions(self):
        off = CUP_ALLOCATION_TABLE_OFFSET
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * CUP_ALLOCATION_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat Cup allocation table exceeds file size')
        for i in range(count):
            values = struct.unpack_from(
                '<7I',
                self.static,
                base + i * CUP_ALLOCATION_RECORD_SIZE,
            )
            self.cup_allocation_instructions.append(
                CupAllocationInstruction(
                    id=values[0],
                    destination_competition_id=values[1],
                    sequence_index=values[2],
                    instruction_type=values[3],
                    source_reference=values[4],
                    quantity=values[5],
                    auxiliary=values[6],
                )
            )

    def _parse_league_allocation_records(self):
        """Parse the RTTI-backed DBTLeagueAllocations season-transition table.

        The canonical table begins at Static.dat 0xFD43. Each 28-byte row
        links two competitions and two inclusive ranking ranges; annual
        finalization swaps the selected clubs between those competitions.
        """
        off = LEAGUE_ALLOCATION_TABLE_OFFSET
        if off + 4 > len(self.static):
            return
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * LEAGUE_ALLOCATION_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat League allocation table exceeds file size')
        for i in range(count):
            values = struct.unpack_from(
                '<7I',
                self.static,
                base + i * LEAGUE_ALLOCATION_RECORD_SIZE,
            )
            self.league_allocation_records.append(
                LeagueAllocationRecord(*values)
            )

    def _parse_real_fixtures(self):
        off = REAL_FIXTURE_TABLE_OFFSET
        if off + 4 > len(self.static):
            return
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * REAL_FIXTURE_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat real-fixture table exceeds file size')
        for i in range(count):
            fixture_id, round_index, home, away = struct.unpack_from(
                '<IIII', self.static, base + i * REAL_FIXTURE_RECORD_SIZE
            )
            self.real_fixtures.append(RealFixture(fixture_id, round_index, home, away))

    def _parse_international_fixtures(self):
        """Parse the 108 records consumed by secondary scheduler 0x4FA790."""
        off = INTERNATIONAL_FIXTURE_TABLE_OFFSET
        if off + 4 > len(self.static):
            return
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * INTERNATIONAL_FIXTURE_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat international-fixture table exceeds file size')
        for i in range(count):
            fixture_id, week, weekday, competition_id, dummy_league_id = (
                struct.unpack_from(
                    '<IHHII',
                    self.static,
                    base + i * INTERNATIONAL_FIXTURE_RECORD_SIZE,
                )
            )
            self.international_fixtures.append(
                InternationalFixture(
                    id=fixture_id,
                    scheduled_week=week,
                    scheduled_weekday=weekday,
                    competition_id=competition_id,
                    dummy_league_id=dummy_league_id,
                )
            )

    def _parse_access_fan_bases(self):
        off = ACCESS_FAN_BASE_TABLE_OFFSET
        if off + 4 > len(self.static):
            return
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * ACCESS_FAN_BASE_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat access-fan-base table exceeds file size')
        for i in range(count):
            r = self.static[
                base + i * ACCESS_FAN_BASE_RECORD_SIZE:
                base + (i + 1) * ACCESS_FAN_BASE_RECORD_SIZE
            ]
            record_id = struct.unpack_from('<H', r, 0)[0]
            values = struct.unpack_from('<19I', r, 2)
            self.access_fan_bases.append(AccessFanBase(record_id, values))

    def access_fan_base(self, index: int):
        index = int(index)
        if not 0 <= index < len(self.access_fan_bases):
            raise IndexError(index)
        value = self.access_fan_bases[index]
        if int(value.id) != index:
            raise ValueError('access-fan-base table IDs are not index-aligned')
        return value

    def _parse_access_skill_financial_values(self):
        off = ACCESS_SKILL_FINANCIAL_TABLE_OFFSET
        if off + 4 > len(self.static):
            return
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        end = base + count * ACCESS_SKILL_FINANCIAL_RECORD_SIZE
        if end > len(self.static):
            raise ValueError('Static.dat financial-value table exceeds file size')
        for i in range(count):
            r = self.static[
                base + i * ACCESS_SKILL_FINANCIAL_RECORD_SIZE:
                base + (i + 1) * ACCESS_SKILL_FINANCIAL_RECORD_SIZE
            ]
            record_id = struct.unpack_from('<H', r, 0)[0]
            values = struct.unpack_from('<6I', r, 2)
            self.access_skill_financial_values.append(
                AccessSkillFinancialValue(record_id, *values)
            )

    def access_skill_financial_value(self, rating: int):
        rating = int(rating)
        if not 0 <= rating < len(self.access_skill_financial_values):
            raise IndexError(rating)
        value = self.access_skill_financial_values[rating]
        if int(value.id) != rating:
            raise ValueError('financial-value table IDs are not rating-indexed')
        return value


    def stadium_source_state(self, club_id: int, buildings_source):
        """Materialize the Gate-10 original stadium state for one club.

        buildings_source is the recovered original Lists\\Buildings.dat member
        (or a path to it). The club's per-stadium MAP path comes directly from
        Master.dat +16 through English.str, e.g. MapFiles\\arsenal.map.
        """
        from stadium_state import parse_buildings_dat, parse_stadium_map

        club_id = int(club_id)
        if not 0 <= club_id < len(self.clubs):
            raise IndexError(club_id)
        club = self.clubs[club_id]
        if not club.map_file:
            raise ValueError(f"club {club_id} has no stadium map source")
        relative = Path(*club.map_file.replace("\\\\", "/").replace("\\", "/").split("/"))
        map_path = self.game_dir / relative
        buildings = parse_buildings_dat(buildings_source)
        return parse_stadium_map(map_path, buildings)

    @property
    def premier_league_rounds(self):
        return [r for r in self.rounds if r.competition_id == 0]

    def club_squad(self, club_id: int):
        return [p for p in self.players if p.club_id == club_id]

    def fixtures_for_round(self, round_index: int):
        return [f for f in self.real_fixtures if f.round_index == round_index]

    def summary(self):
        return {
            'clubs': len(self.clubs),
            'players': len(self.players),
            'managers': len(self.managers),
            'countries': len(self.countries),
            'positions': len(self.positions),
            'competitions': len(self.competitions),
            'rounds': len(self.rounds),
            'cup_allocation_instructions': len(self.cup_allocation_instructions),
            'league_allocation_records': len(self.league_allocation_records),
            'real_fixtures': len(self.real_fixtures),
            'access_fan_bases': len(self.access_fan_bases),
            'access_skill_financial_values': len(self.access_skill_financial_values),
        }
