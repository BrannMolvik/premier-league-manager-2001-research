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
