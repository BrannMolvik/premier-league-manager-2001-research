# Gate 14 Windows runtime pixel-format receipt

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Why a runtime receipt is required

The original renderer does not hard-code one 16-bit RGB layout for FastView.

The canonical executable queries the active DirectDraw surface description at
`0x653090`, copies the returned format at `0x6530D0`, and derives channel
mask metadata through `0x653120`.

The retained runtime configuration lives under `0x984820`:

- red mask metadata: `0x984824`;
- green mask metadata: `0x984830`;
- blue mask metadata: `0x98483C`.

Later 16-bit surface construction at
`0x655673/0x65567C/0x655685` copies those same masks into new surface
descriptors.

Therefore choosing RGB565, RGB555, or another layout from convention would be
an unsupported fidelity claim. The exact values must come from one observed
original Windows runtime surface.

## Static source facts already closed

The source also closes the native font color-key relationship independently of
the unresolved runtime values.

Color-key setup `0x604090` stores:

`native_color_key = red_mask | blue_mask`

at global `0x87B680`.

The font path calls the packed-16 glyph blitter at
`0x65722E -> 0x658BC0` with replacement color **0**. Intermediate-alpha
pixels whose destination equals the native key are therefore replaced with zero
before the recovered /256 RGB-mask blend.

No fixed packed key constant is needed because the key follows the runtime
channel masks.

## Strict receipt contract

`reconstruction/gate14_windows_pixel_format_receipt.py` validates a private
receipt against the exact canonical executable identity:

- filename: `footballmanager.exe`;
- bytes: **4,714,541**;
- SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

The receipt must state that it was observed on Windows through the
source-qualified original runtime surface-description path and must retain the
exact recovered source anchors.

It accepts only:

- bit count exactly **16**;
- nonzero uint16 red/green/blue masks;
- individually contiguous masks;
- pairwise-disjoint masks;
- native color key exactly equal to `red_mask | blue_mask`;
- explicit positive observation flags;
- no claim that overlap pixels or Gate 14 are complete.

The validator deliberately does not rank or prefer RGB565 versus RGB555. It
accepts whichever valid mask triplet the original Windows runtime actually
reports.

## What a successful receipt closes

A successful receipt may establish:

- `runtime_rgb_mask_values_recovered=true`;
- `native_color_channel_layout_recovered=true`;
- the exact packed native magenta key for that layout;
- applicability of the already source-closed font key/blend primitive to that
  runtime mask set.

It still leaves these false:

- `packed16_to_modern_rgba_recovered`;
- `cross_component_pixels_resolvable`;
- `complete_fastview_frame_recovered`;
- `gate14_complete`.

## Exact next evidence requirement

An actual private Windows receipt is still required. It must report the mask
triplet observed from the original runtime surface path rather than from a
modern renderer assumption or a hand-selected common format.

Once that receipt exists, the next source task is to close the original
packed-16 to modern RGB expansion/quantization semantics needed to reproduce
the native blended pixel in the modern RGBA preview. Only then may ordered
PossessionFigures/PossessionDiagram overlap pixels be removed from the
resolved-only mask.
