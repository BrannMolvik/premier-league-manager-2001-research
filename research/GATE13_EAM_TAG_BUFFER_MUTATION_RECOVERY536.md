# Recovery536 — original eCText tag parser mutates its owned text buffer

> **Corrected for Inbox rows:** this generic-vtable dispatch does not apply to
> the final PMessageRow children. Their `0x7BFAC8+0x98/+0x9C` are color getters
> `0x43B680/0x43B6A0`. See [the independently rechecked list contract](GATE13_ORIGINAL_INBOX_LIST_MILESTONE.md).

## Evidence scope and original identity

Direct inspection of owner-authorized shipped `footballmanager.exe` (4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`). Static PE disassembly only: no original-game launch, physical mouse input, or Windows 11 observation. This extends [native font/tag branch Recovery535](GATE13_EAM_NATIVE_TEXT_FONT_SWITCH_RECOVERY535.md), which verified default object `0x9269F0` bound to shipped Zurich BdXCn 16px font and original tag type jump table `0x5D7A4C`.

## Verified original owner/vtable semantics

Native `eCText` vftable at `0x7BE340`, independently decoded from the PE data mapping:
- Virtual `+0x98 -> 0x650650`: reads an editable text pointer at **object+0x2C**, cursor offset at **object+0x34**, checks nonnegative cursor; copies the later C-string bytes toward the cursor using an overlap-tolerant move, *decrements cursor*, invalidates via `0x64F600`. It is **not** a color/decoration setter.
- Virtual `+0x9C -> 0x6506A0`: reads the same editable text pointer and offset; computes string length, checks cursor against length bound, then shifts bytes **from cursor+2 toward cursor+1** using a forward overlapping byte/DWORD move and invokes `0x64F600`. It is **not** a color/decoration setter.
- Native `0x5D75B0` initially calls virtual+0x98 at `0x5D7616`, and on `<T-` (from `0x5D7855..0x5D787E`) also calls +0x98; `<D-` (from `0x5D788A..0x5D78B3`) shares this removal path.
- `<T+` or `<D+` (from `0x5D7883/0x5D78B8→0x5D78BD`) calls virtual+0x9C and reads a following byte into the working selector at stack+0x13, with `+0x98` / `+0x9C` mutations interspersed in the parser loop. The original `<T+P>...` and `<T+C>...` fragments in player labels are therefore **not** equivalent to a simple formatting-only marker passed to immutable Python text.

## What this proves and does not prove

It **proves actual in-place character-removal calls** tied to the parser and mutable native text-owned buffer. It **does not yet prove** that the final glyph colors, selector P/C values, cursor/transforms, final string mutation persistence, end-marker handling, clipping or status bit4 visibility have been fully recovered. Do not mistake `eCText`'s `+0x120=0xFFFF` constructor value for final glyph color until its draw path is traced. Do not naively erase tag spans, draw angle-brackets literally, or assume white.

## Next task within Gate13

Trace full `0x5D75B0` glyph rendering/control flags, `0x5D794D→0x5D79BD` terminal parser states, `0x650650/0x6506A0` caller semantics and color path, then bind the verified default font / conditional rich text in source-owned PMessageRow child ID2/3/0 at actual native coordinates. Source-verified text values already exist in `reconstruction/original_eamail_native_row_fields.py`; text is **not yet rendered** by normal game host. Preserve first/second click semantics, original delivered mailbox and source-only current manager. Independently map original PBg `back_3.444` four frame states before painting the button. No Gate13 acceptance until complete original Inbox GUI/action and real Win11 mouse test.
