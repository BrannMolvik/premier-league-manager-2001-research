# Recovery 465 — actual NEXT rollback surface is wider than calendar date and schedule wrapper flags

_10 October 2026 KST. Continue exactly Recovery464's original event dependency audit through **read-only** Codex runtime verification. All implementation, CI, original asset handling, Windows11 tests and gate closure remain **Codex-only**, per the binding `research/CURRENT_STATE.md` and agent-runtime `audit_only` directive._

## A. Live source and branch provenance

At start, **main `4245d4ba2f0d30163efcab6cfb55a3a240ace0dd`**, **Codex `0ae745d1b56f45cade460f03cd893849a2f53b45`**. The latter has not committed changes since 2026-10-09 14:32 UTC. Read live `CURRENT_STATE.md`, runtime generation464, and `research/GATE13_NEXT_LOCAL_EVENT_NEIGHBOR_SELECTION_AUDIT_RECOVERY464.md`, avoiding repetition of the old postponed-event source trace.

The authorized, privately held original `footballmanager.exe` is **4,714,541 bytes**; verified SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** via `sha256sum`. **No original executable process was started, no proprietary material uploaded, no Windows11 GUI run.**

All implementation facts below are from current Codex code at these verified blob identities:
- `reconstruction/human_gameplay.py` **`980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`**.
- `reconstruction/game_state.py` **`3091aaed12d180ee810ba046e41761c642ff6b18`**.
- `reconstruction/primary_schedule_shadow.py` **`5d8fbcbf411a308375f209fcae00d068fb55dea6`**.
- `reconstruction/internal_save.py` **`ad4b046756691bb1101aade80598e7e699a2b684`**.
- `reconstruction/test_human_gameplay.py` **`0516276f9206e6ec185545c31cc49a30b5bb259e`**.
- `reconstruction/test_original_management_advance.py` **`a9fbbb367d955f67a3b4257a5fb837ca036544e6`**.

## B. Verified current NEXT mutation boundaries — rollback just two fields is insufficient

The bounded `HumanGameplayController.advance_original_management_turn` in `human_gameplay.py` lines1571–1609:

1. validates human selection and `original_management_advance_target` BEFORE moving date;
2. in the next-day roster path may call `current_selection()` before movement;
3. loops `target.processing_dates`; **in each iteration**, mutates `GameCalendar.current_date` using `increment_one_day()`, globally downgrades schedule-wrapper certainties via `state.invalidate_primary_schedule_wrapper_links()`, then calls `_process_current_primary_day(native_primary_order=True)`;
4. has **no whole-state transaction, rollback handler or controller rehydration** if any per-day function raises.

The existing wrapper guard `_process_current_primary_day` around lines1503–1522 can immediately raise `RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')` on a due fixed-League fixture after date+wrapper changes. This is the Recovery460 **already confirmed conditional partial-mutation path** — not an observed user-facing failure, because normal header NEXT `on_click` is still unconnected.

**New boundary established from the exact downstream code:** on a path without such a wrapper exception, the *same* day worker may mutate much more than the calendar/shadow:
- `_process_current_primary_day` calls `state.simulate_due_primary_ai_entries(...,match_rng,match_engine_rng)` when no human fixture is due; if one is due, it loops `simulate_primary_ai_entry(...)` for AI fixtures before setting `pending_primary_entry`, `_pending_prior_primary_results`, `_pending_after_primary_entries`.
- `_finish_shared_primary_day(had_results)` at lines1465–1487 may run source-derived season financial transition, calendar daily/monthly hooks, transfer maintenance, weekly payroll, AI transfers using **match_rng**, monthly counters and source single-user sacking. Some of these operations can affect game state, financial balances, player status, RNG and controlled-club identity.
- The loop can process **multiple dates** in one NEXT call; an exception after an earlier successful day can leave a **partially completed turn**, not merely a partially changed current day. A before/after assertion checking only `current_date` and `wrapper_link_state` would miss accepted AI results, upkeep/hook changes, pending human match context and RNG.
  
This is **code-derived possible partial state upon a later error** and should be tested. It does not prove that any of these methods presently raises after completing unrelated work in a normal source-qualified game, or prove the exact original FM2001 atomicity semantics.

## C. Existing full modern internal-save snapshot is a useful oracle, but NOT a one-line in-place rollback

The **current** `reconstruction/internal_save.py` already provides stronger coverage than two-field snapshots:

- `snapshot_game_state` (~line1284) serializes `calendar_date`, league results/round order, roster/players, competitions, real/derived cup results, transfer state, finances and **`primary_schedule_shadow.snapshot()`** (~line1446).
- `snapshot_human_gameplay` (~line2027) includes the game snapshot, **current human club/formation/lineup/orders**, `pending_fixture_id`, `pending_primary_entry`, pending prior/after AI results, explicit match RNG state and optional `match_engine_rng.snapshot_state()`; schema version **48**.
- `restore_human_gameplay(database, attack_matrix, defence_matrix, snapshot)` (~line2109) verifies original source-database descriptor, constructs a **new** `GameState`, match RNG/engine RNG and **new** `HumanGameplayController`, then restores controller human/pending details.
- `primary_schedule_shadow.py::snapshot()/restore()` (~lines366/404) preserve source reference IDs, day order and wrapper-link states.

**Crucial limitation:** the save restoration path **creates new state and controller objects**. It does **not** implement an in-place transaction around `advance_original_management_turn`, nor rebind the already live Tk host/presenter and its pointers to a new controller. `snapshot_human_gameplay` is also an explicitly versioned modern internal save, **not** original FM2001 `.sav` file compatibility or proof every transient presentation/dialog/async resource-state is serializable. It currently omits ephemeral `controller.last_transfer_executions` and control bindings from its controller mapping (a bounded observation, not automatically a save bug). Its state/source validation may itself fail on unsupported runtime states.

