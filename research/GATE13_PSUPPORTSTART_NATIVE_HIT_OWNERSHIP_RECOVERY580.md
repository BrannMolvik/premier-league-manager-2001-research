# Gate 13 Recovery580: native PSupportStart input ownership and hit-gate limits

**13 October 2026 KST.** Original, unchanged private `footballmanager.exe`, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, inspected statically with `objdump -D -Mintel` and MSVC RTTI. **Not an original gameplay run or Windows 11 GUI acceptance.** Gates 13–17 remain OPEN.

## Original RTTI and final row-child dispatch

The original **final** native vtables (not temporary constructor base vtables) and their RTTI complete-object locators establish this row/control hierarchy:

| Original row owner | Final vft | RTTI | vft+0x6C input dispatch |
| --- | --- | --- | --- |
| Group row parent | `0x7C6780` | `StaffGroupToggle` | `0x5D6270` |
| Group child +0x38 | `0x7BE9BC` | `ToggleButton@ease_2001` | `0x652B50` |
| Group child +0x3C | `0x7C66C8` | `SupportStartText` | `0x652B50` |
| Group child +0x40 | `0x7C66C8` | `SupportStartText` | `0x652B50` |
| Group child +0x44 | `0x7BE530` | `Bitmap@ease_2001` | `0x64F7A0` |
| Group child +0x48 | `0x7BFF14` | `NumText@ease_2001` | `0x64F7A0` |
| Modal owner | `0x7C6DDC` | `PSupportStart` | `0x5D4940` |

The registration flags are `(0x33,0x31,0x31,0x15,0x15)` in this order. Native row `0x5D4790` at `0x5D47C6..0x5D47CD` explicitly gates *child* dispatch on registration flag `0x04`. **Only +0x44 and +0x48 are eligible under this child loop**. The first three child objects are real visual/text/button children, but their registration flags do not authorize them as accepted input dispatches *through this loop*. This does **not** mean they cannot affect other original event paths.

Original `0x5D6270 -> 0x5D4790` calls parent `0x64F7A0` first when the second native argument is nonnull (`0x5D479B..0x5D47B3`). A rejected parent ends immediately, regardless of child flags. Otherwise it loops the registered children, tests `0x64F570` state bit0x01, calls eligible child vft+0x6C (`0x5D47E8`), ORs parent/children results and, when accepted, toggles row bit15 via virtual+0x98 (`0x5D629D`). These are source dispatch rules, **not screen-coordinate mapping**.

## Why source layout rectangles are NOT native mouse hit tests

Native `0x64F7A0` first requires control state `[control+0x18] & 0x02 != 0` and `[control+0x18] & 0x10 == 0` (`0x64F7A5..0x64F7BA`). If control+0x20 is nonnull and the event argument is nonnull, it calls an opaque object in control+0x24 through **virtual+0x0C** (`0x64F7D3..0x64F7DF`), which can veto acceptance. Accepted routing also invokes the control's virtual+0x1C with argument 1 (`0x64F801..0x64F807`) and can call a second callback through vft+0x10 (`0x64F811..0x64F81C`). Active-global observer pointers at `0x984810`, `0x984818` and `0x984814` may receive notifications. The complete native mouse event value, parent coordinate transform, callback object identity and real hit decision are not observed. A bare original layout rectangle is therefore not proof of a successful native click.

Native `0x64F570` is only a *state-bit accessor* (`[control+0x18] & 1`). Native `0x652B50` starts with a further `0x64F7A0` call and, when callback-qualified, invokes `[control+0x24]` vft+0x0C, conditionally control vft+0xB0 and callback vft+0x10. It also does not establish a rectangle-only coordinate decision. Native `0x5D4900` row parent vft+0x0C propagates an argument to each registered child vft+0x0C before local `0x64F3E0` state flag routing. These are independent of row visual geometry.

## Integration boundaries and next source-backed work

Source module `original_supportstart_input.py` already requires observed parent/child acceptances; `original_supportstart_layout.py` carries qualified layout rectangles and `original_supportstart_editor_projection.py` holds staged seven-row Apply/Cancel. **Do not replace native acceptance with `x,y` inside 326×37 row rectangle** or infer clicked children from names, button images, or a hit on the rectangle alone. Also never generate staff names using a fresh RNG or bypass the two selected-user queue drains.

