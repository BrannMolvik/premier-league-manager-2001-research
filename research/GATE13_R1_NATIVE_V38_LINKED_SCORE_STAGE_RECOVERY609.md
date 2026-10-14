# Recovery609: original LeagueMatch 0x513570 linked score stage

Date: 14 October 2026 KST. Base main `5d8bdd6c30cd8b96f73e6679b89692949dbea292` includes independently reviewed, exact-head green Gate13 and asset-policy source PR704. Canonical original `footballmanager.exe` length 4,714,541B, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspected **only via static disassembly**; no binary committed or executed.

## Reached original caller and exact scoring scope

Wrapped LeagueMatch vtable owners `0x7C9D9C`, `0x7C9E80`, `0x7C9EF8`, `0x7C9F70` dispatch v+0x38 to `0x5136C0`. The original `0x5136C0` calls `0x5112A0` *first* and then `0x513570`; the former has unmodeled world effects, so this model never claims it produced a complete original cleanup operation.

Independently statically traced original `0x513570..0x513659`:

- `+D0C` and `+D10` are **DWORD counts**; if both zero, `0x51358B` jumps to `0x5136B6`, skipping both score and optional bit2 later branch. The source has no dependency on the event head in this case.
- If primary count nonzero, the original loads context `+B60` head and scans `event+0x34` links until type `event+0x28==8` (`0x6326B0`) or null. From the qualifying type8 anchor it iterates same-linked list, stops **before processing type7** (`0x632680`) or type9 (`0x6326E0`); otherwise qualifying `0x632940` means signed event type 0..4 and event DWORD +0x24 equals 0 or 3. Increment byte `match+0x58` when event DWORD +4 is zero or byte `+0x59` when nonzero. All increments wrap to uint8. Regardless of whether a type8 anchor is found, the code sign-extends both bytes to **signed 16-bit** and subtracts them from the existing unsigned score WORDs `match+0x3C` and `+0x3E` modulo 65536 (`0x5135F6..0x513604`). Initial negative bytes can increase a score; never assume zero.
- If primary count is **zero**, original scans head until first type9 anchor. With primary count nonzero, secondary instead uses the **same cursor left behind by the primary pass**, never restarts at head. When secondary count nonzero and cursor non-null, a type7 cursor immediately skips the entire secondary loop. Otherwise every event in the rest of the list meeting `0x632940` increments match byte `+0x5A` (event +4 zero) or `+0x5B` (event +4 nonzero), wrapping uint8. The secondary pass does **not** adjust the already-subtracted score WORDs here.
- At `0x513659` source tests match `+0x44` flag bit2. When set, `0x513F00`, `0x513ED0`, optional `+D14` and virtual +0x4C getter equality, then `0x64D540(2)` may further increment `+0x5A/+0x5B`. This conditional branch is **not implemented**. The projection explicitly marks it unresolved when either count nonzero.

## Strict standalone source projection

`reconstruction/original_native_v38_score_stage.py` accepts only actual caller-supplied **original match bytes with native wrapped v38 vtable**, original context through +D10, and a pointer->event map of actual original event 0x38-byte records. A linked pointer that is missing, malformed, cycles or exceeds the explicit traversal bound raises before any result is returned. It produces an immutable *projected* original match buffer and visited ptr/cursor receipt. It never writes to the real reconstructed game world, transfers native completion status, declares 0x5112A0 complete, or silently fabricates pointer identity / original event allocations.

Tests cover zero count early return even if bit2 set; primary type8 anchor, type7/type9 stops, primary-to-secondary cursor carry-over, secondary-only type9 search, signed byte-to-word score math, uint8 wrap, malformed pointers/owner, cyclic list and traversal bound. CI gate13 workflow includes the tests. **Exact-head CI still to run when PR opens; no merge or gate closure yet.**

NEXT: Independent review and exact-head CI, then identify actual original event owner allocation/linked list construction and live reachable results before integrating the per-match score updates. Fully resolve `0x513659` bit2 helper/RNG/world and `0x5112A0` wrapper, native v3C rescheduler `0x511370`, 0/1/2 match mode engines, PResults and management return, and Windows11 graphical acceptance. Gates 13–17 remain OPEN.
