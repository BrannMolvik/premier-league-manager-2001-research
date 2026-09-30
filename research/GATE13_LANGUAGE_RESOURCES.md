# Gate 13: recovered original EAUK STR/IDX language resources

_30 September 2026. Confirmed from bytes extracted from the owner's authorized original FM2001 disc. The interpretation of how the executable maps each UI widget to a specific IDX position is a separate pending xref task._

## Source identities and SHA-256

- `English.str`: **369,644 bytes**;
  SHA-256 `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.
- `English.idx`: **5,428 bytes**;
  SHA-256 `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1`.
- `EnglishEAM.str`: **298,747 bytes**;
  SHA-256 `98387ef673e87a02cf2cab7349770a4415f29fd381877b603922302c3e3f174f`.
- `EnglishEAM.idx`: **5,754 bytes**;
  SHA-256 `bd0e2b804f1ce85011509ff828cdc70f2409509537ec61a012d1fa0175932367`.

These are original disc **root paths**, not reconstructed UTF-8 or mock-language fixtures.

## Verified `.str` binary layout

```text
+0 u32le payload_size
+4 u32le number_of_strings
+8 byte[payload_size] NUL-terminated CP1252 strings, directly concatenated
+8+payload_size u32le[number_of_strings] payload-relative byte offsets
EOF exactly 8 + payload_size + 4*number_of_strings
```

The offsets are strictly ascending; offset[0] is zero; each next offset starts immediately after the previous NUL terminator; the last string's terminator ends the payload. All **21,856** extracted English strings and **1,609** EnglishEAM strings decode strictly as CP1252 and meet every invariant.

Measured original headers:

| File | u32 payload bytes | u32 strings | Expected == actual bytes |
| --- | ---: | ---: | ---: |
| `English.str` | 282212 | 21856 | 369644 |
| `EnglishEAM.str` | 292303 | 1609 | 298747 |

## Verified `.idx` layout

Each `.idx` is a packed sequence of **little-endian uint16 indices into the companion `.str` offset table**, **not direct string-byte offsets**. Duplicates are intentional. All 2,714 indices of `English.idx` fall within 0–21,855, and all 2,877 indices of `EnglishEAM.idx` fall within 0–1,608.

The first original `English.idx` entries decode through `English.str` to the following exact text, demonstrating that the menu-label data is accessible without redrawing or retyping strings:

| IDX position | STR string ID | Exact original text |
| ---: | ---: | --- |
| 0 | 19608 | Continue |
| 1 | 19609 | Start New Game |
| 2 | 19610 | Load Game |
| 3 | 19611 | Save Game |
| 4 | 19612 | Settings |
| 5 | 19613 | Virtual Managers |
| 6 | 19614 | Quit to Windows |
| 7 | 19615 | Main Menu |
| 8 | 19616 | Team Selection |

Additional source examples: STR ID 19617 = Delete Game; 19618 = SFX; 19619 = Speech; 19620 = FMV; 19621 = Fade Speed; 19622 = Match View. `English.idx` also repeats earlier entries for related submenus, confirming the necessity of a distinct index-lookup layer.

## Implementation and verification

`reconstruction/ea_language_strings.py` implements the validated two-file grammar, strict CP1252 decoding, relative offsets, duplicate IDX references and fail-closed malformed-resource checks. `reconstruction/test_ea_language_strings.py` has synthetic normal/corruption tests and an optional exact-hash **licensed original** test enabled only by `FM2001_ORIGINAL_LANGUAGE_DIR`, so original resource bytes are not silently bundled into CI.

Independent local test against actual source data passed for **both** language pairs, all counts and all first-nine menu labels; a separate synthetic malformed-resource sanity pass also passed. The normal GitHub full and focused workflows are intentionally explicit/manual to conserve Actions minutes, so do not claim a new hosted CI green run unless it was genuinely launched and checked.

## Gate 13 implications / next steps

1. Wire these original resource bytes through a narrow presentation-only loader once the actual assets are intentionally provenance-imported. Avoid hardcoding source strings as replacement UI content.
2. Recover executable references that associate menu widgets with the exact original IDX positions and control/event IDs. The observed menu-label order is strong corroborating evidence but **not proof** of final widget placement.
3. Keep recovering the proprietary `.444` graphics/animation decoder; only then bind original layout and visual assets to the already-tested `front_end_session.py` state seam.
