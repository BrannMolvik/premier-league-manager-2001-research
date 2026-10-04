# Gate 14 FastView score/table static raster planes

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

The score/table source-art loader provides exact original pixels for the
already-recovered current-fixture and LeagueTable resources. This checkpoint
turns only those proven pixels and rectangles into separate transparent
800x600 planes.

It does not render unresolved text, flatten components, or claim a complete
FastView frame.

## League-scores static plane

For a source count within the verified LeagueScores visible-page capacity of
1..12:

- current_fix_grid_1 is placed once at the true left LeagueScores rectangle
  **(38,32)-(347,51)**;
- current_fix_grid_2 is placed down the fixed left column beginning at
  **(38,55)** with a 19-pixel row step;
- optional phase icons are accepted only through the existing typed
  EventHalfTime/EventExtraTime/EventPenalties/EventFullTime source mapping;
- each phase icon is placed in the recovered icon rectangle for that exact
  source entry;
- the paired phase text control is deliberately not rasterized.

Counts above 12 remain fail-closed in this LeagueScores static slice because
native LeagueScores paging chronology is not yet integrated. The separate
FastViewCupScores source contract retains the centered/two-column geometry but
is not silently rendered through the LeagueScores plane.

## LeagueTable static plane

The plane contains only:

- current_table_grid_1 at the exact heading rectangle;
- current_table_grid_2 repeated for the exact source-derived visible-row count.

Heading and row text controls remain transparent/unrendered.

## Composition boundary

The emitted FastViewScoreTableStaticRasterSet keeps:

- cross_component_z_order_recovered = False;
- flattened_frame_available = False;
- text_rasterized = False;
- complete_component = False.

These planes therefore add original pixels without guessing their overlap
order relative to chrome, possession, TeamTable, or any future score text.

## Validation

Focused tests cover:

- exact fixed-left LeagueScores current-fixture placement;
- exact 12-row LeagueScores page boundary;
- typed phase-icon placement at first/last visible LeagueScores rows;
- separate source tests for the CupScores centered/two-column threshold;
- exact LeagueTable visible-row transform and 19-pixel row step;
- duplicate phase-icon rejection;
- rejection of unproved EventGlobalSecondHalf phase-icon mapping;
- continued unflattened/incomplete status.

The new raster source/test paths explicitly trigger the hosted reconstruction
suite. Local process execution remains unavailable with
caas.internal.errors.ClientError, so no local passing claim is made.

## Next boundary

After this correction is canonical, the next source-backed presentation step
is to split the aggregate score raster by native draw phase so the early
ScoreComposite block, LeagueTable block, later LeagueScores decorations, and
runtime phase tails can participate in an honest partial z-order. CupScores may
receive its own raster plane when required by a source-backed match view; it
must not be passed through the LeagueScores API.
