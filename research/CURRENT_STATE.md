# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. It is intentionally short. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 1 - Repository stabilization**

See `../ROADMAP.md` for gate definitions and completion criteria.

## Technical baseline entering stabilization

- Repository technical HEAD: `1014b042a19fc851b8d87e653ee1e5d807816630`
- Commit: **Advance startup RNG boundary before TeamSelect click**
- Last reconstruction-changing CI baseline: `0205d90a61d8b0386bfd6660a46910833257256a`
- Last verified reconstruction suite at that baseline: **307 tests passing**
- Commits after `0205d90a...` through `1014b042...` changed research documentation only, not reconstruction code.

## Current implementation state

Already implemented and tested at a substantial level:

- canonical Master.dat / Static.dat / STR parsing for the core shipped database;
- mutable runtime player state;
- player aging/development/training;
- exact MSVC CRT RNG primitive;
- recovered runtime-player startup RNG block using the shared CRT stream;
- Premier League real fixtures, dates, mutable results, and table;
- AI formation, lineup, substitutes, roles, and Non-EU restriction behavior;
- MatchCalculator normal-time simulation;
- set pieces, possession, Condition decay, injuries, discipline, and substitutions;
- post-match Form/Condition, persistent injury and discipline state;
- fixture -> match -> result -> table integration;
- exact schedule head insertion and descending Fisher-Yates primitives;
- recovered fixed Premier League fixture insertion order and schedule-container selection.

## Known live fidelity boundaries

- Exact global CRT state entering the first Premier League schedule shuffle is not yet completely bounded.
- Default same-day fixture execution still falls back to deterministic fixture-ID order unless explicit scheduler order is supplied.
- League-table tie ordering after points / goal difference / goals scored is unresolved and uses club ID as a deterministic fallback.
- Persistent-injury availability count still contains an approximation around the original helper `0x405080`.
- Real-data full-matchday / full-season integration is not yet automated in CI.
- Transfers/contracts and finance/board research are much further ahead than clean-room implementation.
- Broader competitions, original save compatibility, faithful UI, and FastView/3D remain incomplete.

## Active work

Repository stabilization and handoff cleanup:

1. establish the roadmap/live-state/backlog/fidelity files;
2. make continuation instructions read the live state first;
3. reconcile stale documentation;
4. add clean-room repository protection;
5. strengthen canonical-data verification;
6. run/observe CI for the resulting reconstruction/workflow changes;
7. mark Gate 1 complete and advance to Gate 2.

## Exact next technical task after Gate 1

Resume the startup RNG investigation at the **TeamSelect panel lifetime/activation path before the user clicks Start/Continue**.

Trace panel construction/activation and its caller chain backward to the already recovered database/player startup sequence. Look specifically for mandatory CRT RNG consumers that can survive until the first Premier League schedule shuffle.

The immediate click-to-new-game path is already proven to consume zero RNG draws before `0x4C41C0`.

## Do not expand into these systems yet

Unless required to unblock the active gate, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competitions;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful leads in `BACKLOG.md` instead.
