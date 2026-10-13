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
