# Gate 14 nested FastView draw-order algorithms

_Status: source-backed nested-order checkpoint; Gate 13 remains the earliest incomplete validation gate._

The outer FastViewPanel order is already canonical as 36 registrations. This checkpoint closes why the two nested wrappers still cannot be flattened into one immutable global list.

## FastViewLeagueScores

`LeagueTableComposite::0x51E000` derives displayed row count from source count `N`:
- `N <= 12`: displayed rows = `N`;
- `N > 12`: displayed rows = `ceil(N/2)`.

Its heading constructor contributes **8 visible controls**: one PictureControl plus seven TextControls. Each row constructor contributes **10 controls**: one PictureControl plus nine TextControls. Therefore the league-table contribution is:

`8 + 10 * displayed_rows`.

`FastViewLeagueScores::0x523CC0` dynamically creates `ScoreCompositeNormal::0x51B740`. Its shared base `0x51A730` contributes **5 static controls**.

Phase helper `0x51BA30` first calls clear helper `0x51BBE0`, destroying any previous phase PictureControl/TextControl pair, then appends a new PictureControl followed by TextControl to the current parent tail. Thus one score composite has **5 static controls plus 0 or 2 runtime phase-tail controls**, and repeated phase changes reappend the pair at a later mutation generation.

## FastViewTeam

`FastViewTeam` creates side-0 and side-1 TeamTables at `0x524C4F` and `0x524DBB`.

`TeamTable::0x524EC0` contributes **6 table-level controls**. It then constructs 11 PlayerRows unconditionally and continues constructing rows while the source player count exceeds 11. Therefore:

`player_rows = max(11, source_player_count)`.

`PlayerRow::0x525DB0` contributes **9 visible controls** in order: one PictureControl, six TextControls, then two PictureControls. Each TeamTable therefore contributes:

`6 + 9 * max(11, source_player_count)`.

## Fidelity boundary

These formulas close nested child-array construction without guessing fixed squad or fixture counts. They also prove the score subtree has event-driven tail mutation. Therefore a single constructor-only total z-order is not yet an honest global FastView order. Runtime score-composite creation chronology and phase-event chronology must be carried into any final flattened frame audit.

This checkpoint keeps `global_fastview_z_order_recovered=false` and `complete_fastview_frame_recovered=false`.
