# Backlog

This file is for **useful but deliberately deferred work**. It prevents side discoveries from hijacking the active roadmap gate.

A backlog item is not necessarily a bug or fidelity error. Known deviations from original behavior belong in `FIDELITY_GAPS.md`.

## Scheduling / competition

- Recover exact original league-table fallback after points, goal difference, and goals scored.
- Convert real-data integration from manual/local verification into repeatable matchday and full-season harnesses once startup/scheduler RNG is closed.
- Expand from Premier League into domestic cups, European competitions, and other competition formats during Gate 12.
- Investigate unresolved qsort relative order when competition initialization-order keys compare equal if it becomes observable.

## Match / player-state research

- Resolve the higher-level semantics of remaining low-level MatchCalculator fields where behavior is implemented but naming is still provisional.
- Replace the persistent-injury availability approximation around helper `0x405080` when the original count path is fully recovered.
- Continue medical/recovery modifiers beyond the already connected core injury path.
- Revisit rare/edge match paths after full-season integration exposes which ones are materially reachable.

## Management systems

- Implement contracts and transfers from the existing research corpus during Gate 9.
- Implement cash, budgets, wages, commercial/stadium flows, chairman/board behavior, and job security during Gate 10.
- Connect scouting, youth, messages/news, and broader manager workflows during Gate 11.

## Save / compatibility

- Add an internal modern save format at Gate 8.
- Continue original FM2001 save-format compatibility later without blocking the internal save system.
- Keep legacy executable/runtime compatibility research separate from the native reconstruction unless it directly supplies evidence.

## UI / presentation

- Intro FMVs are now identified and decoded: `FMV/easp.tgq` and `FMV/premintro.tgq` both contain embedded original audio; see `STARTUP_PRESENTATION.md`. Continue the asset inventory for separate menu/login music, sound effects, UI graphics, fonts, badges, icons, backgrounds, and match-presentation resources.
- Restore management screens after the core human-manager loop is stable, preferring original resources and layouts over unnecessary recreations.
- Integrate original login/menu music and front-end audio during the presentation gates.
- Leave FastView/3D presentation until Gate 14 unless a presentation structure is needed to understand simulation semantics.

## Tooling / quality

- Add more real-data invariant checks without storing copyrighted data in Git.
- Add long-duration multi-seed stress harnesses at Gate 16.
- Consider stricter typing/static analysis after the simulation APIs settle.
- Periodically audit historical research for statements that are technically superseded but not clearly labeled as such.


- **DBTLeagueAllocations / DBRLeagueAllocation table**: canonical Static.dat
  offset `0xFD43`, 28 packed 7-dword records, RTTI vtables `0x7C9844` /
  `0x7C9858`. This is distinct from DBTCupAllocInstructions and was not
  needed for Gate-3 startup. Recover its season-transition semantics when
  broader promotion/relegation lifecycle work becomes active.
