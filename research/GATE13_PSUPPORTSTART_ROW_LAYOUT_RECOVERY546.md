# Recovery546: exact original PSupportStart seven-row layout anchors

## Identity and source

Private owner-provided `footballmanager.exe` 4,714,541 bytes verified SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Static x86 disassembly only; **original executable was not run**.
Previously verified source PSupportStart RTTI `.?AVPSupportStart@@`,
vft at `0x7C6DDC`, and vft +0x04 pointer `0x4C7B70` identify
the owner of the actual original layout method. The layout method is
**`0x4C7B70`**, not an unrelated support routine. In it, seven
native child objects stored at offsets starting `+0x2224` with
0x4C stride are registered by group indices 8–14 and configured
through seven **direct calls to `0x4C9510`**:

| Index | Call address | Original first arg x | Second arg y | Group index |
| --- | --- | ---: | ---: | ---: |
| 0 | `0x4C8060` | 391 | 181 | 8 |
| 1 | `0x4C80B5` | 391 | 221 | 9 |
| 2 | `0x4C810A` | 391 | 261 | 10 |
| 3 | `0x4C815F` | 391 | 301 | 11 |
| 4 | `0x4C81B4` | 391 | 341 | 12 |
| 5 | `0x4C8209` | 391 | 381 | 13 |
| 6 | `0x4C825E` | 391 | 421 | 14 |

The callee `0x4C9510` reads its first and second argument into
EBX/EDI and passes them as source x/y (plus a source image extent
computed from original resource runtime values) into `0x64F380`
at `0x4C9539`. Native `0x64F380` stores x in child
`+0x08`, y in `+0x0C`, and computes right/bottom in
`+0x10/+0x14`. These **seven positions are true original
client-coordinate anchor arguments**, not estimates.

Source text buffers per row are
`PSupportStart+0x70+0x80*i` (first) and
`+0x4F0+0x80*i` (second), as separately evidenced by
`0x4C804B/+0x8051`, `0x4C8097/+0x80A0`,
through `0x4C8240/+0x8249`, plus original
`0x4D06D6` row-advance `0x80`.
The registered selector object is at
`+0x2224+0x4C*i`. The PSupportStart
factory `0x450C74..0x450C86` gives window
width760, height500. Source text editor control
`0x4C7E28..0x4C7E50` consumes first-name
buffer `PSupportStart+0x97C` with numeric
coordinate arguments `0x84=132`, `0xB1=177`;
`0x4C7EC1..0x4C7EE9` similarly consumes
surname buffer `+0x980` with `x=132, y=199`
through separate `0x5D5DC0` call. Since
`0x5D5DC0` is not the `0x64F380`
rectangle constructor, those two **numeric text
origin arguments** are not yet promoted to
source-accepted clickable input hit rectangles.

## Implementation and boundaries

The scoped source-data `reconstruction/original_supportstart_layout.py`
captures these seven original row anchors, selector owner offsets,
text-buffer owner offsets, native group indices and 760x500 native
window dimensions. A test in
`reconstruction/test_original_teamselect_native.py`
independently checks the exact address-derived values
and ensures no guessed clickable rectangle or staff
label has been added. This is a **presentation geometry
source primitive**, not the original GUI or
staff application transaction.

Still unresolved and P0: source `0x4C9510`
resource extent from pointers `0x945924/0x945928`,
actual bounding rectangles and control hierarchy;
five child controls registered per selector
`0x33, 0x31, 0x31, 0x15, 0x15`, row style assets;
source event 1 Cancel vs event 2 Apply
labels and hit owner; seven live staff
selection flags, three selected-user linked
lists, original closed modal/TeamSelect
continuation, fresh shared CRT RNG startup
and original source-save fidelity. Do not
import graphical binaries or add an
approximate interactive form before these
boundaries close.

**Source-level**: row anchors exact.
**Port integration**: bounded data/layout only.
**Original runtime observed**: NO.
**Windows11 GUI accepted**: NO.
**Gate13–17**: OPEN. PR638 remains
DRAFT/BLOCKED from shared CRT mismatch.

## Reproduction

```bash
sha256sum footballmanager.exe
objdump -s --start-address=0x7c6ddc --stop-address=0x7c6e2c footballmanager.exe
objdump -D -Mintel --start-address=0x4c7b70 --stop-address=0x4c7c12 footballmanager.exe
objdump -D -Mintel --start-address=0x4c8014 --stop-address=0x4c8264 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9510 --stop-address=0x4c953f footballmanager.exe
objdump -D -Mintel --start-address=0x64f380 --stop-address=0x64f3be footballmanager.exe
objdump -D -Mintel --start-address=0x4c7e28 --stop-address=0x4c7e52 footballmanager.exe
objdump -D -Mintel --start-address=0x4c7ec1 --stop-address=0x4c7eeb footballmanager.exe
```


## Follow-up: complete source width/height and actual original user_entry art (Recovery546)

The original row width and height are now **source-qualified**, correcting
the provisional unknown width/height in the first section of this report.
The same original `0x4C9510` call reads the **native** width from
`[0x945924]` and height from `[0x945928]`, adds
`0x14=20` to each, and passes these as width/height along with the
two earlier source x/y args into `0x64F380` at `0x4C9539`.

