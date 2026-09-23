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

### Continent table

Offset: `0x0000`

Header: uint32 count (=7)

Record size: 10 bytes.

Confirmed:

- +0 uint32: continent ID
- +4 uint16: English.str continent-name ID

Decoded names are Europe, Africa, Asia, North America, South America, Oceania, Other.

The meaning of +6..+9 is not yet proven.

### Country table

Offset: `0x004A`

Header: uint32 count (=209)

Record size: 43 bytes.

Confirmed:

- +0 uint32: country ID
- +4 uint16: English.str country-name ID
- +10 uint16: English.str three-letter abbreviation ID
- +24 uint32: continent ID
- +41 uint16: third country-related English.str ID (semantic role not yet proven)

Examples correctly resolve Albania/ALB/Europe, Algeria/ALG/Africa, United States/USA/North America, Argentina/ARG/South America and Australia/AUS/Oceania.

### Nationality table

Offset: `0x2369`

Header: uint32 count (=209)

Record size: 3 bytes.

Confirmed:

- +0 uint8: nationality ID
- +1 uint16: English.str nationality-name ID

Examples include Alaskian, Albanian, Algerian, American, Saudi Arabian, Argentinian, Australian and Austrian.

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

### Round table

Offset: `0x4F1F`

Header: uint32 count (=1,053)

Record size: 36 bytes.

Confirmed / strongly verified fields:

- +0 uint32: round-record ID
- +4 uint16: round/competition type code
- +6 uint16: competition ID
- +10 uint16: round or matchday number
- +14 uint16: English.str round/display-name ID
- +16 uint8: scheduled week
- +17 uint8: scheduled weekday
- +18 uint8: replay week (zero when not used)
- +19 uint8: replay weekday (zero when not used)
- +24 uint16: number of teams in the round
- +26 uint16: number of new entrants/allocated entrants for that round

Evidence:

- competition ID 0 has 38 records named `Prem League`, matching 38 Premier League matchdays.
- FA Cup records decode as 1st Round, 2nd Round, 3rd Round, 4th Round, 5th Round, Quarter Final, Semi Final, Final.
- Premier League scheduling begins week/day 7/6, 8/3, 8/6, matching Saturday → midweek → Saturday cadence.
- FA Cup round records carry replay week/day values.
- FA Cup team counts progress 80, 40, 64, 32, 16, 8, 4, 2; the 3rd round contains 44 new entrants.

Other flags/financial fields remain unmapped.

### Cup-allocation instruction table

Offset: `0xE337`

Header: uint32 count (=238)

Record size: 28 bytes.

Confirmed:

- +0 uint32: instruction ID
- +4 uint32: destination competition ID
- +8 uint32: instruction sequence/index within the competition

Strong evidence indicates later fields specify allocation source/type and team count. FA Cup instructions enumerate sources/counts that sum to 124 teams, and subsequent blocks target League Cup, Challenge Shield, Charity Shield, Champions League and other cup competitions. Exact semantics of +12/+16/+20/+24 are still being separated.

### League-allocation table candidate

Offset: `0xFD43`

Header: uint32 count (=28)

Record size: 28 bytes.

The table is structurally confirmed (records begin with sequential IDs), and the +4 field repeatedly references league competition IDs. It is the strongest current match for RTTI class `DBTLeagueAllocations`, but individual field semantics are not yet promoted to confirmed.

### Real fixture table

Offset: `0x10057`

Header: uint32 count (=380)

Record size: 16 bytes.

Confirmed:

- +0 uint32: fixture ID
- +4 uint32: zero-based Premier League round index
- +8 uint32: home club ID
- +12 uint32: away club ID

The 380 records equal 38 rounds × 10 matches. Round index 0 contains 10 fixtures, round index 1 the next 10, etc. Club IDs resolve to the real Premier League club set in `Master.dat` (Arsenal, Aston Villa, Chelsea, Manchester United, Charlton Athletic, Derby County, Ipswich Town, Leicester City, Sunderland, Bradford City, etc.).

### Previous international score table

Offset: `0x11EDF`

Header: uint32 count (=141)

Record size: 28 bytes.

Confirmed:

- +0 uint32: score-record ID (all 0..140 are present, though file order is not numeric)
- +12 uint32: home national-team club ID
- +16 uint32: away national-team club ID
- +20 uint32: home score
- +24 uint32: away score

The home/away IDs resolve to national-team club records such as Austria, Spain, San Marino, Israel, Cyprus, Estonia, Faroe Islands, Bosnia, Scotland, etc. Non-zero result examples (including 5-0) verify that the last two fields are scores.

The semantics of +4 and +8 remain to be mapped. RTTI contains `DBRPrevInternationalScore` / `DBTPrevInternationalScores`, matching this structure.

### International tournament-cycle / host table

Offset: `0x12E4F`

Header: uint32 count (=23)

Record size: 20 bytes.

Confirmed:

- +0 uint32: record ID, 1..23
- +4 uint32: tournament year (2002, 2004, ... 2046)
- +8 uint32: competition ID
- +12 uint32: primary host national-team club ID
- +16 uint32: secondary host national-team club ID, or `0xffffffff`

Competition IDs alternate between World Cup (174) and European Championship (171). Host IDs resolve to national-team records. This structure matches RTTI `DBRInternationalFixture` / `DBTInternationalFixtures` and demonstrates that FM2001 carries international tournament-cycle data through 2046.

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
