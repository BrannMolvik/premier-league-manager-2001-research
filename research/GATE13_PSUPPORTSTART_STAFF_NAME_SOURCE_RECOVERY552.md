# Recovery552: original SupportStart staff personal name path and missing name-pool boundary

**Source:** statically inspected original 4,714,541-byte
`footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The original executable was NOT launched. This is an exact source
allocation/selection/concatenation trace, not a generated staff-name
implementation.

## Native staff name data producer

- Actual CSupportStaff vtable `0x7C6834+0x08`
  resolves `0x4CA340`, which returns address
  `CSupportStaff+0x184`; that is the source
  name buffer returned to original SupportStart.
- Native `0x4CA2F0` constructor calls
  `0x4CA660` with an original group/nationality
  selector at its arguments after storing native
  staff type at+0x04.
- `0x4CA660` invokes `0x421C00` on original
  name pool owner `0x875638` using the same
  group selector. `0x421C00` obtains the source
  group record from `0x874BE0`: stride is
  exactly **0x6C=108 bytes** (`27*sizeof(DWORD)`);
  it uses the group record's +0x0C field. A
  `0xFFFFFFFF` sentinel maps to fallback group
  index `0x1A=26`.
- It invokes `0x421BA0` **twice** with the same
  group index and returns candidate first-name pointer
  from chosen record+0x08 and independently
  chosen surname pointer from record+0x0C.
  Each of those calls may draw from the shared
  original CRT RNG via `0x64D540`.
- `0x421BA0` indexes group table `0x874BD0`
  at **0x14=20-byte** stride. If group entry
  +0x10 (count) is strictly greater than 10,
  it draws `randbelow(group_count)`
  and follows the group pointer array at+0x0C.
  Otherwise it draws from the global
  `0x875638+0x04` count and obtains a
  fallback fixed-size `0x250=592-byte`
  record at `0x875638+0x08 + draw*0x250`.
  These are different original RNG-owner paths,
  not a uniform choice from displayed staff names.
- Native `0x4CA660` compares the selected
  first-name string against original literal
  `0x8185D0`, known sentinel `"-"`, and
  repeats the source name-draw attempt if equal.
  It then calls staff virtual+0x0C
  (`0x4CA6E0`) with first/surname pointers.
- `0x4CA6E0` concatenates source first name,
  original literal `0x81AF38` (verified
  **ASCII space `" "`** from the original
  executable .data), then surname into
  `CSupportStaff+0x184`, using native
  CRT-style string copying. This does not
  establish a safe maximum size for the
  legacy write; a port must enforce safe bounds
  rather than replicate unsafe overflow.

## Source pool lifecycle and current unresolved inputs

The original collection global `0x874BE0`
is an MSVC-style owner with count at
`0x874BDC`, pointer at `0x874BE0`,
source record stride `0x6C`.
Original static init `0x410AA0` zeros the count
and pointer; `0x410B00` resizes/constructs
the `0x6C` vector. Separate table `0x874BD0`
has owner `0x874BC8`, count at
`0x874BCC`, pointer at `0x874BD0`,
`0x14` stride, initialized at `0x410C70`
and resized via `0x410CB0`.
The code trace does **not yet identify** the
actual `Master.dat/Static.dat/DataInGame`
producer fields that populate either table,
the exact first-name/surname candidate records
or where in the canonical fresh game the shared
CRT TLS RNG sits at staff creation.
Do not fabricate personal names by sampling
unrelated player names or consuming one of the
reconstruction's separated RNG streams.

The current reconstruction `SupportStaffState`
stores only `staff_type, age_like, rating, status`;
it has **no source-proven full-name field** and
therefore cannot yet display authentic original
PSupportStart staff personal names.
The new original source-art loader and role-label
projection can render art/roles but must not
pretend that the names are restored. The
complete SupportStart modal and GUI acceptance
remain OPEN, as do other Gates13–17 criteria.

## Exact reproducible private disassembly

```bash
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca33f footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca6d0 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca6e0 --stop-address=0x4ca760 footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421c49 footballmanager.exe
objdump -D -Mintel --start-address=0x410aa0 --stop-address=0x410be0 footballmanager.exe
objdump -D -Mintel --start-address=0x410c70 --stop-address=0x410d91 footballmanager.exe
```

**Next source task:** trace the original producers for
`0x874BE0` 0x6C records and `0x874BD0`
0x14 name-group records back to specific data files,
tie `0x875638` global pool to its initialization,
and prove exact shared CRT RNG state before each
staff name draw. Then build first/surname payloads
from original source bytes, integrate authentic
rows/action buttons and native input callbacks,
test Apply/Cancel, and finish actual playable
SupportStart → TeamSelect return without synthetic
click maps. Preserve already merged PR #648 and
old draft PR #645, currently subsumed only as
bounded native geometry on this new branch.


## Additional source producer evidence: serialized pool records

Further original disassembly identifies how the `0x875638`
fallback name-record pool is populated; the source
file path and startup callsite are still UNKNOWN.

`0x4218C0` invokes `0x421C80` followed by
`0x421CE0` on the same original name-pool object.
In `0x421C80`:

1. Invokes the name-pool owner virtual+0x0C to
   release or reset its existing values.
2. Calls original generic file reader `0x667E90`
   with arguments including **size4, count1**
   to read the 32-bit record count into pool+0x04.
3. Calls owner virtual+0x08 to allocate the
   array using the newly supplied count.
4. Iterates count records at `pool+0x08`
   with exact **0x250/592-byte stride** and
   calls `0x418B90` per record to parse
   further fields and name strings.

`0x421CE0` then iterates the same 0x250
records and calls runtime maintenance/association
routines before staff name selection can use the
grouped lookup through `0x421BA0`.
This establishes that the name-pool record
stream is original serialized data, not a
source-proven collection of arbitrarily sampled
player names.

Critical unknown remains the specific original
filesystem path/record producer and the exact
serial field implementation in `0x418B90`,
plus downstream `0x421CE0` group table
construction and shared CRT RNG ordering.
No code should synthesize a pool before those are
qualified. Continue by following callsites of
`0x4218C0` and the owning native file-handle
open, then parse only the specific authorized
original file with a reproducible byte receipt.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x4218c0 --stop-address=0x4218dd footballmanager.exe
objdump -D -Mintel --start-address=0x421c80 --stop-address=0x421cdb footballmanager.exe
objdump -D -Mintel --start-address=0x421ce0 --stop-address=0x421e01 footballmanager.exe
```


