# Gate 14 FastView component raster planes

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

The existing Gate-14 frame plan had source-backed semantic state, exact component
geometry and decoded original art, but it deliberately stopped before any RGBA
composition because the source draw order between FastView components is still
unrecovered.

This checkpoint advances that boundary without inventing the missing ordering.

## Source-backed raster boundary

reconstruction/gate14_fastview_component_rasters.py now emits three separate
transparent 800x600 RGBA planes:

1. directly PictureControl-owned FastView chrome;
2. PossessionDiagram;
3. PossessionFigures source-font text.

Each plane uses only already recovered component ownership and geometry.

### Direct chrome plane

The chrome plane contains only the two source-bound PictureControls:

- top_bar.444 at (0,0)-(800,95);
- ticker.444 at (0,557)-(800,590).

No loose FastView/background.444 content is introduced.

### PossessionDiagram plane

The diagram plane preserves the already recovered internal source order:

1. base pitch;
2. active state overlay when present.

The existing exact placement rectangles and decoded original EA444 RGBA payloads
are used directly.

### PossessionFigures plane

The text plane places only the exact rendered Zurich glyph bounds at each
source-proven line origin. It does not fill the complete 40x18 control rectangle
with invented pixels and refuses any glyph that exceeds its recovered clip.

## Cross-component ordering remains fail-closed

The three planes are intentionally not flattened into one FastView frame.

The emitted FastViewComponentRasterSet requires:

- cross_component_z_order_recovered = False;
- flattened_frame_available = False.

FastViewFramePlan now carries this raster set alongside the existing semantic
shell, PlayerRow render plans and partial-surface layout. A frame plan therefore
contains real source-backed pixels while remaining unable to claim a complete
raster frame, audio readiness or recovered 3D choreography.

This removes a renderer implementation gap without turning an unresolved
component-overlap question into a guessed draw order.

## Validation

Focused tests cover:

- exact 800x600 transparent plane size;
- top-bar and ticker placement boundaries;
- PossessionDiagram base/overlay ordering;
- PossessionFigures glyph-bounds-only rendering;
- plane SHA-256 integrity guards;
- rejection of malformed RGBA geometry and out-of-clip glyphs;
- continued rejection of cross-component flattening;
- frame-plan attachment of the component raster set.

The new files are included in the full reconstruction workflow trigger so the
hosted suite can validate this checkpoint even when the local execution sandbox
is unavailable.

## Remaining boundary

This does not yet provide a complete player-visible FastView screen.

Still unresolved or separately bounded:

- cross-component z-order where recovered controls overlap;
- rasterization of TeamTable PlayerRow resources/text;
- ScoreComposite / league-score pixels not yet source-complete;
- commentary/audio integration;
- original 3D choreography;
- a live Windows renderer/player that consumes these planes.

The next efficient Gate-14 step should either source-close enough TeamTable
pixel inputs to add a fourth independent raster plane, or connect these separate
planes to a player-visible Windows FastView host without flattening unresolved
overlaps prematurely.
