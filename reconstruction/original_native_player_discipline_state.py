"""Explicit original DBRPlayer disciplinary bytes, independent of generic state.

SOURCE: original footballmanager.exe SHA256
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Native readers/writers 0x4178D0, 0x419490 and 0x4197C0 qualify the
exact offsets. This is ONLY a preservation carrier for verified reached
native player records. It does not generate incidents, execute callbacks,
deduce native values from generic RuntimePlayer suspensions, or deliver mail.
"""
from __future__ import annotations

from dataclasses import dataclass
from struct import unpack_from
from typing import Mapping


class OriginalNativeDisciplineError(ValueError):
    pass


_OFFSETS = (0x139, 0x13a, 0x13b, 0x13c, 0x13d, 0x13e, 0x144)
_RECORD_WIDTH = 9


def _uint(value: int, bits: int, name: str) -> int:
    if type(value) is not int or not 0 <= value < 1 << bits:
        raise OriginalNativeDisciplineError(f"source {name} unsigned {bits}-bit required")
    return value


@dataclass(frozen=True)
class OriginalNativePlayerDiscipline:
    native_player_id: int
    native_139: int
    native_13a: int
    native_fa_counter_13b: int
    native_13c: int
    native_13d: int
    native_uefa_counter_13e: int
    native_incident_accumulator_144: int
    native_fa_due_date_raw_160: int

    def __post_init__(self):
        _uint(self.native_player_id,16,"native player identity")
        for name in (
            "native_139","native_13a","native_fa_counter_13b",
            "native_13c","native_13d","native_uefa_counter_13e",
            "native_incident_accumulator_144",
        ):
            _uint(getattr(self,name),8,name)
        _uint(self.native_fa_due_date_raw_160,32,"native due-date DWORD")

    def array(self) -> list[int]:
        return [
            self.native_player_id,self.native_139,self.native_13a,
            self.native_fa_counter_13b,self.native_13c,self.native_13d,
            self.native_uefa_counter_13e,self.native_incident_accumulator_144,
            self.native_fa_due_date_raw_160,
        ]


def source_original_native_discipline_from_reached_player(
    *, original_native_player_record: bytes,
    original_mapped_runtime_player_index: int,
) -> OriginalNativePlayerDiscipline:
    """Preserve actual original fields; no synthetic new-game defaults.

    Caller must establish source player -> RuntimePlayer identity separately.
    A matching original +4 native id is a necessary, not sufficient, proof.
    Raw +160 is retained unsigned; signed compare/date base must not be guessed.
    """
    b=original_native_player_record
    if type(b) is not bytes or len(b)<0x164:
        raise OriginalNativeDisciplineError(
            "actual source player record through +0x160 required")
    target=_uint(original_mapped_runtime_player_index,16,"mapped RuntimePlayer identity")
    original_id=unpack_from("<H",b,4)[0]
    if original_id != target:
        raise OriginalNativeDisciplineError(
            "native +4 player identity and independently mapped RuntimePlayer differ")
    return OriginalNativePlayerDiscipline(
        original_id,*(b[x] for x in _OFFSETS),unpack_from("<I",b,0x160)[0])


def snapshot_original_native_discipline(
    records: Mapping[int,OriginalNativePlayerDiscipline],
) -> list[list[int]]:
    """Sparse sidecar keeps existing 48-field positional player save unchanged."""
    if not isinstance(records,Mapping):
        raise OriginalNativeDisciplineError("source native discipline map required")
    out=[]
    for player_id,record in sorted(records.items()):
        if type(player_id) is not int or not isinstance(record,OriginalNativePlayerDiscipline):
            raise OriginalNativeDisciplineError("native discipline player/type invalid")
        if player_id != record.native_player_id:
            raise OriginalNativeDisciplineError("native record key/player identity mismatch")
        out.append(record.array())
    return out


def restore_original_native_discipline(
    raw: list | None, valid_player_ids: set[int],
) -> dict[int, OriginalNativePlayerDiscipline]:
    """Old saves lack this optional field and contain NO inferred native state."""
    if raw is None:
        return {}
    if type(raw) is not list or type(valid_player_ids) is not set:
        raise OriginalNativeDisciplineError("native discipline sparse list/source players required")
    out={}
    previous=-1
    for entry in raw:
        if type(entry) is not list or len(entry)!=_RECORD_WIDTH:
            raise OriginalNativeDisciplineError("native discipline saved tuple must have nine fields")
        record=OriginalNativePlayerDiscipline(*entry)
        pid=record.native_player_id
        if pid not in valid_player_ids or pid<=previous:
            raise OriginalNativeDisciplineError(
                "native source player missing/duplicate/out of stored order")
        out[pid]=record
        previous=pid
    return out
