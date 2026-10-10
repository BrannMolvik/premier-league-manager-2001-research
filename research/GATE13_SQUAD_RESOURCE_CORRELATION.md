# Gate 13 Squad Resource Correlation

_Date: 1 October 2026 KST_

## Evidence boundary

This report records the canonical-executable owner correlation for the four
exact files returned by the whole-disc Squad catalog query. The authorized ZIP
matched SHA-256
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4` and
the private `footballmanager.exe` matched
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
before the trace. Private exhaustive disassembly reports remain outside Git.

Filename and directory similarity were not treated as ownership. Each result
below requires the exact path literal, the loader/wrapper chain, a code
consumer, and an RTTI-backed owner where applicable.

## Exact catalog and loader bindings

| Exact source path | SHA-256 | Native size | Path literal / load thunk | Raw handle -> wrapper |
| --- | --- | --- | --- | --- |
| `FM2001_Art/Coaching/squad/blue_toggle.444` | `3fe515f5a4a2d798a8f62917a45047b274e08bd3e68147a4fe0e25dfbd1d3343` | 22x17 | `0x83827C` / `0x5FBDD4` | `0x943070` -> `0x943050` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_bars.444` | `c0ba37cc991e5449830af3e550f14dc7d9444cc545e91fa7936dc38508c6110b` | 81x64 | `0x8394B8` / `0x5FF7F4` | `0x941750` -> `0x941730` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_but_anim.444` | `6a5180d9212fe50418537fa181c44ba075bc0317c5bb55aed8b9c6a9e0fc0632` | 73x575 | `0x83943C` / `0x5FF6D4` | `0x9417D0` -> `0x9417B0` |
| `FM2001_Art/Generic/GenericButtonsAndBars/squad_form_anim.444` | `e4bcc6981cc99fde44b093696791a05f91100752559b0b2f12dc0c0177392828` | 23x368 | `0x839478` / `0x5FF764` | `0x941790` -> `0x941770` |

All four load thunks call the established resource loader `0x64D750`. Their
wrapper initializers call `0x64E500`. The four files are now provenance-
imported individually under `original_assets/source/`; no archive, executable
or raw report entered Git.

## General Squad panel identity recovered

`squad_but_anim.444` supplies the decisive general-Squad binding:

- setup method `0x4B5720` is vtable slot 1 at `0x7C5CA8`;
- the vtable begins at `0x7C5CA4`, COL `0x7E5F00`;
- TypeDescriptor `0x819D48` names `.?AVPSquadScreen@@`;
- setup calls `0x652C50` with wrapper `0x9417B0` at exact origins
  `(37,92)`, `(113,92)` and `(189,92)`.

This is the first persisted proof of the distinct native `PSquadScreen` class.
The 73x575 atlas is retained intact. Its internal frame boundaries or user-
facing frame meanings are not inferred from height alone.

## Exact top-control bindings and captions

The same setup method registers the three adjacent controls through vtable
slot `+0x08` (`0x64F3C0`), which stores the supplied numeric control ID and
owner pointer. Their complete source bindings are:

| Control ID | Object offset | Origin | Label global | English.idx | Exact English text |
| ---: | ---: | ---: | ---: | ---: | --- |
| 3 | `+0x37A4` | `(37,92)` | `0x982110` | 2490 | `1ST & RES` |
| 4 | `+0x37F8` | `(113,92)` | `0x98210C` | 2491 | `1ST FORM` |
| 5 | `+0x384C` | `(189,92)` | `0x982108` | 2492 | `RES. FORM` |

The caption mapping is not inferred from visual order. Language loader
`0x635F30` begins its sequential two-byte `English.idx` reads at `0x635F56`.
Calls `0x64AA0E`, `0x64AA30` and `0x64AA52` are zero-based entries 2490,
2491 and 2492 and install those values into the three globals above. The
committed original `English.idx` / `English.str` pair resolves them to the
exact text shown.

The first control receives one distinct setup flag while the other two receive
zero. Its semantic name is not claimed, and no atlas row is labelled as a
normal, hover, pressed or selected state without a separate state transition
trace.

## Roster/pitch layout and control transitions

`PSquadScreen` embeds two `CBasePlayerList` instances (TypeDescriptor
`0x81DCB8`, vtable `0x7C5BC8`) and one `PSquadPitch`:

| Embedded object | Object offset | Initial rectangle `(x,y,w,h)` |
| --- | ---: | --- |
| first-team player list | `+0x130` | `(37,0,228,520)` |
| reserve player list | `+0x1030` | `(418,0,228,520)` |
| formation/pitch panel | `+0x1F30` | `(388,92,412,432)` |

The two player-list constructor calls at `0x4B82A4..0x4B82BA` pass exact
discriminators 0 and 1. Event handler `PSquadScreen::0x4B8E70` then switches
the container bindings directly from the now-proven control IDs:

| Control | Exact transition |
| --- | --- |
| 3 `1ST & RES` | bind the first-team list left and reserve list right; set native mask 1 on the second-list container and clear it on the pitch container |
| 4 `1ST FORM` | bind the first-team list left; clear native mask 1 on the second-list container, set it on the pitch container, and store pitch team index 0 |
| 5 `RES. FORM` | bind the reserve list left; clear native mask 1 on the second-list container, set it on the pitch container, and store pitch team index 1 |

The generic methods used here are `0x64F510` and `0x64F520`, which set and
clear control flag mask 1 through `0x64F3E0`. The durable contract retains the
neutral native-mask wording rather than assigning a broader UI meaning beyond
the proven container transitions.

## Exact `PSquadPitch` / formation-control geometry

RTTI proves setup method `0x4B3C80` is vtable slot 1 of `PSquadPitch`
(TypeDescriptor `0x81DB30`, vtable `0x7C54A8`). It constructs 22 paired
`FormationBtn` / `FormationText` pairs with consecutive control IDs 12..55:

- row `i` is at local y `25 + 17*i`, for `i=0..21`;
- the `squad_form_anim.444` control is `(279,y,23,16)`, ID `12+2*i`, object
  offset `+0x8C0 + 0x58*i`;
- the `squad_bars.444` control is `(303,y,81,16)`, ID `13+2*i`, object offset
  `+0x1050 + 0x58*i`.

The last row is therefore y=382 with IDs 54/55. Wrapper initializers
`0x5FF7B0` and `0x5FF840` independently pass frame sizes 23x16 and 81x16;
the geometry is not inferred merely by dividing atlas height. The 17-pixel row
step leaves one native pixel between adjacent 16-pixel rows.

## Formation resources

`squad_bars.444` is consumed by `FormationText::0x4B6B60`; the method forwards
caller-provided geometry into `0x652C50` with wrapper `0x941730`.
`squad_form_anim.444` is consumed by `FormationBtn::0x4B6C30`, which forwards
caller-provided geometry into `0x652CB0` with wrapper `0x941770`.

`FormationText` is independently identified by TypeDescriptor `0x81DBC0`, COL
`0x7E5BB8`, and vtable `0x7C5700`. `PSquadPitch` (TypeDescriptor `0x81DB30`,
vtable `0x7C54A8`) constructs a 22-element embedded `FormationText` array at
`0x4B5B18`. The separate form array is constructed by `0x4B5C20`, which
installs `FormationBtn` vft `0x7C5644`; its COL `0x7E5B58` resolves to
TypeDescriptor `0x81DBA0` (`.?AVFormationBtn@@`). The earlier shared-class
claim is superseded. These two resources therefore belong to the formation/pitch
presentation family, not automatically to the general roster panel.

## `blue_toggle.444` is shared, not `PSquadScreen` proof

The wrapper `0x943050` is consumed by four RTTI-owned setup methods:

| Setup | Vtable / TypeDescriptor | Owner |
| --- | --- | --- |
| `0x464400` | `0x7C1AB4` / `0x81C1C0` | `PFormation2k` |
| `0x48A590` | `0x7C47C8` / `0x81D380` | `PSCFTitle` |
| `0x4DB370` | `0x7C783C` / `0x81D270` | `PTraining` |
| `0x4E5F90` | `0x7C8650` / `0x81F378` | `PYouthTeam` |

No `PSquadScreen` setup reference to this wrapper was found. Its `Coaching/
squad` directory is therefore a shared-control provenance clue, not evidence
that the general Squad panel draws it.

## Durable implementation boundary

`reconstruction/original_squad_resources.py` fail-closes on the four hashes and
native `.444` header sizes, records the exact owner boundary, locks the three
recovered `PSquadScreen` controls, and resolves their captions from the
committed original language pair. It deliberately does not split either
vertical atlas, name native frame states, invent formation coordinates, or
claim the shared blue toggle for the general Squad screen.

## Concrete roster owner, rows and columns

The expanded private trace was rerun against the independently rehashed
canonical executable. Manual CFG/data-flow adjudication replaces the earlier
base-class-only description with the concrete native hierarchy:

| Class | TypeDescriptor | Vftable | Proven entry |
| --- | ---: | ---: | ---: |
| `PSquadList` | `0x81DC60` | `0x7C5864` | setup `0x4B4FE0` |
| `CSquadPlayerList` | `0x81DD00` | `0x7C5AF4` | player-row factory `0x4B7170` |
| `CSquadSCFList` | `0x81DC98` | `0x7C5968` | side-row factory `0x4B7240` |
| `PSquadPlayerRow` | `0x81DBE0` | `0x7C57BC` | setup `0x489530` |
| `PSCFRow` | `0x81D348` | `0x7C4720` | setup `0x489B40` |
| `PPlayerEmptyRow` | `0x81D2B0` | `0x7C46CC` | empty-row factory branch |
| `PSCFEmptyRow` | `0x81DC40` | `0x7C5810` | empty-row factory branch |

`PSquadList::0x4B4FE0` constructs exactly 20 visible row shells at local
y-origins 154..477 in 17-pixel steps. It owns a `CSquadPlayerList` at
`+0xE44` and paired `CSquadSCFList` at `+0xEA8`; discriminator byte `+0x98C`
selects first or reserve data and is passed into both lists.

The populated player row directly binds `(x,width)` columns: club-relative
assignment selector `(1,22)`, assigned role `(28,38)`, and formatted player
display name `(76,144)`. The paired side row binds a native status icon at
x=1, Condition `(24,19)` from `DBRPlayer+0x77`, six-entry recent-form average
`(47,19)`, and current assigned-role rating `(70,19)`. The status icon result
from `0x418330` selects a 32-byte entry in `0x87BBF0`; result -1 clears it.
Its user-facing category name remains deliberately unclaimed.

`CBasePlayerList::0x48B0D0` also proves the filter-mask-to-native-code map:
`0x1 -> 3`, `0x2 -> 0`, `0x4 -> 1`, `0x8 -> 2`. These remain neutral native
codes: no unsupported UI labels are attached. Both concrete factories emit
their empty-row class when the shared visible-row mapping returns -1.

## Exact distinct formation-control state-to-atlas transforms

**9 October independent correction:** the following `(2,1,1)` rule applies
only to the adjacent `FormationText` bar. Applying it to `FormationBtn` is
incorrect. Constructor `0x4B5C20` installs vft `0x7C5644`, whose `+0xA8`
is `0x652BC0`, returning `(11,1,1)`. The shared `0x5D4D70` source-offset
method calls that actual owner virtual. Its form rows are ordinary `0..10`,
selected `11` (y176), and disabled `22` (y352). Constructor `0x4B6B30`
installs the bar's `0x7C5700`, whose `+0xA8=0x4D8D30` returns `(2,1,1)`.
`original_squad_resources` now requires the explicit source-qualified class
for source-row/y selection, and the private source tracer includes both vfts.

Primary source review and independent canonical replay executed both actual
constructors and updater/offset virtuals: 6,656 form and2,048 bar cases, all
valid old group/subframes, all low8 flag combinations, selected8000 clear/set.
Synthetic owner/resource-wrapper dimensions and null invalidation callback are
explicit fixtures; no original process, live raster or visible acceptance.
Vector SHA256: form `fce4705d8dccc242a4ae311083225c01ec4f23bb81a4a5181b962feb22a5b2f6`;
bar `9c8f700bbf2c79600d4cf9a93dd9026ddc645c10f63aea80930eab9ffd639871`.
A targeted regression failed before the repair (`32 != 176`). Ordinary pitch
activation is still withheld until its complete producer/render/input path is
integrated. This is SOURCE-VERIFIED contract correction, not a playable view.

The generic transform is now source-bound rather than inferred from atlas
height. Vtable slot `+0xA8` (`0x4D8D30`) returns group lengths `(2,1,1)`;
slot `+0xAC` (`0x652AE0`) chooses group 2 when native mask `0x2` is clear,
group 1 when mask `0x8000` is set, otherwise group 0. Pointer-inside mask
`0x8` advances the group-0 subframe and pointer-out retreats it.

Slot `+0x98` (`0x5D4D70`) maps group 0 to source rows 0/1, group 1 to row 2,
and group 2 to row 4, then multiplies by the proven 16-pixel frame height.
`PSquadPitch::0x4B6910` calls the paired controls' state setter with 1 only
when all 11 formation positions are represented, setting mask `0x8000` and
therefore selecting row 2 (source y=32). An ordinary enabled row uses rows
0/1 for pointer-out/in.

The inherited mask-2-clear transform calculates row 4. That is outside the
four-row 81x64 `squad_bars.444` atlas, and no Squad runtime path clearing that
mask has been proved. It must therefore fail closed rather than inventing a
disabled bar. Bar row3 is not selected by this `FormationText` path. The form
atlas follows the separately verified `FormationBtn` rule above; its otherwise
unused rows receive no guessed meaning.

## Next action

Run the real Windows PStartMenu/TeamSelect graphical audit, then recover the
remaining TeamSelect native hierarchy input/state mapping. Continue the
management-screen correlations and presentation work only from executable,
resource, or direct graphical evidence. Gate 13 cannot close until the real
Windows source-backed audit passes.

## Recovery 164 cloud-safe row presentation seam

The already recovered row contract can now be consumed without private source
execution through `reconstruction/original_squad_presenter.py`.

The read-only management bridge exposes two values that were already
source-reconstructed in runtime code:

- the six-entry circular match-performance average used by the native
  `PSCFRow` recent-form field;
- the exact `0x41C7E0` rating for the player's currently assigned role.

The presenter maps only the proven row fields and local geometry:
assigned role at x=28/width 38, display name at x=76/width 144, Condition at
x=24/width 19, recent-form average at x=47/width 19 and current-role rating at
x=70/width 19, with the 20 native visible row origins 154..477 at 17-pixel
steps.

It deliberately leaves `club_relative_assignment` and `native_status_icon`
unresolved at the value layer, and refuses more than one 20-row viewport.
First/reserve membership, filtering/scrolling behavior and user-facing status
icon meanings therefore remain source-gated rather than inferred.

## Recovery 179 - fresh PSquadScreen top-control pixel closure

Recovery 179 reverified the canonical executable
`833bf95e...b7cc3` from the authorized source and followed the three
`PSquadScreen::0x4B5720` calls through the concrete embedded control class
instead of inferring atlas frames from appearance.

The three 0x54-byte objects are constructed by `0x42DEB0`, which installs
vtable **0x7BE814**. Their shared setup remains `0x652C50`. The one distinct
literal passed only for control 3 is not a text-layout flag: `0x652C50`
withholds that argument from the common `0x651E30` text setup and later passes
it through vtable `+0xB0 -> 0x652D80`. That method drives `0x652B10`,
which sets/clears source control mask **0x8000**.

The same concrete vtable supplies:

- state selector `+0xAC -> 0x652AE0`;
- state frame-count method `+0xA8 -> 0x652BC0`;
- source offset `+0x98 -> 0x5D4D70`.

With the normal initial enabled flags and zero subframe, the exact fresh state
is therefore:

| Control | Source state | Source frame | Native text endpoint |
| --- | ---: | ---: | ---: |
| 3 `1ST & RES` | group 1 / mask 0x8000 set | **11** | `0x0000` |
| 4 `1ST FORM` | group 0 | **0** | `0xFFFF` |
| 5 `RES. FORM` | group 0 | **0** | `0xFFFF` |

The 73x575 `squad_but_anim.444` atlas is thus source-partitioned into the same
23 physical 73x25 frames consumed by this concrete control path; this statement
comes from the executable source-offset/frame-count methods, not height division
alone.

### Caption geometry

All three calls use runtime font object `0x9269F0`, already source-bound to
`Fonts/Zurich_BdXCn_BT_16pixel.fnt`, and pass raw text style **0** with zero
x/y text offsets. The shared `0x6520C0` renderer's style-0 path centers the
measured line horizontally and the native 18-pixel line vertically in each
73x25 control. The exact English captions remain the loader-correlated entries
2490..2492 documented above.

Generic draw `0x6520C0` adds the parent draw origin to each stored child
coordinate. Therefore the three setup origins are **PSquadScreen-local**, not
final screen positions. With the independently recovered PSquadScreen parent
rectangle `(0,79,800,520)`, the fresh live screen origins are:

- control 3: **(37,171)**;
- control 4: **(113,171)**;
- control 5: **(189,171)**.

This parent-relative result also preserves the native alignment with the
`PSquadPitch` local y=92 boundary.

### Clean-room consequence

`reconstruction/original_squad_top_controls.py` now composes only these six
verified overlays: three exact source frames plus three original Zurich caption
masks. It does **not** render unrecovered roster typography/status icons or
invent a Squad background. The default host can use this bounded fresh landing
layer underneath PMenu while the rest of the Squad surface remains fail-closed.



## Recovery 332 — ordinary row text/color closure

Fresh canonical-executable analysis against SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
closes the previously deferred ordinary `PSquadPlayerRow` display-name and
assigned-role text path.

### Display-name helper and source colors

`PSquadPlayerRow::0x489530` calls `0x5D6C50` for the player-name control.
That helper resolves the player display string through `0x417AE0`, whose
style-0 result is first initial + `. ` + surname. A first-name string whose
first byte is `-` uses surname only.

The same helper checks four selection predicates in exact precedence order and
selects these source RGB8 values before the native packed-16 conversion:

- first-team active `0x417EE0`: `(255,255,255)`;
- first-team substitute `0x417F00`: `(232,191,94)`;
- reserve active `0x417EA0`: `(176,176,176)`;
- reserve substitute `0x417EC0`: `(185,167,131)`;
- otherwise: `(217,210,62)`.

The first-team pair is represented by the reconstructed gameplay model. The
reserve pair lives at native player `+0x174` bits 0/1 and is not currently
modeled. Therefore the clean-room presenter resolves active/substitute colors
when those higher-priority predicates prove the branch, and withholds name
pixels when neither first-team predicate applies and reserve state is unknown.
It does not fabricate the default yellow branch.

The row text font path is source-bound through runtime font slot `0x94758C`,
wrapper `0x87BE90`, base object `0x9197E0`, to
`Fonts/Zurich_BdXCn_BT_18pixel.fnt` (SHA-256
`4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd`).

PR #489 merged this first-roster player-name path at main
`1a24b456f763a8f8899b2eb940a8316bf35aef2b` after reconstruction
`37399160903`, Gate-13 `37399160894`, Windows package `37399160807`,
and repository asset-policy `37399160815` all passed.

### Assigned-role label and color

The same row setup obtains the current assigned role from `0x4EA3C0`, indexes
the runtime Position table at global `0x874B68` with 20-byte records, then
loads the text pointer at record `+0x0C` before constructing the centered
`(28,1,38,14)` control with raw text flags `0x24` and the same 18px Zurich
font.

Runtime record reader `0x401030` fills the 20-byte Position record in source
order: ID byte at `+0x04`, first localized string pointer at `+0x08`, second
localized string pointer at `+0x0C`, then bytes `+0x10` and `+0x11`.
The clean-room Static.dat parser reads the matching seven-byte source record as
ID, localized name ID, localized abbreviation ID, lineup order, lineup group.
Therefore the Squad control's `+0x0C` string is source-bound to
`Position.abbreviation`.

Color predicate `0x4EA3F0` compares the assigned role's low five-bit code with
the player's three preferred role bytes. A match selects source RGB
`(255,255,255)`; a mismatch selects `(0,0,125)`. Native packed-16 masks
remain a separate Windows/display receipt, so the modern renderer preserves the
recovered RGB8 intent without claiming RGB565 or RGB555.

The current Recovery-332 branch projects that original abbreviation from
`state.positions` and rasterizes the role control at the exact first-roster
geometry. Missing position-table identity or abbreviation fails closed.

## Recovery 334 - PSCFRow numeric text/color closure

Fresh private analysis re-extracted the canonical root `footballmanager.exe`
from the authorized MODE1/2352 disc and reverified SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The paired side-row path is now source-closed far enough to render its three
numeric controls without borrowing styling from `PSquadPlayerRow`.

`PSquadList::0x4B4FE0` constructs the paired `CSquadSCFList` at local
**x=239, y=154**, with the already proven 20-row viewport. Inside each populated
`PSCFRow::0x489B40`, the numeric controls are:

| Field | Row-local rect | Source value |
| --- | --- | --- |
| Condition | `(24,1,19,14)` | `DBRPlayer+0x77` |
| recent-form average | `(47,1,19,14)` | native six-entry average |
| current-role rating | `(70,1,19,14)` | current assigned-role rating |

All three route through numeric text helper `0x652400` with raw text flags
`0x24` (horizontal + vertical centering) and font object `0x8CAB80`.
**9 October correction:** the earlier 18px ownership claim was incorrect.
The sequential loader pushes the 16px path at `6044AC`, assigns ECX=`8CAB80`
at `6044F4`, and calls `657650` at `6044F9`. The following 18px block loads
**`8BD970`**, not `8CAB80`. The exact direct-owner resource is
`Fonts/Zurich_XCn_BT_16pixel.fnt` (75,217 bytes; SHA-256
`e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18`;
atlas 1261x17, native line height18).

Independent canonical re-execution/source challenge establishes that `604160`
is sequential, reached from `5310E6` after the display branches merge.
`6040B0` changes resolution-dependent aliases, not this direct font object.
PSCFRow, `48A590` headings, and application header controls
`4306D8/43075C/4307DA` pass `8CAB80` directly; they cannot use the neighboring
18px font. PMenu child labels already use the correct16px resource.

Implementation gate: the original draws these controls with the16px atlas;
the reconstruction's18px binding is a confirmed defect. Minimum repair is
the Squad/header font identity, size/hash/atlas guards and affected tests,
without changing rectangles, text styles, row membership or simulation.
Source identity is verified; actual Windows widget output is a separate check,
and visible/user acceptance is not inferred from static or bounded evidence.
Other font aliases and later-gate consumers are not certified by this repair.

The exact format strings are `%N` at `0x81ACAC` for Condition and role
rating, and `%.N` at `0x81B534` for recent form. In formatter
`0x655F40`, the `.` modifier maps through the `0x656194` dispatch table
to `0x6560E5`, setting the one-decimal flag. Helper `0x655EE0` implements
that flag by multiplying by 10, adding/subtracting 0.5 according to sign,
integer-converting, then multiplying by 0.1. The clean-room renderer therefore
uses whole decimal strings for Condition/rating and one-decimal, half-away-from-
zero rounding for recent form.

The canonical image stores dword **75** at condition-threshold global
`0x821814`. `PSCFRow::0x489D4D` takes the low-color branch on `<= 75`
and the high-color branch only on `> 75`. Native packed-color construction
resolves those source RGB inputs as:

- Condition `>75`: **(255,255,255)**;
- Condition `<=75`: **(0,45,255)**;
- recent form and current-role rating normal state: **(255,255,255)**.

Fresh generic controls initialize state bits to `0x183` at `0x64F300`;
therefore bit `0x4` is clear and `0x651F40` selects stored color `+0x44`,
the normal colors above. The alternate stored color is not promoted into an
independent user-facing state.

This closure does **not** resolve the x=1 native status icon, its category
meaning, or the player-row club-relative assignment selector. Those remain
fail-closed.

## Recovery 335 - PSCFRow status atlas and definition-table closure

Fresh canonical analysis binds PSCFRow status presentation to the original
resource string `fm2001_art\\generic\\status.png` at executable VA
`0x835D98`. Resource initialization `0x603940` loads that path into global
`0x946110` and materializes fourteen source entries beginning at
`0x87BBF0`, with 0x20-byte entry stride. The source asset is the byte-identical
18x196 RGB PNG now staged at
`original_assets/source/FM2001_Art/Generic/status.png`: 4,015 bytes, SHA-256
`59cd053c93ea789a010d813f46f650c2e4c16ea46163c63ae01209f69e4f5b1b`.
The initializer advances source Y by 14 for each entry, proving fourteen
vertical 18x14 frames.

The serialized player-status table begins at Static.dat `0x26F2`. Reader
`0x401310` builds the runtime table behind global `0x874B40`; the recovered
twelve source definitions are, in order:

1. Injured
2. Banned
3. International
4. Cup Tied
5. First Team
6. Subsitute
7. On loan
8. Out of contract
9. Transfer listed
10. Bid in
11. Wanted
12. Non EU

The misspelling `Subsitute` is present in the original English source and is
preserved as evidence rather than normalized.

`PSCFRow::0x48B8A0` calls resolver `0x418330`; its integer result is used
directly to select the corresponding 0x87BBF0 source entry, while -1 removes
the icon. Frames 0..11 therefore correspond to the ordinary definition-table
order. Native override helper `0x418360` additionally reaches frame 12 for a
special Non-EU registration state and frame 13 for an alternate On-loan state.

This does **not** yet justify a clean-room status renderer. The native resolver
can supersede ordinary fallback status with separate Cup-Tied collection state,
and the clean runtime currently has no exact materialized equivalent of that
collection or of the special Non-EU registration branch. Recovery 335 therefore
pins the exact source image/frame/table contract but deliberately leaves live
status selection fail-closed until those priority predicates are represented.



## Recovery 336 - direct PSCFRow status priority closure

Fresh canonical disassembly of the verified executable (SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`)
closes the direct-return portion of `0x418330`.

