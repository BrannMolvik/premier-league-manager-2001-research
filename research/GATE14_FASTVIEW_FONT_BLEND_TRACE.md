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
- active-surface format capture: `0x653090 -> 0x6530D0`;
- per-channel mask metadata builder: `0x653120`;
- runtime native RGB-mask setup: `0x656320`;
- native color-key setup: `0x604090`.

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

The active-surface capture path proves why those values are runtime evidence.
`0x653090` queries a 0x6C-byte surface description and `0x6530D0`
retains its 16-bit channel layout under config base `0x984820`:

- red mask metadata: `0x984824`;
- green mask metadata: `0x984830`;
- blue mask metadata: `0x98483C`.

Helper `0x653120` stores each raw mask plus the source shift metadata used
by the game's own packed-color conversions. Later 16-bit surface creation at
`0x655673/0x65567C/0x655685` copies those same retained masks into new
surface descriptors.

The exact mask values used by the target Windows presentation surface are
therefore intentionally not hard-coded by this checkpoint.

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

## Recovered font color-key path

Color-key setup `0x604090` reads the retained red mask at `0x984824`,
reads the retained blue mask at `0x98483C`, ORs them, and stores the result
at global `0x87B680`.

The native key is therefore exactly:

`red_mask | blue_mask`

which is the packed magenta key for whichever 16-bit runtime layout DirectDraw
reported. No fixed RGB565 or RGB555 constant is required.

The font call at `0x65722E -> 0x658BC0` passes literal zero as the blitter's
replacement-color argument. In each packed-blitter orientation branch, only for
intermediate alpha 1..254:

1. read the destination packed word;
2. if destination equals the native key, replace it with the caller's
   replacement color, which is zero on this font path;
3. if the replacement color itself equals the key, skip the blend;
4. otherwise apply the already recovered per-channel /256 blend.

Alpha zero skips before this key path and alpha 255 directly writes the source
color before this key path.

`blend_native_font_pixel16_with_color_key()` now records these exact
source semantics while remaining parameterized by an explicit runtime mask
set.

## Fail-closed state

The source report now records:

- `glyph_alpha_source_recovered=true`;
- `possession_pairwise_draw_order_recovered=true`;
- `glyph_destination_read_recovered=true`;
- `glyph_alpha_blend_rule_recovered=true`;
- `runtime_rgb_mask_source_recovered=true`;
- `runtime_rgb_mask_values_recovered=false`;
- `native_color_channel_layout_recovered=false`;
- `font_color_key_applicability_recovered=true`;
- `cross_component_pixels_resolvable=false`;
- `complete_fastview_frame_recovered=false`.

No FastView overlap pixel is unmasked by this checkpoint.

## Exact next source task

The static font path is now closed through color-key handling. The remaining
translation boundary for actual overlap pixels is the **runtime mask value set**
used by the target Windows FastView surface.

The next repository step is a strict private Windows pixel-format receipt
contract that accepts only a 16-bit, pairwise-disjoint runtime mask triplet
captured from the source-qualified surface path and checks that the retained
native key equals `red_mask | blue_mask`. Until an actual Windows receipt
supplies those mask values, RGB565 and RGB555 both remain unclaimed.

After that runtime evidence exists, source-close the exact packed-16 to modern
RGBA expansion rule before removing any overlap pixels from the resolved-only
mask.
