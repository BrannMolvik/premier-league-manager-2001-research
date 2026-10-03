# Gate 14 FastView TeamTable bar source trace

_Date: 3 October 2026 KST. Recovery 197. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Correction

Earlier Gate-14 notes grouped `team_bar_1.444`, `blank_bar.444`, and
`team_bar_2.444` under `PossessionFigures`. Fresh bounded RTTI and constructor
tracing proves that ownership was wrong.

`PossessionFigures` is the separate three-text-control class built by
`0x51E7E0` and updated by `0x51EA80`. The three 82x16 bar images flow through
`FastViewPanel::FastViewTeam::TeamTable::Row`.

The correction does not invalidate the four PossessionDiagram assets or the
PossessionFigures percentage text rectangles recovered in Recoveries 195-196.

## RTTI / constructor chain

The canonical image proves:

- `FastViewPanel::FastViewTeam`
  - constructor: `0x524A20`
  - vftable: `0x7CA888`
  - type descriptor: `0x8299D8`
- `FastViewPanel::FastViewTeam::TeamTable`
  - constructor: `0x524EC0`
  - vftable: `0x7CA950`
  - type descriptor: `0x829B50`
- `FastViewPanel::FastViewTeam::TeamTable::Row`
  - constructor: `0x525DB0`
  - vftable: `0x7CA968`
  - type descriptor: `0x829A78`

The three full resource strings are copied by `0x524A20` into the two
TeamTable configurations and then consumed by Row constructor `0x525DB0`.

## Exact row resource pairing

For source side index 0, `0x524A20` supplies:

- third row image string: `FM2001_Art/FastView/team_bar_1.444`
- fourth row image string: `FM2001_Art/FastView/blank_bar.444`

For source side index 1, it supplies:

- third row image string: `FM2001_Art/FastView/blank_bar.444`
- fourth row image string: `FM2001_Art/FastView/team_bar_2.444`

`0x525DB0` stores the third-string control at Row `+0x38` and the
fourth-string control at Row `+0x3C`; both use the same rectangle. The side
index is stored at Row `+0x40`.

The dynamic row-bar routine at `0x526680` operates on the `+0x38` control
and branches on the Row `+0x40` side flag. This explains why the two source
sides reverse which of the colored/blank images occupies the dynamic slot. The
higher-level gameplay meaning of that width update is deliberately not named
until its receiver predicate is separately closed.

## Exact geometry

`TeamTable` creates exactly **11 rows**. The per-row step is **17 pixels**.

Both source bar files and the blank bar are 82x16 EA444 images. The Row image
controls use the full 82x16 dimensions:

- side index 0: x **309..391**
- side index 1: x **409..491**
- row 0: y **27..43**
- row `n`: y **27 + 17*n .. 43 + 17*n**
- row 10 therefore ends at y **213**

`reconstruction/gate14_fastview_teamtable.py` materializes this exact
side-indexed row geometry and resource pairing while keeping human-user
orientation and dynamic-update semantics neutral.

## Source assets

The three exact originals are now staged byte-identically under
`original_assets/source/FM2001_Art/FastView/`:

| Path | Bytes | Dimensions | SHA-256 |
| --- | ---: | ---: | --- |
| `team_bar_1.444` | 2,344 | 82x16 | `edd35c18a53598b3cfd3e93adc2b27153742582d7888a0923fdd672d36e2681d` |
| `blank_bar.444` | 2,776 | 82x16 | `961eb49ae0810a522130f4b6e7401c7d16250d0de65bc7e51bc8341c6b8a7e3a` |
| `team_bar_2.444` | 2,312 | 82x16 | `4514b621f8d6a7b41c82c5215c4a1af571f60d773f0a3d1ea095c87d62e8a751` |

## Remaining boundary

This checkpoint does **not** claim:

1. that side index 0 or 1 is the human user's screen side;
2. the gameplay semantic bound to `0x526680` until the receiver/caller chain is
   explicitly closed;
3. FastView audio/commentary bindings;
4. 3D/SCI choreography;
5. Gate 14 completion.

Gate 13 remains the earliest incomplete validation gate because the real
Windows schema-8 management receipt is still external.
