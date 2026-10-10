# Recovery 458 — original multi-human manager NEXT flow is inaccessible from TeamSelect Start

_10 October 2026 KST. Continued Gate13 P0 functional-fidelity audit from Recovery457, strictly **AUDIT ONLY** under research/CURRENT_STATE.md. Codex retains implementation, GUI acceptance, CI and gate/release ownership; no game code, asset, saved game, original file or Codex implementation branch was changed._

## Verified checkpoint, source and branch identity

- Recovery entry main HEAD **`945b921a0eee7336c18e287ca855dc8cbc83947f`**, authoritative state read, `agent-runtime` `worker_role=audit_only`, `implementation_allowed=false`. Codex latest checked implementation HEAD **`0ae745d1b56f45cade460f03cd893849a2f53b45`** (no new Codex progress since Recovery457).
- Original private `/mnt/data/fm2001_private/footballmanager.exe` independently rehashed: size **4,714,541 bytes**, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Source `objdump -d -Mintel --start-address=0x413c4f --stop-address=0x413c78` and `--start-address=0x43261f --stop-address=0x432647` were re-run in this recovery.
- Previously independent source `research/GATE13_NEXT_MULTI_MANAGER_INDEX_FIDELITY_AUDIT_RECOVERY445.md` confirms original manager-owner address `0x874C10`: **`+0x9C4` selected user index** (global `0x8755D4`), **`+0x9D4` registered human count** (global `0x8755E4`) and **`+0x9CC` human manager linked collection** (`0x8755DC`). No need to restart that source work.

## A. Original multi-user lifecycle is real and required to finish the source-complete game

- Native original new-user branch `0x413C60..` loads count at owner `+0x9D4`; **`0x413C6A` sets selected index at `+0x9C4` equal to that prior count**, then `0x413C70..` increments manager count. This original code registers multiple users, not only a single replaceable selected club.
- The native conditional NEXT branch `0x43261F` requires source local state=2; at `0x432626..` it computes **`(selected_index+1) modulo manager_count`** with `idiv [0x8755E4]`, saves remainder into **`0x8755D4`** at `0x432639` and reconstructs original manager shell. Not a game-day increment.
- Original PResults scans all registered managers' upcoming event owners and restores previous selected manager (Recovery445); deferred EAM delivery and per-user mailbox cleanup also iterate all registered managers (Recoveries451–452). A one-human model cannot honestly claim those multi-manager paths are tested/implemented.

## B. Hard code-level stop appears *before* normal management gameplay

Both `main` and Codex use byte-for-byte **the same** `reconstruction/front_end_session.py` Git blob **`7ab004fd4e5ff56886b055d4dca7014447ec7405`**.

The code does preserve a source-like TeamSelect user selection array:
- `selected_club_ids: tuple[int,...]` (~line76); `set_club_selections` (~152) validates uniqueness and a max-six selected count; `toggle_club_selection` (~172) adds/removes one choice.
- **But `FrontEndSession.dispatch(TeamSelectControl.START_CONTINUE)` (~lines238–245) checks `len(self.selected_club_ids)!=1` and raises `FrontEndSessionError` saying “Multiple original TeamSelect users are source-proven, but the modern gameplay backend currently supports one human manager.”** The failure happens **before backend creation, `select_club` or management navigation**, so it is not merely NEXT lacking a later hotseat callback.
- An existing unit test `reconstruction/test_front_end_session.py::test_source_style_multiple_users_are_recorded_but_fail_closed_at_start` **explicitly expects** the two-club selection to reject Start, remain unstarted and leave backend selected clubs empty. This is an intentional correct *fail-closed partial implementation*, **not evidence the original multi-manager game works**.
- Therefore normal original TeamSelect selection of two users **cannot reach the PMenu/Squad/NEXT UI in the same game**. No backend test of manager cycling can substitute for the blocked first user journey.

