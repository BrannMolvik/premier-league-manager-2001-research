# Gate 17 sporting-objective progression source trace

_Status: cloud-safe private-source preparation only. The current clean-room runtime still connects the season-end sporting objective only through the Premier League completion path._

## Existing source boundary

Repository-backed implementation research already retains these original anchors:

- annual competition transition: `0x4A8628`;
- sporting-objective progression: `0x5E1C00`;
- neighboring sporting-objective branch family: `0x5E0310`;
- competition-classification comparison used by the recovered objective-6 path: `0x5E07E4`;
- competition transition between the two annual progression passes: `0x4F9010`;
- annual objective evaluation caller: `0x426220`;
- year-gated financial/objective evaluation: `0x5E1D90`;
- DBRUser sacking-reason setter: `0x42C6C0`.

The clean-room objective state also preserves the selected objective ID at relative `+0x64`, progression gate at `+0x68`, and progression-state byte at `+0x9C`. Earlier canonical source work proves that `0x5E0310` is a 17-way switch on the selected objective ID and that season finalization invokes the progression path twice: pass 1, then after `0x4F9010`, pass 0.

The existing Premier League slice is intentionally bounded. It reproduces the recovered same-league branches used by current PL objectives and keeps the broader promotion/relegation classification routes deferred.

## Why this remains a Gate-17 blocker

Deterministic non-PL fresh objectives can already materialize for some clubs, but every non-PL TeamSelect League still reports `sporting_objective_progression_missing`.

Opening objective generation and later sporting progression are separate capabilities. A source-backed opening candidate must not be treated as a complete career objective unless the annual transition can update its progression state correctly across the competition outcomes the shipped game supports.

## Private tracer

`reconstruction/gate17_sporting_objective_progression_source_trace.py` prepares a checksum-gated private report over bounded canonical-executable windows around the anchors above and enumerates decoded direct CALL candidates to the progression, classification, evaluation and sacking-state routines.

The CALL records retain the generic
`decoded_direct_call_candidate_not_lifecycle_semantic_proof`
classification. They are discovery aids only.

## Fail-closed boundary

The report preserves as already recovered:

- the exact source anchors above;
- selected-objective ID offset `+0x64`;
- objective progression gate offset `+0x68`;
- progression state offset `+0x9C`;
- the 17-way switch structure and exact annual pass sequence `(1, 0)`;
- the bounded same-Premier-League sporting slice;
- the year-gated annual evaluator.

It deliberately leaves false:

- annual sporting owner/caller chronology;
- complete non-PL sporting-objective branch table;
- promotion/relegation classification semantics;
- non-PL progression-gate update behavior;
- non-PL sporting-objective progression readiness;
- all-playable-scope sporting progression readiness;
- Gate-17 full-scope readiness;
- Gate 17 completion.

## Intended private adjudication

A future private-source pass should first classify the annual owner path from `0x4A8628` into `0x5E1C00`, then recover the branch dispatch rooted around `0x5E0310`, and finally source-close how the competition-classification path around `0x5E07E4` maps promotion, relegation, unchanged class and improved class to the progression gate/state.

No non-PL objective IDs, table thresholds, promotion/relegation result mapping or season-transition behavior may be copied from the PL slice without source equivalence.
