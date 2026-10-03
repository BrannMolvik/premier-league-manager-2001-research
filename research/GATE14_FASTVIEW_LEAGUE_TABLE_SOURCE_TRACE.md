# Gate 14 FastView LeagueTableComposite source trace

_Date: 3 October 2026 KST. Recovery 205. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Scope

This trace source-closes the separate FastView current-league-table graphic
family. It must not be confused with the current-fixture score-grid family in
`GATE14_FASTVIEW_SCORES_SOURCE_TRACE.md`.

It closes:

- exact source identity of `current_table_grid_1.444` and
  `current_table_grid_2.444`;
- RTTI ownership by `LeagueTableComposite::Heading` and
  `LeagueTableComposite::Row`;
- the parent `LeagueTableComposite` FastView origin;
- exact heading/row background rectangles;
- all seven heading and nine row generic text-control rectangles;
- the exact source transform used to choose the number of visible row objects.

It does not yet assign user-facing semantic names to the text columns and does
not import either bitmap into Git.

## Exact source identities

| Owner | Path VA | Original source path | Bytes | Dimensions | SHA-256 |
| --- | ---: | --- | ---: | ---: | --- |
| `Heading@LeagueTableComposite` | `0x829114` | `FM2001_Art/FastView/current_table_grid_1.444` | 4,496 | 381×19 | `db8114130becce71ba84f890ccd157606d04bf68501484df308564da28957a5f` |
| `Row@LeagueTableComposite` | `0x8290B4` | `FM2001_Art/FastView/current_table_grid_2.444` | 4,276 | 381×16 | `e5a1b5688115cc8a63d47c738cf5af7f66f20eee9433292e47ee4e7c152ed70b` |

Both source files were re-extracted directly from the authorized raw
MODE1/2352 disc during Recovery 205.

## RTTI ownership

MSVC complete-object locators prove:

- vtable `0x7CA3F0`:
  `.?AVHeading@LeagueTableComposite@@`;
- vtable `0x7CA3E8`:
  `.?AVRow@LeagueTableComposite@@`;
- primary parent vtable `0x7CA400`:
  `.?AVLeagueTableComposite@@`;
- secondary parent vtable `0x7CA3F8`:
  the same `LeagueTableComposite` type at subobject offset 4;
- embedded vtable `0x7CA40C`:
  `Sender<EventLeagueTableUpdate>`.

This is a different class family from
`FastViewPanel::FastViewLeagueScores` / `ScoreCompositeNormal`.

## Parent FastView placement

The only direct `LeagueTableComposite::0x51E000` construction found in the
FastViewLeagueScores path is call `0x523472`.

Its source arguments set:

- x = **382**;
- y = **32**.

Constructor `0x51E000` passes those coordinates directly to
`Heading::0x51DCB0`, and initializes row y to `y + 23 = 55` with a
**19-pixel** row step.

The later refresh path `0x51E4C0` calls row mover `0x51DC10`. That routine
stores supplied x/y on the Row and forwards the same coordinates to the row
PictureControl plus all row text controls. The active rows therefore retain the
source x **382**; unused rows are moved to x **-500** by the same source path.
This confirms the screen coordinates are live child geometry rather than merely
temporary constructor values.

## Heading bitmap and text geometry

`Heading::0x51DCB0` constructs `current_table_grid_1.444` through generic
PictureControl `0x527730`.

At the parent FastView origin its exact bitmap rectangle is:

**(382,32)-(763,51)**

Static initializer `0x51D650` supplies seven heading text rectangles, each
30×19:

1. **(550,32)-(580,51)**
2. **(580,32)-(610,51)**
3. **(610,32)-(640,51)**
4. **(640,32)-(670,51)**
5. **(670,32)-(700,51)**
6. **(700,32)-(730,51)**
7. **(730,32)-(760,51)**

Their semantic labels remain unclaimed.

## Row bitmap and text geometry

`Row::0x51D730` constructs `current_table_grid_2.444` through the same
generic PictureControl. Row mover `0x51DC10` applies the stored parent x/y.

Row 0 is therefore:

**(382,55)-(763,71)**

Subsequent active rows add 19 px to y. For example:

- row 1: **(382,74)-(763,90)**
- row 11: **(382,264)-(763,280)**

Static initializer `0x51D4F0` supplies nine row text rectangles. At row 0
they are:

1. **(550,55)-(580,71)**
2. **(580,55)-(610,71)**
3. **(610,55)-(640,71)**
4. **(640,55)-(670,71)**
5. **(670,55)-(700,71)**
6. **(700,55)-(730,71)**
7. **(730,55)-(760,71)**
8. **(382,55)-(408,71)**
9. **(412,55)-(542,71)**

The source loop creates exactly nine text controls per row. Geometry alone does
not justify naming any of these controls.

## Visible-row count

`LeagueTableComposite::0x51E000` calls source count accessor `0x6335B0`.

- count <= 12: visible row-object count = count;
- count > 12: visible row-object count =
  `floor((count - 1) / 2) + 1 = ceil(count / 2)`.

Examples:

- 12 -> 12 rows;
- 13 -> 7 rows;
- 20 -> 10 rows;
- 24 -> 12 rows.

This is the source transform only. The higher-level meaning of the two-side
presentation for larger tables should be named only after the data-selection
path is traced.

## Reconstruction contract

`reconstruction/gate14_fastview_league_table.py` now records exact source
identity, RTTI ownership, parent origin, heading/row rectangles, row count and
generic text-control geometry.

Both bitmaps remain unstaged and the frame explicitly reports:

- `text_semantics_recovered = False`;
- `bitmap_resources_imported = False`.

## Next source step

After CI:

1. trace `LeagueTableComposite::Row::0x51D9C0` and the parent refresh path
   `0x51E4C0` to identify the nine row text producers without naming columns
   from visual intuition;
2. trace Heading text producers similarly;
3. only then decide whether these two exact EA444 resources and their text can
   join the player-visible FastView surface.

Gate 13 remains the earliest incomplete validation gate for its remaining
management shell/navigation fidelity tasks; its Windows schema-8 validation
has already passed.

