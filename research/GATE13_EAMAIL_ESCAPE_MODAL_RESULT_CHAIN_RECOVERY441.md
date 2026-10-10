# Recovery 441 — original PEAMMessage Escape-to-result16 modal return chain independently closed

_9 October 2026 KST. Strict audit-only original-file fidelity sweep, following Recovery440. Original executable access is private; no binary/disassembly/derived art committed. No implementation, Codex changes, CI, original-process launch, merge, Windows 11 playtest or gate closure._

## Canonical source verification and exact method identities

The original authorized `footballmanager.exe` was rehashed before investigation: **SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Standard x86 disassembly of the hash-gated executable at `0x471270..0x4713D5`, `0x473870`, `0x6539F0`, `0x659650`, `0x532650`, `0x654210` and `0x532B80` closes the native path. The class identity `MyWindow` is independently verified from original MSVC RTTI: **vtable `0x7CB294`**, COL `0x7EC938`, TypeDescriptor **`0x82A190`** `.?AVMyWindow@@`. Its virtual **`+0x00 -> 0x532B80`**, and virtual **`+0x20 -> 0x532650`**. This is *not* `PEAMMessage`'s vtable; that stays `0x7C2714`.

## Direct instruction-level argument/owner chain

1. `PEAMMessage` original keyboard virtual **`+0x34 -> 0x473870`** accepts key code **`0x1B`** and pushes `0x10` into **`0x6539F0`**.
2. `0x6539F0` masks code to 16 bits, reads current detail object's **`+0x64` owner** and calls `0x659650` with `(message=0x400, wParam=0x10, lParam=0)`. `0x659650` loads owner HWND via owner **`+0x04`** and invokes import `PostMessageA` at **`0x7BD2D8`**. Thus Escape posts `WM_USER / 16` to the owner window, not a generic fullscreen command.
3. The detail-launcher **`0x471270`** pushes `PEAMMessage` onto the source stack at `0x47136D -> 0x5EB540`, invokes `0x532C10` for a preliminary message pump, then at **`0x47137F..0x471387`** calls **`MyWindow::0x532650(window=0x877960, detail=PEAMMessage, parameter=0)`**. It stores its return in `EBX` at **`0x47138C`**.
4. **Critical pointer distinction:** `0x532650` pushes `0`, then the detail pointer, then the `MyWindow` pointer into `0x654210`. At `0x654210` the first object argument is the **detail** (`ESI`), and the second is the **MyWindow** (`EDI`). This method stores `MyWindow` into **`PEAMMessage+0x64`**, registers the detail with `0x6542B0`, then obtains **`[EDI]`** and invokes its virtual **`+0x00`**. Because `EDI` is the original **MyWindow** and its final verified vtable is `0x7CB294`, the dynamic call resolves to **`MyWindow::0x532B80`** — not the detail's own `+0` (which is its deleting destructor).
5. **`MyWindow::0x532B80`** drives the native Windows message loop. It reads queued `MSG` values and explicitly branches when **`MSG.message==0x400`** at **`0x532BBF..0x532BC7`**; instead of normal `TranslateMessage/DispatchMessage`, it jumps to exit at `0x532BF9` and **returns `MSG.wParam`** via `[esp+0x18]` at `0x532BF9`. Thus when the pending message is the detail Escape `WM_USER(0x400), wParam=16`, the registered modal call yields **result `16`**.
6. `0x654210` returns that virtual result, `0x532650` forwards it to `0x471270`, and **`0x4713B2..0x4713BE`** dispatches `result-5` through twelve source dword entries at `0x4715E8`. **Result16 -> `0x4713C5` -> `0x5EB920`** with the live detail object and original flags `0x8000, 1`; thereafter common return at `0x4715C9`.

**Classification: CONFIRMED original *instruction-conditional* Escape event16 → MyWindow WM_USER interception → modal result16 → native detail stack removal.** This closes Recovery440's precise sender/receiver/result gap. This is a source-level claim about the valid original detail/parent ownership and a posted message actually delivered to its window, not a claim to have observed the original program interacting on screen or to know the original visual transition duration.

## Related original return state and boundaries

Recovery440 independently proved that before result dispatch, `0x47138E..0x4713AC` tests live `PEAMail` pointer **`0x876758`** and restores/refills its `CMessageList` through virtual `+0xA8` using saved scroll index **`PEAMail+0x127C`**. The complete intended **Escape-from-message-detail return into existing inbox list** is therefore now source-addressable: detail stack entry, original parent binding, source event16, message loop result16, list scroll refresh, stack removal and common return. Unknown original-visible details remain message row focus, selection highlight, animation duration, redraw timing and any separate gameplay side-effects.

**Do not overextend to other controls or screens:** `main` and Codex `reconstruction/original_game_host.py` bind global `<Escape>` to `leave_fullscreen`, but have *no actual live PEAMail/PEAMMessage*. This documents a missing context-specific original input path, **not** proof that their existing, unsupported EAMail screen responds to Escape improperly. The default game-screen Escape semantics are separately unresolved.

## Implementation-owner handoff (no implementation here)

Reproduce original message row acceptance and repeated activation before integrating native `PEAMMessage`. Preserve the original 710×420 detail, current message index/filtered order, original posted-code result dispatch (especially 6/7 previous/next and 16 remove), `CMessageList` scroll restore and source category-dependent actions. Codex should implement context-specific Escape input only after the original view exists; the game's normal/default Escape must not be blindly repurposed, and modern fullscreen toggles must remain compatibility-only without violating original semantics. Obtain real Windows 11 mouse/keyboard/return receipts across more than one club/mailbox.

Next audit item under the **P0 core journey**: original source event producer/hit-test for `PSquadScreen` first+reserve/first-formation/reserve-formation IDs 3/4/5 and original management NEXT/MATCH source action/visibility; compare actual main vs current Codex event wiring. Preserve 'no original-source proof' labels for incomplete control geometry/press timing.

Gate 13 remains OPEN; Gates 14–17 / the complete shipped-scope Windows 11 release are incomplete.
