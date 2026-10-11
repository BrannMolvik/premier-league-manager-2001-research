# Recovery 540 — Original eCText two-phase event gates and character-advance link hits

## Exact source identity and bounded method

Original private extracted disc-root `footballmanager.exe` (4,714,541 bytes) fetched independently from the owner's private Drive direct file ID `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`. Local `sha256sum` returned `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, matching the canonical authorized original. PE i386 `.text` spans VA 0x401000..0x7B86BD. This is ORIGINAL STATIC DISASSEMBLY via `objdump -D -Mintel`, not an authorized original runtime launch, pixel playback, or Windows 11 test.

Reproduce on the original file:
```sh
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x64f7a0 --stop-address=0x64fa20 footballmanager.exe
objdump -D -Mintel --start-address=0x5d7380 --stop-address=0x5d7440 footballmanager.exe
objdump -D -Mintel --start-address=0x5d75b0 --stop-address=0x5d7a29 footballmanager.exe
```

## New source-verified constraints on original link interactions

1. **First eCText route has its own input gate.** Original `0x64F7A0` tests native control `[this+0x18]` **bit 1 set** at `0x64F7AA..0x64F7AF`, then **bit 4 clear** at `0x64F7B5..0x64F7BA`. With owner callback/context enabled, it consults parent vft **+0x0C** at `0x64F7D3..0x64F7DF` before control vft +0x1C. Original `0x5D7380` calls this gate before invoking the text-coordinate walker and can invoke parent +0x10 = `PMessageRow::0x471B80` only after selector, row child ID, callback flag and owner are accepted. That child-forwarding route supplies a nonneutral pointer, not native neutral row-selection.

2. **Second eCText route is NOT the same gate.** Original `0x64F960` checks **bit 1 set** at `0x64F96A..0x64F96F` and **bit 5 clear** at `0x64F975..0x64F97A`; when parent veto is enabled it instead consults parent vft **+0x1C** at `0x64F993..0x64F99F`. It then invokes control vft +0x20. Only then can `0x5D73E0` return the native selector and forward to parent vft +0x20 = `PMessageRow::0x471C60`, which resolves ID2 P/C typed link targets (original `0x5CF7B0`; merged PR633). Equating the two routes, checking the same disabled bit on both, or using a naked template P/C tag to dispatch a club/player detail would be incorrect.

3. **Text coordinate walker checks an individual character-advance interval, not just tag presence.** In original `0x5D75B0`, `0x5D794D..0x5D7993` records the pre-character pen x and passes character+previous character and current source font to `0x5D7500`; this updates the post-character pen using native glyph advance and kerning. When an actual point is provided, `0x5D7997..0x5D79D0` requires **x ≥ previous pen x, x < new pen x, y ≥ current line y, y < current line y + active native font height** before emitting the then-current active selector at `0x5D79F2`. The native `<T+P>` / `<T+C>` branch `0x5D7855..0x5D78D0` stores active ASCII selector `P` or `C`; `<T->` resets it to NUL. A visual fragment width or full row rectangle cannot be blindly equated with the final hit interval.

4. The native T branch itself **does not change the initial 0x9269F0 font object or directly assign a pixel RGB color**. This is NOT proof that the final renderer has no conditional color, cursor, caret or compositing effects; other parser operations, glyph routines, owner control states and display palette are not yet traced through to the final framebuffer. Accordingly the existing native alpha masks must NOT be painted in an invented color/baseline merely from source markup.

## Challenged boundaries and existing-port implications

The modern `original_game_host.py::_press_original_eamail_row` currently dispatches only the separately proven neutral row click over source native decorative row bounds. It does not implement the eCText secondary callback or draw the dynamic text. It is **PARTIAL**, not proof that all P/C label pixels should select instead of navigate: original source demands separate hit/event gates and original typed association before detail navigation. Do not silently turn every row click into a P/C detail click, or mark a missing popup as completed. The owner-local coordinate transform, bitmap/text z-order, clip, enabled-state producers, actual event sequencing, detail display/back stack/ESC and final font color remain unaccepted. No new behavioral code or tests are claimed in this source-only checkpoint.

## Verified integration checkpoint and next work

PR633 exact head `e0b0091dc206a24c658dca307b74e09c4fff409f` passed Gate13 run 38178776486, full reconstruction 38178776484 and asset 38178776496; zero unresolved reviews. Squash merged on main as `05fd7961e8a6c4d5a51cc38123eb0c51ce7aa8e7`. This proves the bounded typed raw reference contract on that commit, **not** original link GUI, painted Inbox, physical input or Windows11 acceptance.

**NEXT P0:** trace the native Inbox eCText draw caller/clip/palette/line advance from 0x5D7360 through 0x5D75B0, 0x5D7500, 0x6570F0 and 0x6503F0, then parent input veto/child pixel transform and original 0x605DC0/0x604900 detail return; implement only when source qualified, with actual visible row text/preview/action/ESC tests. Then complete R1 NEXT/PPreMatch all modes/PResults, Squad/Save/Load and every shipped nation/league and 2–6 human career; Gates13–17 and genuine Win11 GUI remain open.
