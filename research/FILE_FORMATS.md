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
              uint32 player_count (=30064)
              Player[30064]         record size 103
              uint32 manager_count (=1612)
              Manager[1612]         record size 43
              EOF
```

### Club record (181 bytes)

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| +4 | uint16 | English.str club full-name ID | confirmed |
| +6 | uint16 | English.str short-name ID | confirmed |
| +16 | uint16 | English.str map-file ID | confirmed |
| +30 | uint16 | English.str stadium-name ID | confirmed |
| +44 | uint16 | English.str badge-file ID | confirmed |
| +46 | uint16 | English.str sponsor ID | confirmed |
| +48 | uint32 | manager-record ID | confirmed |

Unmapped fields remain.

### Player record (103 bytes)

The record size is now confirmed independently in two ways:

1. the `Master.dat` section boundary fits exactly with 30,064 × 103-byte records; and
2. EA's actual startup importer at `0x418B90` performs 35 file reads totaling exactly **103 bytes per player**.

The player section begins after a **four-byte header only**:

```text
uint32 player_count = 30064
Player[player_count]
```

This is confirmed directly by loader `0x421C80`, which reads one 4-byte count and immediately enters the 103-byte record loop. The earlier six-byte-header interpretation was a two-byte alignment error.

The compact record is expanded into a 592-byte runtime `DBRPlayer` object. The following table therefore records **file offsets and loader destinations**, not speculative UI names.

| File offset | Size | Destination / processing | Semantic identification | Status |
|---|---:|---|---|---|
| +0 | 2 | runtime +0x04 | player record ID | confirmed |
| +2 | 2 | Core.str index -> runtime +0x08 | first name | confirmed |
| +4 | 2 | Core.str index -> runtime +0x0C | surname | confirmed |
| +6 | 2 | runtime +0x10 | club record index | confirmed |
| +8 | 1 | runtime +0x12 | nationality ID | confirmed |
| +9 | 1 | temporary | primary/default position code (zero-based relative to position table IDs) | strongly verified |
| +10 | 4 | runtime +0x14 | flags/state field | confirmed read; semantic details unresolved |
| +14 | 4 | runtime +0x18 | date of birth, OLE-style serial date | confirmed |
| +18 | 1 | runtime +0x70 | shirt/squad number | strongly verified |
| +19 | 1 | runtime +0x1C | height in centimeters | confirmed |
| +20 | 1 | runtime +0x1D | weight in kilograms | confirmed |
| +21 | 3 | temporary, then transformed by `0x4EA2D0` | three zero-based position codes | strongly verified |
| +24 | 17 | runtime +0x1E..+0x2E | skill-related array A | confirmed block; labels unresolved |
| +41 | 17 | runtime +0x2F..+0x3F | skill-related array B | confirmed block; relationship unresolved |
| +58 | 1 | runtime +0x40 | unknown | confirmed read |
| +59 | 1 | runtime +0x41 | unknown | confirmed read |
| +60 | 1 | runtime +0x42 | unknown | confirmed read |
| +61 | 1 | runtime +0x43 | unknown | confirmed read |
| +62 | 1 | runtime +0x44 | unknown | confirmed read |
| +63 | 1 | runtime +0x45 | unknown | confirmed read |
| +64 | 4 | runtime +0x48 | unknown | confirmed read |
| +68 | 8 | runtime +0x50 | unknown 64-bit/date-like field | confirmed read |
| +76 | 4 | runtime +0x58 | unknown | confirmed read |
| +80 | 2 | runtime +0x5C | unknown | confirmed read |
| +82 | 2 | runtime +0x5E | unknown | confirmed read |
| +84 | 1 | runtime +0x60 | unknown | confirmed read |
| +85 | 1 | runtime +0x61 | unknown | confirmed read |
| +86 | 1 | runtime +0x62 | unknown | confirmed read |
| +87 | 1 | runtime +0x63 | unknown | confirmed read |
| +88 | 4 | runtime +0x64 | unknown | confirmed read |
| +92 | 4 | runtime +0x68 | unknown | confirmed read |
| +96 | 1 | runtime +0x6C | unknown | confirmed read |
| +97 | 2 | temporary A | version-dependent/derived choice input | confirmed read |
| +99 | 2 | temporary B | version-dependent/derived choice input | confirmed read |
| +101 | 2 | temporary C | version-dependent/derived choice input | confirmed read |

#### Corrected alignment and attribute interpretation

The former assumptions that the player section had a six-byte header and that `+22..+39` was an 18-byte attribute array are **incorrect**.

The original importer proves that the compact record instead contains:

- a 3-byte group at `+21..+23` containing three zero-based position codes, transformed into the runtime position structure;
- a **17-byte array at +24..+40**;
- a **second 17-byte array at +41..+57**.

These two arrays map directly into the same two 17-byte regions present in the runtime `DBRPlayer` object. Their exact semantic relationship (for example current/base/potential skill representations) is still under investigation and must not yet be labeled.

Earlier semantic labels for file offsets such as first name, surname, club, DOB, height and weight are being revalidated against EA's actual importer/accessors. Some happened to produce plausible values in the prototype, but the original loader shows that several early fields are transformed through reference tables rather than copied literally.

### Player compact-vs-runtime caution

The 103-byte `Master.dat` player record is an initial compact database representation. EA's runtime `DBRPlayer` object is 592 bytes.

The startup importer `0x418B90` reads both 17-byte arrays directly from `Master.dat`, while the runtime/save representation contains the same adjacent regions. This is stronger evidence than the earlier inferred 18-byte block, but the actual rating scale and field names still require tracing through accessors/consumers.

Therefore:

- do not apply the prototype's earlier linear `raw * 30 / 255` conversion;
- do not label the 17 elements until their accessor/consumer code is recovered;
- keep compact-file offsets distinct from runtime-object offsets and save-game fields.


### Player skill-array semantics and scale

The two 17-byte arrays in the compact player record now have a substantially firmer interpretation.

Runtime/file relationship:

- compact `+24..+40` -> runtime `+0x1E..+0x2E`: **current skill values**
- compact `+41..+57` -> runtime `+0x2F..+0x3F`: **corresponding peak/development target values**

Evidence:

- routine `0x41A870` indexes the same slot in both arrays and only increases the current-skill byte while the incremented value remains below the matching second-array value;
- the age/development routine around `0x41EB03..0x41EDC8` repeatedly reads the second-array byte and writes an interpolated/adjusted value into the matching first-array slot;
- across all 30,064 compact player records, 99.605% of the 511,088 paired bytes satisfy `array_B >= array_A`.

The few exceptions must still be explained, but the second array is clearly acting as a development/peak target rather than another independent visible characteristic set.

#### Raw-byte to 0-30 conversion

EA's own overall-rating code converts each raw 0-255 skill byte with the exact integer transformation equivalent to:

```text
displayed_skill = floor((30 * raw + 128) / 255)
```

This yields an integer range of 0..30.

The earlier prototype's general idea of mapping bytes to a 0-30 scale was therefore directionally correct, but the record alignment and attribute boundaries were previously wrong.

#### Confirmed current-skill slot identities

The position-overall function at `0x41C7E0` combines current-skill slots with named tuning weights such as `overallgkspeed`, `overallrbtackling`, etc. This directly proves these slot identities:

| Array slot | Runtime offset | Skill |
|---:|---:|---|
| 0 | +0x1E | Speed |
| 1 | +0x1F | Strength |
| 5 | +0x23 | Passing |
| 6 | +0x24 | Shooting |
| 7 | +0x25 | Tackling |
| 8 | +0x26 | Heading |
| 11 | +0x29 | Awareness |
| 12 | +0x2A | Agility |
| 13 | +0x2B | Goalkeeping |
| 14 | +0x2C | Confidence |
| 15 | +0x2D | Leadership |

Leadership is independently supported by code around `0x41BA80` / `0x41BB10`: accessor `0x41EDE0` returns runtime byte `+0x2D`, and that value is compared directly against tweak variable `goodleadership`.

The complete 17-slot order is now recovered:

| Slot | Skill |
|---:|---|
| 0 | Speed |
| 1 | Strength |
| 2 | Stamina |
| 3 | Determination |
| 4 | Injury Proneness |
| 5 | Passing |
| 6 | Shooting |
| 7 | Tackling |
| 8 | Heading |
| 9 | Control |
| 10 | Technique |
| 11 | Awareness |
| 12 | Agility |
| 13 | Goalkeeping |
| 14 | Confidence |
| 15 | Leadership |
| 16 | Set Piece |

The remaining six names were verified using EA's bundled Editor.exe. Its Player Skills dialog (dialog resource ID 0x73) binds edit controls to an internal contiguous skill-byte region in this exact order. The editor mapping independently agrees with every slot already proven from the game's position-overall formula.


### Manager section and record (43 bytes)

The player section is followed by a four-byte manager count (=1,612), then 1,612 packed 43-byte manager records. The manager array ends exactly at EOF.

| Offset | Type | Meaning | Confidence |
|---|---|---|---|
| +0 | uint32 | manager record ID | confirmed |
| +4 | uint16 | Core.str first-name ID | confirmed |
| +6 | uint16 | Core.str surname ID | confirmed |
| +8 | uint32 | DOB serial date | confirmed |
| +20 | uint32 | club-join serial date | confirmed |
| +27 | uint32 | club ID; 0xffffffff = no club | confirmed |

Validation examples:
- manager 10 -> Alex Ferguson, DOB 1941-12-31, joined 1986-11-06, club ID 10;
- manager 204 -> Arsène Wenger, DOB 1958-01-01, joined 1996-09-30, club ID 0 (Arsenal).

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
| +5 | uint8 | position ordering key used by team-selection/status ordering; 255 for None/RF/LF | strongly verified |
| +6 | uint8 | broad selection category: 0 defender, 1 midfielder, 2 attacker, 3 goalkeeper; 255 for None/RF/LF | strongly verified |



The two final Position-table bytes correlate directly with the runtime 20-byte position metadata used by team selection. The shipped values are:

| Runtime role | +5 order | +6 category |
|---|---:|---:|
| None | 255 | 255 |
| GK | 0 | 3 |
| RB | 1 | 0 |
| LB | 3 | 0 |
| CB | 5 | 0 |
| SW | 6 | 0 |
| RWB | 2 | 0 |
| LWB | 4 | 0 |
| ANC | 7 | 1 |
| DM | 8 | 1 |
| RM | 10 | 1 |
| LM | 11 | 1 |
| CM | 9 | 1 |
| RW | 13 | 1 |
| LW | 14 | 1 |
| AM | 12 | 1 |
| RF | 255 | 255 |
| LF | 255 | 255 |
| CF | 15 | 2 |
| ST | 16 | 2 |

Runtime helper `0x4EA310` returns the category byte through the loaded position-metadata record. The status comparator `0x417E20` uses the order byte inside each selection-status class.

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


#### Week/day date interpretation

For the shipped Premier League schedule, the two scheduling bytes decode as:

- weekday **1..7 = Monday..Sunday**;
- week 0 = the Monday-led week containing July 1 of the season start year.

Thus:

```
week_zero_monday = July 1 - weekday_offset_to_Monday
date = week_zero_monday + week*7 + (weekday-1)
```

This reproduces known 2000–01 schedule dates directly from Static.dat, including 19 Aug 2000, 23 Aug 2000, Boxing Day (26 Dec), New Year's Day (1 Jan), and the final Sunday 20 May 2001.

### Cup-allocation instruction table

Offset: `0xE337`

Header: uint32 count (=238)

Record size: 28 bytes.

Confirmed:

- +0 uint32: instruction ID
- +4 uint32: destination competition ID
- +8 uint32: instruction sequence/index within the competition

Strong evidence indicates later fields specify allocation source/type and team count. FA Cup instructions enumerate sources/counts that sum to 124 teams, and subsequent blocks target League Cup, Challenge Shield, Charity Shield, Champions League and other cup competitions. Exact semantics of +12/+16/+20/+24 are still being separated.

### League-allocation table

Offset: `0xFD43`

Header: uint32 count (=28)

Record size: 28 bytes.

Class identity is confirmed as `DBTLeagueAllocations` by the actual `Static.dat` load order: global object `0x876C28` has vtable `0x7C9844`, whose RTTI is `DBTLeagueAllocations`, and is loaded immediately after `DBTCupAllocInstructions`.

Confirmed:

- records are 28 bytes on disk
- +0 uint32: sequential allocation-record ID
- +4 uint32: league competition ID

Other field semantics are still being mapped.

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

### International fixture table

Offset: `0x1181B`

Header: uint32 count (=108)

Record size: 16 bytes.

Class identity is confirmed as `DBTInternationalFixtures` from the actual loader sequence. Its record reader (`DBRInternationalFixture`) reads the packed fields as:

- +0 uint32
- +4 uint16
- +6 uint16
- +8 uint32
- +12 uint32

Observed values strongly indicate scheduling/routing information for international competition regions. The final two fields reference international competition/region IDs such as Europe (170), South America (177), North America (178), Africa (179), Asia (180), and Oceania (181). Exact semantic names for all five fields remain under investigation.

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

### International tournament host table

Offset: `0x12E4F`

Header: uint32 count (=23)

Record size: 20 bytes.

Class identity is confirmed as `DBTHosts` / `DBRHost` from the actual loader sequence.

Confirmed:

- +0 uint32: record ID, 1..23
- +4 uint32: tournament year (2002, 2004, ... 2046)
- +8 uint32: competition ID
- +12 uint32: primary host national-team club ID
- +16 uint32: secondary host national-team club ID, or `0xffffffff`

Competition IDs alternate between World Cup (174) and European Championship (171). Host IDs resolve to national-team records. FM2001 therefore carries international tournament host-cycle data through 2046.

### Manager rating table

Offset: `0x1301F`

Header: uint32 count (=20)

Packed record size: 6 bytes.

Class identity is confirmed as `DBTManagerRatings`. The binary reader for `DBRManagerRating` reads:

- +0 uint32
- +4 uint8
- +5 uint8

All 20 records in this release have first field 0; the second field runs 0..19. The exact semantic labels of the final byte are still being traced.

### Manager expected-ranking table

Offset: `0x1309B`

Header: uint32 count (=262)

Packed record size: 9 bytes.

Class identity is confirmed as `DBTManagerExpectedRankings`. The binary reader for `DBRManagerExpectedRanking` reads:

- +0 uint32
- +4 uint8
- +5 uint16
- +7 uint16

### Manager sack-league table

Offset: `0x139D5`

Header: uint32 count (=24)

Packed record size: 7 bytes.

Class identity is confirmed as `DBTManagerSackLeagues`. The binary reader for `DBRManagerSackLeague` reads:

- +0 uint32
- +4 uint8
- +5 uint16

The 24 records begin with sequential IDs 0..23 and threshold-like values.

### Manager sack-cup table

Offset: `0x13A81`

Header: uint32 count (=66)

Packed record size: 8 bytes.

Class identity is confirmed as `DBTManagerSackCups`. The binary reader for `DBRManagerSackCup` reads eight one-byte values into the record after its vtable/base object bookkeeping. The data forms competition/round-like groups with six threshold values; exact labels remain to be mapped.

### Access fan-base table

Offset: `0x13C95`

Header: uint32 count (=42)

Packed record size: 78 bytes.

Class identity is confirmed as `DBTAccessFanBase` / `DBRAccessFanBase`. The class binary reader consumes one uint16 followed by nineteen uint32 values (78 packed bytes total).

The table ends exactly at `0x14965`, where the next verified table begins.

### Access skill/financial-values table

Offset: `0x14965`

Header: uint32 count (=100)

Packed record size: 26 bytes.

Class identity is confirmed as `DBTAccessSkillFinancialValues` / `DBRAccessSkillFinancialValue`. The binary reader consumes one uint16 followed by six uint32 values.

The 100 records end exactly at `Static.dat` EOF (`0x15391`).

## Save files

Known executable path pattern: `games\\%d.sav`.

The executable contains an incompatible-save/version message, but the save binary format has not yet been decoded.

## MatchEngine scenario / animation data

The exact extracted disc contains **235 loose `.SCI` files** under `DATAING`. This supersedes the earlier rough estimate of approximately 252.

The loose `SCTABLE.STI` contains uint32 count **137** followed by 137 fixed **48-byte** records:

- +0x00: SCI filename[16]
- +0x10..+0x1C: four uint32 condition/mask fields
- +0x20: VIV filename[16]

Executable loader `0x70F000` independently confirms the 48-byte runtime record size.

`AISCRIPT.VIV`, `MOAI.VIV`, and `GEN4TBLS.T` use EA's BIGF archive format with big-endian offsets/sizes and NUL-terminated filenames.

Archive counts:

- AISCRIPT.VIV: 140 entries, including an embedded 139-record SCTABLE plus 139 SCI files;
- MOAI.VIV: 584 entries;
- GEN4TBLS.T: 7 entries.

`AISEQS.TBI` and `AITMPS.TBI` are each 23,088 bytes and consist of:

- 8-byte header;
- 452 × 20-byte primary records;
- 585 × 24-byte secondary entries.

AISEQS contains one blank secondary entry; its other **584 names exactly match the 584 MOAI.VIV entry names**.

The internal SCI instruction/choreography format is not yet decoded, but SCI files contain many readable identifiers that overlap MOAI motion names and are clearly structured rather than encrypted/opaque.

Related readable `CAMERA.SCR` contains camera-mode definitions for live play, set pieces, replays, manual replay, out-of-play and half time.

See `research/MATCH_ENGINE.md` and `tools/inspect_match_assets.py` for the current detailed analysis.

## Next format work

1. Finish semantics of remaining partially decoded Static.dat fields (competition/allocation/manager thresholds).
2. Map remaining Master.dat club/player/manager fields needed by gameplay.
3. Decode save serialization.
4. Decode .SCI and formation/tactical data needed by the match engine.
5. Keep clean-room parsers synchronized with the verified layouts above.
