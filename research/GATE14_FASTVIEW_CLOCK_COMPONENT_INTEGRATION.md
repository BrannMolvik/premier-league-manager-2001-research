# Gate 14 ClockControl component / overlap integration

_Status: stacked follow-on to the white-endpoint clock raster. Gate 13 remains the earliest incomplete validation gate._

## Purpose

The source-closed outer FastViewPanel registration sequence places the visible
ClockControl TextControl after the top-bar/ticker PictureControls and before
PossessionDiagram.

The white-endpoint clock raster can therefore participate in the same
component/overlap accounting as other source-backed FastView planes without
claiming that every ClockControl state is rasterizable.

## Draw order

The recovered outer child sequence gives these pairwise relations:

`direct_chrome -> clock_text -> possession_diagram -> possession_figures_text`

Later score/team wrapper relations follow from the same outer traversal.

This is a relative order claim only. Omitted controls between these modeled
families remain omitted; their omission does not invalidate the order of the
modeled children.

The historical aggregate `league_scores_static` plane is still special because
it spans multiple nested score positions. The clock remains safely earlier than
that whole score wrapper because it is a direct outer child created before the
wrapper.

## Component plane

`FastViewComponentRasterSet` accepts one optional `clock_text` plane lifted
from the exact `FastViewClockRaster`.

A zero-layer initial clock plane is permitted because the native constructor
starts with the empty string. A visible clock plane carries one source text
layer.

The component set still rejects:

- an arbitrary object in place of an exact Clock raster;
- a different component identity;
- any attempt to mark cross-component z-order or a flattened frame complete.

## Resolved-only composition

The resolved-only compositor orders supplied planes as:

1. `direct_chrome`;
2. optional `clock_text`;
3. `possession_diagram`;
4. `possession_figures_text`;
5. optional score/team planes in their existing source order.

This ordering is metadata/order evidence only. It does **not** flatten
cross-component overlaps.

If top-bar chrome and a clock glyph both contribute to one pixel, that pixel
remains transparent in the resolved-only output and is recorded as an
unresolved contributor group:

`("direct_chrome", "clock_text")`

The draw-order audit can classify that group as order-resolved, but the pixel
remains blocked by the existing blend/output-format boundary.

## Partial-state boundary

This integration does not widen the raster's color coverage.

The optional clock plane can only be built for states whose source color is the
exact native 0xFFFF endpoint. Alert-colored ClockControl states still fail
closed before component integration.

Therefore this checkpoint keeps false:

- alert-color modern RGBA recovery;
- complete ClockControl state rasterization;
- cross-component overlap resolution;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.
