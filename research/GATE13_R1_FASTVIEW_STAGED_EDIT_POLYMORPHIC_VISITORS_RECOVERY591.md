# Original FastView staged edit polymorphic visitor map: Recovery591

**Date:** 13 October 2026 KST. **Base:** canonical main 454c64ede1d7e361aaa2d2a386c2d9b130f58f60 (source milestone PR666 merged). **Active gate:** 13 OPEN. Later Gates14–17 OPEN. **Status:** ORIGINAL-STATIC-SOURCE, NO LIVE REPLAY.

## Provenance

Owner-authorized original disc executable privately materialized from connected Drive, size 4,714,541 bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Disassembled on a private scratch runtime using objdump -D -M intel, checked VA mapping and original .rdata bytes. No original process run, no original binary or screenshots committed. This continuation does not claim Windows 11 acceptance.

## All eight original staged-edit record classes

Original .rdata vtables are consecutive in 12-byte increments, but their native +4 forwarding callback addresses differ. Each wrapper passes the record pointer to the active visitor's DISTINCT virtual slot. All eight original vtable pointers, all 24 wrapper-instruction segments, and the two visitor vtable pointers were checked against this exact original file.

| Original record vtable | Record vft+4 | Forwarded visitor virtual offset |
| --- | --- | --- |
| 0x7D7F3C | 0x633450 | +0x20 |
| 0x7D7F48 | 0x633480 | +0x1C |
| 0x7D7F54 | 0x6334B0 | +0x18 |
| 0x7D7F60 | 0x6334E0 | +0x14 |
| 0x7D7F6C | 0x633530 | +0x10 |
| 0x7D7F78 | 0x633580 | +0x0C |
| 0x7D7F84 | 0x6335C0 | +0x08 |
| 0x7D7F90 | 0x633600 | +0x04 |

The final 0x7D7F90 class is the original 0x6335D0 replacement record (record DWORD +4 source player, +8 target player). The remaining seven classes must NOT be called replacement records without source class-specific evidence. The base 0x7D7F30 class is not one of these eight; base virtual +4 is a CRT abort-like path, not a usable visitor variant.

Original 0x633240 counts nodes by instantiating a counter visitor (vtable 0x7D803C, +4=0x634E40) and invoking each native staged-record vft+4. Original 0x6331A0 processes existing records with replay visitor vtable 0x7D8014 (+4=0x634B00), and OTHER slot methods 0x634920/0x634990/0x634AB0. It is therefore incorrect to collapse all native events to one swap, or to call 0x633020 a pure boolean validator. Its nonempty-list path can reconstruct an edit list and write side-buffer values before returning its AL flag.

## Replay visitor structural finding (bounded)

Source 0x6331A0 builds an original visitor 0x6348E0: original slot +4 stores current iteration index, +8/+9 are scratch flags, +0x0C is requested source player, +0x10 requested target player, +0x14 links staged-list owner, +0x18 stores club, and +0x1C stores original 280-byte match-side payload pointer. Original replacement visitor 0x634B00, reached only through record vtable 0x7D7F90, tests its own scratch status and existing node destination. At 0x634B82/0x634B89 it obtains old record target and compares with requested source. A matching case can rebuild another replacement node (0x634BB8) and modify actual source side ordering/DWORDs at 0x634C1D..0x634CF4; at 0x634CF4 it sets visitor +9 to one. Source 0x634DF0 returns visitor +9. This is NOT equivalent to simply vetoing a player edit or pure validation; conditional replay can modify side state. Full record-type interactions and saved/committed side ownership remain unresolved.

## Branch implementation / missing player journey

Read-only source classification in reconstruction/original_fastview_tactics_selection.py: SOURCE_FASTVIEW_STAGED_RECORD_VTABLE_DISPATCH and source_fastview_original_staged_record_visitor_dispatch. Exact original-vtable and original-trampoline regressions in reconstruction/test_original_fastview_tactics_selection.py are opt-in with FM2001_ORIGINAL_EXE; ordinary tests classify every of eight native classes, deny base/nearby/incorrect types. This is NOT a live mode2 modal or mutation integration. No PR/CI on this WIP branch as of this research checkpoint. No original art or binary bytes committed.

**Next:** reverse all non-replacement visitor slots and the +8/+9 counterexamples, trace 0x633020 temporary-list mutation and native side ownership through modal return; then source-complete original mode2 click/input, two-sided writeback, PResults and management return with a normal Windows 11 GUI acceptance run. Gate13–17 remain open. Batch work rather than creating a new PR per static trace.