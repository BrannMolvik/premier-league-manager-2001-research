# Gate 4 - Primary Schedule Placement and Premier League Order

_Last verified: 27 September 2026_

This note is the canonical evidence for Gate 4. It starts from the Gate-3
actual-count competition checkpoint and follows the primary schedule container
through placement, bucket shuffle, and same-day linked-list traversal.

## Executable path

Canonical `FOOTBAL.EXE` SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Recovered primary-container path:

```text
0x615670 -> 0x615700   construct primary ScheduleContainer
0x615950              choose date bucket / resolve conflicts / head-insert
0x615890 -> 0x615790  adjacent-bucket conflict scan
0x615BE0 -> 0x615AE0  ascending-bucket Fisher-Yates shuffle
0x615C10              later head-to-tail linked-list traversal
```

`0x615670` passes `0x16E` and `0x615700` adds seven, producing exactly
**373 primary buckets**. The primary container offset is **-1**.

For an ordinary startup date pair the nominal primary bucket is:

```text
7 * scheduled_week + scheduled_weekday - 1
```

`0x615950` contains the original Christmas-Day exception. When the computed
calendar date is 25 December it advances the target by one bucket before the
conflict search.

## Conflict placement

The complete Gate-3 schedule-node stream is supplied to `0x615950` in
construction order. Each chosen bucket is head-inserted.

The overlap predicate is the already-recovered generic ClubRef identity used by
CupMatch / FirstLegMatch / SecondLegMatch / LeagueMatch:

- two resolved refs conflict only when they resolve to the same club;
- resolved vs unresolved does not conflict;
- two unresolved refs conflict only when type, referenced runtime object, and
  selector are all equal.

The first conflict probe covers `center-1 .. center+1`. If occupied by a
conflicting node, the search expands in two-bucket steps. The branch at
`0x6159D1` chooses the later side on an exact-distance tie.

Canonical complete-node placement results:

- input nodes: **9,346**;
- non-empty primary buckets: **168**;
- largest bucket: **147 nodes**;
- nodes displaced from their nominal bucket by conflict placement: **38**;
- compact-JSON SHA-256 of the 373-element bucket-count vector:
  `fce6003d6a415813c08d3b55152ae6bf3da3fb9f68eef3bf4c0666e1df67718b`.

## First Premier League matchday / bucket 54

Premier League round 1 is week 7 / weekday 6:

```text
7 * 7 + 6 - 1 = bucket 54
```

With the complete 9,346-node set:

- bucket 54 contains **142 nodes** before shuffle;
- all 142 were nominal bucket-54 insertions;
- **0** nodes moved into bucket 54;
- **0** nominal bucket-54 nodes moved out;
- composition is **132 procedural LeagueMatch nodes + 10 fixed Premier League nodes**;
- PL fixtures occupy pre-shuffle relative slots **96..105**;
- those slots contain fixture IDs **9,8,7,6,5,4,3,2,1,0**.

The corrected Gate-3 state entering primary `0x615BE0` is
**`0x0E556598`**.

Buckets 0..53 consume **391** shuffle draws, so bucket 54 begins at
**`0x1CBB48A1`**. Its 142-node Fisher-Yates consumes 141 draws and leaves
state **`0xC290356C`**.

After shuffle, `0x615C10` walks the linked list head-to-tail. The first
Premier League matchday therefore executes its ten PL fixtures in this order:

```text
8, 3, 2, 4, 6, 9, 5, 0, 1, 7
```

Their relative positions among all 142 bucket entries are:

```text
0, 8, 10, 16, 26, 78, 88, 95, 97, 103
```

## Complete primary shuffle

`0x615BE0` visits primary buckets in ascending index order. For each bucket,
`0x615AE0` copies the current linked-list order to an array, performs
descending Fisher-Yates `RNG(N), RNG(N-1), ..., RNG(2)`, and rewires the
linked list in the resulting array order.

Canonical complete primary shuffle:

- starting state: **`0x0E556598`**;
- bucket-shuffle draws: **9,178**;
- final state after all 373 primary buckets: **`0x839953AA`**.

This final state is distinct from the Gate-3 boundary because it includes the
entire primary schedule-container shuffle.

## First ten Premier League matchday orders

These are canonical shipped-data results from the complete node set and shared
CRT stream. They are regression-locked in
`reconstruction/test_primary_schedule.py`.

| PL round | Bucket | CRT state before bucket | Fixture execution order |
| ---: | ---: | --- | --- |
| 1 | 54 | `0x1CBB48A1` | 8, 3, 2, 4, 6, 9, 5, 0, 1, 7 |
| 2 | 58 | `0xC836DF29` | 14, 10, 15, 12, 18, 17, 11, 19, 16, 13 |
| 3 | 61 | `0x2A01F910` | 27, 24, 25, 23, 26, 21, 28, 20, 22, 29 |
| 4 | 68 | `0x24BF4337` | 37, 36, 33, 30, 38, 32, 31, 35, 39, 34 |
| 5 | 82 | `0x895E0D2A` | 43, 48, 42, 41, 47, 45, 46, 44, 40, 49 |
| 6 | 89 | `0xA13ED3A6` | 53, 54, 51, 50, 56, 57, 59, 52, 58, 55 |
| 7 | 96 | `0x929F341B` | 60, 65, 64, 68, 67, 69, 66, 62, 63, 61 |
| 8 | 103 | `0x555492A2` | 73, 74, 78, 75, 70, 77, 72, 79, 76, 71 |
| 9 | 117 | `0x0191E699` | 81, 88, 84, 82, 83, 87, 89, 80, 85, 86 |
| 10 | 124 | `0xC067FF47` | 95, 98, 94, 90, 96, 99, 91, 97, 92, 93 |

Round 2's bucket contains only those ten PL fixtures. The other listed
matchdays share their bucket with other competition nodes, so the PL matches
appear at non-contiguous linked-list positions.

## Clean-room implementation

`reconstruction/primary_schedule.py` now provides:

- `nominal_primary_schedule_bucket()`;
- exact generic `0x615950` conflict placement;
- full 373-bucket head-insertion materialization;
- exact `0x615BE0 -> 0x615AE0` bucket shuffle;
- fixed-League fixture-order extraction in `0x615C10` traversal order.

Validation at `c44e72ddae2e7976e8a1685f1662d659dc4a5e4c`:

- reconstruction GitHub Actions: **399 tests passed**;
- repository asset-policy workflow: **passed**.

## Gate-4 conclusion

The Premier League fixed-fixture source order, primary container/date
selection, generic conflict placement, corrected shuffle input state, bucket
Fisher-Yates, and head-to-tail same-day traversal are all reproduced and
regression-covered.

The deterministic fixture-ID fallback in the standalone matchday API is still
useful for synthetic callers that do not supply startup scheduler state, but
the original scheduler order is no longer unknown. Gate 5 can now integrate
the recovered order into canonical real-data matchday execution.
