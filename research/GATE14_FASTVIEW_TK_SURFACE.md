# Gate 14 resolved-only FastView Tk surface

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The Gate-14 frame pipeline already produces a source-backed 800x600
`FastViewResolvedOnlyComposite`. Pixels with one proven component owner are
retained exactly. Pixels whose cross-component ordering is not yet recovered
stay transparent and are tracked by the unresolved-overlap mask/topology.

This checkpoint adds a player-visible rendering boundary for that exact partial
image without modifying the Gate-13 management host.

## Rendering contract

`encode_fastview_resolved_png()` converts only the existing composite RGBA
bytes into a lossless 8-bit RGBA PNG using filter 0 scanlines. It does not fill,
blend, recolor, scale, or reinterpret transparent pixels.

`draw_fastview_resolved_on_tk_canvas()`:

- requires an exact `FastViewResolvedOnlyComposite`;
- creates one Tk `PhotoImage` from the lossless PNG;
- places it at native origin `(0, 0)` on a caller-owned canvas;
- returns an object that retains the Tk photo reference so the image is not
  garbage-collected;
- carries the resolved count, unresolved count, and exact overlap groups into
  the draw result.

The draw helper deliberately does **not**:

- clear the canvas;
- choose a background color or unknown shell pixels;
- scale or stretch the 800x600 source surface;
- create a window;
- bind input;
- invoke gameplay, simulation, RNG, management-host, audio, or 3D code.

This makes the recovered FastView subset directly drawable while leaving
surrounding composition policy to a later source-backed host integration.

## Fidelity boundary

The returned draw record requires:

- `unresolved_pixels_remain_transparent = True`;
- `cross_component_z_order_recovered = False`;
- `complete_fastview_frame = False`.

The surface therefore cannot be presented as a complete original FastView
screen. Transparent pixels include both areas with no currently recovered
component owner and pixels deliberately masked because multiple components
overlap without a proven original order. The compositor's overlap mask/topology
remains the audit source for that distinction.

## Validation

Focused tests verify:

- PNG IHDR is exactly 800x600 RGBA8;
- decompressed scanlines reproduce the resolved composite RGBA byte-for-byte;
- unresolved overlap pixels remain alpha-zero;
- Tk receives exactly one native-origin image draw;
- the PhotoImage payload decodes to the exact emitted PNG;
- overlap audit metadata is retained;
- false complete-frame promotion is rejected;
- the module has no gameplay, RNG, Gate-13 host, or simulation dependency.

This is a rendering seam, not Gate-14 completion. Cross-component order,
dynamic PictureControl resize pixels, unrecovered text/background ownership,
audio bindings, and SCI/3D choreography remain separate blockers.
