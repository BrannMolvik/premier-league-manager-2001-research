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
