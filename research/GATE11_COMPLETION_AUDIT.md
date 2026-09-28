# Gate 11 Completion Audit

_Last updated: 29 September 2026_

## Decision

**Gate 11 - Broader management systems satisfies its roadmap completion
criterion.**

The criterion is:

> A human manager can complete a Premier League season using the core
> management systems.

This is now tested directly rather than inferred from short runs. Commit
`22027de93df54fe7a83151ba642f6d0f86ecc93f` adds a 38-round / 380-match
human-manager regression. The human controller completes one fixture in every
round while the other nine matches run through the shared autonomous backend.
The test also leaves normal recurring maintenance active and enables the live
user-training calendar.

GitHub Actions at that checkpoint ran **676 reconstruction tests**. The only
two failures are the unchanged, pre-existing secondary-schedule assertions:

- `OrderedCompetitionRngTests.test_secondary_root_order_uses_same_crt_qsort_then_mode_filter`;
- `ScheduleBucketShuffleTests.test_secondary_container_bucket_counts_reach_canonical_staff_seed`
  (expected 262, current recovered value 280).

The new 38-round Gate-11 season regression passes. Repository asset policy
also passes.

## Roadmap target audit

### Training / development - satisfied for the core loop

The runtime has persistent per-player training-method state, daily training
Condition recovery and the recovered Saturday primary training transition.
Configured user training is executed by normal calendar progression in the
source-backed commercial-before-training order. Monthly player development is
also a normal calendar hook.

The full-season Gate-11 regression enables the user training calendar and sets
a human player's training method before traversing all 38 rounds.

Broader training-screen presentation and still-unmapped peripheral training
branches remain presentation/fidelity work, not blockers to the core
management loop.

### Scouting - satisfied for the core loop

`HumanGameplayController` exposes both the generic and mapped scouting search
pipelines. The mapped path consumes live player age, value, country context,
preferred positions, transfer/loan/out-of-contract status, six-match
performance history and the recovered Strengths selector/threshold.

Source evidence and implementation details are in
`research/GATE11_SCOUTING_STATUS_AND_STRENGTH.md` and
`research/GATE11_OUT_OF_CONTRACT_LIFECYCLE.md`.

### Youth - satisfied for the core loop

The separate controlled-user youth list is materialized with its 20-record
limit and source-backed fresh/activation initialization. Human management can
inspect the youth list, promote a youth player with a contract or release a
youth player. Youth training state and generated identity survive internal
save/reload.

Evidence: `research/GATE11_YOUTH_WORKFLOW.md`.

### Morale - satisfied for the core loop

Live player morale now covers the ordinary reachable fresh-game producers
needed by the current Premier League management loop:

- post-match loss/win/not-played changes in exact roster/RNG order;
- signed-contract morale in the common signing finalizer;
- loan morale after loan state is installed;
- controlled-club danger morale, including the exact `RNG(30)` boundary and
  next-day `PlayerAskTransferList` mail;
- accept/refuse consequences and persistent Wanted state.

`UnhappyWonTrophy` is proven loader-only/dormant in the canonical executable
and is deliberately not synthesized. The request-new-contract process is
load/compatibility-only on the recovered fresh path.

Evidence: `research/GATE11_MORALE_LIFECYCLE.md`.

### Medical / injury management - satisfied for season continuity

The shared human match backend already generates and persists injuries,
updates Condition, excludes unavailable players from legal team selection and
runs dated injury-return maintenance during calendar progression. A human
manager therefore has to manage availability when selecting the squad and can
continue through injury/return cycles over the season.

A dedicated original treatment/medical presentation surface is not required
for the Gate-11 backend criterion and belongs with the later management
presentation/fidelity gates. The remaining approximation around one
persistent-injury availability-count helper remains explicitly tracked in
`research/FIDELITY_GAPS.md`.

### Discipline - satisfied for season continuity

The common match pipeline applies bookings, sendings-off, competition
discipline state, suspensions and later suspension resolution. Human fixtures
use that same path, and suspended players participate in the existing
availability/selection gates. This state persists across matchdays and
save/reload.

### Messages / news - satisfied at the core event-state layer

Gate 11 requires the management loop, not the final original visual news
screen. The backend now materializes actionable manager-event state needed by
the supported workflows, including:

- controlled contract-renewal suggestions with original Bosman/ordinary kinds;
- next-day low-morale transfer requests and accept/refuse handling;
- persistent manager-sacking reason consumed at the single-user control
  boundary.

These records survive internal save where required. Full original
message/news presentation, text layout and navigation remain intentionally
assigned to Gate 13.

### Recurring manager tasks - satisfied for the core loop

Normal progression now connects the major recovered recurring tasks rather than
requiring isolated helper invocation:

- daily injury returns;
- daily commercial timing before configured user training;
- daily training recovery and Saturday primary training;
- monthly player development;
- monthly controlled/non-controlled contract maintenance;
- due transfer completion;
- weekly player payroll;
- weekly autonomous AI acquisition;
- Premier League matchday financial/objective progression;
- post-match Condition, injury, discipline, Form and morale persistence.

The 38-round regression traverses the season calendar through these recurring
boundaries while retaining active human control.

## Full-season regression

`reconstruction/test_gate11_management_season.py` constructs a complete
20-club, 38-round, 380-fixture Premier League schedule and exercises
`HumanGameplayController` through every human fixture.

It verifies:

- 38 distinct human fixtures complete;
- every matchday completes all 10 fixtures;
- all 380 league fixtures have results by season end;
- table played totals equal 760 and the human club has played 38;
- legal 11-starter / 5-substitute selections remain possible each round;
- human-squad Condition stays inside 0..100;
- Form stays inside 0..4;
- the user training calendar remains enabled during the run;
- no next human Premier League fixture remains after round 38.

This is deliberately a deterministic backend completion test. Gate 13 later
restores the original management presentation on top of this state.

## Explicit non-blockers retained for later gates

Gate 11 closure does **not** claim that all FM2001 management fidelity is
finished. In particular, the following remain tracked rather than hidden:

- the two long-standing secondary-schedule assertions;
- broader competition/cup behavior, which is Gate 12;
- original message/news, medical, training and scouting screen presentation,
  which is Gate 13;
- original save-file compatibility;
- remaining bounded items in `research/FIDELITY_GAPS.md`;
- FastView/3D and original match presentation.

Those items do not invalidate the Gate-11 criterion because the clean-room
human manager can now traverse a complete Premier League season with the core
management state and recurring systems active.

## Gate transition

With the completion criterion verified, the project can advance to
**Gate 12 - Other competitions**.

The first Gate-12 task should stay narrow: audit the already-recovered generic
competition/cup runtime against the canonical English domestic cups and identify
the first missing behavior required to make the Premier League cease behaving
as an isolated world. Preserve the existing deterministic competition tests
while extending from source-backed FA Cup / League Cup data.
