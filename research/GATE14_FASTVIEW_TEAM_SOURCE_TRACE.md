# Gate 14 FastViewTeam / TeamTable source trace

_Date: 3 October 2026 KST. Recovery 208. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace source-closes the two side-indexed `FastViewTeam::TeamTable`
constructor configurations and the bounded nested `Row` presentation
geometry. It deliberately does not assign user-facing meanings to the six row
text controls, the two bar layers, or the row-index transition after the first
11 rows.

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

## Recovery 209: typed PlayerRow event semantics

RTTI identifies the four Row receiver bases and their final callback overrides:

| Row subobject | Receiver RTTI | Final vtable | Callback |
| --- | --- | ---: | ---: |
| `+0x54` | `Receiver<EventPlayerUpdateForm>` | `0x7CA90C` | `0x526740` |
| `+0x58` | `Receiver<EventPlayerUpdateEnergy>` | `0x7CA900` | `0x5267D0` |
| `+0x5C` | `Receiver<EventPlayerGoal>` | `0x7CA8F4` | `0x526800` |
| `+0x60` | `Receiver<EventPlayerOwnGoal>` | `0x7CA8E8` | `0x526880` |

### Energy bar

`EventPlayerUpdateEnergy::0x5267D0` reads event dword `+0x04` and passes it
to Row helper `0x526680`.

The helper uses source constants **58**, **99**, and **82**. Static initializer
`0x51F330` stores `99 - 58 = 41` into runtime divisor `0x877754`.
The exact transform is:

`extent = trunc(clamp((energy - 58) / 41, 0, 1) * 82)`

The truncation helper is `0x668350`. For integral event values this is
exactly `floor((energy - 58) * 82 / 41)` inside the 59..98 interval.

The full bar rectangle is the already source-closed 82×16 Row bar rectangle.
The two PictureControls have distinct roles:

- Row `+0x3C`: full static bar-B layer;
- Row `+0x38`: dynamically resized bar-A layer;
- Row `+0x40`: source side index controlling the resize direction.

Side index 0 therefore uses full `blank_bar` below a `team_bar_1` dynamic
layer growing from 0 to 82 pixels from the left.

Side index 1 uses full `team_bar_2` below a `blank_bar` dynamic layer whose
width shrinks from 82 to 0 pixels, revealing the team-bar layer from the right.

This is now source-proven as **player Energy** presentation, not a generic or
possession bar.

### Form text

`EventPlayerUpdateForm::0x526740` reads event dword `+0x04`, formats it
with exact source format `%u` at `0x828D3C`, and writes Row text control
`+0x34`.

That is generic text-control index 5 from the Recovery-208 geometry:

- side 0 row 0: **(276,27)-(296,43)**;
- side 1 row 0: **(504,27)-(524,43)**.

### Goal / own-goal count

`EventPlayerGoal::0x526800` increments Row dword `+0x18`, formats the new
value with exact source format `(%u)` at `0x829B94`, and writes Row text
control `+0x2C`.

`EventPlayerOwnGoal::0x526880` increments the same counter and writes the same
`(%u)` text to the same control. It additionally changes that control's
native packed color before returning. The packed-color operation is retained
as an exact source action, but no human-readable color name is assigned here.

The goal-count control is generic text-control index 3:

- side 0 row 0: **(243,27)-(263,43)**;
- side 1 row 0: **(743,27)-(763,43)**.

The remaining text controls stay unnamed.

## Reconstruction contract

`reconstruction/gate14_fastview_team.py` records the exact side-indexed asset
pairing, source identities, row origins, 17-pixel step, name/bar rectangles,
six generic text rectangles and row-11 name-grid transition.

All seven listed binary assets remain unimported in this checkpoint and no
substitute pixels are introduced.

## Next source step

After CI verifies this checkpoint, prioritize Gate-14 closure work: use the
newly source-closed FastViewTeam presentation only where it helps construct the
recognizable match workflow, and pivot to exact menu/match audio bank ownership
or another directly integrated presentation seam. Do not exhaustively name
remaining decorative cells unless they are required by the Gate-14 criteria.
