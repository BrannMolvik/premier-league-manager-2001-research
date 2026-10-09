# Recovery 439 — PEAMail/CMessageList native row, selection and message-detail audit

_9 October 2026 KST. Strict independent AUDIT ONLY. Resumes Recovery438 main `7f32ea24ad842b9a003b8975ee48b8d06f1bdb30`; latest Codex branch `8702eded049643220bf4b590d8d45c2197cfd42a`. No new UI implementation, assets, saves, merge, CI, original process launch or Windows-11 GUI acceptance._

## Provenance and class/vtable identity — direct original executable recheck

Original authorized `footballmanager.exe` **SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** was hash-verified locally again before disassembling. All virtual-table values below were independently extracted as native little-endian pointers at `.rdata` VAs, corroborated with original RTTI:

| Original concrete class | Vtable | RTTI type descriptor | Relevant virtuals |
| --- | --- | --- | --- |
| `PEAMail` | `0x7C2950` | `0x819540` `.?AVPEAMail@@` | `+0x10 -> 0x4721C0` |
| `CMessageList` | `0x7C2A50` | `0x81C7B8` `.?AVCMessageList@@` | **`+0x9C -> 0x471D20`**, `+0xA8 -> 0x6512A0` |
| `PMessageRow` | **`0x7C266C`** | **`0x81C628` `.?AVPMessageRow@@`** | **`+0x10 -> 0x471B80`**, **`+0x08 -> 0x471FC0`** |

For independent reproduction, `objdump -d -M intel --start-address=0x471B80 --stop-address=0x472010 footballmanager.exe`, plus ranges `0x472680..0x472b92`, `0x474b10..0x474f29`, `0x471270..0x47138e`. The private original executable and disassembly are **not** committed to Git.

## A. The exact native message-row producer

**CONFIRMED: `CMessageList` virtual `+0x9C -> 0x471D20`** receives a source row index argument, adds the list `+0x3C` offset, reads its owner at **`CMessageList+0x24`**, and bounds-checks the resulting index against **`PEAMail+0x6C` message count** at `0x471D3D..0x471D49`. On an in-range index:

1. `0x471D50` allocates **`0x79C` bytes** and calls inherited row construction `0x448310`.
2. `0x471D73..0x471D9F` selects the message pointer from **`PEAMail+0x68` sorted/filtered pointer array** and stores it into **`PMessageRow+0x70`**.
3. `0x471ECC` overwrites its final vtable with **`0x7C266C`**, native RTTI **`PMessageRow`**.
4. Row text binding is source-driven: `0x471ED7` calls the message object's virtual `+0x18` and copies the resulting byte string to row `+0x74`; `0x471F01` resolves the message's `+0x1C` string-like field via `0x5CE6A0` and copies it to row **`+0x174`**; `0x471F31..0x471F52` formats a message `+0x04` dword into row **`+0x274`**, via `0x64CCD0` then `0x471FA0 -> 0x64D150`.
5. Constructor also creates child text/graphic controls at row offsets `+0x348`, `+0x37C`, `+0x4AC`, `+0x5DC`, `+0x70C`, `+0x73C`, and `+0x76C`; specific native fonts/colors, visible sub-rectangles and string semantic labels require further evidence.

This proves the screen uses **actual concrete native PMessageRow controls**, not a generic date-sorted textual list; the output is bound to the selected/sorted `PEAMail+0x68` array from original source producer `0x472680/0x472880`.

## B. Native scrolling/viewport contract

At the end of `PEAMail::0x472880`, the selected array count at `PEAMail+0x6C` is converted to `max(0, count-8)` at **`0x472B4F..0x472B5E`**, stored at **`PEAMail+0x1278`**, and passed to scroll control at `PEAMail+0x1268` via `0x64FF90`. The current viewport position **`PEAMail+0x127C`** is then passed into `CMessageList` virtual **`+0xA8 -> 0x6512A0`** at `0x472B6F..0x472B84`; that generic method writes the list `+0x3C` offset and reuses/discards/rebuilds row children based on the scroll displacement.

