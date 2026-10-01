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

Recovery 120 completed the private physical audit and imported all ten exact
resources. The real repository now passes the readiness CLI. This success is
distinct from the synthetic unit-test coverage and does not by itself close
TeamSelect hierarchy behavior or the Windows graphical audit.

Unit tests use tiny synthetic bytes solely to prove pass/fail behavior. Hosted
CI cannot turn those fixtures into evidence that the licensed originals were
physically audited or imported.

## Hosted verification

PR #36 head `ec50eafb9bd323af3c301752dc739762b3c7bce5` was validated by:

- focused Gate-13 run `36768095800`: **226 tests**, **19 expected
  original-source-gated skips**, zero failures;
- repository asset-policy run `36768095889`: passed.

It was squash-merged to main as
`947fc7d26e6383a7da15113994baf858a44dd609`.

The previous full reconstruction integration baseline, run `36767384882`,
remains green at **1,055 tests with 21 expected source-gated skips** and zero
failures. This PR did not touch the fragile runtime paths configured to trigger
that full suite.

## Completion use

Completed recovery sequence:

1. run the canonical Button/Zurich and strict physical ten-resource audit;
2. import the verified originals using `gate13_asset_import.py`;
3. run `gate13_first_screen_manifest_readiness.py`;
4. it passed; proceed to the graphical/source-backed first-screen smoke test
   and the remaining Gate-13 criterion audit.

This makes partial provenance impossible to promote accidentally as a complete
first-screen source slice.
