# Gate 14 FastView font-blend source trace

_Status: disjoint Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

Native draw order now proves that PossessionFigures percentage text is painted
after the PossessionDiagram controls. That pairwise order is not by itself
enough to flatten the remaining overlap pixels because the source font atlas is
8-bit alpha, not a binary mask.

The exact compositing rule at anti-aliased glyph edges therefore remains a
pixel-fidelity boundary.

## Bounded private trace

`gate14_font_blend_source_trace.py` packages the already source-qualified text
renderer path for one private checksum-gated pass:

- generic text draw: `0x64F090`;
- native control/text color setter: `0x650480`;
- EA font draw: `0x657280`;
- EA font loader: `0x657650`;
- generic text style selector: `0x527BA0`.

The existing possession-text evidence already binds style index 1 through
wrapper `0x87BE90` to font object `0x9197E0` and the verified
`Zurich_BdXCn_BT_18pixel.fnt` atlas.

## Fail-closed boundary

The tracer explicitly records:

- `glyph_alpha_source_recovered=true`;
- `possession_pairwise_draw_order_recovered=true`;
- `glyph_destination_read_recovered=false`;
- `glyph_alpha_blend_rule_recovered=false`;
- `native_color_channel_layout_recovered=false`;
- `cross_component_pixels_resolvable=false`;
- `complete_fastview_frame_recovered=false`.

No standard alpha-over equation is assumed. The next healthy private run must
follow `0x657280` far enough to prove how a non-binary atlas byte combines
with the current destination pixel. Only then may diagram/text overlap pixels be
removed from the unresolved mask.

No proprietary source bytes or generated disassembly belong in Git.
