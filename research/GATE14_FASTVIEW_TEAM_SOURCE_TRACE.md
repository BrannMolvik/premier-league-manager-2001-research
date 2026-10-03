# Gate 14 FastViewTeam / TeamTable source trace

_Date: 3 October 2026 KST. Recovery 208. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace source-closes the two side-indexed `FastViewTeam::TeamTable`
constructor configurations and the bounded nested `Row` presentation
geometry. Recovery 209 additionally source-closes the two bar layers as the
mirrored `EventPlayerUpdateEnergy` display. It still does not assign
user-facing meanings to the six row text controls or the row-index transition
after the first 11 rows.

Gate 13 remains the earliest incomplete validation gate for its remaining
management shell/navigation fidelity work.

## Class ownership and construction

Canonical RTTI and constructor flow already established:

- `FastViewTeam@FastViewPanel` final vtable `0x7CA888`;
- FastViewTeam setup `0x524A20`;
- nested `TeamTable@FastViewTeam@FastViewPanel` vtable `0x7CA950`;
- TeamTable constructor `0x524EC0`;
- nested Row constructor `0x525DB0`, final primary vtable `0x7CA918`.

`FastViewTeam::0x524A20` constructs two TeamTables with explicit source side
indices **0** and **1**.

## Side-indexed source assets

The source pointer table at `0x829308..0x829324` gives exact asset pairing.

### Side index 0

- primary name grid: `team_name_grid.444`;
- alternate name grid: `team_name_grid_2.444`;
- bar A: `team_bar_1.444`;
- bar B: `blank_bar.444`.

### Side index 1

- primary name grid: `team_name_grid_3.444`;
- alternate name grid: `team_name_grid_4.444`;
- bar A: `blank_bar.444`;
- bar B: `team_bar_2.444`.

Exact source identities:

| Resource | Bytes | Dimensions | SHA-256 |
| --- | ---: | ---: | --- |
| `team_name_grid.444` | 3,496 | 259×16 | `368f7c86ef07d9447af886b0a4d8857fa4a732d65f17913f72b2a9155e9a4d93` |
| `team_name_grid_2.444` | 3,512 | 259×16 | `0cce4d1646afa3dd11da5f0db6b3a887ded8a6d647f39d998eaef8ffe5f71602` |
| `team_name_grid_3.444` | 3,512 | 259×16 | `8deb413437234504cbb6c3a076b172304469d873f4e2df5fbedd314e5f22b095` |
| `team_name_grid_4.444` | 3,496 | 259×16 | `6fc1446b5d65a07a5165fa0947282dfeb6b783d142ae9edc76f60dbd5cecd3e8` |
| `team_bar_1.444` | 2,344 | 82×16 | `edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d` |
| `blank_bar.444` | 2,776 | 82×16 | `961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a` |
| `team_bar_2.444` | 2,312 | 82×16 | `4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751` |

This preserves the Recovery-198 correction: the three bar resources belong to
FastViewTeam/TeamTable, not PossessionFigures.

## Row geometry

TeamTable copies its source configuration into the nested Row configuration.
The Row constructor then uses those fields directly for the name-grid
PictureControl, six generic text controls, and two bar PictureControls.

All rows advance by exactly **17 pixels** vertically.

### Side index 0

Row 0 origin: **(37,27)**.

- name grid: **(37,27)-(296,43)**;
- shared bar rectangle: **(309,27)-(391,43)**;
- six generic text rectangles, source order:
  1. `(37,27)-(61,43)`;
  2. `(64,27)-(104,43)`;
  3. `(107,27)-(243,43)`;
  4. `(243,27)-(263,43)`;
  5. `(223,27)-(243,43)`;
  6. `(276,27)-(296,43)`.

### Side index 1

Row 0 origin: **(409,27)**.

- name grid: **(504,27)-(763,43)**;
- shared bar rectangle: **(409,27)-(491,43)**;
- six generic text rectangles, source order:
  1. `(537,27)-(561,43)`;
  2. `(564,27)-(604,43)`;
  3. `(607,27)-(743,43)`;
  4. `(743,27)-(763,43)`;
  5. `(723,27)-(743,43)`;
  6. `(504,27)-(524,43)`.

The six generic text controls use raw source flags
`[0x24, 0x24, 0x21, 0x21, 0x21, 0x24]`. Their semantic labels are not
assigned by this checkpoint.

