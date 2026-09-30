# FM2001 modern runtime reconstruction

This directory contains the modern replacement/runtime code used by the Windows 11 port. Authorized original FM2001 resources may be reused from `../original_assets/` according to `../research/ASSET_POLICY.md`; raw disc images and temporary extraction data stay outside Git.

## Canonical files

The runtime reads the analyzed FM2001 release from the user's existing installation, including `Master.dat`, `Static.dat`, `Core.str`, `English.str`, and `FOOTBAL.EXE` where executable-backed coefficients or verification are required.

Verify the shipped files before canonical integration work:

```text
python verify.py C:\Games\FM2001
```

`RUN_PROTOTYPE.cmd` opens the current Tkinter prototype. Its **Play** tab is a minimum human-manager gameplay surface, not the final presentation layer.

Gate 13 presentation work now starts in `front_end_state.py`, which isolates the recovered PStartMenu / TeamSelect navigation contract from simulation code. Rendering remains intentionally unimplemented there until the authorized original UI resources are inventoried and imported.

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
- schema-8 internal save/load with source-database binding, gzip `.fm2k` files, mid-matchday continuation, transfer state, and Play-tab Save/Load controls;
- evidence-backed human cash bids, player contract terms, scheduled transfer completion and safe roster movement;
- recurring Saturday autonomous AI acquisitions integrated into calendar progression.

Canonical real-data evidence now includes:

- three-round autonomous integration: `../research/GATE5_REAL_MATCHDAY_INTEGRATION.md`;
- three deterministic full seasons: `../research/GATE6_FULL_SEASON.md`;
- six human-controlled Arsenal fixtures over more than a month: `../research/GATE7_HUMAN_GAMEPLAY.md`;
- canonical mid-matchday save/reload branch equivalence through that same six-fixture span: `../research/GATE8_INTERNAL_SAVE.md`;
- transfer/contract completion with human and AI calendar paths: `../research/GATE9_TRANSFERS_AND_CONTRACTS.md`.

The final Gate-9 reconstruction checkpoint contains **486 passing tests**. Gate-8 historical canonical save/reload evidence remains in `../research/GATE8_INTERNAL_SAVE.md`.

## Current development boundary

Gates 1 through 12 are complete. The active roadmap gate is **Gate 13: restore original management presentation**, beginning with the original PStartMenu / TeamSelect flow while preserving the stable simulation backend.

Known remaining fidelity boundaries include:

- exact final league-table tie fallback beyond points / goal difference / goals scored;
- the remaining approximation around persistent-injury availability helper `0x405080`;
- original FM2001 save-file compatibility;
- residual transfer-negotiation / same-day ordering fidelity gaps tracked explicitly;
- finances/board and broader management systems;
- broader competition season transitions;
- faithful original FM2001 front-end presentation;
- original match presentation / FastView / 3D.

The live list is maintained in `../research/FIDELITY_GAPS.md`. Research evidence, addresses, confidence levels, and gate status live under `../research/` and `../ROADMAP.md`.


## Gate 13 source inventory

When the authorized source archive is available as local bytes, inventory it
without committing the raw archive:

```text
python gate13_source_inventory.py <source.zip> --deep --hash-source --output gate13-source.json
```

If the ZIP contains the historically observed raw MODE1/2352 BIN image, deep
mode first validates and converts each 2352-byte sector to its 2048-byte Mode-1
user-data payload in a temporary ISO file. It then uses 7-Zip (`7z`, `7zz`,
or `7za`) to list the ISO9660/Joliet filesystem. Pass
`--seven-zip <path>` when it is not on PATH. Use
`--extract-candidates-to <staging-directory>` only for a deliberate staging
extract; imported originals still require `original_assets/MANIFEST.md`
provenance and the repository asset-policy check.


After staging an intentionally selected original file, import it with provenance:

```text
python gate13_asset_import.py <staging-dir> FM2001_Art/Generic/<asset> --repo-root ..
```

The importer refuses raw ZIP/BIN/ISO-style containers and performs the strict
known-hash/header check for `bground.444`.
