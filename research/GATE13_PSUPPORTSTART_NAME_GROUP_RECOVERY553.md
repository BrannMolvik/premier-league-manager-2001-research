# Recovery553: source-correct original SupportStart name group routing

Original source original `footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
and original `Static.dat` 86,929 bytes SHA-256
`e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`
plus `Master.dat` 3,391,446 bytes SHA-256
`183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`
were independently used **as private source bytes**, without executing
the original EXE or publishing the original input datasets.

## Actual original source owner distinction (corrects Recovery552 ambiguity)

The original `0x50D630` open/read sequence loads:
`0x40B9C0` on owner `0x874B88` first, count **1246 CLUBS**
with expanded **0x2A8** byte records; then
`0x4218C0` on owner `0x875638`, count **30064 PLAYERS**
with expanded **0x250** byte records; then
`0x415B70` on `0x875620` for **1612 MANAGERS**.
The three counts and raw stream byte alignment are independently
reproducible from original Master.dat sections:
clubs 181B, players103B, managers43B. The earlier wording in
Recovery552 that conflated managers with the `0x875638`
fallback pool was incorrect: it is unequivocally a PLAYER pool.

Original `0x50D47D→0x4117E0→0x410640` loads
`0x874BD8` country record owner (native 0x6C stride) from
Static.dat. The source country section starts at `0x4A` with
209 countries of serialized stride 43B from `0x4E`.
The native country record `+0x0C`, read by
name selector `0x421C00`, comes from serialized raw
`country+6` u32 at `0x410676`; this is
**not the country's array index in every case**.
Independent original byte audit: **59 of 209 country
records remap their group**, including record199's
`0xFFFFFFFF` which `0x421C00` maps
to fallback group **26**. All other country source
group indices are within 0..208.

Immediately after 209×43 countries,
`Static.dat+0x2369` contains 209 original native
group identities, serialized **3 bytes apiece**
from `0x236D` through `0x25DF`.
Original `0x50D48D→0x64CB40` dynamically
constructs `0x874BC8` name-group vector in
native 0x14-byte slots; per-record vft+0x0C
`0x410480` reads a u8 group ID and
localized u16 source text index through `0x64CAA0`.
The 209 group IDs are exactly 0..208, and
their English indices run634..842. Native group
`+0x0C` pointer and `+0x10` count start
zero (constructor `0x410D80`) until actual
Master-driven runtime membership construction.

At `0x50D6B6→0x4F6EB0→0x411440`,
the original constructs per-group **CLUB**
counts from `0x874B90` 1246 club records,
using expanded club field `+0x14`
(original source `Master.dat` club+12 country ID).
It counts, allocates, then inserts original club
record pointers into each group, preserving
the original source owner and record order.
Original `0x421BA0` has two distinct name
candidate branches:

- When a native group has **more than 10 clubs**,
  calls original `0x64D540` with group club count
  and dereferences its pointer array (selected
  expanded CLUB record `+0x08/+0x0C` values).
- When it has **10 or fewer clubs**, calls
  original `0x64D540` with the **global 30064
  PLAYER count** and resolves a fixed
  0x250-stride player record from `0x875638`
  (selected player first/surname `+0x08/+0x0C`).

Both branches are original source selection facts;
this is NOT independent proof of which exact name
strings appear for generated staff at startup,
since original shared CRT seed, group/native owner
callback details and per-string concatenation
require further validation. Do not replace them
with guessed managers or uniform player sampling.

The feature branch adds
`original_supportstart_name_group_source.py`:
a checksum-strict parser of the original Static.dat
country/group mapping (supports synthetic
source-shaped fixture only when explicitly flagged
for tests), and a **data-only source routing
projection** that decides the qualified club-vs-player
candidate pool from the original 1246 club records,
source country group and global player count.
It does NOT call random, pick an index, invent
source users or render fake staff names.
Three unit test methods verify source native
threshold >10, country199 fallback26,
group labels, file-size/offset checks,
and fail-closed unknown inputs.

### Independent original concrete counts

The original serialized Master.dat club country
distribution contains **1246 clubs** across
91 represented source country IDs; group26
contains 130 clubs, group1 contains 11 clubs;
36 original source country groups have more
than10 clubs and 173 have at most10.
This is independent source-data evidence,
not a claim of an observed original GUI session.

### Next gate implementation step

Trace original `0x421BA0` selected-CLUB +8/+C
name/text semantics, the true `0x4CA660`
name concatenation branch under a real qualified
source group, and reconcile original CRT TLS
state before support staff creation. Do not
construct fake names or approximate mouse hitboxes.
Connect the authentic PSupportStart renderer,
seven staff rows, original source-labelled role
and user fields, source event ownership, Apply/Cancel
and TeamSelect return as one fully verified
player-visible milestone. Gate13–17 and genuine
Windows11 GUI tests remain open.

Private disassembly:
```bash
objdump -D -Mintel --start-address=0x50d630 --stop-address=0x50d6c0 footballmanager.exe
objdump -D -Mintel --start-address=0x410640 --stop-address=0x410790 footballmanager.exe
objdump -D -Mintel --start-address=0x411440 --stop-address=0x411558 footballmanager.exe
objdump -D -Mintel --start-address=0x410480 --stop-address=0x4104bc footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421c49 footballmanager.exe
```

## Recovery553 additional source-qualified club-name candidate projection

Original `0x421BA0` group-club >10 case returns an actual native
`0x874B90` CLUB pointer, not a first/surname PLAYER pointer.
Native `0x421C00` uses `selected_first_record+0x08` and
`selected_second_record+0x0C`. Original club loader
`0x4022D0` resolves those from the real original
Master.dat `club+4` name and `club+6` short-name
indices, respectively, through the original English.str.
The result can resemble an unusual staff name, but
**no invented personal name may replace that source
branch simply because it seems odd**.

The new bounded
`original_supportstart_club_name_source.py`
requires a source-proven group>10 route and two
explicit source-observed *club positions* within
its true native country group; then reads
only the original club text fields from the
unchanged 1246-club source records, with strict
source sentinel, CP1252 and member validation.
It does not perform the original shared CRT RNG
calls or invent which indices were chosen.
Its focused tests demonstrate a synthetic
first-club full-name plus second-club short-name
projection (not an actual staff name), and
reject all unqualified group/position/encoding
cases.

This is an additional source-reader building block,
**not** live SupportStart render/edit acceptance.
The exact random choice/first-text sentinel retries,
source UI event-hit callback and multimanager
persistence still require original-first verification.

Original private source reproductions:
```bash
objdump -D -Mintel --start-address=0x4022d0 --stop-address=0x40232a footballmanager.exe
objdump -D -Mintel --start-address=0x411440 --stop-address=0x411558 footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421c49 footballmanager.exe
```
