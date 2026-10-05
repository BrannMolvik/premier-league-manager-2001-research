# Gate 14 FastView surfaced-resource raster planes

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The verified decoded surfaced resources are now representable as two distinct
800x600 FastView raster planes without collapsing different native draw ranks:

1. `match_background_surface`
   - source layers: 1;
   - native rectangle: `(0,0)-(800,600)`;
   - native position: first outer visible FastView control.
2. `club_badge_surfaces`
   - source layers: 2;
   - home rectangle: `(38,1)-(173,94)`;
   - away rectangle: `(627,1)-(762,94)`;
   - native position: after ScoreCompositeMain and before PossessionDiagram.

The two badge controls may share one aggregate raster plane because they are
consecutive outer registrations, do not overlap each other, and have the same
relative order against the currently modeled raster families.

The full background may not be merged into that badge plane because many outer
controls are drawn between them.

## Fidelity boundary

Promoted:

- exact decoded full-background pixels;
- exact decoded home/away badge pixels;
- exact source rectangles;
- two source-correct outer draw positions;
- source path retention for each raster layer.

Still false:

- component-set integration;
- cross-component native blend resolution;
- flattened complete FastView frame;
- Gate 14 completion.

## Next step

Lift these two planes into the existing FastView component-raster set and
source-order ledger. `match_background_surface` must precede direct chrome,
clock and all later components. `club_badge_surfaces` must follow the
unmodeled GoalFlash/ScoreCompositeMain boundary and precede
`possession_diagram`. Existing unresolved overlap pixels must remain masked
until the native packed-pixel output/blend boundary is completed.
