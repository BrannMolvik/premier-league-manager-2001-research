# Gate 17 full-scope implementation preflight

_Status: prepared cloud-safe work-ahead while Gate 13 remains the earliest open validation gate._

## Purpose

Gate 17 now has three independent source-backed/read-only measurements that
must agree before full-scope runtime validation is meaningful:

1. whether every original TeamSelect League/club can reach the human-control
   selection backend;
2. whether each TeamSelect League's required fixed-primary,
   procedural-primary, or procedural-secondary runtime owner is actually
   materialized, human-playable, and connected to annual progression;
3. whether a completed runtime state exposes every playable-country
   LeagueAllocation ranking endpoint and can preview all source-backed
   membership exchanges without mutation.

This checkpoint joins those measurements without creating capability.

## Contract

`build_full_scope_preflight()` accepts exactly:

- `HumanScopeCapabilityAudit`;
- `RuntimeOwnerCapabilityAudit`;
- `RuntimeProgressionAudit`.

All three must target the same canonical TeamSelect catalog SHA-256. The
runtime-owner audit must contain the same scope IDs in the same order as the
human-scope audit. The progression audit must internally bind its
ranking-capability audit and optional allocation preview to that same catalog.

The preflight records:

- catalog SHA-256 and TeamSelect scope-entry count;
- supported and unsupported human-selection scope IDs;
- supported and blocked runtime-owner scope IDs;
- exact runtime-owner blocker codes;
- whether the live progression audit is complete;
- unresolved allocation and ranking endpoint IDs;
- previewed allocation IDs;
- the runtime-membership immutability result;
- high-level preflight blocker codes.

## Blocker codes

Current high-level fail-closed blockers are:

- `human_scope_incomplete`;
- `runtime_owner_capability_incomplete`;
- `progression_rankings_incomplete`;
- `allocation_preview_missing`;
- `runtime_membership_mutation`;
- `runtime_progression_incomplete` for any otherwise-unclassified incomplete
  progression result.

The runtime-owner audit separately preserves its exact underlying blockers,
including unavailable human selection, missing runtime materialization, missing
human match dispatch, missing source-backed fresh financial/chairman-objective
setup, and missing annual progression country coverage.

`ready_for_full_runtime_validation=true` means only that repository-side
capability has reached the point where full runtime validation is meaningful.
It is not a Gate 17 pass and does not replace the external Windows 11 release
receipt.

## Integrity boundary

The preflight rejects mismatched catalog fingerprints, mismatched TeamSelect
scope identities, a preview built from a different ranking audit, a preview
that changes the membership key set, and non-exact audit object types. It does
not reinterpret incomplete audits as partial success.

## Remaining release boundary

Even a green preflight still requires the shared runtime to expose every
cataloged human club route, all required primary and secondary runtime owners,
real-season publication of all required ranking endpoints, atomic live
membership installation and annual regeneration, full per-scope Windows 11
validation against the final archive, and a `full_original_scope.json`
receipt bound to the exact canonical catalog and release archive.

Gate 13 remains the earliest incomplete gate. This work is independent Gate 17
readiness infrastructure only and must not be used to bypass Gate 13 or declare
a later gate complete early.
