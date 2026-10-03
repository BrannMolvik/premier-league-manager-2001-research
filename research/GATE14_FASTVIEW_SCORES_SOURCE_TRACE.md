# Gate 14 FastView score-grid source trace

_Date: 3 October 2026 KST. Recovery 205. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace separates the two similarly named FastView current-fixture grid
resources by their actual owning classes. It source-closes the
`FastViewLeagueScores` grid-1 strip layout and the bounded
`ScoreCompositeNormal` grid-2 local layout/receiver lifecycle.

It does **not** infer grid-2 final screen origin from bitmap dimensions, import
either binary asset into Git, or claim the complete FastView score screen.

Gate 13 remains the earliest incomplete validation gate pending its external
real-Windows schema-8 receipt.

## Revalidated source

Recovery 205 rematerialized the canonical authorized disc-image ZIP, recovered
the nested MODE1/2352 image, and re-extracted the canonical executable.

- authorized ZIP: **511,121,336 bytes**
- raw `famg2001.bin`: **631,627,248 bytes**
- canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The private Joliet reader again enumerated **2,456 files**.

## Distinct current-fixture resources

| Owner | Path literal VA | Exact source path | Bytes | Dimensions | SHA-256 |
| --- | ---: | --- | ---: | ---: | --- |
| `FastViewPanel::FastViewLeagueScores` | `0x829920` | `FM2001_Art/FastView/current_fix_grid_1.444` | 3,704 | 309×19 | `bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057` |
| `ScoreCompositeNormal` | `0x828ED0` | `FM2001_Art/FastView/current_fix_grid_2.444` | 4,060 | 309×16 | `ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e` |

The paths are not interchangeable despite their similar names.

## FastViewLeagueScores ownership and grid-1 layout

MSVC RTTI resolves final vtables `0x7CA750` and `0x7CA744` to:

`.?AVFastViewLeagueScores@FastViewPanel@@`

Its source layout path uses generic `PictureControl` constructor `0x527730`
(vtable `0x7CAA5C`) for `current_fix_grid_1.444`.

Method `0x523DF0` switches at source count **12**:

- count 1..12: one centered strip
  **(246,32)-(555,51)**;
- count >12: two strips
  **(38,32)-(347,51)** and **(454,32)-(763,51)**.

Every rectangle is exactly 309×19, matching the original resource.

A separate method owned by the same final vtable, `0x523370`, also directly
constructs the left 309×19 grid-1 strip at **(38,32)-(347,51)**. The reason
that method selects that particular branch is not assigned a higher-level
fixture semantic until its caller state is separately closed.

## FastViewLeagueScores event receiver and score-composite factory

The class's receiver base vtable `0x7CA7B4` resolves to
`Receiver<EventLeagueTableUpdate>`. Final receiver vtable `0x7CA744`
overrides the event callback with `0x523DB0`.

Primary-vtable method `0x523CC0` allocates a `ScoreCompositeNormal` and
calls its constructor `0x51B740`. This ties the two score families together
through class ownership without collapsing their distinct graphics.

## ScoreCompositeNormal grid-2 contract

Constructor `0x51B740` directly references
`FM2001_Art/FastView/current_fix_grid_2.444` and calls the shared
`ScoreComposite` builder.

Its fixed source layout table at `0x828E98` contains fourteen dwords:

`[309, 16, 0, 0, 0, 0, 2, 139, 177, 158, 130, 16, 13, 16]`

The first two values exactly match the grid-2 image dimensions, **309×16**.
The final on-screen origin is supplied by the owning composite call path and is
not promoted by this checkpoint.

Final `ScoreCompositeNormal` vtables resolve to the class RTTI, with primary
vtable `0x7CA36C`.

The constructor installs five typed receiver bases before replacing them with
the final class vtables:

| Event family | Base receiver vtable | Final vtable | Callback |
| --- | ---: | ---: | ---: |
| `EventHalfTime` | `0x7CA160` | `0x7CA354` | `0x51B9A0` |
| `EventExtraTime` | `0x7CA16C` | `0x7CA348` | `0x51B9C0` |
| `EventPenalties` | `0x7CA148` | `0x7CA33C` | `0x51B9E0` |
| `EventFullTime` | `0x7CA154` | `0x7CA330` | `0x51BA00` |
| `EventGlobalSecondHalf` | `0x7CA240` | `0x7CA324` | `0x51BA20` |

This source-closes the receiver families and callback identities, not yet every
visible text/icon effect inside those callbacks.

## Recovery 205 follow-on: final visible row geometry

The owning layout helper `0x522CD0` stores six row-layout fields on
`FastViewLeagueScores`; relayout method `0x5230B0` then positions existing
score composites from those exact fields.

For source counts **1..12**:

- columns = 1;
- rows per column = 12;
- composite origin = **(246,55)**;
- row step = **19** pixels.

For source counts **>12**:

- columns = 2;
- rows per column = 12;
- first origin = **(38,55)**;
- column step = **416** pixels, giving second-column x = **454**;
- row step = **19** pixels.

The same source has separate page handling above 24 records. This checkpoint
therefore treats the geometry as one visible 24-slot page and does not invent
off-page mapping.

