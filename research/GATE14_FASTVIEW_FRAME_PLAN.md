# Gate 14 FastView frame plan

_Status: independent Gate-14 work-ahead; Gate 13 remains the earliest incomplete validation gate under the active Codex ownership lock._

Recovery 225 introduces one immutable renderer-input boundary after the already
source-backed presentation seams.

`gate14_fastview_frame_plan.py` combines:

- one exact `FastViewSemanticShell`;
- the shell's retained `FastViewPlayerRowRenderPlan` tuple;
- the fail-closed 800x600 `FastViewPartialSurfaceLayout`.

The builder does not reconstruct gameplay state. Before composing the frame plan
it re-derives each retained PlayerRow render plan from its retained snapshot and
rejects count or content drift. The partial surface is then driven by those same
validated render plans, removing a second manual TeamTable row-selection path.

The resulting frame plan explicitly keeps all unresolved fidelity boundaries
false:

- `complete_raster_frame = False`;
- `audio_ready = False`;
- `choreography_3d_ready = False`;
- partial-surface raster composition and complete-frame flags remain false.

No localization result is invented, no generic TeamTable text pixels are
rasterized, no cross-component z-order is assigned, and no simulation/RNG,
gameplay controller, audio, or commentary module is imported.

This advances Gate 14 toward a single player-visible presentation input while
remaining evidence-bounded. It is not a Gate-14 completion claim.
