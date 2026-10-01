# Gate 13: canonical Button@ease and Zurich render trace

_1 October 2026 KST. Direct analysis of the authorized canonical
`footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`._

## Source and calibration

The authorized 511,121,336-byte source ZIP independently matched SHA-256
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
The repository extractor materialized only `footballmanager.exe` to private
storage outside Git and the executable matched the canonical hash above.

The expanded RTTI inspector passed its fail-closed known-positive calibration:

- `PMain@TeamSelect` TypeDescriptor `0x81EC10`;
- `PMain@TeamSelect` vftable `0x7C7650`.

It then recovered one `Button@ease_2001` candidate, manually corroborated by
constructor vftable writes at `0x438808` and `0x480576`:

| Structure | Virtual address |
| --- | ---: |
| TypeDescriptor | `0x81AD90` |
| Complete Object Locator | `0x7E0B90` |
| Class Hierarchy Descriptor | `0x7E0B80` |
| vftable | `0x7BF4CC` |

The vftable has 44 consecutive code-valued slots. Raw reports and executable
disassembly remain in private storage outside the repository.

## Native 23-frame mapping

The shared constructor initializes flags at control `+0x18` to `0x183` and
the Button setup zeros current subframe `+0x48` and group `+0x4A`.

The exact selection path is:

```text
0x653040 group selector
  mask 0x2 clear -> group 2
  else mask 0x4 set -> group 1
  else -> group 0

0x5D62F0 group length
  group 0 -> 11
  group 1 -> 11
  group 2 -> 1

0x652860 source frame
  sum(lengths of earlier groups) + current subframe (+0x48)
```

Therefore the canonical PStartMenu `button_type_1.444` and TeamSelect
`choice_start_anim.444` atlases map identically:

| Native condition | Group | Source frames |
| --- | ---: | ---: |
| enabled, mask `0x4` clear | 0 | `0..10` |
| enabled, mask `0x4` set | 1 | `11..21` |
| disabled, mask `0x2` clear | 2 | `22` |

`0x652780` changes groups while preserving proportional subframe progress.
Update virtual `0x6527F0` calls the group selector every update. When mask
`0x8` is set it advances `+0x48` toward the last subframe; when clear it
retreats toward zero. Pointer handler `0x64FBE0` sets mask `0x8` while the
pointer is inside the control rectangle and clears it outside, proving the
directional hover animation behavior.

The user-facing meaning of mask `0x4` is not renamed to pressed/down/selected
without a final event-owner proof. Code and tests therefore use the neutral
term **alternate group**. Mouse input methods at `0x64F7A0` and `0x64F860`
toggle capture mask `0x10`; that mask is not the group selector.

## Frame draw and Zurich captions

Button draw `0x6520C0` calls atlas helper `0x651C90`, which obtains the native
source-frame index through vtable slot 38 (`0x652860`). Caption setup
`0x651E30` stores label, font, style, offsets and two 16-bit colors. Both
first-screen call families pass:

- style `0x2000`;
- x/y offsets `0,0`;
- normal native color value `0xFFFF`;
- group-1 native color value `0x0000`.

Color selector `0x653020` returns `0x0000` only while active group `+0x4A`
is 1 and `0xFFFF` otherwise. These are retained as original 16-bit render
values; no unsupported modern color conversion is claimed.

`0x6574D0` defines line height as the space glyph height plus twice its
`draw_y`. For the exact Zurich 20-pixel font this is `15 + 2*3 = 21`.
`0x6574E0` measures glyph widths with signed pair adjustments. Style `0x2000`
centers the measured line horizontally and the 21-pixel line vertically in
the control, while `0x657280` applies each glyph's `draw_y` and the clipped
control rectangle.

The resulting PStartMenu line origins are:

| Caption | Text width | Control | Line origin |
| --- | ---: | --- | --- |
| Continue | 63 | `(181,478,169,25)` | `(234,480)` |
| Start New Game | 117 | `(7,478,169,25)` | `(33,480)` |
| Load Game | 81 | `(355,478,169,25)` | `(399,480)` |
| Quit to Windows | 120 | `(181,508,169,25)` | `(205,510)` |

The same arithmetic gives TeamSelect Back `(282,306)` and Start `(484,306)`
inside their 150x32 controls. Their caption/source-string integration remains
separate from the now-implemented PStartMenu caption model.

## Strict original-source audit and import

The exact ten-path extraction, selection check and firsthand source audit all
passed against the canonical ZIP/executable. Both decoded background digests,
all Zurich caption-mask digests and both 23-frame action atlases matched the
existing independent regressions. The ten pinned resources were then imported
one at a time through `gate13_asset_import.py`. The post-import readiness guard
and repository asset-policy guard both pass.

No ZIP, executable, disc image, raw disassembly report or uncontrolled dump is
tracked. The implementation adds only the recovered state model, caption
geometry/native values, tests, concise evidence and the deliberately selected
provenance-tracked resources.

## Verification and remaining boundary

Focused synthetic tests pass. Opt-in tests also pass against the exact private
executable, atlases, Zurich font and English STR/IDX bytes. Gate 13 remains
active: mask-4's user-facing event name, TeamSelect hierarchy item mapping,
the broader manager-screen resource/layout/navigation correlation and a real
Windows graphical audit are still open. This trace does not promote Gate 13
or authorize Gate 14 by itself.
