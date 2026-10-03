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

For a source count within the recovered one-page capacity of 1..24:

- current_fix_grid_1 is placed using the exact one-strip/two-strip threshold;
- current_fix_grid_2 is placed at every visible ScoreCompositeNormal slot;
- optional phase icons are accepted only through the existing typed
  EventHalfTime/EventExtraTime/EventPenalties/EventFullTime source mapping;
- each phase icon is placed in the recovered icon rectangle for that exact
  source entry;
- the paired phase text control is deliberately not rasterized.

Counts above 24 remain fail-closed because paging beyond one visible source
page is not part of this static slice.

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

- exact one-column and two-column current-fixture placement;
- the 12-entry source threshold;
- typed phase-icon placement on left and right columns;
- exact LeagueTable visible-row transform and 19-pixel row step;
- one-page 24-entry fail-closed boundary;
- duplicate phase-icon rejection;
- rejection of unproved EventGlobalSecondHalf phase-icon mapping;
- continued unflattened/incomplete status.

The new raster source/test paths explicitly trigger the hosted reconstruction
suite. Local process execution remains unavailable with
caas.internal.errors.ClientError, so no local passing claim is made.

## Next boundary

After the loader and raster slices are verified, the next source-backed
presentation work should connect these new planes into the same unflattened
FastView frame-plan family or close additional score text semantics only where
their producers are already persisted. Audio-bank adjudication remains blocked
until private executable execution is healthy.
