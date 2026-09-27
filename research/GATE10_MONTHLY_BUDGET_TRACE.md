# Gate 10 Monthly Budget Producer Trace

Checkpoint: 27 September 2026

## Verified narrowing

- After `0x429CB0` appends a new `CMonthHistory`, the continuation around
  `0x429FAF` only fills additional monthly-history fields.
- It uses Balance aggregate pairs `0x5DD2E0` / `0x5DD3C0` when history exists
  and `0x5DD4A0` / `0x5DD500` for the initial path.
- Direct DBRUser `+0x6DC` references classify as construction/destruction,
  save/load, UI binding, or the monthly producer. No direct chairman-budget
  consumer of the rolling history list was found.

## EAMbcmonthlybudget construction

- Event ID: `0xA1`.
- Generic EAM factory: `0x538DE0`.
- Jump-table entry: `0x540484` -> branch `0x53B593`.
- The branch allocates the 0x5C-byte event with factory tag `0xA4` and calls
  constructor `0x541B20`.
- The constructor has no separate direct gameplay caller.
- Direct callers `0x5CE588` and `0x5CF8A7` of the generic factory are
  event-list deserialization/load paths, not gameplay producers.

Immediate `0xA1` constants around `0x4B480F/0x4B4849` and `0x4D2F4E` are UI
setup. The `0x41F18E` comparison against 0xA1 is an unrelated numeric
player/contract range threshold.

## Event behavior

- `EAMbcmonthlybudget` vtable is `0x7D01A4`.
- Its gameplay-handler slot `+0x3C` is generic `0x4093E0`, so the event does
  not itself mutate finance state.
- Vtable `+0x40` method `0x470CE0` is a one-year date-validity check, not a
  budget-population routine.
- DBRUser event-queue maintenance around `0x42B980..0x42BC1A` filters and
  dispatches other event IDs and is not the 0xA1 producer.

## Next trace

The strongest remaining path is generic event/template/rule population:
identify the machinery that creates or clones Business Consultant / board
events and follow the source values written to `EAMbcmonthlybudget` fields
`+0x3C..+0x54`.


## Global enqueue classification

The common EAM queue insertion path is now identified as:

- a 12-byte `MPMEAMail` wrapper (vtable `0x7BD564`);
- dated from the current calendar;
- enqueued into global queue `0x947AA8` through `0x613EC0`.

A complete vtable/RTTI classification of direct `0x613EC0` producer sites was
run across the executable. In the finance/business range, direct payloads
resolve to season tickets, funding requests, financial objectives, stadium
messages, loans/transfers and similar already-mapped event families.

Extending the same classification to all direct enqueue sites found **no**
directly constructed payload whose RTTI is `EAMchairbudgetsettings`,
`EAMchairbudgetwarning`, `EAMbcmonthlyincome`,
`EAMbcstartseasonmail`, or `EAMbcmonthlybudget`.

This is positive evidence that the chairman/Business Consultant budget family
does not enter the mail queue through the ordinary pattern of local typed-event
construction followed by `MPMEAMail -> 0x613EC0`. The remaining producer is
therefore very likely a generic/generated/template path that supplies an event
pointer without a nearby class-vtable write.

Next target: trace the named `ModFmt::BusinessConsultant` runtime class and
generic generated-event machinery rather than scanning additional direct
enqueue sites.


## EnglishEAM localization files recovered from the authorized disc

The executable references installed files `englisheam.idx` and
`englisheam.str`. The installation manifests identify those names and their
exact sizes. The authorized disc contains loose files with the same sizes:

- `ENGLIS2.IDX`: 5,754 bytes;
- `ENGLIS2.STR`: 298,747 bytes.

Therefore `ENGLIS2.IDX/.STR` are the shipped disc aliases for the installed
EnglishEAM localization pair.

### ENGLIS2.STR format

The string file decodes as:

- dword +0x00: text-block byte length = 292,303;
- dword +0x04: string count = 1,609;
- text block begins at +0x08;
- trailing table contains 1,609 little-endian dword offsets.

The early string range includes the chairman quarterly-budget phrase family.
String indices 15 through 27 include the variants for staying within budget,
new quarterly budgets, and overspending consequences. In particular, the
shipped text explicitly includes the case where the chairman has to take money
from the building and transfer budgets to compensate for overspending. This
independently reconfirms that those two reserves are mutable inputs to the
quarterly board process.

### ENGLIS2.IDX format and loader

`ENGLIS2.IDX` is exactly 2,877 little-endian uint16 values (959 triples).
The language initialization path loads the EAM string data into the object at
`0x876C70` and parses the index through `0x5B65A0`.

Helper `0x64E320` takes a destination pointer slot, the loaded string-table
object and a uint16 string index. It resolves the corresponding string pointer
from the table and stores it into the fixed destination global. The first
destination is `0x87AC28`, followed by descending four-byte slots.

Thus the EnglishEAM index is a startup mapping from localization-string indices
to fixed live string globals, not a board-calculation script.

The quarterly-budget string indices 15..27 map to globals
`0x87ABEC..0x87ABBC`. Whole-image reference checks find only their loader
assignments and no later direct code/data references to those specific slots.
The loaded EAM string-table and index objects are likewise only startup
language-loader state.

### Consequence

The EnglishEAM files recover and verify the exact original board wording but
do not contain the live transfer-budget calculation or mutable reserve state.
The quarterly budget producer remains executable/runtime behavior.

## Business Consultant formatter and loader false leads

RTTI resolves `ModFmt::BusinessConsultant` to vtable `0x7D60F8`. Its
single virtual method `0x6135B0` is a text formatter: it resolves support
staff type 4 from the DBRUser support-staff list and substitutes that person's
name. It is not a budget-state owner or event generator.

The alternate event-load helper `0x534520` was also inspected. It is a
separate subtype factory whose switch covers IDs 1..155, so it cannot directly
construct `EAMbcmonthlybudget` ID 161. It is not the missing A1 template
lookup.

The neighboring Business Consultant event constructors
`bcmonthlyincome` (0x9F), `bcstartseasonmail` (0xA0) and
`bcmonthlybudget` (0xA1) remain generic-factory-only.

### Refined next target

Direct typed construction, ordinary queue insertion, CMonthHistory consumers,
Business Consultant name formatting, EnglishEAM localization data and the
alternate subtype factory are now bounded.

The next trace should focus on either:

1. generic event clone/copy/template methods reachable through the common EAM
   vtables, especially methods shared by the 0x9F/0xA0/0xA1 family; or
2. unidentified persistent/scalar DBRUser save-state that could hold the
   chairman operating/building/transfer allocations and feed generated events.
