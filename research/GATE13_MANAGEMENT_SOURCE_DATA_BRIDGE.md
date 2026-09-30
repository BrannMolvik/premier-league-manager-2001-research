# Gate 13 management source-data bridge

_Date: 1 October 2026 KST_

## Purpose

Gate 13 needs the original FM2001 management presentation to sit on top of the
already reconstructed simulation rather than duplicating league, squad,
fixture or player-state logic inside widgets.

`reconstruction/gate13_management_source_data.py` introduces a deliberately
read-only boundary for that work. It does **not** claim original screen layout,
screen IDs, navigation events, fonts, colors, column labels, fixture-screen
sort order or widget behavior. Those remain original-resource/native-executable
research.

The bridge only projects already recovered runtime/source data into immutable
rows that a future original-resource renderer can consume.

## Source-backed ordering/field rules

### Controlled-club header

The bridge exposes the current human club's original database `name` and
`short_name` plus the reconstructed game calendar date. Missing source names
fail closed; the bridge does not synthesize display labels.

### Squad

`HumanGameplayController.squad()` delegates to
`GameState.ordered_club_roster()`, which is the live controlled-club roster
order already used by the reconstructed backend. The bridge preserves that
order exactly and records each row's source-roster index.

Projected fields are already recovered runtime state only:

- player ID and source first/surname;
- original three-position tuple;
- shirt number;
- condition, form-state and morale values;
- injury/suspension;
- out-of-contract, transfer-list, loan-list and Wanted states.

No positional label names, status icons, colors, sorting or screen-specific
visibility rules are assigned here.

### Fixtures/results

`PremierLeagueState.fixture_source_order` is constructed directly from the
fixture source sequence before the dictionary map is built. The bridge iterates
that exact sequence and exposes each row's source index, reconstructed round
date, clubs and any recorded result.

This is **not a claim that the original Fixtures/Results screen displayed rows
in this exact order**. It is the safest lossless source ordering to hand to the
future original presentation layer until its own comparator/navigation logic is
recovered. The bridge intentionally refuses to substitute an ID/date sort when
`fixture_source_order` is absent.

### League table

`GameState.premier_league_table()` now uses the firsthand recovered
`League::0x4F45E0` order whenever all original CP1252 club short-name bytes
are available:

1. points descending;
2. played ascending;
3. goal difference descending;
4. goals for descending;
5. goals against ascending;
6. original short-name bytes ascending.

The bridge **does not sort table rows again**. It preserves the backend result
and only attaches source club names plus one-based display position. Therefore
future original presentation cannot accidentally regress to generic club-ID or
Unicode ordering at this seam.

See `research/GATE13_SOURCE_LEAGUE_COMPARATOR.md` for the comparator evidence
and remaining native equal-key qsort boundary.

## Architectural boundary

The bridge never:

- advances the calendar;
- simulates a fixture;
- changes team selection or tactics;
- executes transfers;
- edits player/finance state;
- guesses a management-screen control ID;
- invents original visual geometry or labels.

This is specifically progress toward Gate 13's requirement that simulation
logic stay separated from presentation code.

## Verification

`reconstruction/test_gate13_management_source_data.py` uses a synthetic
backend contract to lock:

- controlled-club source names/date;
- live source-roster ordering;
- fixture source insertion order even when fixture IDs/dates could tempt a
  modern resort;
- recorded/unplayed result projection;
- preservation of the already-sorted backend league table;
- neutral recovered player-state fields;
- fail-closed behavior when source names, human control or fixture-source order
  are unavailable.

Hosted CI validates only this read-only plumbing. It cannot establish original
screen pixels or native FM2001 management-screen ordering.

## Remaining Gate 13 work

The primary critical path remains unchanged:

1. restore private byte execution;
2. run the hash-gated original Button RTTI trace with the known-positive
   TeamSelect calibration;
3. prove the original action-atlas frame states and Zurich caption rendering;
4. execute the strict ten-resource original-source byte/pixel audit;
5. provenance-import only proven source assets;
6. complete authentic PStartMenu/TeamSelect and then manager-home, squad,
   tactics, fixtures/results, league table, player profile, transfers,
   finances, messages/news, training/scouting and remaining original screens;
7. audit Gate 13 before advancing to Gate 14.

This bridge supplies source-faithful management data to those future screens;
it does not substitute for them.
