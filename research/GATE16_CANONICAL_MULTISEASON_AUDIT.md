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
