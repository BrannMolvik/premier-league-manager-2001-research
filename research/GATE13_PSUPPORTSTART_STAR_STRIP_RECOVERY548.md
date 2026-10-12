# Recovery548: source-verified PSupportStart cumulative staff stars

**Original source, not GUI acceptance.** Verified exact original private `footballmanager.exe` (4,714,541 bytes, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`) and original private extracted `FM2001_Art/Support/stars.444` (2,776 bytes; SHA-256 `16c619e305ebad013e7404ea9e5d4414a9f9a8bd0d6ad26f269ee82a49849633`). Neither original file is committed to Git.

**New original owner trace:**

1. PSupportStart's seven-row update at `0x4D06B0` for a non-null staff pointer invokes staff virtual+0x24, multiplies the result by original `1000.0` at `0x7C6828`, then separately invokes staff virtual+0x40, passing its integer return value to row refresh `0x4C9830`. The former is used in another row field; do not conflate these two values.
2. `0x4C9830` at `0x4C9861–0x4C9873` resolves the rating-like integer with `0x4C97D0` and writes the selected source wrapper into row child+0x44 at child+0x2C. The non-null path recomputes the child right boundary from source wrapper field+0x14; NULL uses a separate no-image path.
3. `0x4C97D0` maps 1..5 to `0x945890`, `0x945850`, `0x945810`, `0x9457D0`, `0x945790` respectively; unsigned out-of-range returns NULL.
4. Disassembly of initializer routines `0x5F6310`, `0x5F63A0`, `0x5F6430`, `0x5F64C0`, `0x5F6550` shows all five wrappers use the **same** original Support/stars.444 source loaded through `0x64D750` and filename literal `0x836414`. The `0x64E500` source rectangle fields are `left=0, top=0, right=15/30/45/60/75, bottom=10`. Original sprite dimensions 75x10. These are cumulative fills, not five different staff-role icons or x-shifted fragments.

| Native integer | Wrapper VA | Original image crop (left,top,right,bottom) |
|---|---|---|
| 1 | `0x945890` | `(0,0,15,10)` |
| 2 | `0x945850` | `(0,0,30,10)` |
| 3 | `0x945810` | `(0,0,45,10)` |
| 4 | `0x9457D0` | `(0,0,60,10)` |
| 5 | `0x945790` | `(0,0,75,10)` |
| other | NULL | none |

**Proof reproduction (private original bytes must remain outside Git):**
```bash
sha256sum footballmanager.exe stars.444
objdump -D -Mintel --start-address=0x4d06b0 --stop-address=0x4d0786 footballmanager.exe
objdump -D -Mintel --start-address=0x4c9830 --stop-address=0x4c98a8 footballmanager.exe
objdump -D -Mintel --start-address=0x4c97d0 --stop-address=0x4c9824 footballmanager.exe
objdump -D -Mintel --start-address=0x5f6300 --stop-address=0x5f6580 footballmanager.exe
objdump -D -Mintel --start-address=0x64e500 --stop-address=0x64e5a5 footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_stars
```

**Scoped code:** `reconstruction/original_supportstart_stars.py` and dedicated `test_original_supportstart_stars.py` preserve the exact original rectangle and NULL result; rejecting non-integer Python inputs is an explicit port guard, not a claim about native input validation.

**Unresolved:** original fourth-child parent transform and hit/hover behavior, fifth-child text/control, source staff role-label derivation, seven-row edit/Apply/Cancel, actual TeamSelect close/return, Inbox shared CRT, R1 all match modes, multi-human/all leagues, and real Win11 acceptance. The complete player-visible PSupportStart remains missing. No PR/CI is opened for this minor source fragment. Resume this feature branch and trace `0x651BA0`, `0x652400`, `0x4C9830` source interaction semantics, then group a genuinely reviewable complete editor integration. Existing PR645 is draft and touches the separate layout module; do not overwrite it.

## Further source-verified native star child layout (Recovery548)

At `0x4C969F–0x4C96BC`, the source row routine increments its incoming
row x by `0xE6=230`, its row y by `4`, then passes x/y/sprite/0
to `0x651BA0`. The original call to `0x651BA0`
uses source wrapper `+0x14/+0x18` as image width/height,
or width=height=0 for NULL, and forwards x/y/width/height to
`0x64F380`. The original `0x64F380` stores x, y and right/bottom
boundaries using `x+width`, `y+height`.
Thus with native row origins `(391,181+40*i)`:

- **native child local x** = 391+230 = **621**
- **native child local y** = 181+40*i+4 = **185+40*i**, for i=0..6
- native sprite rectangle = `(621,185+40*i,15*grade,10)` for grade1..5
- NULL/out-of-range state has geometry `(621,185+40*i,0,0)`.

These are original **native layout child bounds**, not independently
observed screen-space coordinates and **not** native mouse hit rectangles.
The source-backed `original_supportstart_star_local_rect()` and added
test encode this precisely without claiming GUI acceptance. Original
`0x651BA0` also stores sprite pointer into child+0x2C and
zeroes child+0x30. Exact visible draw ordering/parent transforms and
hit behavior remain unresolved.


## Seven-row selection-state propagation, separate from the stars

Further native disassembly clarifies the original selected-state control
hierarchy without assuming mouse-hit behavior:

- Original row constructor `0x4C9340` sets row vtable
  `0x7C6780`. Its virtual offset `+0x98`
  points exactly to `0x5D6200` (pointer at `0x7C6818`).
- Original `0x4D06B0` at `0x4D078A–0x4D07A0` reads
  source selected-byte array `PSupportStart+0x974`, index0..6,
  computes `selected_byte == 0`, and calls row vft+0x98.
  This is original **row refresh / selection-state initialization**,
  not proof of a physical click or state mutation.
- `0x5D6200` walks registered row children (count at row+0x34,
  pair entries at row+0x2C, per-child registration flag byte+4).
  It changes control bit `0x8000` only for children
  whose registration flag has bit `0x20` set.
  It calls original `0x64F710` (OR bit) for true,
  `0x64F750` (clear bit) for false; it also
  changes the same flag on the parent row object.
- `0x4C9340` registers five children with exact flags
  `0x33,0x31,0x31,0x15,0x15`. Therefore this selected-state
  propagation applies to first three children
  `+0x38,+0x3C,+0x40` (bit `0x20` set), but *not*
  star sprite `+0x44` or fifth child `+0x48`.
  This independently differentiates the cumulative star
  display from the row's selectable/control region.
- Original `0x652F80` reads bit15 of object+0x18.
  In the existing original `0x4D0830` Apply trace,
  that bit is inverted for selected staff record+0x28.
  The native read/set/commit relation is supported;
  user input hit routing and complete transaction are still unknown.

Reproduce with source x86:
```bash
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94d0 footballmanager.exe
objdump -D -Mintel --start-address=0x4d0788 --stop-address=0x4d07a8 footballmanager.exe
objdump -D -Mintel --start-address=0x5d6200 --stop-address=0x5d6268 footballmanager.exe
objdump -D -Mintel --start-address=0x64f710 --stop-address=0x64f795 footballmanager.exe
objdump -D -Mintel --start-address=0x652f80 --stop-address=0x652f89 footballmanager.exe
```

**Next source objective:** establish which of `+0x38,+0x3C,+0x40`
actually receives pointer/keyboard events and the exact parent row event
dispatch, rather than conflating the passive stars or text rendering
with source-verified click behavior. Preserve all seven original slots.
