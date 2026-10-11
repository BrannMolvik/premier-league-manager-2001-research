# Original FM2001 Source Locator

## Purpose

This file records the durable private location of the authorized original
FM2001 disc-image archive used by the reconstruction project.

The binary archive itself must **not** be committed to this public repository.
GitHub remains canonical for code/research state; ChatGPT Library is the
canonical private binary source store.

## Canonical private source

- Library path:
  `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`
- Library file id:
  `file_00000000010c8209961739423e78473b`
- Stable library file id:
  `libfile_0ce96709612c81919f30acce4b4bdfbd`
- MIME type: `application/zip`
- Size: **511,121,336 bytes**
- Owner authorization: the project owner has explicitly authorized use of the
  supplied FM2001 archive/disc-image contents for this modernization project.

- **SHA-256 of the actual authorized 511,121,336-byte Library ZIP:**\n  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`\n  (computed from the actual materialized original ZIP on 30 September 2026).\n- Nested raw `famg2001.bin`: **631,627,248 bytes**, MODE1/2352;\n  **268,549** physical sectors validated; the Joliet level-3 catalog\n  contains **2,456 files and 211 folders**. See\n  `research/GATE13_REAL_DISC_INVENTORY.md` for independently checked paths,\n  original-asset SHA-256 values and reproduction instructions.

## Private Google Drive alternate source location — created 11 October 2026

The project owner requested a clearly labeled Google Drive folder for separately
uploaded original game bytes. The Drive connector **created and verified** the following
**not-shared** directories. These are stable navigational pointers, not proofs that
the original game files have been uploaded or are readable by the worker.

- **Source root:** `FM2001 — ORIGINAL GAME SOURCE — PRIVATE — AUTOWORKER`
  - Folder ID: `1gfuugjPoBsSp-AWuO5pOkEcTVNuvUirk`
  - URL: https://drive.google.com/drive/folders/1gfuugjPoBsSp-AWuO5pOkEcTVNuvUirk
- **01 — ORIGINAL DISC ARCHIVE ZIP — KEEP UNCHANGED:** untouched complete source
  ZIP only. https://drive.google.com/drive/folders/1z5-I-BfxuEFnV77fg_2EC43hbCr2EqmT
- **02 — EXTRACTED ORIGINAL GAME FILES — FOLDERS AND ASSETS:** original disc/game
  filesystem directory tree, with internal filenames and relative paths preserved.
  https://drive.google.com/drive/folders/1E6sIeKjeXEMCijxNRlNAb-Em_8WgRxnG
- **03 — AUTOWORKER DIRECT ACCESS — ORIGINAL EXE AND NEEDED ASSETS:** standalone
  executable and small individually needed resources (not another raw disc image).
  https://drive.google.com/drive/folders/1xnQlXjOToK-e6WTgQ0Kwyb19Y07aANYA

**Current evidence status:** all three Drive subfolders exist, were empty when
checked on creation, and were reported by Google Drive as `shared=false` and
`source_visibility_status=not_shared`. No original data has yet been uploaded.
The old authorized ChatGPT Library ZIP remains the only verified source archive.
Drive privacy must be preserved; do not make any folder or file public. URL
knowledge alone does not grant access. Prefer the 03 standalone executable
and a hash check once actually uploaded; then use 02 targeted files, 01 ZIP
as a fallback. If the Drive connector cannot read/download bytes through the
worker runtime, do not claim access. When new original files are uploaded,
record actual filenames/size/SHA-256 and direct source IDs in this locator.

**Do not confuse disc-image container extraction with original game files.**
The original ZIP contains a disc-image `.bin`; a raw extracted `.bin` in
folder 02 would not remedy the large-file access issue. Folder 02 should
contain the game filesystem files from *inside* the disc image, not only the
disc-image container. Keep originals unmodified and avoid duplicate full
disc-image uploads.

### Actual Drive upload inspection — 11 October 2026 (after owner upload)

The Google Drive connector listed the private folders and returned these
**actual stored files**, all shown as not shared and downloadable. This
supersedes the earlier *empty at creation* observation above:

- Folder **01** currently holds `FM2001-Windows11-rc-94a620839624f293c0d4343f7e42c9ddfb31d549.zip`
  (71,319,074 bytes), Google Drive id `18DUzW9tNty0Huu_tzdyOMBDKTiUq4qWv`.
  **This appears by filename/size to be the Windows 11 reconstruction release
  candidate, NOT the original game/disc ZIP; classification is not a byte-content
  verification. Do not mistake it for an original-source archive.**
- Folder **02** has **no files or subfolders** in the listing.
- Folder **03** holds `famg2001.bin` (631,627,248 bytes, Drive id
  `1ABjHP8uGQSYFhFX0N32pO2D-k_bTL_8x`),
  `famg2001.cue` (77 bytes, id `1wBAjDgEVb7mmtHdQMjZiwtkZy5Vx6o0L`), and
  `fltfm2k.nfo` (5,081 bytes, id `12sMrFLq-5QWOdbPDqbpw3MBHVx2sObwW`).
  The BIN size **matches** the previously inventoried nested original image,
  but the BIN's actual SHA-256 is **not freshly verified**. Small CUE raw-byte
  fetch succeeded and reads `FILE "F:\\FAMG2001.BIN" BINARY`,
  `TRACK 01 MODE1/2352`, `INDEX 01 00:00:00`. The F: path is
  a recorded image-creator drive path; treat it as a cue reference to the
  paired BIN, not a path that exists in the worker environment.
- **No separately uploaded original `FOOTBAL.EXE` or
  `footballmanager.exe` was found in the target source folders;** small-file-first
  executable verification cannot yet run. User should mount/extract actual
  files *inside* BIN/CUE to folder 02 (preserving game paths), and separately
  place the original executable file in folder 03. Original ZIP may be kept as
  a preservation copy in folder 01, but the Library already holds the canonical
  original ZIP.
- A harmless `container.exec` health check returned
  `caas.internal.errors.ClientError` even without materializing the BIN.
  The upload resolves Drive discoverability but **does not establish byte-readable
  local source analysis or Windows GUI gameplay testing**. Do not download the
  632 MB BIN as a speculative fix; first establish a working execution sandbox.
- No uploaded file has been moved, altered, executed or shared by the inspector.

### VERIFIED standalone original source executable — 11 October 2026

**Source recovered: YES (direct private Google Drive read, actual byte hash checked).**
The user's IsoBuster user-data extraction of original disc-root
`footballmanager.exe` was separately uploaded to the already registered
private **03 — AUTOWORKER DIRECT ACCESS** folder:

- Google Drive file ID: `1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q`
- Browser URL: https://drive.google.com/file/d/1ejKHlLHqru7aCU-fKSFaby8KeQf6SB3Q/view?usp=drivesdk
- Drive folder ID: `1xnQlXjOToK-e6WTgQ0Kwyb19Y07aANYA`
- Exact downloaded byte count: **4,714,541**
- Independently recomputed **SHA-256:**
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
- Result: **EXACT MATCH** with independently recovered canonical disc-root
  and crack/ executable evidence from `research/GATE13_REAL_DISC_INVENTORY.md`.
- Checked file header is `4d5a9000` (`MZ`).
- Drive `list_folder` returned `shared=false`,
  `source_visibility_status=not_shared`; the user has not granted public access.

Verification mechanism: connected Google Drive raw-file fetch returned
4,714,541 actual executable bytes, decoded and hashed via independent
pure-JavaScript SHA-256 inside the connector-capable execution environment,
not based on filename or size alone. This **proves byte access via Drive
connector**, despite a separate `container.exec` harmless command still
failing `caas.internal.errors.ClientError`. Future workers should **first
fetch this small exact file via the Google Drive connector** rather than
materializing the 511 MB Library ZIP or 632 MB BIN. Check file metadata and
hash if original file could have changed. File is available for static
analysis through a suitable compatible execution/runtime; do not infer shell
availability or a successful Windows original-game/port playtest from this
verification. No original binary was committed to Git.

### VERIFIED extracted original FM2001 game filesystem — 11 October 2026, 20:19 KST

**Owner upload CONFIRMED; this newer inspection supersedes the earlier "folder 02 empty" note.**
Connected Google Drive listed the actual extracted disc-file tree directly from
**02 — EXTRACTED ORIGINAL GAME FILES**:

- **Extracted root:** `FM2001`, Drive folder id
  `1pQy4V8tq5COGhtIMgNPVSDFjSRqiqnTC`
  https://drive.google.com/drive/folders/1pQy4V8tq5COGhtIMgNPVSDFjSRqiqnTC
- Original root has **52 direct entries: 15 folders and 37 files**, including
  `footballmanager.exe` (4,714,541 bytes, separate root Drive id
  `10xq-q-y7IIzfnZnT5lQ-wGotAfOiGWM7`), `FOOTBALLMANAGER.ICD`,
  `Master.dat` (3,391,446 bytes, id `1M3Ci2RUmkM-lK0_Qonq3fQ7zC08B97OR`),
  `Static.dat`, `English.str`, `EnglishEAM.str`, `Resource.res`, and original
  `FM2001_Art`, `Data`, `DataInGame`, `ArtInGame`, `FMV`, `Fonts`,
  `FormationFiles`, `Games`, and other original folders.
- Direct source folders:
  - FM2001_Art:
    https://drive.google.com/drive/folders/1XguguFvDXZoBQ6rNXuQn0bEY2e3Do8gI
  - FM2001_Art/Generic:
    https://drive.google.com/drive/folders/1DBkT3qeGvntkuObdkExViWpUh9ZFW-4D
  - FM2001_Art/Generic/EAMail:
    https://drive.google.com/drive/folders/1WhzWAPpa7j10wQKG-OItGRhC5YsUpmyX
  - DataInGame (252 direct files):
    https://drive.google.com/drive/folders/10Hbjmk-g8mHklkvcy90CHoQTzAmZ2yWl
  - FMV (4 direct files including `premintro.tgq`):
    https://drive.google.com/drive/folders/1iuVY7_LyINMR7983Qaid5avoVkxRr02u
  - Fonts (18 direct files, original Zurich bitmap fonts):
    https://drive.google.com/drive/folders/1sityvIVKKh0qK8_K7Ie6hw8exoiPSiRw
  - FormationFiles (9 direct files):
    https://drive.google.com/drive/folders/1eYpyro4HFB6HiETamrObsTq2Goh3lsk3

**Original EAMail resource byte-level source verification:** downloaded these
four raw original assets independently through the connected Drive file
connector; independently computed SHA-256 and checked against
`reconstruction/original_eamail_source_contract.py` (PR #595).
**ALL FOUR EXACT HASH/SIZE MATCH:**

| Native path under FM2001_Art/Generic/EAMail | Google Drive file ID | Size | Verified SHA-256 |
|---|---|---:|---|
| `text_grid_nor.444` | `1X0Tfr8l6zwdmZtX1WKQQJT7GQZa_tDqU` | 8124 | `74676dce75532b781551cab6e8598f805fa4698b2e1b828c9f4ef15b3ff0816d` |
| `text_grid_sel.444` | `1C7exJFBL4SRBmy-7LycovGoOoSaolsCz` | 7504 | `6b6ff7ce36b3c507df2d590ba7ad48b9253409757844acf4ec93204807bad556` |
| `text_grid_high.444` | `1_OxNRhbyxANNW3TL7sKW1Mi6vYvPNg_X` | 6856 | `a13b413d13b5fa9c5f6a7b36f632c60342898de72bcff2ee73025bc92fdb68c8` |
| `text_grid_des.444` | `1qw1__CyAp6at0gBNjsmJVDjph2YqUeoe` | 7184 | `cb1fb08a99dfe204ea9b485f5102e808ab758f80aec96f69e17e9537d8eb2f70` |

All sampled Drive source files and folders were shown not shared. This proves
**a correct navigable original directory tree and sample original asset-byte
retrieval**. A recursive attempt to enumerate all folders exceeded connector
tool-call limits, so **the complete 2,456-file / 211-folder parity is not yet
independently reverified**. Do not claim full-archive checksum parity, local
shell health, live Windows 11 GUI acceptance, or successful original-game
execution from this check. The previous 511 MB Library ZIP remains archival
fallback, and the verified directly uploaded 4,714,541-byte executable in
folder 03 remains available from the previous source-locator entry.

**Worker next action:** Use the direct Drive folder/file IDs above as the
first retrieval route for original artifacts needed by source reconstruction,
including Inbox and management/match presentation. Fetch and hash only the
required small file; do not rematerialize the huge disc image routinely.
No further owner extraction should be needed for ordinary original source
files already present in this tree.

## Small-file-first recovery and alternate private storage (11 October 2026)

**Known problem:** the 511,121,336-byte archive is visible and materializable from Library, but container/Python may fail with `caas.internal.errors.ClientError`, sometimes even on trivial commands after materialization. Merely copying that ZIP to a different provider does not repair a broken execution sandbox.

**Preferred recovery improvement, pending an actual user upload:** directly stage the original source executable as its own private file in the ChatGPT Library (and optionally a restricted Google Drive FM2001/Original Source folder), plus a small ZIP of only needed original art/data paths. The previously hash-verified original `footballmanager.exe` is **4,714,541 bytes**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. The executable has NOT yet been verified from a new direct-upload location. Record the new actual file IDs/paths here only after a successful upload and a fresh hash check. Keep the full authorized disc archive intact as the canonical fallback; never add proprietary original binaries to GitHub or public shares.

**Access procedure:**
1. Before materializing any large file, run one harmless execution health check. If trivial shell and Python probes fail, classify it as an execution-sandbox failure and stop retrying bulk materialization in that session.
2. Look for an individually uploaded original executable or the specific small resource bundle in private Library/connected Drive. If found, materialize only that file and verify its actual SHA-256/size against the provenance before using bytes for source analysis. A connector returning metadata or a link alone does not prove that local code can read the bytes.
3. If no small file is present and shell execution works, recover the original via the existing full ZIP path once, using the known source tools and canonical integrity checks.
4. If small-file extraction works but source analysis still fails, test a new clean execution environment or an explicitly configured private development runner. Do not assume changing storage provider cures a process failure. Preserve the precise failing command and full source evidence boundary.
5. Only claim original-game or Windows 11 playtesting when the executable was actually launched with explicit authorization on a suitable environment and the GUI was observed. Static byte analysis is not a playtest.

## Mandatory recovery procedure

Before any worker declares `FOOTBAL.EXE`, the canonical game directory, or the
authorized original source unavailable:

1. Check this file for the current canonical private source location.
2. Use the ChatGPT Files/Library tools to list
   `/FM2001/Original Source`.
3. Prefer the stable Library identity above when available; otherwise resolve
   the file by the exact Library path.
4. First apply the small-file-first/health-check procedure above. Materialize the full ZIP only if the execution sandbox is functioning and no suitable hash-verified smaller file is available.
5. Inspect/extract the supplied disc image/archive using the repository's
   source-access tooling, if necessary.
6. Recover the required canonical game files, including `FOOTBAL.EXE`, into a
   temporary workspace.
7. Verify any existing repository hash/size/provenance checks before using
   recovered bytes as evidence.
8. Only report a source-access blocker after this Library recovery route has
   actually failed.

A lost temporary extraction, expired sandbox, missing local shortcut, new chat,
or new execution workspace is **not** evidence that the original source has
been lost.

## Repository policy

Do not commit the full ZIP, raw disc image, or uncontrolled extraction dump to
this repository. Store only intentionally imported original resources permitted
by `research/ASSET_POLICY.md`, plus derived research metadata and tooling.

If the Library file is intentionally replaced, update this locator with the new
stable Library identity, exact byte size, and verified checksum/provenance
information.
