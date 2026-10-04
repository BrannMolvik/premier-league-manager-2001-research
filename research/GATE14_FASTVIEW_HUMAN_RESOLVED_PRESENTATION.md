# Gate 14 completed-human resolved presentation bundle

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The source-backed Gate-14 pieces now form a complete fail-closed path from an
already-completed human match outcome to pixels that can actually be placed on a
Tk canvas:

1. completed outcome -> `HumanMatchPresentation`;
2. presentation -> semantic FastView shell;
3. shell + verified original art -> `FastViewFramePlan`;
4. frame -> resolved-only RGBA/mask PNG preview;
5. resolved composite -> exact 800x600 coverage audit;
6. canonical RGBA preview -> caller-owned Tk canvas.

`gate14_fastview_human_resolved_presentation.py` binds those existing layers
together without adding any new source semantics.

## Integrity contract

`HumanFastViewResolvedPresentation` retains the exact frame, preview and
coverage records. Construction verifies that all three agree on:

- source composite RGBA SHA-256;
- source unresolved-overlap-mask SHA-256;
- resolved pixel count;
- unresolved-overlap pixel count;
- unresolved overlap groups.

The bundle rejects any layer drift rather than silently rebuilding or
normalizing it.

It also requires every unresolved fidelity flag to stay false:

- complete FastView raster frame;
- cross-component z-order recovery;
- background binding recovery;
- audio readiness;
- 3D choreography readiness.

## Completed-outcome paths

`build_human_fastview_resolved_presentation()` uses the existing completed
human outcome adapter and any PlayerRows already retained on that outcome.

`build_human_fastview_resolved_presentation_from_retained_histories()` reuses
the already source-backed retained-history row adapter. Visible row identity,
GlobalTick and presentation RNG(6) rolls remain explicit caller inputs exactly
as required by that lower layer.

Neither path mutates the completed match outcome or reruns match simulation.

## Player-visible draw seam

`draw_human_fastview_resolved_presentation()` passes the bundle's canonical
RGBA preview directly to the existing standalone Tk surface. It does not
recompose pixels, clear the canvas, add a background, scale the 800x600 image,
create a window, or bind controls.

This is therefore a genuine completed-match -> drawable-original-pixels path,
but still only for the subset whose ownership is already unambiguous.

## Remaining fidelity boundary

This checkpoint does **not** claim Gate 14 complete.

Still fail-closed:

- cross-component FastView draw/z-order;
- unknown/unbound surrounding background pixels;
- dynamic PictureControl resize raster semantics where not source-closed;
- menu/login/match audio bank ownership and sample/event bindings;
- original SCI/3D choreography and sequencing.

The resolved preview keeps ambiguous overlaps transparent and its mask/topology
remains authoritative for those pixels.
