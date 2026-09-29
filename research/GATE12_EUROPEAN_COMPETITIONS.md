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
