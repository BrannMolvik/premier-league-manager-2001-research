# Gate 13 central management-header source trace

_Recovery 396, 8 October 2026._

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

## Conditional next-match selection boundary

Routine `0x432760` clears the two match-line buffers and asks `0x615DA0`
for a qualifying match using the current human club and date. Only a successful
result populates y=34/y=51 via the two exact templates above.

Existing canonical-executable analysis independently source-closes `0x615D10`
through the shared post-match path `0x5127A0`: from current relative day + 1,
the caller selects the primary/secondary `ScheduleContainer` through
`0x510300`, then `0x615D10` scans forward in that container for a match
involving the same club. The base same-club forward scan is therefore no longer
an open semantic boundary.

The remaining source-open boundary is `0x615DA0` itself. It calls the proven
`0x615D10` scan, examines the returned wrapper/underlying match, and can
advance to another date/match before returning a qualifying wrapper. Its
exclusion/advance predicate is not yet semantically named. This trace therefore
does **not** replace that wrapper filter with a plausible "next fixture" search.

The two match-line **format/layout contracts are closed**; their clean-room
producer remains fail-closed until the remaining `0x615DA0` wrapper filter is
source-closed or matched to an already reconstructed equivalent.

### Recovery 397 execution blocker

The authorized Library ZIP was successfully resolved and materialized again,
but the current execution sandbox fails even trivial container and Python
process startup with `caas.internal.errors.ClientError`. Therefore a fresh
private byte-level trace of `0x615DA0` cannot be executed in this recovery.
This is an infrastructure blocker, not evidence that the source is unavailable
and not a reason to infer the missing predicate. The wrapper filter remains
fail-closed while independent source-closed Squad integration proceeds.

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
