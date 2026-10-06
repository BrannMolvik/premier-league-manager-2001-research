# Gate 14: PPreMatchPanel source correlation

_7 October 2026. Evidence tier: confirmed first-hand canonical executable + authorized original-disc bytes._

## Scope and safety boundary

This note records the original pre-match Match Detail panel evidence needed for
Gate-14 presentation work-ahead while Gate 13 remains externally blocked on the
normal Windows 11 acceptance receipt.

It does **not** establish the management-screen action that launches a human
fixture. That transition remains fail-closed. It also does not invent a
replacement 3D match presentation.

Canonical executable:

- `footballmanager.exe`
- SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Canonical authorized source archive:

- 511,121,336-byte Library ZIP
- SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`

## Native modal and Match Detail contract

Previously recovered source evidence establishes:

- `PPreMatchPanel` constructor/entry at `0x499C30`;
- event handler `0x49AB50` dispatches event IDs 1..4;
- selector commit routine `0x49ABA0` writes the selected mode to
  `0x877530`, refreshes all four controls, signals the modal owner, and
  closes the panel;
- event 1 -> mode 3, event 2 -> mode 2, event 3 -> mode 1, event 4 -> mode 0;
- mode contract:
  - 0 = `3D Match`
  - 1 = `3D Highlights`
  - 2 = `FastView`
  - 3 = `Quick Match`.

## Four-choice selector geometry and asset binding

The four controls are contiguous 0x4C-byte objects at:

- `PPreMatchPanel+0x3740`
- `PPreMatchPanel+0x378C`
- `PPreMatchPanel+0x37D8`
- `PPreMatchPanel+0x3824`.

Setup code around `0x4996F4..0x499803` binds all four to global wrapper
`0x946350`. Static initializer `0x5F4A10` defines that wrapper as
**106 x 25** with resource type/index 15. Its underlying original path is
loaded at `0x5F4A50` from string VA `0x835C18`:

`FM2001_Art/Generic/GenericButtonsAndBars/button_type_15.444`

The constructor calls pass a common y-coordinate 107 and four x-coordinates.
Accounting for x86 thiscall argument order plus the event-to-mode mapping gives
the exact left-to-right selectable row:

| Mode | Label | Event ID | x | y | w | h |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 3D Match | 4 | 176 | 107 | 106 | 25 |
| 1 | 3D Highlights | 3 | 290 | 107 | 106 | 25 |
| 2 | FastView | 2 | 404 | 107 | 106 | 25 |
| 3 | Quick Match | 1 | 518 | 107 | 106 | 25 |

The corresponding language globals resolve consistently as:

- `0x981DD4` = `3D Match`
- `0x981DD0` = `3D Highlights`
- `0x981DCC` = `FastView`
- `0x981DC8` = `Quick Match`.

This closes the selector ordering and geometry without synthesizing a modern
layout.

## Dedicated original pre-match assets

The authorized Joliet filesystem contains the following exact resources under
`FM2001_Art/Generic/pre_match/`. Dimensions are the first two little-endian
16-bit values in the original EA444 header.

| Original path suffix | Bytes | Dimensions | SHA-256 |
| --- | ---: | ---: | --- |
| `pitch.444` | 32,268 | 261 x 374 | `23a776bf9445818ac5356d6c4fa8ca0595affdaf5980bbbe6cdf9df2030a82dd` |
| `playername_active_left.444` | 2,988 | 200 x 16 | `da3bc727a6980b267165dcf8c63b235e12b07cd6aa446b7875b1e19519652a00` |
| `playername_active_right.444` | 2,912 | 200 x 16 | `af809c7bb2961cc46b011fe8c7557b4eb23e97fffee6d99bd36178b48bd8b0d9` |
| `playername_disabled_left.444` | 2,604 | 200 x 16 | `59e1a1e1714b1e9dab0929112246b59c6dcd9344841aab764ef87a1850b564cd` |
| `playername_disabled_right.444` | 2,604 | 200 x 16 | `c9138b788561b7c47082755cdaa26a432ca8ce41ec3b7d6373ba63f9ef75c2df` |
| `prematch_bground.444` | 247,608 | 800 x 600 | `964d6765d7eedd7d064b3c439ed144c851ab102ec029e8fc198df0c9adb31576` |
| `rating_bar_left.444` | 3,156 | 171 x 16 | `3a7f14cee9067971c5267210bd235e457171aa9438b40be992a9009942fbc07c` |
| `rating_bar_right.444` | 3,784 | 171 x 16 | `579421a7677aedae39663fe5e14a48f3b44eb053546ffa472407f0b639ea3652` |
| `rating_bar_right2.444` | 3,188 | 171 x 16 | `dae7d2a3649c199fdc5e8829c6c0cf603c0186747c0ee8671d6e9061f7b9f7b3` |
| `top_bar.444` | 18,604 | 800 x 95 | `e3fb5f772784dd3608774aae44620e1ab932682b1f06d8153157d981ff869534` |

Executable loader strings and static wrapper initializers independently bind the
same resources and dimensions. Relevant wrapper/source pairs include:

- background wrapper `0x9420B0`, source `0x9420D0`, 800 x 600;
- pitch wrapper `0x941EB0`, source `0x941ED0`, 261 x 374;
- top-bar wrapper `0x941E70`, source `0x941E90`, 800 x 95;
- active-left wrapper `0x941F30`, source `0x941F50`, 200 x 16;
- active-right wrapper `0x941EF0`, source `0x941F10`, 200 x 16;
- disabled-left wrapper `0x942070`, source `0x942090`, 200 x 16;
- disabled-right wrapper `0x942030`, source `0x942050`, 200 x 16.

## Source-backed panel positions recovered so far

The native calls provide these exact placements:

- top bar: x=0, y=0, 800 x 95;
- pitch: x=269, y=152, 261 x 374;
- active left player-name strip: x=36, y=152, 200 x 16;
- active right player-name strip: x=563, y=152, 200 x 16;
- disabled left player-name strip: x=36, y=358, 200 x 16;
- disabled right player-name strip: x=563, y=358, 200 x 16.

Rating-bar wrappers are also referenced in the same panel family, including
coordinates around x=65/y=497 and x=564/y=497, but the exact behavioral
distinction among `rating_bar_left`, `rating_bar_right`, and
`rating_bar_right2` is not yet fully source-closed. Do not claim a final
simultaneous rating-bar layout until that call path is audited.

The 800 x 600 `prematch_bground.444` ownership is source-proven by the
dedicated loader/static wrapper, but its final draw invocation appears to pass
through shared panel/background machinery rather than a simple direct literal
reference. Do not invent a draw-site claim.

## Implementation boundary

The next implementation may safely introduce a source-backed pre-match
presentation model/render seam with:

- exact 800 x 600 panel coordinate space;
- exact four-choice row, labels, modes, and button dimensions;
- exact recovered top-bar/pitch/player-strip positions;
- original assets, once intentionally imported/provenance-tracked under
  `original_assets/`.

It must **not**:

- invent a management-screen button or fixture-launch action;
- expose native sentinel 5 as a selectable mode;
- route modes 0/1 to FastView as a substitute for missing 3D presentation;
- assume unresolved rating-bar behavior;
- claim that the pre-match background draw call itself is source-closed beyond
  its dedicated resource ownership.

## Exact next task

Inspect the existing EA444 import/derivative and production Tk presentation
paths. Import only the newly source-correlated pre-match resources required by
the first renderable seam, add deterministic provenance/tests, and bind the
source-backed selector row and recovered static panel geometry without adding
the still-unrecovered management-to-match launch transition.
