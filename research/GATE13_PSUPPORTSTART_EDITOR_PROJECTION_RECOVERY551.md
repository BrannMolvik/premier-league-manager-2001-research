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