## Primary-to-alternate name-grid transition

The first TeamTable construction loop creates exactly **11** Row objects using
the primary name-grid string. At `0x52583E`, the constructor copies the
alternate name-grid string into the same Row-config slot. Any remaining rows
are then constructed through the same Row constructor.

Therefore the exact source rule is:

- row indices 0..10 -> primary name-grid asset;
- row indices >=11 -> alternate name-grid asset, when such rows exist.

This numeric transition is source-closed. It is deliberately not labelled
"starting XI", "substitutes", "reserves", or any similar gameplay term until a
direct semantic bridge proves that interpretation.

## Recovery 209: EventPlayerUpdateEnergy bar lifecycle

Fresh first-hand disassembly of the rehashed canonical executable closes the
previously unnamed bar consumer.

`PlayerRow` contains four typed receiver subobjects. The energy receiver is
the subobject at overall row **+0x58**:

- base RTTI vtable `0x7CA92C` =
  `Receiver<EventPlayerUpdateEnergy>`;
- final PlayerRow receiver vtable `0x7CA900`;
- callback `0x5267D0`;
- callback reads `EventPlayerUpdateEnergy +0x04` and forwards that integer
  value to row routine `0x526680`.

Routine `0x526680` rewrites only the dynamic bar PictureControl at row
`+0x38`. Its source rectangle comes from row fields
`+0x44/+0x48/+0x4C/+0x50`; row `+0x40` is the side index.

The exact source normalization is:

- lower anchor: **58.0** at `0x7CA544`;
- upper anchor: **99.0** at `0x7CA548`;
- span global `0x877754` initialized at `0x51F330` to **41.0**;
- output width constant: **82.0** at `0x7CA96C`;
- float-to-int helper `0x668350` truncates toward zero;
- values above the normalized maximum are clamped to 1.0;
- this routine contains **no lower clamp**.

For integer event values at or below 99, the width expression therefore
reduces exactly to:

`2 * (energy - 58)`

and values above 99 produce width 82.

The side-specific resource composition now has source-proven meaning:

- side 0: `team_bar_1.444` is the dynamic layer over static
  `blank_bar.444`; its right edge grows from the bar's left edge;
- side 1: `blank_bar.444` is the dynamic mask over static
  `team_bar_2.444`; its right edge shrinks as energy rises, revealing the
  team bar underneath.

At row 0 this means side 0 grows within **(309,27)-(391,43)**, while side 1
shrinks the blank mask within **(409,27)-(491,43)**. The reconstruction
preserves the source's lack of a lower clamp rather than silently sanitizing
values below 58.

This closes the bar-state semantics as **player energy**. It does not assign
semantics to the six generic text controls; those remain separate receiver/data
traces.

## Recovery 209: typed PlayerRow text-event receivers

The three remaining typed PlayerRow receiver callbacks adjacent to the energy
receiver source-close three of the six generic text cells.

### EventPlayerUpdateForm

- receiver subobject: overall row **+0x54**;
- base RTTI vtable: `0x7CA938` =
  `Receiver<EventPlayerUpdateForm>`;
- final PlayerRow receiver vtable: `0x7CA90C`;
- callback: `0x526740`;
- event field: `+0x04`;
- source format: `%u` at `0x828D3C`;
- destination control: row `+0x34` = constructor text cell **6**.

Therefore text cell 6 is the source PlayerRow **form** value display.

### EventPlayerGoal

- receiver subobject: overall row **+0x5C**;
- base RTTI vtable: `0x7CA920` = `Receiver<EventPlayerGoal>`;
- final PlayerRow receiver vtable: `0x7CA8F4`;
- callback: `0x526800`;
- row-local counter: `+0x18`, initialized to zero by the constructor;
- callback increments that counter and formats it with `(%u)` at
  `0x829B94`;
- destination control: row `+0x2C` = constructor text cell **4**.

Therefore text cell 4 is the source per-player **goal count** display.

### EventPlayerOwnGoal

- receiver subobject: overall row **+0x60**;
- base RTTI vtable: `0x7CA95C` = `Receiver<EventPlayerOwnGoal>`;
- final PlayerRow receiver vtable: `0x7CA8E8`;
- callback: `0x526880`;
- separate row-local counter: `+0x1C`, initialized to zero;
- callback increments that counter and formats it with the same `(%u)`
  source string;
