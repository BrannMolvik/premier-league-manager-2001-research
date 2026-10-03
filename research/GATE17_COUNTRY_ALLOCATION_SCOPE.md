# Gate 17 playable-country LeagueAllocation scope

_Status: independent work-ahead while Gate 13 shared runtime remains Codex-owned._

## Purpose

The original `DBTLeagueAllocations` table contains 28 source records and the
existing `apply_league_allocation_exchanges()` implementation already performs
the recovered paired membership swap generically. The live annual wrapper,
however, currently resolves only the source-closed English subset.

This checkpoint maps the source rows onto the exact TeamSelect-playable country
catalog without performing any exchange or inventing promotion/relegation rules.

## Contract

`derive_playable_country_allocation_plan()` takes:

- the source-backed `OriginalPlayableScope`;
- parsed LeagueAllocation records in their source order;
- parsed competition records.

For each allocation row it resolves both competition endpoints to their source
`country_region_id`.

- When both endpoints belong to the same TeamSelect-playable country, the row
  is assigned to that country in original record order.
- Rows whose endpoints are entirely outside the playable-country set remain
  explicit as ignored rows.
- A row that touches a playable country but crosses to another country fails
  closed.
- Missing competition endpoints, duplicate competition IDs, or duplicate
  allocation IDs also fail closed.

Each country entry records:

- exact TeamSelect-selectable root League IDs;
- ordered allocation IDs;
- first-seen ordered ranking endpoint competition IDs;
- whether the source contains any transition rows for that country.

No endpoint is labelled as a playoff, promotion place, relegation place, or
lower-division policy unless those semantics are independently recovered.

## Canonical runner

`load_canonical_playable_country_allocation_plan(game_dir)` verifies the
canonical source hashes, parses the database once, derives the TeamSelect scope,
and maps `database.league_allocation_records` against the canonical
competitions.

This creates the exact source inventory needed to generalize annual membership
movement after Gate 13 releases shared-runtime ownership.

## Remaining implementation boundary

The plan deliberately does not resolve final rankings or mutate current club
memberships. The existing generic exchange executor can consume those inputs
later, but non-English ranking endpoints and their live cup/playoff/dummy
owners must first be source-backed and connected to the annual runtime.

This therefore advances Gate 17 planning without claiming full-scope
competition progression.