**Next:** trace the actual modal event-context and pointer/coordinate ownership passed into `0x64F7A0`/control+0x24 vft+0x0C for each registered input child; establish a reproducible original hit predicate and its modal/viewport transform, then connect the complete seven-row controls and native Apply/Cancel transaction into the real player flow as one coherent tested UI milestone. If the original event callbacks require runtime-only evidence, document the exact missing original-process receipt and advance other source-proven player-visible Gate13 elements rather than claiming interaction parity. Do not open a standalone research-only PR or run CI until a reviewed substantive integration is ready.

## Recovery581: original selector star-strip and native input-event prefilter

**13 October 2026 KST.** Independently materialized the owner's actual 4,714,541-byte private original executable from the verified Google Drive standalone file and computed SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Used GNU `objdump -D -Mintel` against **that actual executable**; did not run it.

### Five-state original source bitmap, now owner-proven

The original row `0x4C96A3..0x4C96BC` passes its source state to `0x4C97D0`, a bounded unsigned switch on `state-1 <= 4`. Its five exact return pointers, in state order, are:

| Source state | Native wrapper | Native initializer | Input `stars.444` crop (x,y,w,h) |
| --- | --- | --- | --- |
| 1 | `0x945890` | `0x5F6310` | (0,0,15,10) |
| 2 | `0x945850` | `0x5F63A0` | (0,0,30,10) |
| 3 | `0x945810` | `0x5F6430` | (0,0,45,10) |
| 4 | `0x9457D0` | `0x5F64C0` | (0,0,60,10) |
| 5 | `0x945790` | `0x5F6550` | (0,0,75,10) |

All five native initializers call `0x64E500` with **height 10, origin (0,0), and cumulative widths 15, 30, 45, 60, 75** (NOT five independent 15-pixel slices). Each preceding initializer calls `0x64D750` with the **same literal `0x836414`**, the exact original `fm2001_art\\support\\stars.444` string. The actual separate original asset was previously byte-verified as 75×10 in Recovery545. Out-of-range states fall through `0x4C9809` to **NULL**; no clamping or duplicate-sprite fallback is justified. The fifth wrapper `0x945790` is also used in non-selector contexts, which does not change this five-state source mapping.

The already-merged `reconstruction/original_supportstart_stars.py` and `test_original_supportstart_stars.py` **correctly implement and verify the cumulative crop**, including the original byte-identical `stars.444` asset. An initial Recovery581 duplicate interpretation incorrectly treated the widths as x-offsets; it was **caught by comparison with the merged source module and reverted on this in-flight branch** before any PR or release. Do not recreate that incorrect independent-slice interpretation. This is **art ownership/layout evidence, not a player-visible renderer or native hit test**. The original proprietary image remains outside Git.

### Original pixel event ingress, still not final native acceptance

Disassembly `0x653480..0x653502` shows a native window receives an `int32 x,y` pointer, subtracts **that window's** `+0x0C/+0x10` native origin, passes the resulting local pointer through window virtual+0x10 **before** iterating child controls, and checks each enabled child's half-open `+0x08/+0x0C..+0x10/+0x14` layout rectangle. For a qualifying child, it passes the local pointer and literal nonzero `1` to child vft+0x6C. For a `StaffGroupToggle`, `0x5D6270 -> 0x5D4790` then invokes the parent `0x64F7A0` and potentially two eligible child callbacks. Source `0x64F7A0` considers control+`0x20` only when the event argument is nonnull; if present, the callback object at +`0x24` can veto. Source base constructor `0x64F300` writes +`0x24=0` and +`0x18=0x183`, but does **not** itself initialize +`0x20`. Source `0x64F3C0` and group propagator `0x5D48C0` *can* assign/propagate +`0x20/+0x24`, so a constructor default cannot prove the live modal's final callback value.

The source path establishes the *native event pointer shape and prefilter*, but the actual caller's window instance, its predispatch vft+0x10 state mutation, final callback assignment/lifetime, row+child state at ordinary TeamSelect entry, and GUI mouse release/Apply/Cancel side effects are **not yet observed end-to-end**. Do not equate a rectangle pass with a successful native toggle. Next inspect PSupportStart `0x4CF0F0` setup/callers and the `0x5D48C0` propagated callback writer, then connect only established event/asset ownership to the full player-visible modal; otherwise defer that exact original-process observation and switch to other Gate13 source-qualified surfaces.

Reproduction (with authorized private original binary kept outside the repository):

