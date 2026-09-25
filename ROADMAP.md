# FM2001 Reconstruction Roadmap

## Purpose

This is the authoritative long-term development plan for the clean-room reconstruction of **The F.A. Premier League Football Manager 2001**.

The project is deliberately organized around sequential gates. Only one gate should be active at a time. Interesting discoveries outside the active gate belong in `research/BACKLOG.md` unless they are required to unblock the active work.

For the exact live resume point, read `research/CURRENT_STATE.md`.

## Working rules

1. GitHub is canonical. Chat context is temporary.
2. Work only on the active gate unless a dependency requires otherwise.
3. A finding is not project truth until it is persisted in the repository.
4. Commit every meaningful verified result.
5. During unresolved work, checkpoint after roughly ten minutes rather than risk losing the trace.
6. Update `research/CURRENT_STATE.md` whenever the exact next task changes.
7. Preserve old research as historical evidence; do not silently rewrite chronology.
8. Mark every fidelity claim as confirmed, probable, hypothesis, fallback, or approximation as appropriate.
9. Keep original copyrighted game assets outside this repository.
10. Before moving to the next gate, verify the gate's completion criteria.

## Current roadmap status

- **Active gate:** Gate 2 - Finish the startup RNG chain
- **Next gate:** Gate 3 - Build an executable startup RNG ledger
- **Gate 1 completed:** 26 September 2026
- **Pre-stabilization technical baseline:** `1014b042a19fc851b8d87e653ee1e5d807816630`
- **Gate 1 validation:** clean-room guard passed and reconstruction suite ran 307 tests successfully

---

## Gate 1 - Repository stabilization

**Status: COMPLETE (26 September 2026)**

Goal: make the repository itself sufficient to resume work across ChatGPT, Codex, and local-agent sessions.

Completion criteria:

- [x] `ROADMAP.md` is the canonical long-term plan.
- [x] `research/CURRENT_STATE.md` is the short canonical live resume point.
- [x] `research/BACKLOG.md` holds deliberately deferred work.
- [x] `research/FIDELITY_GAPS.md` tracks known reconstruction deviations.
- [x] `research/CONTINUATION_INSTRUCTIONS.md` starts new sessions from the live files rather than the full history.
- [x] A reusable new-chat handoff prompt exists.
- [x] Stale 279-test / Python-Random / match-day-blocker status text is reconciled.
- [x] Old audits are clearly historical snapshots.
- [x] A clean-room asset guard and `.gitignore` are present.
- [x] `reconstruction/verify.py` validates canonical hashes with explicit failures.
- [x] CI uses maintained GitHub Actions versions.
- [x] The stabilization changes are committed and the live state advances to Gate 2.

## Gate 2 - Finish the startup RNG chain

**Status: IN PROGRESS**

Goal: close the remaining mandatory new-game RNG path before the first Premier League schedule shuffle.

Work:

- trace TeamSelect construction and activation before the Start/Continue click;
- walk its caller chain backward until it reconnects with the already recovered database/player startup sequence;
- identify every mandatory CRT RNG consumer;
- separate mandatory, conditional, unreachable, and deterministic paths;
- preserve intermediate addresses and proof in the research files.

Completion criteria:

- [ ] TeamSelect lifetime/activation path is bounded.
- [ ] Every mandatory RNG consumer before schedule initialization is enumerated or an explicit unresolved boundary remains.
- [ ] The RNG state entering competition/schedule initialization can be described from a known seed for the standard new-game path.
- [ ] Findings and implementation consequences are committed.

## Gate 3 - Build an executable startup RNG ledger

Goal: turn the recovered startup sequence into reproducible code and tests.

The ledger should cover, as applicable:

- initial CRT seed;
- runtime-player constructor morale draws;
- player startup peak/development draws;
- generated-name setup;
- per-user youth generation;
- competition startup RNG;
- Premier League schedule-bucket shuffle.

Completion criteria:

- [ ] One shared MSVC CRT RNG stream is used for all mapped mandatory startup draws.
- [ ] Fixed-seed tests verify intermediate state, not only final output.
- [ ] Legacy Python-RNG fallbacks are removed or isolated where original behavior requires CRT RNG.
- [ ] Remaining uncertain consumers are explicitly documented.

## Gate 4 - Resolve exact Premier League matchday ordering

Goal: replace deterministic fixture-ID fallback with the original scheduling/execution order.

Completion criteria:

- [ ] Premier League source fixture insertion order is preserved.
- [ ] Schedule bucket/container selection is reproduced.
- [ ] Shuffle input RNG state is reproduced.
- [ ] Same-day extraction/execution order is reproduced.
- [ ] Regression tests cover the first several real matchdays.

## Gate 5 - Real-data matchday integration

Goal: prove the reconstructed systems work together against the canonical shipped database.

Completion criteria:

- [ ] Canonical data hashes are checked before integration runs.
- [ ] One complete real 10-match Premier League round runs.
- [ ] All 20 clubs participate exactly once in that round.
- [ ] Results, table, statistics, discipline, injuries, Form, Condition, and Pitch Wear persist coherently.
- [ ] Several consecutive real rounds run without invalid state.

## Gate 6 - Full autonomous Premier League season

Goal: complete a robust real-data 38-round / 380-fixture season.

Completion criteria:

