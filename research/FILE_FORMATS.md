# File Format Analysis

This file records verified structures for FM2001 game data. Offsets currently apply to the exact analyzed release identified by hashes in `research/FINDINGS.md`.

## String-table format (.str)

Used by at least `English.str` and `Core.str`.

### Header/index

| Offset | Type | Meaning |
|---|---|---|
| +0 | uint32 LE | table/index boundary |
| +4 | uint32 LE | number of indexed strings |
| table_offset + 8 | uint32[count] | relative offsets to NUL-terminated strings |

For each entry, the decoded byte position is `8 + relative_offset`. Strings decode correctly using CP1252.

## Master.dat

### Top-level layout

```text
+0x00000000  uint32 club_count (=1246)
+0x00000004  Club[1246]             record size 181
              ...
              player section header/count
              Player[30064]         record size 103
              Manager[1612]         record size 43
              2-byte trailer
```

The exact meaning of every player-section header byte is still being formalized; the known parser uses a six-byte player header at the current boundary.

### Club record (181 bytes)

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| +4 | uint16 | English.str club full-name ID | confirmed |
| +6 | uint16 | English.str short-name ID | confirmed |
| +16 | uint16 | English.str map-file ID | confirmed |
| +30 | uint16 | English.str stadium-name ID | confirmed |
| +44 | uint16 | English.str badge-file ID | confirmed |
| +46 | uint16 | English.str sponsor ID | confirmed |
| +48 | uint16 | manager-record ID | confirmed |

Unmapped fields remain.

### Player record (103 bytes)

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| +0 | uint16 | Core.str first-name ID | confirmed |
| +2 | uint16 | Core.str surname ID | confirmed |
| +4 | uint16 | club ID | confirmed |
| +12 | uint32 | DOB serial date | confirmed |
| +17 | uint8 | height cm | confirmed |
| +18 | uint8 | weight kg | confirmed |
| +19 | uint8 | primary position code | confirmed |
| +20 | uint8 | secondary position code | confirmed |
| +21 | uint8 | tertiary position code | confirmed |
| +22..+39 | uint8[18] | player attribute bytes | confirmed block; semantic order tentative |
| +74 | uint32 | club-join serial date | confirmed |

Dates decode using the OLE-style epoch `1899-12-30`.

### Manager record (43 bytes)

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| +6 | uint16 | Core.str first-name ID | confirmed |
| +8 | uint16 | Core.str surname ID | confirmed |
| +10 | uint32 | DOB serial date | confirmed |
| +22 | uint32 | club-join serial date | confirmed |
| +29 | uint32 | club ID; 0xffffffff = no club | confirmed |

## Static.dat

`Static.dat` is a concatenation of database-like tables.

### Position table

Offset: `0x25E0`

Header: uint32 count (=20)

Record size: 7 bytes.

| Offset | Type | Meaning |
|---|---|---|
| +0 | uint8 | position ID |
| +1 | uint16 | English.str long-name ID |
| +3 | uint16 | English.str abbreviation ID |
| +5..+6 | bytes | not yet mapped |

### Formation table

Offset: `0x2670`

Header: uint32 count (=21)

Record size: 6 bytes.

| Offset | Type | Meaning |
|---|---|---|
| +0 | uint8 | formation ID |
| +1 | uint16 | English.str formation-name ID |
| +3 | uint8 | tactical/shape parameter A |
| +4 | uint8 | tactical/shape parameter B |
| +5 | uint8 | tactical/shape parameter C |

Decoded names, in order:

`4-4-2`, `4-4-2 Att`, `4-4-2 Def`, `5-3-2`, `5-3-2 Att`, `5-3-2 Def`, `3-4-3`, `3-4-3 Att`, `3-4-3 Def`, `3-5-2`, `3-5-2 Att`, `3-5-2 Def`, `4-3-3`, `4-3-3 Att`, `4-3-3 Def`, `4-5-1`, `2-5-3`, `5-4-1`, `Long Ball`, `Sweeper`, `Xmas Tree`.

The exact meaning of the three trailing bytes remains unproven.

### Player-status table

Offset: `0x26F2`

Header: uint32 count (=12)

Record size: 4 bytes.

| Offset | Type | Meaning |
|---|---|---|
| +0 | uint8 | status ID |
| +1 | uint16 | English.str status-name ID |
| +3 | uint8 | status flag (semantic meaning not yet proven) |

Decoded statuses:

1. Injured
2. Banned
3. International
4. Cup Tied
5. First Team
6. Subsitute [sic in game data]
7. On loan
8. Out of contract
9. Transfer listed
10. Bid in
11. Wanted
12. Non EU

### Competition table

Offset: `0x2726`

Header: uint32 count (=193)

Record size: 53 bytes.

| Offset | Type | Meaning |
|---|---|---|
| +0 | uint32 | competition ID |
| +12 | uint16 | English.str competition-name ID |

Other competition fields are not yet semantically mapped.

## Save files

Known executable path pattern: `games\\%d.sav`.

The executable contains an incompatible-save/version message, but the save binary format has not yet been decoded.

## .SCI match data

Approximately 252 `.SCI` files exist under `DataInGame`.

Current status: binary format unknown.

Related readable `camera.scr` contains camera-mode definitions for live play, set pieces, replays, manual replay, out-of-play and half time.

## Next format work

1. Map all remaining `Static.dat` table boundaries to RTTI table classes.
2. Decode league allocation, cup allocation, rounds and fixture structures.
3. Map player attribute semantics and contract/financial fields.
4. Map club financial/stadium fields.
5. Decode save serialization.
6. Decode `.SCI` and formation/tactical data as needed by the match engine.
