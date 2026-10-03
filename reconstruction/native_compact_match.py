"""Source-written compact fields and the 0x62F7C0 -> 0x62FBF0 finalizer.

This is not a report/context constructor. Unwritten native allocation bytes
are deliberately absent, not zero-filled. Ordinary production must supply its
HalfTime and FullTime records; malformed fallback lists remain unsupported.
"""
from dataclasses import dataclass, replace


def _signed(value):
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


@dataclass(frozen=True)
class NativeCompactRecord:
    minute: int
    kind: int
    fields: tuple[tuple[int, int], ...] = ()

    def __post_init__(self):
        if (type(self.minute) is not int or not -0x80000000 <= self.minute < 0x80000000
                or type(self.kind) is not int or not 0 <= self.kind <= 16
                or type(self.fields) is not tuple):
            raise ValueError('Compact record requires signed minute, family and immutable fields')
        offsets = []
        for entry in self.fields:
            if (type(entry) is not tuple or len(entry) != 2
                    or type(entry[0]) is not int or entry[0] not in range(4, 0x30, 4)
                    or entry[0] == 0x28 or type(entry[1]) is not int
                    or not 0 <= entry[1] <= 0xFFFFFFFF):
                raise ValueError('Compact fields require explicit offset/uint32 pairs')
            offsets.append(entry[0])
        if offsets != sorted(set(offsets)):
            raise ValueError('Compact fields must have unique ordered offsets')

    def field(self, offset):
        if offset == 0:
            return self.minute & 0xFFFFFFFF
        if offset == 0x28:
            return self.kind
        for address, value in self.fields:
            if address == offset:
                return value
        raise ValueError(f'Missing source-written compact field {offset:#x}')


def native_boundary(minute: int, kind: int, *, outcome: int | None = None):
    """0x632640/660/690/6C0: only FullTime writes +0x24."""
    if kind not in (6, 7, 8, 9):
        raise ValueError('Unsupported compact boundary')
    if kind == 7:
        if type(outcome) is not int or outcome not in (0, 1, 2):
            raise ValueError('FullTime requires the calculator outcome payload')
        fields = ((0x24, outcome),)
    else:
        if outcome is not None:
            raise ValueError('Only FullTime owns an outcome payload')
        fields = ()
    return NativeCompactRecord(minute, kind, fields)


def native_full_time_outcome(current: tuple[int, int], previous: tuple[int, int],
                             penalties: tuple[int, int]) -> int:
    """0x62AE00 over explicit live D4C/D50, D28/D2C and D7C/D80 inputs.

    Do not call this with a persisted fixture score to reconstruct context.
    The asymmetrical second comparison is exactly the native instruction flow.
    """
    for pair in (current, previous, penalties):
        if (type(pair) is not tuple or len(pair) != 2
                or any(type(v) is not int or not -0x80000000 <= v < 0x80000000
                       for v in pair)):
            raise ValueError('Outcome requires three explicit signed calculator pairs')
    home, away = current
    old_home, old_away = previous
    a, b = _signed(home + old_home), _signed(away + old_away)
    if a != b:
        return int(a < b)
    if old_home != -1:
        a, b = _signed(home + 2 * old_home), _signed(old_away + 2 * away)
        if a != b:
            return int(a < b)
    return 2 if penalties[0] == penalties[1] else int(penalties[0] < penalties[1])


