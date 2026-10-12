# Recovery551: source-only seven-row SupportStart Apply/Cancel transaction projection

Source original EXE SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Exact source control ownership and critical missing runtime behavior described in
`GATE13_PSUPPORTSTART_STAR_STRIP_RECOVERY548.md`, especially Recovery551
empty-row disabling. No original executable was launched and no proprietary
bytes have been written to Git.

The existing independent source primitives are now composed into a
source-bounded `OriginalSupportStartEditorProjection`, not yet a live editor:

- `0x4D06B0`: seven rows from actual original selected-user staff pointers;
  missing seventh pointer takes original disabled-parent/fifth-text control
  flags, without reading unqualified stale selected bytes.
- `0x4D0796→0x5D6200`: for actual populated rows, initialize native
  selection bit15 from original selection-record byte.
- `0x5D6270`: only a positively verified upstream accepted native event
  toggles the selection bit. No guessing mouse hits from rectangle bounds.
- `0x4CF6AC` preloads selected user first/surname. Edited fields have
  the source-backed CP1252 maximum-31-byte memory bounds used by
  `OriginalHumanUserName`.
- `0x4D05E0` native event1 exits with result0 and does **not** call
  full original staff/name Apply; the port projection returns original
  user/list identities and pre-edit selected bytes unchanged.
- `0x4D05E0` native event2 invokes full original
  `0x4D0830` staff list + selected record mutation **before**
  committing name fields `DBRUser+0x05/+0x25`; the projection first
  validates both then calls existing verified
  `project_original_supportstart_staff_apply` and returns
  independent new user/list data and original flag bytes.
- `0x4D0830` writes inverse native parent bit15 for all seven row
  records even when the final source staff pointer is NULL;
  source NULL staff branch skips actual staff transfer. The final
  source byte therefore becomes 1 when source-native
  disabled row parent bit15 is clear. This does *not* invent the
  initial uninitialized byte, which remains None prior to Apply.

Do not confuse transaction data projection with original DBRUser
`+0x04` extra GUI byte, multi-human persistence, original resource
renderer, full native event routing, or actual GUI launch: those remain
unqualified. The source projection itself never mutates GameState and is
not evidence of player-visible functionality. The existing
`OriginalSupportStartLinkedLists` is a source-bounded identity/list
projection, not every native global/linked-node/allocator side effect.

Five focused regression methods cover populated/empty original row
flags, Cancel rollback, original Apply flags and name commit, upstream
rejected input and source bounds/invalid event counterexamples.
Integration remains P0: bind source TeamSelect input/manager creation
to an actual original PSupportStart modal; bind original graphic
resources and native event hit/control owners; perform correct save and
multi-human and Win11 GUI acceptance. PR645 stays separate draft,
and PR638 remains shared CRT blocked.

Run after checkout:
```bash
cd reconstruction
python -m unittest test_original_supportstart_stars test_original_supportstart_input test_original_supportstart_editor_projection test_support_staff test_original_human_user_name
```


## Recovery551 original role labels integrated into seven-row source projection

Exact CSupportStaff constructor+type virtual relation now verified:
`0x4CA2FF` stores raw type in `CSupportStaff+0x04`;
native vft `0x7C6834+0x14=0x42CB40`
returns this field, and PSupportStart
`0x4D0725..0x4D072E` invokes `0x4CDCD0`
with the returned ordinal. Original
`English.idx`/`English.str` provide real
six fresh user role names (types1,2,3,4,5,13);
the unpopulated seventh source row still has
**no staff pointer, no role and no invented label**.

`OriginalSupportStartEditorProjection.original_source_role_labels()`
now binds the existing authentic language reader and
`original_supportstart_staff_type_label()` to the actual
seven source staff pointers, with source NULL→None.
The test loads existing `original_assets/source/English.str`
and `English.idx` and checks all six original
source role labels and seventh None.
The underlying staff **personal names** remain
unrecovered: original getter vft `0x7C6834+0x08`
resolves `0x4CA340` and returns
`CSupportStaff+0x184`; constructor
`0x4CA2F0` calls `0x4CA660`,
which gets localized/random candidate name pointers
through `0x421C00` and native name pool
`0x875638`, rejecting a sentinel `0x8185D0`.
Without the exact name pool context and shared original
RNG state, the port cannot fabricate source-real
staff names or complete seven-row rendering.
No GUI, normal path, native hit acceptance or
Windows11 acceptance is claimed.

Native reproduction:
```bash
objdump -s -j .rdata --start-address=0x7c6834 --stop-address=0x7c688c footballmanager.exe
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca347 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca6d0 footballmanager.exe
objdump -D -Mintel --start-address=0x421c00 --stop-address=0x421c49 footballmanager.exe
```
