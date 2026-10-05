# Gate 13 final management header and ordinary-text adjudication

This note records the final bounded Gate-13 source adjudication used by the
live management host. Raw executable disassembly and the authorized source
archive remain outside Git.

Canonical identities:

- source archive SHA-256:
  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`;
- canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`;
- final private trace SHA-256:
  `7fdf1a539a2a5da916afc81e634d0ac399e92e461e8f200be82b54880dc63ae4`;
- approved three-file asset-bundle SHA-256:
  `70addedecfda3a0212bd2e4b0f06f9409861335dee310f88f835ac4721dcff32`.

## Event-2 management header

The application-owned compound is constructed at screen
`(599,0,100,95)`.

- `back_4_anim.444`: 30x4845, child rect `(599,0,30,95)`,
  SHA-256 `867abd21e89b21c878d20777547524e8ea4a00fcc9b49524f8356b631a665f69`;
- `back_4.444`: 70x380, child rect `(629,0,70,95)`,
  SHA-256 `710016aa4f9c2d5a04580ba48e2449882040482d231b875726203836b8cb42bb`;
- caption rect `(631,62,70,30)`, style 10, font object `0x8B0760`;
- English global `0x9820F4` resolves to English.idx 2497, exact text
  **MENU**;
- font object `0x8B0760` is bound to
  `Fonts/Zurich_XCn_BT_24pixel.fnt`, SHA-256
  `f165d39423a9f20532132d2bd9a3c53aba4244531aa3291a73502fa956a46405`.

The management-specific group methods and shared picture selector establish
left group lengths `(26,1,0)` and right group lengths `(2,1,1)`.
The live host therefore uses left source rows 0..25 for the ordinary animated
group, row 50 for the one-frame selected group, no left bitmap for the
zero-length disabled group, and right rows 0..3 for its 2/1/1 groups.

The shared source update path uses the same recovered enabled/inside/selected
bits and serialized UI-pass cadence already qualified for Gate 13. The Tk host
advances one source update per eligible idle pass; it does not introduce a
millisecond animation timer.

## Ordinary League Tables row text

The final trace closes the visible `PLeagueTableRow::0x446930` typography.

The canonical font-wrapper branch calls `0x6596A0`. Earlier canonical source
work proves that helper always returns zero, so the ordinary branch is the
reachable branch. In that branch runtime slot `0x947578` contains font object
`0x9269F0`. The already-qualified PMenu font-loader evidence binds
`0x9269F0` to exact original
`Fonts/Zurich_BdXCn_BT_16pixel.fnt` (SHA-256
`9dc371caba34823b0d6ba6fd4c5e82f94775de1168daa5dad936b70a6e4f9732`).

For each visible row:

- rank and all seven numeric controls pass raw flags `0x24`, recovered as
  horizontal-center + vertical-center;
- club name passes raw flags `0x21`, recovered as left + vertical-center;
- visible row controls pass native endpoint color `0xFFFF`;
- rank/name/stat rectangles and 16-pixel row step remain the previously
  recovered `CLeagueTableList/PLeagueTableRow` geometry;
- row values come only from the immutable source-backed table snapshot,
  including original `Pts = 3*W + D`.

`original_management_text.py` checksum-gates that exact font, rasterizes the
source glyph alpha, applies the recovered line-origin arithmetic and clips each
glyph plane to the original 12-pixel-high control rectangle. The live 800x600
management host draws those layers below the PMenu popup, so ordinary table
data is no longer represented only by presenter objects.

## Squad typography boundary retained fail-closed

The same final trace also resolves the relevant font identities without
requiring a new Gate-13 implementation guess:

- `PSquadPlayerRow` references slot `0x94758C`; the reachable ordinary
  wrapper is `0x87BE90`, independently source-bound in Recovery 200 to
  `Fonts/Zurich_BdXCn_BT_18pixel.fnt`;
- `PSCFRow` directly uses font object `0x8CAB80`, already source-bound to
  `Fonts/Zurich_XCn_BT_16pixel.fnt`.

The `PSCFRow` controls compute packed native colors dynamically from source
values before calling the shared text helper. Those color transforms are not
needed to prove the bounded ordinary League Tables data/text slice and are not
replaced with white or a modern palette. Likewise unresolved Squad
status-icon/club-relative-assignment styling remains fail-closed. Per the fixed
Gate-13 closure slice, secondary/pixel-perfect refinements belong to Gate 15
rather than reopening a broad presentation sweep.

## Asset provenance

The three final header files are byte-identical imports under
`original_assets/source/` and are recorded in `original_assets/MANIFEST.md`.
The private bundle excludes `footballmanager.exe`; no executable, archive,
raw disassembly or temporary reverse-engineering report is tracked.
