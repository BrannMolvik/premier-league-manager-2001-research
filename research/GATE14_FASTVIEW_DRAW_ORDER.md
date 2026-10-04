# Gate 14 source-closed FastView raster-family draw order

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

The current source audit closes a **partial** native order across the raster
families:

1. `direct_chrome`;
2. `possession_diagram`;
3. `possession_figures_text`;
4. the FastViewScores wrapper, containing both `league_scores_static` and
   `league_table_static` but with no aggregate pairwise order between those
   two planes;
5. `team_table_static` or `team_table_energy`.

The earlier total-order claim between the two score-wrapper raster planes has
been withdrawn.

The two TeamTable names are alternative reconstruction views of the same native
TeamTable position. They are not two native siblings and therefore are not
ordered against each other.

This result is deliberately narrower than a global FastView z-order. Omitted or
unbound source layers remain outside the relation, including the rejected loose
800x600 background. Cross-component blend behavior also remains unresolved.

## Revalidated private source

The authorized Library ZIP was materialized again at exactly **511,121,336
bytes**. The raw MODE1/2352 image was recovered and the root
`footballmanager.exe` extracted directly from the Joliet filesystem.

The executable SHA-256 revalidated as:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

No executable bytes or private disassembly are committed.

## Generic child-order contract

Generic PictureControl constructor `0x527730` registers through
`0x52782A -> 0x5274C0`. Generic text-control constructor `0x527960`
registers through `0x527A15 -> 0x5274C0`.

The parent stores:

- child pointer array at `+0x1C`;
- child count at `+0x38`.

Append helper `0x5275C0` preserves existing indices and writes a new child at
the old count. Generic traversal `0x6533A0` walks index 0 through count-1 and
dispatches visible children through virtual offset `+0x64`.

This is the previously verified basis for
`possession_diagram -> possession_figures_text`.

## Recovery 275: SubPanelControl render bridge

The missing boundary was how nested FastView panels participate in the outer
FastViewPanel traversal.

RTTI identifies vtable `0x7CA5E4` as
`SubPanelControl@FastViewPanel`. Constructor/setup routine `0x650B20`
stores its target panel pointer at wrapper offset `+0x2C`.

The wrapper's normal `+0x64` render slot is `0x650BB0`. During that render
path, callsite `0x650BFF` invokes the same generic traversal `0x6533A0` on
the stored target panel.

Therefore a SubPanelControl is not merely an ownership wrapper. It occupies one
position in the outer parent's forward draw array, and at that exact position it
synchronously renders the owned panel's own forward child array.

### Score subtree before team subtree

FastViewPanel stores the selected FastViewScores object at `+0x90`. Its
SubPanelControl is appended to the outer draw array at
`0x520DEF -> 0x5274C0` and stored at `+0x98`.

FastViewTeam is then constructed at
`0x520E67 -> 0x524920` and stored at panel `+0x94`. A second
SubPanelControl targeting that object is appended later at
`0x520EEF -> 0x5274C0` and stored at `+0x9C`.

Because the outer array is append-order and forward-traversed, the complete
FastViewScores subtree paints before the FastViewTeam subtree.

This relation does not rely on their overlapping rectangle or allocation
addresses.

## Ordering inside the score subtree: aggregate edge withdrawn

Fresh canonical-executable tracing shows that the earlier simplified relation
was incomplete.

`FastViewLeagueScores::0x523370` calls the generic source-entry builder at
`0x5233C2 -> 0x522CD0` **before** constructing LeagueTableComposite.
The class vtable slot `+0x5C` is `0x523CC0`, so that builder creates one
ScoreCompositeNormal per source entry. Each ScoreComposite registers its
five static controls into the same FastViewScores child array before the
LeagueTable constructor at `0x523472 -> 0x51E000`.

Later in the same setup, additional league-score-owned controls are appended
after the LeagueTable block. In particular, the call at `0x523554` uses
`title_bar_22.444`, not `current_fix_grid_1.444`; the actual
`current_fix_grid_1.444` reference appears later at `0x5239AB` and is
constructed at `0x5239F3`. Event-driven ScoreComposite phase controls may
also be cleared and re-appended later.

Therefore the aggregate `league_scores_static` plane spans native positions
both before and after `league_table_static`. A single pairwise relation
between those two aggregate raster planes would be false. The source contract
now deliberately exposes **no relation** for that pair while retaining the
proven order from the outer score wrapper to the later team wrapper.

## Phase-specific score order

The aggregate score/table boundary above remains the compatibility contract for
the historical `league_scores_static` plane. A newer source-backed raster
split can be more precise without assigning that aggregate plane a false
position.

For the phase-specific LeagueScores planes, the source-closed order is:

1. `league_scores_early_rows_static`;
2. `league_table_static`;
3. `league_scores_late_grid_static`;
4. `league_scores_runtime_phase_icons`;
5. the later FastViewTeam wrapper.

The first three score/table positions come from constructor append order:
ScoreComposite factory calls begin at `0x5233C2`, LeagueTable is constructed
at `0x523472`, and the verified current_fix_grid_1 PictureControl is appended
at `0x5239F3`.

The runtime phase-icon plane is different: phase helper `0x51BA30` first
removes the old phase pair through `0x51BBE0`, then appends the replacement
PictureControl/TextControl pair at the FastViewScores parent array's current
tail. The raster phase contains only the icon pixels; paired phase text remains
unrasterized.

These phase-specific relations do **not** make
`league_scores_static <-> league_table_static` valid. They exist precisely
because the aggregate score plane spans multiple native positions.

## Direct FastViewPanel controls precede both subpanels

The directly bound top bar and ticker PictureControls are created at
`0x51FDA3` and `0x51FE31`. PossessionDiagram follows at
`0x5206CD`, and PossessionFigures at `0x520802`. All of these visible
controls are registered before the later score SubPanelControl at `0x520DEF`
and team SubPanelControl at `0x520EEF`.

Combining the direct append order, the subpanel wrapper positions, and each
wrapper's synchronous nested traversal yields the modeled raster-family order
listed above.

## Reconstruction contract

`reconstruction/gate14_fastview_draw_order.py` exposes pairwise relations for
every pair at different levels of the recovered modeled order.

Each relation records whether its proof is:

- one shared parent draw array; or
- a recovered nested SubPanelControl traversal bridge.

A relation still hard-fails if either component is unmodeled, if both names are
the static/energy aliases of the same TeamTable native position, or if the two
names are identical.

The contract continues to forbid promotion of:

- `pixel_blend_rule_recovered`;
- `global_z_order_recovered`.

## Fidelity boundary

The result does **not** establish:

- global ordering for unmodeled or unbound FastView layers;
- the native cross-component alpha/destination blend equation;
- a complete flattened frame;
- ownership of `FM2001_Art/FastView/background.444`;
- audio/commentary behavior;
- 3D choreography.

The resolved-only compositor therefore keeps every multi-contributor pixel
masked. Groups that contain both aggregate score/table planes retain a
cross-component draw-order blocker until those planes are split by native draw
phase. Other source-closed pairwise relations remain available. Blend evidence
remains independently required before any overlap pixel can be emitted.
