# Gate 13 Settings modernization extension

_Status: implementation target for Recovery 385._

The shipped FM2001 PStartMenu remains the source of truth. Its four recovered
controls, rectangles, labels, source frames, and event IDs are not moved or
renumbered by this extension.

Gate 13 adds one intentional modernization control, **Settings**, in the unused
169x25 source-button slot at `(355,508)`. It reuses the exact verified
`button_type_1.444` 23-frame atlas and the provenance-tracked
`Zurich_BdXCn_BT_20pixel.fnt` renderer. The label is explicitly modern and is
not represented as a recovered English.idx string.

The first Settings surface is intentionally narrow:

- **Profile: Original/Custom** resets to the original baseline when activated.
- **Fullscreen: On/Off** exposes the display mode already supported by the
  Windows host.
- **Back** returns to the untouched PStartMenu.

The default application state is `Profile: Original` with fullscreen enabled,
which is the existing recovered-port baseline. No simulation, save-game,
database, match, or management state is changed by Settings. Advanced renderer,
resolution, scaling, and upscaling choices remain Gate-17 work and must be
explicit opt-ins when introduced.
