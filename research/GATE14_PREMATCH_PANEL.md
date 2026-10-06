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
