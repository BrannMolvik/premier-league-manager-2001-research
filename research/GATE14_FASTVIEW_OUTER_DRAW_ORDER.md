# Gate 14 FastView outer draw-array order

_Status: source-backed outer-array checkpoint; Gate 13 remains Codex-owned until its audit releases the lock._

## Result

The canonical executable now source-closes the complete **outer**
FastViewPanel draw-array registration sequence reached by the recovered setup
path.

The generic parent appends controls to its `+0x1C/+0x38` draw array and the
renderer traverses that array forward. Recovery 284 corrects the outer inventory after constructor cross-checks found three builder-owned visible families missed by the first direct-call pass: `GoalFlash`, `ScoreCompositeMain`, and `SurfacedPictureControl@FastViewPanel`. The outer FastViewPanel contains exactly
36 registrations in this source order:

1. full-surface `SurfacedPictureControl@FastViewPanel`;
2. top-bar PictureControl;
3. ticker PictureControl;
4. ClockControl's nested TextControl;
5. embedded control at parent `+0x388`;
6. embedded control at parent `+0x3D4`;
7-16. ten GoalFlash TextControls, five for each of two flash records;
17-21. the five base controls of the single `ScoreCompositeMain` instance;
22-23. two top-corner `SurfacedPictureControl@FastViewPanel` objects;
24-27. four PossessionDiagram PictureControls;
28-30. three PossessionFigures TextControls;
31. direct TextControl at `(250,45)-(550,75)`;
32. direct TextControl at `(250,70)-(550,86)`;
33. FastViewScores SubPanelControl;
34. FastViewTeam SubPanelControl;
35-36. two post-team embedded controls at parent `+0x424/+0x478`.

This is stronger than the earlier raster-family subsequence. It proves where
non-rasterized controls such as the clock and four embedded controls sit
relative to the score/team subpanels.

## Source anchors

SurfacedPictureControl:

- RTTI final vtable `0x7CA974` =
  `.?AVSurfacedPictureControl@FastViewPanel@@`;
- constructor `0x526940` appends itself to its supplied parent through
  `0x5269E5 -> 0x5274C0`;
- owner call `0x51FD31` supplies the outer FastViewPanel and rectangle
  **(0,0)-(800,600)** before the top-bar PictureControl;
- owner calls `0x520642` and `0x520697` supply the outer FastViewPanel
  and rectangles **(38,1)-(173,94)** / **(627,1)-(762,94)** after the
  ScoreCompositeMain branch and before PossessionDiagram.

The remaining constructor-like calls in the bounded outer setup were checked for parent forwarding as well as direct generic append/Picture/Text construction. GoalFlash was the one deeper forwarding case: its child constructor creates the ten controls above. The remaining helpers are data/receiver/list paths in this boundary and do not add another visible outer child.

Direct PictureControl calls:

- top bar: `0x51FDA3 -> 0x527730`;
- ticker: `0x51FE31 -> 0x527730`.

ClockControl:

- owner constructs ClockControl at `0x51FE7B -> 0x51EB90`;
- ClockControl constructs its visible TextControl at
  `0x51EC30 -> 0x527960`, passing the FastViewPanel parent.

Embedded pre-possession controls:

- parent `+0x388`: append `0x51FFE5 -> 0x5274C0`, later initialized
  through `0x520061 -> 0x652FD0`;
- parent `+0x3D4`: append `0x52000B -> 0x5274C0`, later initialized
  through `0x52009F -> 0x652FD0`.

GoalFlash:

- owner call `0x5200CB -> 0x51C700` passes the outer FastViewPanel as the
  first constructor argument;
- `GoalFlash::0x51C700` executes a two-iteration child-record loop;
- each child record is constructed by `0x51BE20`, which forwards that same
  outer parent into five generic TextControl constructors at
  `0x51BF51`, `0x51BFDC`, `0x51C067`, `0x51C0F2`, and
  `0x51C180`;
- the five constructor rectangles per flash record are
  `(0,0)-(134,33)`, `(0,0)-(30,33)`, `(0,0)-(30,33)`,
  `(0,0)-(134,33)`, and `(0,0)-(160,33)`.

Because the child loop executes twice, GoalFlash contributes ten direct
FastViewPanel TextControls. They are appended after the two pre-possession
embedded buttons and before ScoreCompositeMain.

ScoreCompositeMain:

- exactly one branch constructs the object at `0x520356 -> 0x51B400`,
  `0x520416 -> 0x51B330`, or `0x5204D6 -> 0x51B330`;
- each branch passes the outer FastViewPanel as constructor argument 1;
- both constructors flow through shared `ScoreComposite::0x51A730`;
- that base appends one PictureControl at `0x51A825` followed by four
  TextControls at `0x51A8C1`, `0x51A93C`, `0x51A9D2`, and
  `0x51AA83`.

These five controls therefore belong directly to the outer draw array and are
created after the two embedded pre-possession controls but before
PossessionDiagram. The earlier direct-call checkpoint omitted this builder-owned
visible family; this document intentionally records the correction rather than
hiding the chronology.

PossessionDiagram's owner call `0x5206CD` creates four PictureControls, in
order, at `0x522894`, `0x52291D`, `0x5229AA`, and `0x522A33`.

PossessionFigures' owner call `0x520802` creates three TextControls, in
order, at `0x51E876`, `0x51E900`, and `0x51E990`.

Two additional direct TextControls are then created at `0x520A16` and
`0x520A69`.

The already source-closed nested-panel wrappers are appended next:

- FastViewScores wrapper: `0x520DEF`;
- FastViewTeam wrapper: `0x520EEF`.

Finally, the loop at `0x520F8B` executes exactly twice. It appends the
embedded controls starting at parent `+0x424` with stride `0x54`, yielding
`+0x424` and `+0x478`; each later uses constructor path `0x652C50`.

## Fidelity boundary

This checkpoint deliberately does **not** set
`global_fastview_z_order_recovered=true`.

The score and team wrappers synchronously render their own child arrays at
outer ranks 32 and 33 (zero-based). PR #366 subsequently source-closed
**parameterized construction algorithms** inside both wrappers: LeagueTable
heading/row counts, TeamTable base/PlayerRow counts and side order, and the
ScoreCompositeNormal five-control base plus runtime 0-or-2 phase tail.

That is stronger than this document's original boundary, but it is not the same
as an exhaustively reconciled visible inventory. Current renderer contracts
still prove that nested pixels are partial:

- score/table static planes carry `text_rasterized=false` and
  `complete_component=false`;
- the retained PlayerRow compositor carries `complete_team_table=false`;
- TeamTable has six table-level controls in addition to each PlayerRow subtree.

Therefore:

- outer FastViewPanel order: recovered;
- score/team parameterized nested construction: recovered;
- modeled raster-family relative order: recovered;
- exhaustive FastViewScores visible inventory/pixels: still false;
- exhaustive FastViewTeam visible inventory/pixels: still false;
- global FastView z-order: still false;
- complete FastView frame: still false.

## Next source task

Continue from the known omitted nested families rather than rerunning the
already-closed count formulas. Source-bind/rasterize the remaining visible
FastViewScores/LeagueTable text and other omitted score-subpanel controls, plus
the TeamTable-level controls outside the already complete retained PlayerRows.
Only after those inventories are reconciled should the global FastView z-order
claim be reconsidered. Runtime phase chronology, pixel-format/blend output and
3D choreography remain separate blockers.
