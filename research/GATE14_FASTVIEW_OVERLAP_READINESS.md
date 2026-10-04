# Gate 14 FastView unresolved-overlap readiness

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The resolved-only FastView compositor refuses to flatten any pixel with two or
more source-backed component contributors. That remains the pixel-fidelity
boundary.

The readiness audit separates two independent questions:

1. is the native draw order for every component in an overlap group source-closed?
2. is the native cross-component pixel/blend rule source-closed?

Recovery 275 materially advances only the first question.

## Current draw-order boundary

`reconstruction/gate14_fastview_draw_order.py` retains the source-closed
outer-wrapper relations:

`direct_chrome -> possession_diagram -> possession_figures_text -> FastViewScores wrapper -> team_table`

Within the FastViewScores wrapper, the aggregate
`league_scores_static` and `league_table_static` planes are now deliberately
**unordered relative to each other**.

Fresh source tracing shows why: the LeagueScores setup creates one
ScoreCompositeNormal per source entry before constructing LeagueTableComposite,
then appends additional score-owned controls after the table block. Runtime
phase callbacks may later clear and reappend a score icon/text tail. Therefore
the aggregate league-scores raster spans native positions on both sides of the
league-table raster.

The TeamTable position may still be represented as either
`team_table_static` or `team_table_energy`. The score wrapper itself still
renders before the team wrapper through the source-closed SubPanelControl
bridge.

This correction is based on constructor/vtable/append order, not geometry or
allocation order.

## Readiness audit

`reconstruction/gate14_fastview_overlap_readiness.py` consumes only an exact
`FastViewResolvedOnlyComposite`.

For every unresolved contributor group it:

- enumerates every component pair;
- asks only the source-closed draw-order contract for a relation;
- records every genuinely known pair;
- marks complete draw order only when every required pair is source-backed;
- keeps cross-component blend recovery false;
- keeps every unresolved pixel non-resolvable.

As a result, groups that do not require the aggregate
`league_scores_static <-> league_table_static` relation may still be
draw-order resolved. A group containing both aggregate score/table planes now
retains a **cross-component draw-order blocker** in addition to the blend
blocker. In the six-family regression, 14 of 15 pairwise relations are
source-closed; the missing pair is intentionally the aggregate score/table
relation.

The audit also keeps a draw-order blocker for an unmodeled layer or any other
pair absent from the source contract.

Static and energy TeamTable rasters are alternatives for the same native
position, not two simultaneously composited native siblings.

## No pixel promotion

The new order evidence does not define what the native renderer does to the
destination pixel when a later component has partial alpha.

Every current unresolved pixel therefore remains in
`blend_unresolved_overlap_pixel_count`, while
`raster_resolvable_overlap_pixel_count` remains exactly zero.

The player-visible resolved-only PNG is unchanged. No masked pixel is unmasked.

## Completed-human presentation integration

`HumanFastViewResolvedPresentation` continues to carry the overlap-readiness
audit alongside the frame plan, resolved PNG preview, and frame-coverage audit.
The bundle remains integrity-bound to:

- source composite SHA-256;
- source overlap-mask SHA-256;
- unresolved pixel count;
- exact contributor group identities, counts, and bounding rectangles.

## Fidelity boundary

This checkpoint still keeps all of these false:

- cross-component blend-rule recovery;
- all-overlap-pixels-resolvable;
- flattened/complete FastView frame;
- global z-order for omitted/unbound layers;
- Gate-14 completion.

The native font destination-read/blend primitive is now separately
source-closed, but the aggregate score/table order correction means these
planes must first be split by native draw phase before their shared overlap can
be flattened honestly. Runtime pixel-format evidence and exact modern expansion
remain separate prerequisites for emitting blended pixels.
