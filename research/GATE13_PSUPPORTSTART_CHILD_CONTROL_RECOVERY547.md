# Recovery547: source child ownership for seven PSupportStart rows

Authenticated original executable `footballmanager.exe`, SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`;
static x86 disassembly only. This follows the previously verified
PSupportStart vtable layout `0x4C7B70` and seven repeated
`0x4C9510` row builders. No original executable run.

At `0x4C9340..0x4C94C7` each 0x4C-byte row control
contains five actual allocated child object pointers:

| Row owner offset | Source constructor or wrapper | Native registration ID |
| --- | --- | --- |
| `+0x38` | `0x64F300` then vft `0x7BE530` | `0x33` |
| `+0x3C` | `0x42DE80` then vft `0x7C66C8` | `0x31` |
| `+0x40` | `0x42DE80` then vft `0x7C66C8` | `0x31` |
| `+0x44` | `0x64F300` then vft `0x7BE530` | `0x15` |
| `+0x48` | `0x64F300`, `0x64F600`, vft `0x7BFF14` | `0x15` |

Every listed child is actually registered through native `0x5D4580`.
The two `+0x3C/+0x40` children are of the *same*
class; `+0x44` is a distinct input/render child.

The row setup `0x4C9510` creates bounds using original
`0x64F380` (already verified to be 326×37 at
x=391,y=181+40*i). It binds the original
`0x945950` animation source to **child+0x38** through
`0x652940` at `0x4C954F`; then it
configures **child+0x3C** at `0x4C95F3` and
**child+0x40** at `0x4C969A` through
`0x6528D0`, passing the source text renderer
`0x945910` as a source dependency. Both text
calls derive their x coordinate **row_x + 0x13**
and use per-row distinct source text arguments.
Those positions are native setup arguments only:
the exact glyph bounds, client text clipping,
parent transform and clickable input rectangle are
not qualified by this evidence.
- At `0x4C96BC`, source `0x651BA0` configures
  **child+0x44**, using `0x4C97D0` to select
  one of five native animation/asset wrappers
  by its control state integer 1–5.
- At `0x4C978A`, `0x652400` configures
  **child+0x48** with separate native text
  symbol `0x81ACB0`, source `0x87B6B0`,
  original `0x8CAB80` font/color-related
  dependencies and width argument `0x5F=95`
  among the pushed values. Without exact
  `0x652400` argument contract, the 95 must
  **not** be promoted to a verified hit width.

Important further original `0x4C97D0` evidence:
it subtracts one from input and accepts exactly
values 1–5 (unsigned bound check `cmp eax,4`),
then uses native jump table `0x4C9810` to
return one of five wrapper addresses:
`0x945890`, `0x945850`, `0x945810`,
`0x9457D0`, `0x945790`. Out-of-range
values return **null**, not the first or
last wrapper. This is source-proven, but the
physical resource identities of all five
wrappers, the row state producer, and the full
event routing remain unresolved. Do not
guess role labels or import assets from their
names.

New original source reproduction:

```bash
objdump -D -Mintel --start-address=0x4c9340 --stop-address=0x4c94da footballmanager.exe
objdump -D -Mintel --start-address=0x4c9510 --stop-address=0x4c9794 footballmanager.exe
objdump -D -Mintel --start-address=0x4c97d0 --stop-address=0x4c9824 footballmanager.exe
```

**Next:** source trace wrapper `0x945890..0x945790` provenance,
`0x6528D0` text argument placement, and
`0x651BA0`/`0x652400` physical hit/interaction
contracts, then implement the *complete* native screen
with actual seven row states, original cancel/apply and
TeamSelect modal return. Bounded source primitives
PRs 642–644 do not yet restore interactive UI;
original shared-CRT and PR638 remain blocked.
Original process observation: NO. Windows11 GUI
acceptance: NO. Gates13–17 remain OPEN.
