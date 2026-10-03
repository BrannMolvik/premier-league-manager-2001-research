# Gate 14 partial FastView surface contract

_Status: independent Gate-14 work-ahead; Gate 13 remains the earliest incomplete validation gate._

Recovery 223 adds a fail-closed 800x600 layout contract for FastView fragments whose screen placement is already independently source-closed.

The contract includes only:

- directly PictureControl-bound `top_bar.444` and `ticker.444` chrome;
- PossessionDiagram base/active art placements;
- PossessionFigures percentage text-control rectangles.

The layout records cross-component overlaps rather than inventing a draw order. In particular, the recovered percentage-control rectangles overlap the possession diagram. Because no source-backed cross-component z-order has been promoted, the contract deliberately keeps `cross_component_z_order_recovered = False`, `raster_composition_available = False`, and `complete_fastview_frame_available = False`.

The authenticated but unbound `FM2001_Art/FastView/background.444` remains excluded. This checkpoint does not add audio, 3D choreography, unresolved shell pixels, simulation logic, or a complete/player-visible FastView frame.

Implementation:

- `reconstruction/gate14_fastview_partial_surface.py`
- `reconstruction/test_gate14_fastview_partial_surface.py`

Verification on PR #213 head `d18b00bf721d6094dbe29738d0ea0c2209611b39` before the lock-safe status-file cleanup:

- reconstruction workflow `37126497098`: passed;
- repository asset-policy workflow `37126497095`: passed.

After removing shared Gate-13 status-file edits from the branch, CI must be rechecked on the final head before merge.

The next independent cloud-safe step is to continue composing only additional already source-closed FastView regions on disjoint Gate-14 files, while keeping rasterization withheld anywhere cross-component ordering or ownership is not yet source-backed.
