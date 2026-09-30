# Gate 13 First-Screen Manifest Readiness Guard

_Date: 1 October 2026 KST_

## Purpose

The Gate-13 source pipeline already has two strong pre-import controls:

- `gate13_first_screen_selection.py` pins the ten independently recovered
  original source paths and SHA-256 values and validates the physical selected
  extraction receipt;
- `gate13_asset_import.py` imports one intentionally selected source file at a
  time and records provenance.

A separate end-state guard was still missing. Without it, a later audit could
mistake a partially imported manifest for a completed PStartMenu/TeamSelect
source slice.

## New fail-closed audit

`gate13_first_screen_manifest_readiness.py` checks the repository after import.
It requires all ten `FIRST_SCREEN_ORIGINALS` entries and verifies for each:

- exact original source path in `original_assets/MANIFEST.md`;
- canonical `original_assets/source/<source path>` destination;
- manifest form `original`;
- the independently pinned source SHA-256;
- a real tracked file at that path;
- current file bytes hashing to the same source SHA-256.

Duplicate source or destination rows are rejected. Extra unrelated authorized
assets are ignored rather than treated as substitutes.

The CLI also locks the durable
`research/GATE13_FIRST_SCREEN_EXACT_PATHS.txt` selection file to the same
ten-entry source contract before checking repository readiness.

## Evidence boundary

This guard does **not** claim that the ten resources have now been imported.
At recovery 101, direct shell/Python byte execution still returns
`ClientError`, and the current manifest contains only earlier intentional
assets/decoder fixtures. Therefore the real repository is expected to fail the
readiness CLI today.

Unit tests use tiny synthetic bytes solely to prove pass/fail behavior. Hosted
CI cannot turn those fixtures into evidence that the licensed originals were
physically audited or imported.

## Completion use

After private byte execution returns:

1. run the canonical Button/Zurich and strict physical ten-resource audit;
2. import the verified originals using `gate13_asset_import.py`;
3. run `gate13_first_screen_manifest_readiness.py`;
4. only if it passes, proceed to the graphical/source-backed first-screen smoke
   test and any Gate-13 criterion audit.

This makes partial provenance impossible to promote accidentally as a complete
first-screen source slice.
