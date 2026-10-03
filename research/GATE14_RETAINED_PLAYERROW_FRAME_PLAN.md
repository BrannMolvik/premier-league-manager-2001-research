# Gate 14 retained-history PlayerRow frame path

_Status: Gate-14 work-ahead on canonical retained-history PlayerRow adapter 7d235383._

## Purpose

The completed match result already retains the source-domain Condition and
match-form histories consumed by FastView PlayerProxy. The retained-history
adapter can turn those histories into immutable PlayerRow snapshots when the
caller supplies visible row metadata and the exact presentation RNG(6) results.

This checkpoint connects that adapter to the completed-human FastView frame
builder without mutating gameplay state or requiring the outcome object to be
rewritten first.

## Contract

`build_human_fastview_frame_plan_from_retained_histories()` accepts:

- one already-completed human outcome;
- the verified FastView chrome, possession, figures and TeamTable art inputs;
- an explicit tuple of `FastViewRetainedPlayerRowIdentity` values;
- one non-negative FastView global tick;
- an explicit source-player -> RNG(6) result mapping;
- an optional already-verified score/table static raster set.

The function:

1. builds the normal read-only `HumanMatchPresentation`;
2. refuses to continue if that outcome already carries PlayerRows, avoiding two
   competing presentation sources;
3. builds PlayerRows from the completed result's retained histories;
4. creates a replaced presentation value with those immutable rows;
5. feeds that value through the existing semantic-shell and frame-plan chain.

The original outcome and completed result are not mutated.

## Fidelity boundary

This path does not import or invoke simulation, MatchCalculator, gameplay
controllers, GameState, an RNG implementation, sound/commentary, or 3D logic.

The caller must supply the correctly ordered RNG(6) results. The presentation
layer never advances or aliases gameplay RNG state.

All existing FastView frame fail-closed boundaries remain unchanged:

- cross-component z-order is unresolved;
- the resolved-only image still masks overlapping component pixels;
- the frame is not promoted to complete raster fidelity;
- audio is not ready;
- 3D choreography is not ready.

## Remaining integration boundary

Automatic production of the row identities and exact presentation RNG sequence
from the live human-match route still crosses shared gameplay/runtime ownership.
That remains deferred while Gate 13 is exclusively Codex-owned.

This checkpoint nevertheless closes the disjoint renderer-input route: once
those source inputs are available, no mutation or replay of the completed match
is required to obtain a PlayerRow-populated FastView frame.
