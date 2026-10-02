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


## Recovery 136 projection-checker correction

After PR #64 merged, the exact merged runner was executed again against the
reverified canonical source. The game runtime completed the first canonical
season and annual regeneration, but the new audit checker failed at cycle 0
with:

`fresh shared-primary order differs from current regeneration projection`

This was an audit-harness defect, not a simulation-state failure. The checker
had derived expected procedural entries from `state.procedural_leagues`, which
contains only competition/context pairs that successfully materialize a live
`LiveProceduralLeagueState`. The source-backed
`gate12_primary_matchday_order` contract is broader: it retains every
`league_match` whose **competition ID** is in the authorized procedural set,
even when a particular context does not become a live owner.

The repaired checker resolves the same procedural competition-ID set used by
`HumanGameplayController.regenerate_annual_primary_season`:

- English primary procedural roots;
- played annual type-3 League qualification sources;
- procedural League children required by annual Cup sources.

Expected shared-primary entries are then projected from those source-authorized
competition IDs, while the separate stale-owner guard still rejects a live
procedural owner whose competition/context no longer exists in the current
materialized schedule.

A regression now covers the exact boundary: competition 14/context 3 remains a
valid shared-primary procedural entry when 14 is authorized even if that
context is absent from `state.procedural_leagues`.


## Recovery 137 passing canonical seed-1 audit

After PR #65's projection-checker correction passed full CI, the exact
authorized shipped-data audit was rerun with player seed 1 for three consecutive
qualification/regeneration cycles. The process exited **0** after 1,617.49
seconds and reached 2003-06-02.

All three cycles completed 380 Premier League fixtures, retained 30,064 live
roster references, applied 28 annual membership changes, committed the
regeneration RNG atomically and passed the current-regeneration projection
guards. The fresh structural shapes were:

- cycle 0: `(380,380,5735,9344,291,371,311,13)`;
- cycle 1: `(380,380,5735,9344,291,371,311,13)`;
- cycle 2: `(380,380,5737,9346,291,373,311,13)`.

The cycle-2 difference is the already-proven UEFA Cup participant-dependent
materialization, not retained prior-season state. Exact machine-readable
evidence is stored in
`research/evidence/GATE16_CANONICAL_MULTISEASON_SEED1_RECOVERY137.json`.

Verification for PR #65 head `31ab282de6d6f62b498801de624526276837ce5a`:

- asset-policy run `36867367968`: passed;
- reconstruction run `36867368043`: passed;
- PR #65 squash merge: `7f3f83eb98b9f29039b691197505dbe74c8b0851`.

This closes the previously open canonical seed-1 multi-season execution
boundary. Gate 16 remains work-ahead rather than a completed gate while Gate 13
is the earliest incomplete prerequisite. Additional canonical seed coverage is
the next independent cloud-safe long-duration stress.


## Recovery 185 canonical multi-seed audit preparation

The seed-1 shipped-data audit above is already verified. The next independent
Gate-16 gap is broader **canonical** seed coverage rather than more synthetic
season stress.

Recovery 185 adds:

`reconstruction/canonical_multiseed_audit.py`

This wrapper delegates each requested seed to the existing
`run_canonical_multiseason_audit` entrypoint and emits one combined evidence
envelope only if every seed completes the requested rollover count. It does not
construct or mutate standings, qualification inputs, competition state, RNG
state or source data itself.

The default bounded seed set is:

- `1`, preserving direct comparability with the already verified canonical
  seed-1 evidence;
- `2`, a nearby independent CRT start;
- `0x12345678`, the nontrivial seed already used in synthetic deterministic
  stress.

The wrapper fails before execution on duplicate/single-seed requests, normalizes
seed values to uint32, aborts on the first failing canonical seed, and rejects a
runner result whose reported seed, rollover count or snapshot count does not
match the request. A partial batch is therefore never emitted as a passing
combined audit.

On a healthy private execution path the intended command is:

```text
cd reconstruction
python canonical_multiseed_audit.py <game-dir> --rollovers 3
```

The default command runs seeds `1`, `2` and `0x12345678`. Additional seeds can
be supplied with repeated `--player-seed` arguments. The resulting JSON must be
persisted together with exact canonical source receipts before any new Gate-16
canonical-seed claim is made.

This repository change is **preparation only**. Recovery 185 does not claim the
new multi-seed batch has run against the authorized source. Gate 16 remains
work-ahead while Gate 13 is the earliest incomplete validation gate.
