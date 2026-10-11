# Recovery537: Native eCText rendering, distinct control-state bits, glyph pipeline audit

## Original-file identity, scope, and reproduction

Authorized reference `footballmanager.exe`, 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, static original x86 disassembly only (no execution). Reproduce `objdump -d -Mintel` on original PE, inspect `0x46E680..0x46E7C0`, `0x5D68D0..0x5D69CF`, `0x5D7350..0x5D75B0`, `0x5D75B0..0x5D7A29`, `0x650650/0x6506A0`, `0x64F5A0/0x64F5B0`, `0x6570F0..0x65726D`, and exact `.rdata` vftable `0x7BE340`. This is static/source provenance only, not original GUI observation.

## Independently checked original vtable and separate bit functions

Map PE `.rdata` at VA `0x7BE340` (file offset `0x3BE340`):

| eCText vtable slot | Raw native function | Proven bounded effect |
| --- | --- | --- |
| +0x14 | `0x64F430` | original row selection callback changes object+0x18 bit mask `0x4` through shared control-state setter/clearer |
| +0x4C | `0x64F5A0` | **reads object+0x18 bit `0x80`** using `shr 7; and 1`, not bit `0x4` |
| +0x50 | `0x64F5D0` | delegates a separate callback to the control's +0x54 vcall, not automatic glyph draw |
| +0x98 | `0x650650` | mutates text buffer at object+0x2C and cursor object+0x34, shifts string, decrements cursor and invalidates |
| +0x9C | `0x6506A0` | another text editing routine, shifts subsequent characters from cursor and invalidates |

Native `0x64F5B0` separately reads **object+0x18 bit `0x100`** using `shr 8; and 1`. Native `0x5D7440` calls bit7 predicate `0x64F5A0`, then calls `0x5D75B0` with an owner-local rect, and conditionally dispatches control virtual +0xA0. `0x5D7490` analogously calls bit8 predicate `0x64F5B0` before `0x5D75B0` and virtual +0xA4. **Do NOT equate bit4 changes with original text hiding/showing**, and do NOT classify bit7/bit8 branches as the primary pixel draw gate without original caller/producer proof; they mediate additional eCText callback behavior.

## Exact original text and font layout bounds

`PMessageRow::0x46E680` initializes 3 eCText controls through `0x5D68D0`: row-local ID2 (38,0,215,16), ID3 (256,0,215,16), ID0 (474,0,71,16); eight source 532×18 row graphic slots x233 y178+20i. ID0's control extends beyond the 532px decorative row bitmap (x707..778 vs row bitmap x233..765), but remains inside parent CMessageList x233..778, consistent with owner geometry, **not** proof of clipping error. `0x5D68D0` writes object+0x120 = `0xFFFF` at `0x5D696F`, also packs color-shaped fields +0x128/+0x12C from global display bit shifts: these raw fields alone do not prove final on-screen color. `0x5D75B0` initializes font object `0x9269F0` at `0x5D75C6`, independently verified `Fonts/Zurich_BdXCn_BT_16pixel.fnt`. Exact source font advance measurement from original font glyph widths+pair adjustment: ID3 `Transfer List`=**69px** inside 215px, ID0 `1/Aug/2000`=**58px** inside 71px. Original x and y baselines/terminal clip and exact T+P/T+C color state still unproven.

## Real glyph downstream rendering and incompleteness

Native `0x5D79xx` calls `0x5D7500` with current char, previous char, font pointer and owner-local state. `0x5D7500` obtains source glyph index via `0x6570A0` and (non-space + enabled draw branch) `0x6570F0`; native `0x6570F0` obtains original atlas glyph bbox and checks the destination clip before passing to `0x659130` and raster/blend functions `0x658BC0/0x6556C0` depending on drawing mode. This is **independent source proof that original layout/color/clip involves more than a trivial uncolored glyph mask**; don't hardcode white/left-top or infer original markup parser output from the saved source template. Source-derived glyph alpha modules in merged PR629/630 intentionally **do not paint** until these actual caller args/clip/color and cursor mutations are verified.

## Required next complete user workflow

Trace native `0x5D75B0` original param stack from ordinary Inbox row child ID2/ID3/ID0 through `0x5D7500/0x6570F0`, determine final color including P and C selector, text metrics/alignment/caret/visible branches and selected-row behavior, then wire source-exact native text color+raster to `OriginalGameTkHost._draw_eamail_rows` and verify actual first-click/second-click/empty/multirow. Preserve native mail delivery ownership, no fake read status. Next preview, PEAMMessage modal return choices, Escape, PBg back3 four original visual states, scroll/filter, complete gameplay and genuine Windows11 GUI audit. All Gates13–17 **OPEN**.
