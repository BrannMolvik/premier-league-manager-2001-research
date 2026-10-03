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

PR #213 was cleaned of shared Gate-13 status-file edits, verified and squash-merged as canonical main `4f8860b325484a19fec7a76cf9d49ae23584899f`:

- reconstruction workflow `37128681158`: **1,701 tests passed, 23 expected skips**;
- repository asset-policy workflow `37128681160`: passed.

## Recovery 224 explicit TeamTable geometry extension

The next independent surface step adds only caller-explicit TeamTable rows. The partial-surface builder accepts a tuple of `FastViewTeamRowSelection(side_index, row_index)` values and never manufactures a visible roster count.

For each selected row it reuses the already source-closed TeamTable contract to expose:

- the exact side/row name-grid rectangle and the source-selected primary/alternate resource identity;
- the exact shared 82x16 energy-bar rectangle and its side-specific static/dynamic resource identities;
- all six exact PlayerRow text-control rectangles.

These new entries are classified as `team_table_geometry` and have `raster_available = False`: the TeamTable grid/bar resources remain unimported in this presentation path and no row text pixels are supplied by this layout-only seam. The existing decoded chrome, possession art and PossessionFigures glyph layers remain raster-available.

Cross-component overlap detection now also catches TeamTable geometry against existing source-bound fragments. For example, explicit row 0 overlaps `top_bar.444`; the layout records that overlap and still refuses to assign a z-order or flatten the frame.

Invalid sides, boolean/non-integer row indices, duplicate row selections, implicit list/tuple shorthand and rows whose translated rectangles leave the recovered 800x600 surface fail closed.

The Recovery-224 TeamTable extension still requires branch CI before merge. Gate 13 remains the earliest incomplete validation gate under Codex ownership.
