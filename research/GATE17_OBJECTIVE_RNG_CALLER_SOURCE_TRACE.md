# Gate 17 fresh-objective RNG caller source trace

_Status: cloud-safe private-source preparation only. The fresh objective branch table is already source-closed; RNG-bearing non-PL branches remain blocked._

## Existing source facts

The authorized canonical executable already closes the fresh-state
`0x5DFD30` candidate table for objective state `+0x9C == 0`.

Normal setup `0x5DF670` requests three candidate slots. The only random
families are:

- first hierarchy class plus high-half fan rank, where slot 1 selects objective
  2 or 15;
- any non-first hierarchy class with one or more promotion-playoff status-2
  positions, where slot 1 or 2 selects objective 5 or 8.

Both use shared CRT helper `0x64D540(100)`. The lower-numbered branch is
selected for return values `<= 50`, preserving the exact inclusive 51/49
split.

Every other fresh branch is deterministic and is already eligible for
clean-room materialization through a sentinel RNG that raises if an unexpected
draw occurs.

## Remaining source boundary

DBRUser construction `0x425680` initializes fresh objective state, but it does
not by itself prove the shared CRT state later observed at `0x5DF670`.

The missing evidence is therefore not the objective branch table. It is:

1. which ordinary owner/caller path reaches `0x5DF670` for each fresh user;
2. the exact process-global CRT state at that entry;
3. the precise draw chronology when one of the three `0x5DFD30` calls takes
   an RNG-bearing branch;
4. how that state is connected to the already-recovered shared startup RNG
   ledger rather than reseeded or inferred.

Until those items are recovered, the clean-room runtime must continue refusing
RNG-bearing non-PL fresh-objective branches.

## Private tracer

`reconstruction/gate17_objective_rng_caller_source_trace.py` prepares a
checksum-gated private report over bounded windows around:

- DBRUser constructor `0x425680`;
- objective setup `0x5DF670`;
- candidate generator `0x5DFD30`;
- shared CRT bounded RNG `0x64D540`;
- hierarchy helpers `0x4FA520/0x4FA570/0x4FA590`;
- promotion-playoff status helper `0x4F88C0`.

It also enumerates decoded direct CALL candidates to those helpers. Those
records retain the existing
`decoded_direct_call_candidate_not_lifecycle_semantic_proof`
classification and are not treated as objective-setup chronology or CRT-state
proof.

Private executable bytes and disassembly remain outside Git.

## Fail-closed report

The tracer carries the already source-closed constants:

- RNG bound 100;
- inclusive lower threshold 50;
- three setup slots;
- fresh branch table recovered;
- deterministic non-PL branches materializable;
- RNG-bearing branches require shared CRT state.

It deliberately leaves false:

- objective-setup callers classified;
- objective-setup entry CRT state recovered;
- RNG-bearing branch draw position recovered;
- fresh objective RNG replay ready;
- all-playable-scope fresh objectives ready;
- full-scope preflight ready;
- Gate 17 complete.

## Next private-source adjudication

The next private pass should begin from decoded callers of `0x5DF670`, prove
the ordinary user/setup owner, and walk backward far enough to attach its entry
state to the existing shared startup CRT ledger. Only after that owner/state
chain is exact should the clean-room runtime consume the actual next
`MsvcCrtRng` draw for an RNG-bearing objective branch.

No fixed seed, per-club reseed, guessed draw index, or unrelated match-engine RNG
may be substituted.
