# Gate 17 full playable-country LeagueAllocation preview

_Status: prepared dependent work-ahead behind the ranking-endpoint readiness audit._

## Purpose

The original TeamSelect scope is now mapped to the exact source
DBTLeagueAllocation rows, and the generic LeagueAllocation exchange executor is
already recovered. The remaining question is whether those two pieces compose
correctly across every playable country once all required endpoint rankings are
available.

This checkpoint proves that composition without changing live GameState.

## Contract

`preview_playable_allocation_exchanges()` consumes:

- the exact `PlayableCountryAllocationPlan`;
- parsed source LeagueAllocation rows;
- immutable endpoint rankings;
- current club-to-competition membership.

It requires the ranking-endpoint capability audit to be complete before any
exchange is attempted.

The country plan identifies the assigned allocation set but groups IDs by
TeamSelect country. The preview therefore recovers execution order independently
by filtering the original LeagueAllocation record stream to that exact assigned
set. Rows outside the TeamSelect-playable scope remain ignored.

The function then delegates the actual slot selection and membership swaps to
the existing source-backed `apply_league_allocation_exchanges()` implementation.
It does not reimplement or reinterpret promotion/relegation semantics.

## Output

The preview records:

- canonical playable-scope catalog SHA-256;
- exact assigned allocation IDs;
- the complete ranking-capability audit;
- memberships before and after;
- ordered source exchange ledger;
- exact changed club IDs;
- per-country allocation IDs, exchange counts and exchanged club IDs.

The caller's input membership mapping is never mutated.

## Fail-closed boundary

The preview aborts before exchange when:

- an assigned source row is missing;
- the source record stream does not cover the assigned allocation set exactly;
- the plan assigns one allocation to multiple countries;
- country assignment does not exactly cover the assigned set;
- endpoint rankings are unavailable or too short;
- membership data is malformed;
- a selected club lacks live competition membership;
- the generic source executor rejects any source slot or duplicate-club case.

## What this does not prove

This checkpoint does not:

- publish any missing non-English ranking;
- run a season;
- integrate with GameState;
- mutate live memberships;
- rebuild competition schedules;
- prove human control outside the current backend;
- claim Gate 17 completion.

After Gate 13 releases shared-runtime ownership, the intended annual-boundary
sequence is:

1. derive the canonical playable-country allocation plan;
2. resolve every required endpoint through live runtime ranking publishers;
3. require the ranking-capability audit to be complete;
4. preview all playable-country source exchanges;
5. commit the resulting memberships atomically into annual regeneration;
6. validate every cataloged scope on Windows 11.

This keeps the progression path source-driven and measurable without inventing
country-specific clean-room policy.
