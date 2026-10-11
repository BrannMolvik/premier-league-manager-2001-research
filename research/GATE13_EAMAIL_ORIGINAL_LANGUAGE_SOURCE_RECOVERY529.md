# Recovery529: original EAM localization resource recovery and native message-text boundary

11 October 2026 KST. **Gate13 remains OPEN.** Original .str/.idx file bytes were directly downloaded from Daniel's unshared extracted-disc filesystem in Google Drive. These are authorized targeted game source resources, not the 511 MB ZIP or 632 MB BIN, and not a replacement subtitle file. Nothing was executed.

## Verified exact original source and provenance

Original private Drive extracted game root `FM2001/`, original filenames **`EnglishEAM.str`** and **`EnglishEAM.idx`**:

| Item | Original length | SHA-256 of actual bytes | Git binary-blob SHA-1 | Private source ID |
| --- | ---: | --- | --- | --- |
| `EnglishEAM.str` | 298,747 | `98387ef673e87a02cf2cab7349770a4415f29fd381877b603922302c3e3f174f` | `e57d905667d3ef738e99933f2c7787c97ddc0424` | `1l1kH5j1GTLLQZpZzzvFKMOx384mzq0rX` |
| `EnglishEAM.idx` | 5,754 | `bd0e2b804f1ce85011509ff828cdc70f2409509537ec61a012d1fa0175932367` | `f6cd2fe78b8e8ca2ea641f876a58197509c3f46b` | `11XjOAadbWE72RITu3W-cTqW_bp3rtomt` |

Original `EnglishEAM.str` begins with little-endian payload size **292,303 bytes** and unique-string count **1,609**; `8 + 292303 + 4*1609 = 298747` exactly. The text payload uses NUL-terminated CP1252 strings. The index data is **2,877 original little-endian uint16 references**, ranging over `0..1608`, **not byte offsets**. The existing verified `ea_language_strings.parse_language_pair` parses these actual files as-is. The exact original language contains player transfer-request textual templates, but a substring match is **not evidence** that one such row is the chosen original message at runtime.

The two files were intentionally staged byte-for-byte under `original_assets/source/` via the authenticated GitHub binary blob/tree API, without text reserialization, and both Git blob IDs exactly matched hashes independently computed over the original Drive-fetched bytes. `original_assets/MANIFEST.md` records each source and SHA. All other original executable/files/disc packages remain outside Git.

## Original text object source chain and remaining precise source questions

The independently verified original `footballmanager.exe` 4,714,541-byte SHA-256 is `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Static native source `0x41B63F..0x41B64D` calls `EAMPlayerAskTransferListsub` constructor `0x56FAD0` with native effective manager key and source player identity; `0x5CE660` embeds kind1 manager and kind2 player typed descriptors in record `+0x10` and `+0x1C`. Original native virtual **`+0x18→0x56FB70`** formats a distinct language-backed returned string via language buffer `0x947AA0` and resource pointer `0x8797A4`; virtual **`+0x1C→0x56FBA0`** is the separate elaborate message body/action formatter. Original `0x5CE6A0` type2 branch `0x5CE715` resolves original player/name/associated manager through `0x417AE0` and `0x40DA70` before writing a localized formatted string. These prove owner references and subtype construction, **NOT the concrete `EnglishEAM.idx` selector for either message field or original GUI text layout/color**.

Required next trace: follow `0x8797A4` initialization `0x5C1438` and language-loader source/IDX entry; trace the exact `0x56FB70` return formatter, `0x56FBA0` body variants and `PMessageRow` text source `0x471D20`/font wrappers. Then use the source-exact template/typed manager/player formatting to implement genuine visible row subject/body with original row art and native buttons. The combined 10-filter/5-sort source-qualified small-list window was merged in PR610, **but it is not a rendered Inbox**.

## Port boundary, tests and non-effects

`reconstruction/original_eamail_language.py` only authenticates/loads the exact source pair and exposes `source_selected_template(idx_entry,original_selector_proven=True)`. A caller may pass an index **only after independently proving that original native selector for the specific message**; otherwise it fails closed rather than guessing one of multiple transfer-related text strings or using an English modernization substitute. Automated source tests check original binary SHA/length/count/IDX linkage and corruption/unknown selector refusal; the original `.str` is source data, not a row-ready caption. No code here sends messages, modifies original saves or unlocks unsupported native sort modes. Original resource bytes are explicitly authored assets, not compiled executable, disc image, archive or whole-game extraction.

**SOURCE-VERIFIED:** exact original resource identities, binary format, native typed manager/player record constructor and two text-provider virtual ownership addresses. **INTEGRATION-VERIFIED:** only if exact PR-head tests pass. **VISIBLE-ACCEPTED:** NO. Original Inbox actions, sorting >16, fonts/rows, navigation, PEAMMessage modal, 2–6 users, all-country/league game and Win11 release remain OPEN.
