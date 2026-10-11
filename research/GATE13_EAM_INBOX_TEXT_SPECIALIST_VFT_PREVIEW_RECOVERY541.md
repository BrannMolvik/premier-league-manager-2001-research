# Recovery 541: Original Inbox specialist eCText owner and source preview renderer audit

## Verified source identity and methodology

Original authorization/private Drive executable (from previous Recovery540 verified direct file) is present in a healthy Linux static-analysis environment as `footballmanager.exe` (4,714,541 bytes). `sha256sum` returned **833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3**, identical to canonical original. PE base 0x400000, `.text` RVA 0x1000/raw 0x1000; `.rdata` RVA 0x3BD000/raw 0x3BD000, so original rdata VA 0x7BFAC8 maps to raw offset 0x3BFAC8. This is original **static x86 and raw vtable evidence**, not an original runtime launch or physical Windows11 GUI acceptance.

Reproduce with:
```sh
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x471dd5 --stop-address=0x471e83 footballmanager.exe
objdump -D -Mintel --start-address=0x5d7360 --stop-address=0x5d7440 footballmanager.exe
objdump -D -Mintel --start-address=0x471620 --stop-address=0x471770 footballmanager.exe
objdump -D -Mintel --start-address=0x470b40 --stop-address=0x470be0 footballmanager.exe
objdump -D -Mintel --start-address=0x6570f0 --stop-address=0x65726d footballmanager.exe
```
Raw pointer table: read 32-bit little-endian DWORDs at file offset `0x3BFAC8`, not at an inferred generic base-type table.

## Crucial constructor-to-specialized-vtable correction

The three **actual PMessageRow Inbox text controls** are placed at row+0x37C (ID2), row+0x4AC (ID3), row+0x5DC (ID0). The original `0x471DD5..0x471E7F` constructor runs base `0x64F300` and auxiliary `0x44B550`, then explicitly writes **specialist eCText vtable `0x7BFAC8`** into *each* child at `0x471E09`, `0x471E43`, `0x471E7D`. This specializes/replaces the generic eCText vtable `0x7BE340` used in earlier general tracing; do **not** assume the generic table is the final virtual call destination for those row children.

Validated native **specialist** vtable slots:
- `+0x08 → 0x64F3C0`: binds child ID+0x20 and parent+0x24, as previously traced.
- `+0x14 → 0x64F430`: selected-state mask **0x4** setter/clearer (shared inherited implementation, see prior recovery).
- `+0x64 → 0x5D7360`: actual specialized text-render dispatch; pushes six arguments to `0x5D75B0` including explicit zero-valued draw/walk mode parameters.
- `+0x6C → 0x5D7380`: first qualified text point event, parent +0x10.
- `+0x78 → 0x5D73E0`: second qualified text point event, parent +0x20.
- `+0x98 → 0x650650` and `+0x9C → 0x6506A0`: inherited cursor/text buffer editing. The native text walker calls these indirectly for caret and T-markup parsing; their precise state-sensitive effect **must not** be replaced by naive literal tag removal.

The old generic vtable still provides useful inherited slot evidence, but original Inbox's paint and event dispatch are **specialized**. This independently connects the original constructor to the correct paint/events, resolving an incomplete owner-vtable link in the prior source audit. Prior assertions that the generic table alone specified Inbox paint/event owner are incomplete and should not be used for action geometry.

## Native paint and glyph clip, bounded

The real `+0x64` function `0x5D7360` dispatches `0x5D75B0`; its text-loop calls `0x5D7500`, which advances the font pen using original glyph metrics, kerning and, for non-space when drawing enabled, `0x6570F0`. The original `0x6570F0` rejects a missing destination clip pointer at `0x6571C5..0x6571CB`, performs rectangle rejection comparisons to four clip edges at `0x6571D1..0x6571EE`, intersects the glyph rectangle at `0x659130` and finally dispatches `0x658BC0` versus `0x6556C0` by graphics mode. This proves the original **per-glyph clip gate**, not final screen-space coordinates or exact RGB/alpha. In `0x5D75B0`, text pen starts from the caller-provided transform and `eCText+0x08/+0x0C`, with additional font line-height/word wrap `0x5D78F1..0x5D794C`; don't render masked glyphs at guessed baseline or accept entire row as a tagged text link.

The selection mask 0x4 toggled by `0x470B40/0x470B90` on all three text children is separate from disabled gates 0x10/0x20 previously proved. Source does not yet prove that selected-state mask changes pixel colors; direct visual parity/GUI absent.

## Native selected Inbox preview is NOT just row highlight

Original first neutral row selection `0x471B80` sets selected pointer, draws original row highlight, gets the record's virtual +0x1C preview string into global `0x876750`, then calls `0x471620`. The latter checks the live `PEAMail` pointer at `0x876758` and whether `panel+0x74`/the current global preview string are present/nonempty:
- nonempty: `0x471647` sets native `panel+0xFD0 = 0x945B70` (preview enabled bitmap), invalidates `panel+0xFA4`, attaches exact source preview pointer `0x876750` to eCText `panel+0xFD8` via `0x5D7350`; native `0x5D6A70` estimates text row count with original 16px Zurich font, initializes `panel+0x1404=0` and `panel+0x1400=max(0,lines-8)` when lines>9, then invalidates preview text.
- null/empty: `0x4716F2` sets `panel+0xFD0 = 0x945B30`, invalidates preview, attaches original default pointer `0x874BA0`, zeroes both `panel+0x1404` and `panel+0x1400`, and invalidates preview.
- same selected row activated: native `0x471270` popup result flows through `0x472770`, resets selected state/global preview pointer to `0x874BA0`, and calls `0x471620` again.

