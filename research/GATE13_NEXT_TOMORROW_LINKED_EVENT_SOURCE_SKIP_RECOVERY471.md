# Recovery 471 — tomorrow's native Side refresh skips already-linked Events; Codex refuses them

_10 October 2026 KST; **strict original-file fidelity AUDIT ONLY**. Continuing Recovery470's native `0x511370/0x5112E0/0x5127A0` and live NEXT/Side scheduling investigation without restarting prior work or changing any game implementation._

## Versioned scope, original evidence and limits

- Canonical main at start: `a8a980049aeb3d06d9e71d39e04c88d6909fa535`; Codex implementation branch `dd69b6a8cf609a2e7c1c7163d486bd126b96f65f` (unchanged during this audit). Runtime recovery generation471 has `worker_role=audit_only`, `implementation_allowed=false`.
- Codex source: `reconstruction/primary_schedule_shadow.py` blob `9f38e61349f10180219b94b1718ce55f52ffd00f`, particularly `prepare_ordinary_day` around lines283–312. Caller `reconstruction/human_gameplay.py` blob `d8023e3d246fda6816144c63d7d2542268eb0357`, `_advance_original_management_turn` around1679–1695.
- Original source independently hash-verified in earlier Recoveries462–464 against the original `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, 4,714,541 bytes. Relevant original report: `research/GATE13_NATIVE_WRAPPER_CREATION_SITES_AND_DAY_REFRESH_AUDIT_RECOVERY462.md` section C, `research/GATE13_NEXT_SIDE_RESOLUTION_INDIRECT_POSTPONEMENT_AUDIT_RECOVERY463.md` exact instruction ranges. These earlier PE disassemblies were **reviewed**, not rerun here.
- Fresh local source inspection, tests, original EXE launch and Windows GUI verification **blocked by `caas.internal.errors.ClientError` even for trivial `bash echo`**. GitHub-hosted source reviews work. No original runtime result is implied.

## Original constructor/CFG contract — two distinct day phases

Native **PResults `0x4A7280` at `0x4A7317–0x4A7364`**:
1. For the current relative day, invokes **`0x615C10`** per calendar (original selected collections `0x947AD8` and `0x947AF0`) to assess postponed-event readiness. This has its **own** payload/virtual predicate, not the tomorrow-refresh routine.
2. For the next relative day, invokes **`0x616600→0x6165D0`** once per calendar. `0x6165D0` walks next-day source Event linked-list nodes and calls **`0x514520(Event)`**.
3. At original `0x514524`, `0x514520` checks **`Event+0x08` first**, and an existing non-null wrapper link makes it return **without resolving either Side**. Only on a clear event does it resolve virtual `+0x18` payload and require payload **`+0x44 & 0x60 == 0`** (`0x514536–0x514548`) before calling Side virtual `+0x00` (`0x51454A–0x514550`).
4. Native `0x514552+` **rechecks `Event+0x08` after Side0**; if Side0 created a wrapper via `0x510320→0x615F40→0x510BA0`, Side1 is **not** invoked. That full indirect producer chain is source-verified in Recovery463.

A **known already-linked** tomorrow Event is therefore a **source-accepted no-op for this particular `0x514520` callback**, independent of its underlying payload-flag knowledge. This is **NOT** a claim that the entire NEXT turn or postponed match automatically completes: current-day event preparation, registration, owner switching, source notification and other phases still have guards.

## New cross-code divergence — exact phase and control-flow order

Codex's new `PrimaryScheduleShadowState.prepare_ordinary_day(on_date, ...)` advertises the right two phases in its docstring: `4A7280: current 615C10 readiness, then tomorrow's 616600/514520`. But **the same shared body** loops `for current in (on_date, on_date + timedelta(days=1))`, and for *both* phases executes:

```python
entry = self.days[current][index]
if entry.payload_filter_bits is None:
    raise RuntimeError('Original NEXT current-day payload flags are unresolved')
if entry.wrapper_link_state != WRAPPER_LINK_CLEAR:
    raise RuntimeError('Original NEXT current-day wrapper lifecycle is unresolved')
if entry.payload_filter_bits & (1 if current == on_date else 0x60):
    continue
```

For **tomorrow**, that sequence contradicts original `0x514520`:
- **Known `WRAPPER_LINK_LINKED` + valid payload bits**: source `0x514520` skips/no-op; Codex raises `Original NEXT current-day wrapper lifecycle is unresolved`.
- **Known `WRAPPER_LINK_LINKED` + payload bits `None`**: source still skips on link *before inspecting payload*; Codex raises `payload flags are unresolved` before even testing the known link.
- **Unknown link**: **do not** infer no-op or clear from uncertainty. Codex must keep fail-closed behavior for missing original evidence; this report does **not** ask to silently treat unknown as linked.
- **Known clear link + payload bits0x20/0x40**: current Codex tomorrow branch does skip before Side resolution, consistent with native tomorrow flag exclusion (subject to verified payload-owner type). Do **not** alter that correct branch.
- The **current-day `0x615C10` half is a different source callback**. Do not automatically import tomorrow's known-linked semantics into current-day readiness without checking that routine's independent input gates.

The new normal backend `HumanGameplayController._advance_original_management_turn` increments the day and invokes this method on a staged controller. A raised exception **does not partially commit** the live controller because Codex's successful earlier atomicity fix rolls it back. Thus the new issue is a **spurious fail-closed refusal** of a source-known inert tomorrow event, **not** the old partial-calendar-mutation bug.

