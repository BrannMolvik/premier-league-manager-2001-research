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


## DBRUser history owners and false 0x4F event lead resolved

A systematic pass over the remaining serialized DBRUser history containers now
identifies their element families:

- `DBRUser +0x6C4` = `CMatchHistory` list (vtable `0x7BE0FC`);
- `+0x6DC` = `CMonthHistory`;
- `+0x6E8` = `CWeekHistory` (vtable `0x7BE1E4`);
- `+0x6F4` = `CDayHistory` (vtable `0x7BE258`);
- `+0x6D0` is another capped twelve-record reporting/history series using
  non-polymorphic 0x28-byte records populated from attendance/stadium/business
  values.

These containers are reporting histories, not a compact persistent
staff/wage/maintenance/building/transfer budget array.

### Correction: the `0x42AD3C cmp eax,0x4F` branch is not chairman event ID 0x4F

The DBRUser list at `+0x6B4` is indeed an EAM/event list. However, event IDs
for normal EAM vtables are returned by vtable slot **+0x0C**. For example:

- `EAMbcmonthlybudget` vtable +0x0C -> `0x541B50` -> ID 0xA1;
- `EAMchairextratransferfail` vtable +0x0C -> `0x540C40` -> ID 0x4F.

The branch at `0x42AD35..0x42AD3C` instead calls vtable slot **+0x14**
before comparing the result with 0x4F. Therefore that comparison is not an
EAM ID comparison.

The large event objects seen in that list are legitimate EAM objects. A
representative 0x1C44-byte object is constructed by `0x54B610`, which writes
vtable `0x7CF028`; RTTI identifies it as
`EAMFAInternationalSquadAnnounceM`. Its large embedded text/state payload
explains offsets such as +0x1C54 in adjacent event variants.

Consequently the earlier apparent link between the `0x42ADxx` cleanup branch
and `EAMchairextratransferfail` was a numeric/vtable-slot coincidence and is
discarded.

### Remaining producer problem

The A0/A1 Business Consultant budget events still have:

- no direct or inlined gameplay construction;
- no static constructor/factory function-pointer dispatch;
- no producer in another shipped runtime module;
- no direct ordinary `MPMEAMail -> 0x613EC0` typed enqueue site.

The generic A0/A1 factory path remains the binary event deserializer. The next
useful target is the higher-level source that supplies serialized/generated EAM
records to that deserializer during new-game/calendar operation, rather than
more direct-constructor searches.


## Business Consultant generic factory is persistence-only in the mapped runtime

The remaining apparent A0/A1 generation route has now been structurally
classified.

### MPMEAMail wrapper serializer/deserializer

Vtable `0x7BD564` is the already-identified `MPMEAMail` wrapper. Its
relevant virtual methods are:

- vtable +0x08 -> `0x5CE530`: binary **read/deserialization**;
- vtable +0x0C -> `0x5CE5E0`: binary **write/serialization**.

`0x5CE530` has no direct call sites because it is invoked virtually by the
generic queue/list persistence machinery. On load it reads the wrapped event
kind, resolves the owning DBRUser/event list and calls either:

- generic EAM factory `0x538DE0`; or
- alternate subtype factory `0x534520`;

then invokes the event's own binary read method.

This explains the previously puzzling `0x5CE588 -> 0x538DE0` reference
without requiring a hidden gameplay producer.

### Global mail queue load/save pair

Global mail queue `0x947AA8` has a matched persistence pair:

- `0x613F80` loads queued wrapper objects;
- `0x614000` saves queued wrapper objects.

`0x613F80` reads a wrapper subtype, creates that wrapper through the small
0..14 factory at `0x6139E0`, then invokes its virtual read method. For an
`MPMEAMail` wrapper this reaches `0x5CE530` and, from there, the generic EAM
factory.

The executable contains only one direct call to `0x613F80`:
`0x50E108`. Its enclosing state-load routine is reached from the save/load
manager at `0x4C4D26` and `0x4C5183`. The matching state-write routine
calls `0x614000` at `0x50DDA4`.

Separately, DBRUser event-list loader `0x5CF840` has only one direct caller,
`0x42744C`, inside the DBRUser serialization/load path.

### Consequence for A0/A1

The only direct executable calls to generic EAM factory `0x538DE0` remain:

