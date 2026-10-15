# Recovery642: 5DB37C four scored stage QWORD totals → nonhuman match context

15 October 2026 KST. Canonical main `318f981666be13dfa14394ff1eaceeab906d57b5` (PR752 safely merged, exact-head Gate13 2,044 tests/186 skipped and asset policy SUCCESS); Gate13 and Gates14–17 remain OPEN. Source private original disc-root `footballmanager.exe`: 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, independently checked and statically disassembled only, not executed/committed.

## Original 5DA8E7–5DA923 zero-initialized four stage results

At original 5DA8E7/E8 two `PUSH`ed coefficient output pointers temporarily shift stack by eight bytes. Therefore original paired DWORD zero stores 5DA8EB/F3 correspond to post-call stage1 QWORD `[S+60..67]`, 5DA8FB/903 stage2 `[S+58..5F]`, 5DA90B/913 stage3 `[S+68..6F]`, and 5DA91B/923 stage4 `[S+50..57]`, where S is the actual native ESP restored after 40CBC0's `RET 8`. If original x87 stage guard skips a stage and there are no aliased side effects, its direct QWORD result remains **zero**; reject supplied altered skipped slots rather than assuming other results. This is separate from 5DA92B/933 B parameter initialization corrected in PR752.

## Native x87 668350 integer return and pair order

At `5DB37C`, original calls `668350` at `5DB380` for stage3 QWORD `S+68`; then `5DB38B` for stage1 QWORD `S+60`; `ADD EBX,EAX` at 5DB394 creates **EBX = (low32(trunc(stage3)) + low32(trunc(stage1))) mod 2^32**. It calls `668350` at `5DB39A` for stage4 `S+50` then `5DB3A5` for stage2 `S+58`, with `ADD EDI,EAX` at `5DB3AA` creating **EDI=(stage4+stage2) mod2^32**, and copies EDI to native `[S+18]` at `5DB3AE`. Independently verified original `668350` temporarily saves x87 CW, sets truncating RC=11, FISTP signed64, restores original CW and returns low EAX (high EDX unused here). Nonfinite/overflow signed64 conversion does not receive invented values and is deliberately rejected.

Human callbacks, a source local byte flag, and selected user+694 may modify first component and emit native 5DC510 side effects; the pair is **PRE-human**, not a final score, context or event count.

## Only reached nohuman + source flag zero direct context

Source `5DB3B2 CALL 4037B0` original human predicate false branches `5DB3BD JE 5DB4CF`, then original `[S+0xF] == 0` makes `5DB4D1 JE 5DB6FA`. No human selected user+694 and no native 5DC510 callback on this direct path. Native `5DB6FC` writes EBX to its local QWORD lower half, `5DB704` reads ECX from saved `[S+18]`, and `5DB70F–726` computes total and writes original native match processing-context **D84 = (EBX+ECX) mod 2^32**, **D8C=EBX**, **D90=ECX**. Existing `original_native_5db6fa_context_tail.py` independently sources nonzero component suffix D94=2, D98=2, D9C=4; use it without inventing FPU zero/NaN behavior.

New `original_match_four_stage_integer_totals.py` source reads actual stage QWORDs and independently supplied booleans; new `original_match_nonhuman_stage_context_join.py` joins the two nonzero components to existing original context receipt with actual pointer identity and nohuman/flag0 evidence. Both outputs explicitly `original_native_executed=False` and `live_game_state_updated=False`. Nine locally executed targeted unit tests PASS, including original canonical PE opcode bytes for every initialization, 668350 call, ADD and the two exact nohuman branch displacement targets. Register on focused Gate13 workflow. This is bounded source proof, **not** real GameState, SaveLoad, normal NEXT→PPreMatch all modes→PResults→management, original graphical acceptance or Windows11 release.

NEXT: resolve original human/flag-nonzero branches at 5DB3C3..5DB6F5 (native 5DC510, two manager user+694 fields, first-side score adjustment), then stage QWORD producers and original FPU ratio; integrate actual native scoring callbacks/side/context into live GameState with original ordinary player lifecycle. Continue on same unopened branch until a cohesive feature milestone for PR/CI. PR739 high-risk injury state remains separate/unmerged.

## Further original first-side HUMAN branch source obligation (Recovery642)

