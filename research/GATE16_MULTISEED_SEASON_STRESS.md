# Gate 16 multi-seed autonomous season stress

_Date: 1 October 2026 KST_

## Scope

This is cloud-safe Gate-16 work-ahead while Gate 13 remains the earliest
incomplete validation gate. It complements, but does not replace, the earlier
canonical Gate-6 evidence for three deterministic full Premier League seasons.

The regression in reconstruction/test_gate16_multiseed_season_stress.py uses the
existing 20-club / 380-fixture synthetic full-season database and runs complete
autonomous seasons for six deliberately varied 32-bit CRT seeds:

- 0x00000001
- 0x00000002
- 0x12345678
- 0x80000000
- 0xDEADBEEF
- 0xFFFFFFFF

The 0x12345678 season is then run a second time and must reproduce the exact
season digest and final RNG state.

## Invariants per season

Every stress season must:

- finish all 380 fixtures within 366 day advances;
- leave exactly 20 league rows with 38 matches each;
- reconcile played totals, goals for/against and wins/losses;
- keep Condition in 0..100 and Form in 0..4;
- keep suspension counts non-negative;
- give every injured player a return date;
- preserve club roster ownership;
- leave final active/substitute selections disjoint at 11 + 5 for all clubs.

The deterministic digest includes every stored score, the final league table and
the persisted per-player condition/form/injury/suspension state.

## Evidence boundary

This is deliberately **synthetic stress evidence**. It is valuable because it
runs thousands of reconstructed matches in ordinary hosted CI across awkward
RNG seeds, but it does not supersede canonical-data audits and it is not yet the
Gate-16 requirement for consecutive multi-season calendar play through annual
qualification/regeneration.

Combined with the separate 30-rollover destructive regeneration soak, this
closes two useful work-ahead risks:

1. repeated season replacement does not retain stale primary runtime state;
2. complete autonomous seasons survive several distinct deterministic seeds.

Still open for Gate 16 are consecutive played seasons in one live world,
broader competitions/transfers/save-load under long-duration stress, more seed
coverage, and regression work for any failures discovered.
