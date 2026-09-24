from __future__ import annotations

import argparse
import struct
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BigFEntry:
    name: str
    offset: int
    size: int


def parse_bigf(path: Path) -> list[BigFEntry]:
    data = path.read_bytes()
    if len(data) < 16 or data[:4] != b"BIGF":
        raise ValueError(f"{path.name}: not a BIGF archive")
    _archive_size, count, _directory_end = struct.unpack_from(">III", data, 4)
    pos = 16
    entries: list[BigFEntry] = []
    for _ in range(count):
        if pos + 8 > len(data):
            raise ValueError(f"{path.name}: truncated BIGF directory")
        offset, size = struct.unpack_from(">II", data, pos)
        pos += 8
        end = data.find(b"\0", pos)
        if end < 0:
            raise ValueError(f"{path.name}: unterminated BIGF filename")
        name = data[pos:end].decode("cp1252", errors="replace")
        pos = end + 1
        if offset + size > len(data):
            raise ValueError(f"{path.name}: entry {name!r} exceeds file size")
        entries.append(BigFEntry(name, offset, size))
    return entries


def bigf_extract(path: Path, entry: BigFEntry) -> bytes:
    data = path.read_bytes()
    return data[entry.offset:entry.offset + entry.size]


@dataclass(frozen=True)
class ScTableRecord:
    sci_name: str
    masks: tuple[int, int, int, int]
    viv_name: str


def _cstring(raw: bytes) -> str:
    return raw.split(b"\0", 1)[0].decode("cp1252", errors="replace")


def parse_sctable_bytes(data: bytes, label: str = "SCTABLE.STI") -> list[ScTableRecord]:
    if len(data) < 4:
        raise ValueError(f"{label}: too short")
    count = struct.unpack_from("<I", data, 0)[0]
    expected = 4 + count * 48
    if expected != len(data):
        raise ValueError(
            f"{label}: expected {expected} bytes for {count} x 48-byte records, got {len(data)}"
        )
    out = []
    for i in range(count):
        off = 4 + i * 48
        rec = data[off:off + 48]
        out.append(
            ScTableRecord(
                _cstring(rec[0:16]),
                struct.unpack_from("<IIII", rec, 16),
                _cstring(rec[32:48]),
            )
        )
    return out


def parse_sctable(path: Path) -> list[ScTableRecord]:
    return parse_sctable_bytes(path.read_bytes(), path.name)


@dataclass(frozen=True)
class TbiLayout:
    count: int
    names_offset: int
    records: tuple[bytes, ...]
    names: tuple[str, ...]


def parse_tbi(path: Path) -> TbiLayout:
    data = path.read_bytes()
    if len(data) < 8:
        raise ValueError(f"{path.name}: too short")
    count, names_offset = struct.unpack_from("<II", data, 0)
    if names_offset < 8 or names_offset > len(data):
        raise ValueError(f"{path.name}: invalid secondary offset 0x{names_offset:X}")
    record_bytes = names_offset - 8
    if count == 0 or record_bytes % count:
        raise ValueError(f"{path.name}: primary table is not fixed-size")
    record_size = record_bytes // count
    records = tuple(
        data[8 + i * record_size:8 + (i + 1) * record_size] for i in range(count)
    )
    tail = data[names_offset:]
    if len(tail) % 24:
        raise ValueError(f"{path.name}: secondary table is not 24-byte aligned")
    names = tuple(_cstring(tail[i:i + 24]) for i in range(0, len(tail), 24))
    return TbiLayout(count, names_offset, records, names)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Inspect FM2001 MatchEngine data assets without modifying them."
    )
    ap.add_argument(
        "dataingame",
        type=Path,
        help="Path to the FM2001 DataInGame/DATAING directory",
    )
    args = ap.parse_args()
    root = args.dataingame

    loose_sci = sorted(
        {
            p.name.lower()
            for p in root.iterdir()
            if p.is_file() and p.suffix.lower() == ".sci"
        }
    )
    sctable = parse_sctable(root / "SCTABLE.STI")
    table_sci = {r.sci_name.lower() for r in sctable}

    print(f"Loose SCI files: {len(loose_sci)}")
    print(f"Loose SCTABLE records: {len(sctable)}")
    print("SCTABLE record size: 48 bytes")
    print(
        "Loose SCTABLE references present on disk: "
        f"{sum(n in loose_sci for n in table_sci)}/{len(table_sci)}"
    )
    print(f"Loose SCI not directly listed in SCTABLE: {len(set(loose_sci) - table_sci)}")

    archives: dict[str, list[BigFEntry]] = {}
    for filename in ("AISCRIPT.VIV", "MOAI.VIV", "GEN4TBLS.T"):
        entries = parse_bigf(root / filename)
        archives[filename] = entries
        print(f"{filename}: BIGF with {len(entries)} entries")

    ai_script = archives["AISCRIPT.VIV"]
    embedded_table_entry = next(
        (e for e in ai_script if e.name.lower() == "sctable.sti"), None
    )
    if embedded_table_entry:
        embedded = parse_sctable_bytes(
            bigf_extract(root / "AISCRIPT.VIV", embedded_table_entry),
            "AISCRIPT.VIV:sctable.sti",
        )
        archived_sci = {
            e.name.lower() for e in ai_script if e.name.lower().endswith(".sci")
        }
        embedded_sci = {r.sci_name.lower() for r in embedded}
        print(f"AISCRIPT embedded SCTABLE records: {len(embedded)}")
        print(f"AISCRIPT archived SCI entries: {len(archived_sci)}")
        print(
            "Embedded SCTABLE references archived SCI: "
            f"{sum(n in archived_sci for n in embedded_sci)}/{len(embedded_sci)}"
        )
        print(
            f"Embedded-only table names vs loose table: "
            f"{sorted(embedded_sci - table_sci)}"
        )
        print(
            f"Loose-only table names vs embedded table: "
            f"{sorted(table_sci - embedded_sci)}"
        )

    aiseqs = parse_tbi(root / "AISEQS.TBI")
    aitmps = parse_tbi(root / "AITMPS.TBI")
    print(
        f"AISEQS.TBI: {aiseqs.count} primary records, "
        f"{(aiseqs.names_offset - 8) // aiseqs.count}-byte primary records, "
        f"{len(aiseqs.names)} x 24-byte secondary entries"
    )
    print(
        f"AITMPS.TBI: {aitmps.count} primary records, "
        f"{(aitmps.names_offset - 8) // aitmps.count}-byte primary records, "
        f"{len(aitmps.names)} x 24-byte secondary entries"
    )

    moai_names = {e.name.lower() for e in archives["MOAI.VIV"]}
    seq_names = {n.lower() for n in aiseqs.names if n}
    matched = seq_names & moai_names
    print(
        f"AISEQS secondary names matching MOAI.VIV entries: "
        f"{len(matched)}/{len(seq_names)}"
    )
    print(f"AISEQS names not found in MOAI.VIV: {sorted(seq_names - moai_names)}")

    print("GEN4TBLS.T entries:")
    for entry in archives["GEN4TBLS.T"]:
        print(f"  {entry.name} ({entry.size} bytes)")


if __name__ == "__main__":
    main()
