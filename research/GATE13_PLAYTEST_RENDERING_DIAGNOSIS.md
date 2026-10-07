# Local packaged play-test: Squad names and menu owner coordinates

7 October 2026, integration branch only; main is not merged or modified.

## Reproduced defects

The frozen `fe5543ff` build reaches Southport management without an exception,
but draws role/numeric columns over the original background with no player
names. This is not successful normal-play acceptance. The presenter discards
every unselected name because reserve flags are missing, even though the
source name and font are available. The main-menu action group is also offset
left/up because its owner-local rectangles were used as screen coordinates.

## Source-qualified repairs

Canonical executable SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Bounded disassembly and diagnostic logs remain outside Git in the private
`work/southport-render-trace*.txt` receipts.

- `DBTPlayers::0x416FC0` constructs its array through `0x4234D0`.
  That constructor sets EDI=0 and explicitly writes it to player `+0x174`
  at `0x423528`, before installing DBRPlayer vtable `0x7BDEDC` and calling
  `0x4178D0`. This is a literal field initialization, not inferred allocation
  contents. `0x417EA0/0x417EC0` test current-club identity and bits 0/1 of
  that independent word. The runtime now retains those booleans, carries them
  through the management bridge, and persists them in unused bits 12/13 of
  the existing internal player flags word. The record shape/schema is unchanged;
  older port saves did not implement reserve selection and restore cleared bits.
  The existing color helper keeps its native predicate precedence and still
  fails closed when a bounded adapter genuinely supplies unknown reserve state.
  This does not implement untraced reserve-selection interaction/lifecycles.
- `0x5312A8 -> 0x653320` registers PStartMenu at `(134,34,532,532)`.
  Its four controls register PStartMenu as their owner and receive local
  `(181,478)`, `(7,478)`, `(355,478)`, `(181,508)` origins through `0x652FD0`.
  Shared owner draw `0x6533A0` adds owner `+0x0C/+0x10`; pointer dispatcher
  `0x653480` subtracts those origins before child hit testing. Live art, captions,
  clipping, hover and pointer candidates must therefore use screen origins
  `(315,512)`, `(141,512)`, `(489,512)`, `(315,542)` respectively.
  Derivative caption metadata stays owner-local and its verified manifest is
  unchanged. No settings button or aesthetic substitute is introduced.

## Outstanding external acceptance

These targeted changes are not a claim that the full Squad surface is complete.
The reproduced screen also lacks additional management/roster presentation;
existing fail-closed rendering boundaries must be completed from original
evidence before calling the whole build playable or closing Gate 13.

Daniel additionally reports the longer Premier League intro as cropped/off-center.
The bounded DPI-aware EA check measures the expected centered physical child
rectangle `(512,144)-(2048,1296)` on a 2560x1440 desktop at 150% DPI, with
WPF content 1024x768 DIPs and device transform 1.5. That validates the EA
geometry only; it does not dismiss the Premier League clip report or establish
its visual acceptance. No speculative media conversion/placement change is made.