- destination control: row `+0x30` = constructor text cell **5**;
- after updating text, the source calls color setter `0x650480` with a
  pixel-format-derived value.

The own-goal control therefore has a source-proven distinct color update, but
this checkpoint does **not** name that color until the runtime pixel-format
channel mapping is independently closed.

The source-order rectangle mapping means row 0 uses:

- side 0 goal cell 4: **(243,27)-(263,43)**;
- side 0 own-goal cell 5: **(223,27)-(243,43)**;
- side 0 form cell 6: **(276,27)-(296,43)**;
- side 1 goal cell 4: **(743,27)-(763,43)**;
- side 1 own-goal cell 5: **(723,27)-(743,43)**;
- side 1 form cell 6: **(504,27)-(524,43)**.

Text cells 1..3 remain deliberately unnamed.

## Reconstruction contract

`reconstruction/gate14_fastview_team.py` records the exact side-indexed asset
pairing, source identities, row origins, 17-pixel step, name/bar rectangles,
six generic text rectangles and row-11 name-grid transition.

All seven listed binary assets remain unimported in this checkpoint and no
substitute pixels are introduced.

## Next source step

After CI verifies the typed text-event checkpoint, trace the shared row refresh
path `0x526470 <- 0x525B66` and producer `0x525BD0` far enough to identify
text cells 1..3 only where their underlying player/database accessors are
directly proven. Keep the own-goal color name fail-closed unless the runtime
pixel-format channel mapping is independently recovered.


## Recovery 211: PlayerProxy form/energy source histories

Fresh canonical-executable tracing closes the source of the two remaining
dynamic PlayerProxy payloads rather than aliasing them to similarly named modern
fields.

RTTI identifies PlayerProxy's primary base as
`Sender<EventPlayerUpdateForm>` (base vtable `0x7CA85C`) and its
`+0x10` subobject as `Sender<EventPlayerUpdateEnergy>` (base vtable
`0x7CA854`). FastViewPanel allocates 11 proxies per side and update path
`0x521C9C` calls two MatchCalculator wrappers for each eligible displayed
player:

- `0x632FC0 -> 0x6308B0` supplies the first argument to
  `PlayerProxy::0x5247A0`; that argument is cached at proxy `+0x4C` and
  dispatched through the **form** sender.
- `0x633000 -> 0x630910` supplies the second argument; it is cached at proxy
  `+0x50` and dispatched through the **energy** sender.

The MatchCalculator player history uses a **0x4C-byte stride** and 24
five-minute samples. Both getters clamp the tick to 119 before integer division
by five.

Condition history:
- side 0 begins at MatchRecord `+0x4C`;
- side 1 begins at `+0x5FC`;
- sample address = side base + player_index*0x4C + floor(min(tick,119)/5).

Form history is the adjacent 24-byte history exactly **+0x18** later:
- side 0 `+0x64`;
- side 1 `+0x614`.

Writer `0x6309D0` proves the distinction. It copies DBRPlayer Condition
`+0x77` into the Condition history, while the separate match-form history is
maintained in the source display range **1..10**, initialized from 5 and
updated by match/player context. Persistent DBRPlayer form-state byte
`+0x192` (the modern `PreparedMatchPlayer.form_state` source, range 0..4)
is merely one input into that history and is **not** the FastView form value.

Energy derivation `0x630910` is also separate from raw Condition. It starts
from Condition at tick 0, walks five-minute form-history transitions before the
requested tick (rising form subtracts 4; otherwise adds 4), consumes one
`RNG(6)` draw and adds `roll-3`, clamps to at least 1, then caps by the
Condition history at the first five-minute boundary at or after the requested
tick. Therefore modern `condition` cannot be copied directly into the energy
bar either.

`reconstruction/gate14_fastview_player_history.py` materializes only this
source contract and exact derived-energy primitive. It requires the source-order
RNG(6) result explicitly and does not import or advance simulation RNG.

The live integration boundary is now precise: a completed modern match must
retain the source-compatible Condition history, 1..10 match-form history, and
the correct post-calculation/presentation RNG sequence before
`fastview_player_rows` can be populated faithfully. Post-hoc copying of
`PreparedMatchPlayer.condition` or `form_state` is forbidden.
