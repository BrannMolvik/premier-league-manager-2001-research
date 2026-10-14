# Recovery613: source-real original 0x615C50 one-node date-event predicate

**14 October 2026 KST.** Baseline main `c32150f2637119b2f3f615936afdbb6c13c6713e` after reviewed green PR709 (exact-head Gate13 1,586 tests/129 expected skips; asset-policy success). Private original `footballmanager.exe`, 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspected **statically only**; no original execution or original bytes committed. Independent original PE raw section mapping and disassembly confirmed 14/14 signatures from `0x615C50..0x615CF8` and downstream `0x514520`.

## Exact normal caller and native return

`0x5127A0` invokes `0x615D10` in both reached team passes. The ordinary native `0x615D10` caller builds `0x615C50` five arguments in reverse order: **(actual source team/event owner pointer, 0, 1, 0, 0)**. `0x615C50` receives the address of a *single dated-event slot*, reads its first native node from `[slot]`, and returns EAX=0 immediately if that node pointer is null. A nonnull source node enters the following ordered checks; failure moves to its linked `node+0x04` successor. `0x615D10` itself may try other date slots later; one candidate is not the whole calendar lookup.

1. **Virtual event extraction before flags:** calls the native node's vtable +0x18 method `[vtable+0x18]` to obtain original event pointer; null return rejects current node. This method can have world/owner effects. No static node kind or modern fixture object is substituted.
2. **Source flag bit5:** event DWORD+0x44 bit5 must match whether 0x615C50 argument 4 is nonzero. Since normal `0x615D10` passes arg4=0, bit5 set rejects the node.
3. **Team/SideRef test:** arg2=0 skips an optional event+0x4C owner equality. Normal nonzero first argument invokes source `0x4F2CB0` to assemble a SideRef, then calls the event virtual+0x04 with it. An actual reached EAX zero rejects the node. Source virtual effects have not been reproduced, so `original_reached_virtual4_comparison_eax` must be explicitly supplied.
4. **Node state and flags:** node+0x08 nonzero rejects; event+0x44 bit6 set rejects. When bit0 set, the normal caller's final argument zero **rejects** the node (an alternate nonzero caller could return it, but that route is NOT claimed by this component).
5. **Mutating 0x514520:** only on the remaining branch, native invokes `0x514520` on the node, then rechecks node+0x08. Source `0x514520` itself can call event virtual+0x18 and event's embedded SideRef getter methods on +0x14/+0x28. If the reached post-callback node+0x08 stays zero, `0x615C50` returns current native node pointer; otherwise it follows the node+0x04 next link. **No reconstruction may invent 0x514520's mutations**.

## What has been implemented

`reconstruction/original_native_615c50_reached_candidate.py` is an immutable, **one-candidate only** source projection. It accepts only a type-qualified reached original `0x615D10` date-window from PR709 with an in-range, nonnegative, nonnull source slot vector; an actual reached slot-node pointer and original node bytes; actual reached v+0x18 event pointer/record; actual reached event v+0x04 return and distinct post-virtual node snapshot when the source executes those steps; and actual post-`0x514520` node+0x08 value only on its reached branch. Skipped extra values, missing virtual outputs, fake/null owner, unsupported source date windows and malformed records raise before any result. It returns a typed branch classification, not guessed linked-list next pointer (virtual methods may have mutated node+0x04). It never calls source callbacks, changes any original/reconstructed state, or claims native PResults.

Tests cover empty slot, null virtual+0x18, bit5, failed v4, node+0x08, bit6, bit0 with real arg5=0, successful and unsuccessful actual 0x514520 post-state, invalid dates/slot source state, skipped/missing source callbacks and malformed input. The private-executable optional test checks **14 exact original instruction signatures**; the Gate13 source workflow includes this module. These tests are function-scope only; normal Windows game behavior remains unverified.

## Audit status and exact next action

- **Source:** bounded `0x615C50` normal `0x615D10` caller decision tree source-verified by static PE evidence, conditional on genuine native virtual callback returns. **No native game process observed.**
- **Integration:** none of the original node v18/v4, SideRef constructor `0x4F2CB0`, post-callback `0x514520`, full per-day `0x615D10` iteration, world/container mutation, source v3C tail, PResults or complete match modes are integrated. Unknown outcomes fail closed.
- **Visible/player acceptance:** unavailable until a genuine Windows11 UI/gameplay test. Gates13–17 OPEN.

**NEXT:** verify PR exact-head focused Gate13/asset tests and independent patch; merge only if green. Then trace source `0x514520` embedded SideRef v0 and node+0x08 writes, virtual+0x18 and +0x04 owner vtables, and original native `0x615C50` linked date nodes. Integrate the complete date lookup and 0x5127A0 reschedule transaction only with qualified world owner/callback effects. Prioritize normal NEXT→PPreMatch→all original modes→PResults→return, subsequent complete manager/country/2–6-human SaveLoad and actual Windows11 GUI acceptance. No gate closure from source tests.