- [ ] Exactly 380 fixtures complete once each.
- [ ] Every club plays 38 matches.
- [ ] Every club has 19 home and 19 away matches.
- [ ] League-table totals reconcile.
- [ ] Goals for/against reconcile globally.
- [ ] Discipline and suspensions progress correctly.
- [ ] Injuries and returns progress correctly.
- [ ] Condition/Form stay within valid state.
- [ ] No invalid player/club IDs or impossible lineups appear.
- [ ] Multiple deterministic seeds complete.
- [ ] Failures become regression tests.

## Gate 7 - Minimum human-manager gameplay loop

Goal: make the backend directly playable before pursuing full UI fidelity.

The user must be able to:

- start a new game;
- choose a club;
- inspect the squad;
- choose a lineup and tactics;
- advance time;
- play/simulate a fixture;
- inspect the result and table;
- continue to the next fixture.

Completion criteria:

- [ ] User-controlled setup feeds the same reconstructed match backend as AI teams.
- [ ] Several weeks can be played without manual developer intervention.

## Gate 8 - Internal save/load

Goal: support reliable development and play sessions before original save compatibility.

Completion criteria:

- [ ] Calendar, clubs, players, managers, competitions, fixtures/results, injuries, suspensions, tactics, and relevant RNG state persist.
- [ ] Save -> reload -> continue produces equivalent state.
- [ ] Multi-week games can be resumed.
- [ ] Original PLM2001 save compatibility remains separately tracked if incomplete.

## Gate 9 - Transfers and contracts

Goal: make squad building part of the playable season.

Completion criteria:

- [ ] Contract state is represented.
- [ ] Bids can be made and evaluated.
- [ ] Clubs accept/refuse according to reconstructed logic where known.
- [ ] Player negotiations, wages, duration, and transfer completion work.
- [ ] Player movement updates squads safely.
- [ ] AI transfer activity can occur during calendar progression.

## Gate 10 - Finances and board systems

Goal: make money and board constraints materially affect management.

Completion criteria:

- [ ] Club cash/balance is represented.
- [ ] Wage and transfer budgets are represented.
- [ ] Match and recurring income/cost paths are integrated.
- [ ] Player wages and transfer spending/income persist.
- [ ] Board expectations/job-security behavior is integrated where recovered.
- [ ] Approximations remain explicitly labeled.

## Gate 11 - Broader management systems

Goal: complete the core management-game loop.

Targets include:

- training/development workflows;
- scouting;
- youth;
- morale;
- medical/injury management;
- discipline;
- messages/news;
- recurring manager tasks.

Completion criteria:

- [ ] A human manager can complete a Premier League season using the core management systems.

## Gate 12 - Other competitions

Goal: expand outward from the Premier League without losing tested generic competition behavior.

Suggested order:

1. English domestic cups;
2. European qualification/competitions;
3. other required English league/divisional structures;
4. remaining competition formats.

Completion criteria:

- [ ] Each newly supported competition format has deterministic regression coverage.
- [ ] The Premier League no longer behaves as an isolated world.

## Gate 13 - Faithful management UI

Goal: reproduce the original interaction flow after gameplay is stable.

Suggested screen order:

1. main menu / TeamSelect;
2. manager home;
3. squad;
4. tactics/team selection;
5. fixtures/results;
6. league table;
7. player profile;
8. transfers;
9. finances;
10. messages/news;
11. training/scouting;
12. remaining screens.

Completion criteria:

- [ ] Simulation logic remains separated from presentation code.
- [ ] Normal play follows recognizably similar screen flow to FM2001.

## Gate 14 - FastView / match presentation

Goal: reconstruct presentation on top of an already stable event/state stream.

Completion criteria:

- [ ] Match presentation consumes reconstructed match state/events rather than duplicating simulation logic.
- [ ] A match is recognizably presented in the style/workflow of the original.
- [ ] Presentation fidelity does not block core management play.

## Gate 15 - Fidelity sweep

Goal: close the finite list in `research/FIDELITY_GAPS.md`.

Completion criteria:

- [ ] Every known deviation is either fixed, proven irrelevant, or explicitly accepted/documented.
- [ ] No deterministic fallback is described as original behavior without evidence.

## Gate 16 - Long-duration and destructive testing

Goal: find failures that only appear after repeated seasons or unusual state combinations.

Completion criteria:

- [ ] Multiple seasons can run automatically.
- [ ] Many deterministic seeds are exercised.
- [ ] No deadlocked calendar, roster collapse, invalid competition state, runaway injury/discipline state, save corruption, or unbounded state growth remains unexplained.
- [ ] Regressions exist for discovered failures.

## Gate 17 - Final clean-room and release audit

Goal: produce a distributable clean-room reconstruction.

Completion criteria:

- [ ] No original copyrighted executable/data assets are distributed.
- [ ] Full automated suite passes.
- [ ] Clean installation works outside the development environment.
- [ ] New game, season progression, save/reload, and management loop work.
- [ ] Documentation identifies remaining limitations honestly.
- [ ] Release build/version is archived against a known repository state.

## Final project definition of done

A person other than the developers can install the clean-room reconstruction, point it at legally owned original data where required, start a game, manage a club through a season, save/reload, and experience gameplay recognizably corresponding to **The F.A. Premier League Football Manager 2001**, with known fidelity differences documented rather than hidden.
