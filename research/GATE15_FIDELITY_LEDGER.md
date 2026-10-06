# Gate 15 fidelity acceptance ledger

_Status: fail-closed work-ahead infrastructure. Gate 15 is not complete._

## Purpose

Gate 15 has two roadmap requirements:

1. every known fidelity deviation must be fixed, proven irrelevant, or
   explicitly accepted/documented; and
2. no deterministic fallback may be described as original behavior without
   evidence.

The authoritative list of live deviations is the **Active gaps** table in
`research/FIDELITY_GAPS.md`. A prose readiness audit alone can become stale if
that table changes. The schema-1
`research/GATE15_FIDELITY_ACCEPTANCE_LEDGER.json` and
`reconstruction/gate15_fidelity_ledger.py` therefore make coverage
machine-checkable.

## Current checkpoint

The live fidelity table currently contains exactly **12** rows:

- ten Gate-15-owned or Gate-15-deferred items; and
- two Gate-14-owned prerequisites:
  `External Windows front-end/management playability regression (#482)` and
  `FastView/3D and original audio/match presentation`.

The schema-1 JSON already contains all 12 exact names/planned-gate cells, and
the canonical unit test asserts both prerequisite rows. Recovery 369 adds a
documentation-count regression so this prose cannot silently drift from the
machine-parsed Active gaps table again.

The ledger has one exact entry for each row, including the exact **Planned
gate** cell from the source table. It deliberately declares
`gate15_declared_complete=false`.

Current Gate-15 statuses are only pre-release classifications:

- `pending_source_or_acceptance`: source closure remains preferable, but a
  final explicit documented limitation may be possible if the roadmap/release
  policy permits it;
- `pending_final_acceptance`: the bounded behavior is already explicit, but
  final Gate-15 adjudication and release wording have not happened;
- `prerequisite_gate_14`: this row belongs to Gate 14 and cannot be accepted
  away by Gate 15.

None of those statuses passes Gate 15.

## Final statuses

Only these statuses are terminal for a Gate-15-owned live row:

- `fixed`;
- `proven_irrelevant`;
- `accepted_documented`.

An `accepted_documented` item must carry
`release_limitation_required_if_accepted=true`; otherwise the audit rejects
it. A fallback marked `fallback_described_as_original=true` is always rejected.

## Gate 13/14 boundary

Two current rows are owned by Gate 14 for ledger purposes: the externally
observed Windows front-end/management regression (#482), which reopened Gate 13
and crosses into startup/match-presentation acceptance, and the broader
FastView/3D/audio presentation row. While either remains live, each must stay
`status=prerequisite_gate_14`, and `gate15_ready` remains false.

Gate 15 may not document either row away as an accepted limitation. After the
earlier Gate-13 acceptance regression is externally cleared and Gate 14 actually
closes, completed prerequisite rows must be removed from the live Active gaps
table (or moved to resolved/superseded history) before final Gate-15 closure.

## Coverage contract

The audit compares the Markdown table with the JSON ledger and reports:

- active-gap count;
- ledger-entry count;
- active rows missing from the ledger;
- unexpected ledger entries;
- exact planned-gate mismatches;
- status counts;
- remaining Gate-14 prerequisite rows;
- whether every fallback claim stays fail-closed;
- whether all Gate-15-owned rows have terminal statuses;
- whether Gate 14 is complete; and
- final `gate15_ready`.

A declared completion is rejected unless the full audit is already ready.

This means adding, renaming, removing, or reassigning an active fidelity row
requires an intentional matching ledger change. The final Gate-15 audit cannot
silently omit a known deviation.

## Current execution boundary

Recovery 369 again resolved and materialized the authorized private
511,121,336-byte FM2001 source archive, but current container and Python
execution routes still fail with `caas.internal.errors.ClientError`, including
trivial process probes. Source-dependent rows therefore remain pending rather
than being inferred from nearby code or analogy.

This ledger does not decide that a source-dependent difference is acceptable.
It only prevents the difference from disappearing from the final audit while
that evidence is unavailable.

## Closure procedure

After Gate 14 closes:

1. refresh `research/FIDELITY_GAPS.md`;
2. update this ledger one-for-one;
3. source-close every practical pending item;
4. give every remaining Gate-15-owned active row exactly one terminal status;
5. carry each `accepted_documented` item into the final release limitations;
6. verify no deterministic fallback is described as original;
7. set `gate15_declared_complete=true` only when the machine audit is ready;
8. rerun the full reconstruction suite and repository asset policy; and
9. only then audit and mark Gate 15 complete in `ROADMAP.md`.

The ledger is an omission guard, not a shortcut around source evidence or
release-scope requirements.
