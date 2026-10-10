# Recovery 457 — Original NEXT control acceptance and the shortest safe Codex integration path

_10 October 2026 KST. Independent original-file Gate13 P0-D **AUDIT ONLY**. Continue Recovery456, do not restart earlier event/scheduler tracing. Codex alone owns reconstructed gameplay source, builds, Windows 11 test and gate/release acceptance._

## A. Verified exact checkpoint and ground truth

Starting repository **main `ef4505c516ab142cf724a33ffa7175e7788145cd`**, Codex implementation branch **`0ae745d1b56f45cade460f03cd893849a2f53b45`**. Read binding `research/CURRENT_STATE.md` and `agent-runtime` generation456, `worker_role=audit_only`, `implementation_allowed=false`. Original private **`footballmanager.exe`** size **4,714,541** and exact SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`** independently rehashed. Original program was **not** run; no licensed art/exe/save/disassembly committed.

Reproduce with:
```
objdump -d -Mintel --start-address=0x430928 --stop-address=0x4309c9 footballmanager.exe
objdump -d -Mintel --start-address=0x5d3900 --stop-address=0x5d39b8 footballmanager.exe
objdump -d -Mintel --start-address=0x652b50 --stop-address=0x652bb6 footballmanager.exe
objdump -d -Mintel --start-address=0x652cf0 --stop-address=0x652d78 footballmanager.exe
objdump -d -Mintel --start-address=0x64f7a0 --stop-address=0x64f85a footballmanager.exe
objdump -d -Mintel --start-address=0x432690 --stop-address=0x432708 footballmanager.exe
objdump -d -Mintel --start-address=0x432190 --stop-address=0x4321ee footballmanager.exe
objdump -d -Mintel --start-address=0x5d3ac0 --stop-address=0x5d3af9 footballmanager.exe
```

## B. EXACT source button ownership and selected input-state gates

Original `PBg` registers its three header children at `0x43092B..0x4309C9`. The right-hand original **NEXT/MATCH** child is **`PBg+0x524`, ID3**, initialized at `0x430995..0x4309B4`, positioned at **x=700, y=0** via `0x5D3900` at `0x4309B4..0x4309C9`. The original `back_5.444` is **100×380** (four 100×95 rows). Its original source identity and concrete **[700,800) × [0,95)** hit region were verified earlier. Note ID1 EAMail and ID2 PMenu are distinct siblings with their own different actions.

The original shared control event acceptance method **`0x64F7A0`** has two explicit *necessary* conditions using the control's **`+0x18` DWORD**, before it can return nonzero:
- **`flags & 0x02 != 0`** at `0x64F7A5..0x64F7AF` (otherwise return0 at `0x64F854`);
- **`flags & 0x10 == 0`** at `0x64F7B5..0x64F7BA` (otherwise return0 at `0x64F854`).

After those masks, `0x64F7A0` also conditionally calls the control's **parent-owner virtual `+0x0C`**, performs control virtual `+0x1C(1)`, dispatches source notifications and returns a boolean. These owner/other-state checks mean **source geometry + the two masks are not alone sufficient** proof that a click is accepted.

Two original common control-input methods **`0x652CF0`** and **`0x652B50`** both invoke `0x64F7A0`, but have distinct source state paths: `0x652CF0` checks the control **`+0x50` pointer**, uses an optional `0x652B40` state step, and only on accepted state calls its parent **virtual +0x10** via **`0x652D59`**; if +0x50 is zero it delegates to `0x652B50`, which also checks parent virtual+0x0C and calls parent virtual+0x10 at `0x652BAB`. Do not claim every control uses the same direct branch or convert a bitmap hover test into action acceptance.

Original **`PBg::0x432690`** is the concrete final **parent virtual +0x10** action handler (confirmed Recoveries441–442). It rejects null events, reads **`event+0x20`** and cases:
- **ID1** → `0x4326D6` original PEAMail factory `0x482BF0(0x65)` and native modal/stack helper;
- **ID2** → `0x4326AE` original PMenu popup/stack branch;
- **ID3** → `0x4326A4` **pushes literal0**, calls **`PBg::0x432190`**, then returns.

**Important separation:** `0x432690` itself has no dedicated “if header caption says MATCH” test inside the ID3 case; eligible events, manager, roster and branch-specific gameplay result are processed *inside* `0x432190` and its callees. But **this does not mean ID3 bypasses** modal owner/input guards: they run at earlier common control stages.

Original **NEXT bitmap selection `0x5D3AC0`** uses the **same +0x18 flag bits** to pick source rows; it selects disabled/non-bit2 behavior, bit0x10 row, hover bit0x08 row, normal otherwise. The original `0x64F7A0` rejects input if bit0x10 is set, regardless of which artwork row is visible. **Do not infer the semantic name “pressed” or “disabled” for this bit without state producers.**

## C. Exact newest Codex runtime: artwork and hover are present, gameplay click still absent

The current Codex `reconstruction/original_management_next.py` blob **`407d9b2249f202c8c49f10de944a5728b4d3a9bf`** already implements:
- `native_next_at_point` true precisely inside source **(700,0,100,95)**;
- bitmap row selection `native_next_source_row` with +0x18 flag **bit2 necessary / bit0x10 select distinct row / bit8 hover**;
- native source caption from qualified retained match date rather than inventing a match in the renderer.

Codex host **`reconstruction/original_game_host.py` blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`** initializes **`self.management_next_flags=2`**, draws original crop/caption at `_draw_management_next_control`, and its `on_fixtures_pager_motion` around lines1764–1769 calls `native_next_at_point` to set/clear **hover flag bit0x08**. This matches the visual-state shape but *is not an input action*.

