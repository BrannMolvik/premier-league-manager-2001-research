# Project Audit — 25 September 2026

> **Historical snapshot notice (added 26 September 2026):** This audit is preserved as a dated record of the repository at its stated parent HEAD. Its **279-test** count and Python-`random.Random` startup risk were accurate to that audit point but were superseded by later commits. Use `research/CURRENT_STATE.md` for live status, `ROADMAP.md` for the active plan, and `research/FIDELITY_GAPS.md` for current unresolved fidelity boundaries.

## Scope

This audit reviews the canonical GitHub state after the large MatchCalculator,
AI preparation, post-match persistence and Premier League scheduler
reconstruction push.

Canonical executable:

- SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Audit parent HEAD:

- `e956925cfdc12cd96583a3cbd6bf86d70d13fa31` — Resolve Premier League schedule container

Latest CI at that parent:

- GitHub Actions reconstruction suite: **279 tests, all passing**

## Headline conclusion

The project remains feasible and has advanced materially beyond the 24
September audit. The earlier description of the clean-room implementation as
a 5–10% parser/browser is no longer accurate.

The strongest new result is that the core autonomous Premier League match path
is now connected end to end:

```text
original data
 -> mutable runtime players
 -> AI formation / XI / bench preparation
 -> MatchCalculator normal-time simulation
 -> cards / injuries / substitutions / possession
 -> score
 -> persistent Form / Condition / discipline / injury state
 -> Premier League result and table
 -> dated maintenance / next fixtures
```

This is not yet the complete game, but the existential uncertainty around
whether the football simulation backend can be faithfully reconstructed has
been substantially reduced.

## Current implementation assessment

| Area | Approximate implementation status | Audit assessment |
| --- | ---: | --- |
| Original data parsing | 88–92% | Strong and broadly tested for the core shipped databases |
| Runtime player state | 80–85% | Important selection, match and persistence fields represented |
| Development / training | 85–90% | Core age curve, peaks, training profiles and monthly changes implemented |
| MatchCalculator normal time | 88–93% | Major chance, state and timing systems implemented and tested |
| AI match preparation | 82–88% | Formation, XI, bench, restrictions and participant bridge substantially implemented |
| Match persistence | 88–92% | Discipline, injuries, Condition, Form and Pitch Wear connected |
| Premier League fixtures/table | 90%+ | Original schedule, dates, result storage and standings operational |
| Calendar / season progression | 70–75% | Due fixtures and proven fixture-before-maintenance ordering implemented |
| Exact same-day fixture order | 70–80% | RNG, head insertion, shuffle, PL source order and container selection recovered; shared startup RNG state remains |
| Transfers/contracts clean-room implementation | 10–20% | Research is much further ahead than implementation |
| Finance/board clean-room implementation | 5–15% | Research corpus is substantial; gameplay code is not |
| Other competitions | 25–40% | Core structures known; full integration incomplete |
| Scouting/youth | 15–25% | Mostly research-stage |
| Save compatibility | 10–20% | Individual serialization facts known; complete format not implemented |
| User-controlled management path | 30–40% | AI autonomous path is much further ahead |
| UI / original-game feel | 15–25% | Browser/prototype only |
| FastView / 3D | 5–15% | Still intentionally low priority |

Two different progress measures should continue to be kept separate:

- **Premier League autonomous season backend:** roughly 65–70% toward a robust
  playable simulation loop.
- **Complete game replacement:** substantially lower because transfers,
  finance, user workflows, UI, saves, broader competitions and presentation
  remain large pieces.

## Strongest verified implementation blocks

### Match engine

The reconstruction now includes:

- type-1 open play;
- type-2 free kicks;
- type-3 corners;
- type-4 penalties;
- Heading/Shooting finish mode;
- exact role compatibility and Form multipliers;
- attack/defence strength coefficient matrices;
- five-minute attack scheduling;
- Condition decay and injury incidence;
- discipline;
- AI substitutions;
- possession and territory;
- Half Time / Full Time timeline handling.

### AI preparation

Implemented behavior includes:

- all 21 original first-team formation templates;
- exact two-pass AI starter selection core;
- Form-adjusted role scoring;
- ranked substitutes;
- active/substitute runtime flags;
- Non-EU limit and retry behavior;
- Premier League strategy/formation inputs;
- runtime participant collection.

### Persistence

Connected post-match behavior includes:

- yellow/red discipline;
- suspension state;
- participant-ordered card/injury RNG handling;
- persistent injury generation;
- injury return date/event behavior;
- post-match Form;
- home Pitch Wear and daily recovery.

