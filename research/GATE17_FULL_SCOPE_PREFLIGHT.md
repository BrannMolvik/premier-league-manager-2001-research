# Gate 17 full-scope implementation preflight

_Status: prepared dependent work-ahead behind the playable-country allocation preview._

## Purpose

Gate 17 now has independent, source-backed measurements for two different
release blockers:

1. whether every original TeamSelect League/club can reach the human-control
   backend;
2. whether every playable-country LeagueAllocation endpoint has an exact live
   ranking and can be previewed through the recovered generic exchange executor.

This checkpoint joins those measurements without creating capability.

## Contract

`build_full_scope_preflight()` accepts exactly:

- `HumanScopeCapabilityAudit`;
- `AllocationRankingCapabilityAudit`;
- an optional `PlayableAllocationPreview`.

All supplied objects must target the same canonical TeamSelect catalog SHA-256.

If an allocation preview is supplied, it must:

- retain the exact same ranking-capability audit;
- cover exactly the same assigned allocation set.

The preflight records:

- catalog SHA-256;
- number of TeamSelect scope entries;
- supported and unsupported scope IDs;
- unresolved allocation IDs;
- unresolved ranking endpoint IDs;
- previewed allocation IDs;
- explicit blocker codes.

## Blocker codes

The current fail-closed blockers are:

- `human_scope_incomplete`;
- `progression_rankings_incomplete`;
- `allocation_preview_missing`.

`ready_for_full_runtime_validation=true` is possible only when none of those
blockers remain.

This flag means only that repository-side implementation capability has reached
the point where full runtime validation is meaningful. It is **not** a Gate-17
pass and it is not equivalent to the external Windows 11 release receipt.

## Integrity boundary

The preflight rejects:

- mismatched catalog fingerprints;
- a preview built from a different ranking audit;
- a preview that omits or adds assigned allocation IDs;
- an empty human-scope audit;
- non-exact audit object types.

It does not reinterpret incomplete audits as partial success.

## Remaining release boundary

Even a completely green preflight still requires:

1. the shared runtime to actually expose every cataloged human club route;
2. all required annual ranking publishers to run during a real season;
3. atomic live membership installation and annual regeneration;
4. full per-scope Windows 11 validation against the final archive;
5. an external `full_original_scope.json` receipt bound to the exact canonical
   catalog and archive.

This checkpoint is therefore a gatekeeper for later runtime validation, not a
substitute for it.
