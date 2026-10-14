# Gate 13 R1: native 613EE0 multi-node global injury queue pre-callback scan

15 October 2026 KST, recovery 631. This is **source and code checkpoint on the existing unmerged feature branch**, not a playable Inbox, a completed original callback, or a Gate 13 acceptance.

## What changed in the real original source evidence

Using the canonical 4,714,541-byte private `footballmanager.exe`, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, locally disassembled original `613EE0..613F7A` with `objdump -D -Mintel`, not by running the original application. Independently byte-compared all nine decisive original opcode receipts and got **9/9 exact matches**:

- `613EF3 8B 73 04`: obtain original `947AA8+4` head.
- `613F00 39 41 04` / `613F03 7F 24`: signed event+4 due date against passed original `9847FC` day, future skips.
- `613F07 FF 52 10`: invoke the concrete event's virtual +0x10 on reached due branch.
- `613F12 8B 7E 04`: cache wrapper+4 NEXT **before** unlink/callback continuation.
- `613F1C E8 6F 62 ED FF`: removal via original `4EA190`, itself calling `42CBF0` to unlink and optionally the event destructor before native wrapper free.
- `613F29 8B 76 04`: future/no-remove advances original next pointer.
- `613F30 C7 43 0C 00 00 00 00`: clear scan active flag.
- `613F37 8B 43 10`: conditionally dispatch deferred `614080` before final deferred-flag reset and per-user `5CF990` sweep.

Direct PE DWORD read additionally independently confirmed event vtable +0x10: `7BD564 → 5CFA20` (human notice transfer into source `413020`) and `7D7760 → 5D7B40` (dated player cleanup).

**Crucial distinction:** a chain of multiple global pending native objects is not the same as multiple delivered original Inbox rows. The original scanner visits each wrapper in linked-list order, calls its own due handler, and may face callback queue mutation or deferred reentrant `614080` work. A correct reconstruction cannot just treat pending objects as delivered, sort them by date, overwrite equal-day events, or silently omit either distinct event type.

## Source-bounded implementation added to existing branch

- `reconstruction/original_native_613ee0_multi_chain.py`: typed exact full input-chain pre-callback verification for header first/tail, each wrapper +0 event pointer/+4 next/+8 prev, original event type 7BD564 or 7D7760, independent raw date and original signed comparison, first-to-last reachability, alias/cycle/missing-tail negatives and five proved due caller sites. Yields only planned native scan decisions in original FIFO order.
- `reconstruction/test_original_native_613ee0_multi_chain.py`: multi-item human notice/player-expiry interleavings, repeated due dates, signed boundaries, no-early-delivery behavior, wrong-chain/type/owner/caller/reentrancy cases, and optional private original executable opcode checks. Registered for future Gate 13 milestone CI.

A correct preview of which due callback is *eligible to be invoked* is not proof that the callback returned, that the queue stayed unchanged, that 4EA190 actually removed an item, that 614080 finished, that 413020 appended to user+6B4, or that a PEAMail row appeared. New receipt flags are false for those claims.

## Next source-backed implementation seam

Build **portable GameState pending and user-owned delivered injury notice event state** without saving original process pointers. Join the independently verified native original producer `41A5B0→605F90→606540→613EC0`, this full linked pre-callback scanner, actual class-specific `7BD564/7D7760` due callbacks, first-matching registered user `413020` and `5CF990` retention, preserving original raw 32-bit day and actual sender/recipient keys and class details. Test two same-day events, different managers, future/past, optional due recheck, expiry and atomic rollback then modern Save→Load. Allow rendered injury Inbox rows/detail only once the actual portable queue consumer and original player/user formatting/control route are integrated and verified. The full original NEXT→PPreMatch 0–3→PResults→management return, all original countries/leagues, multi-human, and genuine Windows 11 gameplay/install audit remain open.

**Current validation boundary:** nine private PE opcode checks and two vtable DWORDs were executed locally; the new GitHub-hosted Python module/tests have **not yet run** on exact branch head, and no PR or CI was opened merely for this incremental source stage. The direct local Git clone is unavailable (`Could not resolve host: github.com`), but connected GitHub repository read/write and local original PE analysis still work.