```bash
sha256sum footballmanager.exe
objdump -D -Mintel --start-address=0x4c97d0 --stop-address=0x4c9810 footballmanager.exe
objdump -D -Mintel --start-address=0x5f6300 --stop-address=0x5f6580 footballmanager.exe
objdump -s --start-address=0x836410 --stop-address=0x836450 footballmanager.exe
objdump -D -Mintel --start-address=0x653480 --stop-address=0x653503 footballmanager.exe
objdump -D -Mintel --start-address=0x64f300 --stop-address=0x64f3d1 footballmanager.exe
objdump -D -Mintel --start-address=0x5d48c0 --stop-address=0x5d48f8 footballmanager.exe
```

**Acceptance:** cumulative source-frame mapping independently VERIFIED against original static bytes and the existing merged source module; no new branch implementation test run. Existing merged tests are not a GUI acceptance claim. Player-visible SupportStart and original-process/Windows11 GUI acceptance NOT VERIFIED. Gate13–17 remain OPEN.

## Recovery581 follow-up: seven native group callbacks resolved, bounded click acceptance now SOURCE-VERIFIED

**Original-source countercheck completed 13 October 2026 KST.** This refines the earlier statement above that callback+0x24 was necessarily unresolved: **the callback identity and result for all seven ordinary PSupportStart row parents are in fact static-source recoverable**. It does not license invented state, user names or a completed GUI.

1. The final `StaffGroupToggle` vft at `0x7C6780` has vft+0x08 = `0x5D48C0` (verified direct original PE `.rdata` bytes). Native `0x4C7B70` registers the seven exact row objects `PSupportStart+0x2224+0x4C*i` in child slots 8..14. At row0 `0x4C8017..0x4C803E`, it pushes modal-owner `esi`, then native group index **8**, and calls that row's vft+0x08; row1 `0x4C8068..0x4C8090` uses index **9**, with corresponding source index continuation through 14. The real call arguments are **first group ID (8..14), second modal-owner pointer**, not arbitrary coordinates.
2. `0x5D48C0..0x5D48D5` calls native `0x64F3C0` with those two values. It explicitly writes `row+0x20 = 8+i` and `row+0x24 = PSupportStart owner`, and forwards the same pair to registered visual children. The source ID is nonzero for every one of the seven parent rows.
3. The **final** PSupportStart vtable at `0x7C6DDC` has virtual+0x0C = `0x42DE00`. Direct native disassembly `0x42DE00..0x42DE07` is `mov eax,1; ret 8`, an unconditional acceptance. Hence the previously opaque `0x64F7D3..0x64F7DF` callback calls this PSupportStart owner and returns **1** for the genuine seven registered row parents. This is a concrete class/callsite proof, not a guess about which callback responds to a visual rectangle.
4. Native `0x653480..0x653502` receives the original window pixel pair, shifts by the window origin, invokes the modal owner's vft+0x10 with **NULL first event arg**, then tests each row's enabled bit0 and half-open rectangle and calls row virtual+0x6C with a real local point pointer and nonnull literal `1`. The owner's final vft+0x10 = `0x4D05E0`; when called with NULL, `0x4D05E0..0x4D0641` bypasses action events1..20 and merely invokes `0x653350` with its window redraw rectangle. This original ingress does **not** dispatch Apply/Cancel as a side effect of the prefilter.
5. For a genuinely registered PSupportStart row reached through that ingress, the parent `0x64F7A0` accepts when its current DWORD state has bit1 (`0x2`) set and pressed bit4 (`0x10`) clear; the source owner callback **cannot veto**. Parent acceptance is ORed with eligible child input results in `0x5D4790`, so child rejection cannot overturn it. Original `0x5D6270` then flips that row's parent bit15. The source hit predicate is therefore the enabled bit0 and half-open native row bounds, combined with parent bit1 and not bit4, **given the actual modal window, registered row identity, current source state and original pointer-down event**. Empty/disabled rows still fail the parent's state check; a held pressed row fails until native release. The input predicate does not separately prove an actual Win11 GUI player clicked that row.
6. `reconstruction/original_supportstart_input.py` now includes `original_supportstart_source_window_click_accepts_row`, which composes the *already source-qualified* original layout window prefilter and the callback-resolved parent state gate. Targeted tests in `test_original_supportstart_input.py` cover inclusive/exclusive pixel edges, blocked empty/disabled/pressed rows, seventh row and malformed data. The bounded source function is **not yet wired to Tk/current selected-user state**, and no new CI/Windows playtest has been run. Further UI work must still restore original row rendering, name/staff data, Apply/Cancel state mutations and real modal return, preserving original events/queued RNG.

