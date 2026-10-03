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

This checkpoint deliberately does not call
`GameState.apply_english_season_transition()`, change
`club_competition_membership`, regenerate schedules, or widen human selection.

After Gate 13 releases shared-runtime ownership, the intended full-scope annual
path can reuse this read-only audit immediately before committing source-backed
membership changes. A complete audit is evidence that the runtime has all
required ranking inputs and that the generic source executor can produce the
next membership map, not permission to skip the later atomic installation and
Windows validation.

## Current canonical runtime seam

The present canonical human-controller constructor still hard-codes the selected
domestic runtime to England:

- `HumanGameplayController.from_canonical_game_dir()` calls
  `partition_root_procedural_league_ids(..., country_region_id=26)`;
- it labels those results `english_primary_leagues` /
  `english_secondary_leagues`;
- it refuses a changed English secondary set;
- only the English primary set is unioned with annual played ranking sources and
  annual Cup-child procedural Leagues before
  `refresh_primary_procedural_leagues()`.

This is important because the underlying procedural League state and the
LeagueAllocation exchange executor are already generic. Once Gate 13 releases
shared-runtime ownership, full-country progression should generalize this
source-backed selected-country ownership boundary rather than fork the league
engine per country.

The audit in this checkpoint will then measure whether that generalization
actually publishes every ranking endpoint required by the canonical allocation
plan.

