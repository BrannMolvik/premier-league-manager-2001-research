# Gate 13 central management-header source trace

_Recovery 396, 8 October 2026._

## Authoritative local correction — 8 October 2026

**Additional9October correction:** the supporting font ownership below was
also wrong. Direct object `8CAB80` is16px, not18px: the canonical sequential
loader pushes path839E30 at6044AC, sets ECX=8CAB80 at6044F4, then calls657650
at6044F9. The following18px resource is bound to8BD970. Header setup passes
8CAB80 directly at4306D8/43075C/4307DA. Use the staged
`Fonts/Zurich_XCn_BT_16pixel.fnt`,75,217bytes,
SHA-256`e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18`,
atlas1261x17/native lineheight18. The minimal repair changes only that binding
and its verification/tests; geometry, formatting and input semantics stay put.
See `GATE13_SQUAD_RESOURCE_CORRELATION.md` for independent lifecycle challenge.
The historical18px claims below are superseded, not implementation authority.

The **36-pixel font mapping below is disproved** by a fresh, hash-gated read
of the canonical executable. The exact `0x6043AA` instruction pushes
`0x839E94`; that string is `Fonts\\Zurich_BdXCn_BT_32pixel.fnt`, including
the native terminating zero. The same loader block sets ECX to `0x8F21B0`
at `0x6043F2` and invokes `0x657650` at `0x6043F7`. Constructor
`0x430651` passes that exact font object into the club-caption control.
The 36px asset identity is real, but does **not** establish this ownership.
Do not import or substitute it for this control.

The staged, byte-identical **32px** font is 136,128 bytes, SHA-256
`27b5e4c42518bef0e000a5878939f859c2c1b1e635e4fd200752e23c468c3e36`,
atlas 2422x34, native line height 37. `Southport` measures 90 pixels,
right-aligned at x=460 in the unchanged `(172,1,378,32)` control.
`test_original_management_club_caption.py` now checks the path reference,
font binding and constructor argument against an opt-in canonical executable,
as well as the real staged font and clipped pixels without private binaries.

Accessor `0x40DA50` is also conditional: it first calls `0x403600`; only a
null result falls back to `DBRClub+8`. The local caption contract preserves
the nonempty human-user caption override and the explicit fresh empty caption
proved at `0x424F3F`; unknown user context remains withheld.

Implementation evidence: original behavior is the existing 32px source control;
the proposed 36px replacement would be a reconstruction regression. Minimum
repair is to retain the verified loader/font and reconcile the conflicting
research. Geometry, source color/style, simulation and RNG are unchanged.
Conditional match-line ownership and startup-FMV transport remain separate.
The following Recovery-396/398 text is retained as historical evidence and
must be read with these two corrections.

## Scope and evidence boundary

This note closes the ordinary **central** management-header text controls that
are missing from the current fresh Southport presentation. It is deliberately
separate from the already recovered application-owned `MENU` compound at
`(599,0,100,95)`.

First-hand analysis used the canonical shipped executable only:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Canonical `English.str` / `English.idx` were used to resolve the referenced
language globals. Original executable bytes and private disassembly remain
outside Git.

The already recovered background layer remains:
- competition header bitmap `back_2_<variant>.444`;
- screen rect `(171,0,385,95)`.

The dynamic text controls below sit over that bitmap. Their absence is therefore
an independent renderer omission, not evidence that the right-side `MENU`
control failed.

## Primary club-name control

The application constructor creates a text control at application offset
`+0x2A4`:

- screen rect: **`(172,1,378,32)`**;
- text setup: `0x651F00`;
- native text/style argument: `0x2102`;
- native color endpoint: `0xFFFF`;
- font object: `0x8F21B0`.

The management refresh at `0x432A20` obtains the current human club, calls
club accessor `0x40DA50`, writes the returned text pointer into the control,
and refreshes it through `0x64F600`.

`0x40DA50` returns the first localized club string field at native
`DBRClub+0x08`. The sibling `0x40DA70` returns the second at `+0x0C`.
The already reconstructed Master.dat parser reads those two source fields in
the same order as `Club.name` and `Club.short_name`. Therefore the central
32-pixel line is source-bound to **`Club.name`**, not a synthetic title.

For the fresh Southport path this value is exactly **`Southport`**.

### Exact original font

Loader `0x6043F2` binds font object `0x8F21B0` to:

`Fonts/Zurich_BdXCn_BT_36pixel.fnt`

The authorized canonical source file is 155,544 bytes with SHA-256:

`92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df`

That font is **not currently staged in `original_assets/source/Fonts`**.
It must be imported byte-for-byte through the normal authorized-source asset
process and added to `original_assets/MANIFEST.md`; substituting another
font is not source-equivalent.

## Supporting 18-pixel controls

The constructor also creates three ordinary white text controls using font
object `0x8CAB80`, source-bound to the already staged original:

`Fonts/Zurich_XCn_BT_18pixel.fnt`

SHA-256:

