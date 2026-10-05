# Gate 17 multi-human Start/user-list source trace

_Status: cloud-safe evidence tooling only. Gate 13 remains the earliest incomplete validation gate._

## Existing source facts

The canonical TeamSelect selection trace already proves that the original is
not single-manager-only:

- selecting a club reaches `0x413BB0`, creates a user, binds the clicked club,
  appends the user to the global user list, and increments the user count;
- user `+0x5B4` stores the selected club pointer;
- TeamSelect Start event `0x4DA480` calls `0x4C41C0` and operates on the
  already-created global user list rather than reconstructing a club identity
  from the private TeamSelect rollback record;
- Start-side continuation resolves users through `0x4139D0/0x413B10`;
- saturation helper `0x4DA4D0` includes global user count
  `0x8755E4 >= 6`, making six the source-proven hard simultaneous-user cap,
  subject to the tighter original manager-availability condition.

These are canonical source results. They do not yet prove how all selected
users are ordered into gameplay, how multiple human fixtures are scheduled, or
how multi-user state is serialized.

## Private tracer

`reconstruction/gate17_multi_human_start_source_trace.py` prepares a bounded,
checksum-gated private report from the canonical executable. It records source
windows around:

- TeamSelect selection `0x4D8E90`;
- Start event `0x4DA480`;
- Start continuation `0x4C41C0`;
- saturation `0x4DA4D0`;
- current/indexed user resolvers `0x4139D0/0x413B10`;
- user append/create `0x413BB0`;
- user removal `0x413B80`.

It also enumerates raw little-endian occurrences of global user-count address
`0x8755E4` and decoded direct CALL candidates to the Start/user-list helper
family. These are explicitly candidate records, not xref or handoff-semantic
proof.

Private executable bytes and disassembly remain outside Git.

## Fail-closed boundary

The report carries the already-proven six-user TeamSelect contract, while
keeping all of the following false:

- ordered multi-user Start iteration recovered;
- shared multi-human runtime ownership recovered;
- simultaneous human-fixture dispatch order recovered;
- multi-human save serialization recovered;
- multi-human save/reload continuation recovered;
- multi-human gameplay supported;
- full-scope preflight ready;
- Gate 17 complete.

The current clean-room capability audit therefore remains correct: TeamSelect
can retain six selections, but gameplay, Start handoff, shared runtime and
save/reload are still single-human/incomplete.

## Next private-source adjudication

The next source pass should inspect the candidate Start and user-resolver
callers with four separate questions:

1. Does `0x4C41C0` iterate every selected user, and in what exact list/order?
2. Does Start hand all users into one shared live world/runtime, or are there
   additional ownership objects that must be reconstructed?
3. When two or more selected users have due fixtures, what source owner and
   ordering rule controls human-match dispatch and continuation?
4. Which save/load paths serialize the full user list and per-user club/runtime
   state, and how are all users restored on reload?

No implementation flag should be promoted until those questions are answered
from source or equivalent executable evidence. In particular, the existing
primary single-human controller must not simply be duplicated six times without
proof of shared-runtime semantics.
