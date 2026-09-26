# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 8 - Internal save/load**

Gates 1 through 7 are complete. Gate 7 closed after the human-controlled path was connected to the same reconstructed match backend as AI clubs, exposed through a temporary playable Tkinter surface, and exercised against canonical shipped data across six Arsenal fixtures / six complete Premier League matchdays from 19 August through 23 September 2000.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc contents are authorized for project use. Preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Gate-7 canonical evidence: `research/GATE7_HUMAN_GAMEPLAY.md`.
- Gate-7 audit runner: `reconstruction/canonical_human_gameplay_audit.py`.
- GitHub reconstruction Actions at `92a003f6fb6e08eb810de8eb964c73260329cb69`: **407 tests passed**.
- Repository asset-policy workflow at that checkpoint: **passed**.
- Canonical executable SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Stable startup / scheduler checkpoint

The solved canonical autonomous path through primary schedule finalization remains:

- actual-count primary competition RNG: **6,156 calls**;
- state entering primary `0x615BE0`: **`0x0E556598`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0x839953AA`**.

Gate-4 evidence: `research/GATE4_SCHEDULE_ORDER.md`.

## Stable autonomous-season checkpoint

Gate 6 completed three deterministic canonical 38-round / 380-fixture Premier League seasons with exact scheduler order, 19 home + 19 away matches for every club, reconciled league totals, valid 11+5 selection state after every round, and injury/return plus suspension/resolution progression.

Evidence: `research/GATE6_FULL_SEASON.md`.

## Gate-7 human gameplay checkpoint

Implemented:

- `GameState.simulate_premier_league_human_fixture()` routes a human side and AI side through the same MatchCalculator and post-match persistence backend;
- `HumanGameplayController` persists human club, formation, XI/bench, tactics and Team Orders;
- legal deterministic human lineup autofill reuses the proven lineup/Non-EU selection core;
- scheduler-aware advance pauses before the human fixture while preserving AI fixtures before/after it on the same date;
- the temporary Tkinter **Play** tab exposes club, lineup, tactics, advance, play, result and table.

Canonical six-fixture Arsenal audit:

- dates: 19 Aug to 23 Sep 2000;
- six complete 10-match PL matchdays / **60 stored results**;
- Arsenal record after six: **4 wins, 1 draw, 1 loss, 13 points**;
- human squad Condition remained **28..80**;
- two active injuries at the final checkpoint, with legal autofill continuing correctly;
- match RNG final state: **`0xBE52A1F6`**;
- audit SHA-256: `6baeb94d17acbdeddcda253f66a6a5e62fb9c427a7ab42e7e7ff0f457721ebee`.

Evidence: `research/GATE7_HUMAN_GAMEPLAY.md`.

## Gate-8 goal

Add an **internal versioned save format** for the modern port before attempting original FM2001 save compatibility.

Required persistent state includes, at minimum:

- current calendar date and scheduler order;
- clubs/managers/competition state required for continuation;
- mutable player skills, Condition, Form, positions, selection flags, injuries and suspensions;
- team tactics and human-manager selection/Team Orders;
- Premier League fixture results/table-reconstructible state;
- Pitch Wear and prepared/runtime state that materially affects continuation;
- relevant MSVC CRT RNG state;
- pending human matchday/controller state if a save occurs before the user fixture.

## Exact next task

1. Audit `GameState`, `HumanGameplayController`, competition state and runtime dataclasses for every mutable field that must survive save/reload.
2. Define a small explicit versioned JSON-compatible snapshot schema. Do not pickle live Python objects and do not conflate this with original PLM2001 save compatibility.
3. Implement save -> reload for the Gate-7 human gameplay state, including RNG and pending scheduler/controller state.
4. Add deterministic equivalence tests: branch one game state, save/reload one branch, then continue both through multiple fixtures and require identical results/state/RNG.
5. Add canonical shipped-data save/reload continuation audit, then re-audit Gate-8 criteria.

## Gate 8 completion criteria

- [ ] Calendar, clubs, players, managers, competitions, fixtures/results, injuries, suspensions, tactics, and relevant RNG state persist.
- [ ] Save -> reload -> continue produces equivalent state.
- [ ] Multi-week games can be resumed.
- [ ] Original PLM2001 save compatibility remains separately tracked if incomplete.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. Most relevant now:

- internal save/load is not yet implemented;
- original FM2001 save compatibility is explicitly later/separate;
- exact final league-table tie fallback remains unresolved;
- persistent-injury availability helper `0x405080` retains an approximation;
- transfers/contracts, finance/board, broader competitions, original front-end fidelity and FastView/3D remain later gates.

## Do not work on yet

Unless required to unblock Gate 8, defer:

- original FM2001 save-file compatibility;
- transfers/contracts implementation;
- finance/board implementation;
- broader competition season-transition behavior;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `BACKLOG.md` instead.
