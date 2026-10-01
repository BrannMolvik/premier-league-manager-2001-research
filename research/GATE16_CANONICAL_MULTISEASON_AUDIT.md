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
results or replays, the runner records the fresh season-owned structural shape
for diagnostics:

- Premier League fixture and scheduler counts;
- shared primary entry count;
- primary shadow entry count;
- domestic Cup node count;
- European Cup node count;
- qualification Cup node count;
- live procedural-League owner count.

Recovery 136 proved that exact Cup node counts are not a valid cross-season
corruption invariant because annual qualification can legitimately change the
number of admitted direct Cup participants. The fail-closed guard now compares
each freshly installed runtime to **that cycle's own materialized schedule**.
The complete primary shadow, all three Cup owners, the shared-primary execution
entries, and live procedural owner keys must project exactly from the current
regeneration. A stale prior-season node therefore still fails closed, while a
legitimate participant-dependent current-season shape change does not.

The diagnostic shape remains in the JSON report, now also as
`fresh_state_shapes` for every rollover. This is a runtime-state accumulation
guard; it does not assert that serialized save byte length must be identical.

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


## Recovery 136 European-node isolation

The focused three-cycle diagnostic completed successfully and retained the
exact current-season Cup runtime alongside the installed European schedule.
Cycles 0 and 1 regenerated UEFA Cup (competition 10) round 210 with **79**
direct participants, producing `floor(79/2) = 39` two-leg pairings. Cycle 2
had **80** direct participants and therefore 40 pairings.

The only added installed nodes were therefore exactly:

- `("cup_first_leg", 10, 210, 39)`;
- `("cup_result", 10, 210, 39)`.

Round 211 consequently received 95 participants instead of 94, but both values
still produce 47 pairings. Round 212 onward retained the same pairing counts,
which is why the complete European-node delta was exactly +2.

This matches the recovered knockout preparation semantics in
`prepare_cup_knockout_round`: odd runtime participant counts are accepted,
the routine pairs `floor(count/2)`, and the final unpaired ClubRef is not
propagated as a bye. The cycle-2 shape change is therefore legitimate
qualification-dependent materialization, not cross-season accumulation.

The regression now models that exact class of change: a fresh European Cup may
gain two nodes when its current regeneration contains them, while an injected
stale Cup node that is absent from the current regeneration still fails closed.
