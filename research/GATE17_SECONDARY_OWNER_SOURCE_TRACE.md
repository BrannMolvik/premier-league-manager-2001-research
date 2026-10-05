# Gate 17 procedural-secondary runtime-owner source trace

_Status: cloud-safe evidence tooling only. Gate 13 remains the earliest incomplete validation gate._

## Why this trace exists

The source-backed TeamSelect runtime plan classifies root League scopes whose
DBRCompetition schedule-container code is 2 or 3 as
`procedural_secondary`. The clean-room runtime still has no distinct live
secondary League owner, human continuation route, or secondary save/reload
path. Those capabilities must not be fabricated by routing the scopes through
the primary engine.

Existing canonical executable research already proves:

- `League::0x4F3B70` reads DBRCompetition runtime `+0x38` and returns the
  secondary branch only for values 2 or 3;
- `0x4F3B50` selects global schedule container `0x947AF0` for that branch
  and `0x947AD8` for the primary branch;
- global constructor `0x6156C0 -> 0x615700` creates `0x947AF0` with mode
  byte 1;
- new-game setup invokes `0x616620` on primary first and secondary second;
- League/Cup match builders route inserts through `0x4F3B50 -> 0x615950`.

That closes startup ownership and insertion routing. It does **not** prove the
live continuation contract required by Gate 17.

## Tool

`reconstruction/gate17_secondary_owner_source_trace.py` prepares a private,
checksum-gated source report from the canonical executable. It records bounded
inspection windows around the already-qualified selector/container seam,
including:

- `0x4F3B50 / 0x4F3B70` selector neighborhood;
- primary/secondary ScheduleContainer constructors;
- `0x615950` insertion;
- `0x615BE0` final shuffle;
- the existing runtime-traversal lead at `0x615C10`;
- `0x616620` startup build;
- the later-finalization lead at `0x616A70`;
- the new-game primary/secondary callsite neighborhood.

The report also enumerates:

- raw little-endian occurrences of globals `0x947AD8` and `0x947AF0`,
  explicitly labeled as **not proven xrefs**;
- decoded direct CALL candidates to the selected lifecycle functions,
  explicitly labeled as **not lifecycle-semantic proof**.

Private executable bytes and disassembly remain outside Git.

## Fail-closed capability boundary

The report deliberately keeps false:

- live secondary runtime owner recovered;
- ordinary/daily secondary execution binding recovered;
- season continuation recovered;
- human secondary match dispatch recovered;
- secondary save serialization recovered;
- secondary save/reload continuation recovered;
- procedural-secondary TeamSelect scope playable;
- full-scope preflight ready;
- Gate 17 complete.

A future private-source pass must adjudicate the reported candidates and prove
the actual live owner/lifecycle before implementation can promote any of those
flags. Exact mode-1 date-bucket contents and equal-key qsort ordering also
remain separate Gate-15 fidelity questions; this tracer does not infer them.

## Intended use

Run the tracer on a machine that has the authorized original executable and
write its JSON output to a private path outside the repository. Use
`--disassemble` only as an analyst aid; linear decode remains non-semantic
evidence.
