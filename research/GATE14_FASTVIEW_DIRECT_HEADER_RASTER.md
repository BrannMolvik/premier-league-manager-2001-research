# Gate 14 direct FastView header raster

_Status: independent source-backed Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Result

The two direct outer FastView header TextControls can now be rasterized from
already source-backed final strings using their exact original style-3 font,
native white endpoint, geometry, centering arithmetic and clipping.

The raster layer deliberately accepts the final two strings as inputs. It does
**not** manufacture a match type, referee identity, stadium or attendance value
when those runtime producers are unavailable to this disjoint Gate-14 worker.

## Exact source contract

The two controls remain:

- first line: rectangle `(250,45)-(550,75)`;
- second line: rectangle `(250,70)-(550,86)`;
- style index **3**;
- native color `0xFFFF`;
- final render flags `0x2C`, horizontally and vertically centered;
- font: `Fonts\Zurich_XCn_BT_18pixel.fnt`.

The provenance-staged font is **79,734 bytes**, SHA-256
`968936a5f5e42c4dd321f0a1096a8668c8f9ca3bd0b86243b585190969c1b71a`.
Its decoded EA atlas is **1366 x 19** and its native line height is **20**.

## Centering and clipping

The generic TextControl center operation uses signed divide-by-two rounding
toward zero. For a control `(left, top, right, bottom)`:

```text
x = left + trunc_toward_zero((control_width - measured_text_width) / 2)
y = top  + trunc_toward_zero((control_height - native_line_height) / 2)
```

Therefore:

- the 30-pixel first-line control starts its 20-pixel native line at **y=50**;
- the 16-pixel second-line control starts the 20-pixel native line at **y=68**,
  then clips strictly to source rectangle y **70..85**.

That second-line clipping is intentional original behavior, not a modern
layout correction.

## Fidelity boundary

This checkpoint promotes only:

- exact style-3 font bytes;
- exact white-endpoint glyph alpha;
- exact centered line origins;
- exact control clipping;
- exact two-layer transparent 800x600 header raster construction.

It deliberately keeps false:

- automatic binding from modern runtime state to every required header field;
- global FastView z-order;
- complete flattened FastView frame;
- Gate 14 completion.

## Next step

After this raster checkpoint is verified, lift `direct_header_text` into the
existing FastView component raster set immediately after PossessionFigures and
before the FastViewScores subpanel family, following the already source-closed
outer draw order. Preserve unresolved cross-component overlaps rather than
choosing winners.
