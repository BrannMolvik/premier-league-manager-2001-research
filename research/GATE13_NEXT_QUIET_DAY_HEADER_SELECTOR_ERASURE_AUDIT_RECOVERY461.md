# Recovery 461 — a qualified quiet NEXT day also erases the future MATCH header candidate

_10 October 2026 KST. Strict independent Gate13 P0-D original-file fidelity / source-state audit; continue Recovery460, do not restart reconstruction. Codex is the sole implementation and Windows11 acceptance owner. No game-source, assets, saves, CI, branch merges or gate states changed._

## 1. Exact starting checkpoint and provenance

- GitHub main **`1ac1f4d9254d1af1ddecc69271e2866beec4c279`**; Codex `codex/gate13-windows-playability-recovery` head **`0ae745d1b56f45cade460f03cd893849a2f53b45`** remains unchanged since 2026-10-09 14:32Z. Read binding `research/CURRENT_STATE.md` and runtime state generation460, `worker_role=audit_only`/`implementation_allowed=false`.
- Original authorized `footballmanager.exe` canonical identity **SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**, 4,714,541 bytes. This source-independent code-audit step relies on original Event/link semantics already verified Recoveries446–460; do not mistake a static cross-code proof for original game execution or Windows11 GUI evidence.

## 2. Explicit cross-component derivation, not a speculative pixel defect

**Source A: bounded NEXT controller.** Latest Codex `reconstruction/human_gameplay.py`, blob `980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`, `HumanGameplayController.advance_original_management_turn` **lines1571–1609**, on each accepted date in its target, calls:

```python
self.state.calendar.increment_one_day()
self.state.invalidate_primary_schedule_wrapper_links()
pending = self._process_current_primary_day(native_primary_order=True)
```

**Source B: global shadow downgrade.** `reconstruction/game_state.py` `invalidate_primary_schedule_wrapper_links` lines3460–3462 forwards unconditionally to `PrimaryScheduleShadowState.invalidate_unmodelled_wrapper_links` in `reconstruction/primary_schedule_shadow.py`, blob `5d8fbcbf411a308375f209fcae00d068fb55dea6`, lines269–285. Its map turns **all** entries that are not already `linked` into `unknown` on every date, **including future dates**, regardless of whether the day just processed contains a fixture. There is no same-turn re-certification in this bounded controller.

**Source C: read-only header next-match selector.** `PrimaryScheduleShadowState.direct_fixed_league_header_candidate` lines287–329 scans relevant future buckets, accepts a live direct fixed-League entry only if `wrapper_link_state==WRAPPER_LINK_CLEAR`, and returns None on relevant unknown states. `ManagementSourceDataBridge.management_header_match` at `reconstruction/gate13_management_source_data.py` around **lines1007–1075** calls that selector to project the original-looking future match; it returns **None** if selector does. The view contains a display fixture/date/name, **not** an independently qualified original live `Event` pointer.

**Source D: visible source-caption fallback.** `reconstruction/original_game_host.py::_draw_management_next_control` at **lines1421–1443** feeds `retained_match_date=None` when `frame.presentation.header_match` is absent. `reconstruction/original_management_next.py::native_next_caption` explicitly returns `MATCH` only when `retained_match_date==current_date+1 day`, otherwise `NEXT`.

**Code-level consequence:** if Codex's bounded backend eventually receives a *genuinely qualified* NEXT action, successfully processes **one fixture-free day** (so `_process_current_primary_day` does not encounter a due entry) and returns to the standard management presenter, the following fresh header projection can lose an otherwise previously source-qualified upcoming direct League fixture **because the earlier quiet day already downgraded its future `clear` wrapper to `unknown`**. When that originally known fixture is the following day's match, the caption would display `NEXT` instead of `MATCH`, despite live fixture data still existing. **Conditional:** this is an exact cross-component static implication with source-backed test behavior, not a report of an observed real UI game bug; the normal NEXT click is currently absent, so no user can reach this precise bounded workflow through the original-looking host.

**Important nuance — the existing test knows this fail-close rule.** Codex's `reconstruction/test_gate13_management_source_data.py::test_management_header_match_uses_bounded_primary_shadow_candidate` (~lines454–496) proves a fresh candidate exists, then **explicitly calls** `invalidate_unmodelled_wrapper_links()` and asserts that `management_header_match()` becomes **None**. That test is correct for its declared conservative source contract. It is not a test of user gameplay or proof that an original live match should disappear after a quiet day. The missing coverage is the **end-to-end bounded advance → shadow state → next header view → ordinary GUI NEXT** sequence, with source-authenticated wrapper lifecycle.

## 3. Relationship to already documented due-day exception and partial state mutation

Recovery460 **already** proved that on a day with due primary events, `_process_current_primary_day(native_primary_order=True)` rejects the newly downgraded wrapper as `unknown` and raises `Original NEXT current-day wrapper lifecycle is unresolved`, **after** the calendar and shadow states have changed, with no controller-level rollback. This report **does not rediscover or mislabel** that bug; it documents the earlier, **quiet-day** consequence that also invalidates upcoming MATCH presentation before the due date.

These are two related effects of **one** missing original-state transition — dynamic wrapper/link revalidation across day boundaries — not grounds to introduce two separate hypothetical scheduling engines.

## 4. Codex-only narrow acceptance checklist

1. **Preserve fidelity:** investigate original `Event+0x08` link creators, postponement and rescheduling producers already scoped in Recoveries446–448. Do NOT simply set unknown back to clear, remove all guards or treat `header_match.scheduled_date` as `selector_source_qualified=True`.
2. **Stage a deterministic original-safe fixture:** source-verified fresh fixed-League direct participants, an actual fixture-free next calendar day, and a still-future direct League match. Check pre-state `clear`, before/after day advancement, next header candidate and display caption; preserve source match identity.
3. **Test the due day separately:** qualified fixture with original-safe wrapper state must reach human match preparation, the correct roster gates and PResults, or refuse without consuming the game date/RNG/manager state if source certainty is truly absent. Snapshot full game state before exceptions (Recovery460).
4. **Wire the existing real front-end entry point:** original PBg ID3, rectangle (700,0,100,95), control flag bit2 set/bit0x10 clear and owner/modal predicates to Codex's existing bounded controller. The current host only handles hover. Test normal user mouse and actual Windows11 management/return, not isolated helper calls.
5. **Avoid redoing completed pieces:** no independent reimplementation of `advance_original_management_turn`, the existing shadow lookup, the original bitmap, the F401 startup scheduler or completed audit art. Other Gate13 blocking work remains native EAMail, Squad 1ST/RES formation tabs, simultaneous human managers in TeamSelect and unintegrated menu actions.

## 5. Explicit status

**CONFIRMED from current code/test:** all-future-entry wrapper downgrade on even quiet-day bounded advance; tested display projection refuses unknown shadow; caption shows NEXT if there is no retained header; current normal click cannot reach the bounded backend. **UNKNOWN:** exact original revalidation/persistence of wrapper links through its daily scheduler, real Win11 visible/physical outcome after a fully source-qualified click; multiple-manager and saved-game acceptance.

This is a **research-only corrective handoff, not a new playable implementation, Windows11 validation, CI pass or gate closure**. Gate13 remains OPEN; Gates14–17 and verified full-scope Windows11 release remain INCOMPLETE.
