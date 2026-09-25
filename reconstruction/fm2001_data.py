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
REAL_FIXTURE_TABLE_OFFSET = 0x10057
REAL_FIXTURE_RECORD_SIZE = 16

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
    country_id: int = 0
    runtime_value_1c_source: int = 0
    team_category_code: int = 0

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

@dataclass(frozen=True)
class RealFixture:
    id: int
    round_index: int
    home_club_id: int
    away_club_id: int

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
        self.real_fixtures = []
        self._parse_master()
        if self.static:
            self._parse_countries()
            self._parse_positions()
            self._parse_competitions()
            self._parse_rounds()
            self._parse_real_fixtures()

    def _parse_master(self):
        d = self.master
        club_count = struct.unpack_from('<I', d, 0)[0]
        club_start = 4
        club_end = club_start + club_count * CLUB_RECORD_SIZE

        for i in range(club_count):
            r = d[club_start + i * CLUB_RECORD_SIZE: club_start + (i + 1) * CLUB_RECORD_SIZE]
            name_id, short_id = struct.unpack_from('<HH', r, 4)
            country_id = struct.unpack_from('<I', r, 12)[0]
            runtime_value_1c_source = struct.unpack_from('<I', r, 18)[0]
            stadium_id = struct.unpack_from('<H', r, 30)[0]
            manager_id = struct.unpack_from('<I', r, 48)[0]
            team_category_code = r[98]
            self.clubs.append(Club(
                i,
                self.english.get(name_id),
                self.english.get(short_id),
                self.english.get(stadium_id),
                manager_id,
                country_id,
                runtime_value_1c_source,
                team_category_code,
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
            ))

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
            'real_fixtures': len(self.real_fixtures),
        }