The same host's **`on_click` management branch around 2330–2415** handles PMenu open, Squad row press, League Fixtures pagination, menu row selection and fixtures grid; it **never calls `native_next_at_point` nor an advance method**. The original-looking button is therefore **nonfunctional through ordinary mouse clicking** on both main and Codex. This remains the important P0 defect, unlike the Recovery454 PMenu false positive corrected in Recovery455 (the PMenu motion-dismiss helper IS wired).

Codex already has **`reconstruction/original_management_advance.py` blob `6343fe0a23112d32d8023243b0e9a7b83d2eaf9b`** and **`HumanGameplayController.advance_original_management_turn` in `reconstruction/human_gameplay.py` blob `980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`**, around line1571. These are meaningful, fail-closed **backend** work, not evidence of UI gameplay completion. The method needs `next_match_date`, **`selector_source_qualified=True`** from a genuine original event selector, `container_end_date` and turn-length/source context; it stops at a pending human event. It does **not** by itself close source modal/roster checks `0x407FE0` and `0x407F40`, scheduled EAM delivery/cleanup, multi-manager cycling, original PResults, or an accepted clickable UI.

**Verified main/Codex comparison:** main host lacks the click route *and* the standalone bounded `original_management_advance.py`; Codex has the **backend component only**, still lacks the click route. Thus source parity isn't obtained by either simply copying main's older prototype date skip or by asserting “no match simulation exists.”

## D. Codex-only implementation handoff — avoid more bitmap research

| Priority | Minimum implementation stage | Falsifiable acceptance |
| --- | --- | --- |
| **1: P0 immediate** | Make original management `on_click` resolve **PBg ID3** after source-qualified owner/modal guards and sprite flags; ensure the exact native rectangle and event-ID acceptance; separate hover from click; avoid synthetic press on an unqualified disabled state | With a real game canvas open, mouse click inside the visible NEXT control enters a *source-qualified* action or an explicitly evidenced refusal. Clicking outside never advances and hover alone never changes date/state. |
| **2: P0 game-state** | Use Codex's **existing** fail-closed backend NEXT selection/turn method; supply authentic manager-specific `0x615D10` candidate/context, not `header_match.scheduled_date` by visual inference or `selector_source_qualified=True` unconditionally. Retain dynamic wrapper invalidation and source match-pending semantics | At least one eligible fixture and one source-null/unknown fixture exercise distinct correct outcomes, with calendar/state snapshot before/after; no fabricated one-day increments. |
| **3: P0 validation/modals** | Integrate source `0x407FE0` ordered eligibility and `0x407F40` adjusted 11-player threshold, warning acceptance/rejection and conditional Squad0xCE return, then PResults and selected-manager restoration/rotation | Tests cover accepted versus rejected warnings with identical initial state, a human match-day outcome, PResults return and non-match turn; rejection doesn't secretly process RNG/game day. |
| **4: other P0 screens** | Complete separate PBg ID1 EAMail inbox, PMenu0x65, Squad tabs3/4/5, PMenu Save0x321 / Return0x323 and original 28-child types | Full standard user loop New Game→club→Squad→NEXT→results→inbox→back→save/reload→return, **two unrelated original clubs and two managers**. No direct developer-seam shortcuts. |
| **5: acceptance** | Run real Windows11 normal pointer/keyboard and original installed-release checks **after** source-equivalent actions and game simulation are wired; preserve frozen modernization | Source-backed Gate13 pass first; Gates14–17/verified Windows11 release only after separate audits/receipts. |

**Important release scope:** a score-only backend simulation does not establish the original animated match-watch presentation or “3D players running around.” Those remain separate Gate14+/full-scope functionality requiring independent evidence. No source or Windows acceptance work in this audit implies those gates are done.

