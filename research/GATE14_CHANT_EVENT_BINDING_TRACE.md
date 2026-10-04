# Gate 14 chant enqueue caller source trace

_Status: disjoint Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The chant runtime is source-backed through bank loading, pool construction,
shuffle, timing and runtime pool selection. The unresolved bridge is the caller
that requests chant enqueue and supplies selector state in the live match path.

`gate14_chant_event_binding_source_trace.py` narrows that bridge without
assigning event semantics.

## Candidate boundary

The source-qualified enqueue entry is:

`0x723360`

The tracer reuses the repository's existing Capstone direct-edge scanner and
retains only linear-decoded direct **CALL** candidates whose immediate target is
the enqueue entry. Direct jumps are ignored.

For each retained call candidate the private mode can save a small bounded
caller context window for later manual CFG/data-flow adjudication. Those
instruction bytes remain private and outside Git.

## Fail-closed state

The report keeps all of the following false:

- caller CFG recovered;
- match-event binding recovered;
- selector-to-event meaning recovered;
- chant meaning recovered;
- audio ready.

A direct call candidate is not evidence that the caller executes on a match
event, which selector it supplies, or which audible chant ultimately plays.

## Next private step

On a healthy private execution path, run the caller trace against the canonical
executable and manually inspect only the returned call neighborhoods. Follow
the selector value and owning callback/receiver far enough to establish an
event identity before adding any clean-runtime event-to-chant routing.
