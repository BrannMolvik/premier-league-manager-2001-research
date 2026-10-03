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

## Recovery 198: EventPossession emission cadence

The exact possession sender path is now located. `MatchIterator`'s primary
base is `Receiver<EventGlobalTick>`: construction temporarily installs the
base vtable `0x7CA24C`, then the final primary `MatchIterator` vtable
`0x7CA1DC`. Its GlobalTick callback is `0x519630`.

The unique direct construction of the bounded `EventPossession` object is
`0x5197B8 -> 0x51A6B0`, followed by iteration of the
`Sender<EventPossession>` receiver list at MatchIterator source offset
`+0x20`.

That branch executes only when all of these source conditions hold:

- MatchIterator byte `+0xA5 == 0`;
- MatchIterator pointer `+0x98` is non-null;
- MatchIterator pointer `+0xA0` is non-null;
- the first dword of the incoming `EventGlobalTick` is divisible by **5**.

Therefore the source cadence is **one EventPossession opportunity every fifth
EventGlobalTick while those gates hold**. This does not yet establish the
wall-clock duration of one GlobalTick and does not imply a per-frame or
per-second interval.

## Recovery 198: GlobalTick wall-clock throttle

The FastView host's source scheduling layer is now bounded independently from
the match-event semantics. Host update path `0x521B64` calls Win32
`GetTickCount()`, subtracts the previous baseline at host `+0x2B0`, and
compares elapsed milliseconds against the three dwords at `0x7CA538`:

- speed index 0: **1000 ms**;
- speed index 1: **500 ms**;
- speed index 2: **250 ms**.

The FastView constructor initializes speed index host `+0x2AC` to **1**, so
500 ms is the source default. Key handler `0x521DA0` reacts to Space
(`0x20`) by cycling the index 0 -> 1 -> 2 -> 0.

When elapsed time reaches the selected threshold, the host stores the current
GetTickCount value as the new baseline and invokes MatchController once at
`0x521C03 -> 0x518330`. This path has no catch-up loop: a delayed host
iteration still advances at most one controller step and can therefore make
real observed intervals longer than the nominal threshold.

MatchController's EventGlobalTick dispatcher `0x518790` sends the current
counter at source field `+0x78` to all registered receivers and increments
that counter after dispatch unless controller state `+0x90 == 5`.

Combined with the source-closed one-EventPossession-opportunity-per-five-
GlobalTicks gate, the **minimum throttle span** between possession opportunities
is:

- speed 0: **5000 ms**;
- speed 1 (default): **2500 ms**;
- speed 2: **1250 ms**.

These are source scheduling thresholds, not guaranteed observed intervals under
a delayed host loop.

## Recovery 199: ClockControl bridge and exact decoded possession art

Fresh bounded executable tracing ties the same `EventGlobalTick` payload used
by MatchIterator to the visible FastView clock. `ClockControl` constructor
`0x51EB90` creates its text control at **(439,44)-(621,64)**. Receiver
`0x51EDB0` reads the event's first dword and render helper `0x51EDD0`
passes that same unsigned value to source format `%u %s` at `0x8292F4`.
The source branches change around values **46** and **91**, matching the
already recovered regulation-half clock boundary structure.

Independently, MatchIterator divides the same GlobalTick value by **5** before
passing the quotient to source statistics lookup `0x631240`. That lookup
indexes the MatchCalculator segment arrays `+0x100C/+0x106C/+0x10CC`.
`reconstruction/gate14_fastview_clock.py` records only these exact numeric
relationships and does not assign an unverified localized suffix to the clock.

The completed-match semantic shell now preserves each reconstructed
five-minute possession segment's `calculation_minute` as the source
GlobalTick value and records the exact `GlobalTick // 5` source-array index.
A non-five-minute possession segment fails this bridge closed instead of being
silently rescheduled.

`reconstruction/original_fastview_possession_art.py` adds an exact pixel-output
seam for the bounded possession component. It checksum-validates the four
already staged original EA444 resources, decodes them using tables and
quantization from the original executable, and returns only the exact
base-pitch plus active-overlay placements. It explicitly reports that a complete
FastView frame is unavailable because surrounding background ownership,
PossessionFigures typography, and human-side orientation are not all recovered.

The authorized disc also contains
`FM2001_Art/FastView/background.444`: **205,984 bytes**, **800x600**,
SHA-256
`499e930fe0a328d969096b8d2cdb8c817169f02812adcc78acf111dc666d95c0`,
with path literal at `0x8294E8`. This is a high-value shell lead, not a live
asset claim: the direct draw/binding from FastViewPanel to this bitmap is not
yet source-closed, so the renderer does not use it.

## Recovery 200: PossessionFigures exact typography

The three percentage controls now have a fully bounded source typography path.
Each constructor call into generic text control `0x527960` passes style index
**1**. Selector `0x527BA0` maps that index to wrapper `0x87BE90`.
Initializer `0x603670` stores font object `0x9197E0` into that wrapper, and
the loader sequence at `0x6042A8..0x6042F5` binds that object to exact source
path:

`Fonts/Zurich_BdXCn_BT_18pixel.fnt`

