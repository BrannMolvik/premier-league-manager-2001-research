# Gate 13: pinned original first-screen source recovery

_30 September 2026. This is a repeatable extraction/verification plan, NOT
a claim that all selected original bytes are already checked into Git._

## Why this limited slice exists

The canonical source ZIP is retained privately at the Library identity in
`research/ORIGINAL_SOURCE_LOCATOR.md`. The working port already has a verified
EA444 decoder, original language and bitmap-font parsers, both first-screen
background composers, exact menu and TeamSelect action rectangles, exact
font-mask preparation, 23-source-frame button atlas extraction, and a tested
presentation/session bridge. Most source assets still need intentional
provenance import. Do not ship or commit the full original ZIP/BIN or the
original executable merely to complete the first-screen asset stage.

`research/GATE13_FIRST_SCREEN_EXACT_PATHS.txt` is the narrow,
executable-correlated source selection. Every SHA below was previously
independently obtained from the authorized original, not calculated from
replacement artwork:

| Original source path | Pinned original SHA-256 | Status |
| --- | --- | --- |
| `FM2001_Art/Generic/bground.444` | `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9` | Shared 800x600 first-screen layer |
| `FM2001_Art/Generic/main_menu/main_menu_bground.444` | `297b54dbee7d7d31a081b1459ed497b251c2bf1aa00092976557d5b8065e7e4b` | Proven menu overlay |
| `FM2001_Art/Generic/team_choice/background.444` | `7927bc3baf35f2ee906f6ea714c77d0e51282ee5316ec43220edb95ed358694b` | Proven TeamSelect overlay |
| `FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444` | `57ba72fd2a978735cbd4537aee4fa3031f13f10994067fb2ceba6c22c5ef41e3` | 169x575 atlas, 23 source frames |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444` | `d204e7086a15ac15bd9d10377526ba40bb40ffd83b5f02ba39ef8404dd42922d` | 150x736 TeamSelect action atlas, 23 source frames |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444` | `de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22` | Verified source binding for hierarchy rows, frame-state semantics pending |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444` | `bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa` | Verified source binding for hierarchy rows, row content/mapping pending |
| `Fonts/Zurich_BdXCn_BT_20pixel.fnt` | `47e3b21f07a3013ba19d257f31e1e876c9b03856c930a8fa5fe58103974ed166` | Recovered authentic menu font |
| `English.str` | `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601` | Original 21,856 English strings |
| `English.idx` | `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1` | Original 2,714 English string references |

The original executable is a private reference only, independently verified
SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
It is intentionally absent from the first-screen import list.

## Exact commands after execution access is restored

The authoritative ZIP is 511,121,336 bytes with SHA-256
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
Materialize the **same** private Library file, not an unrelated public copy.
From the repository root, use distinct temporary paths outside Git:

```text
python reconstruction/gate13_source_inventory.py "<private-source>.zip" --deep --hash-source --extract-path-file research/GATE13_FIRST_SCREEN_EXACT_PATHS.txt --only-explicit --require-all-explicit --extract-candidates-to "<private-staging>" --output "<private-selection>.json"

python reconstruction/gate13_first_screen_selection.py "<private-selection>.json" "<private-staging>"
```

The second command checks canonical ZIP identity and size, an exactly matched
ten-path explicit inventory, one verified original-disc extraction candidate
per path, and independently hashes every staged file. It refuses partial,
duplicate, unrelated, altered or broad extractions. Do **not** bypass it if
the original bytes do not match the above receipt.

Only after validation, use the existing asset importer separately for each
deliberately selected original file, for example:

```text
python reconstruction/gate13_asset_import.py "<private-staging>" "FM2001_Art/Generic/bground.444" --inventory-report "<private-selection>.json" --repo-root . --notes "Byte-identical canonical original first-screen resource."
```

Repeat only for the verified ten-path list. The importer uses the same source
receipt and updates `original_assets/MANIFEST.md` with provenance. Verify the
manifest and repository hygiene guard afterward. If interrupted after some
files are imported, inspect already-imported original bytes and manifest rows;
do not overwrite duplicates blindly.

To run the existing opt-in first-hand tests, set
`FM2001_ORIGINAL_EXE` to the matching private executable,
`FM2001_ORIGINAL_444_ROOT` to `<private-staging>/FM2001_Art`,
`FM2001_ORIGINAL_FONT_20` to the staged font, and
`FM2001_ORIGINAL_LANGUAGE_DIR` to the staging root before running focused
unit tests locally. Hosted synthetic CI does **not** prove the newly extracted
licensed art pixels. Preserve the original menu/TeamSelect background RGBA
hash regressions and inspect the resulting original images directly.

## Private exact-pixel reference export once source staging succeeds

The renderer inputs now have a lossless standard-library PNG export for
comparing exact source pixels with the old game's screen references. This is
**not** a reconstruction of the unrecovered native button frame selection,
caption coordinates/colors, hierarchy row contents or original timing.

After the canonical source archive passes the exact-path validator above,
the complete 10-file staging root and separately verified canonical
original executable can drive the preview (paths here are examples only):

```text
python reconstruction/gate13_original_pixel_preview.py --original-exe "<private-executable>" --original-art-root "<private-staging>/FM2001_Art" --original-language-root "<private-staging>" --original-font20 "<private-staging>/Fonts/Zurich_BdXCn_BT_20pixel.fnt" --output-dir "<new-private-folder-outside-Git>"
```

Both screen background images are composed from the exact decoded originals
and retain pixelwise RGBA through lossless PNG encoding. Each 23-frame
PStartMenu/TeamSelect action atlas is exported once in **unmapped source
order**; available hierarchy animation/bar frames are also exported
separately. Original Zurich menu glyph **alpha masks** are exported as
uncolored PGM to avoid inventing native font color or placement. The
accompanying JSON lists previously source-backed event rectangles, exact
language IDX positions, original asset SHA identities and per-frame RGBA
digests. Unresolved native interaction state and glyph appearance are null,
not invented visual defaults.

The exporter rejects output inside Git and refuses overwriting previous
private diagnostics. Ordinary CI validates synthetic RGBA/PNG bit-preserving
roundtrips; only opt-in tests with the canonical original assets can prove
the actual first-screen background/image hashes. Review the exported
original pixel previews alongside original gameplay references, then
continue the executable Button@ease trace before promoting interactive
screen fidelity.

## Open source-recovery boundary

Native Button@ease_2001 23-frame state selection, Zurich caption
placement/color and TeamSelect hierarchy control content still require
direct original executable/source evidence. They must not be inferred
from atlas frame count, guessed visual themes, or substitute fonts.

The current worker's shell/Python containers returned `ClientError` even
for trivial commands. This selection and its source-hash validator can be
committed and tested independently, but no new real ZIP staging/import or
first-hand disassembly is claimed until execution access genuinely recovers.
The full Gate 13 through Gate 17 mission remains active.