- `0x5CE588`: wrapped-mail deserialization;
- `0x5CF8A7`: DBRUser event-list deserialization.

Both are now bounded to persistence/load machinery.

Together with the existing negative evidence that
`EAMbcstartseasonmail`/A0 and `EAMbcmonthlybudget`/A1 have no direct typed
construction, no inlined vtable construction, no static constructor pointer
dispatch and no ordinary typed `MPMEAMail -> 0x613EC0` enqueue site, the
generic factory is **not a fresh-game budget producer** in the mapped
executable.

This does not prove that the event classes are globally unreachable under every
possible legacy/save-state condition. It does prove that continuing to search
the generic deserializer for the authoritative live transfer-budget
calculation is the wrong route.

### Revised next target

Return to live board state itself:

1. identify remaining persistent/scalar DBRUser fields not yet classified;
2. prioritize values written/read around quarterly/monthly board processing;
3. look for arithmetic involving the known operating-budget ledger categories
   and building/transfer reserve values rather than presentation-event
   construction.


## DBRUser +0x6A4 and +0x6AC ruled out as chairman budget owners

The remaining small serialized DBRUser objects immediately before stadium state
have now been classified far enough to remove two more false budget candidates.

### DBRUser +0x6A4 is out-of-game/injury state

The object at `DBRUser +0x6A4` is a linked container persisted by:

- read: `0x5E3E50`;
- write: `0x5E3F20`;
- rebuild/initialization: `0x5E3FD0`;
- periodic routines: `0x5E4190` and `0x5E4210`.

Its subtype factory is `0x5E2710`, switching over values 0..0x24. RTTI from
the factory-created vtables identifies the family directly as out-of-game /
injury records. Representative types include:

- `AogVirus`;
- `AogFluWeak`;
- `AogFluOut`;
- `AogBrokenLegHeavy`;
- `AogBrokenFootSerious`;
- `AogDamagedAnkle`;
- `AogDamagedShoulder`;
- `AogAchillesMild`;
- `AogShinSerious`;
- `AogCalfMild`;
- `AogThighSerious`;
- `AogKneeModerate`.

The periodic paths compare/update record dates and active/status bits. This is
consistent with the injury/out-of-game subsystem and not with a chairman
operating/building/transfer budget store.

### DBRUser +0x6AC is monthly-summary message state

The object at `DBRUser +0x6AC` is a small persisted state block:

- read: `0x617DE0`;
- write: `0x617E30`;
- monthly/update routine: `0x617E80`, called from DBRUser monthly maintenance
  around `0x42AE91`.

Its state includes two qwords and two status bytes. The update routine checks
the mail/message queue for existing relevant wrapper kinds and can create
monthly-summary EAM objects. RTTI identifies the concrete event constructors
used there as:

- vtable `0x7D024C`: `EAMsmmonthlysummarytwo`;
- vtable `0x7D32E4`: `EAMsmmonthlysummaryfour`.

Those events are then wrapped in `MPMEAMail` and enqueued through the normal
`0x613EC0` path.

Therefore `+0x6AC` is monthly-summary/message bookkeeping, not live chairman
budget storage.

### Remaining compact candidate

Among the small serialized objects in this DBRUser region, `+0x6A0` remains
unclassified. It is a linked-list owner persisted by `0x61C290/0x61C230`
and should be classified next before moving to larger scalar blocks.


## DBRUser +0x6A0 is condition-injury state, not chairman finance state

The final compact serialized object in the `+0x6A0..+0x6AC` region is now
semantically bounded.

### Persistence and record layout

`DBRUser +0x6A0` owns a linked list persisted by:

- write: `0x61C230`;
- read: `0x61C290`.

Each loaded list record is 0x14 bytes and contains three 16-bit values followed
by dword state including a date/status field. The wider condition-injury
runtime record family around `0x61C360..` also carries player-linked state and
date ranges.

### Direct player linkage

Helper `0x61C4B0` takes the record's 16-bit player index at `+0x08` and
resolves it directly into the global DBRPlayer table at `0x875640`. The
subsequent paths call established DBRPlayer/player-status helpers and club
eligibility routines.

For example, `0x61C6C0..`:

- resolves the record's DBRPlayer;
- checks player status and active club/manager state;
- checks club roster capacity;
- calls player transfer/status helpers including `0x417DD0`,
  `0x4173B0`, `0x41E1D0`, and club helper `0x405590`;
