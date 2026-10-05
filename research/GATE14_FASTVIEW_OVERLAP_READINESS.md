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

Within the FastViewScores wrapper, the historical aggregate
`league_scores_static` and `league_table_static` planes remain deliberately
**unordered relative to each other** because the aggregate score raster spans
more than one native position.

The new phased raster path removes that ambiguity for currently source-backed
score pixels. It carries these distinct component identities through the
resolved-only compositor:

- `league_scores_early_rows_static`;
- `league_table_static`;
- `league_scores_late_grid_static`;
- `league_scores_runtime_phase_icons`.

Their source-closed order is exactly:

`early rows -> league table -> late grid -> runtime phase-icon tail`.

The score wrapper as a whole still renders before the TeamTable wrapper.

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

As a result, legacy groups that still use the aggregate
`league_scores_static <-> league_table_static` representation retain a
**cross-component draw-order blocker** in addition to the blend blocker. In
that legacy six-family regression, 14 of 15 pairwise relations remain
source-closed; the missing pair is intentionally the aggregate score/table
relation.

By contrast, overlap groups built from the four phase-split score/table
identities above have complete source-closed pairwise order, including the
outer relation to TeamTable. Those groups are therefore blocked only by the
remaining cross-component blend/output-format boundary, not by draw order.

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

The native font destination-read/blend primitive is separately source-closed,
and the score/table phase split is now represented directly in component raster
and overlap topology. Runtime pixel-format evidence and exact modern expansion
remain separate prerequisites for emitting blended pixels. The phase split does
not by itself recover omitted score text/title controls or global FastView
z-order.
