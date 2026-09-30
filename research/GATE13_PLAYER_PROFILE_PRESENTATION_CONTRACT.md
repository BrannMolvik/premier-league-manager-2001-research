# Gate 13 Player Profile Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes the already recovered DBTPlayers / DBRPlayer runtime
identity into the Gate-13 read-only presentation seam. It does not claim the
original Player Profile screen class, attribute layout, icons or navigation.

## Backend identity

Persisted executable research identifies:

- `DBTPlayers` vtable around `0x7BDA78`;
- global DBTPlayers object `0x875638`;
- player-record accessor around `0x416F90`;
- `DBRPlayer` vtable around `0x7BDEDC`;
- runtime record size `0x250` bytes = 592 bytes;
- large binary/save reader around `0x416210`;
- compact Master.dat importer `0x418B90`.

The vtable/accessor/reader addresses were historically recorded as approximate
anchors. The contract therefore keeps the `*_anchor_va` naming. A future
private-byte PE canary may tighten them, but this checkpoint does not.

## Paired 17-byte runtime vectors

The DBRPlayer runtime/save reader contains adjacent 17-byte vectors:

- current live skills: `+0x1E..+0x2E`;
- development targets: `+0x2F..+0x3F`.

Later simulation research has independently established the first as current
skills and the second as development targets rather than a hard invariant
ceiling.

The existing player-profile presentation view exposes the current 17-byte vector
because it is recovered live player state. It deliberately excludes the
development-target vector because original Player Profile visibility of those
bytes has not been proven.

## Read-only profile projection

The existing `player_profile()` seam also exposes already reconstructed source
identity and runtime fields such as source names, club/nationality identity,
date of birth, shirt number, body dimensions, preferred positions, condition,
form, morale, wage/contract and recovered player status state.

This contract does not assert that every such field was visible simultaneously
or at a particular position in the original profile screen.

## Explicit non-claims

The contract contains no:

- original Player Profile screen class or numeric screen ID;
- attribute column labels or icon mappings;
- claim that English.str's player/scouting labels define profile column order;
- row/column coordinates;
- art/resource paths;
- font/color/alignment rules;
- click targets or navigation edges.

## Gate 13 consequence

Player-profile presentation now has a source-backed runtime identity and a clear
boundary between current skills and deliberately hidden development targets.
The original profile screen presentation remains open.
