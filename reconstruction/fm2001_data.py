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

    @property
    def full_name(self):
        return f'{self.first_name} {self.surname}'.strip()

@dataclass(frozen=True)
class Position:
    id: int
    name: str
    abbreviation: str

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
        self.positions = []
        self.rounds = []
        self.real_fixtures = []
        self._parse_master()
        if self.static:
            self._parse_positions()
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
            stadium_id = struct.unpack_from('<H', r, 30)[0]
            manager_id = struct.unpack_from('<I', r, 48)[0]
            self.clubs.append(Club(
                i,
                self.english.get(name_id),
                self.english.get(short_id),
                self.english.get(stadium_id),
                manager_id,
            ))

        player_count = struct.unpack_from('<I', d, club_end)[0]
        player_start = club_end + 4
        player_end = player_start + player_count * PLAYER_RECORD_SIZE

        for i in range(player_count):
            r = d[player_start + i * PLAYER_RECORD_SIZE: player_start + (i + 1) * PLAYER_RECORD_SIZE]
            player_id, first_id, last_id, club_id = struct.unpack_from('<HHHH', r, 0)
            nationality = r[8]
            dob = ole_date(struct.unpack_from('<I', r, 14)[0])
            shirt = r[18]
            height = r[19]
            weight = r[20]
            positions = tuple(r[21:24])
            current = tuple(r[24:41])
            target = tuple(r[41:58])
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
            club_raw = struct.unpack_from('<I', r, 27)[0]
            club_id = None if club_raw == 0xffffffff else club_raw
            self.managers.append(Manager(
                i,
                self.core.get(first_id),
                self.core.get(last_id),
                dob,
                joined,
                club_id,
            ))

    def _parse_positions(self):
        off = 0x25E0
        count = struct.unpack_from('<I', self.static, off)[0]
        base = off + 4
        for i in range(count):
            r = self.static[base + i * 7: base + (i + 1) * 7]
            pid = r[0]
            name_id, abbr_id = struct.unpack_from('<HH', r, 1)
            self.positions.append(Position(pid, self.english.get(name_id), self.english.get(abbr_id)))

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
            'positions': len(self.positions),
            'rounds': len(self.rounds),
            'real_fixtures': len(self.real_fixtures),
        }