via path literal `0x839F00`.

The font is already provenance-staged from the authorized source:

- bytes: **83,174**;
- SHA-256:
  `4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd`;
- atlas: **1633x18**;
- native line height: **20**.

The generic constructor receives source flags **1**, ORs bit 3, and stores
render flags **9**. Draw path `0x64F090` interprets these flags as the default
**left** horizontal alignment and **top** vertical alignment: right and center
horizontal branches require bits 1/2, while bottom and center vertical branches
require bits 4/5. The constructor also supplies native color **0xFFFF**.
Rasterization ultimately reaches font draw `0x657280`.

Therefore each percentage glyph mask begins at the recovered control's top-left
origin and uses endpoint-white native color. The widest valid percentage string,
`100%`, rasterizes to **34x17**, so all `0%..100%` values fit completely
inside the source 40x18 controls without clipping.

`reconstruction/original_fastview_possession_figures_art.py` verifies the
staged font identity/metrics and renders only these exact percentage glyphs at
the already source-closed side1/neutral/side0 rectangles. It still does not
assign side 0/1 to the human user or synthesize surrounding FastView pixels.

## Recovery 202: home/away screen orientation and rejected loose background binding

The fixed-fixture path now closes the match-role meaning of the side indices
used by FastView.

`0x6173D0` resolves the real fixture's team at `fixture+0x0C` first and
the team at `fixture+0x10` second. These are the already recovered home and
away fixture fields. The builder wraps them and calls `LeagueMatch::0x5104F0`.
Its base constructor `0x5103D0` stores the first/home wrapper in the embedded
team-reference subobject at `LeagueMatch+0x14` and the second/away wrapper at
`LeagueMatch+0x28`.

Match setup `0x510D60` invokes the first virtual accessor on those two
subobjects in that order:

- `LeagueMatch+0x14` -> `MatchCalculator+0x0000` = **side 0 = home**;
- `LeagueMatch+0x28` -> `MatchCalculator+0x05B0` = **side 1 = away**.

Combining that source identity with the already closed PossessionFigures
rectangles gives the fixed match-role presentation:

- **away / side 1 = left** at (311,181)-(351,199);
- neutral = center;
- **home / side 0 = right** at (454,181)-(494,199).

The human-controlled club is therefore left when it is the away club and right
when it is the home club. This is a fixture-role mapping, not a claim that the
whole FastView scene mirrors itself around the human user.

The loose 800x600 `FM2001_Art/FastView/background.444` lead was also traced
to exhaustion at the direct-reference level. Literal `0x8294E8` is passed at
`0x51F2F0` to generic string constructor `0x684620`, creating static string
object `0x877758`; the only direct executable references to that static
object/data are its construction and destruction (`0x68467F`). FastViewPanel
constructor `0x51F490` does construct an 800x600 generic panel through
`0x527350`, but that constructor receives no background path and no direct
runtime consumer ties `0x877758` to the panel draw path.

Therefore the authenticated 800x600 bitmap remains **unbound** and must not be
rendered merely because its filename and dimensions look appropriate.
`reconstruction/gate14_fastview_background.py` regression-locks this negative
result.

## Recovery 203: directly owned full-width chrome

The next shell slice is source-bound more strongly than the rejected loose
background string. Live FastView code passes two concrete file paths directly
into image-control constructor `0x527730`:

- callsite `0x51FD63`: `FM2001_Art/FastView/top_bar.444`, exact source
  800x95, placed at (0,0)-(800,95);
- callsite `0x51FDF0`: `FM2001_Art/FastView/ticker.444`, exact source
  800x33, placed at (0,557)-(800,590).

The authorized source files rehash to
`f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a`
(19,268 bytes) and
`b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257`
(6,352 bytes). Both are staged byte-identically with provenance.
`reconstruction/gate14_fastview_chrome.py` guards identity/geometry and
`original_fastview_chrome_art.py` exposes only the two exact decoded strips.

This still does not recover the middle surface between y=95 and y=557 or the
bottom 10 pixels y=590..599. A complete 800x600 FastView frame is therefore not
claimed.

## Remaining boundary

Still open before claiming the bounded diagram is player-visible original
FastView behavior:

1. recover any process/match reset semantics for the private presentation RNG; EventGlobalTick event-count cadence and the host's GetTickCount throttle are now source-closed;
2. keep the now source-closed home/away mapping distinct from any broader
   scene-mirroring claim: side 0/home is right and side 1/away is left for
   PossessionFigures, while the human user's side follows fixture role;
3. keep the three 82×16 `team_bar_1` / `blank_bar` / `team_bar_2` assets under
   the separately proven `FastViewTeam` / `TeamTable` ownership. They must not
   be wired into `PossessionFigures`; percentage text placement is already exact;
4. combine the exact diagram pixels and exact percentage typography into a
   player-visible FastView surface only after surrounding shell/background
   ownership and side-orientation boundaries are source-closed or explicitly
   fail-closed;
5. recover audio/commentary and broader FastView/SCI choreography separately.

No unresolved timing or orientation is described as original behavior by this
checkpoint.
