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

The existing clean-room competition engine already has generic procedural
League construction for the primary container. The current human gameplay
controller only materializes an English/annual subset of those owners and does
not provide a human procedural-League dispatch. Secondary-container League
support is a separate boundary and must not be silently routed through the
primary engine.

This plan therefore makes the full-scope implementation boundary explicit
without changing `GameState`, `HumanGameplayController`, fixtures, RNG,
annual transitions, or save state.

## Remaining boundary

After Gate 13 releases shared-runtime ownership:

1. materialize every cataloged primary League owner required by the selected
   human career;
2. add the source-backed human procedural-League match branch;
3. provide the distinct secondary-container continuation for catalog entries
   classified there;
4. connect the already-parsed country allocation/ranking endpoints for annual
   progression;
5. validate every catalog scope through the final Windows 11 archive.

This checkpoint is a source-backed routing contract, not a claim that those
routes are already playable.
