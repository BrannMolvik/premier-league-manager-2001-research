# Recovery565: original SupportStart nested modal return is NOT TeamSelect handler result

**Date:** 13 October 2026 KST. **Original:** private SHA256-checked disc-root `footballmanager.exe`, 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Only STATIC disassembly was performed. No original process launch, screen/input observation, original assets in Git, full branch test, or Windows11 GUI validation.

## Distinct original modal vs outer event results

Native TeamSelect **outer control callback** `0x4D91C0` first invokes original acceptance base handler `0x4D91D0 -> 0x64F960` and **saves its return value in EBX at 0x4D91D5**. Only if that value is nonzero and original `0x4D91DD -> 0x652F80` condition is true does it obtain current human user `0x413B80`, locate real seven selectors and call nested `0x4D9224 -> 0x450BB0` PSupportStart.

Inside the nested modal `0x450BB0`, after `0x532650` completes, `0x450CBF` reads PSupportStart `+0x1DE4` into BL, and **`0x450CD9` copies BL to the nested function's AL return** after graphical cleanup. Native PSupportStart events are distinct: event1 runs `0x4D061F` setting `+0x1DE4 = 0` and requesting UI close, without invoking Apply; event2 runs `0x4D0606 -> vtable+0x4C` (actual `0x4D0830` original staff/name Apply) then sets `+0x1DE4 = 1` and requests close. This verifies the **inner** Cancel 0 / Apply 1 semantics only.

Critically, the outer TeamSelect `0x4D922C` does **`mov eax,ebx`**, returning its **previous base control acceptance**, not the result `eax` that just came back from `0x450BB0`. Therefore **an implementation that treats TeamSelect event success/selection or new human presence as equal to SupportStart Apply(1)/Cancel(0) is unsupported and contradicted by source**. Both forms of nested dialog closure are associated with a successful outer accepted event, assuming same original acceptance gate and control selected state. Other post-return observer/state relationships still require proof; this does not make Cancel equivalent to Apply.

## Native teardown and staff lifecycle boundaries

Original PSupportStart destructor `0x4CF790 -> 0x4CF7B0` directly destructs many UI child controls via `0x64F350`/`0x5D4600`; seven selector array is destructed at `0x4CF936 -> 0x66820D` with callback `0x4D89E0`, whose body is only `jmp 0x5D4600`. It then runs base `0x6532A0`. There is **no direct call to `0x4D0830` in this bounded destructor instruction inventory**, and Cancel event1 itself also does not call Apply. This is **NOT proof** that native linked-list staging performed *before* the modal is rolled back on Cancel; indirect component/base destructors, queue callbacks and outer selection side effects remain separate research targets. Do not erase the new human, reset the global CRT, restore all staged staff, or declare original Cancel side effects without full source proof.

## Direct queue producer/timed processing classification

Original queue helper `0x613EC0` has 175 direct original `.text` call instructions (see prior Recovery565 report), but **three specific enqueue and timed-processor pairs** occur immediately in source: `0x41A352 -> 0x613EC0` followed by `0x41A364 -> 0x613EE0`, `0x41A463 -> 0x613EC0` followed by `0x41A475 -> 0x613EE0`, and `0x5E3322 -> 0x613EC0` followed by `0x5E3335 -> 0x613EE0`. These construct the same native `0x7BD564` wrapper shape, but class payload and reachability are not fully qualified. The timed processor `0x613EE0` is distinct from selected-human two `0x614080` drains: native timer scans owner queue, compares `event+0x04` with caller time (0x613F00), calls source event **vft+0x10** (0x613F07), conditionally deletes, and then processes user-owned `+0x6B4` follow-ons. Syntactically adjacent enqueue/processor calls do NOT guarantee the newly added event is due, removed, or that native CRT is untouched. The other timed processor direct sites `0x43216C` and `0x4A8084` require broader reachability analysis.

## Reproduce and exact next step

Private local x86 `objdump -D -Mintel` assertions independently passed for **17 original native instruction edges** related to the modal and timed queue, in addition to the previous 12 human/queue edges. New matching repeatable assertions are appended to `research/audit_original_teamselect_continue_static.py`; run it only against the authenticated private original executable. No exact remote feature-head full CI or Win11 GUI claim.

Next: source trace initial first-user event queue construction/producers/callback vtables from real boot and database loading; trace native staff linked-list mutation/survival on nested Cancel and later deselection; integrate immediate manager creation and six staff, original shared CRT, seven original interactive SupportStart rows, Apply/Cancel and TeamSelect outer return without conflating the results. Batch a genuine playable original-feature milestone before new PR/CI. All Gates13–17 remain OPEN.