## Recovery552: original name pool source-file identity and byte-level record discovery

**Correction to the earlier UNKNOWN file producer:** original
`0x50D630` has a single direct name-pool reader call at
`0x50D687`, calling `0x4218C0` on the native
`0x875638` player/name pool. At `0x50D63D–0x50D647`
the source opens ASCII filename literal `0x827F48`,
independently read from the SHA-verified original PE as
**`master.dat`**, with access-mode literal `0x81E168`
equal to **`rb`**. Therefore the name source was NOT an
unknown separate hypothetical staff names file: it is the
existing real `FM2001/Master.dat` player pool.

The owner-only extracted original `Master.dat` and
`Core.str` were independently byte-fetched and
SHA-256 validated from private Google Drive, without
committing either original dataset to Git:

| Private original file | Bytes | SHA-256 | Drive source ID |
|---|---:|---|---|
| `FM2001/Master.dat` | 3,391,446 | `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8` | `1M3Ci2RUmkM-lK0_Qonq3fQ7zC08B97OR` |
| `FM2001/Core.str` | 351,695 | `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06` | `1tUf8XOHa5KKE1gluQVO7h79aU30ss2VM` |

The existing `reconstruction/fm2001_data.py` has already
decoded their original saved record format.
Byte-level independent check of the two actual files:

- `Master.dat+0x000000`: `u32 club_count=1246`.
- Clubs occupy 181 serialized bytes apiece,
  starting at file offset 4, finishing at **225,530**.
- `Master.dat+225530`: `u32 player_count=30064`.
  The player record stream begins at **225,534**,
  with exactly **103 serialized bytes** per player.
  Its end is **3,322,126**.
- `Master.dat+3,322,126`: `u32 manager_count=1612`,
  followed by 43-byte manager records ending at
  **3,391,446**, exactly file length. There are
  no unexplained trailing bytes.
- Each player's 103-byte record begins with
  `u16 player_id, first_name_core_index,
  surname_core_index, club_id`.
  Original source `0x418B90` parses player ID
  into native record+0x04, reads a second u16
  and resolves the first-name pointer into
  native+0x08 via `0x64E320`, then a third u16
  resolves the surname into native+0x0C.
  Those are the exact two fields read at
  `0x421C2A` and `0x421C3F` for staff
  first/surname selection.
- Original `Core.str` is an index-bearing CP1252
  NUL string resource with 29,033 string entries
  and 235,555 bytes in its string payload,
  following the existing verified `EAStringTable`
  format.
  The independent first source player (`player_id=0`)
  is **David Seaman** (`Core.str` indices0,1),
  and last record (`player_id=30063`) is
  **Arild Stavrum** (indices6317,27934).
  These are **corpus identity samples**, NOT
  claims that any initially generated support
  staff has either of those names.

