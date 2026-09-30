# FM2001 modern runtime reconstruction

This directory contains the modern replacement/runtime code used by the Windows 11 port. Authorized original FM2001 resources may be reused from `../original_assets/` according to `../research/ASSET_POLICY.md`; raw disc images and temporary extraction data stay outside Git.

## Canonical files

The runtime reads the analyzed FM2001 release from the user's existing installation, including `Master.dat`, `Static.dat`, `Core.str`, `English.str`, and `FOOTBAL.EXE` where executable-backed coefficients or verification are required.

Verify the shipped files before canonical integration work:

```text
python verify.py C:\Games\FM2001
```

`RUN_PROTOTYPE.cmd` opens the current Tkinter prototype. Its **Play** tab is a minimum human-manager gameplay surface, not the final presentation layer.

Gate 13 presentation work starts in `front_end_state.py`, which isolates
the recovered PStartMenu / TeamSelect navigation contract from simulation.
`front_end_session.py` is the separate **application boundary** connecting
those proven controls to the existing `HumanGameplayController` without
putting simulation rules into the presentation module.

The headless integration sequence is:

```python
from front_end_session import FrontEndSession
from front_end_state import StartMenuControl, TeamSelectControl

session = FrontEndSession.for_canonical_game_dir(game_dir)
session.dispatch(StartMenuControl.NEW_GAME)  # event 2: load backend, enter TeamSelect
session.choose_club(selected_club_id)         # presentation choice; no game mutation
outcome = session.dispatch(TeamSelectControl.START_CONTINUE)  # event 0x2A
# outcome.selected_manager is returned by the real backend.
# outcome.transition.command instructs the future original-asset renderer to
# hand off to the manager screen. No replacement screen has been designed.
```

TeamSelect Back (event `0x29`) returns to PStartMenu without synthesizing
an unverified backend reset. The current backend is limited to Premier League
teams; it does not yet implement the original multi-country selection UI.
The original visual renderer remains deliberately unimplemented until the
authorized graphics, labels and layout resources are inventoried and imported.

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

For the historically observed source path, deep mode extracts the nested raw
MODE1/2352 BIN image, **validates every physical sector**, then exposes the
original track through a read-only **virtual ISO9660/Joliet view**. Only
requested 2048-byte user-data sectors are read; it no longer needs to create a
second hundreds-of-MB temporary ISO file. The original separate conversion
helper remains available for manual/compatibility checks. It also inventories any loose
presentation resources directly packaged in the outer ZIP, including opaque
resources chosen via `--extract-path` or `--extract-path-file`. The loose
ZIP layer is scanned once; its disc-member list is retained for the nested
pass. 7-Zip is only an optional fallback for other supported disc-image formats.

The JSON report preserves both archive layers:

- `zip_files`: **every** outer-ZIP member, normalized path, byte size and
  whether it is a recognized nested disc container (raw BIN tracks are
  recognized by their Mode-1 sector signature, not the `.bin` suffix alone);
- `disc_files`: the complete nested ISO9660/Joliet disc catalog with normalized
  path, byte size and ISO extent;
- `candidates`: the smaller Gate-13 presentation shortlist, with hashes when
  bytes were intentionally extracted.

The catalog-query CLI searches **both** archive layers by default and annotates
result records as `zip` or `disc`. Use `--layer zip` or `--layer disc`
when investigating one layer. Layer filtering is analytical only: the
source-inventory exact-path staging CLI still matches source-relative paths
across both layers. If the same path is present more than once,
`--paths-only` refuses to emit an ambiguous list, and the extractor rejects
cross-layer and case-insensitive staging collisions instead of overwriting
one original with another. Isolate the correct source layer before staging
ambiguous assets; never pretend an unqualified path identifies both uniquely.

Use the full catalog to identify opaque layout/string resources rather than
guessing filenames. Query a saved report without reopening the
source archive:

```text
python gate13_catalog_query.py gate13-source.json --summary
python gate13_catalog_query.py gate13-source.json --layer zip --contains menu
python gate13_catalog_query.py gate13-source.json --contains menu
python gate13_catalog_query.py gate13-source.json --suffix dat --top-level Data
python gate13_catalog_query.py gate13-source.json --regex "(team|start|layout)"
```

Multiple `--contains` filters are ANDed. `--suffix`, `--top-level`, and
`--regex` can be combined to narrow opaque presentation leads. To turn a
query directly into a reproducible staging selection, emit paths only:

```text
python gate13_catalog_query.py gate13-source.json \
  --regex "(team|start|layout)" --paths-only > gate13-selected-paths.txt
```

Then feed that list back into the source inventory. `--only-explicit` prevents
other heuristic candidates from being staged alongside selected originals,
and requires a nonempty explicit path selection. Blank lines and `#`
comments are allowed in path-list files:

```text
python gate13_source_inventory.py <source.zip> --deep \
  --extract-path-file gate13-selected-paths.txt \
  --only-explicit \
  --require-all-explicit \
  --extract-candidates-to <staging-directory> \
  --output gate13-source-selected.json
```

Once an exact path is known, stage only that resource:

```text
python gate13_source_inventory.py <source.zip> --deep \
  --extract-path FM2001_Art/Generic/<exact-path> \
  --only-explicit \
  --extract-candidates-to <staging-directory> \
  --output gate13-source-selected.json
```

Repeat `--extract-path` for multiple exact files. By default, unresolved
requests are recorded as `unresolved_explicit_paths` and also produce warnings
in the JSON report. Add `--require-all-explicit` when staging: it saves that
report for audit but returns a failing exit code if any selected resource is
missing, preventing partial imports from being accepted accidentally.

After staging an intentionally selected original file, import it with
provenance:

```text
python gate13_asset_import.py <staging-dir> FM2001_Art/Generic/<asset> \
  --inventory-report gate13-source-selected.json --repo-root ..
```

The importer refuses full raw ZIP/ISO-style containers and performs the
strict known-hash/header check for `bground.444`. With
`--inventory-report`, it also verifies the source path is represented by
**exactly one extracted candidate**, whose SHA-256 and byte count match the
staged file. An unresolved/partial selection report prevents import.
Opaque UI `.bin` resources require this provenance report and must be
distinguishable from a raw disc image; they are not categorically banned
merely because of their filename extension. If the selected report includes
the source archive's SHA-256, it is retained in the import manifest notes.
The repository's `original_assets/MANIFEST.md` and asset-policy check remain
mandatory.
