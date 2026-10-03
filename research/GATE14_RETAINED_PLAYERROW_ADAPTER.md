# Gate 14 retained-history PlayerRow adapter

_Date: 4 October 2026 KST_

_Status: independent Gate-14 work-ahead. Gate 13 remains the earliest incomplete
validation gate and stays exclusively Codex-owned._

## Purpose

The current match runtime already retains the exact completed 24-sample
FastView Condition and match-form histories used by the original PlayerProxy.
The existing PlayerRow presentation code can also build source-backed rows from
those histories, but there was no presentation-only bridge between the two.

This checkpoint closes that bridge without changing gameplay state.

## Source boundary

The adapter consumes only already-retained source-domain presentation inputs:

- side-local player identity;
- 24 Condition samples;
- 24 match-form samples;
- explicit visible row index;
- shirt/squad-number byte;
- source position code;
- source player display-name fields;
- optional goal/own-goal text counts only when the caller knows those callback
  writes occurred;
- one caller-supplied RNG(6) result for each requested PlayerProxy energy
  evaluation.

It delegates form and energy evaluation to the existing exact
gate14_fastview_player_history.py primitives and delegates row construction to
the existing gate14_fastview_playerrow_snapshot.py source contract.

## Implementation

reconstruction/gate14_fastview_playerrow_from_result.py adds:

- FastViewRetainedPlayerRowIdentity;
- build_fastview_player_rows_from_retained_histories().

The completed result is intentionally structural. The module reads only
fastview_condition_histories and fastview_form_histories and does not import
match_simulation, game_state, human_gameplay, MatchCalculator, or any RNG
implementation.

The adapter fails closed when:

- retained Condition/form identity sets differ;
- a retained history identity is duplicated;
- a requested source player or visible row slot is duplicated;
- a requested player has no retained histories;
- a retained history is not exactly valid in the source 24-sample domains;
- RNG(6) results do not exactly cover the requested source-player identities;
- a supplied RNG result is outside 0..5.

The explicit RNG-result requirement is deliberate. PlayerProxy energy consumes
one presentation RNG(6) result when evaluated; this adapter must not advance,
recreate, or alias a gameplay RNG stream.

## Verification

reconstruction/test_gate14_fastview_playerrow_from_result.py covers:

- multi-side retained-history projection;
- exact form and energy values at a selected GlobalTick;
- explicit goal/own-goal callback text retention;
- mismatched and duplicate retained histories;
- duplicate source-player and visible-row identities;
- exact RNG(6) key coverage and bounds;
- malformed/missing retained history data;
- an architectural guard against simulation/gameplay/RNG imports.

The local execution sandbox is currently unavailable before process start, so
this checkpoint requires hosted CI before merge. No local passing-test claim is
made.

## Remaining integration boundary

The shared human gameplay/runtime files are still inside the active Gate-13
Codex ownership boundary. This checkpoint therefore does not mutate a completed
human outcome to attach rows automatically.

Once that ownership lock is released, the shortest integration path is to feed
the retained histories plus source display metadata and the correctly ordered
presentation RNG(6) results into this adapter, attach the resulting immutable
PlayerRow snapshots to the completed human presentation payload, and let the
existing semantic-shell/frame-plan chain consume them unchanged.

This is source-backed Gate-14 implementation progress, not Gate-14 completion.
