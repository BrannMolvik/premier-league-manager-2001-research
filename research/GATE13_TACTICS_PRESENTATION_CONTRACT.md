# Gate 13 Formation and Team Orders Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes previously recovered primary executable/RTTI and
MatchCalculator evidence for the tactics area into a read-only Gate-13
presentation contract. It does not claim the original tactics artwork, slot
geometry, controls, drag/drop behavior, or navigation.

## PFormation2k identity and persisted formation family

Existing firsthand executable analysis identifies:

- panel class: `PFormation2k`;
- vtable: `0x7C1AB4`;
- DBRUser serialized region: `+0x70C .. +0x10D7`, size `0x9CC`;
- magic: `0x074A3216`;
- five records beginning at DBRUser `+0x714`;
- record size: `0x1F4` bytes;
- record contents include formation/team-sheet names, current-club player IDs
  and assigned-role data.

The arithmetic is exact: five 0x1F4-byte records equal 0x9C4 bytes, plus the
8-byte header equals the full 0x9CC serialized region.

This proves a native five-slot formation/team-sheet family attached to the
original formation panel. It does **not** prove where those records were drawn,
which controls selected them, or how a user edited them on-screen.

## PTeamOrders2K identity

RTTI/source analysis identifies:

- panel class: `PTeamOrders2K`;
- recorded vtable neighborhood anchor: approximately `0x7C6FE0`;
- recorded TypeDescriptor neighborhood anchor: approximately `0x81DE68`;
- source path:
  `Applications\\FootballManager\\SquadPan.cpp`.

Because the existing research records these two RTTI addresses as "around"
rather than as a fresh strict PE canary, the reconstruction contract names them
`*_anchor_va`. They must not be upgraded to hash-gated exact RTTI addresses
until private executable byte execution is available again.

## Four proven Team Orders priority categories

The MatchCalculator consumes four ordered player lists through recovered
club/user helpers. Their semantics are independently established by the actual
selectors/chance paths and corroborated by original English resources:

| Category | Recovered semantics | Corroborating original strings |
| ---: | --- | --- |
| 0 | captaincy order | `Captains`; `Click for captaincy order`; `CAPTAIN` |
| 1 | penalty-taker order | `Penalty Takers`; `Click for penalties order`; `PENALTIES` |
| 2 | corner-kick order | `Corner Kicks (Left)`; `Corner Kicks (Right)` |
| 3 | free-kick order | `Free Kicks (Left)`; `Free Kicks (Right)` |

Category 0 is consumed by the captain selector used in team-strength
calculation. Category 1 is consumed by normal penalties and penalty-shootout
candidate ordering. Category 2 is consumed by the corner chance family.
Category 3 is consumed by the direct free-kick family.

The left/right strings for corners and free kicks are corroboration for the
original Team Orders vocabulary. This checkpoint does not claim that one
category maps one-to-one to either visible left/right widget.

## Reconstruction boundary

`gate13_management_source_data.py` now exposes
`TacticsPresentationContract` alongside the already recovered runtime
`TacticsSelectionView`.

The presentation contract deliberately contains no:

- original screen/control ID;
- button/list rectangle;
- player-slot coordinate;
- formation or Team Orders art path;
- font/color/alignment rule;
- click, drag/drop or reorder gesture;
- navigation edge.

Those omissions are required until source evidence recovers them.

## Gate 13 consequence

The tactics screen is no longer presentation-anonymous: its original formation
and Team Orders panel families plus four ordered semantic categories are locked
into the presentation seam. The Gate-13 tactics visual/navigation resource
coverage remains **open** until the original assets, layout and interaction
bindings are recovered and exercised on Windows.
