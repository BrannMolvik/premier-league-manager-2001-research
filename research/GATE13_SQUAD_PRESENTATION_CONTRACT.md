# Gate 13 Squad Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes already recovered ordered-team-roster and
DBRPlayer match-selection state into the Gate-13 read-only presentation seam.
It does **not** claim the original Squad screen class, row sort, visible columns,
layout, artwork or navigation.

## Ordered team roster

Canonical executable research confirms the live team roster representation:

```text
team +0x244  uint16 player IDs
team +0x294  roster count
```

Player startup `0x421CE0` appends players through team helper `0x40D4F0`.
The append tail writes the player ID at the current count and increments that
count. There is no separate rating/position sort before the fresh roster is
built.

For a newly initialized shipped database, the resulting initial roster order is
the global Master.dat / DBRPlayer order filtered by current club. Later
transfers or roster-reordering operations may mutate the live order, so Gate 13
must consume the current ordered roster rather than reconstructing a new sort.

## Participant collection and selection flags

After lineup state has been assigned, participant collector `0x510CD0` walks
the ordered roster, resolves each player ID to the runtime DBRPlayer record and
includes the player when either:

- active predicate `0x417F50` succeeds; or
- substitute predicate `0x417F60` succeeds.

Included players retain team-roster iteration order.

For the player's current club, both predicates are backed by DBRPlayer
selection flags at `+0x14`:

- bit 4 / `0x10` = starting/on-field active;
- bit 5 / `0x20` = substitute available.

The recovered mutation helpers are:

- `0x4182F0`: set active and clear substitute state;
- `0x4182C0`: set substitute and clear active state;
- `0x4181B0`: clear both and reset position state.

These are runtime/backend selection semantics. They do not prove how the
original Squad screen visually represented a starter, substitute, reserve or
unavailable player.

## Read-only Gate-13 boundary

`ManagementSourceDataBridge.squad_rows()` already projects the live controlled
club roster in backend order and records the source-roster index for every row.
The new immutable `SquadPresentationContract` pins the native roster offsets,
selection predicates/setters and flag masks that justify preserving that
ordering/state.

The bridge remains read-only. It does not assign lineups, toggle DBRPlayer
selection flags, reorder the roster or simulate a match.

## Explicit non-claims

The contract intentionally contains no:

- original Squad panel RTTI class or numeric screen ID;
- proof of the original Squad screen's row comparator/sort;
- visible column names or their order;
- status icon or color bindings;
- row/column rectangles;
- original art/resource paths;
- font/alignment rules;
- click, drag/drop or navigation mappings.

Those remain open Gate-13 presentation/resource work.

## Gate 13 consequence

The Squad data seam now has an instruction-backed ordered-roster and
active/substitute-state contract. This narrows the backend-to-presentation
boundary without pretending that the original Squad screen itself has been
recovered.
