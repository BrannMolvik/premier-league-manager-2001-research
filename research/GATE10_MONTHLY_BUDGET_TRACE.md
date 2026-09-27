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


## Canonical-disc rule inventory and DBRUser +0x5EC classification

Recovery resumed from main `df12a79645270c07374189e43a0e9d007080ffaa`.
The authorized disc image was re-materialized and converted from MODE1/2352
locally. The extracted `FOOTBAL.EXE` SHA-256 was reverified as:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

No extracted binary/data was added to Git.

### No external chairman-budget rule/script resource on the disc

A full ISO9660 filename inventory was checked for event/rule/config/data
resources outside the already-inspected BUSINESS presentation tree.

The potentially executable/data-oriented loose resources are limited to known
families such as:

- `ENGLIS2.IDX/STR` and `ENGLISH.IDX/STR` localization;
- `MASTER.DAT`, `STATIC.DAT`;
- match/presentation data such as `AISCRIPT.VIV`, `GEN4TBLS.T`,
  `CAMERA.SCR`, `FC.BIN`, set-piece/control files;
- audio `.EAM/.STR` data;
- UI/image resources under `FM2001_/BUSINESS`.

There is no separate board/chairman/business-consultant rule file, EAM
scenario file, budget table, or other obvious external source capable of
holding the live quarterly reserve mutation.

This strengthens the current producer model: the mutable chairman
building/transfer reserve is executable/runtime behavior, not a missed loose
disc script.

### DBRUser +0x5EC is scouting state, not budget storage

DBRUser construction creates exactly four 0x1C-byte records beginning at
`+0x5EC` through constructor `0x424F70`. Save/load iterates those four
records through `0x4ACAC0`.

The DBRUser accessors `0x42BCE0/0x42BD10` first call `0x42B8A0`, map the
requested context to one of the four records, then address:

`DBRUser + 0x5EC + index * 0x1C`.

Those accessors are heavily consumed throughout the already-identified
`PScouting2K` / scouting routine family around `0x4ADxxx..0x4AFxxx`.
The record helpers manage player-indexed list entries and scouting-side state;
for example `0x4AD080` compares a 16-bit player identifier with record
fields and `0x4AD130` searches the record's dynamic player list.

Therefore the four persisted `+0x5EC` records are scouting/list state and
are removed from the chairman-budget search.

### Revised next target

Continue classifying the remaining large serialized/raw DBRUser state,
especially the `+0x700/+0x704/+0x708/+0x70C` region and any scalar fields
with finance/monthly consumers. Do not revisit external scripts, the four
`+0x5EC` records, presentation events, Balance objective records, or named
budget-default globals.


## DBRUser +0x700/+0x704/+0x708 is managed-club ID history

The next large-state pass resolves the dynamic array immediately preceding the
opaque +0x70C raw block.

Constructor/setup state:

- `DBRUser +0x700` = dynamic dword-array pointer;
- `+0x704` = current count;
- `+0x708` = capacity, initialized to **10**.

Helper `0x425590` appends one dword and grows capacity by ten when needed.
Helper `0x425620` returns the last dword or -1 when empty.

The only direct append call is in DBRUser setup at `0x4256D7`. Immediately
before that call:

- `EDI = DBRUser +0x5B4` current club/team object;
- `EDX = [EDI+0x04]`;
- EDX is passed to `0x425590`.

Thus the array stores the current club/team record identifier as part of
manager/user setup and preserves prior entries. Its shape and sole producer are
consistent with managed-club/career club-ID history, not a monetary budget
array.

Save/load independently persists:

- the count at +0x704;
- capacity at +0x708;
- exactly `count * 4` bytes of +0x700 array contents.

Therefore +0x700..+0x708 is removed from the chairman transfer/building-budget
search.

Next target remains the adjacent raw 0x9CC-byte block at `DBRUser +0x70C`
through just before +0x10D8, plus any scalar finance/monthly consumers elsewhere
in DBRUser.


## DBRUser +0x70C..+0x10D7 is PFormation2k preset state

The previously opaque 0x9CC-byte DBRUser save block is now identified from a
direct runtime consumer and MSVC RTTI.

### Exact block shape

DBRUser save/load copies exactly 0x9CC bytes beginning at `+0x70C`.
Formation-screen initialization at `0x46583B` obtains the active DBRUser
through `0x4139D0` and checks:

`[DBRUser+0x70C] == 0x074A3216`.

