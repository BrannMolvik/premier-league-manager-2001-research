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
