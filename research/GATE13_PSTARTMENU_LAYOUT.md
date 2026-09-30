# Gate 13: exact original PStartMenu controls and language binding

_Date: 30 September 2026. Evidence tier: confirmed canonical executable plus
original English STR/IDX resources._

## Scope

This note closes the primary action-control mapping for the original
PStartMenu. Coordinates and labels below are recovered from the canonical
`footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
not estimated from screenshots.

## Button source and frame geometry

The shared PStartMenu button handle at runtime global `0x946590` is built at
`0x5F4500` from the resource object loaded immediately beforehand from:

`FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444`

The original file is 45,116 bytes and its EA444 header is **169 × 575**.
The initializer passes width `0xA9 = 169` and height `0x19 = 25`, proving
the visible button frame is **169 × 25**. The source atlas therefore contains
23 vertical 25-pixel rows.

## PStartMenu primary actions

Screen-specific setup `0x4C1BA0` creates four ordinary
`Button@ease_2001` controls through `0x652FD0`. The final two arguments are
x then y, as independently established for the TeamSelect controls.

| Event | Executable label global | English.idx position | Exact original label | Rectangle (x,y,w,h) | Dispatch |
| ---: | --- | ---: | --- | --- | --- |
| 1 | `0x9847F8` | 0 | Continue | `181,478,169,25` | `0x4C37B6` continue path |
| 2 | `0x9847F4` | 1 | Start New Game | `7,478,169,25` | `0x4C37C7` New Game / TeamSelect path |
| 3 | `0x9847F0` | 2 | Load Game | `355,478,169,25` | `0x4C3A59` load-game UI path |
| 4 | `0x9847E0` | 6 | Quit to Windows | `181,508,169,25` | `0x4C3CDF` confirmation/shutdown path |

This explains the original visual arrangement: three 169-pixel buttons on the
first row and the quit control centered beneath them.

## Direct language proof

Language loader `0x635F30` opens the selected language IDX, repeatedly reads
one entry through `0x667E90`, and installs entries sequentially:

- first -> `0x9847F8`
- second -> `0x9847F4`
- third -> `0x9847F0`
- fourth -> `0x9847EC`
- fifth -> `0x9847E8`
- sixth -> `0x9847E4`
- seventh -> `0x9847E0`

For English, the caller selects original `English.idx`.
`research/GATE13_LANGUAGE_RESOURCES.md` independently proves IDX positions
0,1,2,6 resolve to **Continue**, **Start New Game**, **Load Game**, and
**Quit to Windows** respectively. Therefore the action-label association is
now executable-bound rather than inferred from ordering or screenshots.

## Events 5–7

The same PStartMenu setup also creates three embedded controls at object offsets
`+0x1D8`, `+0x230`, and `+0x288`, events 5–7, through a different helper
(`0x4C59D0`). All three dispatch to `0x4C3D43`. They are not the four
primary text-button actions above and must not be relabelled speculatively.
Their exact visual/behavioral semantics remain a separate trace if needed by
the mature screen.

## Reconstruction consequence

`reconstruction/original_front_end_layout.py` now records the source atlas,
frame dimensions, exact rectangles, event IDs and language IDX positions.
`front_end_state.py` exposes all four recovered PStartMenu actions while
leaving actual continue/load/quit application side effects outside the
presentation-state module.

The next presentation step is to decode/select the correct frame states from
`button_type_1.444`, use the original language resource for the four labels,
and compose/click-test the authentic PStartMenu before continuing deeper into
TeamSelect.
