# Gate 14 FastView score-grid source trace

_Date: 3 October 2026 KST. Recovery 205. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace separates the similarly named FastView current-fixture resources
and corrects a historical class-attribution error between
`FastViewLeagueScores` and `FastViewCupScores`. Both score views use
`current_fix_grid_1.444`; `ScoreCompositeNormal` independently owns
`current_fix_grid_2.444`.

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
| `FastViewLeagueScores / FastViewCupScores` | `0x829920` | `FM2001_Art/FastView/current_fix_grid_1.444` | 3,704 | 309×19 | `bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057` |
| `ScoreCompositeNormal` | `0x828ED0` | `FM2001_Art/FastView/current_fix_grid_2.444` | 4,060 | 309×16 | `ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e` |

The paths are not interchangeable despite their similar names.

## Corrected LeagueScores / CupScores class split

MSVC RTTI resolves `0x7CA750` / receiver vtable `0x7CA744` to:

`.?AVFastViewLeagueScores@FastViewPanel@@`

Its setup method is **`0x523370`**, and its score factory at vtable
slot `+0x5C` is **`0x523CC0`**. The call to shared layout helper
`0x522CD0` passes the exact six-field tuple:

`(x=38, y=55, rows=12, columns=1, column_step=0, row_step=19)`.

The same method constructs `current_fix_grid_1.444` through PictureControl
callsite **`0x5239F3`**, producing one left strip
**(38,32)-(347,51)**.

Separately, RTTI resolves primary vtable **`0x7CA680`** to:

`.?AVFastViewCupScores@FastViewPanel@@`

Its setup method is **`0x523DF0`** and its score factory is
**`0x5243B0`**. This is the method that owns the previously misattributed
count-12 layout split:

- count 1..12: `(246,55,12,1,0,19)`, with one centered grid-1 strip
  **(246,32)-(555,51)**;
- count >12: `(38,55,12,2,416,19)`, with left/right grid-1 strips
  **(38,32)-(347,51)** and **(454,32)-(763,51)**.

For CupScores, source counts above 24 additionally create paging controls.
Thus the former centered/two-column `fastview_league_scores_*` contract was
class-mislabeled and is now represented explicitly as CupScores behavior.

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

For **FastViewLeagueScores**, the stored layout is always:

- columns = 1;
- rows per column = 12;
- composite origin = **(38,55)**;
- column step = 0;
- row step = **19** pixels.

The static LeagueScores raster therefore exposes one verified 12-row page and
fails closed above that visible page until paging chronology is integrated.

For **FastViewCupScores**, `0x523DF0` owns the separate count-dependent
layout:

- count <=12: one centered column at **(246,55)**;
- count >12: two columns beginning at **(38,55)** and **(454,55)**;
- rows per column = 12;
- row step = 19;
- page capacity = 24 before the separately constructed paging controls.

Shared `ScoreComposite::0x51A730` proves that the grid-2 PictureControl begins
at the composite origin itself. Its exact local rectangle is:

`(0,0)-(309,16)`

so the first LeagueScores row is **(38,55)-(347,71)**.
For CupScores, the first centered row is **(246,55)-(555,71)** and the first
right-column row in the two-column branch is **(454,55)-(763,71)**.

The same fixed layout table creates four generic text controls at these local
rectangles:

1. `(2,0)-(132,16)`;
2. `(177,0)-(307,16)`;
3. `(139,0)-(152,16)`;
4. `(158,0)-(171,16)`.

At LeagueScores row 0 those become:

1. `(40,55)-(170,71)`;
2. `(215,55)-(345,71)`;
3. `(177,55)-(190,71)`;
4. `(196,55)-(209,71)`.

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

## Recovery 207: typed phase icon + label presentation

The four phase-image resources referenced beside ScoreCompositeNormal are now
bound directly to the already source-closed typed receiver callbacks rather
than inferred from filenames.

| Typed callback | Callback VA | Exact source path | Bytes | Dimensions | SHA-256 |
| --- | ---: | --- | ---: | ---: | --- |
| `EventHalfTime` | `0x51B9A0` | `FM2001_Art/FastView/half_time_icon.444` | 568 | 18×16 | `351589aa787ef62dae4013c67e231c90c7b6f2e82acd635fb67adb13e1c994c8` |
| `EventFullTime` | `0x51BA00` | `FM2001_Art/FastView/full_time_icon.444` | 616 | 18×16 | `9a24ab846620d6460afe265c6c98488870a08e2802d55476b9735a8641ae81b8` |
| `EventExtraTime` | `0x51B9C0` | `FM2001_Art/FastView/extra_time_icon.444` | 400 | 18×16 | `cf8af734450ab3069e0b32d82a770909d962ade9545533e7715d36d53e0eea2e` |
| `EventPenalties` | `0x51B9E0` | `FM2001_Art/FastView/penalties_icon.444` | 280 | 18×16 | `0fc5b157ecfadfa437f65ef5a4b940b5de6886e8c1e81e1f4ccba8d97af23545` |

The exact path literals are `0x828DD0 / 0x828DF8 / 0x828E20 /
0x828E48`. Their second static string-object family is initialized at
`0x51B650 / 0x51B690 / 0x51B6D0 / 0x51B710`. The typed callbacks load the
corresponding internal string pointer at
`0x877630 / 0x877618 / 0x877600 / 0x8775E8`, respectively. This closes the
event-to-icon identity independently of any localized display text.

All four callbacks also load a separate language-string pointer and call shared
phase-display helper `0x51BA30`. That helper first clears the previous display
through `0x51BBE0`, then constructs:

- one `PictureControl` at local rectangle **(316,0)-(334,16)** using the
  callback-supplied icon path;
- one paired generic text control at local rectangle
  **(311,0)-(339,16)** using the callback-supplied language string.

The helper stores its active byte at ScoreComposite offset `+0xAC`, the
picture pointer at `+0xD8`, and the text pointer at `+0xDC`. Its raw
PictureControl variant argument is 0; its paired text-control arguments include
raw flags `0x24` and style index 1.

For example, at the LeagueScores row-0 origin (38,55), those rectangles
translate to icon **(354,55)-(372,71)** and paired text
**(349,55)-(377,71)**.

The exact localized strings behind callback globals `0x982380`,
`0x98237C`, `0x982378`, and `0x982374` are not named here. The typed
event identity proves the phase event and matching icon, but this checkpoint
does not manufacture English label text from conventional football
abbreviations.

`EventGlobalSecondHalf` callback `0x51BA20` calls only clear helper
`0x51BBE0`. It therefore has no source-proven phase icon in this family and
the reconstruction mapping fails closed for that event.

## Reconstruction contract

`reconstruction/gate14_fastview_scores.py` now records:

- exact source identities/checksums/dimensions;
- distinct class ownership;
- corrected LeagueScores and CupScores class/vtable/method identities;
- true fixed-left LeagueScores grid/layout and separate CupScores
  centered/two-column geometry;
- shared grid-1 resource ownership across both score views;
- FastViewLeagueScores EventLeagueTableUpdate receiver identity;
- ScoreCompositeNormal fixed layout table and typed receiver lifecycle.

Both resources remain `imported=False`; no substitute art is used.

## Next source step

After CI verifies this checkpoint:

1. verify the typed ScoreComposite phase icon/text helper contract through CI;
2. after it is canonical, continue the next direct FastView resource family or
   source-close exact localized phase strings only if their language-index
   producer can be proved without guessing;
3. keep the already source-closed top/ticker binary import as a deterministic
   transport follow-up rather than a blocker.