def compact_record_from_live_event(minute, event):
    """Retain constructor-written fields from live calculator event arguments.

    0x62ECF0/62EE20/62EEA0 write side twice: the secondary lookup owns +4.
    An absent secondary identity is NOT a zero participant. Incident branches
    0x62EF20 write only their selected payload; substitutions use 0x62F000.
    """
    from match_events import ChanceRecord, IncidentRecord, IncidentKind, SubstitutionRecord, BoundaryRecord
    if isinstance(event, ChanceRecord):
        if event.secondary_player_side is None or event.secondary_player_index is None:
            raise ValueError('Missing native secondary participant lookup')
        return NativeCompactRecord(minute, int(event.source), (
            (4, int(event.secondary_player_side)), (8, event.player_index),
            (12, int(event.secondary_player_index)), (0x20, int(event.side_inversion)),
            (0x24, event.raw_outcome), (0x2C, int(event.finish_mode)),
        ))
    if isinstance(event, IncidentRecord):
        if event.kind is IncidentKind.INJURED:
            fields = ((4, event.player_side), (0x10, event.player_index), (0x20, 1))
        else:
            fields = ((4, event.player_side), (0x14, event.player_index),
                      (0x18, int(event.kind is IncidentKind.BOOKED)),
                      (0x1C, int(event.kind is IncidentKind.SENT_OFF)), (0x20, 0))
        return NativeCompactRecord(minute, 5, fields)
    if isinstance(event, SubstitutionRecord):
        return NativeCompactRecord(minute, 10, ((4, event.player_side),
            (8, event.outgoing_player_index), (0x2C, event.incoming_player_index)))
    if isinstance(event, BoundaryRecord):
        return native_boundary(minute, int(event.kind), outcome=event.outcome)
    raise ValueError('Unsupported live compact event payload')


def finalize_native_compact_events(records: tuple[NativeCompactRecord, ...], *,
                                   spacing: int, cutoff: int = 0
                                   ) -> tuple[NativeCompactRecord, ...]:
    """Ordinary source-complete path of 0x62F7C0; immutable linked-list order.

    Pruning stops at kind 9, but spacing's lookahead skips all families >5,
    including boundaries. 0x62FBF0 clamps only the immediate predecessor;
    its backwards register-only calculation does NOT rewrite earlier minutes.
    Sorting is signed and stable. Inputs are untouched even on rejection.
    """
    if (type(records) is not tuple or any(type(r) is not NativeCompactRecord for r in records)
            or type(spacing) is not int or not 0 <= spacing <= 0xFFFFFFFF
            or type(cutoff) is not int or not -0x80000000 <= cutoff < 0x80000000):
        raise ValueError('Finalization requires explicit immutable native inputs')
    if not any(r.kind == 6 for r in records) or not any(r.kind == 7 for r in records):
        raise ValueError('Ordinary production must retain HalfTime and FullTime')
    for record in records:
        if record.kind == 7:
            if record.field(0x24) not in (0, 1, 2):
                raise ValueError('Invalid native FullTime outcome')
    stream = list(records)
    end = next((i for i, r in enumerate(stream) if r.kind == 9), len(stream))
    count = sum(r.kind <= 4 for r in stream[:end])
    for limit, misses_only in ((8, True), (12, False)):
        while count > limit:
            candidate = None
            for i, record in enumerate(stream):
                if record.kind == 9:
                    break
                if record.kind < 4 and record.minute not in (0, 130) and record.minute > cutoff:
                    outcome = record.field(0x24)
                    eligible = outcome == 1 if misses_only else outcome not in (0, 3)
                    if eligible:
                        candidate = i
            if candidate is None:
                break
            del stream[candidate]
            count -= 1
    i = 0
    while i < len(stream):
        current = stream[i]
        if current.kind == 9:
            break
        following = next((j for j in range(i + 1, len(stream))
                          if stream[j].kind <= 5), None)
        if following is None:
            break
        next_record = stream[following]
        if (current.kind <= 5 and next_record.minute != 0
                and current.minute != 130 and current.minute > cutoff):
            minute = (current.minute + spacing) & 0xFFFFFFFF
            if minute > (next_record.minute & 0xFFFFFFFF):
                stream[following] = replace(next_record, minute=_signed(minute))
                if next_record.kind == 5:
                    if following + 1 == len(stream):
                        raise ValueError('Unsupported native dangling incident spacing path')
                    if stream[following + 1].kind == 10:
                        stream[following + 1] = replace(stream[following + 1], minute=_signed(minute))
        i = following
    for i, record in enumerate(stream):
        if record.kind not in (7, 8, 9):
            continue
        if i == 0:
            raise ValueError('Unsupported native boundary without predecessor')
        previous_record = stream[i - 1]
        if previous_record.kind == 8:
            break
        if previous_record.minute > record.minute:
            stream[i - 1] = replace(previous_record, minute=record.minute)
        if record.kind == 9:
            break
    return tuple(sorted(stream, key=lambda r: r.minute))
