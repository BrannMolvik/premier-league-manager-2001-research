# Gate 17 full original scope evidence contract

_Date: 3 October 2026 KST_

## Why this receipt exists

PR #189 made the permanent release target explicit: this project is a Windows
11 compatibility port of the shipped original game, not a Premier-League-only
reinterpretation. The older Gate-17 external evidence harness predates that
scope invariant. Its `new_game_management_loop.json`, season and save/reload
receipts exercise the current Premier League path and therefore cannot prove
the full release definition of done.

Gate 17 now requires a fifth distinct external receipt:
`full_original_scope.json`.

## Required true flags

The final release audit accepts this receipt only when it is bound to the same
Windows 11 client workstation, repository commit, release version and release
archive SHA-256 as the other release evidence and declares all of these true:

- `full_original_scope`;
- `all_original_playable_leagues`;
- `all_original_playable_countries`;
- `human_career_flow`;
- `competition_progression`;
- `original_management_gameplay_subsystems`;
- `all_original_scope_save_reload`;
- `multi_human_management`.

The receipt must additionally record
`simultaneous_human_users_verified: 6`. The original TeamSelect path is
source-proven to append human users rather than replace the prior selection and
to saturate at the global user count of six. The current clean-room backend
models only one `HumanManagerState` and fails closed when Start has multiple
active selections, so this remains a release blocker rather than a documented
limitation.

The receipt cannot reuse the clean-install, Premier League management,
season-progression or save/reload receipt file.

## Canonical catalog binding

The repository now has a source-backed catalog primitive in
`gate17_full_scope_catalog.py`. It derives the exact recovered TeamSelect
country/League/club projection from the hash-verified canonical game directory;
no original game bytes or guessed modern league list are committed.

The final Windows 11 release audit independently rebuilds that catalog and
requires `full_original_scope.json` to carry:

- `scope_catalog_sha256`, equal to the deterministic canonical catalog hash;
- `scope_country_count`;
- `scope_entry_count`, one entry for each selectable country/League pair;
- `scope_selectable_club_row_count`;
- `verified_scope_entry_count`, equal to the full entry count;
- `verified_scope_ids`, in exact canonical order, using
  `<country_id>:<competition_id>`;
- empty `missing_scope_ids`;
- empty `failed_scope_ids`;
- `save_reload_verified_scope_entry_count`, equal to the full entry count;
- `save_reload_verified_scope_ids`, in the same exact canonical order;
- empty `save_reload_missing_scope_ids`;
- empty `save_reload_failed_scope_ids`.

The save/reload fields are deliberately separate from generic scope verification.
They require the final Windows 11 full-scope producer to prove continuation across
every cataloged TeamSelect country/League route rather than reusing the older
Premier-League-centered `save_reload.json` receipt or one representative
non-PL procedural-primary audit. PR #271 provides a source-driven canonical
non-PL primary audit harness, but no private canonical or Windows receipt is
inferred from its hosted tests.

The catalog SHA also covers the exact selectable club IDs and captions recorded
inside every League entry. A broad set of true booleans can therefore no longer
stand in for an audit of an unspecified scope.

## Current fail-closed boundary

There is deliberately still no producer in the current repository that claims
the full-scope runtime facts. `gate17_windows_gameplay_receipts.py` remains
honest about producing three Premier-League-centered gameplay receipts only.

The current human gameplay handoff is still Premier-League-only, so the
full-scope receipt cannot legitimately satisfy the binding above yet. After
Gate 13 releases the shared-runtime ownership lock, the gameplay continuation
must be generalized across the source-backed catalog, then every cataloged
country/League route must be exercised against the final archive on a real
Windows 11 client.

Until that external audit passes, Gate 17 remains open.

This is not a new product requirement. It makes the already-canonical ROADMAP
scope invariant machine-checkable so missing shipped functionality cannot be
documented away as a release limitation.
