# FM2001 clean-room reconstruction

This directory contains clean-room code only. It does **not** include EA game data or executable code.

The parser reads a user's existing FM2001 files:

- `Master.dat`
- `Core.str`
- `English.str`
- `Static.dat`

Run:

```
python verify.py C:\Games\FM2001
```

to validate that the files match the analyzed release and that the core parsed invariants still hold. `RUN_PROTOTYPE.cmd` opens the small Tkinter data browser.

## Implemented clean-room systems

The reconstruction is no longer only a parser/browser. Current tested implementation includes:

- corrected Master.dat and Static.dat parsing for clubs, players, managers, countries, positions, competitions, rounds, and the 380 real Premier League fixtures;
- mutable runtime player state;
- monthly aging/development and training mechanics;
- Premier League dated fixtures, mutable results, and league table;
- exact runtime match-state defaults for Condition, Form, and position state;
- AI formation strategy, lineup selection, substitutes, role assignment, and Non-EU restriction handling;
- ordered match participant collection;
- exact role compatibility, role rating, and 4 x 20 x 17 attack/defence coefficient support;
- open-play, free-kick, corner, and penalty chance resolution;
- normal-time five-minute scheduling and chance routing;
- recurring Condition decay and match injury incidence;
- bookings, sendings-off, and suspension persistence;
- AI substitutions and injury replacements;
- possession/territory normalization;
- weather and home pitch wear;
- post-match Condition/Form synchronization;
- persistent match injury generation and return events;
- Premier League fixture -> match -> result -> table integration;
- fast-calendar fixture-before-maintenance day ordering;
- exact MSVC CRT RNG primitive used by the original executable;
- recovered DBRPlayer startup RNG block on the shared MSVC CRT stream;
- exact schedule-bucket head insertion and Fisher-Yates shuffle primitives;
- recovered fixed Premier League fixture insertion order and schedule-container selection.

At reconstruction-changing commit `0205d90a61d8b0386bfd6660a46910833257256a`, GitHub Actions ran **307 tests successfully**. Later commits through the pre-stabilization technical baseline `1014b042a19fc851b8d87e653ee1e5d807816630` changed research documentation rather than reconstruction code.

## Important fidelity boundaries

This remains a reconstruction prototype rather than a complete replacement.

Known boundaries include:

- the full mandatory startup RNG path before the first Premier League schedule shuffle is not yet completely bounded;
- the default multi-fixture season loop still uses deterministic fixture-ID order unless an explicit scheduler order is supplied;
- exact league-table tie ordering beyond points / goal difference / goals scored is unresolved and currently uses a deterministic club-ID fallback;
- persistent-injury availability counting still contains an approximation around original helper `0x405080`;
- some competition-specific eligibility and user-controlled match setup paths remain incomplete;
- contracts, transfers, finance/board logic are extensively researched but are not yet implemented as a complete clean-room gameplay loop;
- broader competitions, scouting, youth, and save compatibility remain incomplete;
- the current UI is a data browser rather than a faithful FM2001 management interface;
- FastView / 3D presentation remains largely unreconstructed.

The live list is maintained in `../research/FIDELITY_GAPS.md`.

Research evidence, addresses, and confidence levels live under `research/`. Code should only be promoted from deterministic fallback to fidelity claim when executable evidence supports it.
