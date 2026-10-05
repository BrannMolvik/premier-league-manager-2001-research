# Gate 17 multi-human private adjudication plan

_Status: stacked cloud-safe successor to the neutral Start/user-list tracer. No multi-human gameplay capability is promoted._

## Purpose

The source-proven TeamSelect boundary is already stronger than the clean-room
runtime: the original can retain up to six selected human clubs and Start
consumes the existing user list. The neutral tracer in
`gate17_multi_human_start_source_trace.py` intentionally stops before claiming
how those users enter gameplay.

`gate17_multi_human_adjudication.py` turns that neutral report into the exact
private-source proof order needed before changing the one-manager runtime.

## Stage 1: ordered Start iteration

The first proof must establish what `0x4C41C0` actually does with the selected
user list:

- whether every selected user is visited;
- the exact list/traversal order;
- how the source-proven six-user count bounds iteration;
- the per-user continuation and selected-club consumption.

Only this proof can justify widening TeamSelect Start and the gameplay manager
capacity beyond one. It does not by itself prove a shared world.

## Stage 2: shared runtime handoff

After Start iteration is known, source must establish:

- whether all selected users enter the same live world/runtime;
- the owner object(s) retaining each user after TeamSelect;
- current-user switching or equivalent ownership semantics;
- whether any part of the original actually creates independent worlds.

The clean-room implementation must not duplicate six independent
`HumanGameplayController` worlds merely because TeamSelect can select six
clubs.

## Stage 3: simultaneous human fixture dispatch

The next proof is intentionally separate from Start:

- trace at least two selected users with due fixtures;
- recover arbitration/order when multiple human fixtures are due;
- recover continuation/current-user transitions after each human match;
- establish whether pending-fixture ownership is global or per-user.

The current controller has one pending human fixture context, so this stage is a
real backend boundary rather than a UI detail.

## Stage 4: multi-human save/reload

Finally, source must recover:

- serialization of the complete selected-user list;
- per-user club/runtime state ownership;
- reload order and current-user restoration;
- pending human fixture/continuation state across reload.

The current internal schema 44 stores one `controller["human"]` object. No
plural schema migration is permitted from the tracer alone.

## Validation rules

The adjudication builder rejects its input if:

- the source-proven hard cap differs from six;
- source-proven user append or Start user-list consumption disappears;
- any currently unresolved trace capability is already true;
- required Start/current/indexed-user/global-count candidate families are absent;
- a decoded CALL candidate loses its explicit
  `decoded_direct_call_candidate_not_lifecycle_semantic_proof` classification.

The resulting plan itself keeps all implementation capability false. It is an
evidence checklist, not a substitute for the private canonical-source pass.

## Gate-17 consequence

The existing `MultiHumanCapabilityAudit` remains red for gameplay capacity,
multi-human Start, shared runtime, and save/reload. The full-scope preflight
continues to emit `multi_human_capability_incomplete` until real implementation
and validation satisfy the source-proven six-user requirement.

Gate 17 remains incomplete.
