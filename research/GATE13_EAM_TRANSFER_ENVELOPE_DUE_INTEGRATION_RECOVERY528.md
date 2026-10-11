# Recovery528: original delayed transfer EAM envelope dispatch into active management turns

11 October 2026 KST. **Gate 13 remains OPEN**. This checkpoint integrates one independently bounded original inbox event subtype into the existing port. It does **not** implement the complete original Inbox, the remaining original polymorphic pending-event classes, original binary saves, physical Windows11 player input or full original career scope.

## New first-party original-file verification and instruction-level source

The worker fetched the owner's private standalone original `footballmanager.exe` from connected restricted Google Drive (source locator ID `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`) and independently recomputed **4,714,541 bytes; SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` EXACT** in the recovered private Linux analysis container. Static native disassembly used `objdump -d -M intel`; **the original executable was not launched, modified, committed or shared**. This source-read recovery is not a Windows11 GUI test.

Reproduction on the authorized private executable, *outside Git*:

```sh
sha256sum footballmanager.exe
objdump -d -M intel --start-address=0x41b580 --stop-address=0x41b6bc footballmanager.exe
objdump -d -M intel --start-address=0x613ec0 --stop-address=0x613f7d footballmanager.exe
objdump -d -M intel --start-address=0x5cfa20 --stop-address=0x5cfa4f footballmanager.exe
objdump -d -M intel --start-address=0x4ea190 --stop-address=0x4ea1c1 footballmanager.exe
```

Verified exact dependencies, **not inferred from tests**:

1. Native **`0x41B580`** creates a 12-byte event envelope and concrete **`EAMPlayerAskTransferListsub`** record with final vtable **`0x7BDB1C`**. At **`0x41B679–0x41B688`**, `envelope+8=record`, `envelope+4=current native date 0x9847FC + 1`, `envelope vft=0x7BD564` (MPMEAMail); `0x41B68B–0x41B690` ORs status bits **`0x06`** into record+8. Status semantics remain **UNKNOWN**. `0x41B698–0x41B6A6` appends to **global pending `0x947AA8`** via `0x613EC0`. The latter separately allocates a **12-byte list node** before `0x617D70`. Queue node, MPM envelope, and EAM record have **three distinct identities**.
2. **`0x613EE0`**, reached at native NEXT **`0x43215E`** and PResults **`0x4A8070`** with flag **1**, walks queue order; `0x613EFA–0x613F07` compares `envelope+4 <= supplied native date` before event virtual `+0x10`. **`0x613F0A–0x613F1C` unconditionally removes each due event from the pending list for flag=1 after its virtual returns**, irrespective of record readiness outcome, through `0x4EA190`. This is a **one-time due dispatch**, not inbox-opening delivery, not "retry until ready" and not an action request removal.
3. `MPMEAMail::0x5CFA20` reads `envelope+8`, invokes record virtual **`+0x3C`** and, when true, stamps record+4 from the **scheduled envelope date** (not time opened or later processing day). It **zeros envelope+8 at `0x5CFA41`** before passing the record to **`0x413020`** for source manager routing and `DBRUser+0x6B4` append. The previous Recovery527 class-exact original `+0x3C→0x4093E0` returns 1 for **this** subtype only; other classes have different predicates.
4. After processing due envelopes, **`0x613F4C–0x613F75` iterates every registered user** (not just the foreground user) and calls native **`0x5CF990`** on the delivered mailbox for class-specific expiry/destruction. This postpass remains **unimplemented** for this port because date-unit conversion, all message classes and record-specific cleanup cannot yet be asserted complete. Source-proven PlayerAskTransferList retention is inclusive `record_native_day+365`, not a generic global wall-clock expiration.

## Source-bounded port integration

- New `reconstruction/original_eamail_pending.py` owns append-ordered typed `OriginalPendingTransferEnvelope` instances with **stable internal event sequence IDs**, separate from `GameState.player_transfer_requests` (still required for the explicit player action) and `GameState.original_delivered_mailboxes` (the native per-user delivery owner). These IDs are **not alleged original memory pointers**.
- At the existing native player transfer request producer `GameState._retain_player_transfer_request`, enqueue only when the original current-user manager key, actual sender club, record type and exact source next-day date are independently present. Do **not** invent emails from AI-only/context-free existing requests or old saves.
- `OriginalPendingTransferEAMQueue.process_original_due` consumes each qualified due envelope once, calls the already source-qualified subtype readiness and appends to the properly registered recipient's delivered owner only. Due envelopes destined for no registered human user are still consumed, not magically broadcast.
- `GameState.process_original_eam_due_events` stages deep copies of pending queue and delivered owner, committing **both together** only if dispatch succeeds. `HumanGameplayController._finish_shared_primary_day`, the existing quiet NEXT/match-results common completion, runs the typed source event pass. Native original NEXT and PResults both call the same global dispatcher; **other source event families, surrounding event order and final result-progress display remain incomplete**.
- The modern `internal_save` snapshot/restore now preserves the pending-event list, its serial, and its original-record recipient/date metadata **independently** of the delivered mailbox and the existing actionable pending request list. Legacy saves without that field restore an empty source envelope owner instead of fabricating historic Inbox messages.
- Player-linked purge/explicit response clears any undelivered typed pending envelopes without silently erasing already delivered row history. The exact original interactive response modal and cleanup are NOT reconstructed by this change.

## Verification and exclusions

Focused source-derived tests cover future/due distinction, native once-only queue consumption, different registered recipients, no-recipient consumption, strict next-day and recipient preconditions, modern save identity, player-linked purge and refusal atomicity. Relevant tests must be GREEN on the **exact proposed PR head**, and the PR needs a separate audit before merge.

**SOURCE-VERIFIED:** above bounded native producer, envelope, due virtual dispatch/removal and delivered-owner transfer, original executable checksum. **INTEGRATION-VERIFIED:** only after applicable CI tests pass. **OBSERVED-IN-ORIGINAL:** no new running-game observation. **VISIBLE-ACCEPTED:** NO.

**Remaining P0:** original scheduled event family breadth, true mailbox global maintenance, all original 5 filtered/sorted list modes `PEAMail+0x68`, input from both PBg ID1 and PMenu0x65, original font/row/detail/text/status/action/ESC, 2–6 humans, non-PL and secondary careers, full NEXT/PPreMatch all modes/PResults and genuine Windows11 acceptance. Complete original gameplay remains the mission, not this partial queue milestone.
