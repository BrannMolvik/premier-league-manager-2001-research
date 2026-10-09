# Recovery 431 — management resource-load input gate and timing receipts

_2026-10-09 KST. Strict independent audit-only continuation from canonical main `95eb1bf91c0f4bd8f0d6acb0852c390a925c2270` and existing Codex implementation head `cbbb15d9242883f2f5185a002b0a5e7443a53ba1`. No game implementation/asset/save/schema changes, Windows/original launch, CI, merge or gate closure._

## Confirmed code behavior: input discarded during asynchronous resource decode

1. `reconstruction/original_game_host.py::_begin_management_resource_load` starts a `management_thread_factory` worker for a requested resource family (`squad`, `fixtures` or `league_tables`), stores it in `self._management_load_thread`, sets a watch cursor and polls its result queue every 25 ms via Tk `root.after`.
2. In `OriginalGameTkHost.on_click`, after event normalization and before any management PMenu open/action, Squad drag, fixtures pager, or grid dispatch, the following unconditional management-screen gate applies:

   ```python
   if self._management_load_thread is not None:
       self.last_status = (
           "Preparing source-backed management "
           f"{self._management_loading_family or 'squad'} resources..."
       )
       return
   ```

   The pointer event is **discarded**, not queued/replayed after resource completion. This gate applies to *all management mouse presses* while the family worker exists, including already-rendered PMenu/header controls. This is **CONFIRMED reconstruction behavior**, not proof of any equivalent native FM2001 input-disable mechanism.

3. The checked-in `reconstruction/test_original_game_host.py::test_management_input_is_ignored_while_async_resources_are_loading` explicitly verifies this behavior for the first Squad load. `test_later_management_route_decode_blocks_input_and_surfaces_failure` repeats it for the later Fixtures family, with a deferred worker and exact status text. Thus it is an **intentional modeled safety/presentation boundary**, not an accidental missing function call. These are existing tests and **were not executed** by this audit.
4. The original publisher has no timing receipt for this user-visible input suppression: `research/CURRENT_STATE.md` and the Codex local handoff explicitly leave native Windows 11 responsive menu/TeamSelect/fresh Squad playtest acceptance OPEN. The reported significant management/menu loading delays could make input suppression noticeable, but **the causal relationship is unverified** until original hands-on timing/interaction receipts are collected. Do not label the background worker as itself a broken event loop or presume exact duration.

## Precise existing instrumentation to collect on Windows — no code required

`reconstruction/runtime_diagnostics.py::timed_stage` prints flushed `[FM2001 runtime] BEGIN/END/FAIL {stage} seconds=...` to stderr. The host already emits relevant stages:

- `management.resources.load_squad`, `management.resources.load_fixtures`, `management.resources.load_league_tables` around actual worker loads;
- `management.resources.pmenu`, `management.resources.squad_top`, `management.resources.squad_rows`, `management.resources.background`, `management.resources.header`, plus route-specific fixtures/tables stages inside the loader;
- `management.presenter.construct`, `management.first_snapshot`, `management.pmenu.render`, `management.first_draw`, `frontend.redraw screen=...` around main-thread presentation.

**Minimal source-grounded next diagnostic for Codex (implementation owner):** use the existing trusted 9 October Windows playtest launcher/log capture, observe actual stage durations, and record whether clicks while a resource worker is active are dropped. Correlate the logged `BEGIN`/`END` times and real screenshot timestamps with native original input/timing under the same screen. No remote Linux CI can establish the reported Windows latency or original visual equivalence.

## Distinct error-path risk (static, conditional)

`original_management_presenter.py::source_accepted_pmenu_action` commits `selected_child_id` after successfully building a snapshot, **before** the host starts any unimported resource-family load. If that later load fails, `_poll_management_resource_load` reports the exception and clears the worker, but does **not** revert the presenter panel selection or restore a prior ready-rendered panel in that failure branch. The checked-in test `test_later_management_route_decode_blocks_input_and_surfaces_failure` exercises the later family failure and asserts its error status, though it does not independently assert resulting panel fallback behavior. This is a **CONFIRMED missing rollback mechanism in the inspected code paths / PROBABLE stale-panel or retry risk on actual resource failures**, not evidence that the user's observed ordinary menu slowdown involved a failed load.

## Original selected-row blocker still highest priority

This audit does not produce any new source-byte proof for the selected blue Squad row background. `stats_grid_disabled.444` is repeated uniformly; the original `stats_grid.444` loader/texture is only a candidate until native row ownership is traced. The next original-source investigation is hash-gated canonical `footballmanager.exe` (expected SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`), with the `reconstruction/gate13_squad_source_trace.py::squad_trace_report` custom `vtable_seeds=(("final PSquadPlayerRow",0x7C57BC),)` argument and output outside Git; inspect `0x4B6ECC` final overwrite, `0x443E70` texture child `+0x2C`, original UI state producer, draw order, bitmap frame/shade before any implementation. Then resolve EAMail `0x65` original `0x47AEC0` factory/RTTI (derived but unverified low byte index candidate `0x47CA04`) and PMenu input/animation clock.

## Environment, audit ownership and acceptance

This recovery reconfirmed canonical main/CURRENT_STATE/agent-runtime and Codex branch heads. Both a trivial `container.exec(['/bin/echo',...])` and a private `python.exec` process-probe failed before execution with `caas.internal.errors.ClientError`. Original archive presence is documented in ChatGPT Library; do not mislabel it missing. No fresh original executable hash, disassembly, original GUI, tests, Windows 11 playtest or performance measurement occurred. No changes to Codex's branch.

The user's latest **explicit** 9 October role assignment remains `audit_only` for this autonomous worker; generic auto-recovery prompts do not authorize implementation. Gate 13 remains open; Gates 14–17 and full playable Windows 11 release remain unverified. **Further repetitive checkpoints without material new evidence should be avoided**; this report documents a distinct and test-backed input/timing cause to investigate.
