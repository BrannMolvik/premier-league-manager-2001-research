# Gate 17 human-control scope capability audit

_Status: independent Gate-17 work-ahead while Gate 13 shared runtime remains Codex-owned._

## Purpose

The source-backed TeamSelect catalog now defines the exact originally selectable
country, League and club rows. The current human gameplay controller still gates
club selection against `state.premier_league.club_ids`.

This checkpoint makes that release blocker machine-readable without widening
the gameplay backend.

## Implementation

`gate17_human_scope_capability.py` compares an
`OriginalPlayableScope` with the exact club IDs a human-selection backend
currently accepts.

For every canonical country/League entry it records:

- stable scope ID `<country_id>:<competition_id>`;
- exact selectable club IDs from TeamSelect;
- the subset accepted by the backend;
- the unsupported club IDs;
- whether the complete League target is human-selectable.

The aggregate audit records:

- canonical catalog SHA-256;
- the backend selectable-club set;
- the full catalog selectable-club set;
- backend club IDs outside the TeamSelect catalog;
- exact supported and unsupported scope IDs;
- `complete=true` only when every cataloged League has every selectable club
  available to the human selection surface.

Extra backend clubs never widen the canonical release scope.

## Canonical runner

`run_canonical_human_scope_capability(game_dir)`:

1. derives the catalog from the hash-verified canonical source directory;
2. constructs the same canonical `HumanGameplayController` used by the existing
   human-gameplay audit, with deterministic seeds;
3. reads the exact current `premier_league.club_ids` selection set;
4. compares that set against every TeamSelect catalog entry.

The CLI exits 0 only for complete coverage and 2 when the audit validly proves
remaining unsupported scope.

## Fidelity boundary

This audit does not modify `HumanGameplayController`, `GameState`, front-end
selection, competition simulation, save/load, or any Gate-13-owned shared file.

It therefore cannot make Gate 17 pass by itself. Its purpose is to provide the
exact before/after measurement for the later shared-runtime generalization once
Gate 13 releases the ownership lock.
