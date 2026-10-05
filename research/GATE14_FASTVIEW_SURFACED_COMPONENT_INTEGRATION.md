# Gate 14 FastView surfaced component integration

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The verified surfaced-resource raster planes are now integrated into the
FastView component model without flattening native draw positions.

Modeled source order is now:

1. `match_background_surface`;
2. `direct_chrome`;
3. `clock_text`;
4. `club_badge_surfaces`;
5. `possession_diagram`;
6. `possession_figures_text`;
7. `direct_header_text`;
8. recovered score/table phases;
9. TeamTable.

This is a relative order among currently modeled raster families. It does not
erase the known unmodeled outer controls that live between some of these
positions.

## Why background and badges stay separate

The 800x600 background is the first outer visible control. The badge pair is
registered much later, after GoalFlash and ScoreCompositeMain and before
PossessionDiagram. Combining them into one aggregate plane would destroy the
native overlap boundary.

Therefore the component set exposes two optional planes:

- `match_background` / component `match_background_surface`;
- `club_badges` / component `club_badge_surfaces`.

## Overlap behavior

Resolved-only composition includes both planes in source order, but any pixel
owned by more than one component remains transparent and is retained in the
unresolved overlap topology.

The pairwise draw-order ledger can classify relationships such as:

- background before direct chrome;
- clock before club badges;
- club badges before possession diagram.

Those source-order facts do not promote the native cross-component blend rule
or global FastView z-order.

## Fidelity boundary

Promoted:

- surfaced raster planes in component-set ownership;
- source-relative order for the two surfaced positions;
- resolved-only contributor accounting;
- overlap-readiness visibility for surfaced-plane collisions.

Still false:

- unmodeled outer-control raster completeness;
- native cross-component packed-pixel blending;
- global FastView z-order;
- flattened complete FastView frame;
- Gate 14 completion.

## Next step

Continue the remaining complete-frame critical path. Highest-value independent
work is either:

1. source-close/rasterize another omitted visible outer family such as
   GoalFlash or ScoreCompositeMain; or
2. complete the native packed16-to-modern display/output rule so currently
   source-ordered overlap pixels can become resolvable.

Choose the route with available source evidence without weakening any
fail-closed boundary.
