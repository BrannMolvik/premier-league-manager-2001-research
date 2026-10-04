# Gate 17 save-scope capability audit

_Status: independent cloud-safe work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Purpose

Gate 17 requires save/reload to work across every originally selectable
TeamSelect country/League route. Runtime ownership alone cannot prove that
criterion. A newly materialized League owner could still be absent from the
internal save schema or fail to continue correctly after reload.

`reconstruction/gate17_save_scope_capability.py` therefore records save/reload
implementation capability independently from runtime-owner capability.

## Source-backed scope partition

The audit consumes the exact `PlayableLeagueRuntimePlan` derived from the
canonical TeamSelect catalog and recovered schedule-container ownership. It
keeps the three owner classes distinct:

- fixed primary;
- procedural primary;
- procedural secondary.

A scope counts as save/reload-capable only when its exact
`<country_id>:<competition_id>` identity appears in the capability set for its
own runtime-owner class. Putting a secondary scope in the primary capability
set does not satisfy it.

## Current canonical boundary

The current repository has dedicated continuation tooling for:

- the fixed Premier League mid-matchday internal save/reload route;
- every procedural-primary TeamSelect League through the all-primary sweep.

The current repository does **not** have a procedural-secondary live runtime
container, secondary serialization path, or post-load human continuation route.
The canonical capability runner therefore marks every fixed-primary and
procedural-primary scope supported and every procedural-secondary scope blocked
with `save_reload_capability_missing`.

This is implementation/tooling readiness only. It does not claim that the
authorized private primary-container sweep has been executed, and it does not
replace the final Windows 11 per-scope save/reload receipt.

## Full-scope preflight integration

The full-scope implementation preflight now requires an exact
`SaveScopeCapabilityAudit` bound to the same canonical catalog and exact scope
order as the human-selection and runtime-owner audits.

A repository-side preflight remains blocked on
`save_scope_capability_incomplete` until every cataloged TeamSelect scope has
an owner-correct internal save/reload continuation capability. Detailed blocked
scope IDs and low-level save blocker codes are retained in the preflight output.

This prevents future secondary runtime work from accidentally making the
full-scope implementation preflight green before persistence support exists.

## Non-claim

No secondary runtime semantics are inferred here. The audit does not alias
secondary owners into the primary engine, fabricate a save schema, or promote
hosted tests into private/Windows continuation evidence.