### Season scheduling

Recovered and implemented pieces now include:

- Static.dat round dates;
- due-fixture execution;
- fixture-before-return/maintenance ordering;
- original MSVC CRT RNG;
- schedule bucket head insertion;
- descending Fisher-Yates shuffle;
- fixed Premier League fixture source/insertion order;
- Premier League schedule-container selection.

## Audit findings / risks

### 1. Global RNG is not yet unified in reconstruction

This is the most important newly identified implementation risk.

`RuntimePlayer.from_database_player` receives Python `random.Random` and uses
`rng.randrange` for the three per-player peak-age draws. The reverse
engineering of `0x41E970` says those draws call the same bounded original RNG
family (`0x64D540`) now reconstructed in `match_schedule.MsvcCrtRng`.

Therefore the **development formulas are valid**, but a clean-room new game
does not yet consume one shared original RNG stream from player initialization
through schedule shuffling and later gameplay.

This matters for bit-exact/draw-exact reproduction. It does not invalidate the
isolated unit tests.

### 2. Premier League simultaneous-fixture execution remains a fallback

`GameState.simulate_due_premier_league_ai_fixtures` still defaults to the
stable fixture ordering exposed by `fixtures_on()`, currently fixture-ID
sorted.

That fallback is deliberately documented and callers can inject an explicit
fixture order. It should not be described as original behavior.

The remaining research task has narrowed considerably: recover the shared CRT
state and all RNG consumers before the mode-0 `0x947AD8` bucket shuffle.

### 3. League tie ordering is incomplete

`PremierLeagueState.table()` implements points, goal difference and goals
scored, then uses club ID as an isolated deterministic fallback. The exact
original fallback after those keys is not yet traced.

This can affect league-position-dependent AI strategy in tied tables.

### 4. Documentation had drifted behind implementation

The audit found several stale statements:

- `reconstruction/README.md` still said season simulation/AI and the match
  engine were not implemented;
- `research/FINDINGS.md` still described authoritative match-day
  initialization as the principal backend match blocker, despite later AI
  preparation work;
- the 24 September project audit still described MatchCalculator knowledge as
  15–25% and actual clean-room implementation as 5–10%.

These documents are historical evidence but must not be treated as the latest
status after this audit.

### 5. Research is still far ahead of implementation in management systems

The repository contains deep work on transfers, contracts, cash, chairman
budgets, stadium/commercial systems and DBRUser state, but there are no
equivalent mature reconstruction modules for those systems yet.

This is now the largest breadth gap in producing a game that *feels* like
FM2001 rather than only a football-season simulator.

### 6. Passing unit tests are necessary but not sufficient

The 279-test suite is valuable and currently green. Most tests are deterministic
unit/regression tests against recovered formulas and branch order.

The next quality step should add larger integration tests using the real
shipped Premier League database, especially:

- all ten fixtures on one real matchday;
- several consecutive real rounds;
- then a full autonomous 38-round / 380-fixture season;
- invariants for player availability, discipline, injuries, pitch wear and
  table totals across the run.

## Documentation reconciliation

This audit treats later evidence as superseding older milestone text. In
particular, old sections in PROGRESS.md and the 24 September audits remain
useful historical records but are not current task descriptions.

The current active engineering/research sequence should be:

1. unify the original RNG stream from startup/player initialization through
   schedule construction;
2. finish exact Premier League same-day shuffle state;
3. execute real ten-match matchdays and multi-round integration tests;
4. run a complete autonomous 380-fixture Premier League season;
5. then shift substantial implementation effort to contracts/transfers and
   finance/board state while retaining match-engine regression coverage.

## Persistence audit

Persistence discipline is currently strong:

- recent verified work has been committed in small blocks;
- three successive schedule commits before this audit each passed CI;
- no EA executable or game-data asset has been added to the repository;
- the latest live investigation after `e956925` had begun examining
  pre-shuffle RNG consumers, but no uncommitted inference from that trace is
  counted as canonical in this audit.

## Overall conclusion

The current repository is best described as:

> A large evidence-backed reverse-engineering corpus plus a substantial tested
> clean-room Premier League simulation backend, with management-game breadth
> and exact global RNG sequencing now more important than basic match-engine
> feasibility.

The project remains feasible. The immediate technical priority is not to
rewrite the match engine again; it is to connect the already recovered systems
under one faithful RNG/state timeline and stress them over real full-season
data.
