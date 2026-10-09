# Recovery 462 — original native postponed-wrapper creation is guarded and source-specific, not a global day invalidate

_10 October 2026 KST. Continue the exact Recovery461 wrapper-lifecycle question. Independent audit only; Codex retains reconstruction/gameplay, CI, Windows11 acceptance and all gate closure. No original EXE execution, binary/art/save upload or implementation edit._

## Live checkpoint and exact original identity

Started at `main` **`4121d8c63cdf42bb99993ecab91bc3d83e28ad69`**, `research/CURRENT_STATE.md` still requires **original PMenu, EAMail, Squad and NEXT ordinary playability** first. `agent-runtime` generation461 and `worker_role=audit_only`, `implementation_allowed=false`. Latest Codex **`0ae745d1b56f45cade460f03cd893849a2f53b45`**, no new implementation commit at checkpoint.

Canonical authorized private `/mnt/data/fm2001_private/footballmanager.exe`: **4,714,541 bytes**, SHA-256 independently rechecked **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. Native x86 disassembly by GNU `objdump -d -Mintel`, and direct `call rel32` scan of the **private** full disassembly; original bytes are not in Git.

## A. Native wrapper creation has two mandatory guards and a concrete bidirectional link

Original **`0x510BA0`** receives an Event object (`ECX`) and literal small source discriminator (one stack argument). It:

1. Checks **`Event+0x08 == 0`** at `0x510BA3..0x510BA8`; when an existing wrapper link is non-null, exits at `0x510C08` without creating another.
2. Resolves **event virtual +0x18 → match payload** and checks **`payload+0x44 bit0x40 == 0`** at `0x510BAA..0x510BB8`; if set, it exits without linking.
3. Allocates a **0x1C-byte `PostponedEvent`**; source ctor `0x510380` uses original calendar family selected by `Event::0x510300`; stores **`new_wrapper+0x14=old Event`**, **`new_wrapper+0x18=caller discriminator`**, and concrete vft **`0x7C9FE8`** at `0x510BD3..0x510BE4`.
4. Writes **`old Event+0x08=new_wrapper`** at `0x510BF8`. Calls original **`0x615A60`** through the Event's selected calendar at **requested relative slot `old Event+0x10 + 7`**. The requested 7-slot displacement remains subject to `0x615A60` conflict resolution; **not** proof every original postponement is precisely one week after the old absolute date.

**Exact:** link-pointer ownership and mandatory two guards, wrapper type, native insertion request. **Unknown:** whether this exact original source routine can allocate a null wrapper and what downstream duplicate/identity handling does in that rare path. Do not claim unconditional creation on all calls.

## B. Seven direct call sites and their *different* source conditions

Scanning the canonical executable's disassembly for direct `CALL 0x510BA0` yields **seven exact call instructions**:

| Original callsite | Immediate source condition / call argument | What can be claimed |
| --- | --- | --- |
| **`0x4A801F`** | PResults user/fixture sweep: source original match/Event **`Event+0x08==0`**, payload **`+0x44 bit0x20 clear`**, resolved one of the two original `Side` participant references equals selected source club; passes **0** | Qualified user/club/event-dependent wrapper creation, not every event |
| **`0x5E3C34`** | Original source selector `0x615D10` resolves eligible event; source slot is before **`current_date+5`** at `0x5E3C24..0x5E3C2E` after further participant conditions; passes **2** | Date-window-bound wrapper operation, not calendar-global |
| **`0x615C33`** | `0x615C10` iterates one original selected calendar **day bucket**; requires resolved payload **`+0x44 bit0 == 0`** AND **event virtual +0x0C returns zero**, then passes **1** | Per-bucket and flag/polymorphic predicate; not all future events |
| **`0x615DD7`** | `0x615DA0` invokes `0x615D10` for event eligible under caller's query, invokes payload virtual **`+0x64`** with original event relative-slot index, calls wrapper creation only if conflict predicate is nonzero; passes **1** | Dynamic lookup can mutate eligible event link state; the reader is not intrinsically pure |
| **`0x615FD2`** | Original **`0x615F40`** local event-ordering/related-event conflict branch at `0x615FB6..0x615FD2`; chooses one original Event to wrap; passes **0** | Ordering-specific source mutation |
| **`0x616003`** | Alternate `0x615F40` branch: source relative ordering comparison and **other match payload+0x44 bit0 set** at `0x615FF2..0x615FFF`; passes **0** | Conditional other-Event wrapper |
| **`0x616013`** | Final `0x615F40` fallback wraps the other Event on unresolved ordering; passes **0** | Local conflict fallback, not every global entry |

The direct scan is **complete for statically encoded direct `CALL rel32` instructions in this observed canonical disassembly**, not a mathematical proof that no *indirect* or runtime-generated call can ever target the same function. Additional Event/link mutations by other functions are not excluded. Multiple branches can reach the same call on different paths; the number seven counts instructions, **not runtime calls or seven distinct match classes**.

## C. PResults date-stage native work is split: current-day wrapper checks vs next-day participant refresh

The original PResults setup **`0x4A7280`** at **`0x4A7317..0x4A7364`** performs distinctly scoped operations:

- Computes `current_date(0x9847FC)−calendar_base(0x947AE0)` for calendar **`0x947AD8`**, calls **`0x615C10`** on *that current-day bucket* at **`0x4A732E`**.
- Computes `current_date−calendar_base(0x947AF8)` for separate calendar **`0x947AF0`** and invokes the same **`0x615C10`** for its current-day bucket at **`0x4A7349`**.
- Then invokes **`0x616600`** for **both** calendars at **`0x4A7353`** and **`0x4A735D`**. That helper delegates to **`0x6165D0`** with **relative slot `current_date−calendar_base+1`**, which iterates **next-day events** and invokes **`0x514520`**.
- Original `0x514520` checks **`Event+0x08==0`**, non-null Event virtual +0x18 payload and clear payload **`+0x44 bits0x20 and0x40`** before invoking concrete participant **`Side` virtual +0x00**, with a second Side only if the wrapper remains unlinked at that point. This is **participant-resolution work** and may have source side effects, **not** a direct `0x510BA0` wrapper creation in this helper's bounded body. **Recovery463 source clarification:** participant resolution can itself call `Side::0x510320→0x615F40→0x510BA0` and thus trigger guarded wrapper creation *indirectly*, including a related Event selected from the same or neighboring bucket; the bounded `0x514520` still contains no direct call to `0x510BA0`. See `research/GATE13_NEXT_SIDE_RESOLUTION_INDIRECT_POSTPONEMENT_AUDIT_RECOVERY463.md`. Do not treat 'tomorrow refresh' as categorically read-only.

This separates the original source's **current-day postponed-wrapper checks** from **next-day Side resolution**. Neither shown operation writes `unknown` to every future Event link or blindly relocates all scheduled games; however other original producers and their wider schedule side effects require further inspection before a clean model may certify arbitrary future links clear.

## D. Exact current Codex mismatch and minimum valid staged modeling

Recovery460 demonstrated that Codex `HumanGameplayController.advance_original_management_turn` calls `state.invalidate_primary_schedule_wrapper_links()` **after every calendar increment**, and `PrimaryScheduleShadowState.invalidate_unmodelled_wrapper_links` (`primary_schedule_shadow.py` **`0x`-free Python implementation around lines269–285**) downgrades **all** non-linked original-shadow entries to `WRAPPER_LINK_UNKNOWN`. Recovery461 showed that even a quiet day therefore loses the future source-qualified fixed-League header match. Due-day paths can then fail their original ordered match guard with a date already advanced.

**Now source-specific positive constraint:** each of the seven observed direct native wrapper-creation instructions occurs under its **own dynamic event, date, participant or competition conditions**, while PResults' direct bucket work is scoped to **today** (link creation) and **tomorrow** (Side resolution). This evidence supports implementing a **source-scoped event lifecycle/update log** rather than treating every untouched date bucket as though the original explicitly invalidated it. This does **not** independently establish that retaining all previously clear future fixtures is safe. The Codex shadow's conservative unknown was intentionally protecting unresolved source producers. Source identity and actual scheduling mutations must be proven before requalifying even the fresh fixed-League subset.

**Codex-only implementation handoff — immediate sequence:**
1. Build a fixture/event-specific model of **`0x510BA0` guard and link transfer** with original Event identity, selected calendar family, ordinal/relative slot, wrapped event +0x14, selector-side references and status word. Do not mutate the entire schedule merely due to a date increment.
2. For known original day processing, explicitly model **`0x4A7280` current-day 0x615C10 and next-day 0x616600→0x514520** only when this original phase is actually reached; also account for `0x615DA0` lookup-induced wrapper mutation and source `0x4A801F/0x5E3C34/0x615F40` branches before declaring an event clear.
3. Preserve **UNKNOWN** for any event whose producer/owner cannot be qualified. Fail before changing calendar/RNG/AI results or use source-tested transaction/rollback if the next processing stage is unresolved; **never** stamp every unknown link as clear just to make the button function.
4. Add a **two-part regression** through the real bounded controller (not only shadow helpers): *(a)* a quiet-day advance with unchanged forthcoming fixed-League match that still shows correct native header when justified; *(b)* due-day original fresh qualified League fixture with exact source link status where human pre-match is reachable, and unknown/linked event that refuses without consuming date/partial state. Include symbolic Cup and original deferred postponement cases to show they remain bounded/fail-closed.
5. Wire **original PBg NEXT ID3 normal mouse action → source-qualified selector → existing bounded controller → actual match/PResults return**, with modal flags and multi-manager context; this UI remains unimplemented in latest Codex. Use two actual clubs and two human managers, external Windows11 receipt before gate closure.

**Do not spend the next implementation iteration fixing already-audited pixels, and do not rewrite a useful backend from scratch.** Gate13 functional loop is the priority. This research adds original-source conditions to the integration fix but is not itself a playable build.

## E. Verification boundaries and gate state

- **EXACT:** seven direct call instructions to `0x510BA0` in this canonical x86 disassembly, first two wrapper link/status guards, original wrapper object links/family and requested relative slot, source current-day vs tomorrow bucket walks in `0x4A7280`, and unchanged current Codex global invalidation.
- **PARTIAL:** all native indirect callers/other status or schedule mutations, original calendar-zone criteria for calling these stages, fresh fixture's full safe lifecycle through matches, +0x44 status meaning, specific original game's acceptance and saved-state behavior.
- **UNVERIFIED:** original Windows11 game execution and UI; normal Tk gameplay press, real original match-watch presentation, human match finish, actual two-manager play, full original save/reload and installed-release parity.

**AUDIT ONLY. Gate13 OPEN. Gates14–17 and the verified full original-scope Windows11 release remain INCOMPLETE.**
