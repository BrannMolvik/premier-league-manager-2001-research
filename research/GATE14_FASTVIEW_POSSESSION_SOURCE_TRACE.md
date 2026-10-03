# Gate 14 FastView possession source trace

_Date: 3 October 2026 KST. Recovery 194. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace closes the exact source identity of the bounded
`PossessionFigures` / `PossessionDiagram` resource family and the
`PossessionDiagram` geometry plus one-call state transition primitive. It
does **not** claim the original update cadence, side-0/user screen orientation,
commentary/audio binding, or broader FastView/3D choreography.

Gate 13 remains the earliest incomplete validation gate because its fresh
schema-8 real-Windows receipt is still external.

## Source revalidation

The authorized Library ZIP from `research/ORIGINAL_SOURCE_LOCATOR.md` was
rematerialized at exactly **511,121,336 bytes**. Its nested
`famg2001.bin` is **631,627,248 bytes**.

A fresh independent MODE1/2352 + Joliet level-3 scan reproduced the durable
source inventory exactly:

- **2,456 files**;
- **211 folders** excluding the root;
- canonical root `footballmanager.exe` SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This means the earlier Recovery-184 process-start blocker is no longer current
for this worker.

## Exact FastView resource paths

The canonical executable contains the complete FastView source paths, not only
basenames. Recovery 198 corrects one earlier ownership assumption: the three
82×16 bar files adjacent to the FastView constants are **not**
`PossessionFigures` controls. Their consumer is the separate
`FastViewPanel::FastViewTeam` / `TeamTable` construction path at
`0x524920 -> 0x524A20 -> 0x524EC0`. RTTI proves vtable `0x7CA888` as
`FastViewTeam@FastViewPanel` and vtable `0x7CA950` as its nested
`TeamTable`. The `PossessionFigures` constructor remains the separate
`0x51E7E0` text-only component.

The relevant image-path string addresses are:

| Component | Executable VA | Exact original source path | Bytes | Dimensions | SHA-256 |
| --- | ---: | --- | ---: | ---: | --- |
| FastViewTeam | `0x8293D4` | `FM2001_Art/FastView/team_bar_1.444` | 2,344 | 82×16 | `edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d` |
| FastViewTeam | `0x8293B0` | `FM2001_Art/FastView/blank_bar.444` | 2,776 | 82×16 | `961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a` |
| FastViewTeam | `0x829334` | `FM2001_Art/FastView/team_bar_2.444` | 2,312 | 82×16 | `4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751` |
| PossessionDiagram | `0x8298D4` | `FM2001_Art/FastView/pitch_left.444` | 9,736 | 125×78 | `bf1cf154f9742b39953771a248c7d1269d8d0394856ab1dc76dd81882b1b29d9` |
| PossessionDiagram | `0x8298AC` | `FM2001_Art/FastView/pitch_middle.444` | 7,896 | 98×78 | `ad53294836bf1f489060e9339da79fa43f2fb70034c890ea93dbff14f5caee77` |
| PossessionDiagram | `0x829888` | `FM2001_Art/FastView/pitch_right.444` | 9,408 | 125×78 | `dedc194dc9410ddc6d606fdabd3fe779a0c1bf0bfdfe85752f9a56d57171e5fd` |
| PossessionDiagram | `0x8298F8` | `FM2001_Art/FastView/pitch_normal.444` | 18,424 | 294×78 | `326f484f264630d656e47aee1eb8419970ddbf336fbbc4e47588ff841a346ced` |

The important collision is `pitch_normal.444`. The source disc also contains:

`FM2001_Art/Generic/match_report/pitch_normal.444`

That distinct 15,932-byte 294×78 asset hashes to
`73f6c0ecc57a383c63288064c371f947772f584800dfd3f4d2b1323063d9a6ba`.
The executable separately embeds that Generic path, while the
`PossessionDiagram` string is explicitly
`FM2001_Art\FastView\pitch_normal.444`. Therefore the old basename-only
ambiguity is now source-resolved without guessing from directory names.

`reconstruction/gate14_fastview_resource_catalog.py` schema 2 matches these
source-proven full paths and fails closed on a missing path, wrong source size,
or conflicting observed SHA-256. A same-basename file elsewhere cannot
substitute for the exact FastView path.

## PossessionDiagram construction and geometry

The FastView owner call at `0x5206CD` invokes constructor `0x5227D0` with:

- parent = the live FastView panel;
- x = `0xFD` = **253**;
- y = `0x8B` = **139**.

The normal pitch child therefore uses the exact rectangle:

`(253, 139) -> (547, 217)`

matching its 294×78 source image.

The object initializes state `+0x0C = 1`. The three territory overlays use
state indices 0/1/2 and source widths 125/98/125. The active x-offset table at
`0x829328` is exactly:

`[0, 98, 169]`

so the active on-screen overlay rectangles are:

- state 0 / `pitch_left.444`: `(253,139)-(378,217)`;
- state 1 / `pitch_middle.444`: `(351,139)-(449,217)`;
- state 2 / `pitch_right.444`: `(422,139)-(547,217)`.

