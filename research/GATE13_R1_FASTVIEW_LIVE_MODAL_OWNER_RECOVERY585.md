# Recovery585: original live mode-2 FastView owns a synchronous match modal, not a post-result extra window

Date: 13 October 2026 KST. Canonical original authorized 4,714,541-byte EXE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3; static private read only. Original program not executed. Gate13–17 OPEN, no GUI acceptance.

## Original match route and native owner ordering

The source branch at LeagueMatch::0x51325D checks numeric modes 0,1,2. For explicitly selected mode2 it enters 0x51326D, pushes the current match context at 0x51326D..0x513272 and calls 0x5331C0. For mode0/1 it calls 0x533D80 with variant, for mode3 it calls neither wrapper. Importantly the mode2 wrapper returns to 0x513294, and only THEN source LeagueMatch vft+0x38 (0x51329D) and +0x3C (0x5132A9) run. These source-common callbacks cannot be skipped by treating FastView as only post-processing.

Native 0x5331C0 (a synchronous original-match presentation wrapper) performs this exact bounded call order:
1. global view owner 0x877960: 0x5328B0 followed by 0x5329D0;
2. 0x533270 builds initial state from supplied match pointer; 0x6C1CF0 and 0x533BF0 continue original view staging;
3. 0x51F490 initializes nested original view/event state;
4. 0x532650 runs the original global 0x877960 owner's modal/pump on that staged state;
5. 0x533CA0 cleans up the original match view; 0x51F6D0 destroys nested state;
6. return to LeagueMatch 0x513294 followed by the two original post-view vtable callbacks.

These addresses/order are static-original SOURCE-VERIFIED; complete dynamic modal activation, input termination and original screen pixels are NOT original-runtime-observed.

## Current reconstruction negative comparison

Current normal Tk host _begin_original_human_match (near line1304) and native mode selector handler (near line2879) allow only source mode3 Quick Match. Modes0,1,2 reject before calculator. The separate host present_completed_match_by_source_mode -> present_completed_match_fastview is explicitly an auxiliary already-completed outcome renderer: it opens a standalone resolved-only partial FastView Tk window with unknown overlap alpha, not the source modal at 0x5331C0 in the live match lifecycle. It must NOT be reinterpreted as completed mode2 support by moving it into the normal player action or as proof of original 3D modes.

Existing partial FastView original-resolved assets/renderers (see research/GATE14_FASTVIEW_HUMAN_RESOLVED_PRESENTATION.md) can be reused only where complete source ownership, z-order, context, common callback and modal close are evidenced. Do not auto-select mode3, simulate mode2 with Quick-only screen, invent undocumented presentation RNG or paint transparent unknown pixels. Keep actual body/UI fail-closed.

## New independent original-source guard

reconstruction/test_gate13_r1_fastview_native_wrapper_recovery585.py uses opt-in FM2001_ORIGINAL_EXE and the existing OriginalPE32 reader to enforce exact caller, ordered modal owner and cleanup call bytes, and common return callbacks. It does not execute the original, attach a native GUI, patch the host, or claim full branch CI.

## Exact next source-backed task

Trace 0x533270 / 0x533BF0 / 0x51F490 source match-event state and 0x532650 modal return/cleanup conditions, compare their producer/consumer graph against the already-present resolved-only FastView frame. Identify minimal source-correct integration into R1 staged once-only match and PResults/management return. If any required view/input semantics are not established, leave mode2 blocked and move to another independent high-impact player-visible Gate13 workflow rather than inventing a display. Preserve prior Inbox-native-filter WIP branch worker/gate13-inbox-ten-filter-visible-font-and-source-assets-583 @ 011b76b15e4e267d7603c106214a2cc70248ce4e with missing original radio sprite explicitly deferred; no PR/CI until coherent milestone.


## Recovery585 next source pass: source-owned modal and state writeback, not passive screenshot

Native 0x532650 is a concrete activation wrapper: it calls original manager/owner precondition 0x4DAF40 then passes 0x877960 owner+0x18 to native activation 0x654210 at 0x53266D. This is NOT merely a draw of a final completed score. At 0x533270, the original loops for two side indices (0 and 1, branch condition cmp esi,2 at 0x5332B9), calling 0x533370 and its downstream view/game-state producers for each side. At 0x533370, the side-selected original +0x5A4 or +0xB54 match record is used as an input; per-entry loop writes eight clamped [0,15] byte outputs based on the native source array (cmp ecx,8 at 0x533421, cmp eax,15 at 0x533413). **No football meaning is inferred for those bytes.**

After returning from modal activation, source 0x533CA0 is not just a passive disposal routine. Its visible branch copies twenty DWORDs from global state beginning at 0x877CF4 into a match-owned object field (source rep movsd at 0x533CE0 with count 0x14 at 0x533CD1), then source 0x4EA330 and other record calls follow. These writes are player-state or source-record interactions whose precise football effects and required simultaneous side contexts remain UNKNOWN. The previous shorthand label 'cleanup' must not imply this wrapper has zero persistent effects. Therefore a detached Tk FastView final screenshot cannot safely be substituted for this original live modal in R1. An opt-in private-source test guards the two-side producer, original input activation and actual native copy. Local independently reproduced static instruction assertions: 7/7 passed. No original EXE launched or Windows GUI acceptance.

**Exact next investigation:** follow source 0x533270->0x533370 and 0x533CA0 producer/consumer state to separate gameplay-dependent writeback from presentation-only values; determine source mode2 once-only result/progress and retained state ordering before attempting a live Tk integration. Reuse existing Gate14 fastview rendering only for source-qualified resolved pixels, not as a fake replacement modal. No source-backed complete mode2 is implemented yet.
