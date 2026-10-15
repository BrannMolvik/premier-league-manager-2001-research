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
