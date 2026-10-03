# Gate 14 FastView TeamTable static raster slice

_Status: descendant Gate-14 work-ahead. Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

The TeamTable art-loader boundary provides the exact decoded original name-grid
and energy-bar resources. This checkpoint consumes that bundle together with
retained PlayerRow render plans and produces a real transparent 800x600 pixel
plane for only the static row art whose raster behavior is already source-safe.

It does not guess dynamic bar clipping/resizing or text rasterization.

## Rasterized layers

For every retained PlayerRow render plan, the plane draws exactly two full-size
source assets in plan order:

1. the selected 259x16 name-grid resource at the recovered row name-grid rect;
2. the side-specific 82x16 static energy-bar resource at the recovered full bar rect.

The existing source rules determine which assets are selected:

- side 0 rows 0..10: team_name_grid.444;
- side 0 rows >=11: team_name_grid_2.444;
- side 1 rows 0..10: team_name_grid_3.444;
- side 1 rows >=11: team_name_grid_4.444;
- side 0 static energy layer: blank_bar.444;
- side 1 static energy layer: team_bar_2.444.

Rows retain the exact side origins and 17-pixel vertical step already encoded
by the PlayerRow render plans.

## Deliberate fidelity boundary

The resulting FastViewTeamStaticRaster records all of these as false:

- dynamic_energy_rasterized;
- text_rasterized;
- complete_team_table.

The dynamic energy PictureControl is not rasterized yet. Source research has
closed the energy value-to-width transform, but the exact generic PictureControl
source-rectangle behavior when its destination width changes remains a separate
pixel-level boundary. The port therefore does not choose clipping versus
scaling by assumption.

PlayerRow text is likewise excluded from this plane even though semantic text
values are retained. Font/color/localization pixel ownership belongs to the
later text raster layer.

## Integrity and failure behavior

The plane:

- is exactly 800x600 RGBA;
- records the retained side-index / row-index identities;
- requires exactly two source layers per row;
- rejects duplicate row identities;
- rejects source geometry that no longer matches the decoded art;
- SHA-256 guards the emitted RGBA payload;
- preserves transparent pixels outside the static source rectangles.

Focused tests cover side 0/side 1 resources, row-11 alternate-grid transition,
independence from dynamic energy width, duplicate/geometry failure, and the
empty retained-row case.

## Next boundary

After the loader and static raster are hosted-CI verified, the shortest
source-backed path is to attach this TeamTable static plane to the existing
FastView component raster set as another independent plane. Cross-component
flattening should remain unavailable until original child draw-list order is
proved.