**Classification:** source-proven eight-row scrolling *capacity calculation* with real existing row-virtual update path. Do not claim exact visible pixels, row heights or scroll animation time without native list layout/runtime observation.

## C. Distinct first-selection vs reactivation behavior on native rows

`PMessageRow` event virtual **`+0x10 -> 0x471B80`** handles the neutral action only for event argument zero (`0x471B8D..0x471B8F`). In that event:

- If global selected row **`0x87675C`** is *different*, `0x471BA8..0x471BCD` stores the row in `0x87675C`, sets selection-active flag **`0x876754 = 1`**, reads the underlying message virtual **`+0x1C`** via `PMessageRow+0x70`, stores its return in global **`0x876750`**, calls **`0x471620`** to refresh selected-message presentation and invokes additional owner functions `0x470B40`.
- If the **same** row is activated again, `0x471BDA..0x471BE5` invokes **`0x471270`** using the current message pointer and owner control field. That helper locates the message inside `PEAMail+0x68` and constructs a distinct **`0xD08`-byte** popup/detail UI via `0x472CD0` (if allocation succeeds). It then **clears message status bit `0x02` at record `+0x08`** at **`0x4712EF..0x4712FD`** and enters a new panel/modal stack via **`0x5EB540`** at `0x47136D`. Row handler refreshes message counters via **`0x472770`**, clears selected globals `0x87675C/0x876754` and refreshes the inbox owner. The record bit mutation is CONFIRMED; it should **not** be labelled read/unread without original constructor/consumer corroboration.
- **Independent row visual-state callback:** `PMessageRow` virtual **`+0x08 -> 0x471FC0`** tests message `+0x08` bit **`0x01`**. The two branches enable/disable embedded controls at `+0x70C/+0x73C` differently and call `0x471780`. Thus original rows have conditional appearance depending on recorded flags, separate from the currently missing clean-room inbox, and from the selected-filter state.

**Source relationship:** PMessageRow `+0x10` virtual action after original accepted event, global selected-row selection, and subsequent second press are distinct from PEAMail `+0x10` callback `0x4721C0` (filter/header/actions IDs 1..25). Do not merge their event namespaces or fabricate a Tk double-click equivalent without the original event source/timing verification. The row's second activation could mean repeated press or another original gesture; *repeat-event path* is certain, exact physical gesture remains UNKNOWN.

## D. Main vs Codex fidelity classification

Both `main` and Codex branch `codex/gate13-windows-playability-recovery` (head above) still integrate only `0xCE` Squad, `0x25C` League Fixtures and `0x25A` League Tables in `build_management_panel_snapshot`. Neither has a live native `PEAMail`/`CMessageList`/`PMessageRow` panel path with the original linked-list filtering, sorting, scrolling, row selection, second-activation/detail, record-bit mutation and return semantics. The native **EAMail menu ID `0x65`** is static-recognized but its destination remains unusable.

**Status: PARTIAL original-source contract; CONFIRMED missing core-gameplay route in both reconstructions. Severity P0 (inbox functional parity).** The data producer and native list/row structure are now reproducibly pinned, but exact message record type meanings, selection gesture and action labels, fonts, assets, original pixel/viewport geometry, message creation/persistence, multi-club states and Windows GUI input must still be audited. Do not claim original-equivalent inbox complete.

**Codex handoff, when implementation work is authorized for its owner:** First source-trace the user `+0x6B4` concrete message container and record/vtable family, original `PMessageRow` factory child rects/fonts/bitmap controls, `0x471270` popup constructor/details return path, accepted physical pointer event leading to `0x471B80`, and original bit `0x02` mutation consumers. Integrate the original panel/list row source and filter + comparator + bounded eight-row scroll, not a generic date order or speculative native labels. Add source-evidence tests for filtered-row membership/order, scroll boundaries, first selection, repeat-action, bit mutation and return once supported. Revalidate multiple original club/mailbox states (Southport alone insufficient).

No implementation code, Codex branch, original assets, saves, binary dumps, runtime behavior, CI or Windows acceptance build were changed this recovery. Gate 13 remains OPEN; Gates 14–17 and full-scope Windows 11 release remain incomplete.
