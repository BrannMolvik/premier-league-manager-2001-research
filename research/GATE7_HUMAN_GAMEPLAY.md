# Gate 7 - Minimum Human-Manager Gameplay Loop

> **27 September 2026 startup-wage RNG correction:** deterministic RNG states,
> schedule orders, audit hashes and later gameplay outcomes in this file that
> conflict with `research/STARTUP_WAGE_RNG_CORRECTION.md` are superseded by
> that correction. The gate's functional conclusion remains valid.


_Status: COMPLETE (27 September 2026)_

Gate 7 proves that the reconstructed Premier League backend is directly usable by one human manager before original-UI fidelity, transfers, finance, or save/load are added.

## Implementation

`GameState.simulate_premier_league_human_fixture()` prepares one explicit human-controlled side and one autonomous AI side, then routes both through the same environment generation, MatchCalculator simulation, result persistence, Condition synchronization, injury/discipline persistence, Form persistence, Pitch Wear update, and Premier League table state used by autonomous matches.

`reconstruction/human_gameplay.py` adds the persistent minimum manager workflow: choose a Premier League club, inspect its runtime squad, set formation/XI/substitutes/tactics, optionally legal-autofill through the proven selection core, advance in recovered scheduler order, pause for the human fixture, simulate it through the shared backend, finish later same-day AI fixtures, run daily maintenance, inspect the result/table, and repeat.

Lineup validation requires exactly 11 starters, the competition substitute quota, unique players from the human squad, no currently unavailable player, and the Premier League Non-EU limit.

`reconstruction/app.py` now includes a temporary **Play** tab exposing club selection, formation 0..20, XI/substitute selection, legal deterministic 11+5 autofill, the four live tactical fields, advance, play, result text, and league table. This is intentionally not the later original-style UI.

## Automated regression

The synthetic Gate-7 regression uses a 20-club, 10-match-per-round Premier League shape. The human fixture is deliberately placed in the middle of the same-day scheduler list so AI fixtures execute both before and after it. The clean-room suite after the Gate-7 additions passes:

```text
Ran 407 tests
OK
```

## Canonical shipped-data audit

Runner: `reconstruction/canonical_human_gameplay_audit.py`.

Canonical authorized files are verified before execution and remain outside Git. The audit selected **Arsenal (club ID 0)**, auto-filled a legal human lineup before every fixture, and played six human-controlled Premier League fixtures while all other PL matches continued autonomously in the recovered Gate-4 order.

| Date | Fixture | Score | Arsenal record/points after |
| --- | --- | --- | --- |
| 19 Aug 2000 | Sunderland vs Arsenal | 1-2 | 1-0-0, 3 pts |
| 23 Aug 2000 | Arsenal vs Liverpool | 1-0 | 2-0-0, 6 pts |
| 26 Aug 2000 | Arsenal vs Charlton Athletic | 2-1 | 3-0-0, 9 pts |
| 2 Sep 2000 | Chelsea vs Arsenal | 3-1 | 3-0-1, 9 pts |
| 16 Sep 2000 | Bradford City vs Arsenal | 1-3 | 4-0-1, 12 pts |
| 23 Sep 2000 | Arsenal vs Coventry City | 1-1 | 4-1-1, 13 pts |

The run spans more than a month and completed exactly **60 Premier League results**, six complete 10-match matchdays.

Final human-squad/runtime checks: Condition remained within 28..80; Form remained within 0..4; two Arsenal players were injured at the final checkpoint, so repeated legal autofill adapted to evolving availability; no human player was suspended at the final checkpoint; match RNG ended at `0xBE52A1F6`.

Deterministic six-fixture audit SHA-256:

```text
6baeb94d17acbdeddcda253f66a6a5e62fb9c427a7ab42e7e7ff0f457721ebee
```

The earlier three-fixture smoke-audit SHA-256 was `1eab7a10822c9137fb13bf2327e23974fb1d14bcaa017e48bb061c95e5d6d21b`.

## Gate 7 completion audit

- [x] User-controlled setup feeds the same reconstructed match backend as AI teams.
- [x] Several weeks can be played without manual developer intervention.
- [x] A minimal temporary UI exposes the required gameplay loop.
- [x] Canonical shipped data has been exercised across six user fixtures and six complete matchdays.

Gate 8 may now begin: internal save/load for reliable development and playable sessions.
