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


---

## Recovery 411 source-evidence supersession (8 October 2026 KST)

**The 18-pixel font attribution and its y=50/y=68 placement calculations above
are historical, superseded claims. Do not use them to implement or validate
the direct FastView header.** Recovery 375 independently followed the
canonical original executable's selector-3 initializer: dispatcher selector
3 returns wrapper 0x87BE30, associated with font object 0x8CAB80; path
literal 0x839E30 is built at 0x6044AC and loaded at 0x6044F9
through 0x657650. That source path is
Fonts\Zurich_XCn_BT_16pixel.fnt, **not** the earlier 18-pixel file.
The 18-pixel literal at 0x839E10 belongs to a different font object,
0x8BD970. See the dated Recovery 375 correction in
research/GATE14_FASTVIEW_DIRECT_HEADER_TEXT.md.

The corrected, provenance-staged style-3 font is **75,217 bytes**,
SHA-256 e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18,
with **1261 x 17** atlas and **18-pixel** native line height. Thus the
original (250,45)-(550,75) header line centers at **y=51**, and the
(250,70)-(550,86) line at **y=69** before clipping to y=70..85.
The current implementation and corresponding tests in
reconstruction/gate14_fastview_direct_header_raster.py and
reconstruction/test_gate14_fastview_direct_header_raster.py use this
corrected font contract. The independent header plane was integrated
into the FastView component set as documented in
research/GATE14_FASTVIEW_DIRECT_HEADER_COMPONENT.md, after possession
figures and before score planes, without guessing cross-component overlap.

This is a **static reconciliation of previously verified executable/source
evidence and currently committed code/tests**, not fresh source
disassembly, new test execution, Windows GUI acceptance, or a newly
complete FastView frame. Runtime metadata binding, overlap fidelity,
and complete FastView presentation remain unresolved; Gate 13 still
requires genuine Windows 11 transport/DPI and normal-play acceptance;
Gates 14-17 and the Windows 11 release remain incomplete.