Both source original `FM2001_Art/Generic/EAMail/preview_panel.444` and `preview_panel_disabled.444` are already hash-authenticated in `reconstruction/original_eamail_control_art.py`, 532×187 each. **Caveat:** although the native pointers `0x945B70/0x945B30` are proved via the original update branch, this analysis has not yet checked which exact bitmap each pointer owns, or their source screen positioning, so do not map them by filename from visual plausibility. The enabled preview is not merely a color toggle on the row.

## Current port audit and next action

`OriginalGameTkHost._draw_eamail_rows` currently draws only original normal/selected row background. `_press_original_eamail_row` on neutral first-click selects but explicitly states preview unresolved. **Confirmed incomplete source behavior**: original first-click also updates native preview text/image and scroll; the port does not. Do not paper over this by painting guessed color or inventing same-row dialog. The correct next highest-impact source implementation is the **authentic preview producer/owner mapping and original panel geometry**, followed by on-screen exact visible rows, preview, PEAMMessage action/ESC/return, then R1 NEXT modes and all original leagues/multi-human.

**Evidence layers:** Original static source proof YES (bounded constructor, vft, per-glyph clip, first-selection preview). Reconstruction integration for those newly traced paint/preview details NO. Original running process NO. Real Windows11 GUI input/visual acceptance NO. Gate13–17 remain OPEN.

**Exact next commands:** Original `objdump -D -Mintel --start-address=0x46f250 --stop-address=0x46f770 footballmanager.exe` for `PEAMail` controls; source pointer search and initializer verification for `0x945B30`/`0x945B70` and 532×187 assets; inspect `0x471270`/PEAMMessage return only when source prerequisites known. Implement partial authentic preview output (first-click selected real delivered user, original bitmap and text where colors/layout proved); meaningful exact-head CI before merge. No original EXE execution without renewed approval.

## Follow-up: exact original preview bitmap sources, dimensions and panel location (Recovery541 source closeout)

Additional read of the **same canonical SHA-authenticated original PE** completes the previously unresolved bitmap-pointer association and geometry, without launching or presenting the original game:

| Original native wrapper | Actual loader and source literal | Original EA444 file | Dimensions | Native constructor placement |
| --- | --- | --- | --- | --- |
| `0x945B70` selected text present | loader `0x5F5C40`, `0x836220` -> `0x64D750` / `0x64E500` | `FM2001_Art/Generic/EAMail/preview_panel.444` | `0x214 × 0xBB` = **532×187** | `0x46F576..0x46F589`: panel-local **(246,195)** |
| `0x945B30` empty/default | loader `0x5F5CE0`, `0x83624C` -> `0x64D750` / `0x64E500` | `FM2001_Art/Generic/EAMail/preview_panel_disabled.444` | `0x214 × 0xBB` = **532×187** | same `panel+0xFA4` control; pointer swap at `0x4716F2` |

The original literal bytes at mapped PE file offsets `0x436220` and `0x43624C` read exactly `fm2001_art\\generic\\eamail\\preview_panel.444` and `fm2001_art\\generic\\eamail\\preview_panel_disabled.444`. These exact two source files already have complete authenticated sizes/SHA-256 in `reconstruction/original_eamail_control_art.py` and were previously imported unchanged. `0x651BA0` consumes source wrapper+image dimensions and the two native x/y arguments; in `PEAMail` it receives x=246,y=195, **not** guessed x from a bitmap screenshot. With independently established native `PEAMail` panel global offset (0,148), preview panel graphical destination starts at **screen (246,343)**. Exact original native text child `panel+0xFD8` is initialized at `0x46F591..0x46F5D4` with ID `0x12`, local rect (252,201,520,175), thus screen rect **(252,349,520,175)**. Text lies 6px inside the bitmap on both top/left; this is a reproducible parent-local relation, not merely a plausible visual.

**Source content limitation remains important.** Original `0x471B80` first-click asks the record virtual+0x1C for body with argument zero. Initial EAMPlayerAskTransferListsub class vft+0x1C is `0x56FBA0`, whose argument-zero native branch `0x56FD65` calls current-user `0x4139D0`, dynamic formatter `0x612FD0`, and `0x659810`, using original template global `0x8797A0`. Its actual finished text, manager/player fields and side effects are **not yet faithfully projected from live port game state**. Do not show the enabled panel solely because a row is selected or invent a static body; original `0x471620` additionally checks whether the text pointer exists and the first byte is nonempty. The original initial constructor passes enabled artwork to `0x651BA0`, but this is *not* proof that it remains enabled after original panel initialization and `0x471620` refresh.

**Next exact feature work:** recover original `0x8797A0` EAM transfer body string ID/formatter and native `0x56FD65..0x56FE4E` record/player/user fields, build a source-qualified delivered selected-user preview string and retain its disabled-vs-enabled state under native `0x471620` semantics. Only then integrate the exact original bitmap at (246,343), body eCText at (252,349) with separately traced original font/color/clip and selected-row input/status. This is meaningful source progress, but **no new UI implementation or visible acceptance** and **Gate13–17 still OPEN**.