The original `0x5F6180` directly loads
`FM2001_Art/Generic/user_entry/text_bars.444` into
sprite input `0x945930`. Its native frame wrapper
`0x5F61D0` invokes `0x64E500` with exact cropped
sprite width `0x132=306` and height `0x11=17`,
writing those to widget `0x945910+0x14/+0x18`
at `0x64E58F/0x64E592`. Thus the layout child
rectangle is `(x, y, width, height) =
(391, 181+40i, 306+20, 17+20)`
= **(391, 181+40i, 326, 37)**, for seven rows.
Original `0x64F380` stores left/top and
computes right/bottom from dimensions.

The original `0x5F60F0` loads
`Generic/GenericButtonsAndBars/user_entry_anim.444`
into sprite `0x945970` and `0x5F6140`
wraps its selected source slice into `0x945950`.
Native `0x4C9510` passes this wrapper to
`0x652940` at `0x4C954F`.
The original `0x5F6220` loads
`Generic/user_entry/background.444` through
resource `0x9458F0`, wrapped by
`0x5F6270` into `0x9458D0`
with original width760 and height500.
This completes asset *identity, native crop frame,
layout child dimensions* but not the final composition
and click semantics for every control.

Connected private original-source Google Drive produced exact
original bytes, independently checked:

| Original user_entry source file | File bytes | EA444 dimensions | SHA-256 |
| --- | ---: | --- | --- |
| `FM2001_Art/Generic/user_entry/background.444` | 176,016 | 760×500 | `a7536fe303e6a340bf6f30a345ce77b7f396b91c8330957e6fd7a30915a3f6c4` |
| `FM2001_Art/Generic/user_entry/text_bars.444` | 11,124 | 306×68 (source atlas, cropped frame 306×17) | `8c569018962a7084c33e5f4fda5d67e63f384d2e18d778281a7ad5aba2cba723` |
| `FM2001_Art/Generic/GenericButtonsAndBars/user_entry_anim.444` | 19,720 | 17×851 | `7eb9df5610dade0d32cde3051e457216be1fb5062dcc66209012ca969203d1bc` |

The existing five `FM2001_Art/Support/` images
are also authentic but do **not** replace these
three original Generic user-entry resources.
Private direct source file Drive IDs:
`1riZydXCbNfew617npZpkGCHqb4AfYWpz`,
`13sDm0KfnIqjS3iQyIdc4IvuoEL_7rhvg`,
`1jZFq_uFfxF4CAzJ7H_GfOSNlyPaDac3C`.
No proprietary original bytes copied to Git.

**Important bounded distinction:** `0x64F380`
creates a native child bounding rectangle (326×37).
This does **not** by itself prove every pixel is visible,
the clickable region is the full rect, hover/pressed frame
counts, on-screen caption positioning or the original
owner's modal close/cancel/commit GUI acceptance.
Those remain OPEN.

Source reproduction:
```bash
objdump -D -Mintel --start-address=0x4c9510 --stop-address=0x4c953f footballmanager.exe
objdump -D -Mintel --start-address=0x5f60f0 --stop-address=0x5f6200 footballmanager.exe
objdump -D -Mintel --start-address=0x5f6220 --stop-address=0x5f6299 footballmanager.exe
objdump -D -Mintel --start-address=0x64e560 --stop-address=0x64e5a7 footballmanager.exe
objdump -D -Mintel --start-address=0x64f380 --stop-address=0x64f3be footballmanager.exe
```


## Original action 1/2 button owner mapping — verified direct original virtual UI route

The original PSupportStart vtable+0x04 layout routine `0x4C7B70`
also creates two distinct child controls, **not just staff rows**.

- Native `0x4C7CC3..0x4C7CF3` registers
  `PSupportStart+0x1EB8` as **original child event 1**
  (`push 1` at `0x4C7CCD`) and calls
  `0x5D3900` with sprite wrapper `0x946190`.
- Native `0x4C7CF8..0x4C7D2A` registers
  `PSupportStart+0x1F08` as **original child event 2**
  (`push 2` at `0x4C7D02`) and calls
  `0x5D3900` with wrapper `0x946150`.
- Native PSupportStart VFT +0x10 `0x4D05E0`
  dispatches source event 1 into `0x4D061F`,
  setting original result byte `+0x1DE4=0`
  **without committing support staff/names**;
  event 2 enters `0x4D0606`, invokes
  original virtual+0x4C `0x4D0830`
  (full support staff/name transaction), then writes
  original result `+0x1DE4=1`.
- The immediate control→native event→result byte
  relation is source-verified and is captured as
  immutable original `SourceSupportStartActionChild`
  entries, with no invented clickable rectangle.
  The precise source animation-path resource mapping,
  button displayed labels, hit rect, and closing
  parent-navigation consequences **remain UNKNOWN**.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x4c7cc3 --stop-address=0x4c7d2e footballmanager.exe
objdump -D -Mintel --start-address=0x4d05e0 --stop-address=0x4d0631 footballmanager.exe
```
Original executable static disassembly only.
No Windows GUI/playtest acceptance; Gates 13–17 OPEN.
