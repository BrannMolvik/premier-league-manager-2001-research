# Gate 13: first-hand authorized source-disc inventory

_30 September 2026. Evidence tier: confirmed original-source bytes. This note supersedes all earlier "container unavailable" statements as a current source-access status; historical logs remain historical._

## Authoritative original source and validation

The private authorized Library file is the same 511,121,336-byte ZIP recorded in `research/ORIGINAL_SOURCE_LOCATOR.md`. Direct checksum of its actual bytes on this recovery:

```
SHA-256 ZIP: 677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4
Outer ZIP nested disc: F.A. Premier League Football Manager 2001/famg2001.bin
Nested raw disc size: 631,627,248 bytes
CUE explicitly identifies TRACK 01 MODE1/2352 and INDEX 01 00:00:00
```

The raw image was successfully extracted into the private temporary workspace. A read-only, independent MODE1/2352 scanner verified the 12-byte synchronization prefix and mode byte of **all 268,549 physical sectors**; **zero bad sectors**. ISO volume descriptors at sectors 16–18 are valid; the highest supported filesystem is **Joliet level 3**. The independent scanner enumerated **2,456 files, 211 folders**, with **zero case-insensitive file-path collisions**. This is the *real supplied disc*, not a synthetic fixture.

Major top-level file counts: `FM2001_Art` 1,403; `ArtInGame` 590; `DataInGame` 252; `Data` 78; `reused_art` 23; `Setup` 22; `Fonts` 18; `FormationFiles` 9. Common extensions: `.444` 1,354; `.fsh` 351; `.sci` 235; `.fxd` 216; `.bnk` 64; `.bmp` 38; `.tga` 29.

**Recovery command for another worker:** resolve the *same private Library ID* from `ORIGINAL_SOURCE_LOCATOR.md`, materialize the ZIP, then run `reconstruction/gate13_source_inventory.py <source.zip> --deep --hash-source --output <private>/gate13-source.json`. Save the resulting complete catalog. This session's temporary independent catalog is at `/mnt/data/fm2001-work/real_disc_catalog.json` (current execution workspace only; never infer that path persists in a later container). Any later catalogue discrepancy must be investigated before importing new assets.

## Confirmed first-slice source paths and verified SHA-256

The original disc filesystem contains *named resources* strongly suggestive of PStartMenu and TeamSelect dependencies. Name/context is a discovery lead, **not yet proof of the exact executable-to-resource binding**. The following bytes were individually extracted from their exact Joliet extents and SHA-256 verified:

| Exact original disc path | Bytes | SHA-256 |
| --- | ---: | --- |
| `FM2001_Art/Generic/bground.444` | 222616 | `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9` |
| `FM2001_Art/Generic/main_menu/main_menu_bground.444` | 206164 | `297b54dbee7d7d31a081b1459ed497b251c2bf1aa00092976557d5b8065e7e4b` |
| `FM2001_Art/Generic/team_choice/background.444` | 179752 | `7927bc3baf35f2ee906f6ea714c77d0e51282ee5316ec43220edb95ed358694b` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444` | 55128 | `d204e7086a15ac15bd9d10377526ba40bb40ffd83b5f02ba39ef8404dd42922d` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_anim.444` | 19416 | `7f04cbe25499e26d2489781a7aa8c0135454dba5b9096ce4de580cf8bca32b88` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_team_but_bars.444` | 6224 | `a0fafa8af76c7dd9b873de77814517a2ac20d88a7d70392311e277d7547ff6ac` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444` | 22768 | `de53b9ed410bf0456e79c03b305cfb7a1ccaae4c10fb77a50fefd7106c2d4e22` |
| `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444` | 7372 | `bdf28df3c32275fa59934be8c85f1cea33626d47dc4f2b3e59619278c7ca73fa` |
| `FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444` | 45116 | `57ba72fd2a978735cbd4537aee4fa3031f13f10994067fb2ceba6c22c5ef41e3` |
| `FM2001_Art/Generic/GenericButtonsAndBars/exit_button.444` | 4864 | `3c317bbb4449a03efbeb867d1de4fd2e5b7d936f29d31f1c11af2092556fa0f9` |
| `FM2001_Art/Generic/team_choice/Divisions/premiership.444` | 22176 | `424bdc2fa9830c8e808a68edb64f1009050209beaa82a670584fe86aca9a5670` |
| `FM2001_Art/Generic/team_choice/country_flags/england.444` | 14376 | `b084452911fe4dd06f9dd4434f771f46909ee0a9344377004114c9d41a692091` |
| `FM2001_Art/Generic/team_choice/Info/info_1.444` | 31580 | `3a9c323c09fcf7cb8634ec778d6c58565481c463f419416c9f11540c77df41c9` |
| `FM2001_Art/Generic/team_choice/Info/info_2.444` | 39668 | `469332057728599740e7f21d8fa8c2f84f12c5f95890b7660b03241db74da1d2` |
| `FM2001_Art/Generic/Background_buttons/back_2_Premiership.444` | 18376 | `1766fc5eb3224f71c68d9a33b7d922230716198a807979af5039fe0247c8e5ac` |

Other original text/database anchors were also extracted privately and hashed: `English.str` (369644 bytes, SHA-256 `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`), `English.idx` (5428 bytes, `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1`), and `Resource.res` (2,114,750 bytes, `7abd0213aacede533af438296ecc67271ada8c16b69f2aacd96df9b8d050bb38`). These are *candidate lookup/label source files*, not proven PStartMenu bindings.

## Validated proprietary image headers

The first two little-endian unsigned words of extracted `.444` images decode as apparent pixel dimensions:

- `bground.444` **800 × 600** and checksum exactly matches the project's earlier first-hand expected source (independent confirmation).
- `main_menu_bground.444` **532 × 532**.
- `team_choice/background.444` **800 × 558**.
- `choice_start_anim.444` **150 × 224**.
- All sampled `.444` images share bytes `64 FF 00 FF` immediately following the dimensions; the compressed pixel stream still needs confirmed decoding, including transparency and frame/animation handling. Do not relabel image dimensions as UI coordinates.

## Next verified Gate 13 work

1. Persist a reproducible full catalog plus source checksum outside the volatile container if possible; the real-disc inventory result above is already durable here.
2. Extract/decode the authentic `.444` first-slice backgrounds and animations, testing against known original-screen screenshots without inventing design elements. Correlate the original executable/layout references before assigning specific controls.
3. Deliberately import only correlated original bytes under `original_assets/` via `gate13_asset_import.py --inventory-report` and document SHA/provenance in `MANIFEST.md`.
4. Bind the decoded original presentation to the already-tested `front_end_state.py` and `front_end_session.py` seam, then continue with the next source-backed management screen.