## D2. Second verified step — do not reuse the visual header projection as a fully qualified native NEXT event

The clean original management snapshot carries a **`ManagementHeaderMatchView`** with only `fixture_id, competition_name, home_short_name, away_short_name, scheduled_date` (from `reconstruction/gate13_management_source_data.py`, latest Codex blob **`4181db2efc218f5bf5c026767b111b3394b7789f`**). `ManagementSourceDataBridge.management_header_match()` around line1007 builds that display view using **`state.primary_schedule_shadow.direct_fixed_league_header_candidate`** and additional Premier League fixtures/results checks. Its own source docstring correctly limits it to the **Recovery401 fresh direct fixed-League** subset.

The underlying current Codex `primary_schedule_shadow.py` blob **`5d8fbcbf411a308375f209fcae00d068fb55dea6`** makes this scope unmistakable:
- `direct_fixed_league_header_candidate()` (line287) only returns **`node_kind='fixed_league_match', competition_id=0, competition_context=0`** with 4-token fixture identity, source-matching direct participant IDs, status not already played and **`wrapper_link_state=WRAPPER_LINK_CLEAR`**.
- If a relevant symbolic source ref, other competition or unknown wrapper state occurs, it **returns None / fails closed** rather than claiming a native candidate.
- The display model does **not** retain the original live Event pointer, its `Event+0x08` linkage, `+0x10` calendar-family-relative bucket index, native payload flag `+0x44`, source Side reference identity, or the deferred update operations in `0x615C50`. It only projects selected original-safe display text/date for a subset.

The original header's **`PBg::0x432760`** call chain at `0x432767..0x432799` obtains manager `0x4139D0`, user's selector `+0x5B4`, original global date `0x9847FC`, calendar `0x4079D0` and invokes **mutable `0x615DA0`** before storing the **returned Event pointer `PBg+0x170`**. Recovery447 proved this lookup may create a `PostponedEvent` through native source conflict rules during specific lifecycle refreshes. Ordinary NEXT's **`0x615D10`** candidate/eligibility path is related but **not identical** to this header read/refresh. Thus a visual header date is neither a complete source selector proof nor evidence that its returned match is exactly the NEXT event in symbolic cup/rescheduled cases.

**Potentially severe implementation shortcut to avoid:** a future adapter should not call:
```python
controller.advance_original_management_turn(
    next_match_date=frame.presentation.header_match.scheduled_date,
    selector_source_qualified=True,
    ...,
)
```
merely because `header_match` is non-null. That is a narrow *display* view with no exact native event identity or mutation/owner evidence; the backend explicitly requires the source-qualified selector. This report does **not** call the existing display bridge incorrect within its declared bounds. It says **promoting it to general gameplay authority would cross an unsupported source boundary**.

**Codex handoff refinement:** create/retain a separate source-qualified runtime selector result (including identity, competition/calendar family, relevant wrapper/flag certainty and selected manager owner) for real NEXT. Use the existing conservative `direct_fixed_league_header_candidate` *only in states its precise contract supports* and fail closed on unknown/symbolic cases until the correct original event/candidate producer is modeled. Test at least one fixed League fixture and one unresolved Cup/postponed candidate so a drawn MATCH caption cannot accidentally authorize the wrong state transition.

## E. Source and implementation uncertainty

- **EXACT:** canonical executable hash, original PBg ID3/0x432190 dispatch, accepted input flags bit0x02/0x10 at shared method `0x64F7A0`, common parent vft+0x0C/+0x10 chain, native bitmap rectangle/row flags, latest Codex hover/bitmap state, normal click gap, and bounded Codex backend method existence.
- **PARTIAL:** the exact dynamic vtable of PBg child +0x524 at every lifecycle point, +0x50 branch selection, event-source enabled/owner guards, input phase, retained header selector acceptance, roster modal text/actions, EAMail/multi-manager event timing.
- **UNKNOWN:** original Windows11 runtime input, the game’s correct presentation of all qualified and rejected states across clubs, full match-watch animation and installed-release parity.

**AUDIT ONLY — no gameplay code edits, Codex branch commits, test/CI dispatch, asset or user save changes, merges, gate closure or Windows11 release claim. Gate13 earliest incomplete; Gates14–17 and verified original-scope Windows11 release incomplete.**


## Recovery471 addendum — genuine staged NEXT entry exists; native header press still never invokes it

_10 October 2026 KST; strict audit-only same-source independent handoff. This updates only the previous Codex integration seam, not the native rules established in Recovery457._

