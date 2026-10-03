# Gate 14 score/table frame-plan bridge

_Status: Gate-14 work-ahead on canonical score/table component-plane dependency e9bb5fda._

## Purpose

The FastView frame plan already carries the source-backed chrome,
PossessionDiagram, PossessionFigures and TeamTable planes. The score/table
component checkpoint adds two optional verified planes for current-fixture
graphics and LeagueTable graphics.

This bridge lets an already-built `FastViewScoreTableStaticRasterSet` travel
through the immutable frame-plan path without manufacturing the still-unproven
live inputs needed to build that raster set.

## Contract

`build_fastview_frame_plan()` and
`build_human_fastview_frame_plan()` accept an optional
`score_table_static` argument.

The value is passed unchanged into the component-raster container. Neither
function derives:

- current-fixture source count;
- LeagueTable source count;
- typed phase state;
- page selection;
- score/table text.

Those remain explicit caller responsibilities until their live presentation
binding is source-proven.

The completed-human adapter likewise does not reinterpret
`matchday_results`, `table`, or boundary events as those original UI inputs.

## Fidelity boundary

This does not promote:

- cross-component z-order;
- flattened FastView output;
- complete raster fidelity;
- audio readiness;
- 3D choreography.

The change only removes a renderer-input wiring gap for a raster bundle that
has already been independently verified.

## Validation

Focused tests prove that the frame builder and completed-human adapter forward
the supplied bundle unchanged and do not derive score/table context internally.
The existing full reconstruction workflow is already triggered by modifications
to the frame-plan and human-frame-plan modules.
