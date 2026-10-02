# Gate 13 League Tables source shell

Recovery 161 starts source-faithful presentation recovery for the already
RTTI-proven `PLeagueTables` panel.

Canonical executable SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

## Concrete panel boundary

- class: `PLeagueTables`
- TypeDescriptor: `0x81B458`
- vtable: `0x7C00C8`
- constructor: `0x448640`
- main setup: `0x446F00`
- event dispatch: `0x448C40`

The shared selector constructor/setup pair is the already-known
`fmRadioTextSm@fm2001_ctrls` family at `0x5D4B50 / 0x5D4C70`, with
0x4C-byte control stride.

## Eight-country selector family

The constructor writes eight literal country identities at object
`+0x1D4..+0x1F0`, while setup binds eight controls beginning at `+0x23C`.
Events 1..8 map directly to active-country index 0..7 stored at `+0x64`.

| Event | Index | Country ID | Source country | setup call |
| ---: | ---: | ---: | --- | ---: |
| 1 | 0 | 26 | England | `0x446FE5` |
| 2 | 1 | 33 | Germany | `0x447044` |
| 3 | 2 | 40 | Italy | `0x4470A5` |
| 4 | 3 | 73 | Spain | `0x447103` |
| 5 | 4 | 66 | Scotland | `0x447164` |
| 6 | 5 | 31 | France | `0x4471C4` |
| 7 | 6 | 24 | Holland | `0x447227` |
| 8 | 7 | 9 | Belgium | `0x44728F` |

The order matches the source literal array, not an alphabetical
reconstruction.

The caption control at object `+0x1F4` is set through `0x5D6090` at
`0x446F92`. Its bounded setup arguments include x=27 and width=150, and
global `0x982670` resolves through English loader entry 2146 to exact shipped
text **Country**.

## Remaining selector families kept neutral

The same constructor creates:
- five `fmRadioTextSm` controls at object `+0x4E4`, setup calls
  `0x447306, 0x447353, 0x4473A1, 0x4473F2, 0x447440`;
- two controls at object `+0x6A8`, setup calls
  `0x4474B5, 0x447501`.

Their higher-level meanings are not assigned by this checkpoint. They remain
source-bounded structural families until their data producers and event cases
are traced.

## Table header band

Eight text controls are initialized with shared text helper `0x6503F0`.
The first is a wider unlabeled source slot; the next seven use exact original
English strings from the complete loader.

| Text | Global | English loader index | call | exact rect (x,y,w,h) |
| --- | ---: | ---: | ---: | --- |
| neutral/blank | — | — | `0x447594` | `(316,152,214,19)` |
| P | `0x9830F4` | 1473 | `0x4475D7` | `(532,152,27,19)` |
| W | `0x9830F0` | 1474 | `0x44761A` | `(561,152,27,19)` |
| D | `0x9830EC` | 1475 | `0x44765D` | `(590,152,27,19)` |
| L | `0x9830E8` | 1476 | `0x4476A0` | `(619,152,27,19)` |
| F | `0x9830E4` | 1477 | `0x4476E3` | `(648,152,27,19)` |
| A | `0x9830E0` | 1478 | `0x447726` | `(677,152,27,19)` |
| Pts | `0x9830DC` | 1479 | `0x447769` | `(706,152,27,19)` |

These are source-local panel coordinates from the setup helper arguments.

## Boundary after Recovery 161 checkpoint

Closed here:
- concrete League Tables setup/event boundary;
- exact eight-country source order and events;
- active-country field;
- Country caption;
- exact P/W/D/L/F/A/Pts header strings and rectangles;
- structural existence/offsets of the five- and two-control selector families.

Still open:
1. producer/event semantics for the five-control and two-control families;
2. row object identity, row fields and exact row geometry;
3. source graphic-resource ownership for League Tables;
4. sorting/paging/navigation beyond the bounded country events;
5. reconstructed presentation integration and corrected Windows validation.