**Native lifecycle caveat:** the original
`0x421CE0` post-processing step loops over
all 30,064 player structs and `0x418B90`
calls `0x6596A0` on a conditional record
branch, so original player-load processing
itself may change runtime state beyond mere
sequential IO. Source name selection still
uses TWO potentially distinct original player
indices filtered by the nationality/group
tables via `0x421BA0`; it is not a naive
uniform sample of arbitrary players.
The exact group-table construction,
original startup CRT TLS state and precise
player choices for a fresh support staff remain
**unqualified**. Do not infer first/surname
draws or substitute names just because
`Master.dat` is now identified.

This discovery unblocks original **candidate name
data identity**, but NOT the deterministic
original six fresh staff names, original UI
interaction, or the whole GameState integration.
Use already recovered `FM2001Database.players`
rather than inventing another Master.dat parser,
when the verified runtime RNG/group source can
eventually select a genuine original candidate.
No game assets or player-name datasets were
silently copied into the public repo.

Reproduction using only owner-authorized
original files locally:
```bash
sha256sum Master.dat Core.str footballmanager.exe
objdump -D -Mintel --start-address=0x50d630 --stop-address=0x50d6b6 footballmanager.exe
objdump -D -Mintel --start-address=0x421c80 --stop-address=0x421cdc footballmanager.exe
objdump -D -Mintel --start-address=0x418b90 --stop-address=0x418bee footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421c49 footballmanager.exe
```

**Next source step:** connect `0x421CE0`/group-table
population with parsed original Master/Static
country-nationality ownership, recover the
native shared CRT seed checkpoint at fresh staff
creation and conditional extra draws, then
compose the authentic first/surname strings
into seven-row SupportStart without guesses.
All Gates13–17 and Windows11 hands-on GUI
acceptance remain OPEN.


## Recovery552: Static.dat completes original name-group file provenance

Independent original `footballmanager.exe` static disassembly
at `0x50D410..0x50D492` finds its original
literal `0x827E98 = "static.dat"`, mode `rb`,
passed to `0x66A164` at `0x50D458`.
It then calls `0x4117E0` at `0x50D47D`
to read owner `0x874BD8` (whose +8 is
the actual **`0x874BE0`** 0x6C-byte
runtime country/group array consumed
by original `0x421C00`).
At `0x50D48D` it invokes
`0x64CB40` on owner `0x874BC8`
(whose +8 is **`0x874BD0`**,
the 0x14-byte per-name-group table
read by `0x421BA0`).
This establishes that both original
nationality→group and grouped candidate
table **originate from the original Static.dat
loading path**, while actual source candidate
first/surname texts come from the separate
original Master.dat player pool + Core.str.

Original `0x64CB40` is a generic array
deserializer: it reads u32 count from the stream,
allocates native vector slots through vft+8,
then calls the record's vft+0x0C per element.
The source-specific record deserializers and
any after-read pointer grouping/maintenance
must still be traced, not inferred from
Static.dat offsets alone.

New privately fetched original `FM2001/Static.dat`
is **86,929 bytes**, SHA-256
`e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`,
Drive source ID `1Z1eaNrqC5Nvrx1HN72zIX4Qd-5-T8CJK`.
Byte-verified original `fm2001_data.py`
already has country records at offset 0x4A:
209 serialized countries at 43 bytes each;
the resulting native 0x6C-byte group records
must not be confused with serialized 43-byte
raw country records. No original static bytes
were committed.

### Explicitly source-observed choice projection (no hidden RNG)

One additional bounded component was staged at
`reconstruction/original_supportstart_player_name_source.py`:
when the caller supplies **the two actually observed
original 0x421BA0 source pool positions** and
unchanged source-ordered `FM2001Database.players`
(the already-existing original Master/Core parser),
it returns first name from the first candidate,
surname from the second, joined by exactly
one original ASCII space, and rejects source
first-name sentinel `"-"` so the native
caller must retry its actual original draw.
It validates source index ranges, original
player index identity and CP1252/terminators
without advancing any reconstruction RNG.
Dedicated tests cover distinct name sources,
same name source, unknown/misaligned positions,
missing source data, CP1252, and the sentinel.
**The data-only projector does not select the
player positions** and must not be used to
fake names in the live original SupportStart.
The currently known actual native group
data-file identity narrows that missing
deterministic source producer but does not
qualify its grouping or CRT seed checkpoint.

Reproduction:
```bash
sha256sum Static.dat Master.dat Core.str footballmanager.exe
objdump -D -Mintel --start-address=0x50d410 --stop-address=0x50d4af footballmanager.exe
objdump -D -Mintel --start-address=0x64cb40 --stop-address=0x64cb8f footballmanager.exe
```

**Remaining path:** source-qualify Static.dat
per-record country/group deserializers and
name-group table pointer linkages; reconstruct
name-selection original seed/draw order;
restore six genuine initial staff names and
all seven source rows within original
SupportStart UI, plus native mouse event and
modal return. No Windows 11 original GUI
acceptance; Gates13–17 remain open.
