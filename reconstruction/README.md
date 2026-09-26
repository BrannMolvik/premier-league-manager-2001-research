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
- temporary Tkinter controls for club, lineup, tactics, advance/play, result and table;
- schema-2 internal save/load with source-database binding, gzip `.fm2k` files, mid-matchday continuation, and Play-tab Save/Load controls.

Canonical real-data evidence now includes:

- three-round autonomous integration: `../research/GATE5_REAL_MATCHDAY_INTEGRATION.md`;
- three deterministic full seasons: `../research/GATE6_FULL_SEASON.md`;
- six human-controlled Arsenal fixtures over more than a month: `../research/GATE7_HUMAN_GAMEPLAY.md`;
- canonical mid-matchday save/reload branch equivalence through that same six-fixture span: `../research/GATE8_INTERNAL_SAVE.md`.

The current reconstruction suite contains **413 passing tests**. Gate-8 canonical save/reload audit digest: `69a91dbce914be2fe5babdf8a8c71ad77bad5653c9cac09468520330f7c7b413`.

## Current development boundary

The minimum human gameplay loop and internal resumable save/load are complete. The active roadmap gate is **Gate 9: transfers and contracts**, making squad building part of the playable season.

Known remaining fidelity boundaries include:

- exact final league-table tie fallback beyond points / goal difference / goals scored;
- the remaining approximation around persistent-injury availability helper `0x405080`;
- original FM2001 save-file compatibility;
- transfers/contracts and AI transfer activity;
- finances/board and broader management systems;
- broader competition season transitions;
- faithful original FM2001 front-end presentation;
- original match presentation / FastView / 3D.

The live list is maintained in `../research/FIDELITY_GAPS.md`. Research evidence, addresses, confidence levels, and gate status live under `../research/` and `../ROADMAP.md`.
