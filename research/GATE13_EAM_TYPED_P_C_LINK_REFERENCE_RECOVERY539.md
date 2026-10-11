# Recovery 539 — Native original Inbox player/club typed link target index

## Original executable proof

This is **static PE disassembly**, not executing the original. Reference original `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Direct `objdump -D -Mintel --start-address=0x5CF7B0 --stop-address=0x5CF810 footballmanager.exe` verifies original native `0x5CF7B0` (missed as a function boundary by unbounded `objdump -d`):
- input `dl=[esp+4]`: `'P' 0x50` writes output kind **1**, returns descriptor+0x04;
- `'C' 0x43` writes output kind **0**, reads subtype descriptor+0x00:
   - subtype **1** reads original `0x875628` table element **descriptor+0x04 × 64 + 0x24** (the original club reference);
   - subtype **2 or 17** reads descriptor+0x08;
   - all other subtypes read descriptor+0x04;
- other selector returns **-1** without assigning link kind.

The native parent `PMessageRow::0x471C60` receives the ID2 selector from row+0x490, calls this resolver with `record+0x1C` and a typed-kind out pointer, suppresses returned -1 at `0x471CB3`, then routes kind1 through `0x605DC0` original player details or kind0 through `0x604900` original club details. In the latter, a negative (not -1) returned index selects original global `0x874B94`; positive indexes native `0x874B90` club array. The index alone is not an original player or club identity without the backing native table and date/context.

## Exact bounded port slice

`reconstruction/original_eamail_tagged_link_target.py` now has pure source-specific **raw-index resolution**, without modern object/screens: native signed descriptor kind/ref words, source P/C byte, and optional source-qualified type1 club table lookup. It refuses unknown original type1 table context, NUL/unknown selectors, invalid signed 32-bit **fields actually read by that branch**, or manufactured substitutes; `-1` returns no target, matching original parent. Importantly the source P branch does **not** read descriptor subtype or +8; C type2/17 does **not** read descriptor+4. The function accepts omitted unrelated fields rather than adding a modern fail-closed limitation that would break otherwise valid original source paths. The P/C selector is checked before accessing any descriptor bytes, just as the original `0x5CF7B0` does. It records returned player/club **kind** and raw source index, with `native_detail_gui_verified=False`. No synthetic clickable UI, modal navigation, album/content URL, guessed current club index or fictional message status is introduced.

Tests cover all source branches (P any descriptor type, C 1/2/17/other), exact table stride/offset, -1 sentinel, other signed negative index staying raw, and missing/corrupt native table. Both focused Gate13 and full reconstruction suites are configured to execute this against the exact PR head.

**Still open:** original eCText real pointer hit rectangle/z-order/clip and release event, actual source object resolution with live original database/association table, original player and club detail screens and return actions, row text colored rendering, selected preview and PEAMMessage modal/actions/Escape, true Windows 11 GUI acceptance. This is **SOURCE-VERIFIED partial index contract**, never **VISIBLE-ACCEPTED**. Gates13–17 OPEN.
