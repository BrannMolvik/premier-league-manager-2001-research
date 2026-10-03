"""Mandatory ordinary setup producers; no score/completion substitutes."""
from dataclasses import dataclass
import struct

from complete_fixture_report import ReportParticipantMetadata
from original_fixture_report_capture import NativeCapturedScalar


@dataclass(frozen=True)
class NativeSetupPlayerPool:
    original_order: tuple[int, ...]
    nationality_order: tuple[tuple[int, ...], ...]

    @classmethod
    def from_database(cls, database):
        master = getattr(database, 'master', None)
        prefix = getattr(getattr(database, 'core', None), 'native_prefix', None)
        if type(master) is not bytes or prefix is None:
            return None
        if len(master) < 4:
            raise ValueError('Incomplete original club table for setup selection')
        clubs = struct.unpack_from('<I', master)[0]
        count_offset = 4 + clubs * 181
        if count_offset + 4 > len(master):
            raise ValueError('Incomplete original club table for setup selection')
        count = struct.unpack_from('<I', master, count_offset)[0]
        start = count_offset + 4
        if not count or start + count * 103 > len(master):
            raise ValueError('Incomplete original player table for setup selection')
        groups = [[] for _ in range(256)]
        identities = []
        for index in range(count):
            offset = start + index * 103
            identity, first, surname = struct.unpack_from('<HHH', master, offset)
            if identity != index:
                raise ValueError('Native setup requires actual DBTPlayers array identities')
            a, b = prefix(first, 2), prefix(surname, 3)
            if a is None or b is None:
                return None
            identities.append(identity)
            # 0x411A10's separate byte predicates, not a "No." prefix.
            if a[1] != 46 and b[0] != 78 and b[1] != 111 and b[2] != 46:
                groups[master[offset + 8]].append(identity)
        return cls(tuple(identities), tuple(tuple(group) for group in groups))

    def draw_pair(self, nationality_id, players, rng):
        if (type(nationality_id) is not int or not 0 <= nationality_id < 256
                or nationality_id >= len(self.nationality_order)):
            raise ValueError('Setup requires the home-country nationality identity')
        group = self.nationality_order[nationality_id]
        candidates = group if len(group) > 10 else self.original_order
        # Validate before consuming RNG; no infinite retry on a missing source.
        names = {}
        for identity in candidates:
            player = players.get(identity)
            name = getattr(player, 'first_name', None)
            if type(name) is not str:
                return None
            try:
                names[identity] = name.encode('cp1252')
            except UnicodeError:
                return None
        if not candidates or all(name.startswith(b'-') for name in names.values()):
            return None
        while True:
            first = candidates[rng.randbelow(len(candidates))]
            if not names[first].startswith(b'-'):
                break
        second = candidates[rng.randbelow(len(candidates))]
        return first, second


def gate_report_scalar_copies(receipts, seating_price):
    """0x5DB71A/720/726 and x87 self/self classification, not occupancy."""
    if receipts is None or type(seating_price) is not int:
        return None
    home = receipts.home_attendance & 0xFFFFFFFF
    away = receipts.visiting_attendance & 0xFFFFFFFF
    # FILD; FLD ST(0); FDIVRP: 1 for nonzero, NaN for zero. FCOM's
    # unordered flags take the <=0.3 branch. The masked invalid is not a ratio
    # using a guessed stadium capacity. 0x5DBDE0 combines the two classes.
    classification = min(((2 * bool(home) + 2 * bool(away)) >> 1) + 2, 4)
    values = ((0x30, 0xD84, (home + away) & 0xFFFFFFFF, 4),
              (0x34, 0xD88, seating_price & 0xFFFFFFFF, 4),
              (0x38, 0xD8C, home, 4), (0x3C, 0xD90, away, 4),
              (0x40, 0xD9C, classification, 1))
    return tuple(NativeCapturedScalar(d, s, value.to_bytes(width, 'little'))
                 for d, s, value, width in values)


def report_participant_metadata(team_ids, participants, result):
    initial = {(s, i): bit for s, i, bit in result.initial_report_condition_bits}
    booked = {(s, i): bit for s, i, bit in result.report_booking_bits}
    sides = []
    for side, (team_id, players) in enumerate(zip(team_ids, participants)):
        values = []
        for index, player in enumerate(players):
            # 0x41E3D0 selects +70 only for the primary team; +76 has no
            # ordinary runtime producer yet. Do not substitute the primary shirt.
            if (player.club_id != team_id or initial.get((side, index)) is None
                    or booked.get((side, index)) is None):
                return None
            values.append(ReportParticipantMetadata(player.index, player.shirt_number & 63,
                                                   booked[(side, index)], initial[(side, index)]))
        sides.append(tuple(values))
    return tuple(sides)
