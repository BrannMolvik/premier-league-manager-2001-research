# FM2001 modern runtime reconstruction

This directory contains the modern replacement/runtime code used by the Windows 11 port. Authorized original FM2001 resources may be reused from `../original_assets/` according to `../research/ASSET_POLICY.md`; raw disc images and temporary extraction data stay outside Git.

## Canonical files

The runtime reads the analyzed FM2001 release from the user's existing installation, including `Master.dat`, `Static.dat`, `Core.str`, `English.str`, and `FOOTBAL.EXE` where executable-backed coefficients or verification are required.

Verify the shipped files before canonical integration work:

```text
python verify.py C:\Games\FM2001
```

`RUN_PROTOTYPE.cmd` opens the current Tkinter prototype. Its **Play** tab is now a minimum human-manager gameplay surface, not just a data browser.

## Implemented modernized systems

Current tested implementation includes:

- canonical Master.dat / Static.dat / STR parsing and executable hash verification;
- mutable player, club, manager, competition, fixture, result and table state;
- aging/development/training and startup player state;
- exact shared MSVC CRT startup and primary competition RNG ledger;
- Cup allocation/pairing, procedural League generation, Scottish split nodes, and primary schedule-node materialization;
- exact 373-bucket primary schedule placement, conflict resolution, Fisher-Yates shuffle, and recovered Premier League same-day order;
- autonomous full 38-round / 380-fixture Premier League seasons;
- AI strategy, formation, XI/substitute selection, role assignment and Non-EU handling;
- match environment, weather, Pitch Wear and tactical state;
- normal-time MatchCalculator simulation with open play and set pieces;
- Condition decay, injuries/returns, discipline/suspensions, substitutions and post-match Form;
- one shared human-vs-AI backend path rather than a separate human match engine;
- persistent human club, formation, XI/bench, tactics and Team Orders workflow;
- scheduler-aware advance-to-user-fixture behavior while other PL matches continue;
- temporary Tkinter controls for club, lineup, tactics, advance/play, result and table.

Canonical real-data evidence now includes:

- three-round autonomous integration: `../research/GATE5_REAL_MATCHDAY_INTEGRATION.md`;
- three deterministic full seasons: `../research/GATE6_FULL_SEASON.md`;
- six human-controlled Arsenal fixtures over more than a month: `../research/GATE7_HUMAN_GAMEPLAY.md`.

The Gate-7 clean-room suite contains **407 passing tests**. Canonical human audit digest: `6baeb94d17acbdeddcda253f66a6a5e62fb9c427a7ab42e7e7ff0f457721ebee`.

## Current development boundary

The minimum human gameplay loop is complete. The next roadmap gate is **Gate 8: internal save/load**, so development/play sessions can persist calendar, roster, competition, fixture/result, injury/suspension, tactics and relevant RNG state.

Known remaining fidelity boundaries include:

- exact final league-table tie fallback beyond points / goal difference / goals scored;
- the remaining approximation around persistent-injury availability helper `0x405080`;
- internal save/load and later original-save compatibility;
- transfers/contracts and AI transfer activity;
- finances/board and broader management systems;
- broader competition season transitions;
- faithful original FM2001 front-end presentation;
- original match presentation / FastView / 3D.

The live list is maintained in `../research/FIDELITY_GAPS.md`. Research evidence, addresses, confidence levels, and gate status live under `../research/` and `../ROADMAP.md`.
