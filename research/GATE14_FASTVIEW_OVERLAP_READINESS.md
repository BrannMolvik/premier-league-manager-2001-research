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

## Recovery 275 draw-order advance

`reconstruction/gate14_fastview_draw_order.py` now source-closes relative
order across every currently rasterized FastView family:

`direct_chrome -> possession_diagram -> possession_figures_text -> league_table_static -> league_scores_static -> team_table`

The TeamTable position may be represented as either `team_table_static` or
`team_table_energy`.

The critical new source chain is the original SubPanelControl render bridge:
the score and team wrappers are appended to the outer FastViewPanel draw array,
and each wrapper's render slot synchronously invokes generic forward traversal
on its stored target panel. The score wrapper is registered before the team
wrapper. Inside FastViewLeagueScores, LeagueTable controls are registered before
the current-fixture score controls.

This is not inferred from geometry, allocation order, or names.

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

As a result, any current overlap group containing only the modeled raster
families at distinct native positions is now **draw-order resolved but blend
unresolved**. The audit still keeps a draw-order blocker for an unmodeled layer
or another pair absent from the source contract.

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

The next source task is therefore narrower: recover the native destination-read
and alpha/blend behavior used by the original rendering path, beginning with the
already bounded EA font renderer. Only then may any ordered overlap pixel be
resolved.
