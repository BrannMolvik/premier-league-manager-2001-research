# Gate 14 resolved-only FastView Tk surface

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The canonical Gate-14 resolved-preview layer now exports the source-backed
800x600 RGBA subset and its authoritative unresolved-overlap mask as
deterministic PNGs. This checkpoint adds only the next presentation seam: put
that existing RGBA preview on a caller-owned Tk canvas without changing its
fidelity boundary.

It does not modify or depend on the Gate-13 management host.

## Rendering contract

`draw_fastview_preview_on_tk_canvas()` accepts an exact
`FastViewResolvedPreview` from
`gate14_fastview_resolved_preview.py`.

It:

- feeds the canonical `rgba_png` bytes directly to Tk `PhotoImage`;
- places exactly one image at native origin `(0, 0)`;
- retains the PhotoImage object so Tk does not garbage-collect it;
- retains the complete canonical preview record, including RGBA/mask hashes and
  exact overlap groups.

`draw_fastview_resolved_on_tk_canvas()` is a convenience adapter that first
builds that same canonical preview from an exact
`FastViewResolvedOnlyComposite`, then uses the identical Tk path.

The helper deliberately does **not**:

- re-encode a second competing PNG representation;
- clear the canvas;
- choose a background color or unknown shell pixels;
- scale or stretch the native 800x600 surface;
- create a window;
- bind input;
- invoke gameplay, simulation, RNG, management-host, audio, or 3D code.

## Fidelity boundary

The returned draw record requires:

- `unresolved_pixels_remain_transparent = True`;
- `cross_component_z_order_recovered = False`;
- `complete_fastview_frame = False`.

The canonical preview itself must also keep its z-order, flattened-frame, and
complete-frame claims false.

This means the Tk surface is directly visible but explicitly partial.
Transparent pixels remain transparent. Their exact unresolved-vs-unowned audit
state remains available through the retained preview's mask PNG and overlap
topology rather than being painted with substitute pixels.

## Validation

Focused tests verify:

- Tk receives the exact canonical RGBA preview PNG, not a re-encoded copy;
- the image is placed once at native origin with the source alpha preserved;
- the returned object retains the preview and PhotoImage lifetime;
- composite-to-preview adaptation preserves source RGBA/mask hashes and overlap
  metadata;
- false complete-frame promotion is rejected;
- the module has no gameplay, RNG, Gate-13 host, or simulation dependency.

This is still not Gate-14 completion. Cross-component draw order, dynamic
PictureControl resize pixels, unrecovered text/background ownership, audio
bindings, and SCI/3D choreography remain separate blockers.
