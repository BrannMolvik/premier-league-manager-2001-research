# Recovery613 — original 0x514520 node activation, embedded SideRef getter order

**14 October 2026 KST.** Baseline main `8a8d482361845db01c0f8508db06e0a8da93c64a` after exact-head green PR710 (1,596 Gate13 tests/130 expected skips and asset policy success). Private canonical `footballmanager.exe` 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspected **only statically**, not launched or added to Git. Independently checked 10/10 original PE signature bytes for 0x514520..0x514563.

## Actual original entry, lifecycle and effect boundary

The source-native `0x615C50` event candidate filter invokes `0x514520` when a date slot node passed its prior flag/virtual tests and node+8 was zero. Native `0x514520`:
- `0x514524`: immediately returns when node DWORD+0x08 is already nonzero. It has not dereferenced its native virtual+0x18 event owner.
- `0x51452B`: otherwise invokes node vtable+0x18 to get original event; if null, returns.
- `0x514536` through `0x514548`: checks original event DWORD+0x44 flags bit5 THEN bit6. Either set returns without invoking the event's embedded SideRef getters.
- `0x51454A..0x514550`: invokes the source event **embedded SideRef at event+0x14 virtual+0x00**, not the generic match object. This getter may resolve a club and mutate cache, native node+8 and wider original game state.
- `0x514552..0x514557`: rechecks node DWORD+0x08 **AFTER first embedded SideRef getter**. Nonzero skips the other SideRef getter.
- `0x514559..0x51455F`: only when node+8 was still zero, invokes the event's **second embedded SideRef at +0x28 virtual+0x00**. `0x514561` then returns WITHOUT another local node+8 check. The caller `0x615C50` rechecks node+8 afterward and decides whether to return this native event node.

These SideRef virtual getters can have source world/cached pointer side effects. The existing authenticated original `0x510320` embedded SideRef v0 is one such mutating owner, but do not presume every input record has that same vtable, or that a source result equals symbolic modern ClubRef identity. Other originally dispatched native class owners need separate qualification.

## Staged source-only model (NOT merged/verified)

`reconstruction/original_native_514520_slot_activation.py` accepts actual original node record/vtable and its entry node+8, actual reached node virtual+0x18 EAX and event record when called, and the **actual node+8 after first SideRef getter** if that first getter is reached. It returns a pure source control-flow receipt showing whether event v18, first embedded v0 and second embedded v0 were called; it does **not** synthesize getter effects, invoke native functions, or mark the calendar node/event/fixture processed. Missing, skipped, contradictory, non-uint32 or malformed source inputs fail closed.

`test_original_native_514520_slot_activation.py` stages negative tests for all early guards, first getter mutating node state vs second invocation, flags, missing source state/vtables and a read-only composition with PR710's `0x615C50` received node+8 poststate. Optional checksum-gated private PE checks verify ten original opcode signatures. `.github/workflows/gate13-tests.yml` lists the new tests. **No PR yet; no exact-head CI, no full-suite/Windows GUI test or merge.** This feature-branch snapshot is recoverable from GitHub without wasting another CI run on a partial milestone.

**Next exact action:** independent source/patch inspection, test this module and the nested integration, then source-prove original embedded SideRef virtual+0x00 ownership, actual native node+8 writes and source return effects, grouping related work before opening a cohesive Gate13 PR. Restore real `0x615D10` and `0x5127A0` two-calendar mutation with valid event objects, complete v3C and original NEXT→PPreMatch→four modes→PResults→management return, all original playable leagues and 2–6 human saves, and verify on actual Windows 11 graphical gameplay. Gates 13–17 remain OPEN.
