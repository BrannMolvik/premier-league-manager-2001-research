# Live captured-report inputs

_3 October 2026 KST. Gate 13 remains OPEN._

Canonical main was reconciled at `9019be2a1efa05e215a63464ea7d86e7a612d9b1`.
PR #183 is already merged; this is a separate continuation branch. The
parallel Gate-14 worker and `agent-runtime` ownership are unchanged. The
full-original-functionality port invariant in ROADMAP is preserved.

## Actual integration, not another codec trace

The existing canonical executable and private reports were reused after
verifying executable SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
No archive/executable/raw report was imported into Git.

`finalize_match_participant_statistics` retains the existing live performance
finalizer's output in complete side-local order. It does not calculate ratings
a second time. The prior `persist_match_performance_history` API remains a
compatibility wrapper returning only appeared ratings, with unchanged RNG
ordering. The non-appeared zero is the explicit native write at `0x630C4B`,
not a missing-value default. All participants retain the already recovered
eight skill flags. Input order and skills are validated before RNG/history
mutation. This does not add the separate FastView trajectory or its RNG work.

Both Premier League AI and human completion paths retain immutable side
outputs plus the actual ordered persistent player IDs in
`GameState.prepared_match_participant_statistics`. No distinct MatchEngine RNG
means no statistics entry, not invented ratings or an aliased CRT stream.
Annual primary regeneration clears the transient map. It is not the captured
report owner and is deliberately excluded from save until the full producer
exists.

`simulate_normal_match` now retains captured possession from its actual
normalized calculator rows at completion. Ordinary rows correspond exactly to
native array indices 1..8 and 10..17; extra-time rows add 19..20 and 22..23.
The existing two/four-group aggregation is shared with the native snapshot
codec. No boundary rows, synthetic calculator memory or score context are
manufactured. Missing, duplicate, reordered or partial rows reject.

Internal save schema **35** explicitly preserves that possession output for
the semantic results it already saves (pending prior matchday results).
Save/load checks it against the complete retained rows. Null stays null; even
complete rows do not authorize reconstructing a missing capture input. This is
not persistence of all finished Premier League reports. Existing schema-34
saves are rejected by the strict version gate; no migration is claimed.

## Verification boundary

Regression coverage includes actual calculation -> mid-matchday save/reload ->
equal possession output -> absent report context. This is deliberately NOT the
requested successful PMatchInfo route. The bridge still ignores these input
fragments and requires complete report ownership/link state.

## Single remaining blocker

Complete live native report production and persistence are still absent.
Next: retain the full source-ordered compact-event list at its live producer,
including native finalization/boundary payloads, and the remaining calculator /
post-match helper outputs (caption/identity/scalars and participant/goal
metadata). Then assemble the complete report, append it to the GameState owner
only after successful capture, save/load that ordered owner and fixture link,
and verify a genuine calculated fixture -> reload -> native right-click ->
correct PMatchInfo context. Do not substitute semantic score/completion or
zero-filled snapshots. Final normal-play/timing closure remains pending that
successful route.
