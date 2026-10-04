# Gate 14 resolved-only FastView composite

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The reconstructed FastView now has separate source-backed 800x600 RGBA planes
for direct chrome, PossessionDiagram, PossessionFigures, TeamTable, current
fixture scores, and LeagueTable graphics. Their internal pixels are recovered,
but the original draw order between those components is not yet source-closed.

This checkpoint makes the already-unambiguous subset renderable without choosing
an unsupported z-order.

## Contract

`compose_fastview_resolved_only_pixels()` accepts an exact
`FastViewComponentRasterSet`.

For each 800x600 pixel:

- zero nontransparent component owners -> output remains transparent;
- exactly one nontransparent component owner -> copy that RGBA pixel verbatim;
- two or more nontransparent component owners -> output remains transparent and
  the corresponding byte in `unresolved_overlap_mask` becomes 1.

Non-zero RGB with alpha zero does not claim pixel ownership.

The result records:

- exact copied RGBA bytes and SHA-256;
- a one-byte-per-pixel unresolved-overlap mask and SHA-256;
- resolved pixel count;
- unresolved-overlap pixel count;
- ordered source component identities and their original plane SHA-256 values;
- the exact contributor-component tuple for every distinct overlap family;
- the unresolved pixel count and half-open aggregate bounding rectangle for
  each contributor tuple.

## Overlap-topology narrowing

The overlap topology is diagnostic evidence, not a draw-order claim.

For every masked pixel, the compositor now inspects all nontransparent
component planes rather than stopping after the second contributor. Pixels with
the same ordered contributor tuple are grouped together. Each group retains:

- the component tuple in the existing source-plane order;
- the number of unresolved pixels with exactly that contributor set;
- the smallest half-open 800x600 bounding rectangle containing those pixels.

This turns the later executable trace from an open-ended request for a global
FastView z-order into a bounded set of concrete component relationships and
screen regions. It still does not say which component wins within any group.
Two spatially separated overlap islands with the same contributor set may share
one aggregate bounding rectangle; the per-pixel mask remains authoritative for
the exact unresolved coordinates.

Integrity checks require the overlap groups to use only known component
identities, preserve the retained plane order, use unique contributor tuples,
remain inside the FastView surface, and account for every unresolved overlap
pixel exactly once.

## Fidelity boundary

This is deliberately **not** a flattened or complete FastView frame.

The result requires all of these to remain false:

- `cross_component_z_order_recovered`;
- `flattened_frame_available`;
- `complete_fastview_frame`.

No overlap is resolved by input order, component name, alpha blending, geometry,
or a clean-room preference. A future source trace can replace masked pixels only
when the original cross-component ordering is actually recovered.

The compositor also does not add PlayerRow text, dynamic energy resize pixels,
audio, commentary, or 3D choreography.

## Validation

Focused tests cover:

- exact copying of singly owned opaque and partial-alpha pixels;
- alpha-zero pixels not claiming ownership;
- two-way and three-way overlaps staying transparent and masked;
- retention of exact two-way and three-way contributor tuples;
- aggregation of equal contributor sets into exact pixel counts and bounds;
- separation of distinct contributor sets;
- operation with only the three mandatory component planes;
- preservation of source plane hashes and component order;
- overlap-topology accounting guards;
- RGBA/mask integrity guards;
- rejection of false flattened/complete-fidelity promotion.

This provides a player-renderer-safe partial image while keeping every unknown
cross-component pixel explicitly visible to audits as unresolved and making the
remaining native ordering trace materially narrower.
