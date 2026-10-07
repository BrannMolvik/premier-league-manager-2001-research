# Gate 13 fresh-Squad reserve-selection source trace

_Recovery 396, 8 October 2026._

## Evidence boundary

This note records first-hand static analysis of the canonical shipped executable
only. No original executable bytes are committed.

Canonical `FOOTBAL.EXE` SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The executable was re-extracted from the authorized
`The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`
MODE1/2352 image during Recovery 396 and its SHA-256 was reverified before this
trace.

## Confirmed player selection-state layout

The previously recovered ordinary-Squad name helper reads four mutually
exclusive selection branches in this priority order:

| State | Native storage / predicate | State code |
| --- | --- | ---: |
| first-team active | `DBRPlayer+0x14` bit 4 / `0x417EE0` | 4 |
| first-team substitute | `DBRPlayer+0x14` bit 5 / `0x417F00` | 3 |
| reserve active | `DBRPlayer+0x174` bit 0 / `0x417EA0` | 2 |
| reserve substitute | `DBRPlayer+0x174` bit 1 / `0x417EC0` | 1 |
| none | all four predicates false | 0 |

Both reserve predicates first require the supplied club/team id to equal the
player's `+0x10` owner-club id, exactly like the two first-team predicates.

`0x4218E0` is the source-closed five-state reader. It tests first active,
first substitute, reserve active, then reserve substitute and returns exactly
`4,3,2,1,0` respectively.

`0x421950` is the inverse state dispatcher:

- state 0 -> `0x4181B0` clear selection;
- state 1 -> `0x418280` reserve substitute;
- state 2 -> `0x4181E0` reserve active;
- state 3 -> `0x4182C0` first-team substitute;
- state 4 -> `0x4182F0` first-team active.

Values above 4 take no setter branch.

## Confirmed initialization and mutation semantics

The player initialization path at `0x417700` writes zero to
`DBRPlayer+0x174` at `0x41774B`. The reset/reassignment path beginning
`0x4177C0` also writes zero at `0x41783C`. Therefore fresh native player
objects do **not** begin with unknown reserve state: both reserve-selection bits
are false.

The four selection setters preserve mutual exclusion:

- `0x4181E0` clears both first-team bits, sets reserve bit 0, and clears reserve
  bit 1.
- `0x418280` clears both first-team bits, clears reserve bit 0, and sets reserve
  bit 1.
- `0x4182C0` sets first-team substitute, clears first-team active, and clears
  both reserve bits.
- `0x4182F0` sets first-team active, clears first-team substitute, and clears
  both reserve bits.
- `0x4181B0` clears all four selection branches and resets the associated
  current-position state through the already recovered helpers.

The dedicated reserve clear helpers are also source-closed:
`0x418170` clears reserve bit 1; `0x418180` clears reserve bit 0 (performing
the associated `0x418220` state maintenance before the clear when it was set).

## Consequence for the clean-room fresh Squad

The clean-room `RuntimePlayer` currently models only
`match_active` and `match_substitute_available`, both defaulting false.
The ordinary Squad presenter consequently passes unknown reserve state and
withholds every name whose first-team flags do not decide the color branch.

That fail-closed behavior was correct while the `+0x174` producer was unknown,
but the source boundary above supersedes that uncertainty for reachable fresh
clean-room states. The exact implementation task is now bounded:

1. represent reserve-active and reserve-substitute state explicitly on
   `RuntimePlayer`, defaulting both false to match native initialization;
2. preserve the recovered five-way exclusivity in selection setters/clear paths;
3. carry the two booleans through `SquadRowView` into
   `build_squad_row_viewport()`;
4. pass them into `squad_name_rgb_from_available_state()`, which already has
   the exact color precedence;
5. cover state codes 0..4 and fresh default-yellow names with regression tests;
6. reconcile save/restore only where current first-team selection state is
   already serialized, rather than inventing a new lifecycle.

This source closure does not itself claim the fresh Squad screen complete. The
runtime propagation above and the separate missing management-header binding
must still be implemented and verified.