**New genuine backend:** Codex `dd69b6a8cf609a2e7c1c7163d486bd126b96f65f` now provides `HumanGameplayController.advance_original_management()` in `reconstruction/human_gameplay.py` blob `d8023e3d246fda6816144c63d7d2542268eb0357` (~line1606). Unlike the older `advance_original_management_turn(next_match_date, selector_source_qualified=True, container_end_date,...)` called by tests, the new method stages a controller copy, calls `primary_schedule_shadow.ordinary_next_candidate` against the actual managed club, source CupRef resolver and Side registration guard, derives an original `OriginalManagementAdvanceTarget` with retained primary calendar end and commits on success. A source-null result is recognized only after this attempted qualified query, not from the painted header. Codex has reported canonical Southport Aug19 pending-match calculation and fresh-process save/reload and 203 focused tests (its independent report `GATE13_NEXT_EVENT_LIFECYCLE_2026-10-10.md`); does **not** claim normal pointer route or full Windows playability. Known unresolved Aug23 Cup9/League27 conflict/postponement still refuses safely. Retain these advances; do not ask Codex to reinvent the controller.

**Newly inspected live GUI call-site:** Codex `reconstruction/original_game_host.py` blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`: initial `management_next_flags=2` (~417); `canvas.bind("<Button-1>", self.on_click)` (~515); `on_fixtures_pager_motion` (~1765) toggles source bit8 hover inside `native_next_at_point`; `_draw_management_next_control` (~1421) paints authentic art and caption from a **read-only** `header_match`. But the complete management branch of `on_click` (~2287–2409), after initial resource-load and PMatchInfo modal guards, handles PMenu open, Squad rows, fixture pagination, PMenu rows and fixture grid. It never invokes `native_next_at_point`, `advance_original_management()`, or `play_original_user_primary_match()`. The older P0 normal-click gap is **still present despite new genuine backend progress**. `original_management_presenter.py` remains a three-panel snapshot presenter, not the native PPreMatch/PResults event owner.

**Correct low-risk Codex-only integration seam now available:**
- Route a *true* accepted PBg **child ID3** input (native `0x432690`) through original common control flags **bit2 required**, **bit0x10 clear**, parent/modal/owner gates and the exact `[700,800)×[0,95)` geometry. Respect in-progress asynchronous resource-family load, PMenu popup ownership and PMatchInfo modal stack. The native header bitmap row/hover alone never authorizes input.
- On accepted ID3, call the **new staged `gameplay.advance_original_management()`**, not prototype skip-to-match, painted `header_match.scheduled_date`, or legacy direct `advance_original_management_turn` with unqualified `selector_source_qualified=True`. Capture no-change refusal. Never auto-invoke `play_original_user_primary_match()` just because the bounded controller returned `pending_primary_entry`: original `PBg::0x432190` has a guarded pre-match player/roster warning and result/modal branch, not an unconditional calculator.
- Reconcile original return/stack paths from Recovery442: under guarded conditions `0x4324B9→0x482BF0(0xCE)` returns to Squad, `0x431F70` creates full-size original `PResults`, and a distinct `0x4325DF` path returns to PStartMenu. A simple `host.redraw()` of the old currently selected panel is **not sufficient native panel semantics** after a successful turn.
- **Responsiveness risk must be measured, not guessed.** Codex reported 8.05–12.82 seconds for canonical successful bounded turns in its local test process; direct synchronous game staging on the Tk `<Button-1>` handler could block event processing for that duration. This is a *conditional architecture/performance risk*, not a measured Win11 GUI freeze. Optimize reconstruction-only overhead or schedule UI-safe work only with proven original input/transaction ordering; do not invent a new UX, loading popup or asynchronous pre-match interaction to conceal it.
- Falsifiable end-to-end checks: exact rectangle edges, hover-only date invariance, source-disabled/bit0x10/modal rejection, active PMenu ownership, successful quiet day retaining next MATCH projection, refused Aug23 conflict unchanged live snapshot, queued human PPreMatch suspended before calculator, followed by accepted match→native PResults→original return panel; two independent clubs; disk save/fresh reload. Distinguish backend test artifacts from actual Windows11 normal mouse operation.

**Separate audit blocker:** Recovery471 identified that `prepare_ordinary_day` wrongly raises for source-known already-linked *tomorrow* events before payload flags, whereas original `0x514520` returns immediately on Event+0x08 link. See `GATE13_NEXT_TOMORROW_LINKED_EVENT_SOURCE_SKIP_RECOVERY471.md`. Recovery470 also documents a different Cup/procedural-League `0x5127A0` post-match date-only certainty leak. Do not close either by bypassing genuine `ordinary_next_candidate` source qualification.

**Audit-only;** no GUI code modified, no tests/Actions/new package/Win11 execution, no merge or gate closure. Gate13 OPEN, Gates14–17 and full Windows11 release incomplete.
