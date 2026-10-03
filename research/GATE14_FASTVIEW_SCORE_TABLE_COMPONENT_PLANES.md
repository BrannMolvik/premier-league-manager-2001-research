# Gate 14 score/table component-plane bridge

_Status: Gate-14 work-ahead on canonical score/table static raster dependency af6afe2c._

## Purpose

The unflattened FastView component container already carries direct chrome,
PossessionDiagram, PossessionFigures, and optional TeamTable static pixels.
The score/table raster slice adds two more independently verified 800x600
planes:

- league_scores_static;
- league_table_static.

This checkpoint bridges those two planes into the same component container
without claiming their order relative to any other FastView child.

## Contract

build_fastview_component_rasters() accepts an optional exact
FastViewScoreTableStaticRasterSet.

When supplied, both score/table planes are lifted without pixel mutation:

- size is preserved;
- RGBA bytes are preserved;
- source-layer count is preserved;
- SHA-256 is preserved;
- component identity is preserved.

The pair is atomic. Supplying only one plane is rejected, as is any object that
is not the exact score/table raster-set type.

## Fidelity boundary

The bridge does not change:

- cross_component_z_order_recovered = False;
- flattened_frame_available = False;
- complete_fastview_frame = False.

It does not add these planes to the human frame plan automatically because that
path does not yet retain a source-proven live current-fixture source count,
LeagueTable source count, or typed phase state. Those inputs must be connected
from real retained match/presentation state rather than guessed.

## Validation

Existing component-raster CI paths already cover the modified source and test
files. New regressions require exact pair lifting, unchanged hashes, rejection
of wrong bundle types, rejection of a partial pair, and continued unflattened
status.
