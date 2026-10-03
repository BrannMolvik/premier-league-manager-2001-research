# Gate 17 runtime-owner capability audit

_Status: independent cloud-safe work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Purpose

The canonical TeamSelect catalog and the playable-League runtime ownership plan
now tell us which League routes the shipped game exposes and whether each route
belongs to the fixed primary, procedural primary, or procedural secondary
runtime family.

This checkpoint measures those requirements against the clean-room human
controller. Primary TeamSelect club selection is now source-driven; secondary
selection remains unavailable until its distinct runtime owner exists.

## Capability dimensions

Every playable country/League scope is checked for five independent conditions:

- every cataloged club in that scope is selectable by the current human backend;
- the required runtime owner is materialized;
- the human match dispatcher can play that runtime-owner family;
- fresh chairman/financial-objective setup is source-backed for that
  competition;
- annual progression is connected for that scope's country.

The audit reports exact blocker codes:

- `human_selection_unavailable`;
- `runtime_owner_not_materialized`;
- `human_match_dispatch_missing`;
- `fresh_financial_objective_missing`;
- `annual_progression_country_missing`.

No blocker is inferred away merely because the generic AI/runtime machinery
exists.

## Current canonical surface

The canonical runner deliberately mirrors the current repository boundary:

- human club selection includes the exact TeamSelect clubs whose required
  runtime owner is fixed/procedural primary, with a live-owner membership
  guard before control is assigned;
- fixed human League support is competition 0;
- every TeamSelect League classified `procedural_primary` is included in the
  canonical primary scheduler/materialization set and is represented through
  `state.procedural_leagues` when its source participants resolve;
- `play_user_primary_match()` now dispatches already-materialized primary
  `procedural_league` entries through the shared human match backend;
- GameState has no secondary procedural League runtime container;
- fresh chairman-objective candidate generation remains instruction-locked
  only for competition 0, so non-PL scopes retain the explicit
  `fresh_financial_objective_missing` blocker;
- canonical annual LeagueAllocation commit now uses the exact TeamSelect-country
  allocation plan, resolving required rankings fail-closed before the existing
  atomic season-regeneration install.

These are implementation facts about the present clean-room port, not claims
about original behavior.

## Boundary

This module is diagnostic only. It does not mutate GameState, install secondary
competition state, apply allocation exchanges, regenerate a season, or alter
save data. Source-driven primary selection and the separately implemented
primary procedural human-dispatch bridge are measured here rather than created
by the audit.

A fully green capability audit would only mean that the repository-side
runtime surfaces needed by every source-backed TeamSelect League are present.
Gate 17 would still require complete gameplay, save/reload, presentation and
Windows 11 release validation. Gate 13 remains a prerequisite validation gate.