### Minimal static counterexample (not executed)

- `on_date=2000-08-22`, no current-day primary Event in the selected shadow bucket;
- the sole tomorrow Event on `2000-08-23` is an original typed `league_match` with **known `wrapper_link_state='linked'`** and `payload_filter_bits=0` (or missing/None);
- the original tomorrow source path `0x6165D0→0x514520` visits the linked event and immediately skips it without Side resolution, preserving its link; the Codex `prepare_ordinary_day` raises before it can finish this phase.

The date is illustrative near the actual Codex Aug23 blocker. **No evidence establishes the actual Cup9/League27 event was already linked**—its current problem is missing Side conflict/postponement behavior. Do not conflate the two. A linked-event counterexample should be tested independently of the Aug23 conflict case.

**Classification:** CONFIRMED from historical original instruction ordering and current Codex branch Python behavior; **conditional P0 source-lifecycle integration blocker** once the original wrapper producer is integrated, not an observed Windows11 click bug, and **not** a claim that arbitrary unknown wrappers are safe to skip.

## Codex-only bounded correction and tests

1. Separate **current-day `0x615C10` readiness** from **tomorrow's `0x514520` Side refresh** even if implemented in the same Python method. At minimum, in the tomorrow branch test **known linked `Event+0x08` before payload** and skip without invoking `resolve_ordinary_side`. For **unknown** link state, continue refusing or staging a source-qualified resolution; do not assume it is clear.
2. Construct deterministic shadow buckets `today=()`, `tomorrow=(linked typed direct Event,)`: assert known-linked tomorrow processing is a no-op for that event and does not overwrite its `wrapper_link_state` or Side cache. Repeat with `payload_filter_bits=None` so that payload uncertainty does not override the earlier source-proven linked exit. Keep a separate known-clear test with bit0x20/0x40 to verify no Side calls.
3. Include **clear linked-state Side0 that creates a wrapper mid-callback**; original `0x514520` must recheck Event link and skip Side1, not eagerly resolve a tuple of both Sides. This case still needs the native `0x615F40/0x510BA0` producer and original source flag/relative slot ordering; do not fabricate outcome now.
4. Add a quiet-day followed by already-linked tomorrow event to **real staged `advance_original_management`**: source-qualified tomorrow skip must not turn into whole-turn `RuntimeError`. Preserve test that truly unresolved link/postponement aborts *without* changing the live state, date or RNG.
5. Keep `research/GATE13_NEXT_CUP_POSTMATCH_DATE_LOOKUP_CERTAINTY_LEAK_RECOVERY470.md` as a **separate confirmed problem**: `GameState` Cup/procedural-League incident preflight still calls link-blind `next_match_date`, unlike the newer NEXT selector. Do not "fix" today's report by globally skipping linked events in every scheduling consumer.

**Implementation owner: Codex.** Worker made no game/runtime/code/test changes, original-process launches, Actions runs, branch merges, Gate13 acceptance or Windows11 release claims. Earliest incomplete gate remains **13**; 14–17 and verified original-scope Windows11 release remain incomplete.

## Recovery471 post-Codex f8b82d integration reclassification

_10 October 2026 KST, read-only concurrent branch recheck._

Codex just advanced from `dd69b6a8` to `f8b82d522a0ffa7cb52ac8593ed0ba94ee55e380` while Recovery471 was being recorded. **Most of the above source-known linked-tomorrow refusal is now FIXED in Codex implementation.** New `reconstruction/primary_schedule_shadow.py` blob `f8edbde67ed18d5601413591aea662784656c842` at `prepare_ordinary_day` lines352–375 splits the current-day and tomorrow branches. For a tomorrow Event with **known linked Event+0x08** and **known `payload_filter_bits`**, it now `continue`s before Side resolution. It also rechecks linkage between Side0 and Side1, as native `0x514520` requires. `reconstruction/test_original_next_event.py::test_readiness_short_circuits_but_tomorrow_update_rechecks_link_between_sides` verifies one injected mid-Side link scenario; the staged canonical run reportedly passes Aug23 and reaches subsequent match days.

**One narrower exact source-order edge remains:** the new method still does
`if entry.payload_filter_bits is None: raise` **before** tomorrow's `if entry.wrapper_link_state == WRAPPER_LINK_LINKED: continue`. Original native `0x514524` reads Event+0x08 and returns early *before* any payload `+0x44` check. Thus `known-linked` tomorrow **with unknown retained payload flags** still raises in reconstruction where native `0x514520` would skip the callback. This matters for source-incomplete/older restored state; no evidence it occurs in the current canonical fresh-game fixture sequence. Do not force unknown links clear, invent payload bits, or change current-day `0x615C10` semantics. Narrow regression: `tomorrow known-linked, payload_filter_bits=None` must exercise the native link-first exit; test separate from `tomorrow wrapper_link_state='unknown'`, which must remain fail-closed until source-qualified.

**Status change:** classify former *general* known-linked tomorrow rejection as **RESOLVED in Codex** (hosted test results reported by Codex; not independently rerun), retaining **one conditional P1 input-state ordering discrepancy**. Historic initial Recovery471 report remains unchanged as a branch-specific finding, with this reclassification appended. The previously identified Cup/procedural-League `0x5127A0` date-only eligibility leak from Recovery470 is still not fixed by these changes. Gate13 remains OPEN for end-to-end pre-match/results/return and physical Windows11 acceptance.
