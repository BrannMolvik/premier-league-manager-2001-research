# Gate 14 PictureControl renderer source trace

_Status: private evidence tooling only. Gate 13 remains Codex-owned._

## Purpose

Two high-value FastView raster gaps now depend on the original generic control
renderer rather than on missing gameplay state:

1. cross-component child/draw ordering;
2. dynamic PlayerRow energy-bar pixels after source rectangle updates.

The repository already proves that the direct top/ticker chrome and score-grid
assets use generic `PictureControl` constructor `0x527730`, whose RTTI-backed
vtable is `0x7CAA5C`. It also proves that PlayerRow energy callback
`0x5267D0` drives rectangle writer `0x526680`.

`gate14_fastview_picturecontrol_source_trace.py` prepares a bounded,
checksum-gated private trace around those exact anchors.

## Canonical bounded windows

The default private report includes source-qualified inspection windows around:

- FastViewPanel constructor `0x51F490`;
- top/ticker PictureControl construction around `0x51FD40`;
- PossessionDiagram child construction around `0x520690`;
- generic panel constructor `0x527350`;
- generic PictureControl constructor `0x527730`;
- generic text/control draw neighborhood `0x64F090`;
- PlayerRow energy rectangle writer `0x526680`.

These are bounded inspection ranges only. They are not asserted to be complete
function boundaries.

## PictureControl vtable candidates

The tracer reads a caller-bounded number of dwords from known vtable
`0x7CAA5C`. For each entry it records:

- slot index and byte offset;
- target VA;
- target PE section;
- a bounded candidate method window when the target is in `.text`;
- optional linear Capstone disassembly.

The requested slot count is an analyst bound, not proof of the complete vtable
extent. No slot is labeled draw, paint, resize, visibility, destructor, or any
other role until private control-flow evidence establishes that role.

The report also retains raw little-endian occurrences of the vtable pointer.
Those remain byte candidates, not validated constructor/xref sites.

## Recovery 268: embedded picture render-chain leads

The private canonical pass progressed beyond the generic control boundary far
enough to identify the next bounded renderer neighborhoods without assigning the
still-missing resize semantics:

- PictureControl visible-child virtual forwarding: `0x64F6D0`;
- embedded picture setup: `0x64E500`;
- lazy embedded image acquisition: `0x64D8A0`;
- embedded picture draw lead: `0x64E5D0`;
- lower picture/blit lead: `0x6556C0`.

The PlayerRow energy writer at `0x526680` changes the dynamic PictureControl
destination rectangle and then invokes the generic refresh/invalidation path.
That proves the destination geometry changes before redraw, but does not by
itself prove whether the embedded renderer crops a native-width source, scales
the source into the changed destination, or derives a separate source rectangle.

The private tracer now includes all five renderer-chain neighborhoods in one
checksum-gated report and exposes them as candidate roles only. The next healthy
private execution should follow the rectangle values from the PictureControl
control rect through `0x64F6D0` into the embedded picture object and through
the lower blit call. Only if the source rectangle and size transform are
unambiguous should `picturecontrol_crop_vs_stretch_recovered` or dynamic
energy pixels be promoted.

## Fidelity boundary

The report hard-codes all of the target conclusions false:

- `cross_component_z_order_recovered=false`;
- `picturecontrol_resize_pixels_recovered=false`;
- `picturecontrol_crop_vs_stretch_recovered=false`;
- `embedded_picture_source_rect_recovered=false`;
- `child_registration_order_recovered=false`.

A future private run must manually establish the relevant control-flow,
container traversal, virtual dispatch, and source/destination rectangle behavior
before any of those flags can change.

In particular, constructor order alone is insufficient evidence for draw order,
and destination-width changes alone are insufficient evidence for crop versus
stretch behavior.

## Private-data policy

The canonical executable bytes, raw trace windows and disassembly output must
remain outside Git. Only the checksum-gated trace tool, synthetic calibration
tests and source-backed conclusions may be committed.


## Reconciliation with earlier draw-trace draft

An overlapping worker draft also proposed bounded FastViewPanel, Panel,
PictureControl and generic draw windows. This tracer subsumes that useful draw
neighborhood while retaining the more targeted PictureControl vtable-slot
inspection and the exact PlayerRow energy rectangle-writer window. The duplicate
draft is therefore not a separate source of renderer semantics.
