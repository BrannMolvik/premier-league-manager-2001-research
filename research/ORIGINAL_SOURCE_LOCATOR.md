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

## Mandatory recovery procedure

Before any worker declares `FOOTBAL.EXE`, the canonical game directory, or the
authorized original source unavailable:

1. Check this file for the current canonical private source location.
2. Use the ChatGPT Files/Library tools to list
   `/FM2001/Original Source`.
3. Prefer the stable Library identity above when available; otherwise resolve
   the file by the exact Library path.
4. Materialize the ZIP into the current execution workspace.
5. Inspect/extract the supplied disc image/archive using the repository's
   source-access tooling.
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
