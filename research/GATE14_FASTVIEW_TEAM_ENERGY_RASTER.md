# Gate 14 PlayerRow dynamic energy raster

_Status: source-backed Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Result

The PlayerRow energy bar can now be rasterized for the normal source domain
without guessing PictureControl resize behavior.

Private tracing of the canonical executable proves that resized PictureControls
are **cropped, not stretched**.

## Native renderer chain

### Energy rectangle writer

EventPlayerUpdateEnergy callback 0x5267D0 forwards the event value to
0x526680. The existing reconstruction already mirrors its exact rectangle
arithmetic:

- source anchor: energy 58;
- source upper endpoint: 99;
- width transform: 2 * (energy - 58), clamped only above 99 to 82 pixels;
- side 0 dynamic rectangle grows from its left edge;
- side 1 dynamic blank rectangle shrinks, revealing team_bar_2 from the right.

The callback changes the dynamic PictureControl's control rectangle at
+0x08/+0x0C/+0x10/+0x14; it does not rewrite the decoded bitmap resource.

### PictureControl source rectangle

Generic PictureControl render preparation at 0x64E5D0 derives its bitmap
source rectangle from the clipped destination/control geometry.

For the source rectangle it computes:

- source left from the original bitmap position plus
  (clipped_left - control_left);
- source top from the original bitmap position plus
  (clipped_top - control_top);
- source right as source_left + (clipped_right - clipped_left);
- source bottom as source_top + (clipped_bottom - clipped_top).

Thus source and destination extents are equal. Reducing the control width
selects a smaller source crop rather than scaling the original 82x16 art.

The normal path reaches blit wrapper 0x6556C0 in mode 0x100, which dispatches
the underlying DirectDraw surface blit with distinct destination and source
rectangles prepared above.

## Layer order

PlayerRow constructs the static bar PictureControl first at call 0x5262E6
and the dynamic PictureControl second at 0x526351.

Combined with the source-closed append-order/forward-traversal renderer chain,
the dynamic crop paints after the static bar:

- side 0: cropped team_bar_1 overlays blank_bar from the left;
- side 1: cropped blank_bar overlays the left portion of team_bar_2, so the
  colored bar is revealed from the right as energy rises.

## Reconstruction boundary

gate14_fastview_team_energy_raster.py reuses the existing verified static
TeamTable raster, then applies only the source-closed dynamic crop for each
retained PlayerRow render plan.

It supports the normal source endpoint domain 58..99, including zero-width
dynamic crops at the appropriate endpoint. It intentionally rejects the
below-58 side-0 inverted rectangle produced by the executable arithmetic until
the generic clipping behavior for that pathological geometry is independently
source-closed.

Still unresolved:

- PlayerRow text-control pixels at the TeamTable raster layer;
- global FastView cross-component order beyond individually proved relations;
- cross-component alpha/blend semantics;
- unbound background ownership;
- audio and 3D choreography.

No proprietary executable bytes or private disassembly are committed.
