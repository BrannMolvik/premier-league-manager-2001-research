# Gate 12 - European Competitions

_Last updated: 29 September 2026_

## Scope

This is the canonical live audit for Gate 12's European expansion. It starts
from the already-recovered primary competition startup/materialization rather
than rebuilding European draws.

## Canonical competition identities

- competition **9** = Champions League;
- competition **10** = UEFA Cup.

Both already participate in the exact primary-container startup RNG stream and
post-shuffle schedule materialization.

## Startup behavior already solved

The Gate-3/Gate-4 reconstruction already owns:

- Europe-root candidate filtering and the original count-minus-one selector;
- exact Champions League / UEFA Cup initialization order on the shared CRT RNG;
- Cup allocation and participant shuffles;
- MiniLeague group construction;
- child procedural-League round-robin generation;
- knockout NormalRound / TwoLeg scheduling;
- competition-position ClubRefs;
- Champions-League-to-UEFA cross-Cup transfers;
- complete primary schedule placement and shuffle.

Canonical materialization contains **1,226 Cup nodes** inside **9,346 primary
schedule nodes**. The UEFA Cup's recovered runtime participant counts for rounds
210..217 are `80, 95, 47, 31, 15, 7, 3, 1`; the scheduler intentionally
pairs `floor(count/2)` and does not synthesize a bye for an unpaired ref.

## ClubRef progression boundary

Instruction-backed meanings relevant to Europe:

- type 0 = direct club;
- type 1 = referenced knockout result, selector 0 winner and nonzero selector
  loser/opposite;
- type 2 = competition-position reference. The selector addresses the
  zero-based eligible position in a referenced runtime competition/context;
- type 3 = the distinct MiniLeague group-position transfer reference used when
  Champions League group placements feed the UEFA Cup;
- type 4 belongs to Scottish Premier League procedural scheduling and is not a
  primary European Cup allocation dependency.

## First live European bridge

Commit `0feb1278ec2cfebc07379732a19ef8ab2f733777` extends
`CupResultRegistry` with persistent rankings keyed by
`(competition_id, competition_context)`.

ClubRef type 2 now resolves its zero-based selector when that live ranking has
been published and remains unresolved otherwise. Rankings can be refreshed as a
live league/group table changes.

Internal save schema **29** persists these rankings alongside knockout outcomes.

Verification at `0feb1278`:

- reconstruction suite: **752 tests**, with only the two unchanged known
  secondary-schedule failures;
- repository asset policy: **passed**.

## Exact next target

Build the minimum live European child/procedural-League state that consumes the
already-materialized `league_match` nodes, updates the source-backed group
ranking, and publishes it to the type-2 registry. In parallel, finish the
instruction trace for ClubRef type 3 rather than assuming it is identical to
type 2.

Only after those position dependencies are live should European knockout nodes
be attached to the existing shared CupMatch execution/controller path.


## Live procedural-League state verified

Commits `17250101` through `867262db` attach Champions League child
competitions **14** and **167** to live `GameState` without rebuilding their
already-canonical startup groups or schedule nodes.

The persisted full-primary schedule shadow is reused as the source of each
`league_match` fixture and symbolic participant reference. A child
competition/context materializes only when every participant ref can resolve;
phase 2 therefore remains pending until the required phase-1 type-2 positions
exist.

Group results update the existing 3/1/0 `LeagueRow` state. Progression
rankings are published to `CupResultRegistry` only when:

1. every fixture in that group has a result; and
2. points, goal difference and goals scored uniquely order every club.

The clean-room club-ID display fallback is never published as gameplay truth.
If a complete group is still tied on all proven keys, any stale ranking is
withdrawn and the dependent ClubRef remains unresolved.

Internal save schema **30** preserves the live procedural-League
fixtures/results plus the type-2 ranking registry.

Verification at `867262db`:

- reconstruction suite: **762 tests**, with only the two unchanged known
  secondary-schedule failures;
- repository asset policy: **passed**.

## Exact next target

Expose child competition 14/167 `league_match` nodes in the post-shuffle
primary matchday order and execute due group fixtures through the shared
MatchCalculator. Record those scores into the verified live procedural-League
state, preserving schedule order and save/reload. Keep ClubRef type 3 separate
until its resolver path is source-backed.


## Primary group execution and ClubRef type 3 closed

Commits `3742a7e` / `9ac3da0` / `da31e5b` execute due child competition
14/167 LeagueMatch nodes in the already-shuffled primary order through the
shared MatchCalculator. The bridge preserves both-AI-selection -> weather ->
side-0 Condition -> side-1 Condition ordering, records the score into the live
procedural-League state, preserves the shared four post-calculator gate draws,
and applies the existing exact-or-pending shared post-match persistence.

Verification at `da31e5b` is **769 tests** with only the same two known
secondary-schedule failures; repository asset policy passes.

Direct canonical-executable tracing now also closes ClubRef type 3:

- constructor `0x4F2D40` encodes
  `runtime_instance_count * position_index + instance_ordinal`;
- resolver `0x4F2992..0x4F2A73` divides that selector back into position and
  ordinal with `0x66A518`;
- it takes that same position from every linked child League/group, after each
  group is refreshed through `0x4F4940`;
- it globally sorts those cross-group candidates with League comparator
  `0x4F45E0` and selects by the decoded instance ordinal.

So the Champions-League-to-UEFA type-3 transfer is a globally ranked pool of
same-position group finishers, not a direct per-group position lookup and not a
type-2 alias.

### Next implementation boundary

Publish that source-backed cross-group ranking into the live result registry so
the existing decoded type-3 descriptors resolve, persist it through internal
save/load, and then attach the now-resolvable European knockout nodes to the
shared CupMatch runtime/controller path.


## Type-3 UEFA transfer dependency verified end-to-end

Checkpoint `474086bb26fe7185b0022ea84568653b443d8e0f` closes the active
European knockout dependency boundary with a deterministic regression that
uses live procedural-League state rather than a hand-injected final club ID.

The regression:

- materializes two child competition-14 groups;
- completes both groups with distinct source-backed numeric table keys;
- lets `record_procedural_league_result()` publish the recovered ClubRef type-3
  cross-group second-place pool;
- verifies the pool order as `(4, 2)`;
- resolves a UEFA Cup competition-10 knockout participant through the symbolic
  type-3 descriptor to club 4;
- verifies that the resulting UEFA knockout node is playable against club 5;
- saves and reloads the game;
- verifies that the same type-3 pool and symbolic UEFA pairing still resolve
  after reload.

The first version of the regression exposed a test-fixture source-identity
mismatch rather than a runtime bug. The corrected test supplies the same
competition-14 source identity on reload and builds the primary shadow through
the canonical `PrimaryScheduleShadowState` constructor.

Verification at `474086bb`:

- reconstruction suite: **780 tests**, with only the two unchanged known
  secondary-schedule failures;
- repository asset policy: **passed**.

This closes the planned Champions-League-group -> type-3 -> UEFA knockout
save/reload bridge. European group execution, type-2 progression, type-3
cross-group progression, shared CupMatch knockout execution, primary-order AI
and human routing, and save/reload are now all covered.

## Next Gate-12 boundary

Move to the roadmap's next slice: **other required English league/divisional
structures**. Start with an audit of the already-canonical startup
materialization and identify the first runtime format/state bridge that is not
yet covered. Do not reopen solved European draw, group, ClubRef, knockout,
primary-order, human-controller, or save/reload behavior.