**Independent counterexample check:** Original constructor `0x64F300` alone is insufficient evidence to omit +0x20; **actual native `0x4C803E` vft+0x08 passes nonzero 8 and the modal owner**. Conversely, the case of a plain Bitmap or a different non-SupportStart native control whose `+0x24` points elsewhere is NOT covered by this seven-row result and remains unknown until independently traced. Never generalize unconditional acceptance to all native controls, to Apply/Cancel buttons, or to GUI event delivery. Separately, originally reported independent 15-pixel star slices were wrong and reverted; authentic star-strip crops are **cumulative**.

Reproduction, private original EXE outside Git (byte hash as above):

```bash
objdump -s -j .rdata --start-address=0x7c6780 --stop-address=0x7c6795 footballmanager.exe
objdump -s -j .rdata --start-address=0x7c6ddc --stop-address=0x7c6df2 footballmanager.exe
objdump -D -Mintel --start-address=0x4c8014 --stop-address=0x4c8095 footballmanager.exe
objdump -D -Mintel --start-address=0x5d48c0 --stop-address=0x5d48f8 footballmanager.exe
objdump -D -Mintel --start-address=0x64f3c0 --stop-address=0x64f3d1 footballmanager.exe
objdump -D -Mintel --start-address=0x42de00 --stop-address=0x42de08 footballmanager.exe
objdump -D -Mintel --start-address=0x653480 --stop-address=0x653503 footballmanager.exe
objdump -D -Mintel --start-address=0x4d05e0 --stop-address=0x4d0679 footballmanager.exe
```

**Updated next task:** verify the original mouse-up path and source row initialization/live staff records, then connect the original seven-row PSupportStart graphics/interaction and native Apply/Cancel transaction to the ordinary TeamSelect frontend. The claimed input route now has a narrow static original-source proof; standalone source tests/byte proof still do NOT close the complete player workflow, Gate13 or Windows11 acceptance.

### Recovery581 subsequent source child and release countercheck

A separate direct original `.rdata` inspection verifies final Bitmap `0x7BE530` and NumText `0x7BFF14` BOTH resolve vft+0x08 to `0x64F3C0` and vft+0x6C to `0x64F7A0`. Native parent `0x5D48C0` propagates the exact same nonzero callback ID and PSupportStart-owner pointer through each registered child vft+0x08. Thus the two input-eligible group children also have a source-resolved callback response 1 (when their state permits it) and a source-resolved blocked state response0. `0x5D4790` invokes them only when their registration flag has bit0x04 and their control has bit0x01. `0x4D05E0` event IDs8..14 are the non-action/redraw dispatch branch; they never enter native Apply/Cancel cases 1/2.

The branch now composes `project_original_supportstart_source_pointer_down` from the native window source predicate and real parent/child gates, producing the existing bit0x10 pressed / bit15 toggle observation. The separate original native mouse-up `0x653510` broadcasts vft+0x70 through all registered window children, and group `0x5D4800` calls parent `0x64F860` plus bit0-enabled eligible fourth/fifth children to clear pressed bit0x10. This **does not** revert row selection bit15. New tests cover first click, rejection of repeated down while still pressed, explicit source release, second click, parent-only acceptance and empty/rectangle rejection. These are pure projections conditional on externally qualified native modal/row state, NOT native executable/UI acceptance and NOT assertions that original GUI was run.

```bash
objdump -s -j .rdata --start-address=0x7be530 --stop-address=0x7be548 footballmanager.exe
objdump -s -j .rdata --start-address=0x7bff14 --stop-address=0x7bff2c footballmanager.exe
objdump -D -Mintel --start-address=0x653510 --stop-address=0x65356b footballmanager.exe
objdump -D -Mintel --start-address=0x5d4800 --stop-address=0x5d485e footballmanager.exe
```

**Outstanding:** actual live TeamSelect->PSupportStart registration and authentic staff/user/CRT records, source-original text glyph placement/row composition, hit semantics for Apply/Cancel, complete close/result state, and interactive Windows11 output. No exact-head test run/PR/CI for this branch yet; keep Gate13–17 OPEN.
