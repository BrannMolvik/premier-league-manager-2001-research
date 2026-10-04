# Gate 14 LeagueScores native draw-phase split

_Status: stacked Gate-14 source checkpoint; Gate 13 remains the earliest incomplete validation gate._

## Why the aggregate plane is insufficient

The historical league_scores_static raster combines source pixels from children
that do not share one native draw position.

The source order in FastViewLeagueScores::0x523370 is:

1. 0x5233C2 -> 0x522CD0 creates one ScoreCompositeNormal per source entry
   through vtable factory 0x523CC0. Their five static controls, including
   current_fix_grid_2.444, enter the score-panel child array here.
2. 0x523472 -> 0x51E000 constructs LeagueTableComposite.
3. later LeagueScores-owned controls are appended, including
   current_fix_grid_1.444 at PictureControl callsite 0x5239F3.
4. match phase callbacks may later call 0x51BA30. That helper first clears the
   prior phase pair through 0x51BBE0, then appends a new phase
   PictureControl/TextControl pair at the current parent tail.

Therefore an aggregate score raster cannot honestly receive one z-position
relative to the LeagueTable block.

## New raster phases

reconstruction/gate14_fastview_score_draw_phases.py keeps the currently
source-backed score pixels in three separate 800x600 planes:

- league_scores_early_rows_static: only grid-2 pixels from ScoreComposite
  objects created before LeagueTable;
- league_scores_late_grid_static: only the grid-1 strip created after the
  LeagueTable block;
- league_scores_runtime_phase_icons: only retained typed phase icons from the
  event-driven tail.

The source-closed static partial order is:

early score rows -> league_table_static -> late grid.

Runtime phase icons are classified separately as tail-appended controls. Their
paired localized text is deliberately not rasterized in this checkpoint.

## Geometry boundary

This checkpoint consumes the corrected FastViewLeagueScores geometry:

- visible page: 12 rows;
- row origin: x=38, y=55;
- row step: 19;
- grid-1 strip: (38,32)-(347,51).

It does not use the distinct FastViewCupScores centered/two-column layout.

## Fidelity boundary

The split improves the z-order evidence model but does not complete it. It does
not claim:

- paired phase text pixels;
- omitted LeagueScores title/button controls;
- a single aggregate score z-position;
- ordering for every omitted/unbound FastView child;
- global FastView z-order;
- a complete flattened FastView frame.

Those flags remain fail-closed.
