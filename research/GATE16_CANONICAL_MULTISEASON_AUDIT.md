# Gate 16 canonical multi-season audit runner

_Date: 1 October 2026 KST_

## Purpose

Gate 16 already has broad synthetic long-duration coverage, but canonical
shipped-data multi-season execution remains open. Recovery 134 adds a dedicated
runner for that exact task:

`reconstruction/canonical_multiseason_audit.py`

The runner is preparation for the real canonical execution, not a substitute
for it. Gate 16 remains incomplete until the runner is executed successfully
against the authorized original FM2001 source data.

## Fail-closed season boundary

Each cycle uses the same `_qualification_if_complete` helper as the proven
Gate-12 canonical annual rollover audit. It therefore does not create or inject
standings, qualification rankings, Cup outcomes, membership swaps, or RNG
state. The live primary scheduler must advance until all recovered annual
qualification inputs exist naturally.

Once the qualification boundary is ready, the runner requires the live Premier
League to have exactly 380 completed fixtures, 20 table rows, 38 matches per
club, reconciled played totals, reconciled goals, and reconciled wins/losses.

## Rollover invariants

Every annual regeneration must then:

- replace the prior Premier League runtime object;
- install exactly 380 fresh Premier League fixtures and zero carried results;
- clear prepared match environments;
- keep the Premier League scheduler duplicate-free and exactly equal to the new
  fixture set;
- commit the controller CRT state returned by annual regeneration;
- commit the previewed membership transition atomically;
- retain every played annual type-3 qualification League as a live procedural
  League owner;
- leave a nonempty shared primary execution order.

The runner also checks club-roster references, player ownership, competition
membership references, Condition, Form, and suspension bounds before every
rollover.

## State-growth guard

Immediately after each regeneration, before the new season accumulates dynamic
results or replays, the runner records a fresh season-owned structural shape:

- Premier League fixture and scheduler counts;
- shared primary entry count;
- primary shadow entry count;
- domestic Cup node count;
- European Cup node count;
- qualification Cup node count;
- live procedural-League owner count.

That fresh structural shape must remain identical across all audited rollovers.
This is deliberately a runtime-state accumulation guard. It does not assert that
serialized save byte length must be identical.

## Canonical command

On a healthy execution path with the authorized original game directory:

```text
cd reconstruction
python canonical_multiseason_audit.py <game-dir> --player-seed 1 --rollovers 3
```

The default is three complete qualification/regeneration cycles on one
continuous controller. A pass should be persisted with the JSON report and the
exact canonical source hash receipts before it is promoted as Gate-16 evidence.

## Recovery 134 infrastructure boundary

The fresh Recovery-134 sandbox failed before its first shell process could
start with `caas.internal.errors.ClientError`. Therefore no canonical source
hash or multi-season runtime result is claimed by this change. Repository-side
runner tests are intentionally separate from the future private shipped-data
execution.


## Recovery 135 canonical execution result

Recovery 135 cleared the prior execution-infrastructure blocker and executed the
canonical runner against the authorized shipped source. Before execution:

- the 511,121,336-byte Library source ZIP was materialized and the raw
  MODE1/2352 disc image was extracted outside Git;
- all **268,549** raw sectors passed the repository's full-sector
  `verify_mode1_2352_image` validation;
- `Master.dat`, `Static.dat`, `English.str`, and `Core.str` matched their
  pinned canonical SHA-256 values;
- the persisted reconstruction runtime ZIP matched its recorded
  `9167302c608882161954109d617824422671d2999d69006bff5d662adeb2c4d6`
  digest;
- the executed `canonical_multiseason_audit.py` matched GitHub blob
  `a6a1de8782eca06291aeffefba11ff4bcd27c14b`.

The exact seed-1, three-rollover canonical process ran for about 22 minutes and
then failed closed on cycle 2, rather than on infrastructure:

```text
cycle 2: fresh season-owned state shape changed
(380, 380, 5735, 9344, 291, 371, 311, 13)
->
(380, 380, 5737, 9346, 291, 373, 311, 13)
```

Only three linked counts changed: shared-primary entries **+2**, shadow entries
**+2**, and European Cup nodes **+2**. Premier League fixture/scheduler counts,
domestic Cup nodes, qualification Cup nodes, and procedural-League owner count
were unchanged.

This is a verified Gate-16 finding, not a passing audit. The immediate next
task is to isolate the two added European nodes by competition/round and prove
whether they are legitimate participant-dependent annual Cup materialization
or an actual cross-season accumulation defect. A regression must encode that
boundary before the canonical three-rollover audit is rerun.