The constructor initially leaves the middle overlay at its active location and
parks the left and right overlays at x = **4000**. State setter `0x522B40`
moves the previous overlay back to x=4000 and places the selected overlay at
the normal pitch x plus the three-entry source table above.

This recovers pixel placement for this bounded component. It does not establish
which match side is visually intended as the user's left/right orientation.

## Territory-driven update primitive

Update method `0x522BB0` reads EventPossession byte `+0x0C`, already
represented by modern `PossessionRecord.territory` in the 0..100 range.

It calls private presentation RNG `0x5227A0`. That routine updates static
state `0x8777F4` with:

`state = (214013 * state + 2531011) mod 2^32`

and returns:

`rand15 = (state >> 16) & 0x7FFF`

The canonical image initializes that static state to zero. A literal-reference
scan found the load/store inside `0x5227A0` as the only direct executable
references to `0x8777F4`; no separate seed semantic is claimed.

The compiled reciprocal-multiply sequence in `0x522BB0` is exactly equivalent
to `floor(rand15 / 327)` for all 32,768 possible 15-bit outputs, yielding a
roll in 0..100.

For one source call:

1. if `roll <= territory` and current state is below 2, increment the state;
2. otherwise, decrement the state when it is above 0;
3. state 0 therefore clamps on a failed roll;
4. state 2 takes the fallback decrement branch even when the roll succeeds.

`reconstruction/gate14_possession_diagram.py` materializes only this exact
single-call primitive and the proven geometry. It deliberately does not decide
how often the original invokes the update method.


## Recovery 196: staged diagram art and PossessionFigures text geometry

The four source-closed PossessionDiagram files are now deliberately staged as
byte-identical authorized originals under `original_assets/source/FM2001_Art/FastView/`.
`reconstruction/original_fastview_possession_resources.py` verifies each file's
exact source path, byte count, SHA-256 and EA444 dimensions before exposing only
the proven base-pitch plus active-overlay rectangles. The caller must supply the
0/1/2 source state; the module does not invent update cadence.

Fresh static tracing also closes `PossessionFigures` text placement. FastView
owner call `0x520802` constructs `0x51E7E0` at **(311,181)**. The constructor
creates three 40x18 text controls, and receiver `0x51EA80` maps the exact
EventPossession byte accessors as follows:

- side 1, byte `+0x0F` / accessor `0x51A720`: **(311,181)-(351,199)**;
- neutral, byte `+0x0E` / accessor `0x51A710`: **(382,181)-(422,199)**;
- side 0, byte `+0x0D` / accessor `0x51A700`: **(454,181)-(494,199)**.

All three are formatted by the source `%u%%` format at `0x82924C`.
`reconstruction/gate14_possession_figures.py` preserves this side-indexed
left/center/right mapping and deliberately does **not** rename either side as
the human team. This closes screen placement of the percentage text without
claiming user-side orientation.

## Recovery 198: typed receiver lifecycle

The bounded diagram is not an independently polled widget. Its constructor
produces three receiver subobjects and the FastView owner registers all three
immediately after storing the new object at panel `+0x420`:

- primary vtable `0x7CA87C`: `Receiver<EventPossession>`, callback
  `0x522BB0`;
- subobject `+0x04`, vtable `0x7CA870`: `Receiver<EventGoal>`, callback
  `0x522C30`;
- subobject `+0x08`, vtable `0x7CA864`:
  `Receiver<EventGlobalPenalties>`, callback `0x522C60`.

The exact receiver effects are now source-closed:

1. `EventPossession` normally performs the already documented one-call
   territory/RNG transition.
2. `EventGlobalPenalties` sets the diagram's byte at overall object
   `+0x20` to one. It does **not** immediately move the overlay.
3. Once that byte is set, every later `EventPossession` returns through the
   early branch after forcing state **1**, without calling the private
   presentation RNG.
4. `EventGoal+0x0C == 0` snaps the diagram to state **2**;
   `EventGoal+0x0C == 1` snaps it to state **0**; other values leave the
   current state unchanged. No side/user meaning is assigned to that field.

`reconstruction/gate14_possession_diagram.py` now exposes these three typed
event reactions separately. This closes the diagram's receiver lifecycle but
does **not** establish how often the match controller emits
`EventPossession`; emission cadence remains a distinct fail-closed boundary.

## Remaining boundary

Still open before claiming the bounded diagram is player-visible original
FastView behavior:

1. recover the original `EventPossession` emission cadence and any process/match lifecycle reset semantics for the private presentation RNG;
2. recover side-0/user orientation rather than inferring it from
   `left/middle/right` filenames;
3. keep the three 82×16 `team_bar_1` / `blank_bar` / `team_bar_2` assets under
   the separately proven `FastViewTeam` / `TeamTable` ownership. They must not
   be wired into `PossessionFigures`; percentage text placement is already exact;
4. connect the source-bounded diagram/text geometry to a player-visible
   FastView surface only after its missing lifecycle/orientation boundaries are
   resolved or explicitly fail-closed;
5. recover audio/commentary and broader FastView/SCI choreography separately.

No unresolved timing or orientation is described as original behavior by this
checkpoint.