The separate gameplay `reconstruction/human_gameplay.py` method `selectable_club_ids` (~line568) includes **fixed Premier League and materialized playable procedural League clubs** in its supported set; this audit does not incorrectly assert that every non-Premier League club is unsupported. `select_club` still installs **one** `HumanManagerState`, so even single-manager support across leagues doesn't provide original multi-human play.

## B2. Front-end host catches the rejected Start — no evidence of process crash or partial gameplay state

The latest Codex `reconstruction/original_game_host.py::on_click` runs its non-management `presenter.pointer` action inside a `try` block (the management cases return earlier). Near **lines2456–2458** an `except Exception` handler sets `last_status` to the exception type/message, calls the injected `error_reporter` and returns. Thus when `FrontEndSession.dispatch` rejects multiple users, **the normal event handler has a documented error-reporting path**, not an independently proven GUI process crash or a fabricated successful management transition. The session guard precedes backend construction/selection; the unit test confirms `started=False` and no selected backend clubs after rejection.

The audit has **not executed Tk on Windows11**; whether an appropriate in-game error dialog appears or the failure only reaches a diagnostic output is **UNKNOWN**. Do not misreport this as a Windows crash or assume that this diagnostic is original-interface parity. Codex should preserve clean rejection while multi-human backend is incomplete.

## C. Why this changes the immediate NEXT/Codex acceptance contract

Recovery457 correctly identified that Codex already has bounded original NEXT backend work but no physical NEXT click. Even **after** the button is connected for a single manager, Gate13/full-original acceptance must not be described as complete:
- Native `0x43261F` really switches among registered human users in one game, **not** between two separately created saves.
- Native PResults and EAM queued delivery preserve per-manager owners. Original `0x8755D4` switching must update the actual visible club, roster, inbox, PMenu and header safely without mutating unrelated player state or reinitializing schedules.
- A test running Southport alone, closing it, then running another club alone only checks shared code paths across clubs. **It does not cover simultaneous registered human managers, shared match dates, owner-specific mailbox recipients, pause/return, or persisted selected human index.**

**Codex implementation handoff, sequential and reversible:**
1. Preserve current intentional fail-closed guard **until** there is real multi-user backend state; do not silently remove `len!=1` as a superficial fix. Build distinct human-manager contexts and source count/index binding on a shared game calendar/fixtures/mailboxes, using existing original user-selector and scheduled event evidence. Keep original max-six TeamSelect selection cap only within its proven source contract.
2. Support Start/Continue for 2+ valid unique clubs; create all registered user owners exactly once with current selected manager semantics. On guarded NEXT state2, rotate selected manager **modulo real count**, rebuild management without resetting shared simulations.
3. Handle PResults date/event selection across all human managers, preserving original source relative bucket ordering and restoring prior index afterward; route delayed EAM to per-manager user+0x6B4 rather than leaking into current user.
4. Verify both **a two-club independent cross-run test** and **a two-manager same-save functional UI test**: New Game→TeamSelect select two clubs→Start→both roster/inbox contexts→NEXT switch→match/PResults→save/reload→correct restored manager and game date. Test rejected duplicate/overflow selection, safe ongoing roster/transfer state, and GUI receipts on real Windows11.
5. Do not claim multi-user complete merely because current single-manager `advance_original_management_turn` passes, or because TeamSelect can *record* multiple choices. Hold gate open until accepted normal user journey.

## D. Scope and verification boundary

**EXACT / source-backed:** canonical original hash, native manager count/index creation and state2 NEXT modulo, Codex/main exact session blob and hard single-manager Start rejection, intentional corresponding unit test, existing procedural-League option in selectable club set.

**NOT demonstrated:** original Windows11 runtime acceptance, correct binary save format for multi-human users, end-to-end native PResults/scheduler UI, direct inbox click and complete EAM screens, complete Squad formation screens and original animated match-watch mode. All remain outside this audit result.

**Gate13 remains OPEN. Gates14–17 and verified full-scope Windows11 release remain INCOMPLETE.** No implementation files changed; no CI was dispatched, no game or proprietary assets were run/committed, and no gate was closed.
