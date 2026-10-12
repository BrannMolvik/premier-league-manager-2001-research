# Recovery565: native global queued-event wrapper is source-qualified, payload is not

**Date:** 13 October 2026 KST. **Status:** STATIC/SOURCE-VERIFIED native wrapper only, not native GUI observation, event population proof, exact original first-human CRT stream, or port integration.

**Private original source:** disc-root `footballmanager.exe` 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` verified in a private temporary working folder. Original process NOT launched, private executable/objdump output NOT added to Git.

## Wrapper identity and original direct-producer examples

Original native queued-event allocations at `0x41A336`, `0x41A447`, `0x5E330E`, `0x42636D` and `0x42642B` set the same source wrapper object's vtable pointer to **`0x7BD564`**, with its separately allocated **inner event pointer at wrapper+0x08** and due date at wrapper+0x04. The **first three** cited source paths enqueue that wrapper by `0x613EC0`, and immediately invoke the distinct time-driven processor `0x613EE0` (see previous Recovery565 report). This does NOT show that any of them fires during original TeamSelect selected-human birth.

From the authenticated original PE `.rdata` at VA `0x7BD564`, the **first seven virtual targets** are **`[0x404620, 0x40DFB0, 0x5CE530, 0x5CE5E0, 0x5CFA20, 0x404600, 0x404610]`**, at offsets `+0,+4,+8,+0x0C,+0x10,+0x14,+0x18` respectively. This table was independently unpacked directly from original bytes, not guessed from the port.

## What the source wrappers actually do

- **Conditional queue drain 0x614080** calls wrapper **vft+0x04 = `0x40DFB0`**, which unconditionally executes `xor eax,eax; ret`. Therefore **for this specific `0x7BD564` wrapper only**, the drain does not take the `+0x04` repeat-call path; it immediately calls **wrapper vft+0x18 = `0x404610`**. This loads `inner = [wrapper+8]` and **tail-jumps to inner event vft+0x24**. That inner return determines retention/removal. The actual inner class/body/CRT consequences are NOT established. Other original event vtables may take the nonzero +4 repeat path.
- **Time-driven queue processor 0x613EE0** calls wrapper **vft+0x10 = `0x5CFA20`**, which loads the same `inner` and invokes **inner vft+0x3C**. On a nonzero result, it writes the wrapper due timestamp to the inner+0x04, clears wrapper+0x08, and calls **global user/event registrar `0x413020`** with the transferred inner pointer (source `0x5CFA2F..0x5CFA48`). On a zero result, it returns without that transfer. **This proves native timed-processing can have a registry side effect**, but it does not prove such effects actually occur on a particular event, at first human click, or consume CRT.
- **Deleting destructor** wrapper vft+0x00 = `0x404620` invokes `0x404640` to free any still-owned inner event; direct code resets the inner vft to `0x7BD5A8` and calls the original allocation/free routine. This does not prove destructor side-effects beyond that bounded source, nor replacement object lifetime elsewhere.

**Correctness implication:** A clean-room direct-only implementation that discards or assumes a no-op for global event callbacks when creating a user can alter future state, because at least one verified original wrapper delegates to **real underlying callbacks**. Do not hardcode a zero-effect queue or add synthetic RNG calls to compensate. The current pure `original_teamselect_queue_lifecycle.py` explicitly models observed callback results and does not claim native callback execution; retain that fail-closed limitation.

## Reproduction / next task

Run `python research/audit_original_teamselect_continue_static.py /private/footballmanager.exe`. The repeatable audit now checks the SHA, 7 actual vtable pointers, and 8 native callback instructions; private Python/objdump checks on the original executable independently **PASSED**. No exact GitHub branch test suite or real Win11 GUI test claimed.

**Next exact native task:** identify the inner object vtables produced by the source reachable global queued-event constructors during real original load/TeamSelect; trace their **inner +0x24** conditional drain, **inner +0x3C** timed process, full user-registry effects and RNG calls; only then determine which effects must precede the original first-human 13 name pairs/six staff, without inventing an exact shared CRT checkpoint. Integrate actual original TeamSelect + PSupportStart user-visible flow after these dependencies, then later Inbox, all R1 modes, all shipped leagues/humans, and verified Gates13–17 Win11 release. All gates remain OPEN.
