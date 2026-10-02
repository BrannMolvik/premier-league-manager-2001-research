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


## Recovery 162 table body, row projection and original graphics

Recovery 162 continues from the selector/header shell into the concrete table
body. All findings below were reread from canonical
`footballmanager.exe` SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
and the authorized raw-disc resources.

### Concrete list and row RTTI

The object at `PLeagueTables+0x9BC` is not another header control.

- class: **`CLeagueTableList`**
- TypeDescriptor: `0x81B478`
- Complete Object Locator: `0x7E1520`
- vtable: `0x7C011C`
- setup wrapper: `0x4477E0`
- generic list setup: `0x6510F0`
- row factory: `0x447820`

Its exact local rectangle is **`(270,184,477,384)`**. The setup supplies a
native capacity of **24 rows**, row step **16 pixels**, and an additional source
value **8** that remains neutral rather than being given an invented modern
meaning.

The row factory allocates `0x4A8` bytes and constructs:

- class: **`PLeagueTableRow`**
- TypeDescriptor: `0x81B378`
- Complete Object Locator: `0x7E1398`
- vtable: `0x7BFEC0`
- visible setup: `0x446930`

The factory stops when the requested source index reaches the source count at
the owning presentation object. In source sort state 0 it prepares ordering
through `0x4F4940`; the alternate state uses `0x4F4A10`. The prepared row
pointer comes from source array `+0x34`.

### Exact row child layout and visible projection

Each row owns 12 children. The source row pointer is retained at row `+0x70`;
its source rank/order value `+0x28` is copied to row `+0xC4`.

Visible local text rectangles:

| Visible field | row control | exact local rect |
| --- | ---: | --- |
| rank/order value | `+0x160` | `(23,1,21,12)` |
| source name string | `+0x1C0` | `(46,1,214,12)` |
| P | `+0x208` | `(262,1,27,12)` |
| W | `+0x268` | `(291,1,27,12)` |
| D | `+0x2C8` | `(320,1,27,12)` |
| L | `+0x328` | `(349,1,27,12)` |
| F | `+0x388` | `(378,1,27,12)` |
| A | `+0x3E8` | `(407,1,27,12)` |
| Pts | `+0x448` | `(436,1,27,12)` |

Adding list x=270 aligns the seven stat columns exactly under the recovered
header band at x=532, 561, 590, 619, 648, 677 and 706.

The source data projection is also exact:

- **P** <- source row `+0x10`
- **W** <- `+0x14`
- **D** <- `+0x18`
- **L** <- `+0x1C`
- **F** <- `+0x20`
- **A** <- `+0x24`
- **Pts** <- **`3 * (+0x14) + (+0x18)`**

The P/W/D/L/F/A/Pts names are not inferred from modern football conventions:
they are the original English header globals recovered in Recovery 161 and
their rectangles align one-for-one with these source fields.

### Exact original League Tables graphic family

The static loader range `0x5F7870..0x5F80C0` owns exactly 15
`FM2001_Art/Generic/league_tables/*.444` resources used by the table/header
presentation.

| Resource | exact size | bytes | raw / wrapper |
| --- | --- | ---: | --- |
| `champion_grid.444` | 477x14 | 8512 | `0x944F10 / 0x944EF0` |
| `promotion_grid.444` | 477x14 | 7096 | `0x944ED0 / 0x944EB0` |
| `relegation_grid.444` | 477x14 | 7288 | `0x944E90 / 0x944E70` |
| `standard_grid.444` | 477x14 | 7304 | `0x944E50 / 0x944E30` |
| `your_team_grid.444` | 477x14 | 8068 | `0x944E10 / 0x944DF0` |
| `playoff_grid.444` | 477x14 | 7068 | `0x944DD0 / 0x944DB0` |
| `champion_icon.444` | 20x12 | 688 | `0x944D90 / 0x944D70` |
| `promotion_icon.444` | 20x12 | 512 | `0x944D50 / 0x944D30` |
| `relegation_icon.444` | 20x12 | 644 | `0x944D10 / 0x944CF0` |
| `playoff_icon.444` | 20x12 | 552 | `0x944CD0 / 0x944CB0` |
| `your_champion_icon.444` | 20x12 | 576 | `0x944C90 / 0x944C70` |
| `your_promotion_icon.444` | 20x12 | 488 | `0x944C50 / 0x944C30` |
| `your_relegation_icon.444` | 20x12 | 492 | `0x944C10 / 0x944BF0` |
| `your_playoff_icon.444` | 20x12 | 552 | `0x944BD0 / 0x944BB0` |
| `league_bar.444` | 475x19 | 5552 | `0x944B90 / 0x944B70` |

Every file was freshly reread from the raw disc and its SHA-256 is persisted in
`LEAGUE_TABLES_RESOURCES`.

The row starts from `standard_grid`. Source position thresholds select
`champion_grid`, `promotion_grid`, `relegation_grid`, or `playoff_grid`;
a separately recovered source byte from helper `0x4037B0` selects the paired
normal versus `your_*` icon variant and can replace the grid with
`your_team_grid`. The backing source byte remains neutrally named until its
higher-level identity is independently proven.

The header band additionally binds `league_bar.444` at object `+0x788` with
exact local rectangle **`(270,152,475,19)`**.

### Boundary after Recovery 162

Closed here:

1. concrete League Tables body/list and row RTTI;
2. 24-row native capacity, 16-pixel row step and exact body rectangle;
3. exact rank/name/seven-stat row geometry;
4. exact source fields for P/W/D/L/F/A and original points arithmetic;
5. source position/current-form preparation boundary;
6. all 15 original League Tables graphics with fresh hash/size/geometry and
   raw/wrapper ownership;
7. source grid/icon selection family without inventing the remaining neutral
   helper-byte meaning.

Still open:

1. reconstructed League Tables presentation integration using this contract;
2. safe import/staging of the exact original table binaries where required;
3. corrected real-Windows/Tk graphical validation;
4. broader Gate-13 management/tactics presentation gaps after League Tables
   integration.
