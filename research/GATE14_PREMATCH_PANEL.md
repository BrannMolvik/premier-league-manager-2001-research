# Gate 14: PPreMatchPanel source correlation

_7 October 2026. Evidence tier: confirmed first-hand canonical executable + authorized original-disc bytes._

## Scope and safety boundary

This note records the original pre-match Match Detail panel evidence needed for
Gate-14 presentation work-ahead while Gate 13 remains externally blocked on the
normal Windows 11 acceptance receipt.

It does **not** establish the management-screen action that launches a human
fixture. That transition remains fail-closed. It also does not invent a
replacement 3D match presentation.

Canonical executable:

- `footballmanager.exe`
- SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Canonical authorized source archive:

- 511,121,336-byte Library ZIP
- SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`

## Native modal and Match Detail contract

Previously recovered source evidence establishes:

- `PPreMatchPanel` constructor/entry at `0x499C30`;
- event handler `0x49AB50` dispatches event IDs 1..4;
- selector commit routine `0x49ABA0` writes the selected mode to
  `0x877530`, refreshes all four controls, signals the modal owner, and
  closes the panel;
- event 1 -> mode 3, event 2 -> mode 2, event 3 -> mode 1, event 4 -> mode 0;
- mode contract:
  - 0 = `3D Match`
  - 1 = `3D Highlights`
  - 2 = `FastView`
  - 3 = `Quick Match`.

## Four-choice selector geometry and asset binding

The four controls are contiguous 0x4C-byte objects at:

- `PPreMatchPanel+0x3740`
- `PPreMatchPanel+0x378C`
- `PPreMatchPanel+0x37D8`
- `PPreMatchPanel+0x3824`.

Setup code around `0x4996F4..0x499803` binds all four to global wrapper
`0x946350`. Static initializer `0x5F4A10` defines that wrapper as **106 x 25**. Its
underlying resource object is `0x946370`, loaded at `0x5F49C0` from string VA
`0x835BDC`:

`FM2001_Art/Generic/GenericButtonsAndBars/button_type_14.444`

The exact original atlas is 36,964 bytes, decodes as **106 x 575**, and hashes
to `7b0148bfa65adaa7cabf08e000050ba9add3cf852a03e66423051603c4b85930`.
That is exactly 23 vertical 106 x 25 frames, matching the already recovered
Button@ease native group lengths 11 + 11 + 1. The adjacent initializer at
`0x5F4A50` loads `button_type_15.444` into a different source object
(`0x946330`) used by the following wrapper and is not the four-choice selector.

The constructor calls pass a common y-coordinate 107 and four x-coordinates.
Accounting for x86 thiscall argument order plus the event-to-mode mapping gives
the exact left-to-right selectable row:

| Mode | Label | Event ID | x | y | w | h |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 3D Match | 4 | 176 | 107 | 106 | 25 |
| 1 | 3D Highlights | 3 | 290 | 107 | 106 | 25 |
| 2 | FastView | 2 | 404 | 107 | 106 | 25 |
| 3 | Quick Match | 1 | 518 | 107 | 106 | 25 |

The corresponding language globals resolve consistently as:

- `0x981DD4` = `3D Match`
- `0x981DD0` = `3D Highlights`
- `0x981DCC` = `FastView`
- `0x981DC8` = `Quick Match`.

This closes the selector ordering and geometry without synthesizing a modern
layout.

## Dedicated original pre-match assets

The authorized Joliet filesystem contains the following exact resources under
`FM2001_Art/Generic/pre_match/`. Dimensions are the first two little-endian
16-bit values in the original EA444 header.

| Original path suffix | Bytes | Dimensions | SHA-256 |
| --- | ---: | ---: | --- |
| `pitch.444` | 32,268 | 261 x 374 | `23a776bf9445818ac5356d6c4fa8ca0595affdaf5980bbbe6cdf9df2030a82dd` |
| `playername_active_left.444` | 2,988 | 200 x 16 | `da3bc727a6980b267165dcf8c63b235e12b07cd6aa446b7875b1e19519652a00` |
| `playername_active_right.444` | 2,912 | 200 x 16 | `af809c7bb2961cc46b011fe8c7557b4eb23e97fffee6d99bd36178b48bd8b0d9` |
| `playername_disabled_left.444` | 2,604 | 200 x 16 | `59e1a1e1714b1e9dab0929112246b59c6dcd9344841aab764ef87a1850b564cd` |
| `playername_disabled_right.444` | 2,604 | 200 x 16 | `c9138b788561b7c47082755cdaa26a432ca8ce41ec3b7d6373ba63f9ef75c2df` |
| `prematch_bground.444` | 247,608 | 800 x 600 | `964d6765d7eedd7d064b3c439ed144c851ab102ec029e8fc198df0c9adb31576` |
| `rating_bar_left.444` | 3,156 | 171 x 16 | `3a7f14cee9067971c5267210bd235e457171aa9438b40be992a9009942fbc07c` |
| `rating_bar_right.444` | 3,784 | 171 x 16 | `579421a7677aedae39663fe5e14a48f3b44eb053546ffa472407f0b639ea3652` |
| `rating_bar_right2.444` | 3,188 | 171 x 16 | `dae7d2a3649c199fdc5e8829c6c0cf603c0186747c0ee8671d6e9061f7b9f7b3` |
| `top_bar.444` | 18,604 | 800 x 95 | `e3fb5f772784dd3608774aae44620e1ab932682b1f06d8153157d981ff869534` |

Executable loader strings and static wrapper initializers independently bind the
same resources and dimensions. Relevant wrapper/source pairs include:

- background wrapper `0x9420B0`, source `0x9420D0`, 800 x 600;
- pitch wrapper `0x941EB0`, source `0x941ED0`, 261 x 374;
- top-bar wrapper `0x941E70`, source `0x941E90`, 800 x 95;
- active-left wrapper `0x941F30`, source `0x941F50`, 200 x 16;
- active-right wrapper `0x941EF0`, source `0x941F10`, 200 x 16;
- disabled-left wrapper `0x942070`, source `0x942090`, 200 x 16;
- disabled-right wrapper `0x942030`, source `0x942050`, 200 x 16.

## Source-backed panel positions recovered so far

The native calls provide these exact placements:

- top bar: x=0, y=0, 800 x 95;
- pitch: x=269, y=152, 261 x 374;
- active left player-name strip: x=36, y=152, 200 x 16;
- active right player-name strip: x=563, y=152, 200 x 16;
- disabled left player-name strip: x=36, y=358, 200 x 16;
- disabled right player-name strip: x=563, y=358, 200 x 16.

These earlier rating/background uncertainties are superseded by the Recovery 363 correction below.

## Implementation boundary

The next implementation may safely introduce a source-backed pre-match
presentation model/render seam with:

- exact 800 x 600 panel coordinate space;
- exact four-choice row, labels, modes, and button dimensions;
- exact recovered top-bar/pitch/player-strip positions;
- original assets, once intentionally imported/provenance-tracked under
  `original_assets/`; specifically the selector requires the source-proven
  `button_type_14.444`, not adjacent `button_type_15.444`.

It must **not**:

- invent a management-screen button or fixture-launch action;
- expose native sentinel 5 as a selectable mode;
- route modes 0/1 to FastView as a substitute for missing 3D presentation;
- assign semantic names to the still-neutral rating discriminators 0/1/2/3;
- use `pre_match/prematch_bground.444` as the live panel background.

## Exact next task

Stage only the assets actually consumed by the verified panel seam, then bind the recovered selector/static/rating geometry. Reuse the dynamic Team_Backgrounds contract from source-equivalent match/date context and keep the management-to-match launch transition fail-closed.


## Recovery 363 correction — live background and rating-bar mechanics

Further first-hand tracing of the same canonical executable corrects one
important assumption from the earlier resource census.

### The shipped pre-match background is not the live panel background

`FM2001_Art/Generic/pre_match/prematch_bground.444` is real, hash-verified,
and initialized by the game's global resource setup. However, no direct
`PPreMatchPanel` consumer was found for its wrapper/source objects. The live
constructor instead builds its full 800x600 background dynamically:

- `PPreMatchPanel::0x499C30` derives the match/team context and calls
  `0x5D3490` into panel member `+0x6D4`;
- `0x5D3490` consumes the current date at `0x9847FC` and resolves the
  background family rooted at
  `FM2001_Art\\Generic\\Team_backgrounds`;
- source helper `0x5D3510` returns the loaded source surface;
- the constructor passes that result into wrapper `PPreMatchPanel+0x6B4`
  through `0x64E500` with exact geometry 800x600 at (0,0).

The background resolver contains the proven name grammar `background`,
`%s%d`, and `generic%d`. The authorized disc contains the corresponding
`FM2001_Art/Generic/Team_Backgrounds` tree, including generic seasonal
variants and country/team directories.

Therefore `pre_match/prematch_bground.444` must remain negative evidence:
shipped and initialized, but **not promoted as the live PPreMatchPanel
background**. The modern seam must eventually consume the same dynamic
Team_Backgrounds contract from source-equivalent match/date context.

### Rating rows are mirrored dynamic bars

The three dedicated 171x16 rating assets are source-bound as:

- `rating_bar_left.444` -> wrapper `0x941FF0`;
- `rating_bar_right.444` -> wrapper `0x941FB0`;
- `rating_bar_right2.444` -> wrapper `0x941F70`.

Four rows are constructed at y=497, 515, 533, 551. Their exact geometry is
anchored at left x=65 and right x=564 with full width 171 and height 16.

Each row has its own capped integer-width calculator:

| Native function | Record discriminator | y |
| --- | ---: | ---: |
| `0x49A3D0` | 3 | 497 |
| `0x49A460` | 0 | 515 |
| `0x49A4F0` | 1 | 533 |
| `0x49A580` | 2 | 551 |

With side selector 0, the returned width sizes the left
`rating_bar_left` overlay directly. With side selector 1, the same four
functions are recalculated and the result is subtracted from the right-side
objects' right-edge field, producing a mirrored dynamic length. The base layers
under those dynamic bars use the two right-family assets.

This source-closes the **geometry and mirroring mechanism**, but it does not yet
justify human-readable semantic names for discriminators 0/1/2/3. Keep those
identities neutral until their underlying player/record field meaning is traced.

### Revised implementation boundary

The source-backed pre-match module may now safely model:

- the dynamic 800x600 Team_Backgrounds contract and exact constructor path;
- the four mirrored rating rows and their native width functions;
- the previously recovered top bar, pitch, player-name strips, selector row,
  original selector atlas, and Zurich caption font.

It must not require or render `prematch_bground.444` as the live native
background. It must also keep the rating-row discriminator meanings,
management-to-match launch action, complete pre-match frame, and Gate 14
completion fail-closed.

The next implementation step is to stage the exact source assets that are
actually consumed by the verified panel seam, then build the render/input seam
around source-equivalent match context. The dynamic Team_Backgrounds selector
must be reused rather than replaced by the shipped but non-live pre-match
background.


## Recovery 365 implementation checkpoint — shared background seam and staged live asset slice

The repository-side pre-match presentation boundary now reuses the existing
FastView Team_Backgrounds selection contract rather than implementing a second
background resolver. `gate14_fastview_surfaced_resource_loader.py` exposes a
background-only load/decode seam that preserves the exact candidate order,
terminal-fallback fail-closed behavior, canonical executable EA444 tables, and
canonical quantization verification. The full FastView loader shares the same
private decode core so executable/table verification is not duplicated.

`gate14_prematch_surface.py` joins that source-selected 800x600 background to
the already-recovered pre-match resources. It exports only source-proven data:

- native background pixels and selected original source path;
- the six exact static placements already recovered from PPreMatchPanel;
- the four Match Detail selector rectangles, labels, modes, event IDs, original
  `button_type_14.444` atlas, and Zurich caption font;
- the four neutral rating-row discriminators, native width-function identities,
  mirrored left/right rectangles, and exact original rating source pixels.

The exact live original asset slice is now intentionally imported under
`original_assets/source/` with provenance in `original_assets/MANIFEST.md`:
the nine resources in `PREMATCH_ALL_EA444_SPECS` plus
`GenericButtonsAndBars/button_type_14.444`. The shipped but non-live
`pre_match/prematch_bground.444` remains excluded from the live import slice.
The Team_Backgrounds family and Zurich selector font were already
provenance-tracked.

This checkpoint deliberately does **not** bind the native rating-width
calculators to clean-room player/match state, claim a complete cross-layer draw
order, expose the modal from an invented management action, substitute FastView
for either 3D mode, or claim a complete pre-match/Gate-14 frame. Those remain
fail-closed.

Next source task after integration verification: trace the inputs to
`0x49A3D0/0x49A460/0x49A4F0/0x49A580` far enough to bind the four dynamic
rating widths to source-equivalent clean-room state, while separately recovering
any remaining PPreMatchPanel draw-order/text controls required before a complete
frame can be claimed.


## Recovery 366 — rating semantics and dynamic widths source-closed

The four previously neutral PPreMatchPanel rating rows are now source-closed by
combining the canonical executable with the shipped Static.dat Position table.

### Native XI-to-width calculation

Functions `0x49A3D0`, `0x49A460`, `0x49A4F0`, and `0x49A580`
all follow the same structure:

1. select one of the two eleven-pointer starting-XI arrays from the side argument;
2. iterate exactly eleven starter pointers;
3. read each player's current assigned role through the runtime position object
   at DBRPlayer `+0x248` / helper `0x4EA3C0`;
4. index the runtime Position table at global `0x874B68`;
5. compare Position byte `+0x11` with the function-specific discriminator;
6. for matching players call `0x41E1B0 -> 0x41C7E0`, the already-recovered
   exact current-role player rating;
7. sum the matching ratings, multiply by the function-specific double,
   convert to integer through `0x668350`, and cap at `0xAB = 171`.

The exact mappings are:

| Native function | Position +0x11 | Scale | Meaning |
| --- | ---: | ---: | --- |
| `0x49A3D0` | 3 | 1.71 | Goalkeeper |
| `0x49A460` | 0 | 0.342 | Defence |
| `0x49A4F0` | 1 | 0.342 | Midfield |
| `0x49A580` | 2 | 0.57 | Attack |

The scale constants are the canonical doubles at `.rdata`
`0x7C4B68/0x7C4B70/0x7C4B78`.

### Position +0x11 is the shipped lineup-group byte

The Position parser at `0x4010A0` stores the final serialized Position byte
directly at runtime Position `+0x11`. The clean-room parser already preserves
the same byte as `Position.lineup_group = Static.dat record +6`.

The complete shipped 20-position mapping proves the row semantics:

- GK -> 3;
- RB/LB/CB/SW/RWB/LWB -> 0;
- ANC/DM/RM/LM/CM/RW/LW/AM -> 1;
- CF/ST -> 2;
- None/RF/LF -> 255.

Thus RF/LF deliberately fail all four native equality tests and contribute to
none of the four pre-match bars. This is not a clean-room omission.

### Clean-room binding

The exact player-rating source already exists as
`RuntimePlayer.current_role_rating()`, which reproduces
`0x41E1B0 -> 0x41C7E0`.

`gate14_prematch_rating_widths.py` now reproduces the eleven-player grouping,
rating sum, native scales and 171-pixel cap. The pre-match surface keeps
resource loading independent and exposes a separate state-binding seam:

- left-side dynamic overlays grow rightward from x=65;
- right-side overlays preserve the native right edge at x=735 and grow
  leftward by using `x = 564 + 171 - width`;
- y remains 497/515/533/551 and height remains 16.

This closes the dynamic-width input and mirrored geometry without inventing a
management launch action or claiming a complete PPreMatchPanel frame.

The next source-backed task is to recover the remaining PPreMatchPanel text,
team/player identity controls and cross-layer draw order needed to assemble a
complete native frame. The management-to-match transition remains separately
fail-closed.


## Recovery 368 — native identity/text control contract

Further first-hand tracing of canonical `footballmanager.exe` closes the
remaining low-level identity formatting used by the pre-match panel without yet
claiming complete cross-layer draw order.

### Date and weather-line formatting

`PPreMatchPanel::0x49A610` reads current date global `0x9847FC`, decomposes
it through `0x64CCD0`, and formats the date into panel buffer `+0x70` using
the executable-resident exact format string at `0x81D5B8`:

`%Df %Mf %Yf`

The same refresh path reads match bytes `+0xD46` (weather selector) and
`+0xD44` (signed temperature). It first formats a temporary weather string
with exact format `0x81D5B0`:

`%s %d°C`

It then combines the date buffer and that temporary weather/temperature string
through English language global `0x98204C`, whose source text is `%s %s`, and
writes the resulting visible line to panel buffer `+0x270`.

The global-language mapping is independently calibrated by the already-proven
Match Detail labels: English.idx position 2697 (`3D Match`) maps to
`0x981DD4`, and positions 2698..2700 map successively down by four bytes.
Thus `global = 0x9847F8 - 4 * idx_position`. Applying that exact mapping to
the five weather globals used by the switch proves:

- weather 0 -> `Clear` (`0x98252C`);
- weather 1 -> `Sunny` (`0x982534`);
- weather 2 -> `Raining` (`0x982524`);
- weather 3 -> `Sleet` (`0x9821E0`);
- weather 4 -> `Snowy` (`0x982520`).

The same mapping resolves `0x982050` to `%s MATCH TODAY AT %s`, used for the
panel `+0x170` fixture header. When match competition/index `+0xD20` is
negative, the first substitution is source string `Friendly` at `0x9830C8`;
otherwise the first substitution is the recovered competition-name object
field. The second substitution remains behaviorally sourced through
`0x62AC80 -> 0x514270` but is left semantically unnamed until that helper is
separately identified. Center team label global `0x9830C4` resolves exactly
to `V`.

### Team badge identity

The constructor seeds both team badge resource members at panel offsets
`+0x600/+0x624` from `Clubbadges\\standard.bmp`. Refresh then resolves
team-specific presentation through the canonical source family:

- root `FM2001_art\\generic\\team_badge_stills`;
- variant key `badge_2`;
- terminal fallback
  `fm2001_art\\generic\\team_badge_stills\\generic.444`.

The resolved active controls are retained at panel offsets `+0x840/+0x890`.
This is presentation identity only; no management-to-match transition is
implied.

### Two 18-player identity banks

The refresh routine iterates exactly two match-side banks and exactly 18 slots
per side:

- side 0 count `match+0x5A4`, pointer array beginning at `match+0x004`;
- side 1 count `match+0xB54`, pointer array beginning at `match+0x5B4`.

The first 11 slots are the native starting-XI region; indices 11..17 use the
alternate disabled/substitute presentation state already correlated with the
dedicated pre-match strip assets. Empty slots are explicitly hidden rather than
filled with invented rows.

For populated slots, `0x417A90` computes the display-name length and
`0x417AE0` writes the display name. The canonical full-name format string at
`0x81858C` is exactly:

`%s %s`

Those helpers retain the native special handling for abbreviated/placeholder
first names. The nearby player byte consumed by the row formatter remains
semantically neutral in this checkpoint until its DBRPlayer field identity is
independently proven.

### Implementation boundary

`original_prematch_panel.py` now exposes these exact source facts in
`prematch_panel_contract()` with regression coverage. This does **not** yet
promote:

- the semantic identity of the second `%s` in the fixture header;
- a complete cross-layer setup/draw order;
- a management-to-match launch action;
- either missing 3D presentation path;
- Gate 14 completion.

The same calibrated language mapping also resolves the four rating-caption
globals used twice at y=498/516/534/552:

- `0x983BE4` = `GK`;
- `0x983B70` = `DEF`;
- `0x983B6C` = `MID`;
- `0x983B68` = `ATT`.

These captions independently agree with the already source-closed
goalkeeper/defence/midfield/attack rating functions.

Exact next source task: prove the PPreMatchPanel child/control registration
order against the generic panel draw semantics, then assemble only the
source-proven complete frame layers.

## Recovery 368 continuation — complete PPreMatch child-array paint order

The remaining cross-layer ordering boundary is now source-closed by combining
the PPreMatch setup routine with the already-proven generic panel traversal.

`PPreMatchPanel::0x4967F0`:

- allocates exactly `0x2D8` bytes for child pointers;
- stores the pointer array at panel `+0x1C`;
- writes child count `0xB6 = 182` at panel `+0x38`;
- fills every pointer index 0 through 181.

The generic control contract was already source-closed during FastView work:
`0x6533A0` traverses parent `+0x1C` from index 0 through count-1 and invokes
the visible-child render slot. Therefore the PPreMatch sequence below is native
paint order, not a heuristic based on allocation or call proximity.

| Child indices | Source-proven family |
| --- | --- |
| 0 | live 800x600 Team_Backgrounds surface |
| 1 | pre-match pitch |
| 2 | top bar |
| 3 | fixture header text |
| 4 | date + weather/temperature line |
| 5-6 | two team badge controls |
| 7-9 | left team identity, center `V`, right team identity text |
| 10-31 | 22 starting-XI pitch-marker controls, 11 per match side |
| 32-64 | side-0 starter row controls, 11 rows x 3 controls |
| 65-92 | side-0 slots 11..17, 7 rows x 4 controls |
| 93-125 | side-1 starter row controls, 11 rows x 3 controls |
| 126-153 | side-1 slots 11..17, 7 rows x 4 controls |
| 154-169 | four rating rows x four picture layers |
| 170-177 | four rating captions on both sides |
| 178-181 | Match Detail selector controls |

The seven post-starter rows contain an additional disabled-strip picture layer,
which accounts for four controls per row rather than the starters' three.
This matches the separately recovered active/disabled pre-match strip assets
without requiring a guessed visibility policy.

Selector child order is the native object/event order, not left-to-right
geometry: Quick Match, FastView, 3D Highlights, 3D Match (modes 3,2,1,0).
Their rectangles do not overlap, so this reverse geometric order has no
pixel-order ambiguity.

The clean-room contract now exposes the complete 182-slot range partition and
keeps the following separate blockers false: a management-screen match launch,
3D Match/Highlights presentation, and Gate 14 completion.

Exact next task: reconcile the existing `gate14_prematch_surface.py` output
against this full source order and bind the newly recovered text/team/player
identity content into a complete pre-match frame model. Do not mark the frame
complete until every one of the 182 native child slots is either represented
or intentionally proven non-pixel/hidden for the supplied match state.

### Recovery 368 frame reconciliation — exact top-layer control geometry

The same source setup closes exact rectangles and style-wrapper identities for
the non-roster identity controls:

- fixture header: `(250,45,300,30)`, text wrapper `0x87BE30`;
- date/weather line: `(250,70,300,16)`, text wrapper `0x87BE30`;
- left badge: `(38,1,135,93)`;
- right badge: `(627,1,135,93)`;
- left team identity: `(184,4,185,39)`, wrapper `0x87BE80`;
- center `V`: `(374,5,52,37)`, wrapper `0x87BE70`;
- right team identity: `(429,4,185,39)`, wrapper `0x87BE80`;
- rating captions use wrapper `0x87BEA0`, 25x14 at x=37/737 and
  y=498/516/534/552.

These controls occupy the already-proven native child positions 3..9 and
170..177. Their geometry is no longer a complete-frame blocker. Remaining
frame work is concentrated in the 22 starting-XI pitch markers, the two
18-player row banks, exact selector visual state, and state-to-text/raster
binding rather than global z-order.


## Recovery 369 — full player-strip row geometry recovered

A separate Recovery 368 branch had already persisted a narrower constructor trace that was not merged with PR #508. Recovery 369 reconciles that evidence on top of the source-closed identity/text and 182-child order contract instead of repeating the trace.

The full player-strip layout is now source-closed:

- starter rows per side: 11 rows at y = 152, 170, 188, 206, 224, 242, 260, 278, 296, 314, 332;
- reserve/post-starter rows per side: seven rows at y = 358, 376, 394, 412, 430, 448, 466;
- left-side strip x = 36, right-side strip x = 563;
- every strip is 200 x 16;
- starter rows construct only the corresponding active-left/active-right strip;
- reserve rows construct both the active and disabled side-specific strip at the same rectangle.

This geometry aligns exactly with the already-proven child ranges: side-0 starters 32..64, side-0 post-starters 65..92, side-1 starters 93..125, and side-1 post-starters 126..153. The extra co-located disabled picture on each reserve row explains the four-child reserve-row group versus the starters' three-child group.

The reserve active/disabled selection itself remains unresolved. The clean-room contract therefore exposes both native source variants and keeps `reserve_variant_state_source_closed = False`; it must not infer eligibility, bench status, or selection state from modern assumptions.

Exact next source task: source-close the 22 starting-XI pitch-marker placement/state, row text/content/style and reserve-state selector, and Match Detail selector visual state, then account for every visible child in native paint order for a supplied match state.

## Recovery 369 continuation — source-closed text controls surfaced

Frame reconciliation now represents the exact non-roster text-control placements already proven by Recovery 368 rather than leaving them only in research constants. The clean-room surface contains 13 text-control records corresponding to native child slots 3, 4, 7..9 and 170..177.

The fixed source text that can be promoted without runtime inference is limited to center `V` and the duplicated rating captions `GK/DEF/MID/ATT`. Fixture header and date/weather controls retain their exact panel buffer offsets `+0x170/+0x270`, rectangles and style wrapper but do not claim a supplied-state string yet. Left/right team identity controls retain exact geometry/style only; their dynamic team-name binding remains separate.

This deliberately narrows complete-frame blockers without collapsing formatting evidence into runtime state. The surface contract continues to report dynamic fixture/date buffers unbound, team identity text unbound, reserve strip variant unresolved, complete frame false, and Gate 14 false.

## Recovery 369 continuation — explicit 182-child frame coverage audit

The clean-room surface now audits the already-proven 182-child native paint partition rather than relying on a single complete-frame boolean. Every source family carries a represented-control count, supplied-state-complete flag, and explicit blocker when incomplete.

At this checkpoint 86 of 182 native controls have a structural/pixel representation in the surface model. This is **not** an 86/182 fidelity score: a represented dynamic control can still be incomplete for a supplied match state. Only the live background, pitch, top bar, and eight rating captions are currently marked supplied-state complete.

Notable fail-closed families include zero of 22 starting-XI pitch markers, zero staged pre-match badge controls, partially represented starter/reserve row groups, unbound dynamic header/date/team strings, base-surface rating widths not yet attached to supplied state, and selector atlases whose exact runtime visual state is unresolved.

The audit itself verifies that the child ranges flatten to exactly indices 0..181. Complete-frame promotion must therefore clear every family blocker rather than bypassing missing source evidence with a generic frame flag.


## Recovery 370 — starting-XI pitch-marker contract recovered

Private byte execution recovered during Recovery 370. The authorized canonical
`FOOTBAL.EXE` was re-extracted from the 511,121,336-byte Library archive and
re-verified at SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No private executable/disassembly bytes are committed.

First-hand disassembly now source-closes the 22 native child controls at indices
10..31:

- `0x499820` positions exactly eleven markers per match side;
- each marker is 36 x 32;
- side-0 controls begin at panel `+0xC60` and side-1 at `+0xE70`, each
  with 0x30-byte stride;
- corresponding source wrappers begin at `+0x9A0/+0xB00`, each with
  0x20-byte stride;
- the first marker on each side, children 10 and 21, uses global source object
  `0x9460D0`, loaded from
  `fm2001_art\\generic\\front-end-shirts\\custom\\goalkeeper.444`;
- the remaining ten markers per side use team-specific sources stored at
  `+0x648/+0x66C` and referenced at `+0x668/+0x68C`, built by native
  `0x408320`;
- that builder uses the original front-end-shirt roots `...\\generic` and
  `...\\custom`, with generic filename grammar `Team%.2d.bmp` plus the
  source `.bmp/.444` variants.

Marker visibility is also source-closed. `0x499820` walks the eleven source
player IDs, resolves each through `0x417F50`, hides the control through its
native visibility slot when resolution fails, and otherwise positions and shows
the marker.

### Formation-coordinate producer and exact pixel transform

`0x499A50` builds normalized coordinate pairs into panel `+0x6D8` using
the current assigned-role object, auxiliary role byte, ordinal among players
sharing that role, formation table global `0x87AE64`, lookup `0x5F0CC0`,
and coordinate transform `0x5F0BD0`. The transform also consumes two manager
shape bytes at relative offsets `+0x180/+0x183`, scaled by 0.01. Their
higher-level semantic labels remain intentionally neutral.

The refresh path calls the marker positioner with base `(270,153)`. Native
float-to-int helper `0x668350` temporarily selects x87 truncation toward zero.
For normalized `(x,y)` this yields:

- side 0:
  - `scaled_y = trunc(y * -187)`
  - `py = 153 - scaled_y + 163`
  - `scaled_x = trunc(x * -261)`
  - `px = 270 - scaled_x - 18`
- side 1:
  - `scaled_y = trunc(y * 187)`
  - `py = 153 - scaled_y + 179`
  - `scaled_x = trunc(x * 261)`
  - `px = 782 - scaled_x - 270`

The clean-room contract now exposes this exact transform and keeps team-shirt
pixel staging false. Therefore the marker family's geometry, visibility rule,
formation-coordinate producer, resource ownership, and pixel transform are
source-closed, while complete supplied-state marker rasterization remains
fail-closed until the dynamic shirt sources are staged/bound.


## Recovery 371 — player-row content/state and selector visual state source-closed

With private executable access restored, the same canonical `FOOTBAL.EXE`
was traced through PPreMatch refresh `0x49A610`, the row text constructors,
the player display-name helpers, and the Match Detail selector commit path.

### Player rows

The two 18-slot row banks now have source-closed content and visibility rules:

- side 0 uses match count `+0x5A4` and player array `+0x004`; side 1 uses
  count `+0xB54` and array `+0x5B4`;
- populated slots show the active 200x16 strip and their two text controls;
- unused reserve slots 11..17 hide the active strip, show the co-located
  disabled strip, and do not publish player text;
- empty starter slots have no disabled-strip child and therefore contribute no
  substitute placeholder layer;
- shirt number comes from runtime player byte `+0x70` and is formatted through
  the native whole-number `%N` path;
- PPreMatch calls native `0x417A90/0x417AE0` with mode 0, so its visible name
  is `%c. %s`, or surname-only when the first-name source string begins `-`;
- the clean-room reuses the already-source-closed Squad helpers
  `format_squad_whole_number()` and `format_squad_display_name()` rather than
  maintaining a second approximation of those native formatters.

Exact text geometry for every row is now represented:

- left number `(37, y+1, 25, 14)`, left name `(67, y+1, 167, 14)`;
- right name `(564, y+1, 167, 14)`, right number `(737, y+1, 25, 14)`;
- shared text-style wrapper `0x87BEA0`, number auxiliary wrapper `0x87B6B0`;
- starter rows contain strip/number/name children; reserve rows contain
  active-strip/number/name/disabled-strip children in the already-proven
  182-child paint sequence.

`bind_prematch_player_rows()` now accepts supplied left/right participant arrays
(maximum 18 each), preserves their source order, and returns exact native strip
state plus source-formatted shirt-number and display-name text. This is a
supplied-state binding seam, not a match-selection policy.

### Match Detail selector visual state

The four selector controls are ordinary Button@ease controls constructed by
`0x5D3810 -> 0x652FD0`. PPreMatch does not read mode global `0x877530` in its
setup/refresh path. `0x49ABA0` writes the selected mode, hides/refreshes all
four controls, signals modal owner `0x877960` through `0x5328B0`, and closes
the modal through `0x6539F0` immediately.

Therefore there is no separate persistent radio/selected visual to recover.
The source visual contract is the already-proven generic Button@ease state:
initial flags `0x183`, 11-frame normal group, 11-frame alternate group, and
one disabled frame, with pointer-driven animation. The only remaining runtime
input for a specific rendered selector frame is the live pointer/update state.

### Frame impact

All four player-row child families are now structurally represented, raising
the fail-closed 182-child audit from 86 to 158 represented controls. This is
not a complete-frame claim: supplied player content must still be attached by
the row-binding seam, marker shirt pixels and team badge pixels are not yet
staged, dynamic header/team text remains unbound, rating widths require supplied
state, and live selector pointer state must still be supplied.



## Recovery 372 — PPreMatch team badges reuse canonical club-art selector

Recovery 372 re-extracted the authorized canonical `FOOTBAL.EXE` from the
511,121,336-byte source archive and re-verified SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No executable or disassembly bytes are committed.

First-hand disassembly of the already-identified PPreMatch refresh routine
`0x49A610` closes the remaining selector-identity boundary for native child
slots 5 and 6:

- callsite `0x49A792` invokes club-art selector `0x40C850` for the first
  match side;
- callsite `0x49A7D6` invokes the same `0x40C850` selector for the second
  match side;
- both calls pass family literal VA `0x81D4F8`,
  `FM2001_art\\generic\\team_badge_stills`;
- both pass variant literal VA `0x81D1A8`, exact key `badge_2`;
- when the selector does not resolve a club-specific resource, native loader
  `0x64D870` receives fallback literal VA `0x81D4C4`,
  `fm2001_art\\generic\\team_badge_stills\\generic.444`;
- the two resource members remain panel offsets `+0x600/+0x624`, while their
  active controls are retained at `+0x840/+0x890`.

This proves that PPreMatch and FastView share the already source-closed club-art
selection contract rather than merely having similar path strings. The
clean-room therefore reuses the existing state binding based on
`Club.graphics_basename` and `CountryDefinition.graphics_directory`, and
the verified surfaced-resource loader now stages the selected home/away
135x93 EA444 badge pixels directly into PPreMatch's exact native rectangles:

- child 5: `(38,1,135,93)`;
- child 6: `(627,1,135,93)`.

The fail-closed 182-child frame audit consequently promotes the `team_badges`
family from zero represented controls to both source controls and marks that
family supplied-state complete. Total represented controls rise from 158 to
160.

This does **not** promote complete PPreMatch fidelity. Starting-XI shirt pixels,
fixture/date buffers, left/right team identity text, supplied-state rating
widths, player-row content attachment, live Button@ease pointer/update state,
the management-to-match launch route, and complete-frame/Gate-14 completion
remain separate boundaries.


## Recovery 373 — starting-XI shirt selector and numbered-frame contract

Fresh first-hand disassembly of the same canonical executable narrows the
remaining 22-marker pixel path without borrowing PMatchInfo assumptions.

### Native kit context: `0x5EF940 -> 0x5EF9E0`

PPreMatch constructor setup calls `0x5EF940` with the two match club records.
The function compares primary kit color bytes at DBRClub `+0x4A` using the
23-row, six-byte sentinel table at `0x834AF8`. Its exact decision tree is:

1. if the two primary colors do not clash, both sides use primary context;
2. on a clash, prefer the away alternate when home-primary differs from
   away-alternate;
3. otherwise prefer the home alternate when home-alternate differs from
   away-primary;
4. otherwise use both alternates when the two alternate colors differ;
5. otherwise both context flags remain primary.

The function returns, per side, the context flag plus DBRClub `+0x44` for
primary or `+0x47` for alternate. Compact club reader `0x4022D0` maps the
corresponding source bytes from Master.dat +52/+55 and maps the color IDs from
Master.dat +58/+70 to expanded `+0x4A/+0x56`. Runtime import `0x403660`
copies these fields unchanged.

### Team shirt ownership: `0x408320`

PPreMatch calls `0x408320` twice, storing resources at panel
`+0x648/+0x66C` and exposing them through `+0x668/+0x68C`.

For primary context, `0x408320` first asks `0x40DA90` for the club graphics
basename and attempts the club-specific source beneath:

`fm2001_art\\Generic\\front-end-shirts\\custom\\<basename>.444`

If that custom load succeeds, it returns without entering generic generation.

Alternate context skips the custom attempt. A failed primary custom attempt
also enters the same generic path. That path uses:

`fm2001_art\\Generic\\front-end-shirts\\generic\\Team%.2d.bmp`

with the source index read directly from DBRClub `+0x47`, clamped to 0..36.
The selected BMP is 36x1280 (40 numbered 36x32 frames). It is then recolored by
native `0x5E4C60`, which consumes the selected primary/alternate color block.
Therefore generic PPreMatch shirts are dynamic generated pixels, not a static
EA444 atlas. Reusing the PMatchInfo primary-custom atlas path is valid only for
the source-identical custom branch; substituting it for generic/alternate
shirts would be a fidelity error.

### Per-player numbered frame: `0x41E3F0 -> 0x41E3D0`

For every one of the 22 marker controls, `0x499820` calls `0x41E3F0`.
The helper compares runtime player registered club `+0x10` with the supplied
team object's club id `+0x04`:

- equal -> player byte `+0x70`;
- different -> player byte `+0x76`.

PPreMatch then applies `(byte & 0xFF) * 32 - 32` as the source-frame vertical
offset, with no additional clamp in this path.

### Clean-room checkpoint

Branch `chatgpt/gate14-prematch-xi-shirts-r373` now:

- exposes Master.dat +52/+55/+58/+70 on `Club`;
- reproduces the exact kit-clash/context decision;
- exposes source-exact custom and generic candidate ownership;
- reproduces the exact per-player 32-pixel frame transform;
- keeps `0x5E4C60` generic recolor pixels, final marker raster staging,
  complete-frame fidelity and Gate 14 completion false.

Exact next implementation task: reproduce the bounded `0x5E4C60` 8-bit BMP
palette/recolor transform or otherwise prove a byte-equivalent clean-room
output, then load custom/generic/goalkeeper sources and bind all 22 marker
rasters into the existing source-closed visibility/formation geometry.


### Recovery 373 continuation — generic TeamNN.bmp source-RGB recolor reproduced

The generic/alternate branch below `0x408320` is now clean-room reproduced
through the source-RGB stage of `0x5E4C60`.

Fresh first-hand disassembly proves:

- the generic source is an uncompressed 8-bit 36x1280 Windows BMP, i.e. forty
  36x32 numbered frames;
- the palette color table is the 23 x 8-byte block at `0x834190`;
- primary context consumes club color IDs `+0x4A/+0x4B` (Master.dat +58/+59);
- alternate context consumes `+0x56/+0x57` (Master.dat +70/+71);
- helper `0x5E4B10` rewrites palette indices 1..31 and 32..63 from the two
  selected color records using signed integer division with truncation toward
  zero and writes the exact endpoint explicitly;
- palette indices 64..79 are rewritten by the same helper from white to black;
- all other original BMP palette entries remain untouched;
- `0x5E4980` skips indexed pixel zero, making it transparent/no-write.

`gate14_prematch_generic_shirt.py` now parses the bounded BMP format,
reproduces those three palette transforms, preserves untouched source palette
entries and emits an RGBA source-color plane with index zero transparent.
The remaining native display-format packing inside `0x5E4980` is intentionally
not promoted yet. It consumes runtime mask/shift globals in the `0x9848xx`
block and must be source-closed separately before exact legacy packed-pixel
equivalence is claimed.

The complete 22-marker raster family therefore remains fail-closed despite the
source-RGB generic atlas being available. Exact next task: recover the
`0x5E4980` display mask/shift initialization and reproduce its packed-color
quantization, then combine primary custom, generic/alternate and goalkeeper
sources into the supplied-state marker binder.
