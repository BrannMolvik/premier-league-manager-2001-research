# Gate 13 R1: portable original injury notice world and Save/Load integration

15 October 2026 KST. Source-qualified **partial implementation milestone** on active unmerged branch `worker/gate13-r1-injury-runtime-bridge-audit-639`, based on main `5c98135a10c8e5628fb0ab230d62bfa36c2d6922`.

## Why it matters

The original player injury sequence has **two distinct** global 947AA8 event types with separate native owners: a 606540 human notice wrapped as 7BD564, and a 60AA20 dated player-expiry event 7D7760. The previously running modern GameState only had a transfer-request global pending queue and transfer-only per-user mailboxes. The original notice could not be retained, reproduced after Save→Load, or delivered without pretending it was a transfer message.

Source evidence: independently byte-verified canonical private `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; source `41A5B0→605F90→606540→613EC0` producer/constructor and `613EE0→7BD564+10=5CFA20→413020` first matching user based on class category1 manager key at original record+14 and source DBRUser manager context+40; 30/31 lookup conditional recheck at due, while type2 skips it. Source `5CF990` uses native date+365 signed wrap and per-user retention, separate from 613EE0. See original producer/route tests, `GATE13_R1_INJURY_LIVE_BRIDGE_AUDIT_RECOVERY639.md`, `GATE13_R1_606540_NOTICE_TITLES_RECOVERY630.md`, and `GATE13_R1_PENDING_MULTINODE_SCANNER_RECOVERY631.md`.

## Staged implementation

- `reconstruction/original_native_613ee0_multi_chain.py`: rejects incomplete/aliased doubly linked native source chains; visits full global 947AA8 source list in original head→tail order, signed due comparisons and exact callback/unlink **eligibility**, explicitly NOT callback execution or final queue mutation.
- `reconstruction/original_606540_portable_notice_world.py`: frozen portable `Original606540PortableWorld` retains stable serials, source player identity, exact original constructor/vtable/kind (2/30/31), immutable global human pending date/creation manager key and separate user-owned projected notice/date/recipient. Source constructor and due stages require original typed receipts. Multi-due batch computes full results before immutable commit, requires every due 7BD564 in source FIFO order, preserves later type 30/31 lookup recheck and first registered user source pointer/key, never broadcasts or promotes unmatched users.
- Fail-closed gap: a **due 7D7760** player cleanup in the same native scan blocks this human-notice-only transaction (no partial notice delivery). Original reentrant callbacks/deferred 614080, native heap/object destructor, original title interpolation, true delivery/user list lifetime, and visible PMessageRow detail remain unimplemented, not guessed.
- `GameState.original_injury_notice_world` is a distinct, empty-by-default port-owned source state. It is **not automatically populated by modern match injuries**, because the currently executing `generate_persistent_match_injury` and source 41A5B0 player+24C/9847FC have not yet been tied under a complete atomic match transaction. It is never conflated with `original_pending_transfer_eam`, `original_delivered_mailboxes`, or normal UI.
- `internal_save.snapshot_game_state` and `restore_game_state` persist this source state in the **modern internal** schema 48 as an additive optional field. Absent historical field restores empty. No native event/heap pointers or original proprietary save bytes are persisted. Strict restore forbids fake GUI read/status, wrong native constructor/vtable/kind, malformed raw native date, duplicate serial and forged value type.

## Staged regression coverage and validation boundary

- New `test_original_native_613ee0_multi_chain.py` checks multiple same-day and future events, mixed human notice vs expiry, signed rollover boundaries, all five original callers, bad links/aliases and nine exact private executable opcode signatures.
- New `test_original_606540_portable_notice_world.py` checks all three native type families, per-user source dynamic owner, no recipient, both 30/31 late lookup fail-closed, two same-day notices, all-due atomicity, first-to-last FIFO, bad source pointers, future dates, invalid saved metadata and 7D7760 requiring separate atomic expiry processing.
- Updated `test_internal_save.py` covers actual modern GameState/controller Save→Load/re-save, historical absent field and forged native kind. New tests are registered in the focused Gate13 workflow.

**Verification:** original private executable + language hashes, vtable slots and native scanner opcode bytes were locally checked; independent source disassembly was performed. The new Python implementation/test files have **not yet been executed on GitHub exact branch HEAD** and cannot be accepted/merged until focused Gate13, broader save/regression suite as warranted and asset policy pass, with code/high-risk review. Direct local Git clone failed because `github.com` DNS was unavailable to the shell; the connected GitHub API remains operational.

## Exact next step, not a release claim

1. Review the candidate portable state and save changes for unexpected constructor/type/due/rollback cases; run exact-head CI once a coherent reviewable PR is opened, not per heartbeat.
2. Source-close original 7D7760 due player cleanup and human 60AA20 mitigation together in an atomic real match producer→saved world path; tie runtime player IDs/manager keys, original 9847FC calendar and existing match RNG to source bytes, ensuring a mixed due batch cannot partially commit.
3. Integrate registered-user notice into the original Inbox row/detail with the exact class-specific title and +1C(arg0) original body interpolation, label actual source-reconstructed delivery vs original native execution. Finish full NEXT→PPreMatch original modes0–3→PResults→management return, all original clubs/leagues/countries and 2–6 human manager career journeys.
4. Only close Gate13 after actual original completeness audit. Gates14–17 and **physical Windows 11 installation and interactive GUI release acceptance remain OPEN**.

No Codex exclusive implementation ownership. No original executable, raw disc or private source bytes committed to Git.

## Recovery635 high-risk fail-closed correction (15 October 2026 KST)

Code review found an omission in the portable all-event source guard: a caller could supply an internally valid but *partial* native global 947AA8 scan (one 7BD564 wrapper), while the saved portable world owned two live pending 7BD564 notices. The previous source-to-batch check only compared the count of due scan nodes to the caller-supplied due receipts, not to the actual number of pending human notices owned by the portable world. That could commit one sibling's user+6B4 notice while silently omitting another. Now require the complete pre-callback scan to contain one source 7BD564 event for each portable pending human notice, counting both future and due events. If any native human wrapper is not represented or the chain is incomplete, fail closed. New regression covers a two-notice world presented with one internally well-formed native node and confirms full two-node delivery remains valid. This count is a necessary safety check, **not** sufficient native identity proof or actual callback/mutation; native event pointers cannot be reconstructed from a portable saved serial alone. High-risk independent review, exact-head CI, main reconciliation, Gate13 player-visible and Win11 audits remain required.