Shared `ScoreComposite::0x51A730` proves that the grid-2 PictureControl begins
at the composite origin itself. Its exact local rectangle is:

`(0,0)-(309,16)`

so, for example, the first one-column row is
**(246,55)-(555,71)** and the first right-column row is
**(454,55)-(763,71)**.

The same fixed layout table creates four generic text controls at these local
rectangles:

1. `(2,0)-(132,16)`;
2. `(177,0)-(307,16)`;
3. `(139,0)-(152,16)`;
4. `(158,0)-(171,16)`.

At one-column row 0 those become:

1. `(248,55)-(378,71)`;
2. `(423,55)-(553,71)`;
3. `(385,55)-(398,71)`;
4. `(404,55)-(417,71)`.

Their semantic labels are intentionally not assigned by this checkpoint. The
geometry is source-closed independently of whether a control later proves to be
a club name, score, state marker or another text role.

## Recovery 206: independent LeagueTableComposite current-table family

The adjacent `current_table_grid_1.444` / `current_table_grid_2.444`
resources are **not** owned by FastViewLeagueScores or ScoreCompositeNormal.
Canonical RTTI and direct constructor references resolve a separate
`LeagueTableComposite` family:

- final `LeagueTableComposite` primary vtable `0x7CA400`;
- final secondary vtable `0x7CA3F8`;
- base `Receiver<EventScore>` vtable `0x7CA3B0`;
- base `Sender<EventLeagueTableUpdate>` vtable `0x7CA40C`;
- `Row@LeagueTableComposite` vtable `0x7CA3E8`;
- `Heading@LeagueTableComposite` vtable `0x7CA3F0`.

The FastView owner call at `0x523472` constructs `LeagueTableComposite`
through `0x51E000` at exact origin **(382,32)**.

The final primary vtable replaces the base `Receiver<EventScore>` callback
with `0x51E360`. That callback applies the source score-record mutations and
calls refresh `0x51E4C0` at `0x51E3A8`. The constructor independently
calls the same refresh at `0x51E1A5` after heading/row construction. The
refresh finishes by iterating the embedded `Sender<EventLeagueTableUpdate>`
receiver list beginning at `0x51E683`, so score events and initial
construction share one table-refresh/update-notification path.

### Exact current-table resources

| Owner | Path literal VA | Exact source path | Bytes | Dimensions | SHA-256 |
| --- | ---: | --- | ---: | ---: | --- |
| `LeagueTableComposite::Heading` | `0x829114` | `FM2001_Art/FastView/current_table_grid_1.444` | 4,496 | 381×19 | `db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f` |
| `LeagueTableComposite::Row` | `0x8290B4` | `FM2001_Art/FastView/current_table_grid_2.444` | 4,276 | 381×16 | `e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b` |

Both remain unimported; no substitute art is used.

### Heading geometry

`Heading` constructor `0x51DCB0` places grid-1 at the parent origin, giving
final rectangle **(382,32)-(763,51)**.

Its fixed seven text rectangles are local:

1. `(168,0)-(198,19)`;
2. `(198,0)-(228,19)`;
3. `(228,0)-(258,19)`;
4. `(258,0)-(288,19)`;
5. `(288,0)-(318,19)`;
6. `(318,0)-(348,19)`;
7. `(348,0)-(378,19)`.

Therefore their final x range is 550..760 at y 32..51. No semantic column
names are assigned here.

### Row geometry and count transform

`Row` constructor `0x51D730` places grid-2 locally at
`(0,0)-(381,16)`. The parent creates the first row at **(382,55)** and
advances y by exactly **19 pixels** per row.

The nine fixed local row text rectangles are, in source-table order:

1. `(168,0)-(198,16)`;
2. `(198,0)-(228,16)`;
3. `(228,0)-(258,16)`;
4. `(258,0)-(288,16)`;
5. `(288,0)-(318,16)`;
6. `(318,0)-(348,16)`;
7. `(348,0)-(378,16)`;
8. `(0,0)-(26,16)`;
9. `(30,0)-(160,16)`.

At row 0 those become grid **(382,55)-(763,71)** and text cells spanning the
same translated locations. Their user-facing meanings remain deliberately
unassigned.

Before row allocation, `0x51E0F0..0x51E101` transforms the source count:

- counts <= 12 are used unchanged;
- counts > 12 become `floor((count-1)/2)+1`, exactly `ceil(count/2)`.

This checkpoint records that numeric transform without assigning a higher-level
page/half-table semantic.

## Reconstruction contract

`reconstruction/gate14_fastview_scores.py` now records:

- exact source identities/checksums/dimensions;
- distinct class ownership;
- exact grid-1 one/two-strip rectangles;
- FastViewLeagueScores EventLeagueTableUpdate receiver identity;
- ScoreCompositeNormal fixed layout table and typed receiver lifecycle.

Both resources remain `imported=False`; no substitute art is used.

## Next source step

After CI verifies this checkpoint:

1. verify the new independent LeagueTableComposite contract through CI;
2. after it is canonical, trace the remaining LeagueTableComposite update/text
   semantics only where direct source evidence exists, or continue the next
   independent FastView resource family;
3. keep the already source-closed top/ticker binary import as a deterministic
   transport follow-up rather than a blocker.

