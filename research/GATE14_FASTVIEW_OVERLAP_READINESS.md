# Gate 14 FastView unresolved-overlap readiness

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The resolved-only FastView compositor already refuses to flatten any pixel with
two or more source-backed component contributors. That remains the correct
pixel-fidelity boundary, but not every masked overlap is blocked by the same
missing evidence.

Recovery 273 now separates two questions:

1. is the native draw order for every component in an overlap group source-closed?
2. is the native cross-component pixel/blend rule source-closed?

This distinction narrows the next private trace without turning known
draw-order evidence into guessed pixels.

## Source-backed relation reused

`reconstruction/gate14_fastview_draw_order.py` currently proves one exact
cross-component pair:

`possession_diagram -> possession_figures_text`

The percentage text is registered later in the same parent draw array and the
generic parent renderer traverses that array forward.

That ordering fact does **not** resolve the pixels. The native font path uses an
8-bit alpha atlas and the destination-read / anti-aliased blend rule remains
unrecovered, as documented in `GATE14_FASTVIEW_FONT_BLEND_TRACE.md`.

## Readiness audit

`reconstruction/gate14_fastview_overlap_readiness.py` consumes only an exact
`FastViewResolvedOnlyComposite`.

For every unresolved contributor group it:

- enumerates every component pair;
- asks only the existing source-closed draw-order contract for a relation;
- records each relation that is genuinely known;
- records the total number of pairwise relations required for a complete order;
- marks complete draw order only when every required pair is source-backed;
- keeps cross-component blend recovery false;
- keeps every unresolved pixel non-resolvable.

The aggregate audit partitions the exact unresolved pixel count into:

- pixels whose full contributor draw order is already recovered;
- pixels whose contributor draw order is still incomplete.

All current unresolved pixels remain in `blend_unresolved_overlap_pixel_count`,
and `raster_resolvable_overlap_pixel_count` is required to remain zero.

This means the known PossessionDiagram/PossessionFigures two-way overlap is now
identified as **draw-order resolved but blend unresolved**, while a group such
as direct chrome plus TeamTable remains **draw-order unresolved and blend
unresolved**. Three-way groups retain any known pairwise subrelation without
pretending that one known edge establishes a total order.

## Completed-human presentation integration

`HumanFastViewResolvedPresentation` now carries the overlap-readiness audit
alongside its existing frame plan, resolved PNG preview and frame-coverage
audit.

The bundle integrity-binds:

- source composite SHA-256;
- source overlap-mask SHA-256;
- unresolved pixel count;
- exact contributor group identities, counts and bounding rectangles.

The player-visible preview is unchanged. No overlap pixel is unmasked and no
new background, alpha equation, audio behavior or 3D choreography is invented.

## Fidelity boundary

This checkpoint still keeps all of these false:

- cross-component blend-rule recovery;
- all-overlap-pixels-resolvable;
- flattened/complete FastView frame;
- Gate-14 completion.

The next source-backed step is therefore materially narrower:

1. recover the native EA font destination-read/blend behavior for the already
   ordered possession text overlap; and
2. recover additional FastView child registration/draw-order relations for the
   remaining overlap groups.

If private executable execution remains unavailable, continue only
repository-side work that preserves these fail-closed boundaries. Constructor
addresses or component geometry alone are not sufficient to promote z-order.
