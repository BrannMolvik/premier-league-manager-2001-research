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


## Recovery585 after-modal two-side writeback: real target record mutations SOURCE-VERIFIED

Further independent read-only disassembly of the exact authenticated original private EXE source `0x533CA0..0x533D7E` closes the bounded writeback transaction more tightly, without claiming the full football meaning or live UI:

- `0x533CA5` initializes side index `edx=0`, and `0x533D69..0x533D71` increments it and loops for sides **0 and 1**. The first side takes match field `[match+0x00]`; the second takes `[match+0x5B0]`. The source buffer for each side is indexed at `0x877CF4 + side*160`, with destination `[team-object+0x244]`.
- For **each side**, `0x533CD1` sets `ecx=20` and `0x533CE0 rep movsd` copies exactly **80 bytes** (20 DWORDs), even if the separate per-participant object count is zero. The original source goes on to examine the side-selected `[match+0x5A4]` or `[match+0xB54]` and, if nonzero, iterate its participant records.
- The inner loop reads 16-bit record identities from successive destination `+0x244` WORDs, resolves through a global object `0x875644`, dereferences actual target `+0x248`, and writes using native `0x4EA330` and `0x4EA350`. **These are real target byte mutators**: `0x4EA330` replaces the low five bits of target `+3` with the supplied value's low five bits while preserving higher bits; `0x4EA350` replaces the low four bits of target `+4` while preserving higher bits. Inputs come from source side-indexed arrays at `0x877BB4` and `0x877A74`. The game semantic names for these packed fields are not independently proven; do not call them fitness, injury, score, cards or morale.
- `0x533370` likewise selects the original `[match+0x5A4]` for side0 or `[match+0xB54]` for side1, builds each side's original participant records, calls source `0x533A00` and `0x41E3D0`, then emits eight data bytes per entry clamped to 0..15. Without producer/consumer proof, those eight bytes are NOT an accepted separate gameplay model.

**Counterexample:** any replacement of source mode2 FastView with a detachable visual frame after a Quick-style simulation would skip, or move out of original order, the above modal-return writes to two team objects and referenced player records. Existing R1 mode3 should remain source-preserving while mode2 is blocked. Exact user-facing FastView return/inputs, numeric-field semantics, validation over real fixtures, and original GUI remain unresolved. A new opt-in native-byte regression guards the above bounded mutators; **19/19 address assertions passed in an independent local PE read against exact private SHA833bf95e original**, separate from unrun exact feature-branch tests and CI. No original executable execution or Windows 11 acceptance.

**Next**: prove input producer arrays `0x877CF4`, `0x877BB4`, `0x877A74` and the resolved target record type through `0x875644`, along with actual `0x51F490/0x532650` termination. After these are source-complete, integrate the original synchronous mode2 state/result lifecycle and only genuinely source-resolved pixels, with explicit modal ownership and post-match callbacks. Defer any unverified visual/interactive portion rather than silently reusing detached FastView as the in-game original.


## Recovery585 source-complete bounded pre/post modal packed snapshot symmetry

A separate first-hand static inspection of the original source **before** modal activation shows `0x533BF0`, called from `0x533209` before original `0x532650`, is the complementary snapshot of the two-side writeback at `0x533CA0` afterward. It traverses both side indices0 and1. For each side, native `0x533BFF..0x533C2A` reads the side's team record `+0x244` and copies **20 DWORDs (80 bytes)** into global `0x877CF4+side*160`. The post-modal `0x533CA0` performs the exact reversed 80-byte copy. Thus the 80-byte transfer is a **real bidirectional team state boundary**, not an opaque temporary display bitmap.

The snapshot loop reads a side-specific participant count from `[team+0x294]` and WORD identities from successive entries of the original team `+0x244` area. It dereferences the player record through global `0x875644` and `+0x248` then calls authentic getters **`0x4EA3C0` = record byte+3 low5** and **`0x4EA3D0` = record byte+4 low4**. The source caches these exact values in side-indexed global arrays **`0x877BB4` and `0x877A74`**. After the synchronous view modal, `0x533CA0` reads those arrays and calls `0x4EA330` and `0x4EA350`, replacing precisely those low 5/4 bit fields in the original resolved target. This closes the primitive source **read ↔ edit buffer ↔ write** contract. It does NOT prove which controls modify the values inside the modal, that values always change, their gameplay labels, how many records are valid, or whether source simulator would regenerate the same writes elsewhere.

New private opt-in exact-source tests guard **15** address sites of the paired initial snapshot/getters; **15/15** independently checked against the owner-authenticated original PE bytes locally. Still NO original process execution, current reconstructed live FastView support, full-suite CI, Windows11 graphical acceptance or gate closure. The highest-impact missing transition is producing the source-edited global arrays during the actual original FastView UI/modal; do not use arbitrary synthetic changes to declare parity.

**Exact next action**: inspect original modality owner `0x51F490` and `0x654210` source input and find the real modifier of `0x877CF4`, `0x877BB4`, `0x877A74` (reads and writes) and view-mode termination. That evidence must precede integrating a live mode2 route in the normal host. Keep modes0/1 blocked as 3D-specific until equivalent proof.


## Recovery586: original FastView modal keyboard exit, three-state cycling and nonvisual post-return record flags

