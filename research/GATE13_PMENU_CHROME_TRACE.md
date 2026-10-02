# Gate 13 PMenu chrome and static menu trace

_Date: 2 October 2026 KST_

This note records the first source-bound management-shell chrome after the
fresh-game route recovered in `GATE13_MANAGEMENT_SHELL_ROUTE.md`.

Trace source: canonical `footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Original resources were read from the authorized source image outside Git.
Raw disassembly and unselected proprietary bytes remain private.

## PMenu row-class family

MSVC RTTI and vtables identify the management menu classes:

| Class | Vtable | Source-bound setup/use |
| --- | ---: | --- |
| `CMenuList` | `0x7C3E34` | embedded by `PMenu` |
| `PBaseMenuRow` | `0x7C3C50` | common row base |
| `PTitleMenuRow` | `0x7C3A80` | setup `0x47A7E0` |
| `PChildMenuRow` | `0x7C3A20` | setup `0x47A990` |
| `MenuTitleArrow` | `0x7C3B98` | title-row child |
| `MenuBackgroundToggle` | `0x7C3AE0` | menu background state |
| `PTitleMenuRow::SelectBmp` | `0x7C3CB0` | title selection bitmap |
| `PChildMenuRow::SelectBmp` | `0x7C3D4C` | child selection bitmap |

The row builder at `0x482300` advances visible rows in **29-pixel**
increments. The same height is encoded by every correlated row resource below.

`CMenuList` also constructs six `eCText` objects (vtable `0x7BE340`) at
vertical origins `0,24,48,72,96,120`, each with a 160x24 presentation
rectangle, plus bitmap/background objects. Those text controls all reference the
runtime font object at `0x87BEA0`.

The exact source font file, native text colors, clipping and all row-state
meanings are still open. The reconstruction must not substitute a modern font
or name atlas frames from appearance alone.

## Exact original row resources

Four original files are now bound end-to-end from literal path -> resource
loader -> wrapper -> concrete PMenu row class.

### Child-row arrow/status strip

`FM2001_Art/Generic/menu_popup/menu_anim.444`

- literal VA: `0x837C20`;
- loader: `0x5FAB10 -> 0x64D750`;
- raw handle: `0x9438B0`;
- wrapper setup: `0x5FAB60 -> 0x64E500`;
- wrapper: `0x943890`;
- consumer: `PChildMenuRow::0x47A990` at `0x47AA06`;
- exact file bytes: 22,768;
- source geometry: 30x667 = **23 x 29-pixel rows**;
- SHA-256:
  `de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22`.

### Title-row arrow/status strip

`FM2001_Art/Generic/menu_popup/menu_arrow_anim.444`

- literal VA: `0x837C4C`;
- loader: `0x5FABA0 -> 0x64D750`;
- raw handle: `0x943870`;
- wrapper setup: `0x5FABF0 -> 0x64E500`;
- wrapper: `0x943850`;
- consumer: `PTitleMenuRow::0x47A7E0` at `0x47A856`;
- exact file bytes: 26,248;
- source geometry: 30x638 = **11 x 58-pixel animation frames**; Recovery 148 corrected the earlier provisional 22x29 interpretation by tracing the source-offset/frame-count methods;
- SHA-256:
  `45d34aea3d4ae3f85a171fe3e6eb1b28ea960f5f500f123d98bcbbab52d22006`.

### Title-row background strip

`FM2001_Art/Generic/menu_popup/submenu_main_box.444`

- literal VA: `0x837C80`;
- loader: `0x5FAC30 -> 0x64D750`;
- raw handle: `0x943830`;
- wrapper setup: `0x5FAC80 -> 0x64E500`;
- wrapper: `0x943810`;
- consumer: `PTitleMenuRow::0x47A7E0` at `0x47A907`;
- exact file bytes: 5,700;
- source geometry: 168x87 = **3 x 29-pixel rows**;
- SHA-256:
  `37bc920cb734cde0ac8891d240341f06319c4d1827cdd03a9c4ef8137e30791c`.

### Child-row background strip

`FM2001_Art/Generic/menu_popup/menu_main_box.444`

- literal VA: `0x837CB4`;
- loader: `0x5FACC0 -> 0x64D750`;
- raw handle: `0x9437F0`;
- wrapper setup: `0x5FAD10 -> 0x64E500`;
- wrapper: `0x9437D0`;
- consumer: `PChildMenuRow::0x47A990` at `0x47AAB7`;
- exact file bytes: 6,864;
- source geometry: 168x116 = **4 x 29-pixel rows**;
- SHA-256:
  `4cc1becee669f1f55749a58051eca8833ed582b1f45754c18485366dd6715007`.

A separate `menu_anim_disabled.444` file and
`GenericButtonsAndBars/menu_arrow.444` were also found and hash-checked
privately, but their PMenu-row ownership/state meaning is **not** yet proven.
They are intentionally excluded from the guarded PMenu resource set.

## Static menu-node representation

`0x60C9C0` constructs one 24-byte menu node:

```text
+0x00 = zero/runtime state
+0x04 = label object/global
+0x08 = auxiliary resource/string object
+0x0C = menu/panel ID
+0x10 = child-array pointer
+0x14 = zero/runtime flags
```

`0x60C9F0` writes the terminating node. `0x60CB60` recursively searches by
the `+0x0C` ID. `0x60CA20` and `0x60CA30` resolve the label and auxiliary
members respectively.

The main root array is `0x947638`, in exact construction order:

| Root ID | Label global | Child array | Exact caption status |
| ---: | ---: | ---: | --- |
| 2 | `0x98475C` | `0x9479C8` | English.idx 39 = **Team** |
| 3 | `0x982298` | `0x947968` | unresolved label global |
| `0x259` | `0x982B1C` | `0x947728` | unresolved label global |
| 6 | `0x982098` | `0x947830` | unresolved label global |
| 7 | `0x98474C` | `0x9477D0` | English.idx 43 = **Analysis** |
| 4 | `0x982094` | `0x9478D8` | unresolved label global |
| 5 | `0x98209C` | `0x947878` | unresolved label global |
| 1 | `0x984748` | `0x947A70` | English.idx 44 = **EAMail** |
| 8 | `0x9820A0` | `0x947770` | unresolved label global |

The main English loader maps entry N to
`0x9847F8 - 4*N`. Only labels satisfying that exact loader/global relation
are promoted as captions.

### Team children, array 0x9479C8

IDs in order:
`0xCE, 0xCA, 0xCB, 0xCC, 0xCD, 0xCF`.

Exact correlated child captions currently include:

- `0xCA`: English.idx 48 = **Stats**;
- `0xCC`: English.idx 53 = **Team Orders**;
- `0xCD`: English.idx 54 = **Training**;
- `0xCF`: English.idx 59 = **Youth Team**.

The fresh PMenu route independently maps `0xCE` to `PSquadScreen`, but its
row caption global `0x982918` is not yet language-correlated.

### Transfer-family children, array 0x947968

IDs: `0x12D, 0x12E, 0x12F`.

Their row-label globals remain unresolved. The panel factory independently uses
the exact main-English **Transfer** heading for this family, and `0x12E`
constructs `PScouting2K`; neither fact licenses guessing the three row
captions.

### Direct 0x259 family, array 0x947728

IDs: `0x259, 0x25C`.

Both row-label globals remain unresolved.

### Tables children, array 0x947830

- `0x25A`: English.idx 71 = **League Tables**;
- `0x25B`: English.idx 72 = **Cup Tables**.

`0x25A` is independently proven to construct `PLeagueTables` in the
management-shell route trace. The root ID 6 caption global itself is not yet
language-correlated and is therefore not forced to the nearby word "Tables".

### Analysis children, array 0x9477D0

IDs: `0x2BD, 0x2BE, 0x2BF`.

The root caption is exactly **Analysis**, but these child-label globals are not
members of the main-English global sequence and remain unresolved. Nearby
English strings such as Ratings/Trophy Room/Match Archive are not accepted as
bindings without the missing initializer/use correlation.

### ID-4 family, array 0x9478D8

IDs: `0x191..0x195`.

Exact language-correlated rows:

- `0x193`: English.idx 67 = **Stadium**;
- `0x194`: English.idx 68 = **Development**;
- `0x195`: English.idx 69 = **Maintenance**.

The corresponding factory family uses the exact **Admin** panel heading, but
the root ID-4 row label global `0x982094` remains unresolved.

### ID-5 family, array 0x947878

- `0x1F5`: English.idx 60 = **Cash Flow**;
- `0x1F6`: English.idx 62 = **Tickets**;
- `0x1F7`: English.idx 63 = **Contracts**.

The root caption remains unresolved.

### EAMail child, array 0x947A70

One child:

- `0x65`: English.idx 44 = **EAMail**.

### ID-8 family, array 0x947770

IDs: `0x321, 0x322, 0x323`.

All three row captions remain unresolved. `0x323` is independently the proven
`PStartMenu` screen ID, but that does not identify its PMenu row caption.

## Separate source-proven team-order array

Array `0x9475A0` exists outside the proven main root tree ownership:

- `0x3E9`: English.idx 47 = Formation;
- `0x3EA`: English.idx 48 = Stats;
- `0x3EB`: English.idx 51 = Ind Orders;
- `0x3EC`: English.idx 52 = Specific Roles;
- `0x3ED`: English.idx 53 = Team Orders.

Its exact owning navigation edge remains open, so it is retained separately
rather than inserted into the main PMenu hierarchy by assumption.

## Reconstruction consequence

`reconstruction/original_pmenu_chrome.py` now guards:

- the concrete PMenu row-class identities and setup addresses;
- the 29-pixel native row geometry;
- the four exact source-correlated row resources and hashes;
- the nine-root static menu order and child arrays;
- only the English captions that have exact loader/global correlation.

This is enough to build a faithful resource-backed PMenu hierarchy skeleton
without inventing category names.

It is **not** enough to claim finished management presentation. Remaining PMenu
work includes:

1. recover the unresolved non-main-English label globals;
2. identify the exact source font behind runtime handle `0x87BEA0`;
3. recover text origin/color/clipping and row selection/hover/disabled state-to-
   frame transforms;
4. trace the exact PMenu shell background/chrome around the row list;
5. provenance-import only the four already-correlated source assets (and later
   assets only after their ownership is proven);
6. execute integrated Windows graphical validation after the corrected first-
   screen audit.

No original resource bytes are added by this checkpoint itself.

## Recovery 145 private source validation

Before this checkpoint was proposed for merge, the four selected files were
re-read from the freshly staged authorized source outside Git. All four matched
the byte lengths, SHA-256 values, source dimensions and original
`64 ff 00 ff` EA444 descriptor recorded above. Their heights divided exactly
into the expected 29-pixel row stacks (22, 3, 23 and 4 respectively).

This private validation proves the selected bytes match the source contract; it
does not replace hosted regressions or authorize any uncorrelated neighboring
asset.


## Recovery 146 label, font, color and background-state closure

The first PMenu checkpoint deliberately left later label globals unresolved
because the early English loader prefix looked like a simple descending global
array. Recovery 146 traced the **entire** main language loader instead of
extending that pattern by assumption.

### Complete English loader correlation

The loader region `0x635F30..0x64C7D4` contains exactly **2,714** calls to
the string-assignment routine `0x64E320`. That count exactly matches the
2,714 uint16 entries in the canonical 5,428-byte `English.idx`.

Each call site carries the destination global explicitly. Early assignments
reproduce the already verified mapping, including:

- entry 39 -> `0x98475C` -> `Team`;
- entry 43 -> `0x98474C` -> `Analysis`;
- entry 44 -> `0x984748` -> `EAMail`.

Later PMenu globals are therefore resolved by their exact loader assignment,
not by extrapolating the early address pattern.

The nine root captions are now source-exact:

| Menu ID | English.idx | Original caption |
| ---: | ---: | --- |
| 2 | 39 | Team |
| 3 | 2392 | Transfers |
| `0x259` | 1847 | Calendar |
| 6 | 2520 | TABLES |
| 7 | 43 | Analysis |
| 4 | 2521 | ADMIN |
| 5 | 2519 | ACCOUNTS |
| 1 | 44 | EAMail |
| 8 | 2518 | GAME OPTIONS |

The modeled child labels are also now exact:

- Team: `Squad`, `Stats`, `Indiv. Orders`, `Team Orders`,
  `Training`, `Youth Team`;
- Transfers: `Transfer List`, `Scouts`, `Player/Club Search`;
- Calendar: `Calendar`, `League Fixtures`;
- TABLES: `League Tables`, `Cup Tables`;
- Analysis: `Charts`, `RATINGS`, `Trophy Cupboard`;
- ADMIN: `Overview`, `Support Staff`, `Stadium`, `Development`,
  `Maintenance`;
- ACCOUNTS: `Cash Flow`, `Tickets`, `Contracts`;
- EAMail: `EAMail`;
- GAME OPTIONS: `SAVE GAME`, `SETTINGS`, `RETURN TO MAIN MENU`.

The separate `0x9475A0` array remains outside the proven main-tree ownership,
but its already-correlated captions remain Formation, Stats, Ind Orders,
Specific Roles and Team Orders.

`reconstruction/original_pmenu_chrome.py` now uses an exact sparse
English-entry -> destination-global map for every modeled PMenu label. The old
simple-address formula is deliberately removed because it is only true for the
early loader prefix.

### Exact PMenu font

Static initialization at `0x603640` wraps font object `0x9269F0` in the
runtime object referenced at `0x87BEA0`.

The canonical font loader at `0x604252..0x60429F` binds that object to:

`Fonts/Zurich_BdXCn_BT_16pixel.fnt`

- path literal: `0x839F24`;
- file size: **79,722 bytes**;
- SHA-256:
  `9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`;
- native atlas: **1526x17**;
- source line height through the recovered EA font parser: **18 pixels**.

This exact authorized font is already provenance-imported at
`original_assets/source/Fonts/Zurich_BdXCn_BT_16pixel.fnt`, so PMenu can reuse
the existing source file rather than adding a duplicate.

### Row color components

Both `PTitleMenuRow::0x47A7E0` and `PChildMenuRow::0x47A990` build the same
two RGB-component triples before background/text setup:

- `(0, 0, 0)`;
- `(255, 255, 255)`.

Because all three components are equal in each tuple, this evidence does not
depend on guessing the display backend's component ordering.

### MenuBackgroundToggle state -> source row

RTTI identifies `MenuBackgroundToggle` at vtable `0x7C3AE0`.
Its state-selection override at `0x47AC00` uses three neutral source bits:

- bit 1: `0x2`;
- bit 3: `0x8`;
- bit 15: `0x8000`.

The exact source-row index is:

```text
if bit 1 is clear:       3
else if bit 15 is set:   2
else if bit 3 is set:    1
else:                    0
```

With the source-proven 29-pixel row height, the corresponding source y offsets
are `87, 58, 29, 0` respectively. Bit 15 has precedence over bit 3.

The bit semantics remain deliberately unnamed. In particular, this checkpoint
does **not** equate the bits with modern hover/down/disabled names.

The title background atlas has only three physical rows. Therefore a computed
row index 3 for the bit-1-clear path must not be interpreted as an in-bounds
draw until the surrounding visibility/draw path is traced. The clean-room
contract records the source arithmetic without fabricating rendering behavior.

### Remaining PMenu presentation boundary

Closed by Recovery 146:

- all modeled root/child captions;
- exact 16px Zurich font identity and reusable imported bytes;
- native black/white component tuples;
- `MenuBackgroundToggle` neutral state-bit -> row-index transform.

Still open:

1. `MenuTitleArrow::0x4825A0` animation/state-to-frame behavior for the
   22-row title arrow strip;
2. child-arrow state/frame behavior for the 23-row child strip;
3. exact clipping/text-origin behavior beyond the recovered control rectangles
   and font metrics;
4. PMenu shell/background resource ownership around the menu list;
5. intentional provenance import of the four already-correlated menu-popup
   `.444` assets;
6. corrected real-Windows/Tk integration validation.

No new proprietary resource bytes are added by this label/font/state checkpoint.


## Recovery 148 arrow animation and shell-background ownership closure

The remaining title/child arrow question was traced through the shared bitmap
animation engine rather than inferred from atlas height.

### Shared neutral animation state

Both arrow objects inherit the source animation state machine around
`0x652780..0x6528C3`.

`0x652AE0` maps the neutral source bits to one of three state indices:

```text
bit 0x2 clear        -> state 2
bit 0x2 set and
  bit 0x8000 set     -> state 1
