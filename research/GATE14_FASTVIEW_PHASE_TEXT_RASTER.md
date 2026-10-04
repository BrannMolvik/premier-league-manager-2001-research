# Gate 14 ScoreComposite phase-text raster

_Status: independent Gate-14 work-ahead while Gate 13 Fixtures paging remains Codex-owned._

## Result

The exact ScoreComposite phase labels recovered in the preceding checkpoint are
now rasterized into a separate transparent 800x600 plane:

- `HT`;
- `FT`;
- `ET`;
- `PEN`.

The raster uses the provenance-tracked original
`Fonts/Zurich_BdXCn_BT_18pixel.fnt`, exact generic TextControl centering, exact
28x16 control clipping, and the source native endpoint color `0xFFFF`.

It is intentionally **not** composited into the runtime phase-icon plane.

## Exact source font

The phase label uses generic text style index 1, already source-bound to:

`Fonts/Zurich_BdXCn_BT_18pixel.fnt`

SHA-256:

`4c5d5d33cb1fb2345c93a0e133863cc3e9e25d4297d0a6d15df762fb710eaccd`

The verified source font has:

- byte size: 83,174;
- atlas: 1633x18;
- native line height: 20.

Exact rendered mask sizes are:

| Label | Mask size |
| --- | --- |
| `HT` | 16x17 |
| `FT` | 14x17 |
| `ET` | 14x17 |
| `PEN` | 23x17 |

## Native centered placement

The local TextControl is `(311,0)-(339,16)`, width 28 and height 16.

Generic text draw uses signed divide-by-two arithmetic that truncates toward
zero. For one LeagueScores row at origin `(38,55)`, the final control is
`(349,55)-(377,71)`.

The line origins are therefore:

- `HT`: `(355,53)`;
- `FT`: `(356,53)`;
- `ET`: `(356,53)`;
- `PEN`: `(352,53)`.

The vertical line origin is two pixels above the control because the native line
height is 20 while the control height is 16. This is not an overflow defect:
the selected glyphs have `draw_y=3`, so their visible 14-pixel bodies begin
inside the clipped control and occupy source rows 1..14.

The raster applies the native control clip. No glyph pixel may escape the exact
28x16 phase-text rectangle.

## Runtime ordering boundary

One original phase callback appends:

1. its 18x16 PictureControl icon;
2. then its 28x16 TextControl label.

However, the global receiver dispatch order between different ScoreComposite
rows is not yet source-closed. Multiple rows may therefore form an interleaved
sequence such as:

`icon(row A), text(row A), icon(row B), text(row B)`

The reconstruction must not replace this with a fabricated aggregate relation
such as `all icons -> all text` or `all text -> all icons`.

For that reason the exact phase text is emitted as component:

`league_scores_runtime_phase_text`

separate from:

`league_scores_runtime_phase_icons`.

No pairwise aggregate order is promoted between those two component families.

## Pixel boundary

The text plane itself contains exact endpoint-white glyph alpha and transparent
background. This is safe because `0xFFFF` is an all-channel endpoint that does
not require choosing an unrecovered packed-16 channel layout.

The plane is **not** a flattened native destination result. Where it overlaps
the runtime icon plane, exact native packed-16 destination blending/output
conversion and aggregate row order still matter. Those overlap pixels remain
unresolved.

## Reconstruction contract

`reconstruction/gate14_fastview_score_phase_text_raster.py` provides:

- strict original-font loading by size/hash;
- source-equivalent centered origin arithmetic;
- exact clipping into each translated phase TextControl;
- one transparent 800x600 plane;
- per-row placement evidence;
- duplicate-row rejection.

This checkpoint may promote:

- exact phase label glyph pixels;
- exact phase label screen placement;
- exact native control clipping.

It deliberately keeps false:

- aggregate icon/text order recovery;
- flattening with the runtime icon plane;
- global FastView z-order;
- complete FastView frame;
- Gate 14 completion.

## Next step

Carry the separate runtime text plane into component/overlap accounting at the
same unresolved aggregate-order level as the runtime icon plane. Both remain
after the source-closed late score grid and before the later TeamTable wrapper,
but no icon<->text edge may be introduced until cross-row event dispatch order
is source-closed.
