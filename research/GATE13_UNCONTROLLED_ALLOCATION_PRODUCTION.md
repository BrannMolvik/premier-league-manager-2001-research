# Gate13 uncontrolled allocation-byte production

5 October 2026 KST. Canonical executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Native lifecycle, not a zero initializer

The approved decisive run stopped before selected DBRClub5 `5DA538`, with
1,156 gap-free dual-context all-user-thread watch checks and no capacity write.
Observed allocation `0/0` survived construction/import/that read. This proves
only those allocation bytes for that lifecycle, not universal zero initialization.
Detailed receipt/adjudication hashes are in `GATE13_NATIVE_CAPACITY_WATCH.md`.

Following that result, exact CRT owner tracing closes the mechanism:

- `66AB1E` pushes 1; `66AB20` calls `66E746`.
- `66E748..66E75F` creates the CRT heap with `HeapCreate(0,4096,0)` and
  retains it at `A8DAE0`. The caller argument makes the `sete` flag result zero.
- Large-array fallback `669CDE..669CF6` rounds the nonzero request up to 16
  bytes, then calls `HeapAlloc(heap,0,size)`; `7BD168` is that exact import.
- `40BBE0` supplies the array's four-byte cookie and 2A8 object stride.
  Constructor/import do not write `+13C/+140`; the controlled-user stadium
  writer is a separate lifecycle and is not substituted.
- Import `403660` derives `+134/+138` by truncating source `+1C` times
  .75/.25. Native `5DA538..5DA5CF`, then cell bodies at `5DA979`, `5DAC05`,
  `5DAE80`, `5DB101` establish their actual order: **home seating, visiting
  seating, home terrace (+13C), visiting terrace (+140)**. Historical watcher
  JSON's `visiting_capacity_u32` key is a legacy name, not semantic proof.
- The two allocation dwords are unsigned and clamp to zero only above 200000.
  Each known zero-capacity cell skips its entire body, including RNG, at
  `5DA981/5DAC14/5DAE92/5DB110`. Earlier unconditional four-draw prose was
  incomplete for this now-reached boundary.
- The uncontrolled host uses original reference prices and no controlled-home
  facility factor. An away human's stadium is not a replacement host producer.

Private heap-owner evidence SHA-256:
`5d68f6753de51ea692b4e1bba4c87837523ba73bef4ad3215ec884bea8cc3c8d`;
caller/import-name evidence SHA-256:
`46ad5606fe5e5dba796e3e1413ac69498f3907a305d06144f167ba357c9c81d3`.
Raw disassembly, executable, memory receipts and saves remain outside Git.

## Small faithful Windows adaptation

`native_club_capacity_state.py` retains explicit unsigned allocation bytes and
their producer/provenance. The canonical Windows database factory performs the
same source-qualified large-array Win32 allocation operations and reads the
actual two dwords for each object before any reconstructed producer uses them.
It neither requests `HEAP_ZERO_MEMORY` nor supplies a zero fallback. Tests
exercise nonzero bytes, large unsigned clamp, allocation failure and cleanup.

This port-owned private heap is a **compatibility allocation boundary**, not
an emulator of the original process's earlier allocation history or an assertion
that every original club had zero terrace bytes. Its actual bytes are retained,
not replayed from the original run. Only these two fields are consumed; no other
uninitialized simulation fields are promoted. Non-Windows/unmaterialized source
inputs remain fail-closed. Controlled-club setup discards this fresh-uncontrolled
lifecycle; annual invalidation likewise cannot silently retain stale evidence.

Internal schema **44** persists both raw dwords, their evidence identity and
producer kind, alongside existing complete report/owner/link state. Neither
receipt import nor allocation creates a report or fixture link. The existing
strict assembler remains the sole publication boundary.

## Genuine calculated-away executable milestone

Canonical data, executable coefficient matrices and both live RNG streams:
fixture2, Coventry City home / human Middlesbrough away, 26 August 2000.
Ordinary calculation produces the complete report, disk schema44 save and a
fresh-process reload; real Windows/Tk `<Button-3>` opens the identical saved
PMatchInfo owner/context with original summary, score/header and nested pitch.
No report, scalar, link or score-derived context was injected.

- Explicit original-lifecycle input proof SHA-256:
  `2e79ec2d7b3ad3ebeca5b5deee6fef4b36a33fb405da37afd92b5e1c5d241e72`.
- Independent **automatic Win32 allocation** proof SHA-256:
  `20c3ab1422244a312d64db53da55cb1f86b58955ab03c7ea65c7580bb34ae9d5`.
- Automatic disk save SHA-256:
  `eebaf8898e9b9b2a5c3ec73fc090e6e1424301f79ffa90fee51be1fb184b0fad`.

Both proofs explicitly disclose that this target lies outside the initial
12-column window and needed the existing source-accepted paging seam. The
ordinary page-button pointer/render/state path is **not** thereby proven.
It is the next real normal-navigation gap; Gate13 stays open.

Focused capacity/gate/save integration: **71 tests passed**; combined probe/
display/integration checks: **134 passed**. Full current-code regression:
**2,267 tests / 23 expected skips** after main reconciliation (2,248 before).
Fresh Windows 11/Tk schema-8 passes,
receipt SHA-256
`131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aae2e8cc9`.
Neither regression nor that audit closes the ordinary paging/timing gap.
