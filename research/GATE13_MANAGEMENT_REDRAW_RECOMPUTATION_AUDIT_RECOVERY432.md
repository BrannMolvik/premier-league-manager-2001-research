# Recovery 432 — management redraw recomputes complete active-panel data

_9 October 2026 KST. Audit-only GitHub inspection of canonical main `beab65e525cf900b21698a7a8f636b44f69684b7`, `research/CURRENT_STATE.md` and Codex technical branch `cbbb15d9242883f2f5185a002b0a5e7443a53ba1`. No game/assets/save/schema changes, CI, branch merges, native original launch or gate closure._

## Confirmed source-code call graph on a redraw

1. `reconstruction/original_game_host.py::_draw_management_host` calls `build_management_canvas_frame(self.management_presenter)` **on every management redraw** before checking family resource readiness, menu raster cache, or painting.
2. `reconstruction/original_management_canvas.py::build_management_canvas_frame` invokes `snapshot = presenter.snapshot()` unconditionally.
3. `reconstruction/original_management_presenter.py::OriginalManagementPresenter.snapshot` calls `build_management_panel_snapshot(..., self.selected_child_id, ...)` without a cached/snapshot-version branch. `build_management_panel_snapshot` creates a new `ManagementSourceDataBridge`, computes `club_header()`, possibly `management_header_match()`, and `build_pmenu_snapshot()` every call.
4. For Squad `0xCE`, the same panel-snapshot call obtains `tuple(bridge.squad_rows())`, uses `build_squad_row_viewport` or `original_paired_squad(source_rows)`. `reconstruction/gate13_management_source_data.py::ManagementSourceDataBridge.squad_rows` iterates through `tuple(controller.squad())`, queries source positions, retained selection and status, and computes each player's performance average and current-role rating (plus further derived status fields). `original_paired_squad` calls `build_paired_squad_snapshot`.
5. The host then calls `_draw_squad_top_controls` and `_draw_squad_rows`, which, for combined 3/first+reserve, build fresh title/grid overlays and `build_paired_roster_text_overlays` before inserting each overlay into the Tk canvas. `_generic_photo_cache` prevents some repeated `PhotoImage` decoding, but neither that cache nor the PMenu render cache prevents **source panel-snapshot recomputation** or all canvas placement/overlay-generation work.

**Classification: CONFIRMED synchronous repeat work on management redraw.** It is a *potential latency contributor*, not a measured lag root cause, original-regression proof or automatically an invalid design. Preserve the original contents and cache invalidation semantics if the implementation owner optimizes this.

## Confirmed header-only redraw path reaches this call graph

`original_game_host.py::on_fixtures_pager_motion` updates `management_header_state` and schedules `_schedule_management_header_update` when appropriate. `_schedule_management_header_update` uses `root.after_idle(self._advance_management_header)` when a source frame update is pending. `_advance_management_header` calls `self.redraw()` if `management_header_state.update()` returns true; `redraw()` calls `_draw_management_host` for management. Thus even a **header animation update can rebuild the entire Squad snapshot and overlay composition**. `test_original_game_host.py::test_management_header_hover_uses_one_idle_update_per_pass` asserts the hover frame and redraw behavior in a fake-Tk test; this audit did not rerun that test.

This is distinct from Recovery431's confirmed `on_click` early return while `_management_load_thread` is non-null. The two potential responsiveness costs must not be conflated: (i) click suppression while worker assets load, and (ii) repeating synchronous gameplay-to-view and canvas composition during an otherwise inexpensive animation redraw.

## Timings and native equivalence still unresolved

`reconstruction/runtime_diagnostics.py::timed_stage` already reports flushed timings for `management.first_snapshot`, `management.first_draw`, `frontend.redraw`, `management.pmenu.render` and background family asset stages. A real Windows 11 receipt should capture these stages plus input response while hovering the header on the fresh first+reserve Squad screen. Where possible separately time the Squad `squad_rows` bridge, `build_paired_roster_text_overlays` and image placements, but **new instrumentation is implementation-owner work**, not permission for this audit-only worker to edit runtime.

Any prospective snapshot caching must invalidate on original state changes such as roster reorders/drops, match/NEXT date, injury/condition/status, performance/rating, selected club/competition, settings/display scale, and PMenu navigation/expansion; derive the exact dependency key from code/native state rather than memoizing indefinitely or changing the shipped game's behavior. Prove original visible/input/timing semantics and avoid inventing pixels.

## Unchanged original-source task / infrastructure blocker

Canonical selected Squad row blue/normal bitmap selection remains unproven. Before implementation, privately hash-gate canonical original executable to `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; seed final populated `PSquadPlayerRow` vtable `0x7C57BC` using `squad_trace_report(pe, vtable_seeds=(("final PSquadPlayerRow",0x7C57BC),))` outside Git; resolve `0x4B6ECC` final constructor overwrite, `0x443E70` +0x2C image-wrapper child, native state input/update/draw call graph and candidate `stats_grid.444` real usage. EAMail `0x65` low dispatch candidate `0x47CA04` and PMenu frame/input timing follow. No blue pixel color or selection semantics inferred from source filenames or name text color.

This recovery retried `container.exec` twice and `python.exec` once with trivial commands; each failed **before process execution** as `caas.internal.errors.ClientError`. Original source ZIP remains in ChatGPT Library, not lost. No fresh PE hash/disassembly, tests, actual Windows 11 UI performance receipt or runtime comparison performed. Gate 13 remains OPEN; Gates 14–17 and original full-scope Windows 11 release remain unverified. The persisted `agent-runtime` role is `audit_only` and Codex retains exclusive implementation ownership.
