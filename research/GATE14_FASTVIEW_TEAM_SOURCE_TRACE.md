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

## Reconstruction contract

`reconstruction/gate14_fastview_team.py` records the exact side-indexed asset
pairing, source identities, row origins, 17-pixel step, name/bar rectangles,
six generic text rectangles and row-11 name-grid transition.

All seven listed binary assets remain unimported in this checkpoint and no
substitute pixels are introduced.

## Next source step

After CI verifies this checkpoint, trace the two bar PictureControl state
consumers, including dynamic routine `0x526680`, far enough to name only
source-proven state semantics. If that remains semantically opaque, continue
the next directly owned FastViewTeam resource/control family without inventing
labels.
