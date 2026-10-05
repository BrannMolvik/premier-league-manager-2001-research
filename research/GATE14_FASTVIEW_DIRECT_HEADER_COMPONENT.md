# Gate 14 direct FastView header component integration

_Status: disjoint Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Integration boundary

The source-closed `direct_header_text` raster is lifted as one transparent
FastView component plane containing the two direct outer TextControls.

The already recovered outer FastViewPanel registration order places those
controls:

1. after all three `possession_figures_text` controls;
2. before the `scores_subpanel` wrapper;
3. before the later `team_subpanel` wrapper.

The resolved-only compositor therefore orders the aggregate header plane after
`possession_figures_text` and before all score/table/team subpanel planes.

## Fail-closed overlap behavior

This checkpoint does not use the recovered outer order as permission to flatten
cross-component pixels. The existing resolved-only compositor still copies a
pixel only when exactly one component owns it. Any overlap involving
`direct_header_text` remains transparent in the resolved preview and is
recorded in the unresolved-overlap mask/topology.

This preserves the distinction between:

- source-backed draw registration order; and
- the still incomplete native packed-pixel/output-format overlap boundary.

## Promoted facts

- exact component identity: `direct_header_text`;
- exact two-source-layer raster lift;
- outer-order placement after possession figures and before score planes;
- contributor ordering in overlap topology.

## Still false

- automatic binding of every header field from modern runtime state;
- generic cross-component overlap resolution;
- flattened complete FastView frame;
- Gate 14 completion.

## Next step

After this integration is verified, continue the highest-value remaining
FastView presentation gap from the canonical Gate-14 readiness state rather
than reopening these direct header controls.
