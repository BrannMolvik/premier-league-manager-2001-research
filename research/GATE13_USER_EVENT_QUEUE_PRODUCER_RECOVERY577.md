# Recovery577 — original user-event enqueue callback and queue-drain ownership

**13 October 2026 KST. Gate13–17 OPEN.** Source: privately authorized original `footballmanager.exe`, 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original binary was inspected statically, not executed, and no private bytes are uploaded to Git.

## Original source call relationships

- Normal TeamSelect club acceptance is `0x4D8EF8 -> 0x413BB0` (the only direct caller of `0x413BB0`). It creates/registers the human; this is **not** itself a global queue enqueue.
- The **second** shared queue drain is `0x4D8F19 -> 0x412EF0` (the sole direct caller of `0x412EF0`); its `0x412F1F -> 0x614080` call uses original global queue owner `0x947AA8`. The drain occurs near the start of `0x412EF0`, before this function's later list cleanup/reallocations.
- The separately compiled registered-human event handler **`0x413020`** walks the original human linked list (+0x9CC) and conditionally reaches **`0x413357 -> 0x613EC0`** to enqueue an event into that global queue. It has exactly one **direct** caller, `0x5CFA48`.
- Native callback **`0x5CFA20`** invokes an object's original virtual method at **vft+0x3C** (`0x5CFA28`), checks its result at `0x5CFA2B/0x5CFA2D`, and only on the eligible branch calls `0x5CFA48 -> 0x413020` with original registered-human owner `0x874C10`. This callback is in actual original vtable slot **`0x7BD574 -> 0x5CFA20`**. Its concrete event object, predicate target and timing relative to first-human startup remain unidentified.
- Original nested first-user constructor `0x60CE70` separately has direct callers `0x425B2C` and `0x427594`, not the registered-user event callback owner.

Original static checks: **four complete incoming direct-CALL inventories, ten exact instruction addresses and one original vtable entry** independently PASS against the SHA-pinned original. Permanent checks live in `research/audit_original_teamselect_continue_static.py`.

## Status and next action

The original contains about **175 direct callers of global `0x613EC0`**. Neither the queue head at first drain `0x4259B5` nor at second drain `0x412F1F` has been observed during real native first-user creation; the initial null queue head cannot stand in for either observation. This source graph shows why a queue-callback producer must not be conflated with direct TeamSelect club acceptance. It neither asserts this callback fires in the normal path nor proves any queue is empty.

PR #656 merged `e5af991503bd16c6b40b57e6816bfba5383e5fd9` after 3,597 tests OK; PR #657 merged `9e753d62db0f509168f8bb57f9ff71fd87e0f5dc` after 3,601 tests OK. Those preserve a source-owned MSVC CRT through Loader444 and actual DBTPlayers, without claiming real startup parity. Next: trace source vft+0x3C identity / event creation, actual first-click RNG time/queue state, then integrate real manager/staff and native seven-row modal into the player-visible GUI, audit Gate13, and proceed through Gates14–17/verified Windows11 release. No gate closed.


## Native event object's concrete +0x3C result, on its successful constructor path

Followed the *specific* event object constructed in the original registered-human handler near `0x4132C5..0x41335C`. At `0x413318` it calls constructor `0x54F060`, then **overwrites the successful payload object's vtable at `0x41331D` with `0x7BD9B8`**, and stores that payload pointer in the enclosing event record at `0x413333`. The event record itself receives vtable **`0x7BD564`** at `0x413336` and can be passed at `0x413357 -> 0x613EC0` into the original global queue when the path conditions hold.

On this concrete, successfully allocated variant, event record virtual **`+0x10`** at `0x7BD564+0x10` is `0x5CFA20`. Its payload's virtual **`+0x3C`** at `0x7BD9B8+0x3C` is **`0x651E20`**, whose entire body is **`mov eax,1; ret`**. Therefore if this event object is actually queued and invoked, its `0x5CFA20` parent predicate **returns true** and reaches `0x5CFA48 -> 0x413020` for this variant, potentially creating another qualified user event when corresponding original human-list conditions hold. This is concrete vtable source evidence, not a guess about an opaque callback.

Original SHA-verified static checks: six exact original x86 instruction owners and two virtual-table pointer slots PASSED. **Actual event instantiation, enqueue timing, dispatch execution and the later human-list conditions remain UNOBSERVED**. Do not infer first/second drain queue membership or accidental self-triggered recurring enqueue. No original EXE launch or Win11 live GUI acceptance; Gates13–17 remain open.


## Recovery578 — queue drain differs from due-tick callback

The original **ordinary queue drain** `0x614080` calls event virtual **+0x04** at `0x6140A5`, then virtual **+0x18** at `0x6140B0`; zero completion calls unlink `0x4EA190` at `0x6140E0`. For the specifically qualified record vtable **`0x7BD564`** with successful payload **`0x7BD9B8`**, record +0x04 points to `0x40DFB0` (returns 0); record +0x18 is `0x404610` forwarding to payload +0x24, also `0x40DFB0` (returns 0). **If this record is genuinely in the queue at `0x4259B5` or `0x412F1F`, this drain removes it and DOES NOT invoke the registered-human callback `0x5CFA20`.** Removal/destructors retain their own native heap/owner effects.

The separate time-qualified event processor **`0x613EE0`** compares `event+0x04` with a supplied current tick at `0x613F00` (signed `jg` skips future events) and calls event **virtual +0x10** at `0x613F07` only if due. In this subtype, `0x7BD564+0x10 -> 0x5CFA20`, payload `0x7BD9B8+0x3C -> 0x651E20` returns one, and `0x5CFA48 -> 0x413020` invokes original registered-human processing. That may conditionally enqueue a subsequent event, but no first-human source call or runtime queue membership has been established for it. Handler-generated record due time is **`[0x9847FC]+1`** at `0x413327..0x413330`, so without signed-overflow semantics it is not due on its creation tick. Another source code path `0x5E330E` constructs the generic event vtable and enqueues then calls timed processing, but its payload subtype is not proven to match `0x7BD9B8`.

This corrects the previous potential conflation of the generic queue drains and the time-qualified user event. The exact 22 instruction-address assertions and 6 native vtable slots were independently verified on the private SHA-256 matched original EXE and added to `research/audit_original_teamselect_continue_static.py`. **Actual event population, OS seed-to-first-click RNG, original manager+staff/GUI, and Win11 acceptance remain unknown. Gates13–17 OPEN.**
