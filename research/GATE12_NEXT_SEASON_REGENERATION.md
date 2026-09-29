# Gate 12 - Next-Season Regeneration Trace

_Last updated: 29 September 2026_

## Scope

This note traces the original transition from the verified annual English
LeagueAllocation membership swaps into the next season's competition runtime.
It is intentionally evidence-first: no clean-room regeneration code should be
added until the startup-only and annual-reuse paths are separated.

## Live calendar rollover entry

The normal calendar/progression function is at `0x4A83F0`; it is directly
called from `0x4320BD`.

At the primary-container season end:

1. `0x4A866B` reads the current year global `0x9847FC`.
2. `0x4A8676` increments the year.
3. `0x4A867B` stores the new year **before** competition finalization.
4. manager/player annual update calls run.
5. `0x4A86AA` calls `0x4F9010(0)` for the primary container.
6. additional manager/player annual reset/update work runs.
7. if the secondary container reaches its own terminal date,
   `0x4A878B` calls `0x4F9010(1)`.
8. `0x4A83F0` then returns; it does not directly call `0x4F7C00`.

This proves live annual rollover is distinct from the initial new-game
competition construction path.

## End-of-season finalization

`0x4F9010` remains the source-backed end-of-season finalizer.

The already-verified English LeagueAllocation membership swaps run inside it at
`0x4F948F`.

Near the end of the routine:

- `0x4F9911` calls `0x4F7A60` for the active schedule container;
- `0x4F991B` calls `0x615860`, which walks bucket linked-list heads and
  frees/clears their nodes;
- `0x4F994A` calls `0x616620(0)`.

The `0x615860` call is teardown/cleanup, not construction. Earlier working
notes that treated this pair as a possible rebuild were corrected by direct
disassembly.

## Initial construction is a separate path

`0x4F7C00` has one direct executable caller: `0x4C4381`, inside
`0x4C41C0`.

`0x4C41C0` is reached from the event/message handler around `0x4DA480`
(`0x4DA4A5 -> 0x4C41C0`) for event codes 0x29/0x2A. No annual calendar
caller reaches `0x4F7C00` directly.

`0x4F7C00` performs first-construction work:

1. calls `0x6169F0` on primary and secondary schedule containers;
2. allocates/builds competition runtime objects;
3. builds per-root runtime arrays;
4. calls `0x4F7A60` for primary and secondary containers;
5. calls `0x616620(1)` on both containers.

Therefore the clean-room year-two path must not simply replay
`0x4F7C00` or all startup materialization.

## Shared container initializer/finalizer

`0x616620(mode)` is the shared lifecycle routine.

Both first construction and annual rollover reach it:

```text
first construction:
    0x4F7C00
      -> create runtime objects
      -> 0x4F7A60(primary)
      -> 0x4F7A60(secondary)
      -> 0x616620(primary, mode=1)
      -> 0x616620(secondary, mode=1)

annual rollover:
    0x4F9010(active container)
      -> LeagueAllocation membership exchanges
      -> old bucket cleanup
      -> 0x616620(active container, mode=0)
```

Inside `0x616620`:

- the container is marked busy at `+0x15`;
- matching competition/country records are walked;
- `0x411020(..., mode)` performs mode-aware date/state updates;
- each matching competition record reaches `0x404110(mode)`;
- the routine ends with `0x615BE0` and clears the busy flag.

The mode bit is therefore a real startup-versus-rollover semantic switch, not
merely UI/progress reporting.

## Competition annual branch: 0x404110

The argument to `0x404110` is read at `[esp+0x10]` after its three saved
registers.

Common work resets competition-season state and eventually converges on
`0x4F32C0`.

### mode = 1: first-season initialization

For applicable competition kinds, the mode-1 branch can:

- call `0x409B50`;
- call `0x4F3240`;
- then converge on `0x4F32C0`.

This path is not executed by the annual mode-0 branch.

### mode = 0: annual team reuse

Correction after direct object-layout reconciliation: `0x404110` is a
**team** annual routine, not a competition object. Its `+0x244` array /
`+0x294` count is the team's player list, and global `0x875640` is the
0x250-byte runtime player table.

The annual branch therefore:

1. walks the team's existing player list at `+0x244` in reverse;
2. calls player annual helper `0x41ACA0` for every referenced player;
3. skips the startup-only team setup `0x409B50 / 0x4F3240` path;
4. converges on the same `0x4F32C0` team-season reset.

This branch does **not** repopulate League membership. Post-promotion
competition regeneration occurs earlier through country helper `0x411020`,
which invokes each competition object's virtual `+0x00` with the same
startup/annual flag.

## Bucket finalization and annual ordering RNG

`0x615BE0` iterates every schedule-container bucket and calls `0x615AE0`
on each.

`0x615AE0` is now instruction-closed:

1. count the bucket's linked-list nodes;
2. copy each node pointer into a temporary array in current linked-list order;
3. for remaining sizes `N, N-1, ... 2`, call `0x64D540(remaining)`;
4. swap the selected array entry with the current tail entry;
5. relink the bucket list from that shuffled array and terminate the final
   node with null;
6. free the temporary array.

This is the same Fisher-Yates ordering layer modeled by
`shuffle_primary_schedule_buckets()`. Annual `0x616620(0)` therefore
consumes a **fresh per-bucket shuffle stream after annual competition
initialization**, rather than preserving the prior season's matchday order.

## Annual competition virtuals

### League::init 0x4F5150

The mode flag passed by `0x411020` has a direct schedule-construction effect.

- `mode=1` (first season): when shipped real fixtures are available,
  `League::init` can call fixed builder `0x6173D0`; otherwise it calls
  procedural builder `0x6170F0`.
- `mode=0` (annual rollover): it bypasses the real-fixture test and calls
  `0x6170F0` directly.

Therefore competition **0, F.A. Premier League, becomes procedurally generated
from year two onward**. The 2000-01 shipped real-fixture list is a first-season
input only and must not be reused after promotion/relegation.

The existing clean-room primary materializer already has this representational
split: passing an empty `fixed_fixture_competition_ids` set makes competition
0 follow the procedural-League path and derives its participant count from
current club membership.

### Cup::init 0x4F5A30

Direct stack-argument tracing shows the startup/annual argument is not read by
the Cup draw/schedule construction body. The sole argument read is at the final
`0x4F632D -> 0x4F3DE0` base-state call after Cup rounds/matches have already
been created.

The recovered Cup allocation, participant shuffle/qsort, symbolic ClubRefs and
round scheduling can therefore be reused for annual mode provided their
**source club memberships and live player/team inputs are updated** and the
same global CRT stream is used.

## Current implementation boundary

Already verified and preserved:

- post-season club competition memberships;
- exact final League rankings;
- playoff winners;
- Conference 2 current-season DummyLeague ranking;
- all 14 English membership exchanges;
- internal save schema 33.

Do **not** implement next-season schedule rebuilding by rerunning the canonical
startup materializer. That would incorrectly replay mode-1-only behavior and
may duplicate startup RNG.

## Exact next trace

1. prove the annual League participant source after the already-verified
   membership swaps and map it to the live `club_competition_membership` view;
2. preserve one global CRT stream through annual competition initialization and
   the now-closed `0x615AE0` bucket shuffle;
3. determine the next season's DummyLeague/Conference 2 ranking regeneration
   timing and ensure live player ratings, not immutable startup ratings, feed it;
4. map annual mode-0 output onto new `PremierLeagueState`, procedural League,
   Cup/playoff, ranking, primary-shadow and primary-order state, clearing all
   prior-season results without replaying first-season-only real fixtures.