The first-side human path must **NOT** be replaced by the direct nonhuman
context join plus `user+694[0]`. Native `5DB3C3` selects human branch when
the first-side 4037B0 source gate is true and `[S+0xF]==0` (different
route if flag nonzero). Reached `5DB450/5DB4B3` reads selected
`user+0x670` and calls **5DC510 twice**, each taking a distinct native
constructed argument and source state. Only **after** both does `5DB4BE`
get `user+694` and `5DB4C4 ADD EBX,[ECX+0]` before jumping to 5DB6FA.
The native 5DC510 itself has nontrivial effects: original 5DC586
`FADD QWORD [ESI+0x10]`, 5DC599 `FSTP QWORD [ESI+0x10]`, calls native
5DC650 at 5DC5D4, and calls **617D70 event/record queue** at 5DC63A.
It pushes and restores EBX, ESI, EDI and returns `RET 0x24`, consistent
with EBX preserved across this call, but state/event effects are NOT.
The separate second-side 5DB5F0/5DB692 reached callback calls are also
not part of the false-4037B0+flag0 direct branch. PE identity tests
for original two first-side callsites, EBX bonus, 5DC510 mutable owner
and 617D70 queue have been added. Until exact native 5DC510 payload,
recipient and event lifetime are joined to GameState/SaveLoad, source
projection must fail closed on these human/alternate paths. The nohuman
route label means `4037B0(ESI)` is false and the native flag is zero;
do **not** assume it proves every possible other participant is AI.

**Next:** source trace native 5DC510 received argument layouts and
5DC650→617D70 payload and record ownership, plus all three original
5DB4D7+ alternate branches; then actual GameState/player-visible
R1 flow. No native execution, full original career, GUI or Win11
acceptance claimed.

## Native nested 5DC650 state and event path (Recovery642 continued)

The original `5DC510` caller invokes `5DC650` at 5DC5D4 **before**
its own `617D70` at 5DC63A. New independent disassembly of original
`5DC650..5DC887` shows two conditional flow families selected from
native EDI argument at 5DC672: nonnull target at 5DC680, null target at
5DC768. Both perform `5E48D0` QWORD source comparisons with
`FNSTSW AH bit0x1` guard; *each* may return early without an event
when an independently source-required pointer is null (5DC6A8 / 5DC790).
Otherwise 5DC6E3–E7 or 5DC7D5–D9 performs original
`FSUBR QWORD [ESI]` then `FSTP QWORD [ESI]`, where
`ESI=EBX+0x10` and `EBX` is the selected 5DC650 original state owner.
It may allocate a 0x20-byte record and then `5DC86B CALL 617D70`
with an allocated data-link pointer or null if allocation fails.
Source `5DC887 RET 0x28` establishes this callback's cleanup.
There is **no source-safe blanket claim** every 5DC650 call queues
a substantive event, nor proof the resulting first-side state can be
reconstructed simply by an EBX score adjustment. Exact original argument
constructor values, FPU status/NaN/error cases, alternate recipient and
queue side effects still require integration evidence. A new optional original
PE regression checks source direct path, both early exits, mutable
ESI-owner stores, and queue call. This is static source proof only.

## Original 617D70 queue order and owner linkage

A further original-disassembly verification of the shared `0x617D70`
called after the 5DC510/5DC650 callbacks establishes an **ordered
intrusive doubly-linked tail append**, not immediately a rendered Inbox
notice or finalized match event. Its `ECX` is the original queue-owner
object; `[ECX+0x8]` is the current tail pointer and `[ECX+0x4]`
is the head pointer. Argument `[ESP+4]` is the new linked node.
For nonempty queue, `617D7B` writes **oldtail+4=newnode**,
`617D7E` clears **newnode+4=0**, `617D88` writes
**newnode+8=oldtail**, and `617D8B` updates **owner+8=newnode**.
For empty queue, `617D91/94` sets both **owner+8=owner+4=newnode**
and `617D97/9E` clears both newnode links. `RET 4` consumes
the one node argument. Original PE bytes were checked independently
for both branch families; a read-only optional original-PE regression
was added.

The two native 5DC510 callback calls are meaningful state mutations
and append ordered wrapper nodes to a queue *owned by their actual
selected +0x670 source object*. Do **not** automatically reclassify
this as the game's per-user +0x6B4 Inbox, or invent an original message
identity; native payload, queue lifetime, delivery/render and SaveLoad
still need original source evidence. Existing GameState live behavior
is not changed by this source trace.
