#!/usr/bin/env python3
"""Inspect verified table boundaries in FM2001 Static.dat.

This tool contains no original game data. Point it at a legally obtained
Static.dat and it validates/prints the table sequence decoded by the project.
"""

from __future__ import annotations
import argparse
import struct
from pathlib import Path

TABLES = [
    ("continents",              0x0000,  7,    10),
    ("countries",               0x004A,  209,  43),
    ("nationalities",           0x2369,  209,  3),
    ("positions",               0x25E0,  20,   7),
    ("formations",              0x2670,  21,   6),
    ("player_statuses",         0x26F2,  12,   4),
    ("competitions",            0x2726,  193,  53),
    ("rounds",                  0x4F1F,  1053, 36),
    ("cup_alloc_instructions",  0xE337,  238,  28),
    ("league_alloc_candidate",  0xFD43,  28,   28),
    ("real_fixtures",           0x10057, 380,  16),
    ("manager_rules_candidate", 0x1181B, 108,  16),
    ("prev_international_scores",0x11EDF,141,  28),
    ("international_fixtures",  0x12E4F, 23,   20),
]

def u32(data: bytes, off: int) -> int:
    return struct.unpack_from("<I", data, off)[0]

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("static_dat", type=Path)
    args = ap.parse_args()
    data = args.static_dat.read_bytes()

    print(f"Static.dat size: {len(data)} bytes (0x{len(data):X})")
    print()
    for name, off, expected_count, record_size in TABLES:
        if off + 4 > len(data):
            print(f"{name:28} 0x{off:06X} OUT OF RANGE")
            continue
        count = u32(data, off)
        end = off + 4 + count * record_size
        status = "OK" if count == expected_count and end <= len(data) else "CHECK"
        print(
            f"{name:28} off=0x{off:06X} "
            f"count={count:5} rec={record_size:3} "
            f"end=0x{end:06X} {status}"
        )

if __name__ == "__main__":
    main()
