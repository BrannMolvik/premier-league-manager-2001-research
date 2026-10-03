# Gate 14 PlayerRow render-plan bridge

_Status: independent Gate-14 work-ahead; Gate 13 remains the earliest incomplete validation gate under the active Codex ownership lock._

## Purpose

The semantic FastView path already retains exact `FastViewPlayerRowSnapshot` objects without rerunning simulation. Recovery 224 adds the next presentation-only seam: a raster-neutral render plan derived from one retained snapshot.

The adapter remains inside `reconstruction/gate14_fastview_playerrow_snapshot.py` so it can reuse the exact source-backed row state without importing gameplay, RNG, match-calculation or controller modules.

## Preserved source channels

For each retained row the plan exposes:

- exact side and row identity;
- source-selected primary/alternate name-grid resource and exact name-grid rectangle;
- exact side-specific static and dynamic energy resources;
- exact full energy-bar rectangle and the source-computed dynamic rectangle;
- six text instructions in source cell order.

Text values remain deliberately typed rather than flattened into guessed display strings:

- shirt number, player display name and form are `literal`;
- position remains a `localization_key`, because this adapter does not invent the result of a language-table lookup;
- goal and own-goal cells remain `unwritten` until an evidenced typed callback supplied their parenthesized text;
- own-goal retains the source color-update flag without naming the unresolved native color channels.

The render plan keeps `raster_ready = False`. It does not claim that TeamTable binary art or generic text rasterization has been integrated.

## Fail-closed validation

Before producing instructions, the adapter rechecks retained state against the independently source-closed TeamTable contract:

- name-grid resource must match the selected side/row;
- energy side, row, full rectangle and static/dynamic resources must match the TeamTable side contract;
- text controls must still match their source cell indices and exact rectangles;
- manually constructed or drifted snapshots are rejected.

The source energy transform is not sanitized. A below-anchor value can therefore preserve the executable's negative-width dynamic rectangle in the plan; rasterization remains a separate unresolved boundary.

## Gate impact

This advances Gate 14's requirement that presentation consume reconstructed/retained match state rather than duplicate simulation logic. It does not close Gate 14, provide missing audio mappings, resolve generic FastView text pixels, assign cross-component z-order, or alter any Gate-13 implementation/status file.


## Recovery 225 semantic-shell integration

The next presentation seam is now explicit: `FastViewSemanticShell` derives one
`FastViewPlayerRowRenderPlan` for each retained `presentation.player_rows`
snapshot, in exactly the same tuple order.

This remains a one-way read-only projection. The shell does not call match
simulation, RNG, scheduling, controller, audio or commentary code. It simply
translates the already retained PlayerRow snapshot through the fail-closed
render-plan adapter.

The shell continues to report:

- `original_layout_recovered = False`;
- `audio_mapping_recovered = False`;
- `choreography_3d_recovered = False`.

Therefore this integration is evidence that Gate 14 presentation consumes
retained reconstructed state without duplicating simulation, not evidence of a
complete or player-visible original FastView frame.


## Recovery 225 partial-surface selection bridge

The partial 800x600 FastView layout can now derive its TeamTable row selections
directly from a tuple of `FastViewPlayerRowRenderPlan` values.

This removes a duplicate manual row-selection channel. The presentation path no
longer needs to separately state `(side_index, row_index)` after those identities
have already been validated in retained PlayerRow state.

The bridge preserves input order, rejects non-tuple/manual shorthand and wrong
types, and rejects duplicate retained row identities. It then delegates to the
existing fail-closed partial-surface builder, so all prior geometry bounds,
cross-component overlap reporting and unresolved raster/z-order boundaries still
apply.

This remains geometry-only for TeamTable rows. No row art/text rasterization,
cross-component draw order, complete frame, audio mapping or Gate-14 completion
is claimed.