**Implementation handoff:** use the existing snapshot to build a deterministic regression **oracle** for qualified refusal and for source-safe successful fixture-day transitions, rather than attempting a naïve `try/except: calendar.current_date=old_date`. A safe future transaction may use genuine preflight on the original due-event/Side dependencies *before mutation*, or snapshot/copy-on-write and an explicitly atomic controller+presenter replacement procedure; both require implementation work and source validation, not a superficial exception handler. If the source doesn't authorize a NEXT event selector or wrapper consequences, reject without changing date, results, RNG or manager state.

## D. Precise minimal Codex-only regression test plan

Add **tests of the actual `advance_original_management_turn`**, not just `original_management_advance_target` or `advance_to_next_user_fixture`. Existing `test_original_management_advance.py` only tests the pure target; `test_human_gameplay.py` covers legacy/prototype match loops and has **no call** to the bounded `advance_original_management_turn`.

1. Build one original-source qualified fixed-League test user/fixture in a deterministic calendar. Capture `snapshot_human_gameplay(controller)` **before** invocation; verify a no-due quiet-day result and its projected next MATCH status separately.
2. Force a **known due fixture** with original shadow wrapper initially `clear` that becomes `unknown` in existing code; assert that the exact existing `RuntimeError` occurs and the **snapshot differs** (the current known defective condition). After Codex fixes it, require a source-backed successful match pending transition *or* a complete no-mutation refusal.
3. Include **earlier AI fixtures** in due order; force a later source owner/flag failure to detect partial AI results, match RNG advancement, financial and pending match changes. Do not label this a guaranteed failure until executed.
4. Include a multi-day NEXT run that successfully processes one day but encounters an unsupported due event later. A rejection must not silently claim completion for all requested days or leave half a turn while the UI still shows the earlier date.
5. Test **two independent original clubs**, and separately **two human managers in one save** (the latter remains blocked by current `FrontEndSession` Start gating; Recovery458). Real physical canvas click must traverse original PBg ID3 source-accepted flags and modal guards, not only invoke controller directly.
6. After gameplay input/progression works, validate native warning/Squad return, EAM delivery, PResults, save/reload, and eventual 3D/match-watch presentation independently. No Gate13 acceptance without real Windows11 GUI/installed-run receipts.

**Release severity:** P0 for transactional game-state integrity **once ordinary NEXT is wired**, P0 for its still absent real click. This report does **not** claim whole backend missing or claim unsafe behavior in a real Windows session today.

## D2. Second source/code cross-check — single-user controller and save are NOT a hotseat rollback oracle

The original new-user constructor registers multiple human managers and NEXT rotates current-manager index modulo count (Recovery445/458, original `0x413C60..0x413C71`, `0x43261F..0x432639`). A second code inspection during Recovery465 makes the *implementation* obstruction exact:

- `reconstruction/front_end_session.py::dispatch(TeamSelectControl.START_CONTINUE)` explicitly rejects `len(selected_club_ids)!=1`. The test `test_source_style_multiple_users_are_recorded_but_fail_closed_at_start` expects that failure; it is intentional fail-closed scope, not a working hotseat mode.
- The current `HumanGameplayController` constructor sets one mutable **`self.human: HumanManagerState|None`** and a single `self.original_squad_membership`. Its `select_club` (~lines582–637) **overwrites `self.human = HumanManagerState(club_id=...)`** and the squad membership and initializes the controlled club's financial/stadium state; it does **not** append a registered human manager to a user collection. Calling `select_club` twice would *replace* the earlier active manager context instead of creating two original registered human users.
- `internal_save.py::snapshot_human_gameplay` (**schema48**) serializes exactly one optional **`controller.human`** to scalar field **`controller["human"]`**; `restore_human_gameplay` rebuilds one `HumanManagerState` and sets **`state.user_controlled_club_id`**. It has **no per-user array and no source current-user-index field** in that controller mapping.
- Thus the modern internal save's otherwise broad rollback/testing scope in Section C is **a single-human contract only**. It cannot prove source hotseat manager switching, both users' independent roster/formations/messages, or the selected current-human index survives save and load.

**Required Codex sequencing:** maintain the present single-user guard until the controller, shared calendar, per-user mail/roster ownership, and versioned save schema **all** support multiple registered human contexts with explicit selected index. Do not “fix” Gate13 hotseat by deleting the front-end length check, by repeated `select_club` calls or by testing two unrelated single-human saves. Source-level test: TeamSelect two distinct clubs → Start creates exactly two owners → NEXT state2 rotates current user without resetting game state → selected club/roster/inbox views follow correct owner → save/reload retains both and current index. Test source roster gate and shared results for both users on real Windows11 before acceptance.

**Classification:** confirmed original multi-human semantics from existing source audit; confirmed current *single-human* controller and save schema code from current Codex; not a live Windows11 gameplay or save test. The finding refines, not overturns, Recovery458.

## E. Standing original-source constraint from Recovery464

Native `Side::0x510320→0x615F40` searches its selected calendar's same-slot, previous-slot and next-slot before conditionally creating a `PostponedEvent`, and the original `0x615A60` inserts using relative slots and source collision adjustment. The original 0x615F40 dependency is locally bounded, but other wrapper producers and post-processing source callbacks remain. No part of this implementation audit justifies marking all `unknown` event wrappers `clear`, inferring a native event from display-only header text, or treating any synthetic date interval as authorized native game progress.

**AUDIT ONLY:** original game executable never launched; Codex code, original source/art/saves, CI, merges and gates untouched. **Gate13 OPEN. Gates14–17 and verified original-scope Windows11 release INCOMPLETE.**