`0x401DE0` scans `DBRPlayer+0x14` status bits in ascending source-table
index order. It always skips index 3 (Cup Tied), and when called with the
nonzero PSCFRow context it also skips indices 4 and 5 (First Team and source-
spelled "Subsitute"). `0x418330` returns scan results `<=5` immediately and
only invokes override helper `0x418360` for later results or -1. Therefore
the only PSCFRow status results guaranteed to bypass every later override are:

- frame 0 / bit 0: Injured;
- frame 1 / bit 1: Banned;
- frame 2 / bit 2: International.

This source table identification supersedes the older neutral label
"selection-exclusion state" for bit 2. Cup-tie state remains separate, as
previously proven.

The lower-priority `0x418360` chain is now bounded as:

1. bit-6 loan state with `WORD +0x10 != WORD +0x72` -> alternate frame 13;
2. Non-EU bit 11 plus its separate registration-record date predicate -> alternate frame 12;
3. `0x418480` Cup-Tied predicate -> frame 3;
4. bit 15 -> frame 10;
5. bit 12 -> frame 6;
6. otherwise retain the fallback scan result.

The special Non-EU branch is backed by the separate collection at global
`0x876B30`: `0x41B4D0` resolves/creates the player record and `0x4E9BE0`
tests the global current date against record `+0x14`. The exact user-facing
meaning of that date is not promoted beyond this predicate.

`0x418480` reaches the competition Cup-Tied collection. Its lookup eventually
uses `0x4E9710(collection, player_id, team_id)`, which returns tied when the
same player has a stored club/team ID different from the team being checked.
The clean runtime does not yet materialize this collection, so all statuses
that enter `0x418360` remain fail-closed in the current presentation.

The PSCFRow status control itself is row-local `(1,1,18,14)`. Combined with
PSquadList first-roster x=37, paired CSquadSCFList local x=239, panel y=79 and
first visible row y=154, the first direct status frame is placed at screen
`(277,234)`. Recovery 336 renders only frames 0..2 from the byte-identical
original `status.png`; no lower-priority fallback is shown yet.
