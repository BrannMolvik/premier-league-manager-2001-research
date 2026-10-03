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
