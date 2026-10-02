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


## Recovery 161 continuation: DIVISION and Sort By selectors

The remaining seven selector events are now source-closed through
`PLeagueTables::0x448C40`.

### Events 9..13: DIVISION

Global `0x982678` resolves through complete English-loader entry 2144 to
exact shipped text **DIVISION**. Its header control is object `+0x49C`,
set up at `0x4472C1`.

Five `fmRadioTextSm` controls begin at object `+0x4E4`. Their exact event
IDs are **9..13**. The event handler does not use a guessed division enum:
for non-country events it scans the five controls' event fields at
control `+0x20`; on a match it stores the selected index at object `+0x68`
and the corresponding source identity from object `+0xA0+4*index` at
object `+0x8C`.

Rebuild method `0x448E60`:
- clears/hides all five controls first;
- resolves the active country from the source country object table;
- iterates country competition entries from `country+0x48`, count
  `country+0x4C`;
- dynamically casts each `LeagueBase` entry (TD `0x818AA0`) toward
  **DummyLeague** (TD `0x81B498`) through `__RTDynamicCast 0x668995`;
- non-DummyLeague entries expose exact caption pointer `+0x14` to
  `fmRadioTextSm::0x5D3F10`;
- their source identity word at `+0x20` is retained in the panel's five-entry
  identity array at `+0xA0`;
- unused selector slots are cleared and disabled.

The initial selection is source-aware: if the current club's country matches
the selected country, the current competition identity is resolved and mapped
back to that country's competition index; invalid `0xFFFF` falls back to
index 0.

### Events 14/15: Sort By

Global `0x983A94` is English-loader entry 857 -> exact text **Sort By**.
Its header control is object `+0x660`, setup call `0x447472`.

The two `fmRadioTextSm` controls begin at `+0x6A8`:
- event **14**: global `0x983C04`, loader index 765 ->
  **League Position**, source state 0;
- event **15**: global `0x983A90`, loader index 858 ->
  **Current Form**, source state 1.

Object `+0x98` stores the binary sort mode and is explicitly initialized to
0 at `0x448BF0`, so **League Position is the source default**. Event 14 writes
0; event 15 writes 1. Both call `0x449090`, which applies the selected mode
to the seven table/display controls at `+0x7FC..+0x97C` via their source
virtual state methods.

This closes selector semantics for all 15 PLeagueTables events without
inventing row meanings.

### Updated boundary

Still open after this continuation:
1. concrete identity and visible-field binding of the table row/display
   controls at `+0x7BC..+0x9BC`;
2. exact row geometry and native row ordering/sort projection;
3. original League Tables graphic-resource ownership;
4. reconstructed presentation integration and corrected Windows validation.
