# Gate 13 TeamSelect native hierarchy trace

_Date: 1 October 2026 KST_

## Evidence boundary

This checkpoint comes from bounded Capstone disassembly of the canonical
original executable (SHA-256 `833bf95e...cc3`) and canonical database records.
Private instruction reports remain outside Git. No executable, disc image,
raw dump, or original resource bytes are committed.

## Recovered owner graph

RTTI identifies the screen as `PMain@TeamSelect` (type descriptor `0x81EC10`,
vftable `0x7C7650`). Its native children are `LeagueBtnGrp@TeamSelect`
(`0x7C7230`, nested `Btn`/`Bar` at `0x7C72D0`/`0x7C7388`) and
`TeamBtnGrp@TeamSelect` (`0x7C75B0`, nested `Btn`/`Bar` at
`0x7C74F8`/`0x7C7440`).

Setup `0x4D7CC0` creates 16 league/country groups at `(20, 78 + 30*i)`,
IDs `1..16`, object offsets `0x2A24 + 0x4C*i`. It creates 24 club groups at
`(581, 78 + 20*i)`, IDs `0x11..0x28`, object offsets `0x2EE4 + 0x40*i`.
The league groups bind the recovered exact `choice_league_but_anim.444` and
`choice_league_but_bars.444` wrappers.

## Native contents and navigation

For English/default locale, constructor `0x4D9290` stores country IDs in this
order: England 26, Scotland 66, Germany 33, Italy 40, Spain 73, France 31,
Holland 24, Belgium 9. Names are resolved from canonical database records.

Population routine `0x4D9C70` binds country rows to those records. Expanding a
country rebuilds the same 16-control list with applicable competition rows.
Clicking a competition calls `0x4DA0F0`, which scans canonical club records,
sorts visible club names, binds at most 24 club controls, and hides unused
rows. Event owner `0x4DA480` routes Back (`0x29`) to PStartMenu and Start
(`0x2A`) through selected country and competition identity. English activation
`0x4D9AA0` selects England and its first resulting competition row.

This proves a two-stage native hierarchy, not a flat developer club picker:

`country -> competition -> club -> Start`

## Exact filters and stable ordering

`0x4D9C70` retains only competition records whose runtime kind is `1`, whose
country is the selected country, and whose parent ID is `-1`. Comparator
`0x4DA0B0` orders the retained root leagues by signed initialization-order
value; the small-range sorter at `0x4DA980` preserves source-table order for
ties. `0x4DA0F0` retains clubs whose competition ID equals the selected league
and stably orders their raw CP1252 visible-name bytes. The reconstruction now
implements those predicates directly and keeps the native 16/24 row caps.

The English default therefore opens England -> F.A. Premier League and shows
the 20 clubs alphabetically from Arsenal through West Ham United. The other
seven country league lists are derived by the same source fields, not a modern
hard-coded league map.

## Native frames, fonts and interrupted selection-write boundary

Both hierarchy animation children use 11 NORMAL frames, 11 ACTIVE frames and
one DISABLED frame: source indices `0..10`, `11..21`, and `22`. Team bars use
NORMAL `0/1`, ACTIVE `2`, DISABLED `3`. League bars use country NORMAL `0`,
competition NORMAL `1`, shared transition row `2`, ACTIVE `3`, DISABLED `4`.
The recovered sources are 30x29/168x29 for league rows and 30x19/167x19 for
club rows. The canonical 30x438 club animation contains 23 addressable 19-pixel
frames plus one trailing source scanline which no recovered state reads.

League labels use `Fonts/Zurich_BdXCn_BT_18pixel.fnt`; club labels use
`Fonts/Zurich_BdXCn_BT_16pixel.fnt`. Both are centered in the native bar child
using source glyph alpha and the recovered white/black endpoint colors.

The interrupted Codex trace associated `0x4D8E90` / `0x4D9240` with the
club-row toggle and a write/clear of the 0x30-byte TeamSelect selection record.
Its semantic annotation of the loaded `DBRClub+0x40` value as a canonical club
ID is **not promoted**: earlier independently verified executable work maps
runtime `DBRClub+0x40` to the manager ID/reference (Arsenal -> manager 204).
The exact selection-record payload, and how Start resolves that payload back to
the controlled club, therefore requires a bounded re-trace.

The reconstruction keeps the recovered visible-row toggle/ACTIVE state but
deliberately does not pass that provisional record index into the gameplay
backend. Start remains fail-closed until the payload identity is reconciled.

## Integrated verification and remaining boundary

The four exact TeamSelect club-row/font resources were imported through the
hash- and inventory-gated asset path. Twenty focused tests pass, including the
real licensed resource loader (one unrelated source-gated test remains an
expected skip in the ordinary run). The upgraded Windows audit now verifies
default 13-row/20-club population, country clear, competition repopulation,
club-row toggle and ACTIVE frame state while requiring gameplay club selection
to remain unset until the payload mapping is recovered.

The current desktop Python runtime cannot execute that upgraded audit because
its bundled Tcl/Tk install lacks `init.tcl`; no upgraded graphical pass is
claimed. The earlier Windows first-screen receipt remains valid for its prior
scope. Gate 13 remains active for the payload re-trace, the upgraded Windows rerun,
and broader management-screen presentation.
