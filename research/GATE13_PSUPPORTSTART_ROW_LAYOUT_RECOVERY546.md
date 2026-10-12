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
