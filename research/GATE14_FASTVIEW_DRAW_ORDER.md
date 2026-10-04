# Gate 14 source-closed FastView raster-family draw order

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

Recovery 275 closes the native relative paint order of every component family
currently represented by the resolved-only FastView raster pipeline:

1. `direct_chrome`;
2. `possession_diagram`;
3. `possession_figures_text`;
4. `league_table_static`;
5. `league_scores_static`;
6. `team_table_static` or `team_table_energy`.

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

## Ordering inside the score subtree

FastViewLeagueScores constructs LeagueTableComposite at
`0x523472 -> 0x51E000`. The composite's Heading
(`0x51DCB0`) and Row (`0x51D730`) constructors receive the
FastViewLeagueScores panel as parent, so their visible controls are registered
into that panel's child array.

Only afterward does FastViewLeagueScores create the current-fixture grid
PictureControl at `0x523554 -> 0x527730`, followed by the fixture score
composites.

The generic forward traversal therefore paints
`league_table_static` before `league_scores_static`.

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
masked. The practical change is only that overlap readiness can now identify
draw order as solved for groups made entirely from the currently rasterized
families. Blend evidence remains independently required before those pixels can
be emitted.
