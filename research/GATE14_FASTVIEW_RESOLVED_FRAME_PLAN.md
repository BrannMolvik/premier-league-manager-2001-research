# Gate 14 resolved-only FastView frame-plan attachment

_Status: prepared dependent work-ahead; do not merge before the resolved-only compositor dependency is canonical._

## Purpose

The resolved-only compositor can produce a player-renderer-safe partial 800x600
image without choosing a cross-component z-order. This checkpoint attaches that
artifact directly to the existing immutable `FastViewFramePlan`.

The frame plan therefore carries, from the same source-backed component set:

- the individual component RGBA planes;
- the resolved-only RGBA image;
- the unresolved-overlap mask;
- the semantic shell and PlayerRow instructions.

## Construction

`build_fastview_frame_plan()` first builds the component raster set as before,
including optional verified score/table rasters. It then calls
`compose_fastview_resolved_only_pixels()` exactly once on that set and stores
the resulting `FastViewResolvedOnlyComposite`.

No match simulation, RNG, audio, commentary, z-order rule, or host/UI action is
introduced.

## Integrity boundary

`FastViewFramePlan.__post_init__()` requires an exact resolved-only composite
and reconstructs the ordered component-name/SHA-256 tuple from the attached
component raster set.

The composite's retained source-plane hashes must match that tuple exactly.
This prevents a caller from attaching a partial image produced from a different
component set while keeping the same semantic frame-plan object.

## Fidelity boundary

The frame plan still requires all unresolved claims to remain false:

- complete raster frame;
- cross-component z-order recovered;
- flattened frame available;
- audio ready;
- 3D choreography ready.

The resolved-only image is not a substitute for the original overlap order.
Masked pixels remain explicit evidence gaps until a later source trace closes
them.

This checkpoint also does not modify the Gate-13-owned player-visible host.
It only advances the disjoint renderer-input boundary.
