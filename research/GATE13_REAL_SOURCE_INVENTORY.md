# Gate 13 Real Source Inventory

_Date: 30 September 2026_

## Status

**Confirmed from first-hand bytes of the authorized original source.**

This note records the first successful Gate-13 inventory of the durable private
511,121,336-byte source archive after the earlier CAAS execution outage cleared.
No source archive or uncontrolled extraction dump is committed here.

## Canonical source identity

Private Library source:

`/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`

Verified properties:

- byte size: **511,121,336**;
- SHA-256:
  **`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`**;
- outer ZIP file count: **3**.

Outer ZIP members:

| Path | Uncompressed bytes |
| --- | ---: |
| `F.A. Premier League Football Manager 2001/famg2001.bin` | 631,627,248 |
| `F.A. Premier League Football Manager 2001/famg2001.cue` | 77 |
| `F.A. Premier League Football Manager 2001/fltfm2k.nfo` | 5,081 |

The BIN is exactly **268,549 MODE1/2352 physical sectors**. Every physical
sector was validated for the expected sync pattern and Mode-1 byte before
filesystem evidence was accepted.

The highest available Joliet supplementary volume descriptor is level **3**.
The Joliet filesystem contains **2,456 files**.

## Disc shape

Largest top-level families:

| Root | Files |
| --- | ---: |
| `FM2001_Art` | 1,403 |
| `ArtInGame` | 590 |
| `DataInGame` | 252 |
| `Data` | 78 |
| `reused_art` | 23 |
| `Setup` | 22 |
| `Fonts` | 18 |
| `FormationFiles` | 9 |
| `FMV` | 4 |
| `Stadium` | 2 |

Largest suffix families include:

- **1,354** `.444` files;
- **351** `.fsh` files;
- **235** `.sci` files;
- **216** `.fxd` files;
- **64** `.bnk` files;
- **38** `.bmp` files;
- **29** `.tga` files.

This proves that original management presentation is overwhelmingly available
as source material rather than needing a replacement UI.

## Canonical executable re-verification

The disc file `footballmanager.exe` was extracted directly from the validated
Joliet filesystem:

- bytes: **4,714,541**;
- SHA-256:
  **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**.

This exactly matches the executable identity already used by the reverse-
engineering research.

## First-slice source assets

### Global startup background

`FM2001_Art/Generic/bground.444`

- bytes: **222,616**;
- SHA-256:
  `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`;
- header dimensions: **800 x 600**.

This independently re-verifies the earlier Gate-2 presentation evidence.

### PStartMenu background

`FM2001_Art/Generic/main_menu/main_menu_bground.444`

- bytes: **206,164**;
- SHA-256:
  `297b54dbee7d7d31a081b1459ed497b251c2bf1aa00092976557d5b8065e7e4b`;
- `.444` header dimensions: **532 x 532**.

The canonical executable contains the literal source path
`fm2001_art\\generic\\main_menu\\main_menu_bground.444`.

### TeamSelect background

`FM2001_Art/Generic/team_choice/background.444`

- bytes: **179,752**;
- SHA-256:
  `7927bc3baf35f2ee906f6ea714c77d0e51282ee5316ec43220edb95ed358694b`;
- header dimensions: **800 x 558**.

The canonical executable contains the literal source path
`fm2001_art\\generic\\team_choice\\background.444`.

## Confirmed TeamSelect asset family

The executable string table contains the TeamSelect base directory plus
country-flag/division paths and the exact original choice-control art paths.

Verified first controls:

| Source path | Bytes | SHA-256 |
| --- | ---: | --- |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444` | 55,128 | `d204e7086a15ac15bd9d10377526ba40bb40ffd83b5f02ba39ef8404dd42922d` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_anim.444` | 19,416 | `7f04cbe25499e26d2489781a7aa8c0135454dba5b9096ce4de580cf8bca32b88` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_bars.444` | 6,224 | `a0fafa8af76c7dd9b873de77814517a2ac20d88a7d70392311e277d7547ff6ac` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444` | 22,768 | `de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444` | 7,372 | `bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa` |

The TeamSelect source tree is concrete rather than hypothetical:

- `FM2001_Art/Generic/team_choice/background.444`;
- **8** country flag resources;
- **4** division resources;
- **2** info resources;
- **99** badge resources;
- **41** stadium resources.

Examples independently extracted and hashed:

- `country_flags/england.444`:
  `b084452911fe4dd06f9dd4434f771f46909ee0a9344377004114c9d41a692091`;
- `Divisions/premiership.444`:
  `424bdc2fa9830c8e808a68edb64f1009050209beaa82a670584fe86aca9a5670`;
- `Info/info_1.444`:
  `3a9c323c09fcf7cb8634ec778d6c58565481c463f419416c9f11540c77df41c9`;
- `Info/info_2.444`:
  `469332057728599740e7f21d8fa8c2f84f12c5f95890b7660b03241db74da1d2`.

## Original menu strings

The extracted original `English.str` is:

- bytes: **369,644**;
- SHA-256:
  `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.

It contains one contiguous front-end string run including:

`Continue\0Start New Game\0Load Game\0Save Game\0Settings\0Virtual Managers\0Quit to Windows\0Main Menu\0Team Selection\0Delete Game`

Therefore the PStartMenu labels previously seen only in secondary screenshots
are now backed by the original authorized localization resource.

The same file directly contains `F.A. Premier League`, `Division 1 (ENG)`,
`Division 2 (ENG)`, `Division 3 (ENG)`, `Conference`, and multiple
`Start Game` strings required by TeamSelect.

## .444 decoder boundary

First-hand inspection plus executable disassembly confirms:

- bytes 0..1 = little-endian width;
- bytes 2..3 = little-endian height;
- byte 4 is passed as the image quant/format control;
- the compressed bitstream begins at byte **8**;
- Loader444 decode entry is `0x68598A`;
- conversion setup is `0x6864A0`;
- block decode/render entry is `0x6868E0`;
- the bitstream helpers live in executable CSEG around `0x7B9000`.

The file header matches the broad Electronic Arts TQI packet shape, and modern
FFmpeg recognizes dimensions when forced to `eatqi`. However, FFmpeg's
standard TQI decoder is YUV420 and reports damaged AC data on these files,
yielding invalid green images. The original `.444` path uses a different
block/chroma variant, so **do not use the failed FFmpeg render as a converted
asset**.

The bundled official FM2001 editor manual independently documents that the
original editor can export `.444` graphics to BMP and import BMP/TGA back
into the game. This establishes that lossless-enough source conversion is an
original supported workflow; the remaining port task is to reproduce the
decoder compatibility layer rather than redraw the UI.

## Exact next step

1. Port/recover the original Loader444 block decoder sufficiently to convert
   the verified PStartMenu and TeamSelect assets to a modern renderable form.
2. Regression-test decoded dimensions and deterministic pixels/hashes.
3. Intentionally import the minimum original first-slice source assets with
   source-inventory receipts and archive SHA provenance.
4. Bind those decoded originals to the already tested
   `front_end_session.py` navigation/application seam.
5. Continue Gate 13 outward through the roadmap's management-screen order.
