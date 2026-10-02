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

## Exact `PSquadPitch` / `FormationText` geometry

RTTI proves setup method `0x4B3C80` is vtable slot 1 of `PSquadPitch`
(TypeDescriptor `0x81DB30`, vtable `0x7C54A8`). It constructs 22 paired
`FormationText` controls with consecutive control IDs 12..55:

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
`squad_form_anim.444` is consumed by `FormationText::0x4B6C30`, which forwards
caller-provided geometry into `0x652CB0` with wrapper `0x941770`.

`FormationText` is independently identified by TypeDescriptor `0x81DBC0`, COL
`0x7E5BB8`, and vtable `0x7C5700`. `PSquadPitch` (TypeDescriptor `0x81DB30`,
vtable `0x7C54A8`) constructs a 22-element embedded `FormationText` array at
`0x4B5B18`. These two resources therefore belong to the formation/pitch
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

## Exact `FormationText` state-to-atlas transform

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
disabled bar. Row 3 and the remaining rows of the 23-frame-high form atlas
are not selected by this `FormationText` path and receive no guessed meaning.

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

