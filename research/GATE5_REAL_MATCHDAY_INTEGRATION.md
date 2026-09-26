# Gate 5 - Canonical Real-Data Matchday Integration

> **27 September 2026 startup-wage RNG correction:** deterministic RNG states,
> schedule orders, audit hashes and later gameplay outcomes in this file that
> conflict with `research/STARTUP_WAGE_RNG_CORRECTION.md` are superseded by
> that correction. The gate's functional conclusion remains valid.


_Last verified: 27 September 2026_

Gate 5 proves that the reconstructed Premier League scheduler, AI match
preparation, MatchCalculator path, post-match persistence, result store, and
league-table state execute together against the authorized shipped FM2001
database.

## Canonical input verification

The reusable runner is:

`reconstruction/canonical_matchday_audit.py`

It begins with `verify_canonical_files()`, so integration runs fail before
simulation if the canonical executable/data/string hashes do not match the
analyzed release.

The verifier was reconciled in `72c60059d2da90eda78e41d69a163a52a3f3d998`
with two stale legacy diagnostic assertions. The current canonical verifier
passes all shipped-file hashes and Gate-3 materialization invariants.

## Scheduler integration

`GameState` now accepts one installed per-round Premier League scheduler
ordering through `install_premier_league_scheduler_order()`.

When installed, `simulate_due_premier_league_ai_fixtures()` uses the exact
Gate-4 order by default. Synthetic/lightweight callers without scheduler state
retain the explicitly documented stable fixture-ID fallback. An explicit
`fixture_order` argument still overrides both.

The canonical audit does not hard-code round orders. It reconstructs them from
the shipped data every run:

1. materialize all 9,346 Gate-3 schedule nodes from CRT state
   `0x2797444C`;
2. verify schedule SHA-256
   `0a22c9f0c1fa20de770a7d679583b6b4e4bdbd9363a5bda07194bfe8919cc35a`;
3. place the nodes into the 373 primary buckets and verify bucket-count SHA-256
   `fce6003d6a415813c08d3b55152ae6bf3da3fb9f68eef3bf4c0666e1df67718b`;
4. shuffle from `0x0E556598`, verify 9,178 draws and final state
   `0x839953AA`;
5. extract all 38 fixed Premier League round orders from the shuffled
   head-to-tail traversal.

## Canonical three-round integration run

The exact committed runner at
`6c87d6a1fae5b6e9ea2fac4fd1dccc4685ea01c5` was run against the canonical
shipped files for three consecutive Premier League rounds.

Audit SHA-256:

`dbe2aa4e5de50884b52616af3312e46f805d43b992c8cbb972d4446479535f4b`

Top-level results:

- rounds completed: **3**;
- real matches completed: **30**;
- days advanced from 18 August 2000: **8**;
- stored result count: **30**;
- table played total: **60**;
- table goals for / against: **87 / 87**;
- prepared match environments: **30**;
- Premier League runtime players: **644**;
- Condition range: **34..99**;
- injured PL players after round 3: **5**;
- suspended PL players after round 3: **3**;
- accumulated PL yellow total: **44**;
- nonzero Pitch Wear clubs: **10**;
- match RNG final state: **`0x140CDCFD`**.

### Round 1 - 19 August 2000

Exact scheduler order:

`8, 3, 2, 4, 6, 9, 5, 0, 1, 7`

Scores by fixture ID:

```text
8  1-2
3  0-3
2  3-0
4  0-0
6  4-0
9  3-1
5  3-1
0  2-0
1  2-1
7  2-0
```

All **20 clubs participate exactly once**. Ten results are stored once each.
Table played total becomes 20 and goals reconcile 28-for / 28-against.

### Round 2 - 23 August 2000

Exact scheduler order:

`14, 10, 15, 12, 18, 17, 11, 19, 16, 13`

Scores:

```text
14 2-1
10 1-2
15 4-3
12 1-0
18 0-1
17 2-0
11 4-2
19 1-2
16 2-2
13 3-3
```

### Round 3 - 26 August 2000

Exact scheduler order:

`27, 24, 25, 23, 26, 21, 28, 20, 22, 29`

Scores:

```text
27 2-2
24 0-4
25 2-0
23 2-1
26 0-1
21 1-0
28 0-1
20 2-1
22 1-0
29 1-2
```

## Persisted-state audit after round 3

Every Premier League club retained:

- exactly **11** active players;
- exactly **5** substitute-available players;
- no active/substitute overlap.

Across all 644 PL runtime players:

- every player belongs to one roster only;
- Condition stays within 0..100 (observed 34..99);
- Form stays within 0..4;
- every injured player has a return date;
- suspension matches remaining are never negative.

Observed Form-state distribution:

```text
0: 1
1: 16
2: 609
3: 14
4: 4
```

The five injuries all had valid return dates. Three active suspensions had
valid remaining counts and effective dates. Pitch Wear remained valid and
persisted between rounds.

## Validation

At `6c87d6a1fae5b6e9ea2fac4fd1dccc4685ea01c5`:

- reconstruction GitHub Actions: **402 tests passed**;
- repository asset-policy workflow: **passed**;
- the exact committed canonical audit runner completed successfully against
  the canonical shipped files.

## Gate-5 conclusion

All Gate-5 completion criteria are satisfied:

- canonical hashes are checked before each audit;
- a complete 10-match real Premier League round runs;
- all 20 clubs participate exactly once;
- results, table, statistics, discipline, injuries, Form, Condition, and Pitch
  Wear persist coherently;
- three consecutive canonical real rounds complete without invalid state.

Gate 6 can therefore extend the same audited path to the full 38-round /
380-fixture autonomous Premier League season and multiple deterministic seeds.
