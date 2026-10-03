# Gate 17 playable-League runtime ownership plan

_Status: independent work-ahead while Gate 13 shared runtime remains Codex-owned._

## Purpose

The source-backed TeamSelect catalog tells us exactly which root Leagues are
player-selectable. The recovered DBRCompetition fields independently tell us
which schedule container owns those Leagues.

This checkpoint joins those facts so full-scope gameplay work can reuse the
existing runtime machinery without a country-name or guessed competition-ID
switch.

## Source contract

For every TeamSelect League the plan requires the parsed competition record to:

- exist exactly once;
- remain a root competition;
- retain the same source country ID as the TeamSelect entry;
- retain `runtime_kind_code == 1`.

Runtime ownership is then classified only from already-recovered source fields:

- a caller-declared source-proven fixed-fixture League in a primary container
  becomes `fixed_primary`;
- any other runtime-kind-1 League whose `schedule_container_code` is not 2/3
  becomes `procedural_primary`;
- runtime-kind-1 Leagues with schedule-container code 2/3 become
  `procedural_secondary`.

The canonical 2000/01 loader defaults the fixed set to competition 0, matching
the already-recovered Premier League fixed-fixture startup exception. A fixed ID
that is not TeamSelect-playable or that belongs to the secondary container
fails closed.

## Output

Every entry retains:

- stable `<country_id>:<competition_id>` scope identity;
- source country and competition captions;
- exact runtime and schedule-container codes;
- runtime-owner classification;
- source club count;
- exact TeamSelect-selectable club IDs.

The aggregate records primary, secondary, fixed-primary, procedural-primary and
procedural-secondary scope-ID sets.

## Why this matters

The existing clean-room competition engine has generic procedural League
construction for the primary container. Canonical controller construction now
adds every TeamSelect entry classified `procedural_primary` to the live primary
scheduler/materialization set, while retaining the English/annual/Cup-child
dependencies needed elsewhere. Human primary procedural entries use the shared
human match backend. Human lineup validation now resolves substitute and
Non-EU limits from the actual pending Cup/League competition, and primary
match outcomes expose the controlled club's live League table rather than
hard-coding the Premier League table. Canonical club selection now accepts the
exact TeamSelect club set whose runtime owner is primary, but only when the
club's current membership resolves to an actually materialized root owner.
Secondary-container League support remains a separate boundary and is not
silently routed through the primary engine.

This plan therefore makes the full-scope implementation boundary explicit
without changing `GameState`, `HumanGameplayController`, fixtures, RNG,
annual transitions, or save state.

## Remaining boundary

After Gate 13 releases shared-runtime ownership:

1. provide the distinct secondary-container continuation for catalog entries
   classified there;
2. recover and connect the non-Premier-League fresh chairman-objective
   candidate branches rather than extrapolating the proven PL branch;
3. connect the already-parsed country allocation/ranking endpoints for annual
   progression;
4. validate every catalog scope through the final Windows 11 archive.

This checkpoint is a source-backed routing contract, not a claim that those
routes are already playable.
