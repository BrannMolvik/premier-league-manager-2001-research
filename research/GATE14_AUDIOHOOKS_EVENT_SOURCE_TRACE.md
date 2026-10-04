# Gate 14 AudioHooks caller source trace

_Status: cloud-safe trace tooling only. Gate 13 remains Codex-owned._

## Purpose

The original dispatcher at `AudioHooks::0x5DBFC0` is already source-closed as
a numeric switch over event IDs 2 through 35, including its exact conditional
routing to `menus.bnk` sample slots. What remains unresolved is the native
sender side: which original callers construct each numeric event ID and state
value.

Decoded audio is not evidence for event meaning. Human-readable sound names
must not be inferred by listening to samples.

## Trace tool

`reconstruction/gate14_audiohooks_event_source_trace.py` accepts only an
`OriginalPE32` source and scans the PE `.text` section for decoded direct
`CALL` candidates whose target equals the already recovered dispatcher VA
`0x5DBFC0`.

For every candidate it records:

- the direct-call instruction VA;
- a bounded linear instruction context;
- nearby `PUSH` operands in reverse proximity to the call;
- immediate values or register identities where Capstone decodes them.

The report intentionally does not call those pushes arguments. A nearby push
can belong to unrelated code, and even a valid direct call does not by itself
prove the caller is reachable in the relevant gameplay path.

## Fail-closed evidence boundary

The generated private report keeps all of these false:

- direct-caller CFG recovery;
- calling-convention recovery;
- event-argument position;
- state-argument position;
- semantic event binding;
- sample meaning.

Every candidate is labeled
`decoded_direct_audiohooks_call_candidate_not_cfg_or_semantic_proof`.

## Exact private follow-up

On the next healthy private canonical-executable path:

1. run the new tracer against the independently verified original executable;
2. manually adjudicate each direct-call candidate against function boundaries
   and reachable control flow;
3. prove the dispatcher calling convention and exact event/state argument
   positions from source;
4. trace literal or data-derived event IDs backward to their native senders;
5. promote only event bindings that are directly supported by that source
   data-flow.

Until those steps are complete,
`semantic_event_binding_recovered` remains false.

No proprietary executable bytes, disassembly output, BNK bytes, or decoded PCM
belong in Git.
