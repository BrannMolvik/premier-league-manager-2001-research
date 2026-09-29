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

## Verified annual primary construction primitive

The first bounded clean-room annual primitive is now implemented without
mutating live GameState.

- `primary_schedule.nominal_primary_schedule_bucket(..., season_year=...)`
  now derives the 25-December skip from the actual Gregorian date. The shipped
  2000/01 coordinate remains week 25 / weekday 1, while 2001/02 correctly
  moves week 25 / weekday 2 instead.
- `season_regeneration.clubs_with_live_competition_memberships()` overlays
  the post-LeagueAllocation live membership map on immutable source Club rows.
- `materialize_annual_primary_schedule()` calls the recovered primary
  competition materializer with **no fixed-fixture League IDs**, so Premier
  League ID 0 follows the proven annual procedural path.
- The same caller-owned CRT object then continues directly through
  `place_primary_schedule_nodes(..., season_year=...)` and
  `shuffle_primary_schedule_buckets()`.
- No shipped 2000/01 real-fixture rows are supplied to the annual path.
- A synthetic promotion/relegation regression proves a newly promoted club
  enters the year-two Premier League schedule while the relegated club does
  not, and every Premier node is `league_match`, not
  `fixed_league_match`.

Verified code checkpoint:

```text
09a5c269e82da597f114b66e71b1416de7f14f2b
Test annual primary schedule regeneration
```

GitHub Actions ran **797 tests with 2 failures**, exactly the unchanged known
secondary-schedule assertions. Repository asset policy passed.

This primitive intentionally stops before GameState replacement. It proves the
annual primary generation mechanics while keeping unresolved cross-season Cup
qualification/finalization state from being silently guessed.

## Annual qualification and DummyLeague source refresh

The two DBRClub fields originally loaded from Master.dat as startup
historical/qualification state are also rewritten by the executable at every
season boundary.

### League/DummyLeague qualification enumeration

League vtable `0x7C9AC0` maps virtual `+0x0C` to `0x4F8000`.
After end-of-season ranking work, `0x4F8000` calls `0x4F7F70`.

`0x4F7F70`:

1. finalizes child competitions through `0x4F7F40`;
2. walks the sorted current League array at `+0x34`;
3. copies each resolved club pointer into the dedicated qualification
   enumeration array at `+0x30` at the same zero-based index;
4. for root Leagues (parent pointer `+0x04 == 0`), writes that same index to
   **club+0x30**.

Then annual finalizer `0x4F9010`, immediately after
`0x616A70` and **before** LeagueAllocation promotion/relegation swaps, walks
clubs in the finalized schedule container and writes:

```text
club+0x2C = low byte of club+0x10
```

Thus the next-season type-3 qualification pair is exactly:

```text
club+0x2C = competition the club just finished
club+0x30 = zero-based final position in that competition
```

LeagueAllocation later changes current membership at club+0x10 through
`0x405700` but does not overwrite +0x2C/+0x30. A promoted or relegated club
therefore enters the new season with separate values for **new membership** and
**prior-season qualification source/slot**.

This maps directly onto the clean-room startup-compatible fields
`historical_competition_id` / `historical_slot_index`; annual code must
overlay them from exact final rankings rather than reuse the shipped
Master.dat values.

### Cup qualification enumeration

Cup vtable `0x7C9B58` maps virtual `+0x0C` to `0x4F8F80` and virtual
`+0x1C` to enumerator `0x4F5770`.

During the same `0x616A70` finalization pass, `0x4F8F80` finalizes the
Cup, resolves the completed result club and opposite/finalist path, and stores
the two persistent enumeration pointers at:

```text
Cup+0x40
Cup+0x44
```

`0x4F5770` is the later type-3 source accessor for exactly those two values.
Annual Cup-to-Cup type-3 allocation must therefore use the just-finished Cup
result pair and must not fall back to the two shipped first-season
DBRCompetition club references.

### DummyLeague annual re-sort

DummyLeague vtable `0x7C9A80` maps annual init virtual `+0x00` to
`0x4F5130`. Every call clears bit 0 of byte `+0x40` before common child
initialization.

