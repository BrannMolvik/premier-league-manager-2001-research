# Original-file fidelity sweep — canonical Gate-13 native Squad / EAMail recheck

_9 October 2026 KST. Audit-only original-source investigation. This is the first post-directive original-byte checkpoint, NOT a claim of original-look acceptance or a gate closure._

## Reproducible provenance — reverified privately this session

- Authorized original ZIP (Library): `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`, **511,121,336 bytes**, SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
- Inner `famg2001.bin`: **631,627,248 bytes**, raw Mode1/2352. ISO9660 sector 17 has Joliet supplementary volume descriptor; root catalog at sector **255**, 4096 bytes. Data sectors read at `2352 * lba + 16` with 2048 user bytes. The root `footballmanager.exe` occurs at LBA **260425**, length **4,714,541 bytes** and hashes to SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**.
- Private original source, extracted bin, disassembly, and derivative image files stayed under `/mnt/data/fm2001_private/` **outside Git**. The Git checkpoint contains only these research findings and ledger changes. No execution of the original program or Windows GUI playtest was performed.
- For the reproducible disassembly use standard GNU `objdump -d -M intel --start-address=... --stop-address=... footballmanager.exe`. Its original `.text` virtual start is `0x401000`; `.rdata` virtual start `0x7BD000`. VA-to-file-offset for those sections is `va - 0x400000`. Vtable slots can be independently read as 32-bit little-endian pointers from the hash-gated executable.

## A. Squad — independently verified class identity and final dispatch

**EXACT / original-proven narrow findings:**
- Final populated row factory at `0x4B6E80` calls parent setup `0x48A8E0` at `0x4B6EC7` and **overwrites the vtable at `0x4B6ECC` with `0x7C57BC`**. This confirms previous Codex research was correct about final, not intermediate, class identity.
- MSVC RTTI for `0x7C57BC`: COL `0x7E5C10`, TypeDescriptor `0x81DBE0`, class `.?AVPSquadPlayerRow@@`. Intermediate vtable `0x7C457C` has TypeDescriptor `0x81D230`, **`.?AVPBasePlayerRow@@`**. It is not the final row class.
- Native vtable slot `+0x04 -> 0x489530` is shared. Two concrete overrides are **`+0x10 -> 0x4B6D80` (vs base `0x48AB70`)** and **`+0x20 -> 0x4B6DA0` (vs base `0x48ABE0`)**. The final overrides perform event/manager state operations and must **not** be mislabeled a selection-background draw routine without caller evidence. At `0x4895BE..0x4895CB`, the populated-row setup passes row `+0x70` through `0x443E70` to a child control; that routine stores a parent-control pointer at child `+0x2C`. The original pointer producer is traced below to `PSquadList+0x9D8`; the selected-state resource selection and drawing/blending remain **UNKNOWN**.
- Native `PSquadList::0x4B4FE0` still proves the existing repeated disabled-grid crop owner (`0x942FD0`, `stats_grid_disabled.444`). Nothing in these verified vtable slots proves what blue background is drawn for a specific selected player or pointer state.

**Resource recheck directly against original disc (no guessed artwork):**

| Source `FM2001_Art/Coaching/stats/` | Bytes | Header dimensions | SHA-256 | Original executable path / loader |
| --- | ---: | ---: | --- | --- |
| `stats_grid.444` | 13,332 | 729 × 16 | `1b3e6dfc1ccc92d294b88562684709431eba515ee754f945b201b513cf683c1e` | `0x837654`, loader `0x5FBE64`, wrapper initializer `0x5FBEB0` |
| `stats_grid_disabled.444` | 12,324 | 729 × 16 | `4fe16ef35b5ee5da748c9de81a14897e162d2d15e73cd143190dfb97a23822a7` | `0x837680`, loader `0x5FBEF4`, wrapper `0x5FBF40` |
| **`highlight_grid.444`** | **9,632** | **727 × 14** | **`3ff2e41dc292f5386146c8a6c65049f8287d949452306066c725c986ee436020`** | `0x8376B4`, loaders `0x5F99C4` (`0x944050`) and `0x5F9BB4` (`0x943F70`), wrappers `0x5F9A10` (`0x944030`) and `0x5F9C00` (`0x943F50`) |

Independent original Joliet directory lists all three assets. **`highlight_grid.444` is NOT a proven Squad-selected-blue rendering layer yet**: its native loader proves resource identity, not row/UI ownership or selected-state conditions. Notably the two native wrapper initializers provide different rectangle dimensions; ownership and source crop handling must be checked before assigning behavior.

**Reconstruction comparison:** on Codex head `8702eded049643220bf4b590d8d45c2197cfd42a`, `original_assets/source/FM2001_Art/Coaching/stats/` imports **only** `stats_grid_disabled.444`; `reconstruction/original_squad_top_controls.py::build_fresh_squad_top_render` emits the same cropped `328 × 16` disabled strip across each row. `stats_grid.444` and `highlight_grid.444` are genuine shipped originals but are **not imported as this renderer's dynamic selected-row resources**. **Status: PARTIAL (existing Squad screen), UNKNOWN (the selected-state-to-actual-frame/bitmap mapping).**

