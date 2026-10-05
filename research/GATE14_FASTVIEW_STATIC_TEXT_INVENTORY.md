# Gate 14 FastView score/table static text inventory

_Status: source-backed cloud-safe inventory; Gate 13 remains the earliest incomplete validation gate._

## Result

The static nested text-control geometry already present in the canonical
ScoreCompositeNormal and LeagueTable contracts is now enumerated explicitly.

This is a structural inventory only. It does not guess column meanings, score
semantics, club-name semantics, fonts, styles, colors, localized values or
pixels.

## ScoreCompositeNormal rows

Each visible FastViewLeagueScores row owns four static generic TextControls.
For the verified one-column LeagueScores page:

- first row origin: (38,55);
- row step: 19;
- visible capacity: 12.

The four local rectangles are already source-closed:

1. (2,0)-(132,16)
2. (177,0)-(307,16)
3. (139,0)-(152,16)
4. (158,0)-(171,16)

At row 0 they become:

1. (40,55)-(170,71)
2. (215,55)-(345,71)
3. (177,55)-(190,71)
4. (196,55)-(209,71)

The inventory therefore contains exactly `4 * visible_source_count` controls
for a verified 1..12-row page.

## LeagueTableComposite

The source-closed heading owns seven TextControls.

Each displayed LeagueTable row owns nine TextControls. The existing count
transform remains unchanged:

- source count <= 12: displayed rows = source count;
- source count > 12: displayed rows = ceil(source count / 2).

For a 20-club table this yields 10 displayed rows and therefore:

`7 + 9 * 10 = 97`

static LeagueTable TextControls.

The inventory preserves exact source-table order and final rectangles from the
existing LeagueTable geometry contract.

## Explicit exclusions

This checkpoint does not include:

- runtime ScoreComposite phase-label text, which already has a separate
  source/raster contract;
- later FastViewLeagueScores title/button controls identified by the native
  draw-phase audit;
- any semantic names for the four score-row or 7/9 LeagueTable cells;
- text values, font/style/color, rasterization or flattening.

Those exclusions are intentional. The resulting contract keeps
`score_subpanel_complete_pixels_recovered=false`,
`global_fastview_z_order_recovered=false`, and
`complete_fastview_frame_recovered=false`.

## Next step

The next score-subpanel source task should bind either the style/value producer
for these now-enumerated controls or the separately omitted later
LeagueScores title/button family. Do not infer either from conventional football
UI labels or resource filenames.
