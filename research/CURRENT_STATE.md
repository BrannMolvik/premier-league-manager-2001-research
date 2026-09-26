# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 7 - Minimum human-manager gameplay loop**

Gates 1 through 6 are complete. Gate 6 closed after three deterministic
canonical 38-round / 380-fixture Premier League seasons completed with exact
recovered scheduler order and coherent match, table, lineup, discipline,
injury, Form, Condition, and Pitch Wear state.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Preserve and reuse original data,
music, sounds, interface graphics, strings, and other resources wherever
technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance
tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Gate-6 strengthened audit checkpoint:
  `b86980bd47e4919ed9ca4a15f22f8d2153c93fb9`.
- Reconstruction GitHub Actions at that checkpoint: **402 tests passed**.
- Repository asset-policy workflow: **passed**.
- Gate-5 evidence: `research/GATE5_REAL_MATCHDAY_INTEGRATION.md`.
- Gate-6 evidence: `research/GATE6_FULL_SEASON.md`.
- Canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Canonical startup/scheduler checkpoint

The solved canonical autonomous path through primary schedule finalization is:

- actual-count primary competition RNG: **6,156 calls**;
- state entering primary `0x615BE0`: **`0x0E556598`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0x839953AA`**.

See `research/GATE4_SCHEDULE_ORDER.md` for the recovered
`0x615950 / 0x615BE0 / 0x615C10` details.

## Gate-5 canonical real-data checkpoint

The reusable runner `reconstruction/canonical_matchday_audit.py` verifies
the canonical shipped files, reconstructs all 38 PL scheduler orders from the
shipped data, installs them into `GameState`, and runs the same autonomous
match backend used by the reconstruction.

Three-round audit SHA-256:

`dbe2aa4e5de50884b52616af3312e46f805d43b992c8cbb972d4446479535f4b`

The three-round run completed 30 real matches with all 20 clubs participating
once per round, table goals reconciling, valid 11+5 selections, coherent
injuries/suspensions, and valid Form/Condition.

## Gate-6 full-season checkpoint

The strengthened audit additionally requires:

- exactly 380 result fixture IDs;
- 38 matches per club;
- 19 home + 19 away per club;
- reconciled played/W/D/L/points/goals totals;
- valid 11 active + 5 substitute-available players after every real round;
- Condition 0..100 and Form 0..4 after every round;
- injury entry **and** return progression;
- suspension entry **and** resolution progression.

Three deterministic full seasons passed.

### Seed 1

Audit SHA-256:

`1516a4a311ec06566bb3e549b102eabc7990bf387f842836a2ffc0003f8819ec`

Key results:

- 380 results;
- table played total 760;
- global goals 960;
- wins/draws/losses 299/162/299;
- Condition 60..99;
- injury entries/exits 102/93;
- suspension entries/exits 52/48;
- final RNG `0x2C36A2D4`.

### Seed 2

Audit SHA-256:

`a3a678366ef2d43b7ba9c84ee9e10bb7e64863b2bb293f7cb9a3214453782bb3`

- global goals 963;
- Condition 55..99;
- injury entries/exits 106/93;
- suspension entries/exits 59/54;
- final RNG `0xA8BCDCAD`.

### Seed 3

Audit SHA-256:

`74b41a698d8932fcf09bca6529cb744f7f6c4c09f47c891c1c870609cfeeadb4`

- global goals 1,024;
- Condition 55..99;
- injury entries/exits 114/97;
- suspension entries/exits 62/60;
- final RNG `0x8773A02A`.

Every full-season run retained 19 home + 19 away fixtures for every club and
completed all 380 fixtures exactly once.

## Gate-7 goal

Make the reconstructed backend directly playable for one human manager before
pursuing full original UI fidelity.

The user must be able to:

- start a new game;
- choose a club;
- inspect the squad;
- choose a lineup and tactics;
- advance time;
- play/simulate a fixture;
- inspect the result and table;
- continue to the next fixture.

## Exact next task

1. Audit the existing human-control and prototype front-end code. Reuse the
   already-reconstructed AI/match backend rather than creating a parallel match
   engine.
2. Define the minimum persistent human-manager state: selected club, user
   tactics, chosen starting XI/substitutes, and whether the next due fixture
   contains the user club.
3. Implement the smallest backend gameplay controller that can:
   - create a canonical new-game state;
   - select a PL club;
   - expose squad/tactics/lineup;
   - advance to the next user fixture while autonomous PL matches continue;
   - simulate the user fixture through the same reconstructed backend;
   - expose result + current table;
   - continue repeatedly without developer-only intervention.
4. Add focused tests for a several-week human-controlled loop.
5. Only after the backend loop is stable, connect it to the existing prototype
   UI or a minimal temporary control surface as appropriate.

## Gate 7 completion criteria

- [ ] User-controlled setup feeds the same reconstructed match backend as AI
      teams.
- [ ] Several weeks can be played without manual developer intervention.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. Most relevant now:

- user-controlled match setup/workflow is incomplete;
- standalone synthetic callers without reconstructed scheduler state retain an
  explicit fixture-ID fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- internal save/load is Gate 8;
- transfers/contracts, finance/board, broader competitions, original front-end
  fidelity, and FastView/3D remain later gates.

## Do not work on yet

Unless required to unblock Gate 7, defer:

- save/load beyond what the gameplay loop strictly needs;
- transfers/contracts implementation;
- finance/board implementation;
- broader competition season-transition behavior;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `BACKLOG.md` instead.