`968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a`

The controls are:

| Purpose | Screen rect | Text source |
| --- | --- | --- |
| conditional match line 1 | `(172,34,378,16)` | application buffer `+0x82` |
| conditional match line 2 | `(172,51,378,16)` | application buffer `+0xE6` |
| current-date line | `(172,68,378,16)` | application buffer `+0x64` |

All three use the recovered constructor style value `0x2102` and the normal
white endpoint. Additional overlapping application controls are not promoted
to ordinary-header semantics by this trace.

## Exact language templates

The previously source-closed `MENU` global at `0x9820F4` is English.idx
entry 2497. The surrounding language-global table is one dword per English.idx
entry. Resolving the exact globals used by the central header gives:

- `0x982AE8` -> English.idx **1860** ->
  **`%C %Rf{ Round} %Lf{ Leg}`**
- `0x981EE0` -> English.idx **2630** ->
  **`%1s Vs %2s %D{%D %M %Y}`**
- `0x983FE4` -> English.idx **517** ->
  **`Today is %D %M %Yf`**

The first two are passed through FM2001's match formatter `0x5146B0`.
Its `%1s` / `%2s` club-name branches call `0x40DA70`, proving that the
matchup template uses the source **short club names**.

The date line is refreshed independently by `0x432710`: it supplies language
global `0x983FE4` plus current date global `0x9847FC` to date formatter
`0x64D150`, writes the result to application buffer `+0x64`, then binds
that buffer to the y=68 control.

Therefore an ordinary fresh management header with valid human-club and game
date state cannot source-correctly be entirely blank: the club-name line and
the current-date line have independent source paths.

## Recovery 398 formatter/style closure

Recovery 398 re-materialized the authorized original disc archive and
re-extracted the canonical executable. Its SHA-256 again matched
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

First-hand disassembly of date formatter `0x64D150` closes the three tokens
used by English.idx 517:

- `%D` emits the **unpadded decimal day**;
- `%M` emits the **first three CP1252 bytes of the localized month name**;
- `%Yf` emits the **full four-digit year**.

For the canonical fresh start on 1 July 2000 the exact English result is
therefore `Today is 1 Jul 2000`. This is not a Python `strftime`
substitution.

The recovered `0x2102` setup for the central text controls reaches the shared
eCText draw path with **right alignment and vertical centering**. The clean-room
renderer may therefore place the y=68 date line by right-aligning its exact
Zurich glyph width inside `(172,68,378,16)`, vertically centering by the
font's native line height, and clipping half-open to that control rectangle.
The native endpoint remains white `0xFFFF`.

The authorized disc also yielded the exact missing
`Fonts/Zurich_BdXCn_BT_36pixel.fnt` bytes (disc basename `ZURICH8.FNT`).
The re-extracted file is 155,544 bytes and independently rehashed to the
already-recorded SHA-256
`92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df`.
Those bytes are verified but are still **not staged in Git** at this checkpoint;
the club-name renderer must remain blocked until the byte-identical asset is
imported through the repository provenance path.

No raw executable, disc image, private disassembly dump, or unstaged font bytes
are committed by this trace.

## Conditional next-match selection boundary

Routine `0x432760` clears the two match-line buffers and asks `0x615DA0`
for a qualifying match using the current human club and date. Only a successful
result populates y=34/y=51 via the two exact templates above.

`0x615DA0` is source-bounded but its internal exclusion predicate is not yet
semantically named. It calls `0x615D10` with the selected collection, club and
date, examines the returned wrapper/underlying match, and can advance to another
date/match before returning a qualifying wrapper. This trace therefore does
**not** replace that selector with a plausible "next fixture" search.

The two match-line **format/layout contracts are closed**; their clean-room
producer remains fail-closed until `0x615D10/0x615DA0` is either source-closed
or matched to an already reconstructed equivalent.

## Clean-room consequence and bounded implementation task

The existing `ClubHeaderView` already carries the two always-required inputs:
`name` and `current_date`. The live host already draws the source-proven
`back_2_<variant>.444` bitmap but does not render this central dynamic text
layer at all.

The minimum original-proven implementation boundary is therefore:

1. import and manifest the exact authorized 36-pixel bold Zurich font above;
2. render `ClubHeaderView.name` in the source rect
   `(172,1,378,32)` using that exact font and recovered control style/color;
3. render the exact source-formatted current-date line in
   `(172,68,378,16)` using the already staged 18-pixel Zurich font;
4. leave y=34/y=51 fail-closed until the match selector is source-closed; once
   closed, use only the two exact original templates and short club names;
5. add a fresh-Southport regression proving the central header contains the
   source club name and a nonblank source date line, instead of accepting the
   current blank bitmap-only result.

This source trace does not claim fresh Squad complete. Reserve-selection state
still needs runtime propagation into ordinary player-name colors, the header
text layer is not yet integrated, and the startup-FMV Windows transport receipt
remains a separate Gate-13 audit blocker.
