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
