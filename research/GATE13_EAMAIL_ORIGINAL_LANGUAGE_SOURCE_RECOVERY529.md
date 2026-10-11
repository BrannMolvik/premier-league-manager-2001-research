**11 October 2026 Recovery530 corrective source note:** The historical #613 section near the end of this document mislabeled native `0x667E90` as `fwrite` and left `0x8797A4` source index unknown. Full native byte-direction/caller trace now proves **`fread`**, English original `englisheam.idx` selected at `0x50D55E`, exactly 2,877 native u16 index loads at `0x5B65A0..0x5CE3EA`, and `0x8797A4` = IDX ordinal **1313**, original string942 **Transfer List**. See [Recovery530 exact native original proof](GATE13_EAM_TRANSFER_LIST_TITLE_NATIVE_RECOVERY530.md). The old hypothesis below is retained only as a superseded research record; **do not rely on its fwrite/source-unknown claim**.

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


## Follow-on source correction: native 0x8797A4 pointer-table owner is not proved to initialize EAM captions

A deeper disassembly of the same authorized unchanged original executable
identified an important counterexample to calling `0x5C1438` a *startup
caption initialization* site merely because it assigns `0x8797A4`.

- Native `0x64E320..0x64E335` reads a source pointer table at
  `arg0+0x08`, masks a supplied `arg1` to **16 bits**, computes
  `table_base+(index&0xFFFF)*4`, and stores the resulting **pointer**
  in the destination object at `ECX`. The value in `0x8797A4` thus
  references a pointer-table entry rather than proving an immediate
  `EnglishEAM.idx` index/string literal.
- The preceding original `0x5C1422..0x5C1444` invokes
  `0x667E90` with an output file/stream handle. Independently
  disassembled `0x667E90/0x667EBF` are CRT-style buffered
  **write/fwrite** helpers, not a source localization lookup.
  The enclosing owner may be a source persistence/serialization
  path; its caller and whether this is load or save remain
  **UNKNOWN** until the complete producer/consumer is traced.
- The fact that `EAMPlayerAskTransferListsub` virtual
  `+0x18→0x56FB70` later dereferences `0x8797A4` remains
  **SOURCE-VERIFIED**. Its actual pointer-table base, constructor
  category-label selection, data-file mapping and displayed
  text bytes are **not yet established**. Do not hardcode a guessed
  `EnglishEAM.idx` index or convert the write-path assignment
  into fabricated new-game startup semantics.

Reproduce privately:
```sh
objdump -d -M intel --start-address=0x64e320 --stop-address=0x64e338 footballmanager.exe
objdump -d -M intel --start-address=0x5c1400 --stop-address=0x5c1466 footballmanager.exe
objdump -d -M intel --start-address=0x667e90 --stop-address=0x667f80 footballmanager.exe
```

Next trace must inspect `0x5C14xx` *callers*, actual table owner/locale
lookup and `0x8797A4` initialization before the first native EAM row,
while preserving the verified original EnglishEAM byte assets separately.
This audit corrects a potential false source inference, not a new port
implementation, runtime observation or Windows11 acceptance.
