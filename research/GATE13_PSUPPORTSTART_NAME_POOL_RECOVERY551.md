# Gate 13 Recovery551: original SupportStart staff personal-name source producer

**Status: bounded original-source proof; NOT a restored name generator, live
PSupportStart, shared CRT RNG, or Windows 11 acceptance.**

This source task continues after bundled SupportStart source/data/art PR #648
was opened for exact-head validation. It intentionally uses a **separate
unopened feature branch based on current main** to avoid resynchronizing
PR #648 and restarting costly CI. Source is the owner's private authenticated
`footballmanager.exe` (4,714,541 bytes, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`).
No original program was executed or imported into Git.

## Actual CSupportStaff name owner

1. Native `0x4C9B30` allocates 0x218 bytes and passes
   type, 0, RNG-derived age-like value and source rating into
   CSupportStaff constructor `0x4CA2F0`.
2. `0x4CA2F0` stores the type in `staff+0x04`, age-like
   source at +0x08, installs actual vft `0x7C6834` and
   calls `0x4CA660` at `0x4CA334` with a nationality/
   name-group context sourced via active club pointer+0x14.
3. Source name getter `CSupportStaff vft+0x08 = 0x4CA340`
   returns **`staff+0x184`**, the generated full
   personal-name buffer. This is distinct from the
   staff role text (type getter vft+0x14 and
   `0x4CDCD0` original English locale switch).
4. Native `0x4CA660` loops: calls
   `0x421C00` on source name picker owner `0x875638`
   with the supplied context, receives two name pointers,
   and compares the **first-name string** with literal
   **`"-"`** at original VA `0x8185D0`.
   If equal, retries the whole original draw.
   This sentinel was byte-verified from original PE .data;
   do not replace it with a blank/None/unknown name
   or infer which names the live original chose.
5. For accepted first name, source `0x4CA6C6`
   invokes staff virtual+0x0C = `0x4CA6E0`
   with the first and surname pointers. `0x4CA6E0`
   copies first name into `staff+0x184`,
   appends original literal **space** from `0x81AF38`,
   then appends surname (source code continues
   after `0x4CA734`). The personal name is not
   simply the role label, a static previous manager
   name or the source fallback `John Smith` used
   in a different DBRUser name lifecycle.

## Source nationality/name-pool selection

Native `0x421C00` first indexes a source group record
through `0x874BE0`:

```text
group_record = *(0x874BE0) + context * (27 DWORDs = 108 bytes)
mapped_group_index = group_record[3]  // +0x0C DWORD
if mapped_group_index == 0xFFFFFFFF: mapped_group_index = 26
```

It invokes `0x421BA0` **twice** on
`0x875638`, each with that same mapped
group index. From the first candidate, it
returns `candidate+0x08` to the caller's
first-name slot, and from the *second* candidate
returns `candidate+0x0C` to the caller's
surname slot. That means two candidate draws
per attempted staff name, followed by an
additional pair on every first-name "-"
retry. This source consumption is critical to
shared CRT synchronization for the original
startup staff generator and later Inbox first-click.

Native `0x421BA0` chooses each candidate
using source group table `*(0x874BD0)`
with fixed **20-byte group entries**.
The group entry's offset+0x10 is
the number of candidates:

- If **count > 10**: call `0x64D540(count)`,
  use the returned RNG index into the pointer
  array at group entry +0x0C and obtain one
  candidate pointer.
- If **count <= 10**: call
  `0x64D540(*(0x875638+0x04))`,
  and obtain a candidate at
  `*(0x875638+0x08) + 0x250 * index`
  (the global candidate fallback).
- No source range check/serialization contract
  for an uninitialized group pointer is proved
  by these two routines. Do not invent a group
  size, populate the pool from unrelated fixtures,
  or infer the original RNG seed at this stage.

## Reproducible original evidence

```bash
sha256sum footballmanager.exe
objdump -s -j .rdata --start-address=0x7c6834 --stop-address=0x7c6870 footballmanager.exe
objdump -s --start-address=0x8185d0 --stop-address=0x8185d8 footballmanager.exe
objdump -s --start-address=0x81af38 --stop-address=0x81af40 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9b30 --stop-address=0x4c9c0d footballmanager.exe
objdump -D -Mintel --start-address=0x4ca2f0 --stop-address=0x4ca347 footballmanager.exe
objdump -D -Mintel --start-address=0x4ca660 --stop-address=0x4ca736 footballmanager.exe
objdump -D -Mintel --start-address=0x421ba0 --stop-address=0x421bf1 footballmanager.exe
objdump -D -Mintel --start-address=0x421c00 --stop-address=0x421c49 footballmanager.exe
```

## Exact next work and hard stop

Recover the initializer and original data/persistence for
`0x874BD0`, `0x874BE0`, `0x875638`, and
each 0x250-byte candidate record, identify how
native `0x64D540` shared CRT state is advanced
during the **whole** original startup, and
materialize original names only when exact
nationality-group/name-index provenance and
draw ordering are qualified. Then integrate
the real per-user editor, staff/name Apply/
Cancel, source-native GUI rendering/click
and TeamSelect return. This has not been
observed in a real original process or a
Windows 11 interactive acceptance run.
Gate 13–17 remain OPEN.
