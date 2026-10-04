# Gate 14 FastView font-blend source trace

_Status: disjoint Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

FastView draw order is now source-closed for the currently rasterized component
families. PossessionFigures text is painted after the PossessionDiagram, but
that ordering alone is insufficient to flatten anti-aliased glyph edges because
the original font atlas carries 8-bit coverage values.

Recovery 277 source-closes the native packed-16-bit glyph blend primitive while
keeping final modern-RGBA overlap pixels fail-closed.

## Canonical private source revalidation

The authorized Library source was rematerialized and the root
`footballmanager.exe` re-extracted. The executable remains exactly
**4,714,541 bytes** with SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No proprietary executable bytes or generated disassembly are committed.

## Source path

The text path is now bounded through these source anchors:

- generic text draw: `0x64F090`;
- EA font draw: `0x657280`;
- per-glyph draw/dispatch: `0x6570F0`;
- packed 16-bit glyph blitter: `0x658BC0`;
- runtime native RGB-mask setup: `0x656320`.

The glyph blitter contains three orientation branches, but all three repeat the
same packed-pixel alpha primitive. The source-qualified destination-read sites
are `0x658D2C`, `0x658E63`, and `0x658FA9`.

## Recovered alpha behavior

The native blitter proves these exact endpoint semantics:

- glyph alpha **0**: leave the destination pixel unchanged;
- glyph alpha **255**: write the packed source color directly;
- glyph alpha **1..254**: read the existing packed 16-bit destination and blend
  each runtime RGB mask independently.

For one mask, with `a = glyph_alpha`, the compiled arithmetic is:

`(((destination & mask) * (256 - a)) + ((source & mask) * a)) >> 8`

The result is masked back to that channel and merged into the evolving packed
16-bit word. Bits outside the supplied RGB masks are preserved by the
intermediate-alpha branch.

This is denominator **256**, not a generic modern RGBA `/255` alpha-over
assumption.

## Runtime RGB-mask source

The blitter reads its channel masks from:

- red: global `0x9848DC`;
- green: global `0x9848D8`;
- blue: global `0x9848D4`.

Setup routine `0x656320` populates those globals from one native pixel-format
record at offsets:

- red mask: `+0x10`;
- green mask: `+0x14`;
- blue mask: `+0x18`.

The surrounding surface-description path is 0x6C bytes and supplies the
pixel-format record at its `+0x48` region. This source-closes that the blend
is parameterized by the active runtime surface format rather than by one
hard-coded RGB565/RGB555 constant.

The exact mask values used by the target Windows presentation surface are not
yet promoted by this checkpoint.

## Pure reconstruction primitive

`reconstruction/gate14_font_blend_source_trace.py` now contains
`Native16PixelMasks` and `blend_native_font_pixel16()`.

The primitive requires an explicit, pairwise-disjoint uint16 RGB mask set and
reproduces only the source-closed non-color-key packed arithmetic. It does not
choose a mask layout for the caller and cannot by itself flatten a FastView
overlap.

Synthetic tests lock:

- alpha-0 destination preservation;
- alpha-255 direct source write;
- denominator-256 intermediate arithmetic;
- preservation of non-RGB bits during intermediate blending;
- rejection of overlapping/invalid masks;
- exact source addresses and mask-source offsets.

## Color-key boundary

The native blitter also references color-key global `0x87B680`. Around an
intermediate-alpha pixel it can special-case destination/source pixels matching
that key before the RGB-mask interpolation.

That logic is real source behavior, but its exact applicability to the
PossessionFigures-on-PossessionDiagram call path has not yet been closed here.
The pure reconstruction primitive therefore excludes color-key handling rather
than guessing it.

## Fail-closed state

The source report now records:

- `glyph_alpha_source_recovered=true`;
- `possession_pairwise_draw_order_recovered=true`;
- `glyph_destination_read_recovered=true`;
- `glyph_alpha_blend_rule_recovered=true`;
- `runtime_rgb_mask_source_recovered=true`;
- `native_color_channel_layout_recovered=false`;
- `font_color_key_applicability_recovered=false`;
- `cross_component_pixels_resolvable=false`;
- `complete_fastview_frame_recovered=false`.

No FastView overlap pixel is unmasked by this checkpoint.

## Exact next source task

The next private source step is to close the two remaining translation
boundaries needed for actual overlap pixels:

1. determine the exact runtime RGB mask values/layout used by the target
   original FastView surface, rather than assuming RGB565 or RGB555;
2. trace the `0x6570F0 -> 0x658BC0` font call arguments far enough to prove
   whether the color-key branches can affect PossessionFigures over the opaque
   possession-pitch destination.

Only after those are source-safe should the reconstruction add native packed
pixel to modern RGBA round-trip logic and remove any overlap pixels from the
resolved-only mask.
