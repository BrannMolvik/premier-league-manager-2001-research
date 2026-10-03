# Live captured-report inputs

_3 October 2026 KST. Gate 13 remains OPEN._

## PR #194 continuation: executable compact-stream milestone

`native_compact_match.py` now implements the ordinary complete-boundary path
of `0x62F7C0 -> 0x62FBF0`: last-eligible pruning at eight/twelve, protected
minutes/cutoff, unsigned spacing, incident/substitution time coupling,
immediate-predecessor boundary clamp and signed stable list ordering. The
backwards boundary loop does not write earlier record minutes; no invented
backward cascade is applied. Malformed missing-boundary native fallback paths
remain unsupported rather than synthesizing a list.

Live Premier League calculation now retains constructor-written compact fields
and FullTime's explicit outcome. `0x510E55/5E/64` initializes previous scores
to `-1/-1`; `0x511120` replaces them only for match family 5 (two legs).
FullTime uses the live accumulator and those setup inputs before the fixture
result is persisted. Other calculation callers without explicit native setup
inputs do not receive a fabricated stream. The sparse field representation
does not allocate fake zero-filled 0x38-byte snapshots. Encoding shares the
existing native packer and rejects any missing consumed field.

Constructor argument inspection found and fixed two omissions in the live
open-play semantic producer: shooting misses retain the carrier as secondary
at `0x62CD0F`; own-goal calls `0x62CAFF/0x62CCC7` retain the selected finisher
as secondary, not the carrier. The second participant lookup owns native +4,
as proven by `0x62ECF0/0x62EE20/0x62EEA0`. No RNG draw or scoring algorithm
was added for these argument-retention corrections.

Internal schema **36** retains finalized compact order, explicit fields and
FullTime payload alongside existing pending matchday calculation results.
Null remains null; missing required keys, partial payloads and unsorted streams
reject. Old schema 35 is rejected by the existing strict version gate.
Five genuinely calculated pending fixtures now retain complete consumed script
fields and survive save/reload with byte-identical packed scripts. This is NOT
the successful PMatchInfo milestone: report helper/scalar/participant metadata,
complete report assembly, ordered GameState report owner and fixture links
remain absent, so the existing right-click bridge continues to return None.

Focused calculation/capture/save regressions: **135 passed**. No full-suite,
Windows schema-8, broad closure audit or Gate-14 work was repeated for this
intermediate milestone. The exact next task remains complete completion-time
report assembly/ownership/persistence using the actual retained producer
outputs; never promote this script alone to a captured report.

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

### Newly resolved live compact-list prerequisite

The live-producer tool inspects only the new constructor/phase/finalization
windows, not the previously recovered eligibility, routing or packers. A new
private checksum-gated report is generated by
`gate13_live_report_producer_trace.py` outside Git.

- `0x62FBC0` finishes calculation, calls `0x62F7C0(head, 0)` and replaces
  the head. Copying the unfinalized semantic list is not a native script.
- The finalizer counts chance-family records until type 9. Above eight it
  repeatedly removes the last eligible exact-outcome-1 record with family
  below 4; above twelve it similarly removes eligible non-goals. Time 0,
  time 130 and records at/before the supplied cutoff are protected. No
  eligible candidate means no forced arbitrary truncation.
- It spaces applicable type-0..5 records using calculator `+0x1150`, couples
  a type-5 incident's following type-10 substitution time, then invokes
  `0x62FBF0` for boundary-adjacent time correction and stable chronological
  linked-list ordering. Existing kind-6/7 boundaries are retained; fallback
  insertion is a separate path, not permission to invent missing live input.
- Native FullTime construction `0x632660` writes an additional outcome
  dword at `+0x24`, supplied by `0x62AE00`. That getter includes aggregate
  tie/away-goal/penalty comparison fields, not just the display score. The
  semantic `BoundaryRecord(FULL_TIME)` alone does not retain this input.
- Phase routine `0x62AE90` normalizes the initial and mid-half boundary
  rows through `0x62B3F0`, in addition to the ordinary rows. These excluded
  possession-average rows still affect native RNG/player-history production.
  Do not synthesize them afterwards from the sixteen visible segment rows.
- `0x62B6D0` is a post-row RNG/status update over `+0x112C/+0x112D`; this
  window does **not** prove a type-13 compact-record producer. Its fields
  retain neutral labels pending their owner semantics.

Exact next producer action is now **retain the complete live compact fields
including FullTime outcome and preserve the native pre-capture list finalizer**,
not simply encode current semantic events. The separate Gate-14 worker's new
PlayerProxy history-lifecycle main `d0dadf1f` was merged without modification.
No complete report/context claim was added on the strength of this trace.

## Checkpoint validation

Final reconciled code `f8b9f4baf5d73d5a291065b1e200a94d408c5968` passed
**1,625 full reconstruction tests with 23 expected skips** (220.137 seconds),
including the preserved Gate-14 history-lifecycle main `d0dadf1f` and new
private-producer-tool contracts. Reconciled focused suite: **134 passed**.
The private live-producer report SHA-256 is
`9bc32884b549bf8f1772f288b45dd6bf04836802dbd2db3dd47ffaf59060c6de`.
Fresh Windows schema-8 receipt SHA-256 is
`131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aa7aae2e8cc9`.
The native interaction/presentation path was unchanged by the subsequent
producer-tool additions. Runtime report producer/owner/save remains incomplete,
ordinary successful PMatchInfo opening remains false, and Gate 13 remains open.

Code `9f5ce577` passed **1,614 full reconstruction tests with 23 expected skips**
(241.851 seconds), using the existing private Capstone runtime. The first run
without that import path failed one optional-disassembly dependency test; it
is not the passing run. Focused calculation/capture/save/route tests passed
115 checks before the final identity-container regression was added.

A fresh real-Windows schema-8 graphical receipt passed at
`work/gate13-live-inputs-schema8-20261003.json` outside Git. Successful ordinary
captured-report opening remains explicitly false. The initial audit invocation
used an incomplete old font staging root; the passing run used a fresh private
root assembled from existing checksum-gated authorized assets. Asset policy
and diff-whitespace checks passed. Frozen-package smoke remains subject to the
previously documented Windows Application Control block; no bypass was tried.