When the magic differs it writes that value and initializes five records
beginning at `DBRUser+0x714`. Record stride is exactly **0x1F4 (500) bytes**:

`+0x714 + slot * 0x1F4`, for slots 0..4.

Five records plus the 8-byte header account exactly for the serialized size:

`8 + 5 * 0x1F4 = 0x9CC`.

### RTTI and player/role contents prove formation ownership

The surrounding screen object's vtable `0x7C1AB4` resolves through MSVC RTTI
to **`PFormation2k`**.

The same PFormation2k routines access each DBRUser record and:

- maintain a text/name field at the record base;
- append a slot digit to a localized default label;
- iterate the current club roster;
- store player identifiers beginning at record `+0x10`;
- obtain each player's current assigned role through `0x4EA3C0`;
- store role data beginning around record `+0xB0`;
- use the byte at record `+0x1F0` as record/status state.

Additional PFormation2k methods around `0x465E..`, `0x4674..`,
`0x4675..`, `0x467A..`, `0x467B..` and `0x467D..` address the same
five records through the exact `+0x714 + slot*0x1F4` layout.

Therefore the entire raw DBRUser region `+0x70C..+0x10D7` is persisted
formation/team-sheet preset state, not chairman financial state.

### Consequence for the Gate-10 search

Together with the already-classified +0x700 managed-club history, this removes
the final large raw save block immediately before the known +0x10D8 sacking
reason from the transfer/building-budget search.

Next trace should focus on remaining DBRUser scalar fields and board/monthly
arithmetic outside the now-classified serialized containers, rather than
continuing to search the +0x700..+0x10D8 save region.


## DBRUser +0x694 is stadium-section state, not chairman budget storage

The previously unclassified persistent pointer at `DBRUser +0x694` is now
bounded by its constructor, serializer, and live consumers.

### Persistent object shape

DBRUser setup allocates exactly **0x7C bytes** for `+0x694`.
The object is serialized by:

- read: `0x6186E0`;
- write: `0x618750`.

Those routines persist five leading dwords followed by a contiguous 0x68-byte
tail. The tail is exactly **26 dwords** beginning at object `+0x14`.

### Live consumers are stadium-section calculations

Initialization and update helpers `0x6187E0`, `0x618A20`,
`0x618B60`, `0x618C10` and related routines iterate exactly 26 entries.
For each index they query the stadium structure at `DBRUser +0x6B0`, resolve
a stadium section through the collection at stadium `+0x1B98`, and read
section flags/capacity-derived values.

The 26 persisted dwords are tested and assigned as small state values such as
0, 1, 2, and -1. Downstream monthly/business routines at `0x429904`,
`0x429BB4`, `0x42A111`, `0x42A5D2` and `0x42C1F2` combine the
object's leading `+0x08/+0x0C` values with stadium capacity helpers
`0x65DA60/0x65D9B0` and the per-section state.

This is stadium/attendance-section state, not a compact set of chairman
staff/wage/maintenance/building/transfer allocations.

Therefore `DBRUser +0x694` is removed from the live transfer-budget search.

### Remaining storage search

The known persistent finance-adjacent DBRUser owners from `+0x688` through
`+0x6B0` are now all semantically bounded. The chairman reserve trace should
move away from this pointer cluster and toward the board/accounting arithmetic
that calculates quarterly budget outcomes or toward other non-DBRUser owners.


## DBRUser +0x5DC is a support-staff selector/controller, not budget state

A remaining finance-adjacent field at `DBRUser +0x5DC` was audited because
the financial-objective path loads it immediately before checking whether the
user has a Business Consultant.

The accessor family at `0x4D0B10..0x4D1290` now establishes the semantics.

### Exact typed staff lookup family

The functions take the DBRUser as an explicit argument and walk its linked
support-staff lists. Each candidate's virtual method at vtable +0x14 returns a
small staff-type ID.

The first lookups are exact:

- `0x4D0B10` -> staff type 1;
- `0x4D0B90` -> type 2;
- `0x4D0C10` -> type 3;
- `0x4D0C90` -> type 4;
- `0x4D0D10` -> type 5;
- `0x4D0D90` -> type 6;

and the family continues through the higher staff-type values. The generic
dispatcher `0x4D13D0` accepts values 1..16 and routes to these exact typed
lookup helpers.

The type-4 lookup at `0x4D0C90` is the already-observed Business Consultant
presence test used by the Balance financial-objective routine at
`0x5E130F -> 0x4D0C90`.

