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
- `original_management_gameplay_subsystems`.

The receipt cannot reuse the clean-install, Premier League management,
season-progression or save/reload receipt file.

## Current fail-closed boundary

There is deliberately no producer in the current repository that claims these
facts. `gate17_windows_gameplay_receipts.py` remains honest about producing
three Premier-League-centered gameplay receipts only.

A source-backed full-scope catalog and runtime audit still need to be recovered
and implemented. That future audit must exercise every originally selectable /
playable entry against the final archive on a real Windows 11 client and only
then write this receipt. Until that exists, the transactional external
validator requires a pre-existing external full-scope receipt and Gate 17
cannot pass.

This is not a new product requirement. It makes the already-canonical ROADMAP
scope invariant machine-checkable so missing shipped functionality cannot be
documented away as a release limitation.

## Source-backed scope catalog binding

The release receipt is additionally bound to
`research/GATE17_ORIGINAL_SCOPE_CATALOG.json`.

The repository file is deliberately a release-blocking placeholder today:
`status` is `unrecovered`, `expected_entry_count` is zero, and no country or
competition entries are asserted. This prevents the current Premier-League-only
runtime from becoming the source of truth for the shipped game's original scope.

Before final release, authorized original evidence must populate that catalog
with `status: source_backed_complete`, a positive exact entry count, non-empty
source-evidence references, and one unique entry per originally playable
country/competition target. Each entry carries a stable `scope_id`, country,
competition, source reference and `originally_playable: true`.

`full_original_scope.json` must then prove it was produced against that exact
catalog by recording:

- the catalog SHA-256;
- the exact catalog entry count;
- the same verified entry count;
- the complete ordered `scope_id` list;
- empty `missing_scope_ids`;
- empty `failed_scope_ids`.

The final audit recomputes the catalog hash and rejects any stale, incomplete,
reordered, missing or failed scope set. Six high-level booleans alone are not
sufficient release evidence.
