# Gate 6 - Full Autonomous Premier League Season

> **27 September 2026 startup-wage RNG correction:** deterministic RNG states,
> schedule orders, audit hashes and later gameplay outcomes in this file that
> conflict with `research/STARTUP_WAGE_RNG_CORRECTION.md` are superseded by
> that correction. The gate's functional conclusion remains valid.


_Last verified: 27 September 2026_

Gate 6 extends the canonical real-data integration path from Gate 5 through a
complete autonomous Premier League season.

## Reusable audit

`reconstruction/canonical_matchday_audit.py` now performs full-season checks
when invoked with `--rounds 38`:

```text
PYTHONPATH=reconstruction \
  python reconstruction/canonical_matchday_audit.py \
  /path/to/canonical/game \
  --rounds 38 \
  --player-seed N
```

Every run:

1. verifies the canonical shipped-file hashes;
2. reconstructs the 9,346-node primary schedule from shipped data;
3. verifies the Gate-3 schedule digest and Gate-4 bucket-count digest;
4. reconstructs and installs all 38 Premier League scheduler orders;
5. runs the existing autonomous AI preparation / MatchCalculator /
   post-match persistence path for every due fixture;
6. audits table, roster, lineup, discipline, injury, Form, Condition, and
   Pitch Wear state.

## Full-season structural checks

A 38-round audit now requires:

- all **380 fixture IDs** completed exactly once;
- all 20 clubs with **38 played**;
- every club with exactly **19 home + 19 away** fixtures;
- table played total = **760**;
- global goals-for = goals-against;
- global wins = losses;
- W/D/L totals reconcile with played totals;
- aggregate draw-row count is even;
- table points reconcile as `3*wins + draws`;
- every PL runtime player remains in exactly one club roster;
- after every real matchday each participating club has exactly
  **11 active + 5 substitute-available** players with no overlap;
- Condition remains in **0..100** after every real round;
- Form remains in **0..4** after every real round;
- every active injury has a return date;
- suspension counters never become negative;
- a full season demonstrates both injury creation and injury return;
- a full season demonstrates both suspension creation and suspension
  resolution.

## Deterministic full-season passes

Three complete canonical seasons were executed with different deterministic
runtime-player startup seeds. Match scheduling always begins from the exact
Gate-4 primary-schedule completion state `0x839953AA`.

### Seed 1

Strengthened audit SHA-256:

`1516a4a311ec06566bb3e549b102eabc7990bf387f842836a2ffc0003f8819ec`

- fixtures/results: **380 / 380**;
- days advanced: **275**;
- final matchday: **20 May 2001**;
- table played total: **760**;
- global goals: **960**;
- table wins / draws / losses: **299 / 162 / 299**;
- table points total: **1,059**;
- Condition range: **60..99**;
- injury state entries / exits: **102 / 93**;
- distinct players ever injured: **86**;
- suspension state entries / exits: **52 / 48**;
- distinct players ever suspended: **46**;
- final injured / suspended: **9 / 4**;
- final yellow total: **576**;
- final match RNG state: **`0x2C36A2D4`**.

Every home-count and away-count entry is exactly 19.

### Seed 2

Audit SHA-256:

`a3a678366ef2d43b7ba9c84ee9e10bb7e64863b2bb293f7cb9a3214453782bb3`

- fixtures/results: **380 / 380**;
- table played total: **760**;
- global goals: **963**;
- Condition range: **55..99**;
- injury state entries / exits: **106 / 93**;
- suspension state entries / exits: **59 / 54**;
- final injured / suspended: **13 / 5**;
- final yellow total: **633**;
- final match RNG state: **`0xA8BCDCAD`**.

All clubs again have 19 home + 19 away and all full-season invariants pass.

### Seed 3

Audit SHA-256:

`74b41a698d8932fcf09bca6529cb744f7f6c4c09f47c891c1c870609cfeeadb4`

- fixtures/results: **380 / 380**;
- table played total: **760**;
- global goals: **1,024**;
- Condition range: **55..99**;
- injury state entries / exits: **114 / 97**;
- suspension state entries / exits: **62 / 60**;
- final injured / suspended: **17 / 2**;
- final yellow total: **653**;
- final match RNG state: **`0x8773A02A`**.

All clubs again have 19 home + 19 away and all full-season invariants pass.

The materially different goals, injury/suspension histories, and final RNG
states show that these are separate deterministic trajectories rather than
repeated copies of one season.

## Validation

At `b86980bd47e4919ed9ca4a15f22f8d2153c93fb9`:

- reconstruction GitHub Actions: **402 tests passed**;
- repository asset-policy workflow: **passed**;
- the strengthened full-season audit completed for seeds 1, 2, and 3.

No Gate-6 full-season failure was observed. Consequently there was no failing
full-season case to convert into a new focused regression. The earlier
scheduler/integration failures discovered on the way to Gates 4-6 were each
persisted as regression tests rather than left as chat-only findings.

## Gate-6 conclusion

All Gate-6 completion criteria are satisfied. The autonomous Premier League
backend now completes multiple deterministic 38-round / 380-fixture seasons
against canonical shipped data while retaining valid league, player, lineup,
discipline, injury, Form, Condition, and Pitch Wear state.

Gate 7 can therefore focus specifically on the incomplete human-controlled
match setup/workflow rather than autonomous-season stability.