### The +0x5DC object does not hold the returned staff list or budget data

Callers conventionally load:

`ECX = [DBRUser+0x5DC]`

and pass the DBRUser itself on the stack. The typed lookup implementations use
the DBRUser argument's support-staff list heads such as `+0x5BC` and
`+0x5C8`; they do not read monetary fields from the `this` object.

`0x4D1320`, another method reached through the same `+0x5DC` owner,
iterates the same staff lists and applies staff/user maintenance through
`0x4CB0B0`.

Therefore `+0x5DC` is a support-staff lookup/controller/service object used
to query and maintain the user's support staff. It is not a persistent
chairman staff/wage/building/transfer budget store.

### Consequence

The entire `+0x5B8..+0x5E8` neighborhood is now finance-irrelevant for live
budget storage:

- the linked structures at `+0x5B8/+0x5C4/+0x5D0/+0x5E0` are support-staff
  containers/state;
- `+0x5DC` is the support-staff selector/controller used to retrieve typed
  staff such as the Business Consultant;
- `+0x5EC` begins the separately classified scouting-state array.

The chairman reserve search should no longer revisit this region.


## Global 0x51F950/0x51F990 path is League participant-cache state

The remaining first-of-month/global call pair reached from the calendar
coordinator through `0x4A83A0` has now been classified and removed from the
chairman-budget search.

### 0x4A8280 builds League-derived cache objects

`0x4A8280` iterates the active DBRUsers and current competition objects. For
candidate competitions it:

- obtains the live polymorphic competition object;
- compares its club/team references against the user's current club;
- performs an MSVC dynamic cast using the RTTI descriptors at
  `0x818958` / `0x818978`, whose type names are
  `Competition` and `League`;
- on a successful League cast, calls `0x4F87A0`.

`0x4F87A0` allocates an 8-byte container and deep-copies the source
League container beginning at `League +0x34` through `0x4F8560`.
The resulting clone is then installed through `0x51F950` for the
per-user slot or `0x51F990` for the singleton/global slot.

### 0x51F950/0x51F990 are replace-and-destroy setters

`0x51F950` indexes global pointer array `0x87776C`; `0x51F990`
owns singleton pointer `0x8777EC`. When an old pointer exists, both call
`0x4F8620`, which destroys the copied container elements and backing array,
then frees the object. Otherwise they simply install the supplied pointer.

`0x4A83A0` passes null through these setters for every user slot and the
singleton, so it is a cache-clear routine rather than a monthly finance
calculation.

Downstream consumers around `0x5233F9/0x52341D/0x523438` read the same
cached pointers while working with live Competition/League objects, further
confirming competition ownership.

### Consequence

The `0x4A83A0 -> 0x51F950/0x51F990` path immediately following
first-of-month user processing is **competition/League participant-cache
maintenance**, not the quarterly chairman budget producer.

The Gate-10 trace should continue with board/accounting arithmetic and other
calendar/season coordinator calls, not this global cache family.


## Static reachability of A0/A1 budget events is persistence-only

The generic-factory route has now been checked for both direct and ordinary
address-taken reachability, tightening the earlier producer boundary.

### Constructor/vtable uniqueness

For the relevant budget-event classes, each concrete vtable constant occurs
exactly once in the entire executable image: at that class's constructor
vtable write. In particular:

- `EAMbcstartseasonmail` vtable `0x7D0150`: one image occurrence;
- `EAMbcmonthlybudget` vtable `0x7D01A4`: one image occurrence;
- `EAMchairbudgetwarning` vtable `0x7CDC10`: one image occurrence;
- `EAMchairbudgetsettings` vtable `0x7CDAC0`: one image occurrence.

The A0 constructor `0x541AD0` and A1 constructor `0x541B20` each have
exactly one direct caller, their respective branch inside generic EAM factory
`0x538DE0`.

There is therefore no second typed construction site and no static prototype
object carrying one of these vtables that could bootstrap a memcpy/clone path.

### Generic factory has only persistence callers

A complete executable disassembly contains exactly two direct calls to
`0x538DE0`:

- `0x5CE588`: wrapped-mail/event deserialization;
- `0x5CF8A7`: DBRUser event-list deserialization.

A raw-image scan also finds no absolute `0x538DE0` function pointer, so the
factory is not present in an ordinary static callback/function-pointer table.
The same check finds no absolute constructor pointer for A0/A1.