otherwise            -> state 0
```

These states remain deliberately unnamed. No hover/down/disabled semantic names
are introduced.

When a state changes, `0x652780` carries the current animation position by
integer division:

```text
new_frame = floor(new_state_frame_count * old_frame / old_state_frame_count)
```

Then `0x6527F0` performs one tick. Source bit `0x8` controls direction:

- bit `0x8` set: increment frame if another frame exists;
- bit `0x8` clear: decrement toward frame zero.

Again, that bit is retained by position only rather than named as a UI event.

### Child arrow: exact 23-row partition

The child arrow uses the generic source-offset method `0x652860` and frame-count
override `0x5D62F0`.

Frame counts by state are exactly:

```text
state 0 -> 11
state 1 -> 11
state 2 -> 1
```

The generic source-offset method concatenates lower-state frame ranges before
the current frame. Therefore `menu_anim.444` (30x667) partitions exactly as:

- rows 0..10: state 0;
- rows 11..21: state 1;
- row 22: state 2.

At 29 pixels per row, the full 23-row strip is accounted for with no unused or
invented frames.

### Title arrow: 11 frames at 58 pixels

`MenuTitleArrow` overrides both the source-offset method and frame count:

- source-offset override: `0x4825A0`;
- frame-count override: `0x5D50E0`.

Its counts are:

```text
state 0 -> 11
state 1 -> 1
state 2 -> 1
```

The resource is 30x638. The source frame height is therefore **58 pixels** and
the strip contains **11 physical frames**, not 22 independent 29-pixel rows.
This correction follows the actual source-offset multiplication and exactly
accounts for 638 pixels: `11 * 58 = 638`.

The custom source-row policy is:

- state 0: current frame 0..10;
- state 1: fixed physical frame 10;
- state 2: fixed physical frame 0.

The state-1/state-2 meanings remain unnamed. The result is an exact rendering
index contract without speculative interaction labels.

### PMenu shell/background ownership boundary

`PMenu::0x47AB40` initializes the embedded `CMenuList` at object offset
`+0x68`. Its raw list-setup vcall arguments are preserved as:

```text
(0, 0, 201, 504, 16, 29, 0, 0, 0)
```

The PMenu constructor/setup and bounded PMenu method range reference the static
menu tree at `0x947638` but **no direct 0x94xxxx original-resource handle**.
The concrete original menu graphics remain owned by the title/child row setup
methods documented above.

This is a negative ownership boundary, not proof that no background is visible
on screen. Any surrounding background may belong to an inherited/application
presentation layer. A distinct PMenu-specific background image must not be
invented unless a later owner/resource trace proves one.

### Reconstruction consequence

`reconstruction/original_pmenu_chrome.py` now guards the exact neutral state
selector, proportional transition arithmetic, per-state frame counts, one-tick
advance/retreat behavior and source-row selection for both arrow types. It also
corrects the title-arrow resource to 11 native 58-pixel frames.

Still open after this closure:

1. exact higher-level semantic names for the neutral animation bits/states, if
   they can be proven from input/event ownership;
2. remaining text clipping/origin details beyond the already recovered control
   rectangles/font metrics;
3. intentional provenance import of the four correlated menu-popup `.444`
   assets once binary Git transport is available;
4. corrected real-Windows/Tk integration validation of the current TeamSelect
   and PMenu behavior;
5. downstream normal-management panel composition/navigation required by Gate 13.

## Recovery 164 exact asset import

The four source-bound menu-popup assets are now intentionally imported under
their original paths in `original_assets/source`. The importer reverified each
file against the exact-path private selection report and canonical source ZIP
SHA-256 `677dcbc...a8a4`. `validate_original_pmenu_resources` now passes against
the tracked bytes, including native geometry and frame partition checks. No
neighboring or filename-only menu asset was imported.

## Recovery 166 visible-row order and fresh-route closure

A fresh checksum-gated private trace of the canonical executable
(`833bf95e...b7cc3`) closed the PMenu composition facts needed by the first
ordinary-management seam. The generated disassembly report remains outside
Git at `work/fm2001-private-gate13/pmenu-integration-recovery166.json`.

`PMenu::0x47AB40` configures its list as **201x504**, with **16** row slots and
a **29-pixel** step. The visible-row layout at `0x482300` assigns each emitted
row the current top/bottom pair and advances the next origin by exactly
`0x1D`. The factory at `0x4823A0` chooses `PTitleMenuRow` when the source node's
`+0x10` child-array pointer is nonzero and `PChildMenuRow` otherwise.

The ordinal tree walker at `0x60CA70` is root-first. It emits a node, descends
into its child array when the bit-0 open path permits it, then continues to the
next 24-byte sibling. The state/open flags live at node `+0x14`; this checkpoint
retains bit 0 only as the selected-or-expanded bit proven by its use, without
naming the still-neutral bit-1 behavior.

The fresh route in the `0x482A00` control-flow region looks up child `0xCE`
(`Squad`) and root `2` (`Team`), then sets bit 0 on both before panel creation.
The resulting exact 15-row order is:

```text
Team
  Squad
  Stats
  Indiv. Orders
  Team Orders
  Training
  Youth Team
