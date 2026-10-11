# Gate 13: native Inbox row first selection versus same-row reactivation (Recovery 534)

## Source and limitations
Direct static x86 disassembly of the privately supplied shipped `footballmanager.exe`, 4,714,541 bytes, independently authenticated earlier in this audit series as SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Native addresses are virtual addresses for that PE, not port addresses. No original executable run, mouse observation, or Windows 11 GUI acceptance occurred. Do not copy proprietary binary/disassembly into the public repository.

## Recovered row input contract

At `0x471B80`, the PMessageRow callback takes an event pointer/word at stack +4. When this argument is nonzero, `0x471B8F -> 0x471BD2` returns without entering the click path. For zero event, global `0x87675C` holds the current selected row pointer.

**First activation of a *different* row** (`0x471B91..0x471BCD`):
1. If a prior row exists, and `0x876754` is nonzero, invoke prior row reset `0x470B90`.
2. Assign `0x87675C = this row` and `0x876754 = 1`.
3. Invoke `0x470B40` on this row, which installs selected sprite address `0x945DF0` on the `row+0x348` bitmap and sets visible state=1 on three row-owned child objects at `+0x37C`, `+0x4AC`, `+0x5DC`.
4. Read message record at `row+0x70`; invoke its virtual method at vft+0x1C; store returned text in global `0x876750`; refresh selected-message preview using `0x471620`.
5. **No call to the detail action `0x471270` on this first-selection branch**. A one-click auto-open would contradict the source.

**Activation of the *already selected* row** (`0x471BDA..0x471C0E`):
1. Pass `row+0x70` record pointer and the value at `(row+0x64)+0x24` to `0x471270` (message dialogue/action chooser).
2. Call `0x472770` on global `0x876758` (PEAMail view); this routine enumerates the currently selected human user's delivered mailbox via `0x4139D0` and `DBRUser+0x6B4`.
3. Clear selected row pointer `0x87675C` and flag `0x876754`, reset preview text global `0x876750` to `0x874BA0`, and invoke preview refresh `0x471620`. A later source call to `0x653350` follows the clear path.

At `0x471270`, the action handler locates record pointer in the source message array `PEAMail+0x68` (count +0x6C); `0x4712FA` **clears status bit 0x2** of `record+0x08` before constructing a popup. It constructs an `0xD08`-byte object, positions a window using bounded coordinates, and opens a modal interaction via `0x5EB540`, `0x532C10`, `0x532650`; the resulting modal selection is dispatched by a jump table `0x4715E8`. This **does not establish** the semantics of all choice codes; do not substitute a modern detail modal or mutate any other flag without tracing those cases.

At `0x470B90` the deselection branch sets the original normal bitmap `0x945E30` and hides three children; `0x470B40` uses selected bitmap `0x945DF0`. These are **distinct originals** from hover/other row art at `0x945DB0` (seen in `0x470BE0`), and exact pixel geometry/resource content must still be verified. Original row text/font/markup painting `0x5D68D0→0x5D7350→0x5D75B0` is not qualified by this particular trace.

## Current port comparison and next source-backed implementation slice

Main `d6f334e01d11e63a25464ec211ffd3b5a04b6162` contains read-only delivered EAM row projection, original normal row art, and real root1→child0x65 normal-host panel. The normal Inbox still **does not implement** selected versus unselected row state, native preview/detail open and modal choices. This is a **confirmed missing normal player GUI route**, not a test-pass claim.

Next work must inspect the original `0x471270` choice-table cases and modal dismissal, then implement only qualified semantics through ordinary `original_game_host` input: first press changes selected sprite/text preview, same-row second press opens genuine original detail/actions, row switch deselects prior row, modal return refreshes delivered mailbox and selection, Escape returns using source-specific event handling. Add negative event, empty view and different-row tests, and verify actual Windows11 mouse and keyboard behavior separately. Preserve unverified message actions as UNKNOWN/fail-closed. Audit native eCText font/colors/markup separately before displaying glyphs. Gate 13 and 14–17 remain OPEN.
