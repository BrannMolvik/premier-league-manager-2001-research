"""Recovered 0x60BCB0/0x633610 projections of supplied native snapshots.

These are byte codecs, NOT a completion-time report producer. They neither
infer calculator records from scores nor allocate a report owner/link. Native
memory and generated analysis stay private; unsupported inputs fail closed.
"""


class _NativeBitWriter:
    """0x659CF0/0x659D30: byte-local OR, low bits first, no alignment."""

    def __init__(self):
        self.data = bytearray()
        self.cursor = 0

    def raw_bit(self, value):
        index, shift = divmod(self.cursor, 8)
        if index == len(self.data):
            self.data.append(0)
        # 0x659CF0 does not mask the supplied byte to one bit. Preserve even
        # its byte-local spill semantics rather than silently normalizing it.
        self.data[index] |= ((value & 0xFF) << shift) & 0xFF
        self.cursor += 1

    def bits(self, value, width):
        for shift in range(width):
            self.raw_bit((value >> shift) & 1)

    def finish(self):
        return bytes(self.data)


def _snapshots(records, size, maximum, label):
    if type(records) is not tuple or len(records) > maximum:
        raise ValueError(f'{label} must be an immutable bounded tuple')
    if any(type(record) is not bytes or len(record) != size for record in records):
        raise ValueError(f'{label} requires exact immutable {size:#x}-byte snapshots')


def pack_native_participant_statistics(records: tuple[bytes, ...]) -> bytes:
    """Pack one side's ordered 0x4C-byte participants exactly as 0x60BCB0.

    Writes the low four rating bits (+0x30), then eight one-bit writes from
    +0x35..+0x3C per participant. Return only bytes actually copied by 0x659D70;
    do not fabricate the remaining bytes of the report's 28-byte destination.
    The native pointer array has capacity 18, not an unbounded roster size.
    """
    _snapshots(records, 0x4C, 18, 'Native participants')
    writer = _NativeBitWriter()
    for record in records:
        writer.bits(record[0x30], 4)
        for value in record[0x35:0x3D]:
            writer.raw_bit(value)
    return writer.finish()


def native_participant_skill_flags(current_skills: tuple[int, ...]) -> bytes:
    """0x630C4F/0x630DE0: exact eight captured +0x35..+0x3C bytes.

    Input is the current 17-byte DBRPlayer skill array at +0x1E. Preserve the
    source's duplicated selector (slots 5 and 6), integer mean in slot 1 and
    unsigned >=200 threshold. These are skill flags, not incident counters or
    the later FastView rating trajectory. No RNG or score input is involved.
    """
    if (type(current_skills) is not tuple or len(current_skills) != 17
            or any(type(value) is not int or not 0 <= value <= 255
                   for value in current_skills)):
        raise ValueError('Current skills require exactly 17 immutable byte integers')
    values = (current_skills[0], (current_skills[9] + current_skills[0]) // 2,
              current_skills[6], current_skills[8], current_skills[10],
              current_skills[7], current_skills[7], current_skills[4])
    return bytes(int(value >= 200) for value in values)


def pack_live_participant_statistics(records) -> bytes:
    """0x60BCB0 from actual finalizer output, without synthetic 0x4C memory."""
    from match_postmatch import FinalizedParticipantStatistics
    if (type(records) is not tuple or not 0 < len(records) <= 18
            or any(type(record) is not FinalizedParticipantStatistics or record.player_index != i
                   for i, record in enumerate(records))):
        raise ValueError('Live packing requires complete ordered participant statistics')
    writer = _NativeBitWriter()
    for record in records:
        writer.bits(record.rating, 4)
        for value in record.skill_flags:
            writer.raw_bit(value)
    return writer.finish()


def pack_native_match_script(records: tuple[bytes, ...]) -> bytes:
    """0x633610 -> 0x6336A0: encode linked-list-order 0x38-byte records.

    The first ten bits are the event count. Each record starts with the low
    eight bits of +0x00, followed by its source-family prefix and payload.
    No score, elapsed-time sorting, or synthesized boundary is accepted here.
    Values are truncated only where the native codec explicitly writes bits.
    Unsupported families/subcommands and count overflow are rejected instead
    of reproducing the original's incomplete/default or truncated stream.
    """
    _snapshots(records, 0x38, 0x3FF, 'Native script records')
    return _pack_match_script_fields(tuple(
        lambda offset, record=record: int.from_bytes(record[offset:offset + 4], 'little')
        for record in records
    ))


def pack_live_native_match_script(records) -> bytes:
    """Encode explicit live fields; no fabricated snapshots/unwritten bytes."""
    from native_compact_match import NativeCompactRecord
    if (type(records) is not tuple or len(records) > 0x3FF
            or any(type(record) is not NativeCompactRecord for record in records)):
        raise ValueError('Live script requires immutable bounded native records')
    return _pack_match_script_fields(tuple(record.field for record in records))


def _pack_match_script_fields(fields):
    writer = _NativeBitWriter()
    writer.bits(len(fields), 10)
    for field in fields:
        def copy(offset, width):
            writer.bits(field(offset), width)

        kind = field(0x28)
        if kind not in range(1, 17):
            raise ValueError('Unsupported native script record family')
        copy(0, 8)
        if kind in (1, 2, 3, 4):  # 0x6337B0
            writer.bits(1, 1)
            copy(4, 1)
            copy(8, 5)
            copy(0xC, 5)
            copy(0x2C, 1)
            copy(0x24, 3)
            writer.raw_bit(field(0x20))
            writer.bits(kind - 1, 2)
        elif kind == 5:  # 0x633870
            writer.bits(12, 4)
            copy(4, 1)
            writer.raw_bit(field(0x20))
            if field(0x20):
                copy(0x10, 5)
            else:
                copy(0x14, 5)
                writer.raw_bit(field(0x18))
                writer.raw_bit(field(0x1C))
        elif kind in (6, 7, 8, 9, 16):  # 0x6338E0
            writer.bits(6, 3)
            if kind == 6:
                writer.bits(3, 2)
            elif kind == 7:
                writer.bits(1, 2)
                copy(0x24, 2)
            elif kind == 8:
                writer.bits(6, 3)
            elif kind == 9:
                writer.bits(2, 3)
            else:
                writer.bits(0, 2)
        elif kind == 10:  # 0x633990
            writer.bits(0, 4)
            copy(4, 1)
            copy(8, 5)
            copy(0x2C, 5)
        elif kind == 11:  # 0x633A20
            command = field(8)
            if command not in range(6):
                raise ValueError('Unsupported native script subcommand')
            writer.bits(4, 4)
            copy(4, 1)
            prefix, width, payload_width = (
                (3, 2, 3), (1, 2, 3), (6, 3, 2),
                (4, 3, 5), (2, 3, 4), (0, 3, 5),
            )[command]
            writer.bits(prefix, width)
            if command == 5:
                copy(0xC, 5)
            copy(0x2C, payload_width)
            if command == 5:
                copy(0x24, 2)
        elif kind == 13:  # 0x6339D0
            writer.bits(2, 3)
            value = field(0x2C)
            for shift in (0, 8, 16):
                writer.bits((value >> shift) & 0xFF, 7)
        else:  # 12/14/15 -> 0x633B30
            writer.bits(8, 4)
            copy(4, 1)
            copy(8, 5)
            if kind == 12:
                writer.bits(1, 1)
                copy(0x2C, 4)
            elif kind == 14:
                writer.bits(0, 2)
                copy(0x2C, 4)
            else:
                writer.bits(2, 2)
                copy(0x2C, 3)
                copy(0x24, 4)
    return writer.finish()
