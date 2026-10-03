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
