# Gate 14 FastView TeamTable component plane

_Status: independent Gate-14 work-ahead while Gate 13 remains the earliest incomplete validation gate and is exclusively Codex-owned._

## Purpose

The existing FastView frame plan already carries three separate source-backed
800x600 raster planes:

1. direct FastView chrome;
2. PossessionDiagram;
3. PossessionFigures text.

The TeamTable work now provides a fourth independently verified source plane
without inventing unresolved cross-component z-order.

## Source boundary

The TeamTable plane is built from the already recovered PlayerRow render plans
and checksum-gated original TeamTable art.

For each retained PlayerRow, the static raster contains only:

- the source-selected 259x16 name-grid PictureControl;
- the source-selected 82x16 full-size static energy-bar PictureControl.

It deliberately does not rasterize:

- dynamic energy-bar destination resizing;
- PlayerRow text cells;
- any cross-component overlap order;
- unrelated score/composite pixels.

The source raster may legitimately contain zero layers when no PlayerRows were
retained. This remains an empty transparent TeamTable plane rather than a
synthetic row set.

## Integration

`FastViewComponentRasterSet` now optionally accepts a
`team_table_static` plane. Existing lower-level callers that only need the
previous three components remain valid.

The actual frame-plan path is stricter:

- `build_fastview_frame_plan(...)` requires exact
  `OriginalFastViewTeamArt`;
- it reconstructs no gameplay state and consumes no RNG;
- it rasterizes the TeamTable only from the shell's already validated retained
  PlayerRow render plans;
- it attaches the resulting fourth plane to the immutable frame plan.

The completed-human adapter passes the same exact TeamTable art through this
one-way presentation path.

## Fidelity guard

This checkpoint still requires:

- `cross_component_z_order_recovered == False`;
- `flattened_frame_available == False`;
- `complete_raster_frame == False`;
- `audio_ready == False`;
- `choreography_3d_ready == False`.

It therefore improves original-pixel coverage without claiming a complete
FastView frame.

## Validation

Hosted reconstruction coverage includes:

- TeamTable static raster;
- TeamTable art loader;
- component-raster fourth-plane conversion;
- frame-plan attachment;
- completed-human adapter attachment;
- valid zero-row transparent TeamTable plane;
- rejection of unresolved complete-frame promotion.

The local execution sandbox is still unavailable with process-start
`caas.internal.errors.ClientError`, so hosted GitHub Actions remains the
authoritative execution path for this checkpoint.

## Next boundary

After this change is verified and merged, the highest-value Gate-14 tasks are:

1. player-visible Windows consumption of the separate source-backed planes
   without guessing unresolved overlap order;
2. original audio-bank/menu-sound ownership once the private executable trace
   can run again;
3. remaining ScoreComposite/3D presentation fidelity needed for a recognizably
   original match workflow.
