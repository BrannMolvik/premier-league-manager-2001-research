# Gate 14 partial PlayerRow text raster

_Status: source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The PlayerRow text renderer is now source-closed far enough to rasterize the
literal/default-color subset without borrowing PossessionFigures styling.

Private tracing of the canonical executable proves that all six PlayerRow text
controls use source text style **3**. Style 3 maps through `0x527BA0` to
wrapper `0x87BE30`, whose font object is loaded from:

`Fonts/Zurich_XCn_BT_16pixel.fnt`

The staged original font is reverified as:

- 75,217 bytes;
- SHA-256 `e0fbe91421642a489721ab167ce3d2db1738802ef0f1e198df3c90ce25ec3d18`;
- atlas 1261x17;
- native line height 18.

The generic text constructor supplies native color `0xFFFF`.

## Alignment and clipping

The six raw constructor flags are:

`[0x24, 0x24, 0x21, 0x21, 0x21, 0x24]`

Native renderer `0x64F090` resolves them as:

- `0x24`: horizontal-center + vertical-center;
- `0x21`: left + vertical-center.

The recovered PlayerRow controls are 16 pixels high while the source font line
height is 18. Native vertical centering therefore starts the line one pixel
above the control rectangle and relies on control clipping. The reconstruction
preserves that clipping; it does not shrink or scale the font.

## Safe raster subset

`gate14_fastview_team_text_raster.py` rasterizes only values already retained
as literal text and still using the constructor's default white color:

- cell 1: shirt/squad number;
- cell 3: player display name;
- cell 4: goal count, only after its typed callback wrote text;
- cell 6: form.

The raster loads and checksum-verifies the staged font internally, so a caller
cannot substitute a same-shaped font while retaining the canonical source hash.

## Explicit unresolved cells

Two channels remain fail-closed:

- cell 2 retains a source `Position*` localization key, but that key has not
  yet been bound to the exact selected language-table string;
- cell 5, when written by EventPlayerOwnGoal, receives a native source color
  update whose 16-bit pixel-format meaning is not yet RGBA-bound.

Unwritten goal/own-goal cells produce no text pixels, matching their source
lifecycle.

The result records rendered cell identities and explicit unresolved cell
records. It does not claim complete TeamTable text, global FastView z-order,
cross-component blending, background ownership, audio, or 3D choreography.

## Provenance

The executable used for the private style/alignment trace again matched
canonical SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No proprietary executable bytes or private disassembly are committed.
