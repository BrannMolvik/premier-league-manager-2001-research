# Gate 17 runtime progression readiness audit

_Status: prepared dependent work-ahead behind the playable-country allocation preview._

## Purpose

The repository now has source-backed primitives for:

- the original TeamSelect playable scope;
- playable-country LeagueAllocation row ownership;
- exact ranking-endpoint readiness;
- non-mutating preview of all playable-country membership exchanges.

This checkpoint connects those primitives to an actual completed runtime state
without modifying GameState.

## Runtime contract

`audit_runtime_playable_progression(plan, state)` requires a state exposing:

- `league_allocation_records`;
- `club_competition_membership`;
- `season_transition_ranking(competition_id)`.

The audit:

1. snapshots exact non-negative integer club membership identities;
2. resolves every required ranking endpoint exactly once in first-seen plan
   order;
3. verifies ranking resolution did not mutate club memberships;
4. runs the source-position ranking capability audit;
5. if and only if that audit is complete, previews every playable-country
   LeagueAllocation exchange through the recovered generic executor;
6. verifies the preview path also left runtime memberships unchanged.

## Output

The result retains:

- canonical playable-scope catalog SHA-256;
- exact required endpoint IDs;
- resolved runtime ranking tuples or explicit `None`;
- complete ranking-capability audit;
- optional full allocation preview;
- an explicit runtime-membership immutability flag.

`complete=true` requires:

- runtime memberships stayed unchanged;
- every source ranking endpoint covered all required positions;
- the full playable-country exchange preview succeeded.

## Fail-closed behavior

The audit rejects:

- missing runtime surfaces;
- non-callable ranking resolver;
- non-dict membership state;
- boolean/string/negative club or competition membership IDs;
- invalid ranking endpoint identities in the plan;
- mutable/list runtime ranking payloads;
- any membership mutation caused by ranking resolution;
- any membership mutation caused by the audit/preview path.

If one ranking endpoint is unavailable, the audit returns a valid incomplete
result and does **not** attempt an allocation preview.

## Integration boundary

The audit itself remains read-only: it does not change
`club_competition_membership` or regenerate schedules. Canonical
`HumanGameplayController.regenerate_annual_primary_season()` now uses the same
source-backed playable-country plan and preview logic to obtain the post-exchange
membership map, then commits that map only through the existing atomic annual
GameState installation boundary.

A complete audit is therefore evidence for the same ranking/exchange contract
used by the live annual regeneration path. It is still not permission to skip
secondary-runtime implementation, non-PL fresh chairman-objective recovery, or
Windows 11 validation.

## Current canonical runtime seam

Canonical construction now derives and retains the exact TeamSelect-country
allocation plan. Annual regeneration resolves every plan-required ranking
endpoint from finalized DummyLeague overrides or the live ranking publisher,
runs the same fail-closed all-playable-country exchange preview, and passes its
post-exchange membership map into the existing atomic primary-season installer.

The remaining full-scope seams are elsewhere: secondary-container playable
Leagues still lack live runtime ownership/dispatch, and fresh chairman-objective
candidate generation remains source-locked only for competition 0. Those gaps
must not be hidden by the now-generic annual membership commit.

