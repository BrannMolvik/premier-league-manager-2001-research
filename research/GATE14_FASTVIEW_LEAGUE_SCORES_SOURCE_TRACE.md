# Gate 14 FastViewLeagueScores current-fixture trace

_Date: 3 October 2026 KST. Recovery 204. Evidence tier: canonical executable plus first-hand authorized source-disc bytes._

## Class ownership

Canonical MSVC RTTI maps primary vtable `0x7CA750` and receiver/subobject
vtable `0x7CA744` to
`.?AVFastViewLeagueScores@FastViewPanel@@`.

The FastView owner constructs the league-scores object on the league branch,
finishes the primary vtable at `0x7CA750`, stores the object, then immediately
invokes virtual slot +4 at `0x520D82`. That slot is method `0x523370`.

## current_fix_grid_1 direct binding

Method `0x523370` directly constructs the league current-fixture grid:

- source path: `FM2001_Art/FastView/current_fix_grid_1.444`;
- path literal VA: `0x829920`;
- local source-string setup: `0x5239AB`;
- generic PictureControl call: `0x5239F3 -> 0x527730`;
- source bytes: **3,704**;
- EA444 dimensions: **309x19**;
- SHA-256:
  `bdd2fe25884e8ce72e21bd7b9296c65827ce90ea058c6f43e2f727f2bae19057`;
- exact **FastViewLeagueScores owner-local** rectangle:
  `(38,32)-(347,51)`.

The 309x19 source size exactly matches that owner-local rectangle. The parent
itself begins from the generic FastViewScores 0,0,1,1 construction path and can
participate in later layout handling, so this checkpoint intentionally does
not promote the child rectangle to screen-absolute coordinates.

## current_fix_grid_2 boundary

The authorized source file
`FM2001_Art/FastView/current_fix_grid_2.444` is separately recovered:

- path literal VA: `0x828ED0`;
- bytes: **4,060**;
- dimensions: **309x16**;
- SHA-256:
  `ffc53c7b5fc9aa8c11053d704c4232505528577bfb9675fa7a4a2985e8e4ec2e`.

It is consumed by `ScoreCompositeNormal` constructor `0x51B740`, whose final
RTTI is `.?AVScoreCompositeNormal@@`. The constructor passes the path and a
layout structure into shared ScoreComposite construction at `0x51B79A ->
0x51A730`; that shared routine later creates the PictureControl.

The exact layout-structure transform for this grid has not yet been reduced to
a stable owner-local/screen rectangle. Therefore grid 2 is ownership- and
source-identity-proven but **not renderable** in this checkpoint.

## Reconstruction boundary

`reconstruction/gate14_fastview_league_scores.py` records the class/method
identity, exact grid-1 source identity, and owner-local rectangle. It also keeps
grid 2 as an explicit ownership-only resource with
`owner_local_rect=None`.

`reconstruction/original_fastview_league_scores_art.py` exposes only grid 1
and marks both screen-absolute placement and grid-2 geometry unrecovered.

As with Recovery-204 top/ticker chrome, the exact source bytes are currently
outside Git because this execution path lacks a binary-safe container-file
handoff to the GitHub connector. No replacement or re-encoded artwork is used.

## Next source task

Decode the `ScoreCompositeNormal` layout structure passed into `0x51A730`
far enough to recover the exact placement of `current_fix_grid_2.444` and its
associated score text controls. Do not infer coordinates from the 309x16 bitmap
size.

Gate 13 remains the earliest incomplete validation gate pending the external
schema-8 Windows receipt.