Independent original-source examination of the **same verified 4,714,541-byte original EXE** (SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`) on 13 October 2026 KST used local GNU objdump on PE32 source; **no original executable process was launched**.

- `0x51F490` constructs the actual nested FastView screen at **800x600** (native `push 0x258` height and `push 0x320` width before `0x527350`), with final screen vtable `0x7CA58C`.
- That screen's vtable slot **+0x34** is `0x521DA0`, an actual keyboard handler. If its byte flag at screen `+0x2B6` is nonzero, the handler skips these actions. Otherwise, key **0x1B (Escape)** calls native `0x6539F0(0)`; that function posts Win32 message **0x400 (WM_USER)** using `0x659650`. Key **0x20 (Space)** increments screen DWORD `+0x2AC`, wrapping from 3 back to 0: exactly **three internal states 0, 1, 2**, not evidence of three independent match modes. The screen constructor initializes `+0x2AC=1` at `0x51F5EB`. The exact visual content of each state and pointer interactions are still unverified.
- The owner at `0x877960` has vtable `0x7CB294` whose entry0 is **`0x532B80`**. `0x654210` registers the nested screen, invokes the owner's vtable entry0 at `0x654258`, and after return removes it via `0x654360` when the supplied third argument is zero (which it is at `0x533223`). Owner `0x532B80` uses imported `PeekMessageA`, `GetMessageA`, `TranslateMessage`, `DispatchMessageA`, and `WaitMessage`; the **`message == 0x400`** branch at `0x532BBF..0x532BC7` returns from the nested loop without dispatching it. Therefore source proves a synchronous input/message-loop modal exit route, not a detached post-result visualization. This is static Win32 source logic, **not** interactive observed behavior on Windows 11.
- Post-modal `0x533CA0` does **not** merely restore `0x877CF4`, `0x877BB4`, and `0x877A74`. For each side-selected participant, index **0..10** invokes `0x4182F0` before packed-byte setters; indices **11 and greater** invoke `0x4182C0` (`0x533D0A` comparison). `0x4182F0` ORs source target DWORD `+0x14` with bit **0x10**, invokes `0x418160/0x418180/0x418170` and conditional `0x41EDF0` after `0x417340` check; `0x4182C0` calls `0x418150`, ORs target `+0x14` with **0x20**, invokes `0x418180`, `0x418170`, and linked packed-object `0x4EA370`. These are **additional source record effects**; no invented sporting labels (substitute/injury/fitness/etc.) are assigned. The source post-modal copies and original common match callbacks remain mandatory.
- Original executable includes only **two literal references each** to `0x877CF4`, `0x877BB4`, `0x877A74` at the direct pre/post snapshot sites; this does **not** prove nobody modifies them indirectly through the 0x877960 owner or calculated pointers. Audit such indirect writers/aliasing before declaring snapshots inert or wiring a live simulated edit.
- Reproduction: `objdump -D -Mintel --start-address=0x521da0 --stop-address=0x521de6 footballmanager.exe`; similarly `0x532b80..0x532c05`, `0x654210..0x6542a5`, `0x533ca0..0x533d7e`, `0x4182c0..0x418327`. Confirm imports via `objdump -x`. The appended private opt-in test guards **26 source address sites**, each **26/26 independently checked directly against the SHA-verified local original PE**; full branch tests/CI and native game GUI have **not** run.

**Exact remaining integration blocker:** identify source event/pointer producers that edit the three two-side buffers, the user-visible meaning of each 0/1/2 FastView view, the other event controls, and mode2 progression/result callbacks on a real fixture. Implement native keyboard behavior only within the authentic live original FastView modal and once-only match transaction, not as a standalone synthetic screenshot. Keep R1 modes0/1 and unresolved mode2 explicitly unavailable in the current port until that source contract is satisfied. Next, trace `0x521DF0` pointer-event paths (`0xBA946/0xBA947`, `0xBAD32/0xBAD33`), `0x522280`, and child control `0x652F80` into view-owner buffer edits and post-match result lifecycle.


## Recovery586: bounded FastView pointer event siblings, no proven live buffer edits

Follow-up first-hand disassembly of the authenticated original executable `0x521DF0..0x521F8F` independently exposes two *separate* native pointer/control action families. This must be reflected in future original FastView UI, not inferred from today's reduced renderer.

1. `0x521DF0` is the FastView vtable **+0x10** pointer/event dispatcher. It requires a non-null event object, both FastView flags `+0x2B6==0` and `+0x2B7==0`, and **`0x518370(screen+0x2D8)==0`** before dispatching the two control families. The event selector is DWORD **event+0x20**. The exact pointer/button semantics of these event IDs are not independently verified.
2. Event IDs **0xBA946 and 0xBA947** branch to `0x522280` after translating to distinct argument values. This nested original routine sets screen byte **+0x2B5=1**, invokes children **+0x388/+0x3D4/+0x424/+0x478** and owner `0x877960` refresh `0x5329D0`; it obtains source data from screen `+0x2A8`, constructs a conditional child view, and invokes native screen setup `0x653320` with **800x600** dimensions. This is not evidence that those buttons change packed player fields or choose Quick Match. Child lifetime/return/persistent effects remain to trace.
3. Event IDs **0xBAD32 and 0xBAD33** run distinct `0x652F80` hit/state checks on child **+0x424** and **+0x478**, respectively. If allowed, each switches active owner component pointers **+0x88/+0x8C** to a different preconstructed pair (**+0x94/+0x9C** for 0xBAD32, **+0x90/+0x98** for 0xBAD33), dispatches original component vtable callbacks, and triggers `0x653350` update. These are genuinely separate source controls; their artwork/content names and whether they indirectly change player/global arrays are **not established**.
4. No direct screen UI write into `0x877CF4`, `0x877BB4`, or `0x877A74` was proved by this bounded dispatch. Treat buffer aliasing and nested view mutators as unresolved instead of asserting a no-op. The synchronous modal, ESC/Space and post-return two-side record effects from preceding section still apply.

A further **15 original machine-code address assertions passed locally** against the same private original PE with no process execution; appended opt-in test is preserved on this unmerged source-work feature branch. The correct next trace is `0x522280` nested source screen construction & return, `0x52D6C0` child component initialization, `0x5218F0` / `0x521500` FastView owner methods, and indirect access to the three buffers through `0x877960` before integrating source-complete live mode2. The normal player-visible port still rejects mode2; no false finish/GUI claim.


## Recovery587: native FastView nested panel has a conditional class, a real return value and restoration ownership

Authenticated original private `footballmanager.exe` 4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspected as static PE32 only. The selected exact x86 sites and existing native screen code were independently reproduced with `objdump -D -Mintel` and a separate stdlib PE section-VA byte reader. **63 distinct native source address checks passed locally**, including new modal source sites. These are private static source results, not original execution or a port GUI test.

### Full bounded `0x521DF0 → 0x522280 → nested modal → parent` transaction

- Original FastView dispatcher `0x521DF0`, after event/flag gates, sends source events `0xBA946` and `0xBA947` to **the same** `0x522280` with distinct argument values 0/1. The events' user-facing labels/icons remain unknown. Do not assume "view" names or reinterpret them as main PPreMatch modes.
- At `0x5222A3`, parent byte `+0x2B5=1` marks busy state. Four children `+0x388,+0x3D4,+0x424,+0x478` receive vtable **+0x34** calls before opening a nested window. `0x522333` resolves actual stored source object `screen+0x2A8` through `0x62AC80`, a selected virtual function and `0x403850`. Its zero/nonzero result selects **two different native screen classes**, not merely skins: true case allocates **0x48B0** bytes and constructs `0x52D6C0`; false allocates **0x2D4C** bytes and constructs `0x52F890`. Both are passed to `0x653320` with **800×600** and then enter nested `0x532650`. The source identity and semantics of `0x403850` remain unresolved.
- `0x532650 → 0x654210` invokes global owner vtable 0, `0x532B80` native Win32 pump. Its WM_USER (`0x400`) branch returns **`MSG.wParam`**, exactly `mov eax,[esp+0x18]` at `0x532BF9` with MSG starting `esp+0x10`. The call through `0x659650` resolves to imported Win32 **PostMessageA** at IAT `0x7BD2D8`, and `0x6539F0` posts `WM_USER` with wParam `input & 0xFFFF` and zero lParam. The original FastView ESC key handler `0x521DB5` passes **0** to `0x6539F0`, so this exit yields a zero response (assuming message delivery). Source-level Escape exit is **not** proof of match cancellation or skipped post-modal LeagueMatch callbacks.
- The nested `0x522280` parent checks the returned value at `0x522428`; **only a nonzero response** calls `0x521FA0` at `0x522445`. This is a nontrivial original state/control refresh: first invokes `0x6C1C20` twice over source context `screen+0x2D4`, processes `+0x2D8` via `0x518380`, allocates `0x154` for `0x518F30`, then calls `0x5194E0`, `0x5195A0`, `0x518070`, repeated `0x5270C0/0x5302C0/0x530330`, and `0x51CBD0`. **Their full semantic/player-state effects remain unresolved**; it is unsafe to replace this with a passive repaint. No claim is made that these calls edit `0x877CF4/0x877BB4/0x877A74`.
- On either normal return path, `0x52244E` clears parent busy byte `+0x2B5=0`, each of four children receives vtable **+0x30**, `0x653350` repaints, and the nested owned object is destroyed by vtable slot0 with argument1 at `0x5224B4`. Parent control restoration and owned resource cleanup are part of the source lifecycle.
- The separate **outer** FastView mode2 wrapper `0x5331C0` remains synchronous: after modal it applies the two-side snapshot/record state writeback and LeagueMatch common callbacks. Do **not** equate a child modal's zero Escape response with discarding an entire played match; the source's complete normal-case result path must be traced.

**Verification / limits:** New opt-in test methods were appended on the **existing** feature branch `worker/gate13-r1-fastview-live-modal-owner-585`, guarding 41 source address checks across construction, two branches, Win32 event result and restoration. Independent ad hoc read-only VA mapping checked 63 unique sites against the hashed PE (the larger number includes supplementary verification beyond the committed 41). Exact tests in their GitHub branch context and reconstruction suite/CI are **not yet run**; no original binary was executed. No match-mode GUI was integrated; Gate13–17 remain OPEN.

**Next source-backed investigation (do not duplicate completed checks):** trace the original `0x521FA0` effect chain into `0x51CBD0` and `0x518070`, trace the real input/control events and modal returns of both `0x52D6C0` and `0x52F890` classes to identify which can emit nonzero `WM_USER.wParam`, and explicitly look for (or fail-close) indirect writes to the 3 native two-side buffers. Only then design the actual original mode2 once-only match and result return inside the normal port, rather than fabricate a detached Quick-style FastView. Revisit source-independent high-impact management workflow if that proof remains blocked. The source bytes live privately; do not commit them, do not create an early PR/CI for this research checkpoint, and do not close a gate without real Windows GUI acceptance.


## Recovery587 continuation: actual dual-class nested event maps, conditional commit vs close

Read-only PE data/vtable recovery identifies the **final concrete classes**, not merely their shared parent: original `0x52D6C0` ends with vft `0x7CACFC` and vft+0x10 **`0x52E3F0`**; `0x52F890` ends with vft `0x7CB214` and vft+0x10 **`0x5302A0`**. This is why both conditional branches in `0x522280` cannot share an invented generic input handler.

The first class `0x52E3F0` source event dispatcher reads **event+0x20**, subtracts 1, and accepts the bounded range **1–68** (`0x52E428 cmp eax,0x43`). The verified original indexed byte table `0x52ECF0` and 14-branch target array `0x52ECB8` decode to the following *source control handlers* (not yet button names):

| Native event ID(s) | Target/source contract |
| --- | --- |
| 1 | `0x52E854`, own action still to investigate |
| 2 | `0x52E8D2`, posts **zero** via `0x6539F0`, with EBP known zero from `0x52E40E` |
| 3 | `0x52E8DF`, invokes `0x632B70`, and if true invokes `0x6C1CB0`; then posts **Boolean** `0/1` result via `0x6539F0` |
| 4–58 | default `0x52E975` (no specific case handler in this dispatcher) |
| 59–60 | `0x52E947`, `0x52E928` |
| 61–68 | `0x52E440,0x52E4AE,0x52E51D,0x52E593,0x52E606,0x52E69B,0x52E72D,0x52E7C2` |

The second class `0x5302A0` checks event+0x20==1 then posts **zero** via `0x6539F0`. This identifies *actual source exit producers* for the nested modal and a conditional follow-up owner effect, not a generic ESC/close replacement. For the first class, event3's nonzero path is precisely the one that can cause parent `0x522280` to invoke nontrivial `0x521FA0` on return. The precise semantic purpose of `0x632B70` and `0x6C1CB0` is still unproven.

**Counterexample correction:** a separate inherited/base vtable `0x7CAC64+0x34=0x52D350` implements ESC → `0xFFFF`, but the *actual final class* vtables have `0x7CACFC+0x34=0x428AE0` and `0x7CB214+0x34=0x428AE0` (**no-op**). Do not transfer the inherited/base keyboard behavior to the final nested screens without tracing a reached callback. The original *outer* FastView keyboard ESC→zero is independently qualified and remains valid. Actual nested keyboard route may involve other control ownership; leave it unresolved.

Reproduction: parse SHA-verified original PE32, read `vft+0x10` and `+0x34` for `0x7CACFC/0x7CB214`; decode `pe.read(0x52ECF0,68)` and little-endian `<14I` at `0x52ECB8`; inspect `0x52E3F0..0x52E975`, `0x5302A0..0x5302B8`. Opt-in branch tests now assert the **entire** table and bounded event/return source sites, but have not been executed as branch CI, original game GUI or original binary runtime.

**Next high-impact task:** trace first-class event3 `0x632B70/0x6C1CB0` through the true match/player owner, and 59–68 controls that affect nested source state, to determine if they can edit the three original side buffers `0x877CF4/0x877BB4/0x877A74`. Trace first-class event1 `0x52E854` for selection changes, and reconcile both nested exits with original match completion. Only source-complete validated effects can be connected to real mode2 gameplay.


## Recovery587: verified separate live 280-byte per-side FastView data commit, not merely a modal callback

Independent SHA-verified original source inspection follows the first nested class event3's actual call `0x52E911 -> 0x6C1CB0` back to the original match setup and buffer owner. This establishes a **second, materially different two-sided state pipeline** from the previously recovered 80-byte team and packed-player post-modal snapshots:

1. `0x533270` loops both match sides 0 and 1, calls original per-side `0x6C1D00` and `0x6C1D30`. `0x6C1D00` copies exactly **0x185 DWORDs (389×4=1,556 bytes)** per-side into side-indexed global `0xA14AD0` (source geometry only, no sporting labels). `0x6C1D30` writes exactly **0x46 DWORDs (70×4=280 bytes)** into the default input buffer `0xA14898 + 280*side`, followed by other bounded initialization steps.
2. `0x5331C0` calls `0x6C1CF0` **after** `0x533270` to initialize both selector flags at `0xA145F0/+4` to **zero** before screen construction `0x51F490`. Original `0x6C1C20` then selects `0xA14898 + 280*side` when that side's flag is zero, but switches to alternate `0xA145F8 + 280*side` when its flag is nonzero; both branches copy 70 DWORDs into the requested destination.
3. Original `0x6C1C70` writes 70 DWORDs to **alternate** `0xA145F8 + 280*side` and marks that side's flag **1**. Conversely `0x6C1CB0` copies 70 DWORDs from its passed source pointer into **default** `0xA14898 + 280*side` and marks flag **0**. This is a verified two-buffer source commit/selection protocol.
4. The first nested class stores the side selector at **screen+0x90** in shared constructor `0x52D370`. Its event3 at `0x52E8DF` calls `0x632B70` over a screen-owned list and side metadata. Only when that Boolean succeeds, it passes `screen+0xA54` and `screen+0x90` to **`0x6C1CB0`**, committing **280 bytes into the selected side's global default buffer**. The event then posts a native WM_USER modal response matching the Boolean, so the parent invokes `0x521FA0` only on the **nonzero accepted** return. The full gameplay meaning of all 70 words and the validator's accepted elements remains to be established.
5. This source-visible side commit modifies global **`0xA14898`**, **NOT** the distinct live outer FastView buffers `0x877CF4` / `0x877BB4` / `0x877A74`. They represent different original state contracts. Do not equate the 280-byte nested edit with direct proof of mutation of the 80-byte team snapshots or the player packed flags, and do not describe it as a known substitution/tactics/injury operation without semantic tracing.

**Verification:** 31 newly selected original machine-code address assertions independently passed direct read-only PE mapping against the same SHA-256 `833bf95e...` authorized original; 28 representative source sites added to private-executable opt-in branch regression guard. No original process execution or Windows11 GUI. Still no source-complete original mode2, no direct player-visible implementation, and no PR/CI. Retain the same branch.

**Next**: trace `0x632B70` from its real list and validator leaves and the `0x6C1D30` / `0x6C1C20` consumer graph to determine source record data semantics and when the 280-byte committed data affects the game/event state. Trace nested event59–68 control changes relative to `screen+0xA54`; then reconcile independent `0x533CA0` record writes and mode2 match result/management return. Until proven, retain the original 280-byte pipeline as a separate boundary, do not wire synthetic side edits or invent labels.


## Recovery587: original human-controlled vs CPU FastView tactics class identity SOURCE-VERIFIED

This closes the crucial identity/class-selection ambiguity in the two nested modal branches without needing runtime guesses. The real original MSVC RTTI complete object locator at `vtable-4` and type descriptor at `COL+0x0C` identify:

- Constructor **`0x52D6C0`** / vtable **`0x7CACFC`**: `.?AVFastViewTactics@@`, the original **FastViewTactics** screen (allocation 0x48B0).
- Constructor **`0x52F890`** / vtable **`0x7CB214`**: `.?AVFastViewCPUTactics@@`, the original **FastViewCPUTactics** screen (allocation 0x2D4C).

Original `0x522280` resolves its selected original side via `screen+0x2A8 -> 0x62AC80 -> virtual side owner -> 0x403850`. That last original source function calls `0x4037B0` (`0x4139E0`) on global user owner `0x874C10`; membership is determined from the source linked human-user list at `+0x9CC` by comparing actual club IDs from linked user's `+0x5B4/+0x04`. On successful membership it calls `0x413B40` to find and return the actual registered user for side's `club+0x04`; otherwise returns NULL. The nonnull result at `0x52235B` selects **FastViewTactics**, while null selects **FastViewCPUTactics**. It is *not* a random art alternative: an actual user-managed side gets a distinct original interactive tactics editor; the other side receives the CPU variant. The first constructor's common base `0x52D370` stores its selected side at `+0x90`, which is the same selector passed into the 280-byte commit `0x6C1CB0`.

**Significance to required port behavior:** original FastView supports original human-managed match tactical interaction, source-verified as a **live per-side modal**, even in the numeric mode2 fast match. Existing detached resolved-only frames cannot reproduce that. With original 2–6 human users, whether a side is human-controlled must be determined from the genuine registered user list, not simply current-player side or hard-coded Premier League. The entire source editor's visible controls and linked payload semantics remain **not yet integrated**.

**Independent proof:** authenticated original PE original RTTI names and vtable addresses checked, plus 19 source-address assertions in the `0x4037B0/0x403850/0x4139E0/0x413B40/0x52D370` chain independently passed on the authorized local PE. Dedicated private-executable opt-in regression added to the same unmerged feature branch; branch CI and Win11 GUI have not run. This is a source-qualified *class choice*, not a complete match/tactics/player-flow acceptance.

**Next:** identify exactly which original `FastViewTactics` controls (native events 1–3 and 59–68), the selection validator `0x632B70`, and the 70-DWORD per-side payload communicate the real edits; verify `FastViewCPUTactics` close/status and outer FastView completion. Build an end-to-end original modal/match/result path only after all required side-specific transitions are accounted for.


## Recovery587 continued: source-proven four live human FastView tactical settings and cyclic event pairs

The authenticated original `FastViewTactics` class event dispatcher `0x52E3F0` has four meaningful +/- event pairs **61–68**, and the native label/key dispatchers `0x635E20/40/60/80` select original source string-key pointers from four independent `.data` tables. This source trace now establishes not just the control count, but the **exact native index ranges, wrap behavior, and original localization key identities**:

| Native event IDs (decrease/increase) | Screen DWORD | Allowed indices; exact source string keys | Native wrap |
| --- | --- | --- | --- |
| 61 / 62 | `+0xA58` | **1** `PlayAttack`, **2** `PlayNormal`, **3** `PlayDefend`; table index0 `NOT_USED` | 1 ←→ 3 |
| 63 / 64 | `+0xA5C` | **0** `WithBallNormal`, **1** `WithBallShortPass`, **2** `WithBallLongBall`, **3** `WithBallCounter` | 0 ←→ 3 |
| 65 / 66 | `+0xA60` | **0** `WithoutBallNormal`, **1** `WithoutBallContain`, **2** `WithoutBallPress`, **3** `WithoutBallOffsideTrap` | 0 ←→ 3 |
| 67 / 68 | `+0xA64` | **0** `AggressionLow`, **1** `AggressionMedium`, **2** `AggressionHigh` | 0 ←→ 2 |

Exact source table addresses are `0x8498C8` (4 keys), `0x8498D8` (4), `0x8498E8` (4) and `0x8498F8` (3). Entries point to actual original zero-terminated ASCII keys; functions `0x635E20/40/60/80` index these key tables then delegate `0x6350D0` for original string lookup. Keys identify the intended original selector *values* but do not independently certify the final localized glyphs, native physical coordinates or player-visible mouse hit areas. Distinct value ranges and the reserved Play index0 are mandatory fidelity behavior.

For each pair, native case control decrements/increments the stored screen DWORD and wraps at its exact boundary (source addresses `0x52E440/4AE`, `0x52E51D/593`, `0x52E606/69B`, `0x52E72D/7C2`). The handlers update their associated source combo/list owner and call `0x52F150/1A0/1F0/240`, respectively, which select the matching original string key via `0x635E20/40/60/80` and redraw the relevant native child. The resulting saved selection is not assumed to have committed to the 280-byte side buffer before event3 validator succeeds; see separate event3 `0x632B70→0x6C1CB0` acceptance path.

**Independent verification:** 15 exact original NUL-terminated key strings and all 16 selected native event/control source sites were freshly byte-checked against owner-authenticated PE; added an opt-in private native-source test to the existing FastView feature branch (including corrected proper NUL comparison). Exact branch suite and GUI are still unrun. The source's four settings can now be implemented faithfully within **FastViewTactics** after coordinate/child owner/actual value-transfer evidence is complete; do not accidentally expose them on **FastViewCPUTactics** or the Quick-only current port.

**Next priority:** trace how initial native `+0xA58/+0xA5C/+0xA60/+0xA64` values are populated from original 280-byte per-side state, how `0x632B70` converts/validates selected options, and which original assets/control rectangles permit authentic visible user input. Then integrate the mode2 in-game human tactical modal, CPU counterpart, outer gameplay progression and PResults/return with one-time source-proven state updates.


## Recovery587 continuing original FastViewTactics: preview is NOT an inert pending form; Apply validator also mutates global registry

New first-hand original PE source trace and counterexample review tightened the **essential accepted/cancel/preview semantics** before any normal-port integration. The source has at least **two** distinct mutation opportunities, and the current reconstruction has neither:

1. Human tactics event **59/60** reaches `0x52E967→0x52EF00`, and a separate native owned event `0x36E788` reaches the **same** preview routine from `0x52ED95`. This occurs before event3 (confirmation) and calls three source routines in fixed order:
   - `0x532E40` applies a conditional call to genuine target packed-player `0x4EA350` for source entries whose side slot index is `>=11`, with nonzero count guard, and zeros corresponding source list values. **It is a player record mutation, not just UI glyph refresh.**
   - `0x52EF00` copies the currently edited **70 DWORDs** from `screen+0xA54` into a local temporary array, then calls `0x532EB0`. That method traverses actual participant/club objects, calls original packed-player low-five-bit setter `0x4EA330` and conditional real status functions `0x4182F0/0x4182C0`, and queries `0x4EA3C0/0x4EA3D0` when rebuilding the same side record. It must not be replaced by a purely visual preview.
   - Calls original `0x6C2830` on the original 280-byte payload. Its precise field semantics and full secondary effects still require source follow-up. The user-selected first DWORD `screen+0xA54` has a source event59/60 wrap including sentinel **0x16 (22)**; original `0x635CE0` accepts up to 22 and uses a 23-entry jump table for label selection. This count is not evidence of any particular formation name without resolving its keys.
2. Human tactics event **3** invokes original `0x632B70` *before* conditionally invoking the previously proven `0x6C1CB0` to copy the accepted 280-byte payload. `0x632B70` is not merely a pure form validator: when the passed source-owned linked container's `+0x08` is zero, it **returns false immediately**; when nonempty, it enumerates source objects, invokes `0x634150`, writes original registry state through global `0x981C78` at calls `0x62FD90` and `0x62FE10`, and calls `0x51A340` before returning true. The original sporting type and semantics of the registry still need source qualification; no invented effects or labels are recorded.
3. **Counterexample to simplistic Cancel/Apply transaction model:** a nested cancel event2 posts zero and prevents the *event3-only* side-buffer copy, but other source input/preview events can already have altered player state or other registered objects earlier in the modal. Therefore “cancel always restores every side effect” is NOT source proven. Replay of a match or generic state rollback requires its own original evidence, and the final source-equivalent Win11 host must preserve actual one-time ordering, not blindly back out or duplicate record mutations.

All **28 selected new native-machine-code sites** were independently checked via PE virtual address against the owner-authenticated original, with one mispointed read address corrected from `0x532E87` to verified `0x532E85` in the feature-branch regression before acceptance. Relevant methods are added to the opt-in original source test on the same unmerged branch; no original executable was launched or played. The previous human/CPU, four selector labels, 280-byte per-side accepted path and outer match callback work remain relevant, but **these mutation semantics are a required integration dependency**.

**Next source task:** inspect genuine `0x6C2830` preview recomputation, the `0x632B70` source list element types/0x981C78 registry model, and actual source `0x52EF00` linked event/control producer. Determine how to stage source-equivalent state to support in-match human and CPU tactics without invented placeholder effects, especially across multiple original human users, repeated NEXT/match results and save/load. When a complete source-recoverable unit is found, integrate with local tests and review without lowering native Windows 11 GUI acceptance.


## Recovery587 private original FastViewTactics art and source preview ordering

The authenticated private extracted original FM2001 source Drive tree at `FM2001/FM2001_Art/FastView/` was inspected directly, without extracting the huge disc image. Six **actual native files** were independently byte-fetched, privately hashed and examined. Neither actual files nor image contents were committed to the public repository:

| Original native basename | Google Drive original file ID | Raw bytes | SHA-256 |
| --- | --- | ---: | --- |
| `tactics_arrow_left.444` | `13v8WdFahaTwZ1hSuHewKjFegoenGmHjZ` | 1,552 | `a770e85f2dc82927ae7141a6c6286b0044fae2e354c74df8ceee54437552383c` |
| `tactics_arrow_left_2.444` | `1v9LJkUj40YLeBmyhttHAdY49x-UlFjgn` | 1,628 | `070ce08a38739a8ab32e275e9ea4220214799a5ec207cd098a825c899f2755e6` |
| `tactics_arrow_right.444` | `14e5Sxz2ZILydbE817T_9YT3M3VNtanKU` | 1,592 | `2778776df231ca6e6b380c47aaecfaee47fe09fcfc4aeeb9b80663f9f4effea7` |
| `tactics_arrow_right_2.444` | `1kxRZWwuPZvLyPvlM9OcKZpFrjJkSccid` | 1,664 | `4b6e807b9c9d06928fe46228d2348b95c67ff46a69e86be70302fe82e2cbfc6e` |
| `tactics_popup_1.444` | `1SgoYnkfkhfnG8yO-uKGtwOoQ7LtvBcZl` | 184,624 | `4b9f43545d5ef890baed7fcce1938a399abb3162602f97dd0ef180ece63e406a` |
| `tactics_popup_2.444` | `1qH7qqSIrrjQ9xOT8yqdehx_YnJLSJ2vC` | 180,392 | `adc091388c6776dd3f7cfe9eff7f8b6604eeef98ee0b180f54f1ce22c80c0115` |

Native EA444 header begins 2-byte little-endian width / 2-byte height: both original popup images report **760×400**, while all four native arrow images report **11×48**. Original executable string literals reference these exact paths, plus `FM2001_Art/FastView/Tactics_Injured.444`, `Tactics_SentOff.444`, `Tactics_Booked.444` (some source paths use `reused_Art/`). The use of specific popup variant for human vs CPU, sprite frame count, actual draw positions, clip/target rectangles and input hit zones still require **the relevant native resource owner** and original UI source trace; image header dimensions alone cannot establish the rendered screen or substitute a game GUI. Retain private/source access; do not assume files can be freely committed or render without asset-policy/provenance approval.

Original source preview method `0x6C2830`, called from original live human editor preview routine `0x52EF00`, is also **source verified**: for each source slot index **0..10** it tests original team/player-role matching via `0x6C1E50`, then, if allowed, writes a new monotonically assigned index to `source_payload+0x60+4*selected`; loops over original category indices **1..19** (`cmp index,0x14`). This is a rank/order recomputation for exactly 11 selected entries, not merely visible form text. The exact sporting names/constraints for categories `0x6C1E50` are still unresolved; do not invent them. Independently 8/8 original byte assertions passed and are now preserved as opt-in source tests.

**Next actionable source/implementation dependency:** recover original native resource owners and exact rectangles/hit-testing for popup/arrow assets; trace 0x532E40/0x532EB0 player state effects, 0x632B70 accepted-list registry updates, 0x6C1E50 role matching and 0x52F0F0/1A0/1F0/240 text controls. Once supported, wire a source-correct live FastViewTactics input and restore under original match R1, including CPU panel and PResults. Gate13–17 remain OPEN, no original process or Win11 GUI run, no PR/CI for partial research branch.


## Recovery587 original resource identity further closed: executable filename → 444 loader → actual sprite wrapper

The six private FastViewTactics assets in the preceding section now have their **actual original loader chains byte-matched** to the same authenticated EXE, not merely file names/Drive metadata:

- Popup1 filename ASCII at native VA `0x8389A4` is passed by 0x5FD4A0 into native `0x64D750` resource owner **0x942670**. A separate screen sprite construction at `0x527DCE` uses **that same exact owner 0x942670**, calling `0x64E500` with source dimensions **760×400**, agreeing with the privately authenticated original 444 header.
- Popup2 filename at `0x8389CC` is loaded at `0x5FD4F0` by `0x64D750` into owner **0x942650**; source sprite wrapper `0x52B715` passes the same 0x942650 to `0x64E500`, also with native dimensions **760×400**.
- The four original arrow literal file names at native `0x835208/0x835234/0x835260/0x835290` are passed to original `0x64D750` by `0x5F3040/0x5F30D0/0x5F3160/0x5F31F0` respectively. Native owners **0x946EB0,0x946E70,0x946E30,0x946DF0** are passed to `0x64E500` variants at `0x5F3090/0x5F3120/0x5F31B0/0x5F3240`. Their privately verified header dimensions are **11×48**. The actual state-specific left/right variant selection and per-control hit boxes remain to trace.

Direct original string and owner xref verification identified all six identities and their native reader/renderer owner pairs. A new original-EXE opt-in test guards **6 exact NUL-terminated original path literals and 12 actual native assembly sites**; independently **18/18 assertions** passed against the owner-verified PE32. No proprietary graphics committed. This is a genuine reusable original-asset path for source-equivalent Windows render compatibility, but not permission to invent source placement or assert a complete original FastViewTactics screen.

**Next:** tie both popup sprite wrapper call owners to the actual human/CPU class construction/visible scene, resolve source frame indices, crop rect, x/y, arrow control IDs/hit target and data-binding; then use the original assets as the default instead of placeholder drawn controls. Keep current reconstruction mode2 fail-closed until match lifecycle and player mutation parity proven.


## Recovery587 original editor three separate entry controls and accept's exact live ownership

The native `FastViewTactics` human popup has **three different primary event flows**, not merely confirm vs cancel:

- **Event1** at `0x52E854` calls the class's reached virtual slot `+0x08` then enumerates and removes source working-list objects from `screen+0x48A8` using `0x5302F0`; when screen byte `+0xB44` is nonzero, eleven native child controls starting at `screen+0x263C`, stride0x44, receive their vtable **+0x38** callback. No `0x6539F0` modal exit is shown in this direct event1 path. Its exact user-facing label and whether downstream virtual callbacks mutate global game state are still unresolved.
- **Event2** at `0x52E8D2` posts native WM_USER exit with argument **zero**; it is the direct Cancel/close *event transaction*, with the caveat from previous section that other preview interactions may already have mutated player objects.
- **Event3** at `0x52E8DF` obtains selected side `screen+0x90` and actual world/global record `[0x877844] + 1`, passes `screen+0x48A4` original working-list source (NOT the 280-byte buffer) to `0x632B70` for the global list/record validation and side effects. On true result only, it passes `screen+0xA54` 70-DWORD edited source and same side to `0x6C1CB0`, updating selected default side buffer. Posts modal Boolean 0/1 via `0x6539F0` in both cases.

All 14 bounded new original executable source sites independently matched the verified private EXE; appended opt-in regression. This narrows what must be source-replayed exactly and distinguishes original Reset/rebuild vs Cancel vs Apply controls. It also blocks the tempting but incorrect implementation of a simplistic form in which every Close equals state rollback, every click is applied immediately to the source match, or a confirm merely writes four dropdowns.

**Next:** source-verifiably identify event1's virtual method effect, initial editor source list and native text/arrow child geometries, and whether original `0x632B70` failing on an empty list (0x632B96) is intended rejection for a legitimate unchanged 11-player formation. This is a correctness question, not license to treat an empty list as success or force the user to change something. Then connect the real modal to the normal R1 match transaction and presentation only after original return and PResults can be tested coherently.


## Recovery587 first source-derived code component: native human +/- selection values (bounded, NOT live mode2)

The existing mode2 source branch now contains two new implementation/test files, deliberately scoped to the verified subset rather than claiming a complete editor:

- `reconstruction/original_fastview_tactics_selection.py` models an immutable full **280-byte** original side-payload draft from original `screen+0xA54`, and source events **61–68 ONLY**, changing exactly one authentic DWORD at indices1..4 with original observed wrap ranges and exact original localization-key identities. The 65 other DWORDs and first source selection word remain byte-for-byte unchanged. Non-int/unrecognized events, wrong-sized byte payloads and source-unverified selector values fail closed. It does **NOT** replay control-list changes, `0x52EF00` preview native packed-player mutations, `0x632B70` registry effects, `0x6C1CB0` match commit or the original modal; it cannot be used as a substitute for live gameplay.
- `reconstruction/test_original_fastview_tactics_selection.py` covers all eight decrease/increase boundary transitions, preservation of unaffected fields, normal value changes and fail-closed unknown events/inputs. A structurally equivalent standalone local Python implementation was executed with **3/3 tests passing** in the private analysis container. The **actual exact new GitHub files** have **NOT been executed via branch CI**; keep that distinction explicit until a cohesive integration runs exact-head validation.
- Original private executable x86 byte tests, source research and six original private native art receipts remain on the same feature branch; no PR opened, no CI billed, no main-branch modifications.

This is recoverable preparation for the original FastViewTactics modal, **not** a completion or acceptance milestone for source mode2 R1 or Gate13. Next meaningful integration requires real native artwork/control geometry, list-owner preview/Apply/Cancel side effects, pre/postmatch state and result callbacks, and ordinary Windows 11 player acceptance.


## Recovery588: both native tactics popup placements and complete eleven-row arrow constructor coordinates

The original authenticated PE was inspected again read-only in Recovery588, and the previous six Drive-sourced tactics 444 files remain unchanged. This establishes an **entire original 11-row control geometry family**, instead of only isolated sprite resource names. No original EXE execution or live GUI observation was performed.

1. The reached original human `FastViewTactics` screen uses the **native popup1 owner `0x942670`**, original source wrapper at `0x527DCE`, and sets the sprite through `0x64F380` at source `0x527E09` with **x=20, y=139**. The original CPU `FastViewCPUTactics` screen uses **popup2 `0x942650`** at `0x52B715`, and the matching source geometry setter at `0x52B752`, **also x=20, y=139**. Both are source-native 760×400 image bounds inside a native 800×600 modal. The `0x64F380` code at `0x64F38F..0x64F3B3` really stores x in child+8 and y in child+12 and derives right/bottom from the source width/height; this is stronger than a mere coincidental literal. No claim about final palette compositing or camera appearance is made.
2. The original human tactics class constructor creates a separate **11-row family** of four `0x651E30` image/control objects per row, sourced from original four arrow resources `0x946E90` (left), `0x946E50` (right), `0x946E10` (left variant2) and `0x946DD0` (right variant2). Their coordinates from actual source push arguments are:

| Original row index | Native y | Left x | Right x | Left variant2 x | Right variant2 x |
| ---: | ---: | ---: | ---: | ---: | --- |
| 0 | 278 | 69 | 120 | 407 | `[0x947304]+420` |
| 1 | 295 | 69 | 120 | 407 | `[0x947304]+420` |
| 2 | 312 | 69 | 120 | 407 | `[0x947304]+420` |
| 3 | 329 | 69 | 120 | 407 | `[0x947304]+420` |
| 4 | 346 | 69 | 120 | 407 | `[0x947304]+420` |
| 5 | 363 | 69 | 120 | 407 | `[0x947304]+420` |
| 6 | 380 | 69 | 120 | 407 | `[0x947304]+420` |
| 7 | 397 | 69 | 120 | 407 | `[0x947304]+420` |
| 8 | 414 | 69 | 120 | 407 | `[0x947304]+420` |
| 9 | 431 | 69 | 120 | 407 | `[0x947304]+420` |
| 10 | 448 | 69 | 120 | 407 | `[0x947304]+420` |

   **Critical unknown deliberately preserved:** the fourth arrow does NOT use a recoverably constant x of 418, 420, or 407 in the source. The initial row at `0x52830F` loads original global `[0x947304]` before the `0x528314` push, and the `add eax,0x1A4` is executed after pushing the sprite owner; other rows follow the same owner/add/Y/actual EAX push shape. The runtime value of this global and whether it derives from a screen anchor are **not independently established**. Do not substitute a guessed pixel coordinate.
3. An **additional lower pair** of first-variant left/right arrows is constructed at **(303,481)** and **(379,481)**, source sites `0x52AE1D` and `0x52AE7A`. These are separate from the eleven repeated row quartets. Their physical user role/event mapping is not yet proven by the constant positions alone. The original arrow files are header **11×48** (likely three stacked 11×16 states; native wrapper passes width11/height16); source frame selection and clipping still require original control method investigation.
4. Reproduction: take owner-authenticated original `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; for each actual owner immediate xref inside constructor `0x527C00..0x52B000`, decode following original `push y` and `push x` (or `add eax,420; push y; push eax` for the dynamic fourth) and trace `0x651E30 → 0x651BA0 → 0x64F380` for target x/y semantics. Independent local PE read-only test passed **49/49 direct source checks**: 44 repeated arrow controls, the two lower controls, both native popup placement callsites and the base geometry writer. These are independent local checks; the exact branch integration tests and Windows11 GUI were NOT executed.

**Persisted working code (unmerged):** `reconstruction/original_fastview_tactics_control_layout.py` now contains a source-only immutable record of all 46 arrow controls and panel geometry, with fourth variant x explicitly dynamic. `test_original_fastview_tactics_control_layout.py` guards 11 row geometry and has opt-in original PE assertions for all 44 instances plus the two extra controls. It does not expose click behavior, artwork rasterization, status changes, or a live mode2 match. No proprietary bytes were added to the repository.

**Next source question**: recover `[0x947304]` actual producer and its relationship to source GUI coordinates, plus native event-to-child mapping and five state objects in FastViewTactics; trace effects of the 11-row 0x651E30 controls and lower pair through the reached event handler. Only then implement original player-visible click/raster routes with source-validated transaction and modal return.


## Recovery588: original right-arrow x global resolved to width of original `name_input_box_7.444`

The formerly deferred native x-expression **`[0x947304] + 0x1A4`** now has an original-owned source initialization:

- `0x947304` equals **original resource/sprite owner `0x9472F0` +0x14**. Owner `0x9472F0` is constructed at `0x5F26B0` through authentic `0x64E500` with explicit width **0x7C = 124** and height **0x10 = 16**. Native `0x64E58F` stores constructor `ebx` in owner+0x14; `0x64E592` stores height in +0x18. The executable loads that sprite's source resource owner `0x947310` from the exact original filename literal `0x834D9C`: `FM2001_Art/Generic/GenericButtonsAndBars/name_input_box_7.444` through native `0x5F2660 → 0x64D750`.
- Owner-authorized extracted original native file privately retrieved directly from existing Google Drive (ID `1CR-mQUC-15qOM6GnacW-vjLOHpIlBU4k`), **6,760 bytes**, SHA-256 **`c2d70cda86db1f39c95ff4579a059157841326c07a401848968c87c41b3ff415`**. Raw verified original EA444 header independently reads **124×64**, consistent with constructor's one-frame 124×16 selection. No private binary was added to Git.
- The original human tactics constructor reads **`[0x947304]`** at `0x52830F` and passes **that value plus 420** as the fourth arrow's native x coordinate. At source initialization the resulting x is exactly **544**, not an estimate. The source **still reads a live mutable owner field**; no global proof excludes later indirect sprite-width replacement, so the port records the initial width 124/initial x544 separately and retains a value-dependent x calculator rather than hardwiring 544 unconditionally.
- This resolves the previously missing initial-control-x dependency for all eleven right-variant2 arrows. It does not establish their click-event receiver, hit rectangle, frame animation choice, mode-specific draw palette or player-record mutations. Those remain separate source obligations.

A new pure source-layout helper `OriginalFastViewTacticsArrowPosition.resolved_native_x(original_box_width=...) ` refuses to invent a live dynamic width and returns x544 when supplied the independently original-proven initial 124. A focused test now checks source `0x5F26B9` width constructor, owner `0x5F26C6`, `0x64E58F` write and the actual `0x52830F` consumer as well as 44 previous geometric callsites. Independent local PE reads verified the chain; exact GitHub branch tests/CI and Win11 GUI still unrun at this report update.

**Next:** source-map actual first-class event IDs 59–68 to the reached screen's child widgets and source hit regions, establish `name_input_box_7` control's clipping/frame display and the rest of tactics art owners, then connect verified control model to authentic modal transitions. Keep the live mode2 unavailable until real player/state/validation/results ordering is verified.


## Recovery588: all eight native human tactics setting event widgets placed and original source art identified

The previously qualified *numeric* four-setting event pairs **61–68** are now connected to the actually constructed native control objects and their source-renderer rectangles. They are **NOT the same graphics or controls as the 11 player-row `tactics_arrow_*.444` sprites**; using those 11×16 arrows as buttons for attack/passing/defense/aggression would be a false reconstruction.

| Actual original child event | Setting source DWORD index | Input-child native x | Native y | Source construction |
| ---: | ---: | ---: | ---: | --- |
| 61 (decrease) | 1 | 576 | 278 | `0x52AEE0 → 0x52AF18` |
| 62 (increase) | 1 | 733 | 278 | `0x52AFCD → 0x52B00A` |
| 63 (decrease) | 2 | 576 | 334 | `0x52B06E → 0x52B0A6` |
| 64 (increase) | 2 | 733 | 334 | `0x52B156 → 0x52B191` |
| 65 (decrease) | 3 | 576 | 390 | `0x52B1F2 → 0x52B22A` |
| 66 (increase) | 3 | 733 | 390 | `0x52B2DA → 0x52B312` |
| 67 (decrease) | 4 | 576 | 446 | `0x52B376 → 0x52B3AE` |
| 68 (increase) | 4 | 733 | 446 | `0x52B45E → 0x52B496` |

The class constructor registers exact IDs 61–68 on children and then calls `0x64F380` on **those same source children** with the listed native x/y plus resource-provided width and height. All **eight ID-push sites and eight geometry push pairs, 16/16 first-hand original byte checks**, independently passed. These positions, combined with original selector DWORD bounds and string-key semantics recovered previously, are a meaningful original UI contract, though pointer hit-state, click-result input delivery and remaining control subtrees are not yet independently accepted.

Original source resource for these eight widgets is **`FM2001_Art/Generic/GenericButtonsAndBars/scroller_hori.444`**, filename literal at `0x835018`, loader at `0x5F2C40` into native original owner `0x947070`. The native `0x5F2C90` wrapper selects an original **25×18** source crop to child sprite owner **0x947050**; the `0x5F2CD0` wrapper selects the other vertical crop (source y=18) to child sprite owner **0x947030**. The resulting original child owners are explicitly assigned in the human tactics constructor (`0x52AF24`, `0x52B016` and sibling sites). These are **source-native horizontal scroller graphics**, not a plausible new dropdown design.

From the owner's verified extracted private Drive source tree, two actual 444 files were newly retrieved and SHA-256 checked, with **no proprietary source bytes committed**:

| Original private file | Google Drive ID | Real bytes | EA444 header (width×height) | Actual SHA-256 |
| --- | --- | ---: | --- | --- |
| `GenericButtonsAndBars/scroller_hori.444` | `1Ku4p38APZIU8F9WenbApHRSGU7KDKkDs` | 5,612 | 100×36 | `84407c5bf69adc1af56aab46fe30d8da876c54c0538ec70963453bf6b2800a09` |
| `GenericButtonsAndBars/scroller_bar_hori.444` | `1johcXpVJp7SYK2wK2RVi9_BNhJdpdV2Y` | 2,656 | 100×18 | `6edfba6b058a34582284eb5a2c05ba1c63d2c35fd9a458273cf435b967c6aedc` |

The second file identity/bytes are independently verified, but its actual per-child role in *these eight events* has **not** been established by this trace; do not substitute it without source ownership evidence. For `scroller_hori`, 11 additional exact original PE source loader/crop/owner assertions independently passed. The persisted code `original_fastview_tactics_control_layout.py` now records the eight native event control coordinates and scroller atlas/frame crop source facts; matching regression tests exist on the same WIP feature branch.

**Remaining high-impact original mode2 blockers:** full `0x6503F0/0x64F380` click hit-state conditions and original event bubbling into `0x52E3F0`; source player-row edit/preview native effects `0x532E40/0x532EB0/0x6C2830`; `0x632B70` global registry validation and first/second side mutation; original outer FastView closure and PResults/management return. No player-visible native mode2 implemented or original Win11 acceptance. Do not merge/close gate based solely on complete layout constants.


## Recovery588: 55 additional original human tactics per-player events uncovered beyond IDs1–68

The prior `FastViewTactics` low-event switch at `0x52E3F0` accepts source IDs1–68 and assigns ID4–58 to a common **fallback target `0x52E975`**. Crucially that branch is NOT an inert no-op: its subsequent **five large non-contiguous event ranges** select *eleven* native row actions each. Treating IDs4–58 as the entire player-row event inventory was incorrect; the actual user-selected player controls supply high numeric event IDs.

| Authentic event range inclusive | 11 source rows | Reached native action (bounded evidence) |
| --- | --- | --- |
| `0x247276..0x247280` | 0–10 | calls `0x6C2170` with side, original source team/list context and **flag1** |
| `0x246E8E..0x246E98` | 0–10 | same `0x6C2170` but **flag0** |
| `0x2466BE..0x2466C8` | 0–10 | **decrements** the selected row's value at `screen+0xAFC+4*row`, wraps -1 to 10, constructs `0x6334C0` source 12-byte edit object, appends it to `screen+0x48A8` linked list and increments `+0x48AC` |
| `0x246AA6..0x246AB0` | 0–10 | **increments** the selected row's value at the same screen+0xAFC array, wraps index 11 to 0, enqueues the source 12-byte edit record with `0x6334C0` |
| `0x8877AE..0x8877B8` | 0–10 | checks indexed `screen+0x263C+0x44*row` native child state via `0x651AB0`; then calls original real state guard `0x633020`, optionally `0x6C2770`, and appends a source edit through `0x6335D0`. Exact conditional semantics and player-record effects need follow-up. |

Source range checks sit at `0x52E97C/983`, `0x52E9CD/D4`, `0x52EA04/0F`, `0x52EAD2/DD`, `0x52EBA2/AD`. They are *exclusive* upper bounds (first ID + 11). A separate independent local static-source read checked **22 native hex sites** covering all five ranges and representative mutation/conditional callsites, with 22/22 matching canonical 4,714,541-byte original SHA `833bf95e...`. The opt-in original PE byte test now preserves these checks.

`reconstruction/original_fastview_tactics_selection.py` now exposes **read-only** `source_classify_fastview_player_control_event`, which maps exactly the five source 11-ID families to native row0..10 without simulating any `0x6C2170/0x6C2770` side effects or guessing their football labels. The companion standard unit-test file now asserts all 55 valid events and fail-closed neighbors, bool, noninteger and unrelated low-ID events. Code and tests are on existing feature branch; **exact branch tests/CI remain unrun**, and neither original executable nor current port was graphically played. This is source-audited event ownership, **not** a completed in-match tactics editor.

**Next highest-impact:** trace original `0x6C2170`, `0x6C2770`, `0x633020` and original constructor event ID producer/hit controls to establish the precise role/substitution/selection semantics and owned record mutations; then reconcile native staging and modal result with the outer FastView full match lifecycle. Implement source-proven reversible paths but do not infer that Cancel backs out edits already committed during preview. Gates13–17 remain OPEN.


## Recovery588: high-ID row handlers are stateful; 70-DWORD working edits and real reordering (original static source)

The authentic high-ID event decoder was followed into its actual callee byte paths. These substantially change the original tactical-editor behavioral contract:

- **`0x6C2170` (first two 11-event families)** copies **70 DWORDs** from actual current `screen+0xA54` into temporary memory, then calls source `0x6C1F90`. That routine considers the user-selected row's original `+0x18` category, `+0xF2` actual row mapping and original `0x6C1E50` compatibility table when adjusting it; the source explicitly has nonsequential transitions around values `0x0F,0x12,0x13`. The callee compares the old and new record fields and creates linked-list objects using **`0x6334F0`** when they change, increments the source list count, sets the working payload DWORD0 to sentinel **22** and creates an additional source event object via **`0x633490`**. It cannot safely be replaced with a bare toggle or arbitrary index++.
- **`0x6C2770` (fifth 11-event family, after its original gate)** searches actual source `payload+0xF2` row index bytes to find two positions, decrements source counter `+0xF0`, clears indexed flag byte `payload+0x104+selected`, swaps two indexed bytes in `+0xF2`, and copies per-row DWORD **`+0x18` and `+0x60`** from one selected slot into another. It then conditionally adjusts source counter `+0xF1` using the actual global `0xA14C0C` lookup. This is **real source state mutation**, not a passive preview. Its exact club/player rules and preconditions still require qualifying `0x633020` and original match participant mapping.
- **`0x633020`** on the same fifth-family route uses a linked-list source count `0x633240`; for empty/non-applicable input returns false at `0x63317E`, otherwise traverses source nodes and delegates to **`0x6331A0`** to combine native Boolean results. It mutates/clears its intermediate container while evaluating. Returning true/false alone is insufficient to reconstruct its original state effects.
- **Third/fourth 11-event families** are therefore also NOT simple UI rotations: native code enqueues a `0x6334C0` source edit record each time it increments/decrements the bounded `screen+0xAFC+4*mapped` numeric value. The *actual mapped index* is original **BYTE `screen+0xB46+visible_row`**, which may not equal the selected visible index. Any replay that silently assumes identity could edit the wrong player.

An additional **34 original PE exact-address assertions** were independently checked against the canonical owner source covering the 70-DWORD copy, sentinel/edit queue, actual row-field swaps, status counters and validator. All 34 matched, and source-guard tests were appended on the existing branch. Original executable still was NOT run.

**New bounded code:** `OriginalFastViewTacticsSelectionDraft.with_original_player_row_step_value_only` now reproduces *only* the source numeric part of the third/fourth families: it requires an explicit caller-supplied authentic row mapping, indexes the real 280-byte payload at DWORD **42+mapped** (since `0xAFC-0xA54 = 0xA8`), cycles 0..10 with wrap, preserves every other byte and fails closed on unknown values. It **intentionally does not** simulate the original edit object/list side effects. The companion unit tests exercise all eleven mapped rows, wrap and invalid unmapped input. Exact branch CI/unittest still unrun; do not promote numeric-only draft to a working player click.

**Next integration dependency:** recover the original per-control event producer and `screen+0xB46` mapping, prove `0x633020` linked-list and `0x6C2170` source object semantics, then implement actual source transactional player edits (with original per-event mutation and persistence) before connecting live mode2 to PResults and management return. Keep original UI and match state honest and fail closed until independently verified.