This does not mathematically exclude deliberately computed code pointers or
unknown behavior outside the mapped executable. It does establish that the
ordinary static call graph has **no fresh-game path** that can instantiate
A0/A1 through their only constructors.

### Interpretation boundary

The strongest evidence-backed description is now:

- A0/A1 and related chairman-budget message classes are **persistence-loadable
  presentation/event types** in this shipped build;
- no mapped fresh-game producer creates them;
- named budget default globals are likewise loader-only;
- current-cash and financial-objective systems, by contrast, have direct live
  gameplay consumers.

This materially raises the possibility that the older chairman operating /
transfer-budget event family is legacy or inactive in the normal FM2001
fresh-game path. Do **not** yet promote that to a global-unreachable claim:
legacy saves or an unmapped computed dispatch may still materialize these
types.

### Revised next target

Test the legacy/inactive-budget hypothesis against the remaining live user
experience and finance paths:

1. identify whether any normal fresh-game UI reads a transfer/wage budget
   outside these event formatters;
2. continue recovering the proven monthly wage/operating cash debits;
3. if no live budget consumer exists, treat the chairman budget event family
   as a fidelity/legacy compatibility item rather than inventing an
   authoritative mutable store for Gate 10.


## Normal Finance/Transfer UI has no chairman-budget consumer

The legacy/inactive-budget hypothesis was tested directly against the two normal
fresh-game UI classes most likely to expose a live transfer or wage budget.

### PFinanceOverview is Balance/accounting-driven

MSVC RTTI resolves:

- `PFinanceOverview` type descriptor at `0x81B0F0`;
- Complete Object Locator `0x7E10A8`;
- vtable `0x7BFCC4`;
- concrete constructor vtable writes at `0x43F7AC/0x43F81E`.

A bounded disassembly of the full Finance Overview implementation region
(`0x43C800..0x440190`) finds **no reference** to:

- chairman budget-default globals `0x821D80..0x821DC0`;
- `TOTALBUDGET`, `PLAYERWAGEBUDGET`, `TRANSFERBUDGET`,
  `BUILDINGSLIMIT` or the sibling budget formatter keys;
- the A0/A1 or chairman budget-settings/warning vtables.

Instead, the panel repeatedly resolves `DBRUser +0x670` and calls the live
Balance aggregate family:

- `0x5DC890` credit/income aggregation;
- `0x5DD650` debit/outflow aggregation;
- `0x43F1E0` net aggregation.

This includes the already-proven category-1000 transfer row.

Therefore the normal Finance Overview presents live Balance/accounting data,
not a separate chairman transfer/wage-budget scalar.

### PTransfer2K likewise has no chairman-budget reference

RTTI resolves:

- `PTransfer2K` type descriptor at `0x81C9A0`;
- Complete Object Locator `0x7E3CD0`;
- vtable `0x7C2EB8`;
- constructor/destructor vtable writes around `0x47B5D6/0x47FA2E`.

A broad disassembly scan across the Transfer screen implementation region
(`0x47A000..0x482500`) likewise finds no reference to the named budget
globals, budget formatter keys, or chairman A0/A1/settings/warning vtables.

Transfer affordability remains enforced in the transfer workflow through the
already-proven current-cash helper `0x404AE0`, outside the presentation
class.

### Budget-key xrefs are formatter-only

A complete direct xref inventory for the executable literals
`TOTALBUDGET`, `STAFFBUDGET`, `PLAYERWAGEBUDGET`,
`MAINTENANCEBUDGET`, `MERCHANDISINGBUDGET`, `MISCBUDGET`,
`BUILDINGSLIMIT/BUILDINGSBUDGET` and `TRANSFERBUDGET` finds them only
inside the already-identified chairman / Business Consultant event formatter
ranges around `0x55C8xx..0x55CExx` and
`0x572Bxx..0x5736xx`.

The A0/A1 constructors themselves only initialize common event base state
through `+0x34`; they do not seed the budget payload fields.

### Consequence

There is now no mapped fresh-game producer **and** no normal Finance/Transfer
UI consumer for a separate chairman transfer-budget scalar in this executable.
The active FM2001 spending model exposed by ordinary gameplay is instead
centered on Balance current cash, accounting ledgers and financial objectives.

This is still a bounded static conclusion, not a claim that legacy budget
events can never be loaded from old save/event state. It does make inventing a
new live transfer-budget store for the modern port increasingly unjustified
without new evidence.
