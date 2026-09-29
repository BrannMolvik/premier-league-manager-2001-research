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

### mode = 0: annual reuse

The annual branch instead:

1. walks the competition's existing club-slot list at `+0x244` in reverse;
2. calls `0x41ACA0` for each referenced club/source object;
3. skips the startup-only `0x409B50 / 0x4F3240` path;
4. converges on the same `0x4F32C0` season-state reset.

This is the strongest evidence so far that year two **reuses the existing
competition runtime objects after the membership swaps**, rather than rebuilding
them from scratch through the initial materializer.

`0x41ACA0` itself performs annual club/source maintenance and consults the
club's current competition relation before additional reset work. Its exact
effect on the competition's club-slot ordering still needs to be
instruction-closed before implementing the clean-room annual roster rebuild.

## Bucket finalization

`0x615BE0` iterates every schedule-container bucket and calls `0x615AE0`
on each.

The body immediately preceding `0x615BE0` contains an RNG shuffle over an
array followed by linked-list relinking; the exact relationship between that
helper and `0x615AE0` still needs to be named precisely.

This is now the leading boundary for proving whether next-season primary
matchday ordering consumes fresh RNG after per-competition annual
reinitialization.

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

1. instruction-close `0x41ACA0` enough to prove how clubs with newly swapped
   competition memberships repopulate/reorder the existing League runtime;
2. trace `0x615AE0` and the surrounding shuffle helper to prove annual bucket
   insertion/order RNG;
3. determine when the next season's DummyLeague/Conference 2 ranking is
   regenerated relative to `0x616620(0)`;
4. map the above annual mode-0 behavior onto the clean-room
   `PremierLeagueState`, procedural League state, Cup/playoff state, and
   shared primary-order structures without reusing stale prior-season results.
