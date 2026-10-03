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

The same continuation now retains `0x631110`'s selected-player ID at actual
AI/human statistics completion when the distinct RNG is supplied: higher
rating wins, equal rating uses strictly higher populated `0x41FB60` recent
history average, equal ties retain side-0/side-local precedence, and all-zero
ratings retain the constructor's `-1`. This transient input is season-cleared
and deliberately not saved as a partial report. `0x41E3F0` was checked: it
delegates to `0x41E3D0` with the team's persistent ID, i.e. the shirt-number
accessor, not a position accessor. Participant capture still needs its native
history/flag metadata before any complete report can be assembled.

Live statistics pack without synthetic participant memory or unused 28-byte
tail padding. Goal capture uses finalized +4/+8/+0/+20 fields verbatim, stops
at kind 9, and does not derive destination/player/minute from persisted scores.
Combined focused chain: **179 passed**. The expanded private producer report
is `work/gate13-finalized-compact-producer-20261003.json`, SHA-256
`453347464fea34e123f24d718370ad7137c59f3d475e57760fa6322b17f3fe79`.
No proprietary bytes or generated disassembly were committed.

Milestone validation: **1,644 full reconstruction tests, 23 expected skips,
228.868 seconds, OK**; final targeted assertions **80 passed**. Asset policy,
JSON syntax and diff-whitespace checks pass. Latest `origin/main` remains
`d0dadf1fbe5088959bf611b360884f414e61590b`. No Windows run was repeated because
the report-opening/presentation path has not become executable; the earlier
receipt is historical, not validation of a completed new report route.
Verified runtime/tool code is checkpointed at
`bd7be42330e43879df2701a120f31fe773618e6a`; subsequent changes only reconcile
documentation/validation identities.

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
The compact list/finalization, FullTime, participant statistics, selected-player
and goal helpers are already recovered; do not retrace them. Next: retain the
missing mandatory native setup metadata, adjusted initial participant-history
flags and caption/context inputs at their actual producers. Then assemble the
complete report, append it to the GameState owner
only after successful capture, save/load that ordered owner and fixture link,
and verify a genuine calculated fixture -> reload -> native right-click ->
correct PMatchInfo context. Do not substitute semantic score/completion or
zero-filled snapshots. Final normal-play/timing closure remains pending that
successful route.

### Metadata continuation from cfab7abc (not a closure audit)

- `0x632550 -> 0x64CCD0` supplies calendar year-offset-from-1900, month and
  day. Its first four years are non-leap, then it uses 1461-day cycles, not
  Gregorian century rules. The live calculator now retains this tuple together
  with its actual D4C/D50 accumulators. `0x60BA80` copies their low nibbles;
  retained values are not reconstructed from `NormalMatchResult.score`, saved
  completion or finalized/pruned goal records. Pending-result schema 37 saves
  explicit values; null remains null and missing/malformed input rejects.
- `0x64C7BF`, the last of the verified 2,714 language assignments, binds
  `0x981D94` to English IDX 2713 / STR 21855: `%C %D{%D %M %Yf}`.
  `0x5146B0` resolves `%C` through the native match context's `+0x4C/+0x14`
  label and dispatches `%D` to `0x64D150`. This particular date format writes
  decimal day, the first three bytes of the original month string and four
  year digits. Month globals `0x984604..0x9845D8` bind IDX 125..136.
  `0x60B29F` serializes 64 caption bytes. The runtime must retain the actual
  context label; this evidence is not permission to guess one from a score.
- `0x514220` uses explicit match `+0x48` venue override unless it is -1;
  otherwise it resolves the home participant and returns its club `+4`, or
  -1 if absent. Capture keeps its low word at report `+0xF0`.
- `0x62B3F0` writes the first normalized Condition-history sample into
  participant `+1`; `0x60B8D0` copies that byte's low bit. The later final
  Condition must not substitute for it. Human-vs-AI's `+0xD48` adjustment
  remains unresolved; the parallel worker's retained **raw** history does
  not itself authorize publishing this normalized bit.
- Setup `0x510F40/0x510F6E -> 0x421BA0` selects persistent **DBRPlayer**
  identities from global DBTPlayers `0x875638`, not a newly invented referee
  database. The country auxiliary list at `0x874BD0 + country*20 +0x0C`
  is used only when its `+0x10` count exceeds ten; otherwise selection uses
  the complete player array in original order. First selection retries when
  its first-name string begins `-`; second selection is unfiltered. FE0/FE4
  must retain those setup draws/identities, not draw new substitutes after
  completion. The live setup currently does not retain this path.
- `0x5DB71A/20/26` writes total/home/visiting attendance to D84/D8C/D90.
  Classification thresholds are original doubles 0.3 / 0.7 at 821118/821128;
  `0x5DBDE0` combines the two classifications as min(((a+b) unsigned>>1)+2,4).
  Do not invent classification inputs or a default D9C byte.

Canonical executable SHA-256 remains `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The reused private English STR/IDX hashes match `original_assets/MANIFEST.md`.
Metadata-only private disassembly report SHA-256:
`da1b3da6f72c623c0214fd5350fb89955a83e467e5d4d205b774e10ffc94dfcd`.
Reports remain outside Git. Focused reconciled suite: **156 passed**, preserving
main `50b70390`'s history lifecycle and side-0 targets/trajectories then side-1
targets/trajectories. Capture receives statistics from the same finalizer;
ratings/RNG are not replayed. Complete assembly, ordered owner/link persistence
and successful PMatchInfo opening remain false. No intermediate broad or
Windows audit was run; the final timing/recognizability audit is still gated
on the successful executable route.

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
