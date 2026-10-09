# Recovery 459 — management-resource loading suppresses user input, and panel transitions precede decode

_10 October 2026 KST. Core player-visible Gate13 P0-E/P0-A functionality audit, continuing live Recovery458. **AUDIT ONLY** per research/CURRENT_STATE.md. Codex remains sole implementation/Win11 test owner. No game code, Codex branch, source assets, user saves, CI or gates were changed._

## Checkpoint and confidence

- Verified incoming live main **`8bcacbd9d091090972d79f64eed5ac3f842e4e44`**, `agent-runtime` Recovery458 with `worker_role=audit_only`, `implementation_allowed=false`, and latest Codex head **`0ae745d1b56f45cade460f03cd893849a2f53b45`**. No Codex advancement was observed this recovery.
- Canonical private original `/mnt/data/fm2001_private/footballmanager.exe` was independently rehashed: **4,714,541 bytes**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. The finding below primarily concerns **reconstructed application control flow**, not a source-proven original asynchronous loader: exact original pending-input behavior is **UNKNOWN**.
- Read current Codex `reconstruction/original_game_host.py` Git blob **`14c4436d600aa2a397779d6fe22cdc74b742bf26`**, management presenter blob **`8cee4bca0686475b4b0a41922b9600afe70879ed`**, test host blob **`a96ba63629c2b344ef22403706ccf7559ccdecea`**. Also checked main host blob **`76820796c9bbf4a51b6972fd9f88099b734c1a91`**, main test blob **`e4e7444e282364ce7f902c18e9d66f4eae73c14f`**: the core input-suppression guard and fixture preloading exist in **both** versions.

## A. Exactly how ordinary mouse clicks are dropped while a route family loads

The current Codex game host binds the canvas **`<Button-1>` to `on_click`** around line515. Its `on_click` around **2287–2301** immediately normalizes the pointer, then in MANAGEMENT:

```python
if self._management_load_thread is not None:
    self.last_status = (
        "Preparing source-backed management "
        f"{self._management_loading_family or 'squad'} resources..."
    )
    return
if not self._management_resources_loaded:
    self._begin_management_resource_load("squad")
    return
```

**CONFIRMED:** when any management family worker is in progress, **each received ordinary click returns without being queued, replayed, or dispatched** into PMenu, Squad, Fixtures, NEXT, inbox or panel controls. This is a deliberate current input-suppression policy, not necessarily an unhandled error or a Tk process hang.

It is **unit-test-confirmed by design**, not only an inferred branch: current Codex `reconstruction/test_original_game_host.py::test_management_input_is_ignored_while_async_resources_are_loading` (approx lines875–910) deliberately uses a deferred worker, clicks during initial Squad loading, and asserts no presenter exists and loading status remains. `test_later_management_route_decode_blocks_input_and_surfaces_failure` (approx lines911–984) triggers deferred Fixtures loading, clicks, asserts status and no redraw, then verifies worker exception handling. The corresponding test names also exist on main.

**Original fidelity unknown:** the original PBg/PSquad input source masks (notably `0x64F7A0`) have been studied, but this reconstructed Python thread/decode lifecycle has **not** been linked to an original Game UI input suppression state. Do not declare the policy “wrong original input” without source/live receipts. Nor claim that it definitively caused all observed loading lag: no Windows11 stopwatch or production trace was captured.

## B. Which resource operations extend the no-input interval

Codex host `_begin_management_resource_load` (~1133) starts a **daemon background Thread**, sets `cursor="watch"`, stores `_management_load_thread` and schedules an every-25ms Tk `after` poll. `_poll_management_resource_load` (~1169) reads the Queue, clears the loading state, applies resources and redraws (or reports the exception).

The production `load_management_resources(family)` (~2542) stages:

| Route family | Decoder work in the same single-family worker | First-screen consequence |
| --- | --- | --- |
| `squad` | PMenu resources, Squad top, row text, status, management background, header, NEXT artwork | Fresh management cannot receive ordinary clicks until all complete |
| `fixtures` | Fixtures contract validation, fixtures grid, pager **plus `load_staged_pmatchinfo_snapshot(require_complete_dialog=True)`, PMatchInfo font, nested font and script art** | Initial Fixtures display is gated on loading **its downstream detailed match-information UI** as well |
| `league_tables` | League Tables contracts, header art, shared text art | Input is suppressed until this route family completes |

