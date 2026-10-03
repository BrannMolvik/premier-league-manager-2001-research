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

## Reconstruction contract

`reconstruction/gate14_fastview_team.py` records the exact side-indexed asset
pairing, source identities, row origins, 17-pixel step, name/bar rectangles,
six generic text rectangles and row-11 name-grid transition.

All seven listed binary assets remain unimported in this checkpoint and no
substitute pixels are introduced.

## Next source step

After CI verifies the energy-bar checkpoint, continue the adjacent typed
PlayerRow receivers. Source candidates are EventPlayerUpdateForm callback
`0x526740`, EventPlayerGoal callback `0x526800`, and
EventPlayerOwnGoal callback `0x526880`. Map only the text/control fields
directly proved by their data flow; do not infer the remaining row labels from
layout.