`League::EnsureSorted 0x4F4940` tests that same bit. If clear, it dispatches
virtual `+0x38`; DummyLeague maps that slot to RNG-bearing `0x4F4750`, then
sets the bit again.

This proves a reused DummyLeague runtime object receives a **fresh one-time
lazy ranking each new season**. Canonical primary Cup allocation makes this
immediately relevant: FA Cup allocation instruction **ID 3** is type 5 from
Conference 2 (competition 89), quantity 10. Therefore annual FA Cup
construction is the legitimate first next-season consumer that can re-sort
Conference 2 after its membership has changed.

The clean-room annual materializer must feed that sort:

- post-LeagueAllocation current Conference 2 membership;
- current live player ratings/club rosters at the annual construction point;
- the same annual competition CRT stream.

It must not carry the prior season's cached Conference 2 ranking into the new
FA Cup draw.

### Primary root finalization order

The annual qualification snapshot is produced through the separate
`0x616A70 -> 0x411150` finalization walk before LeagueAllocation membership
swaps. Direct traversal reconciliation closes its outer ordering:

- countries remain in source-table order;
- each country's root array is the already-qsorted runtime array;
- `0x411150` walks that array **forward**;
- `0x411020` initialization walks the same array **backward**.

Finalization is therefore the reverse of initialization **within each country
chunk**, not a global reversal across countries.
`primary_mode0_root_finalization_order()` models this explicitly and
`cb4f8abd41c0ac5ff3cf7df03d0295393ab7b8ec` adds a regression covering
the per-country reversal.

GitHub Actions at that checkpoint ran **802 tests with 2 failures**, exactly
the unchanged known secondary-schedule assertions. Repository asset policy
passed.

### Annual materializer safeguards

`materialize_annual_primary_schedule()` now separates current membership from
finished-season qualification state:

- `competition_id` comes from the post-swap live membership map;
- annual League/Dummy type-3 sources require an explicit exact
  `qualification_rankings_by_competition`;
- those rankings overlay the source-compatible
  `historical_competition_id/historical_slot_index` fields;
- annual Cup type-3 sources require explicit
  `cup_enumerated_club_ids_by_source`;
- missing refreshed type-3 state raises instead of silently reusing shipped
  startup references.

A regression deliberately relegates a club after it finished first in a source
League. The club remains selected by annual type-3 Cup allocation from its
finished-season ranking while its new current membership is already the lower
League, reproducing the executable's separated +0x10 versus +0x2C/+0x30 state.

## Current implementation boundary

Already verified and preserved:

- post-season club competition memberships;
- exact final League rankings;
- playoff winners;
- Conference 2 current-season DummyLeague ranking;
- all 14 English membership exchanges;
- annual League/Dummy type-3 qualification source requirements;
- annual Cup type-3 requirement for the just-finished `Cup+0x40/+0x44` pair;
- annual DummyLeague invalidation and first-consumer lazy re-sort semantics;
- per-country primary-root finalization order;
- internal save schema 33.

One source detail is still intentionally open. The executable-backed research
proves that `0x4F8F80` writes the completed result club and the opposite/finalist
path into the two persistent enumeration slots, and `0x4F5770` later returns
`Cup+0x40` as index 0 and `Cup+0x44` as index 1. The repository does **not**
yet record which semantic value owns which slot. Because type-3 allocation is
positional, annual live-state extraction must not guess that ordering.

Do **not** implement next-season schedule rebuilding by rerunning the canonical
startup materializer. That would incorrectly replay mode-1-only behavior and
may duplicate startup RNG.

## Exact next trace

1. instruction-close the positional writes in `0x4F8F80`: prove which of
   `Cup+0x40` / `Cup+0x44` receives the completed result club and which
   receives the opposite/finalist path;
2. expose one live end-of-season qualification snapshot containing every
   required League/Dummy ranking plus each proven ordered Cup pair, with
   explicit failure for missing sources;
3. atomically replace GameState's prior-season Premier/procedural
   League/Cup/ranking/primary-shadow/order objects from the verified annual
   materialization;
4. preserve the controller's competition/match CRT stream across that rebuild
   and keep the separately persisted GameState maintenance RNG split explicit
   rather than silently conflating the two.
