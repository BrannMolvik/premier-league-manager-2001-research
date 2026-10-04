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