Transfers
Calendar
TABLES
Analysis
ADMIN
ACCOUNTS
EAMail
GAME OPTIONS
```

The state-1 return route similarly looks up child `0x25A` (`League Tables`)
and root `6` (`TABLES`).

`reconstruction/original_pmenu_presenter.py` now projects this source-proven
one-root-expanded ordering, exact row geometry, labels, font identity and
title/child resource identities. It fails closed on non-recovered child IDs or
an expansion exceeding the native 16-row capacity. It does not invent the
remaining exact text origin/clipping behavior. The focused chrome/presenter
suite passes **23 tests**.

### Recovery 166 application-owned screen placement

A raw rel32 scan (used because linear disassembly skipped one exception-framed
call site) finds the only direct `PMenu` constructor call at `0x4C2FF8` inside
the application owner routine beginning at `0x4C2FB0`. Immediately after
construction, the owner calls the shared panel-layout method at `0x4C301F`
with the exact rectangle:

```text
x=599, y=96, width=201, height=504
```

This matches the independently recovered `CMenuList` local size exactly. The
fresh `PSquadScreen` factory branch for ID `0xCE` begins at `0x47AF2D` and calls
the same layout method at `0x47AF80` with:

```text
x=0, y=79, width=800, height=520
```

The overlap is native: PMenu occupies the rightmost 201 pixels over the full
Squad panel. These coordinates close the parent placement needed for an
800x600 composition. They do not establish a new PMenu-specific background;
the earlier negative resource-ownership boundary still applies. Exact label
origin/clipping and a source-backed surrounding background remain open, so a
finished pixel renderer is not yet claimed.
