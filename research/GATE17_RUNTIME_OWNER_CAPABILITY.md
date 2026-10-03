# Gate 17 runtime-owner capability audit

_Status: independent cloud-safe work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Purpose

The canonical TeamSelect catalog and the playable-League runtime ownership plan
now tell us which League routes the shipped game exposes and whether each route
belongs to the fixed primary, procedural primary, or procedural secondary
runtime family.

This checkpoint measures those requirements against the clean-room human
controller without widening it.

## Capability dimensions

Every playable country/League scope is checked for four independent conditions:

- every cataloged club in that scope is selectable by the current human backend;
- the required runtime owner is materialized;
- the human match dispatcher can play that runtime-owner family;
- annual progression is connected for that scope's country.

The audit reports exact blocker codes:

- `human_selection_unavailable`;
- `runtime_owner_not_materialized`;
- `human_match_dispatch_missing`;
- `annual_progression_country_missing`.

No blocker is inferred away merely because the generic AI/runtime machinery
exists.

## Current canonical surface

The canonical runner deliberately mirrors the current repository boundary:

- human club selection comes from `state.premier_league.club_ids`;
- fixed human League support is competition 0;
- every TeamSelect League classified `procedural_primary` is included in the
  canonical primary scheduler/materialization set and is represented through
  `state.procedural_leagues` when its source participants resolve;
- `play_user_primary_match()` now dispatches already-materialized primary
  `procedural_league` entries through the shared human match backend;
- GameState has no secondary procedural League runtime container;
- annual LeagueAllocation commit remains the English-only transition path.

These are implementation facts about the present clean-room port, not claims
about original behavior.

## Boundary

This module is diagnostic only. It does not mutate GameState, install secondary
competition state, change human selection, apply allocation exchanges,
regenerate a season, or alter save data. The separately implemented primary
procedural human-dispatch bridge is measured here rather than created by the
audit.

A fully green capability audit would only mean that the repository-side
runtime surfaces needed by every source-backed TeamSelect League are present.
Gate 17 would still require complete gameplay, save/reload, presentation and
Windows 11 release validation. Gate 13 remains a prerequisite validation gate.
