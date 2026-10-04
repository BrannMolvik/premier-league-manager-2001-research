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

## English position localization source closure

Cell 2 no longer requires an inferred abbreviation. Helper `0x635EC0` indexes
the exact `Position*` pointer table at `0x849930` and resolves the selected
key through `0x6350D0`. That resolver has one dedicated global string object
per position key.

The source language initializer fills those objects by sequentially reading
uint16 entries from `English.idx`. The sequence is independently anchored:
`Versus` maps to English index entry 2257 and returns the expected source
string `"v"`; the same contiguous object/read order reaches
`PositionGK` at entry **2305**. Entries 2305..2323 resolve exactly to:

`GK, RB, LB, CD, SW, RWB, LWB, ANC, DM, RM, LM, CM, RW, LW, AM, RF, LF, CF, ST`.

That sequence exactly matches the executable's `PositionGK..PositionST` key
order. The raster therefore source-binds cell 2 for the canonical English
release and records `position_english_localization_recovered=true`. It does
not claim equivalent strings for other language resources.

## Own-goal color source closure

The final PlayerRow text-color blocker is also source-closed.

EventPlayerOwnGoal constructs its native color at `0x5268A5..0x5268E8` and
writes it through text-color setter `0x650480`. Only the channel pair
`0x98482C/0x984828` receives source intensity 255; the other two channels are
zero.

A generic packed-24-bit RGB conversion path at `0x434357` labels those same
three channel pairs directly:

- `0xFF0000` uses `0x98482C/0x984828`;
- `0x00FF00` uses `0x984838/0x984834`;
- `0x0000FF` uses `0x984844/0x984840`.

Therefore the own-goal text update is source-proven **pure red**. The clean
RGBA raster uses `(255, 0, 0, alpha)` for written cell 5.

Unwritten goal/own-goal cells still produce no text pixels, matching their
source lifecycle.

For the canonical English release, all six PlayerRow text cells are now
rasterizable when written. The result records
`position_english_localization_recovered=true`,
`own_goal_color_recovered=true`, and `complete_team_table_text=true`.
This completeness applies only to PlayerRow text, not to the whole TeamTable or
FastView frame.

The result does not claim global FastView z-order, cross-component blending,
background ownership, audio, or 3D choreography.

## Provenance

The executable used for the private style/alignment trace again matched
canonical SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No proprietary executable bytes or private disassembly are committed.