Families are cached thereafter: `_management_resource_families_loaded` records successful loads and subsequent route visits reuse them. Loading is **not synchronous work on the Tk UI event loop**, so source says the UI thread should retain an event loop; this audit did **not** measure whether the loader's heavy CPU work competes for interpreter time, disk or raster time.

**P0/P1 user-impact hypothesis, not measured cause:** the eager PMatchInfo resources on entering Fixtures may extend the wait for people who only want the fixtures grid, and any clicks issued during that wait are dropped. Keep this as **code-confirmed dependency/input policy + unmeasured latency hypothesis**, not a claimed Windows11 observed delay.

## C. Selected menu panel changes *before* the new family finishes loading

Another code-level sequencing fact is source-verifiable within the reconstruction:

- In Codex `original_game_host.py::on_click` around **2390–2411**, after an accepted PMenu row, the host **first calls** `management_presenter.source_accepted_pmenu_action`, then obtains `result.presentation.panel_class` and starts `_begin_management_resource_load` if that family is not cached.
- In Codex `original_management_presenter.py::source_accepted_pmenu_action` around **329–375**, after a successful `build_management_panel_snapshot`, the presenter **sets `self.selected_child_id=menu_id`** and returns the activation. This is a **committed selection before asynchronous resources exist**.
- On a loader exception, Codex `_poll_management_resource_load` clears the worker handles, reports `last_status` through `error_reporter` and **does not restore `selected_child_id` to the previously rendered panel**. The route therefore has no transactional rollback in this layer.

**Proven:** selected panel mutation precedes async resource readiness, and the error handler has no explicit presenter selection rollback. **Not proven:** whether the full GUI visibly breaks or only displays a diagnostic after a real failed decode, whether redraw immediately causes retry and whether original panel state should be restored. This is an actionable failure-recovery test, not proof of an existing original-game memory bug.

## D. Minimum Codex-owned test and correction plan, without reopening cosmetics

1. Instrument existing `timed_stage("management.resources.*")` timers and `_management_loading_family` state in an **actual Windows11 build**: record time from menu activation to first *interactable* Squad, Fixtures, Tables and PMatchInfo. Separate duration per decoder stage. No invented timing target or ungrounded claim of a measured bottleneck.
2. Run a real pointer sequence **New Game → club → first Squad → PMenu → Fixtures → immediate click NEXT/Squad/Fixtures while loading → after ready retry**. Verify that dropped inputs are visibly signaled/appropriately retried under source-qualified ownership. Do not simply replay a stale input whose modal context has changed.
3. Test resource-loader failure and recovery: a known simulated Fixtures failure after accepted menu selection, then a safe return/retry. Confirm `selected_child_id`, active tab, PMenu ownership, cursor restoration, retries and previous panel state remain coherent. Existing tests check exception surfacing but not this full user recovery.
4. Consider separating **initial Fixtures grid readiness** from downstream PMatchInfo prefetch when source-faithful and supported by real profiling; keep canonical content and source UI freeze intact. Do not remove source assets just to make unsupported panels appear quickly.
5. Preserve the already proven ordinary **PMenu motion-dismiss handler**. Recovery454 mistakenly alleged it was uncalled and Recovery455 correctly retracted that claim; this audit does not reinstate it.
6. Higher priority for actual playability remains Codex integration of normal **NEXT/MATCH ID3 → source-qualified calendar/controller, direct EAMail, Squad 4/5, Save/Return and simultaneous human manager gameplay**, as recorded in Recoveries457–458. No amount of loader optimization can close Gate13 while those basic paths remain absent.

## E. Status

- **CONFIRMED code:** both hosts ignore clicks during management loads; per-family cached background loader; Fixtures family includes PMatchInfo dialog/fonts/script before first readiness; Codex presenter commits selected child before resources; loader error reports without selection rollback; existing tests intentionally assert click ignore.
- **PARTIAL source fidelity:** original game's native input acceptance flags and UI owner lifecycle are known from earlier PBg/Squad audits, but no evidence maps them to the new Python decoder thread behavior.
- **UNKNOWN:** measured Windows11 duration/jank, which codec/asset stage is slowest, whether the original suppresses/queues any equivalent action, full failure recovery UI outcome and 2-club Windows11 parity.

**Gate13 OPEN. Gates14–17 and the verified original-scope Windows11 release INCOMPLETE. No game implementation, Codex edit, original asset/save mutation, CI run, merge or Windows11 test occurred.**
