# Recovery658: original 409C90 -> 4181B0 native status-world shadow

15 October 2026 KST. Validation Gate 13 OPEN, Gates 14–17 OPEN. Current-main base: `575c6d7a77acf904e75fe1bd483026ea70aae80d`. This milestone continues existing source work rather than repeating the previous recovered disassembly.

## Original provenance and exact bounded original behavior

Original licensed disc `footballmanager.exe`, size **4,714,541 bytes**, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Its source opcodes, owner/caller conditions and early 409C90 / 4181B0 / 418220 / 4EA370 stores were previously privately and independently checked in merged PR768 and related research, with no native original process executed. This checkpoint reuses those receipts rather than claiming a new binary or GUI observation.

Original `409C90` selected-roster loop reaches original `40A18C` -> `41FA50`, and **only on EAX=0** reaches `40A1A8` -> `4181B0`; EAX=1 skips this reset. On reached reset: original `418150` and `418160` clear player DWORD+0x14 bits4/5, `418180` conditionally invokes `418220` if player DWORD+0x174 bit0, then clears bit0; `418170` clears +0x174 bit1. `418220` exchanges the old status-object byte+3 low5 and byte+4 low4 with the **full** saved player bytes+0x152/+0x153: the status setters preserve high status bits; the player's saved bytes receive the prior masked role and position. Finally `4EA370` writes status byte+3 low5 from **status byte+0**, and clears status byte+4 low4, preserving the high bits. The status object is a separate pointer at player DWORD+0x248, **not bytes of the player record**.

Source-only projections and negative cases were merged in `reconstruction/original_native_409c90_assignment_status.py` with the original 41FA50 gate and two alternate +174 paths. Existing `original_native_status_world_state.py` / `GameState.native_status_world` and internal-save schema 48 already persist the independently verified native player fields, status-object+3/+4, source club indices and registered quotas. No new save schema is required.

## Integration under review on this branch

- Add `GameState.apply_verified_native_409c90_preselection_reset`: it requires an independently source-qualified 41FA50-false reset plan, valid existing mapped original player, matching separately pointed-to pre-call status bytes and exact retained source-native status-world prestate. It recomputes the full source reset and rejects a modified/synthetic after-state.
- Stage **all** changes to the native-status-world shadow and validate the candidate, then replace the shadow once; preserve registered-club quotas. Do not write generic `RuntimePlayer` flags, formation, roster, 41EDF0 quota, callback queues, 513010 match, or calendar.
- Tests cover bit0 CLEAR and SET (including preserved high flags), original status-byte masks and full saved-player exchange, unvisited 41FA50 skip, pointer/mapping mismatch, forged poststate, absent source prestate, stale replay, unrelated mutable-world isolation and a complete human-controller save/restore roundtrip using the unchanged schema.

**Evidence classification:** SOURCE-VERIFIED bounded original leaf from earlier canonical opcode receipts; NEW PORT NATIVE-SHADOW INTEGRATION is pending exact-head tests/review and must not be called full source-native roster/GameState execution. Neither original game execution nor true Windows 11 GUI acceptance has been performed. The original player+248 pointer and source status byte0 are supplied in a reached original receipt; they are **not** guessed from the partial save shadow.

## Scope that remains open

Original full `409D79..40A2A4` 11-role selection with `41C7E0` scorer, `41B970` FPU, selected player 4182F0 including 417340/41EDF0 and 409B50 team+1D8/40 writes, post-selection `5111A0`, all original `513010 -> 5DA2F0 -> v38/v3c` score/event saved-world, true mode0/1/2/3 PPreMatch, both event-date registries into PResults and management return, 2–6 humans/all shipped leagues/countries, and physical Windows 11 reference/port interaction and Gate17 release audit.

**Next action:** examine exact-head CI and code diff, merge only if required checks/counterexamples pass; then investigate/integrate the next complete source-qualified original 4182F0 selected-player world effects (particularly reached 417340/41EDF0), before claiming any complete original 409C90/5111A0 lineup.
