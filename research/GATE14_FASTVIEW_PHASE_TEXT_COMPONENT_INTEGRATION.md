# Gate 14 runtime phase text component and overlap integration

_Status: independent Gate-14 work-ahead while Gate 13 Fixtures paging remains the earliest incomplete validation gate._

## Result

The separately rasterized ScoreComposite runtime phase-label plane is now
carried through the same component and unresolved-overlap accounting used by
the other FastView planes.

The new component identity is:

`league_scores_runtime_phase_text`

It is distinct from:

`league_scores_runtime_phase_icons`

The two runtime families deliberately occupy the **same source-order level**.

## Why the same order level is required

The original per-row phase callback appends its phase icon and then its phase
text for that ScoreComposite row.

What remains unresolved is the global callback order across different
ScoreComposite rows. Therefore a flattened aggregate sequence such as:

`all runtime icons -> all runtime text`

or:

`all runtime text -> all runtime icons`

would be unsupported.

The source-backed aggregate relation is only:

`league_scores_late_grid_static -> {runtime icons, runtime text} -> TeamTable`

No pairwise icon/text edge is exposed.

## Component raster integration

`FastViewComponentRasterSet` now accepts an optional
`league_scores_runtime_text` plane.

The plane:

- must retain component identity `league_scores_runtime_phase_text`;
- may be fully transparent when no visible phase labels are active;
- may only be supplied alongside the already verified phased LeagueScores
  evidence;
- cannot coexist as a substitute for aggregate score evidence;
- cannot promote cross-component z-order or a flattened FastView frame.

`build_fastview_component_rasters(..., score_phase_text=...)` lifts the exact
phase-text raster without changing its bytes, source-layer count, or SHA-256.

## Resolved-only overlap accounting

The resolved-only compositor now includes the runtime phase-text plane as an
independent contributor.

This does **not** flatten it with the runtime icon plane. If both contribute at
one pixel, the pixel remains transparent in the resolved-only output and the
overlap mask remains set.

The overlap-readiness audit uses the partial draw-order contract:

- every preceding phased score component is ordered before both runtime
  families;
- both runtime families are ordered before TeamTable;
- runtime icon vs runtime text remains unresolved.

For a six-component overlap containing early rows, LeagueTable, late grid,
runtime icons, runtime text, and TeamTable, 14 of 15 pairwise relations are
source-closed. The only missing relation is icon vs text, so the group retains
both the draw-order and blend blockers.

## Fidelity boundary

This checkpoint does not promote:

- aggregate runtime icon/text order;
- native flattening of icon/text overlap;
- cross-component blend recovery;
- global FastView z-order;
- complete FastView frame;
- recognizable complete match workflow;
- Gate 14 completion.

## Next step

After this checkpoint, the highest-value source question is the runtime
ScoreComposite receiver/callback ordering across rows. If that order can be
closed, the icon/text aggregate ambiguity can be removed. If it cannot, the two
families must remain at one unresolved order level while work continues on
other omitted FastView layers.
