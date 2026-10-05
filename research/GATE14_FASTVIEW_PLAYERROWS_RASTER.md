# Gate 14 complete retained PlayerRow raster

_Status: dependent Gate-14 work-ahead; Gate 13 remains Codex-owned._

## Result

The retained PlayerRow controls can now be combined into one source-backed
800x600 row raster for the canonical English release.

Inputs are the already-verified:

- dynamic TeamTable energy raster, including name-grid and static/dynamic bar
  PictureControls;
- complete English PlayerRow text raster.

The result is deliberately named around **retained PlayerRows**, not the whole
TeamTable or FastView frame.

## Native control order

Private canonical-executable tracing closes the Row constructor sequence:

1. name-grid PictureControl at `0x525E7F`;
2. six text controls, first call `0x525F1A` through final call
   `0x526244`;
3. static energy PictureControl at `0x5262E6`;
4. dynamic energy PictureControl at `0x526351`.

The previously source-closed generic child registration appends controls, and
the renderer traverses that array forward. This is therefore the native
per-row paint order.

## Safe composition simplification

The source geometry places every text rectangle outside the energy-bar
rectangle for both side layouts. Text overlaps the name-grid art, but the
name-grid is natively constructed first. Energy bars are constructed after the
text, but they are disjoint from every text rectangle.

Therefore applying the complete text plane over the already-composed
name-grid/energy raster is pixel-equivalent to native order for these retained
controls. The compositor verifies the disjointness for every supplied render
plan and fails closed if it ever changes.

## Fidelity boundary

`gate14_fastview_playerrows_raster.py` requires:

- exact energy and text raster types;
- identical retained row identities;
- an exact rendered-cell set matching every written text instruction;
- no unresolved text cells;
- text/bar rectangle disjointness.

It records:

- `native_row_control_order_recovered=true`;
- `text_energy_rectangles_disjoint=true`;
- `complete_retained_player_rows=true`.

It keeps:

- `complete_team_table=false`;
- `complete_fastview_frame=false`.

This checkpoint does not add non-row TeamTable presentation, global FastView
z-order, background ownership, audio, or 3D choreography.


## Canonical completed-human frame integration

The source-closed retained PlayerRows raster is now the TeamTable view carried
by `build_fastview_frame_plan()` and therefore by both completed-human frame
adapters. The older energy-only raster remains a useful intermediate artifact,
but it is no longer the final TeamTable plane attached to a normal human
FastView frame.

The component identity is:

`team_table_player_rows`

It occupies the exact same native FastViewTeam/TeamTable paint position as the
existing `team_table_static` and `team_table_energy` reconstruction views.
Those names are aliases for alternative fidelity views of one native subtree,
not separate siblings. The partial draw-order model therefore exposes no
pairwise ordering relation among the three aliases.

Each retained row contributes exactly nine constructed native controls to this
plane:

1. one name-grid PictureControl;
2. six TextControls;
3. one static energy-bar PictureControl;
4. one dynamic energy-bar PictureControl.

The frame builder rasterizes the verified dynamic-energy view, rasterizes all
source-closed English PlayerRow text from the provenance-tracked Zurich 16px
font under the runtime application root, composes those already-proven planes,
and only then hands the complete retained-row plane to the component model.

This integration promotes no broader completeness. The six non-row TeamTable
controls remain outside the retained PlayerRows raster, so
`complete_team_table=false` and `complete_fastview_frame=false` remain
mandatory. Cross-component overlap pixels also retain the existing native-blend
blocker.
