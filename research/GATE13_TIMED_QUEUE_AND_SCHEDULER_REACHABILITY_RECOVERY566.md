# Recovery566: timed original queue removes due nodes by caller flag, not callback return

**13 October 2026 KST.** Gate 13 original first-user lifecycle. **Original identity:** owner-authorized privately materialized `footballmanager.exe`, 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Verified against raw file; **no original executable launch**, no original GUI observed, no private source binary copied into Git. The following conclusions are limited to source-static code and verified direct callsite inventory.

## Original timed queue 0x613EE0, separated from selected-human conditional drain 0x614080

The earlier source evidence identified `0x613EE0` as a timed queue processor, distinct from the two selected-human `0x614080` drains at `0x4259B5` and `0x412F1F`. The original x86 now establishes its full **bounded removal predicate**:

- `0x613EE5` sets global owner `+0x0C=1` (processing), `0x613EEC` resets owner `+0x10=0`. `0x613F00` compares the node event's native due time `event+0x04` to **first function argument** (`[esp+0x10]`, before nested pushes); the signed `jg` branch at `0x613F03` skips *future* events.
- For a due event, `0x613F07` invokes event virtual **`+0x10`**. Its return value is **not** tested to decide whether to remove the node. The immediately following `0x613F0A` **overwrites EAX** with the **second function argument** at `[esp+0x14]`; `0x613F0E` tests that independent argument. Nonzero removes the node via `0x613F1C -> 0x4EA190`; zero leaves it. Thus both callback return 0 and callback return 1 lead to the **same removal decision** for a fixed caller flag, though their *internal callback side effects* may differ.
- All FIVE direct `.text` callsites `0x41A364, 0x41A475, 0x43216C, 0x4A8084, 0x5E3335` explicitly push literal **1** as the removal flag and load first argument from original date owner `[0x9847FC]`. Therefore on these five source direct paths the processor removes every due event after its callback, regardless of virtual return. No indirect callers were proven or excluded.
- At `0x613F30`, processor clears owner+0x0C. If callbacks marked owner+0x10 deferred during reentrancy, `0x613F40` runs **`0x614080`** and `0x613F45` resets deferred. This can trigger additional original virtual `+0x04`/`+0x18` paths. Then **for each registered human** `0x613F57..0x613F75` invokes `0x5CF990` on current user `+0x6B4` list. Those postprocessing effects are not represented by the existing source-only queue projection.
- After first selected-human conditional drain `0x4259B5`, native `0x4259C0 -> 0x5CF830 -> 0x42C9F0` performs a *different* user-owned linked-list disposal, whose direct body frees owned nodes and vft resets; it is not another call to `0x613EE0`. Do not collapse the global event queue and per-user event lists into one synthetic structure.

**Consequence for future implementation:** the existing `original_teamselect_queue_lifecycle.py` models only source-observed results of conditional `0x614080` and Continue cleanup. A future native timed-queue port **must** use the caller-specified removal flag rather than mistakenly deleting on truthy callback results, run deferred conditional drain when source calls it, and account for user+0x6B4 postprocessing. This source evidence does not prove any of those callbacks run before first human click or are RNG-free.

## New independent direct-caller boundary on a suspected first-user event producer

The original inner event construction chain `0x426220`, analyzed in Recovery565, has exactly **one syntactic direct caller**: `0x4041D1` in `0x404110`, guarded by `0x4041BF -> 0x4037B0` returning 1. `0x404110` likewise has exactly **one direct caller** at `0x616830` inside `0x616620`, itself conditional on original `0x616811 -> 0x403640` byte matching `[caller+0x14]` at `0x616816`. Finally `0x616620` has exactly **three direct callers**, `0x4F7F0F`, `0x4F7F1B`, `0x4F994E`, from competition/scheduling source sites. They are **distinct source sites from `0x4D8E90` selected-club callback**.

These gates exclude treating `0x426220` as an **unconditional direct** first-human event producer. They do **NOT** prove those competition/career paths never execute before TeamSelect, exclude an indirect caller, or establish whether a generated event survives either first human drain. Still necessary: source call graph from shipped New Game `0x53109E` CRT initialization through TeamSelect; exact per-class event queues, destructor/rollback, and full shared CRT costs.

## Reproducible independent proof and next work

A private Python verifier over complete Intel GNU objdump `.text` of the SHA-matched original source **passed 33 instruction-address assertions plus all four exact direct caller sets**, with originals never executed. Corresponding persistent assertions were added to `research/audit_original_teamselect_continue_static.py`; they are part of the currently **unopened** SupportStart branch, not accepted gameplay. No exact feature-head Python suite/CI or native GUI acceptance is asserted. This remains source-only evidence.

**Next:** follow the `0x4F7F0F/0x4F994E` producer caller reachability from actual new-game sequence, and type concrete original events flowing through `0x613EE0` vs `0x614080`. Then source-audit PSupportStart Cancel/staged staff unlink and implement the *player-visible* immediate first human+13 pairs+six staff+seven-row name/staff modal, actual input/return/persistence, followed by Inbox/R1/all shipped leagues and Windows 11 Gates 13–17 audit.

## Recovery566 follow-up: close the *direct* `0x426220` scheduler ancestry to Continue/time paths

Further SHA-verified x86 source tracing narrows the remaining supposed early first-user event producer significantly:

- Original `0x4F7F0F` and `0x4F7F1B` are inside one original function **`0x4F7C00`**, whose **sole direct original caller is `0x4C4381`**, *inside* TeamSelect Continue/new-game owner `0x4C41C0`. In the same function's straight-line normal setup, `0x4C4275` has already cleared pending global events, then `0x4C4304` has begun precompetition initialization, and only then `0x4C4381` calls the scheduler. Thus these two direct scheduler-entry calls are **AFTER normal Continue**, not calls inside the earlier first selected-club click.
- Third scheduler call `0x4F994E` sits inside original function beginning **`0x4F9010`** (no intervening return instruction in the decoded continuous function path). **Its only two direct original callers are `0x4A86AA` and `0x4A878B`**, part of original game-time simulation paths. This is also separate from native TeamSelect selected-club handler `0x4D8E90`, which does not directly call either route.
- Combine the full unique direct-call chain:
  `0x4DA4A5 (TeamSelect Continue event42) -> 0x4C41C0 -> 0x4C4381 -> 0x4F7C00 -> 0x4F7F0F / 0x4F7F1B -> 0x616620 -> 0x616830 -> 0x404110 -> 0x4041D1 -> 0x426220`.
  The other two time/simulation callers reach `0x4F9010 -> 0x4F994E -> 0x616620` and share its later conditional chain.
- This is a **source-verified exclusion** of an *unconditional direct* `0x426220` callback or its nested `0x426600` constructors **before the initial TeamSelect human click**. An external original call through a function pointer, old/save-game state, a queued callback already present, or one of the other 175 original enqueue sites would require independent investigation. No universal pre-first-human empty event-queue claim is established.

The private independent regression now passes three additional exact direct-caller sets and four original function call addresses on the hash-matched PE. Source audit script extended with these contract checks. This is **not** an original GUI observation or an accepted startup RNG checkpoint, and no Windows11 gameplay/CI was run for this branch.

**Next immediately executable task:** identify any remaining source reachable enqueue owners between global owner construction `0x613E40` and source selected-human queue drains. In parallel, source trace SupportStart Cancel's staged staff-list/destructor persistence and proper TeamSelect human unselect effects, so a real 7-row modal can be integrated without corrupting original users or RNG. Keep Gate13 open.
