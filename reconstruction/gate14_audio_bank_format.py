"""FM2001 old-EA BNKl v2 parser and bounded modern sample decoder.

The canonical FM2001 banks use the early little-endian BNK container with PT
variable headers. This module supports only the exact source-backed subset seen
in the four Gate-14 banks: PC platform, mono 22050 Hz defaults, codec1 0x07
EA-XA v1, and the codec1-omitted PC PCM16LE default.

No filename/event semantics are assigned here.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import struct


class Gate14BnkFormatError(ValueError):
    pass


BNK_SIGNATURE = b"BNKl"
BNK_VERSION = 0x02
BNK_TABLE_OFFSET = 0x0C
EA_PLATFORM_PC = 0x00
EA_CODEC1_PCM = 0x00
EA_CODEC1_EAXA = 0x07
DEFAULT_PC_SAMPLE_RATE = 22050
DEFAULT_CHANNELS = 1
EA_XA_FRAME_BYTES = 0x0F
EA_XA_FRAME_SAMPLES = 28

# vgmstream's reverse-engineered EA-XA v1 coefficient table.
_EA_XA_TABLE = (
    0, 240, 460, 392,
    0, 0, -208, -220,
    0, 1, 3, 4, 7, 8, 10, 11,
    0, -1, -3, -4,
)

_VALUE_TAGS = frozenset(
    set(range(0x03, 0x16))
    | {0x19, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25}
    | {
        0x80, 0x81, 0x82, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
        0x8A, 0x8B, 0x8C, 0x8D, 0x8E, 0x8F, 0x90, 0x91, 0x92, 0x93,
        0x94, 0x95, 0x98, 0x99, 0x9C, 0x9D, 0x9E, 0x9F, 0xA0, 0xA1,
        0xA2, 0xA3, 0xA6, 0xA7, 0xAB, 0xAC, 0xAD,
        0x1A, 0x26, 0x27, 0x28, 0x29, 0x2A,
    }
)
_NO_VALUE_TAGS = frozenset({0xFC, 0xFD})


@dataclass(frozen=True)
class FM2001BnkSample:
    slot_index: int
    pt_offset: int
    data_offset: int
    sample_count: int
    sample_rate: int
    channels: int
    codec: str
    codec1_value: int
    encoded_size: int
    available_span: int
    alignment_padding: int
    loop_start: int | None = None
    loop_end: int | None = None

    def __post_init__(self) -> None:
        if self.codec not in {"ea_xa_v1", "pcm16le"}:
            raise Gate14BnkFormatError("unsupported FM2001 BNK codec")
        if self.sample_rate != DEFAULT_PC_SAMPLE_RATE or self.channels != 1:
            raise Gate14BnkFormatError("FM2001 source subset must remain mono 22050 Hz")
        if self.encoded_size <= 0 or self.available_span < self.encoded_size:
            raise Gate14BnkFormatError("sample payload span is too small")
        if self.alignment_padding != self.available_span - self.encoded_size:
            raise Gate14BnkFormatError("sample padding does not match payload span")
        if not 0 <= self.alignment_padding <= 3:
            raise Gate14BnkFormatError("FM2001 sample padding must be 0..3 bytes")


@dataclass(frozen=True)
class FM2001BnkBank:
    version: int
    slot_count: int
    header_size: int
    samples: tuple[FM2001BnkSample, ...]
    dummy_slots: tuple[int, ...]

    def __post_init__(self) -> None:
        if self.version != BNK_VERSION:
            raise Gate14BnkFormatError("FM2001 bank must use BNKl v2")
        if self.slot_count != len(self.samples) + len(self.dummy_slots):
            raise Gate14BnkFormatError("BNK slot accounting mismatch")
        if self.samples and self.header_size != min(x.data_offset for x in self.samples):
            raise Gate14BnkFormatError("BNK header size must equal first payload offset")

    @property
    def real_sound_count(self) -> int:
        return len(self.samples)


def _read_patch(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise Gate14BnkFormatError("truncated PT patch")
    count = data[offset]
    offset += 1
    if count == 0xFF:
        if offset + 4 > len(data):
            raise Gate14BnkFormatError("truncated long PT patch")
        size = int.from_bytes(data[offset:offset + 4], "big")
        offset += 4
        if offset + size > len(data):
            raise Gate14BnkFormatError("long PT patch exceeds bank")
        return 0, offset + size
    if count > 4:
        if offset + count > len(data):
            raise Gate14BnkFormatError("PT patch exceeds bank")
        return 0, offset + count
    if offset + count > len(data):
        raise Gate14BnkFormatError("truncated PT patch value")
    value = int.from_bytes(data[offset:offset + count], "big") if count else 0
    return value, offset + count


def _parse_pt_tags(data: bytes, pt_offset: int, header_size: int) -> dict[int, list[int]]:
    if data[pt_offset:pt_offset + 2] != b"PT":
        raise Gate14BnkFormatError("BNK table entry does not target PT header")
    if pt_offset + 4 > header_size:
        raise Gate14BnkFormatError("PT platform header crosses metadata boundary")
    platform = int.from_bytes(data[pt_offset + 2:pt_offset + 4], "little")
    if platform != EA_PLATFORM_PC:
        raise Gate14BnkFormatError("FM2001 Gate-14 banks must use PC PT platform")

    tags: dict[int, list[int]] = {}
    pos = pt_offset + 4
    while pos < header_size:
        tag = data[pos]
        pos += 1
        if tag in (0xFF, 0xFE):
            return tags
        if tag in _NO_VALUE_TAGS:
            continue
        if tag == 0x00 or tag in _VALUE_TAGS:
            value, pos = _read_patch(data, pos)
            tags.setdefault(tag, []).append(value)
            continue
        raise Gate14BnkFormatError(f"unsupported PT tag 0x{tag:02X}")
    raise Gate14BnkFormatError("PT header has no terminator before payload")


def parse_fm2001_bnk(data: bytes) -> FM2001BnkBank:
    if not isinstance(data, bytes):
        raise Gate14BnkFormatError("BNK payload must be bytes")
    if len(data) < BNK_TABLE_OFFSET or data[:4] != BNK_SIGNATURE:
        raise Gate14BnkFormatError("not a little-endian EA BNKl bank")
    version = data[4]
    if version != BNK_VERSION or data[5] != 0:
        raise Gate14BnkFormatError("unsupported BNK version/header variant")
    slot_count = int.from_bytes(data[6:8], "little")
    header_size = int.from_bytes(data[8:12], "little")
    table_end = BNK_TABLE_OFFSET + slot_count * 4
    if not slot_count or not table_end <= header_size <= len(data):
        raise Gate14BnkFormatError("invalid BNK table/header bounds")

    raw_entries: list[tuple[int, int, dict[int, list[int]]] | None] = []
    dummy_slots: list[int] = []
    for slot in range(slot_count):
        entry_pos = BNK_TABLE_OFFSET + slot * 4
        relative = int.from_bytes(data[entry_pos:entry_pos + 4], "little")
        if relative == 0:
            raw_entries.append(None)
            dummy_slots.append(slot)
            continue
        pt_offset = entry_pos + relative
        if not table_end <= pt_offset < header_size:
            raise Gate14BnkFormatError("PT offset lies outside BNK metadata region")
        raw_entries.append((slot, pt_offset, _parse_pt_tags(data, pt_offset, header_size)))

    data_offsets = []
    for item in raw_entries:
        if item is None:
            continue
        tags = item[2]
        if 0x85 not in tags or 0x88 not in tags:
            raise Gate14BnkFormatError("FM2001 PT entry lacks sample count/data offset")
        data_offsets.append(tags[0x88][-1])
    if not data_offsets or min(data_offsets) != header_size:
        raise Gate14BnkFormatError("BNK header size does not match first payload")
    if any(not header_size <= value < len(data) for value in data_offsets):
        raise Gate14BnkFormatError("sample data offset lies outside bank")

    unique_offsets = sorted(set(data_offsets))
    next_offset = {
        value: (unique_offsets[index + 1] if index + 1 < len(unique_offsets) else len(data))
        for index, value in enumerate(unique_offsets)
    }

    samples = []
    for item in raw_entries:
        if item is None:
            continue
        slot, pt_offset, tags = item
        sample_count = tags[0x85][-1]
        data_offset = tags[0x88][-1]
        if sample_count <= 0:
            raise Gate14BnkFormatError("sample count must be positive")

        channels = (tags.get(0x82) or [DEFAULT_CHANNELS])[-1] or DEFAULT_CHANNELS
        sample_rate = (tags.get(0x84) or [DEFAULT_PC_SAMPLE_RATE])[-1] or DEFAULT_PC_SAMPLE_RATE
        codec1 = (tags.get(0x83) or [EA_CODEC1_PCM])[-1]
        if channels != 1 or sample_rate != DEFAULT_PC_SAMPLE_RATE:
            raise Gate14BnkFormatError("unexpected non-default FM2001 channel/rate")

        if codec1 == EA_CODEC1_EAXA:
            codec = "ea_xa_v1"
            encoded_size = math.ceil(sample_count / EA_XA_FRAME_SAMPLES) * EA_XA_FRAME_BYTES
        elif codec1 == EA_CODEC1_PCM:
            # PC V0 default: codec1 PCM, bps omitted -> 16-bit LE.
            bps = (tags.get(0x81) or [0])[-1]
            if bps not in (0, 16):
                raise Gate14BnkFormatError("unsupported FM2001 PCM bit depth")
            codec = "pcm16le"
            encoded_size = sample_count * 2
        else:
            raise Gate14BnkFormatError(f"unsupported FM2001 codec1 0x{codec1:02X}")

        available = next_offset[data_offset] - data_offset
        padding = available - encoded_size
        loop_start = (tags.get(0x86) or [None])[-1]
        loop_end_raw = (tags.get(0x87) or [None])[-1]
        loop_end = None if loop_end_raw is None else loop_end_raw + 1
        samples.append(
            FM2001BnkSample(
                slot_index=slot,
                pt_offset=pt_offset,
                data_offset=data_offset,
                sample_count=sample_count,
                sample_rate=sample_rate,
                channels=channels,
                codec=codec,
                codec1_value=codec1,
                encoded_size=encoded_size,
                available_span=available,
                alignment_padding=padding,
                loop_start=loop_start,
                loop_end=loop_end,
            )
        )

    return FM2001BnkBank(
        version=version,
        slot_count=slot_count,
        header_size=header_size,
        samples=tuple(samples),
        dummy_slots=tuple(dummy_slots),
    )


def _clamp16(value: int) -> int:
    return max(-32768, min(32767, int(value)))


def _signed32(value: int) -> int:
    value &= 0xFFFFFFFF
    return value - 0x100000000 if value & 0x80000000 else value


def decode_ea_xa_v1_mono(payload: bytes, sample_count: int) -> tuple[int, ...]:
    if not isinstance(payload, bytes) or type(sample_count) is not int or sample_count <= 0:
        raise Gate14BnkFormatError("EA-XA decode input is invalid")
    needed = math.ceil(sample_count / EA_XA_FRAME_SAMPLES) * EA_XA_FRAME_BYTES
    if len(payload) < needed:
        raise Gate14BnkFormatError("EA-XA payload is truncated")

    out: list[int] = []
    hist1 = 0
    hist2 = 0
    offset = 0
    while len(out) < sample_count:
        frame_info = payload[offset]
        coef_index = (frame_info >> 4) & 0x0F
        shift = (frame_info & 0x0F) + 8
        coef1 = _EA_XA_TABLE[coef_index]
        coef2 = _EA_XA_TABLE[coef_index + 4]
        for i in range(EA_XA_FRAME_SAMPLES):
            if len(out) >= sample_count:
                break
            packed = payload[offset + 1 + i // 2]
            nibble = (packed >> 4) & 0x0F if i % 2 == 0 else packed & 0x0F
            expanded = _signed32(nibble << 28) >> shift
            sample = (expanded + coef1 * hist1 + coef2 * hist2 + 128) >> 8
            sample = _clamp16(sample)
            out.append(sample)
            hist2, hist1 = hist1, sample
        offset += EA_XA_FRAME_BYTES
    return tuple(out)


def decode_fm2001_bnk_sample(
    data: bytes,
    sample: FM2001BnkSample,
) -> tuple[int, ...]:
    if type(sample) is not FM2001BnkSample:
        raise Gate14BnkFormatError("sample must be exact FM2001BnkSample")
    end = sample.data_offset + sample.encoded_size
    if end > len(data):
        raise Gate14BnkFormatError("sample payload exceeds bank")
    payload = data[sample.data_offset:end]
    if sample.codec == "ea_xa_v1":
        return decode_ea_xa_v1_mono(payload, sample.sample_count)
    if sample.codec == "pcm16le":
        return tuple(
            value[0]
            for value in struct.iter_unpack("<h", payload)
        )[:sample.sample_count]
    raise Gate14BnkFormatError("unsupported sample codec")


def pcm16le_bytes(samples: tuple[int, ...]) -> bytes:
    if type(samples) is not tuple or any(type(value) is not int for value in samples):
        raise Gate14BnkFormatError("PCM sample sequence must be exact tuple[int,...]")
    if any(not -32768 <= value <= 32767 for value in samples):
        raise Gate14BnkFormatError("PCM sample is outside int16 range")
    return b"".join(struct.pack("<h", value) for value in samples)
