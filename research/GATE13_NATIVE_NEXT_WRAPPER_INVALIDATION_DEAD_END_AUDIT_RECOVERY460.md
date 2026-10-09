# Recovery 460 — bounded Codex NEXT has a due-fixture wrapper-state dead end

_10 October 2026 KST. Independent Gate-13 P0-D read-only implementation audit and Codex handoff, continuing exact runtime Recovery459. **AUDIT ONLY**: Codex alone owns game implementation and Windows11 testing. No original files/game assets/saves or implementation branches modified, no CI/gate status changes._

## Provenance and branch scope

- Verified live main at start **`12be7bf8cbd8f89e2525794502c6ac8531b2b166`** and binding `research/CURRENT_STATE.md` (core PMenu, EAMail, Squad and NEXT actual playability); runtime `agent-runtime` generation459, `worker_role=audit_only`, `implementation_allowed=false`.
- Codex's latest source branch `codex/gate13-windows-playability-recovery` **`0ae745d1b56f45cade460f03cd893849a2f53b45`** has not advanced since Oct9 14:32 UTC. This finding refers to its **current source**, not a hypothetical older implementation.
- Canonical original executable remains privately available at `/mnt/data/fm2001_private/footballmanager.exe` and was independently SHA-256 reverified **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** (4,714,541 bytes). Native Event+0x08 wrapper eligibility and original runtime rescheduling are source-audited in Recoveries446–448; this report does **not** substitute a novel direct original program execution.

## A. Concrete current Codex call order yields a due-fixture state contradiction

**Source 1:** Codex `reconstruction/human_gameplay.py` blob **`980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`**, `HumanGameplayController.advance_original_management_turn` at lines **1571–1609**, is correctly fail-closed about needing an authenticated selector. Yet within the per-day loop it always executes:

```python
self.state.calendar.increment_one_day()
self.state.invalidate_primary_schedule_wrapper_links()
pending = self._process_current_primary_day(native_primary_order=True)
```

**Source 2:** Codex `reconstruction/game_state.py` blob **`3091aaed12d180ee810ba046e41761c642ff6b18`**, lines **3460–3462** delegates `invalidate_primary_schedule_wrapper_links` directly to shadow `invalidate_unmodelled_wrapper_links()` (no re-certification).

**Source 3:** Codex `reconstruction/primary_schedule_shadow.py` blob **`5d8fbcbf411a308375f209fcae00d068fb55dea6`**, lines **269–285**, transforms *every* source wrapper state except `linked` into **`unknown`** across *all* days:

```python
entry if entry.wrapper_link_state == WRAPPER_LINK_LINKED
else replace(entry, wrapper_link_state=WRAPPER_LINK_UNKNOWN)
```

Its default fresh `PrimaryScheduleShadowEntry.wrapper_link_state` is **`WRAPPER_LINK_CLEAR`** (line51), so even the previously source-qualified direct fresh League fixture immediately loses its clear claim on the first day boundary.

**Source 4:** In **the very next call**, `HumanGameplayController._process_current_primary_day(native_primary_order=True)` (same Codex `human_gameplay.py`, lines **1489–1544**) enumerates any `due_order=self.state.primary_entries_due_today()`. For every due entry, it resolves a matching shadow fixture owner and requires:

```python
if len(matches) != 1 or matches[0].wrapper_link_state != 'clear':
    raise RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')
```

There is **no intervening source-state revalidation** between invalidation and this guard. Accordingly, **on an advanced day with one or more due primary fixtures represented by previously `clear` shadow entries**, the gated controller reaches an **unresolved-wrapper exception before simulating AI entries or presenting the human pre-match choice**. Entries already `linked` also fail the clear check. If there are *no due entries*, the guard doesn't run, so this is **NOT** a claim that every quiet-calendar day fails; it is a targeted failure at due fixture days. The exact behavior of separately direct/legacy prototype `advance_to_next_user_primary_match` can differ; do not conflate the two methods.

### Why this is high-severity but not permission to bypass source checks

The explicit invalidation is intentional. Its docstring correctly notes the original post-start producers may create link state at native `Event+0x08` and are not fully modeled. **Removing invalidation or setting all unknown links to clear just to make matches run would be an unverified original rule change.** The source-safe remedy is to model/reconfirm the relevant original wrapper state at the due-date boundary, or to retain a narrower proven-clear subset only when source evidence establishes that it cannot have been modified. Otherwise fail closed with a precise tested reason.

This is an **implementation dead end within a deliberately bounded source contract**, not proof that the backend's prototype match engine is absent. Its correct integration could be staged for source-qualified fresh fixtures, while symbolic Cup/postponed/rescheduled events continue to fail closed.

## B. Existing tests do not cover this actual controller path

- `reconstruction/test_original_management_advance.py` blob **`a9fbbb367d955f67a3b4257a5fb837ca036544e6`** tests the **pure** `original_management_advance_target` date-selection function, but has **no call** to `HumanGameplayController.advance_original_management_turn`.
- `reconstruction/test_human_gameplay.py` blob **`0516276f9206e6ec185545c31cc49a30b5bb259e`** has broad prototype/human match tests but **zero mentions** of `advance_original_management_turn`, and therefore no end-to-end coverage of the invalidation→native-primary-day guard sequence.
- `reconstruction/test_original_management_next.py` blob **`5025e2907aaf6223edb8606345b445a72cb5b9af`** tests bitmap/caption/hit rectangle, not an ordinary NEXT mouse click invoking fixture processing.
- The live Codex `reconstruction/original_game_host.py` blob **`14c4436d600aa2a397779d6fe22cdc74b742bf26`**, `on_click` lines 2287–2415, still has no PBg ID3 NEXT action. Thus **two independent blockers** remain: no normal UI dispatch, and a due-day backend path blocked by unconditional wrapper invalidation.

## C. Codex-exclusive corrective contract, in priority order

1. **Create a narrow deterministic controller integration regression** from an original-safe fresh direct League fixture: known `clear` wrapper, qualified current manager and exact date/calendar, the requested NEXT press reaching the due date. Assert whether `advance_original_management_turn` processes/resolves a due primary event or intentionally fails with precise original missing evidence. Also test a quiet day without due fixtures.
2. **Trace original runtime producers of Event+0x08** (Recovery446/448) to determine when the relevant subset can keep or reacquire a source-proven clear state through day progression. Do **not** globally mark unknown as clear and do **not** skip native reschedule/event identity.
3. **Preserve staging**: the original direct-fixed-League display projection is not sufficient to set `selector_source_qualified=True` for all fixtures (Recovery457); identify true native selector, source event flags/owner and selected club. Unknown symbolic/Cup/postponed states must remain fail closed.
4. **Wire actual UI** only through the source PBg ID3 control acceptance and modal stack to the already bounded controller, implement roster `0x407FE0/0x407F40`, human match/PResults and return. Ensure no date or RNG mutation from rejected unqualified click, and no false success after a failed due-day partial transition.
5. **Validate on real Windows11**: ordinary NEXT→eligible human match→result→management, non-match turn, two separate clubs, and true two-human save (once TeamSelect backend stops rejecting it; Recovery458). Check save/reload. Later gates and 3D match-watch remain unverified.

**Classification:** **CONFIRMED current source control-flow and test gap**; CONDITIONAL failure when a due fixture is reached through the native-ordered bounded advance; original re-certification semantics and exact Windows/UI user-visible outcome UNKNOWN. No CI or original Windows process executed in this audit, and no gate closed.

**Gate13 earliest incomplete; Gates14–17 and verified original Windows11 release incomplete.**
