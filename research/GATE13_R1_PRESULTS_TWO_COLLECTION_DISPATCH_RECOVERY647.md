# Recovery647: original PResults processes BOTH date registries, returns FIRST only

15 October 2026 KST. Source authority: owner-private original 4,714,541-byte `footballmanager.exe`, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original binary statically disassembled, never executed or uploaded to Git. Main baseline `53f3eb5763780ced8e03bc39a0ffe715a7c6f33f` includes original PResults bottom art and multi-human/postponed-source PR754–756, but **NOT** real native dated GameState callbacks.

## Native whole-day source 4A8260, not one calendar or match count

Direct original `objdump -d -M intel --start-address=0x4a8240 --stop-address=0x4a82e0` gives:

- `4A8261 MOV ECX,947AD8` / `4A8266 CALL 6168C0`: **FIRST/PRIMARY** date collection full two-pass event processing.
- `4A8270 MOV BL,AL`: retains primary `6168C0` AL (this is whether its **second pass** executed any event, not whether any first-pass work ran).
- `4A826B MOV ECX,947AF0` / `4A8272 CALL 6168C0`: **SECOND/SECONDARY** collection; may execute its own event+v10 callbacks and increment global `PResults+64` via original `4A71F0`.
- `4A8277 MOV AL,BL; POP EBX; RET`: **4A8260 returns ONLY primary AL**, discarding secondary AL, but **not undoing** secondary event callbacks/world side effects.
- The PResults `4A83D0` parent calls `4A7280` to update date-caption text, `4A8260` to process both collections, and `4A8070` for further actual world callbacks.
- Original `4A84EA` `4A7210` pre-count calls **ONLY first collection 947AD8** for eligible nodes and stores `PResults+68 = first-count+already-processed`. It does **not** count all secondary events. Original `4A71F0` increments PResults+64 for **all** source callbacks from either collection, and `4A7190` calculates quantized bar width from that mutable +64/+68 pair.

**Important counterexample:** Primary source `6168C0` can return false while secondary returns true, and **4A8260 still returns false**. Its PResults+64 can increase twice while eligible pre-count from primary remains small; original native width may then exceed the 800px source loading_fill.444 sprite. Our current Tk `original_presults_bottom_surface.py` correctly refuses painting an overfull event projection without independent original clip evidence, rather than pretending the bar is 100% or counting only visible matches. Do not clamp or equate primary `AL` with total progress.

## Code and tests on the active WIP

`reconstruction/original_presults_two_collection_dispatch.py` requires **two independent qualified native `OriginalPResultsDatedEventReceipt` inputs**, one per source registry, validates ordered per-registry first/second callbacks, v+0x10 native ticks, their AL flags, and disjoint original event pointer ownership across the two collections. It returns *first* AL unchanged, ordered PRIMARY callbacks followed by SECONDARY callbacks, and explicit no-native-execution/non-state-update flags. A companion function creates native `OriginalResultsProgress` counter snapshots using **independently supplied ORIGINAL primary-only denominator** and prior processed count. It intentionally supports counter > denominator as a source-observable arithmetic state, but it does not render extra beyond-800px pixels, mutate GameState or claim the native x86 integer-overflow arithmetic is fully modeled.

`reconstruction/test_original_presults_two_collection_dispatch.py` covers primary/secondary return AL disagreement, disjoint source event pointers, ordered callbacks, exact source count increments, overshoot counter without fake 800px clipping, no-event cases, malformed/cross-owner tuples and signed overflow safeguards; optional private-original PE verification of seven opcode sites and 3 direct call targets was independently performed and **PASS**. Python tests authored but **not yet certified in CI**; add to focused workflow and test at the next coherent reviewed source/player integration, not micro-PR after every trace.

## Remaining actual player result

The modern `HumanGameplayController` is still one-human, and its `PrimaryScheduleShadowState` reflects only primary match-event semantic nodes without a full original event+8 identity, all virtual+0C qualifiers, original 947AF0 second collection or mutable native event+v10 callbacks. So the code above is a source-backed **bridge**, not permission to emit ordinary NEXT UI tick messages. NEXT→PPreMatch modes0–3→PResults→PBg 432505 native conditional Start/PMenu/multiuser return, native 513252→5DA2F0 score/v38/v3c, SaveLoad, all original leagues and real Win11 GUI remain OPEN. PR739 high-risk separate. Gate13 earliest incomplete, Gates14–17 open.

**NEXT source-proven implementation:** reconstruct both first and second event registries as durable scheduled GameState owners (including non-LeagueMatch entries), original+8/vtable/event+44 and callback ordering/mutating effects, and validated 4A7210 total. Then use the existing ordinary `OriginalGameTkHost` source progress drawing seam with actual ordered dual source ticks; finish guarded 432505 postresults return without inventing modal close/return click. Further independent cloud-safe source work can proceed even if physical Windows11 original gameplay remains externally blocked.


## Recovery647 player-display integration, source-gated dual callback receipts

The WIP now continues beyond static callback analysis: original
`source_original_presults_bottom_surface` and the **ordinary
`OriginalGameTkHost`** have a strictly typed pathway
`apply_source_original_presults_two_collection_callbacks`
for a *caller-supplied authentic dual-registry* 4A8260
receipt. This source-qualified pathway draws the genuine
three imported PResults bottom bitmaps and quantized fill
using both ordered original 6168C0 callback lists and the
separately supplied first-only 4A7210 denominator.
Primary 6168C0 returned AL remains independently recorded,
never synthesized from whether secondary events occurred.

The host refuses a forged or missing second-registry receipt,
source numerator/denominator overflow, mixed single/dual source
owners, an inactive results input owner, missing original source
art or an overfull bitmap. The original second-registry may
increase event processed+64 above first-only denominator+68;
in such a case the read-only source model preserves the
overshoot counter, but the renderer **refuses to clamp or
invent overdraw pixels**. The actual old 800px game blit
boundary under overfull counters is not yet source-verified.

Five new renderer/host tests cover authentic source pixels
in expected source XY, source primary/secondary AL disagreement,
secondary-only ticks, overfull rollback without a state change,
inactive match-owner refusal and mixing two incompatible event
owners. They are registered alongside the existing
five original 4A8260 dispatcher tests in focused Gate13 CI.

**Crucial fidelity boundary:** The current ordinary Quick3
worker **does not call this method automatically** because
the modern `GameState` does not yet produce original-native
event+8/vtable/v+0C/v+10 receipts for both registries.
This work makes the existing real Tk component source-ready,
not a genuine completed original 6168C0 callback stream,
fully playable NEXT return or release acceptance.
No native original game process/Windows11 physical comparison
occurred. Source + unit test quality gates remain necessary
before a substantive merge; original score/v38/v3c,
all four match modes, SaveLoad and multi-human are OPEN.