- applies bounded RNG decisions before mutating the player/record state.

### Tuning keys identify the subsystem

The same path reads globals:

- `0x821814`;
- `0x821818`.

Their tuning-loader writes are directly tied to the shipped keys:

- `0x821814` <- **ConditionInjuryInducingLevel**;
- `0x821818` <- **ConditionInjuryRandomiser**.

Nearby keys are the matching condition-injury duration family, including
`ConditionInjuryAchillesOutMin/Max`, shin/thigh variants, and related injury
settings.

This establishes `+0x6A0` as persistent player condition/injury-management
state, not a staff/wage/maintenance/building/transfer budget owner.

### Consequence

All three formerly-unclassified compact serialized DBRUser owners in this
region are now removed from the chairman-budget search:

- `+0x6A0`: condition-injury state;
- `+0x6A4`: out-of-game/injury record container;
- `+0x6AC`: monthly-summary message bookkeeping.

The next chairman-budget trace should move to the remaining larger
serialized/scalar DBRUser regions rather than revisiting these objects.


## Chairman budget-warning payload and tuning-default boundaries

Two remaining apparent routes to the live reserve have now been bounded.

### EAMchairbudgetwarning does not contain a hidden 0x400-byte budget array

RTTI identifies `EAMchairbudgetwarning` vtable `0x7CDC10`, event ID
`0x4A`. Its binary serializer is `0x55BA10`.

The serializer persists:

- inherited event state;
- one dword at `+0x38`;
- a **0x400-byte block** beginning at `+0x3C`;
- dwords at `+0x43C`, `+0x440`, `+0x444`, and `+0x448`.

The 0x400-byte region is not a 256-dword chairman-budget array. Formatter
`0x55B650` passes `event+0x3C` through the generic **STRING** substitution
path. The same formatter:

- converts `event+0x43C` to a numeric value and binds it to the EA-authored
  **DEFICIT** key;
- binds the fixed **OVERSPENTBUDGET** text key;
- resolves club/chairman/user-name substitutions separately.

Thus this large warning object mainly carries a prebuilt 1,024-byte text
payload plus deficit/context fields. The actual decision about how operating
overspending affects building/transfer reserves has already happened before
this presentation object exists.

This also explains why the object's size, 0x44C, is not evidence of an
embedded seven-budget store.

### Named budget tuning globals are loader-only in the shipped executable

The tuning-loader block maps the expected budget defaults to globals:

- `0x821D94` = `StaffWageBudget2K`;
- `0x821D98` = `PlayerWageBudget2K`;
- `0x821D9C` = `FacilitiesBudget2K`;
- `0x821DA0` = `MiscBudget2K`;
- `0x821DA4` = `StadiumBudget2K`;
- `0x821DA8` = `TransferBudget2K`;
- `0x821DAC` = `StaffWageBudget`;
- `0x821DB0` = `PlayerWageBudget`;
- `0x821DB4` = `FacilitiesBudget`;
- `0x821DB8` = `StadiumBudget`;
- `0x821DBC` = `MiscBudget`;
- `0x821DC0` = `TransferBudget`.

`ChairBudgetProfit` at `0x821D80` and the adjacent profit-pool defaults
show the same pattern.

For each exact budget-global address above, a complete image scan finds only
its tuning-loader write and no ordinary later absolute-address consumer.
A separate check for a shared `0x821000`-style indexed/base access covering
the block also found no static runtime reference.

The heavily consumed globals immediately before this block
(`0x821D00..`) are a separate support-staff star-threshold family
(`DefCoach5Star`, `MidCoach*Star`, `AttCoach*Star`, Doctor/Scout
thresholds, etc.); they must not be mistaken for budget values merely because
they are adjacent.

Therefore the named `TransferBudget` / `*Budget2K` globals are
configuration defaults with no recovered direct runtime consumption in this
build. They are not the authoritative mutable transfer/building reserve.

A dynamically computed or external use cannot be disproven solely by static
absolute-address scanning, so this conclusion is deliberately limited to the
mapped executable's ordinary static consumers.

### Revised producer signature

The quarterly producer must now be sought through live accounting/board
arithmetic or another generated-data path. Presentation objects and named
default globals no longer provide a credible storage location.