**Exact next owner trace:** begin at final `PSquadPlayerRow` and `CSquadPlayerList` constructors (`0x4B6E80`, `0x4B7170`) and the native control pointer through the list owner's `+0x54` to row `+0x70`, then child `0x443E70 +0x2C`. Independently follow `highlight_grid.444` image-loader/wrapper consumers at `0x5F99C0/0x5F9A10` and `0x5F9BB0/0x5F9C00`; verify source owner, actual control draw call and selection/pointer flag source. Do **not** paint a guessed blue rectangle.

### Further private source closure — exact populated-row control parent pointer (same session)

Following the native call chain disambiguates an earlier ambiguous description of row `+0x70` as a “texture/image-wrapper”:

1. `PSquadList::0x4B4FE0` at **`0x4B5086`** executes `lea ebp,[esi+0x9D8]` and does not overwrite EBP before its `0x4B56B9` indirect call. That call operates on `CSquadPlayerList` at `PSquadList+0xE44`, through **vtable `0x7C5AF4 +0xCC -> 0x4B7FD0`**.
2. `0x4B56A8..0x4B56B9` supplies the eight arguments to `0x4B7FD0`: for this call, `[esp+0x18]` at the callee is the original **`PSquadList+0x9D8`** control pointer. `0x4B7FDB..0x4B7FE6` stores it in **`CSquadPlayerList+0x54`**.
3. `CSquadPlayerList::0x4B7170` reads its `+0x54` and passes the pointer to the populated-row factory via virtual `+0xC8 -> 0x4B6E80`. The latter calls `0x48A8E0`; **`0x48A92C` stores that pointer as `PSquadPlayerRow+0x70`**.
4. `PSquadPlayerRow::0x489530` passes row `+0x70` to `0x443E70` for multiple child controls; `0x443E70` copies its respective argument to **child `+0x2C`**.

**Classification: EXACT original pointer-provenance chain (original executable), UNKNOWN downstream graphic ownership and meaning.** The forwarded address is *not* directly the global image-wrapper VA `0x943010` or `0x943F50`; it originates from a **`PSquadList`-local control at `+0x9D8`**. Label its semantic role neutral until this owner's vtable/init and downstream draw are traced. Any earlier handoff description that treated the child `+0x2C` assignment alone as proof that a particular texture or blue selection layer was attached overclaimed the evidence. The real background/selection frame still requires separate original-byte/caller verification.

**Remaining next native question:** identify the concrete class/vtable/parent relationships for `PSquadList+0x9D8`, its drawing/highlight children and the resource access path for `highlight_grid.444` before authorizing a selected-row bitmap fix.

## B. EAMail — original factory/RTTI identity now CLOSED, visible screen remains PARTIAL

**Independent canonical executable dispatch:**

```text
0x47AEC0  management panel factory
0x47AF12  index = panel_id - 0x65
0x47AF15  verifies index <= 0x69
0x47AF20  load byte from [index + 0x47CA04]
0x47AF26  indirect jump through [0x47C9E4 + 4*byte]
0x47CA04  byte 0x00  (index zero, panel id 0x65)
0x47C9E4  dword 0x47B1D0
0x47B1D0  allocate 0x14A0-byte PEAMail panel object
0x47B1F9  read user data field +0x6B4
0x47B202  call constructor 0x474B10
0x47B220  call panel layout/header helper 0x47F2B0
0x474EEF  set final vtable to 0x7C2950
```

MSVC RTTI for `0x7C2950`: COL `0x7E3960`, TypeDescriptor `0x819540`, class **`.?AVPEAMail@@`**. Its constructor `0x474CF8` invokes `0x4489B0` to create a concrete list child at panel `+0xF58`, later sets **`CMessageList` vtable `0x7C2A50`** at `0x474CFF`. Independently verified `0x7C2A50` RTTI: TypeDescriptor `0x81C7B8` = `.?AVCMessageList@@`. This discharges the earlier **unverified** `0x47CA04` EAMail dispatch guess: case and class are now proven, not merely arithmetic.

**Reconstruction comparison:** `original_management_presenter.py::build_management_panel_snapshot` supports Squad `0xCE`, Fixtures `0x25C`, Tables `0x25A`; EAMail `0x65` raises `OriginalManagementPresentationError`. No complete native `PEAMail` layout/render/data/action bridge is present. Existing generic `MPMEAMail` message action families cannot substitute for original `PEAMail` screen and `CMessageList` dynamic content or native interleave.

**Status: PARTIAL (PMenu recognizes EAMail child; native producer identified; current inbox absent).** Next verify the constructor's `CMessageList` data producer and row factory, message ordering / view-state / native text/assets/fonts, input callbacks, saved state, and exact layout. **Do not implement** or substitute modern inbox/UI from the factory identity alone.

## Audit constraints and acceptance

This is **research only**. No original program execution, no real Windows 11 render/input/DPI/movie/sound acceptance, no tests/CI dispatch or implementation branch modifications. `main` remains a research/ledger checkpoint. The latest durable `agent-runtime` explicitly maintains `worker_role=audit_only, implementation_allowed=false`; Codex retains implementation ownership. Southport-only fidelity remains insufficient: all P0 shared UI must be validated on another original club/state.

Gate 13 is still OPEN; Gates 14–17 and full original-country Windows 11 release are incomplete.
