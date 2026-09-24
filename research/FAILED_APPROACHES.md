# Failed and Inconclusive Approaches

_Last updated: 24 September 2026_

This document prevents future sessions from repeating analyses that have already been disproven, superseded, or shown to be low-value.

## Runtime / Windows

### Run original game as administrator

Attempt:
- launch restored original `footballmanager.exe` with “Run as administrator”.

Result:
- no visible change; game still did not open.

Conclusion:
- disproves the hypothesis that the immediate failure is simply denied write access to the legacy HKLM registry key.

Status:
- ruled out as the primary fix.

### Patch legacy HKLM registry access to HKCU

Attempt:
- back up executable;
- patch the relevant predefined-HKEY selector from HKLM to HKCU;
- create equivalent 32-bit HKCU game registry values.

Result:
- patch itself was applied correctly;
- Windows Device Guard / Code Integrity blocked the modified executable.

Conclusion:
- binary patching an already-unsigned legacy executable is not a practical way around the current host security boundary.

Status:
- abandoned on the main Windows host.

### Treat exit code -1 as an application-internal crash

Early interpretation:
- `start /wait footballmanager.exe` returned `-1`, suggesting a silent FM2001 startup failure.

Later evidence:
- Code Integrity Operational Event ID 3077 explicitly identifies the executable as blocked.

Conclusion:
- host execution policy must be considered before interpreting the return code as an internal FM2001 crash.

Status:
- superseded.

## Master.dat / player records

### Six-byte player-section header

Early assumption:
- uint32 player count + an additional uint16 header field.

Why it looked plausible:
- an earlier manual boundary calculation happened to produce plausible strings/records.

Disproof:
- EA's actual loader `0x421C80` reads one 4-byte player count and immediately starts 103-byte records;
- re-parsing at the four-byte boundary aligns names, clubs, dates and skill arrays correctly.

Conclusion:
- player section header is exactly four bytes.

Status:
- definitively wrong; do not reuse.

### One 18-byte player attribute block at +22..+39

Early assumption:
- 18 bytes represented player attributes.

Disproof:
- compact importer `0x418B90` performs a 3-byte position read at +21..+23, then two separate 17-byte reads at +24..+40 and +41..+57.

Conclusion:
- there are two 17-byte skill arrays, current and development target.

Status:
- definitively wrong; do not reuse.

### Linear `round(raw * 30 / 255)` skill conversion

Early prototype:
- used generic rounded linear conversion.

Recovered game formula:

`floor((30*raw + 128) / 255)`

Conclusion:
- old prototype conversion is not exact.

Status:
- superseded.

## Manager records

### Old manager offsets (+6/+8 names, +10 DOB, +22 joined, +29 club)

Early documentation used those offsets.

Disproof:
- direct byte validation against manager 10 and 204 produced malformed names such as “Ferguson Sijes” and “Wenger Gilhaus”;
- corrected layout resolves Alex Ferguson and Arsène Wenger exactly.

Correct offsets:
- +0 uint32 ID
- +4 first-name Core.str ID
- +6 surname Core.str ID
- +8 DOB
- +20 joined club
- +27 current club ID

Status:
- definitively wrong; corrected in FILE_FORMATS/FINDINGS.

## Club / budget analysis

### Assume runtime club +0x3C..+0x54 is the seven-budget block

Reason:
- seven consecutive dwords visually matched the seven fields in the start-season budget mail.

Disproof:
- EA's compact club reader maps:
  - runtime +0x3C from disk +0x2E localized sponsor string;
  - runtime +0x40 from disk +0x30 manager ID;
  - following bytes are ordinary club record data.
- Arsenal validates as sponsor string “Sponsor” and manager ID 204.

Conclusion:
- the similarity in count/spacing was coincidental.

Status:
- definitively rejected.

## Finance cheat-code analysis

### Label 0x516090 as /cash777 and 0x516020 as /budget777 from caller context

Reason:
- those tiny accessors appeared near current-cash and finance/business branches.

Disproof:
- RTTI resolves the global object at `0x877540` as C++ standard-library stream machinery:
  - `std::basic_istream`
  - `std::basic_istringstream`
  - `std::basic_streambuf`
  - `std::basic_stringbuf`
- therefore the byte getters around `0x515FF0..0x5160E0` expose stream/internal state, not cheat flags.

Conclusion:
- all cheat labels assigned to those accessors are invalid.
- literal switches `/cash777` and `/budget777` still exist, but their real data-driven parser/storage must be recovered separately.

Status:
- definitively superseded.

## Transfer deal states

### Interpret states 2/5 as counter-offer states

Early behavioral interpretation:
- transfer execution copied stored player terms and blocked completion when state 2/5 was present.

Later named-event evidence:
- reason-code/event classes identify state 2 as player-rejected/declined-contract outcome;
- state 5 is the swap/exchange variant.

Current safe model:
- 0/3 pending/unresolved
- 1/4 cleared/ready family
- 2/5 player rejected/declined
- +3 denotes swap/exchange variant

Status:
- earlier “counter-offer” label superseded.

## Documentation rule

When a later analysis disproves an earlier interpretation:
1. update the canonical file;
2. mark historical notes as superseded or remove them;
3. add an entry here if the mistake is likely to be repeated;
4. commit the correction before continuing.


### Treat 0x877540..0x877562 as one basic_istringstream object

Earlier correction:
- RTTI for nearby routines identified `std::basic_istream`, `std::basic_istringstream`, `std::basic_streambuf`, and `std::basic_stringbuf`;
- this was used to conclude that `0x877550..` were bytes inside a global stream object and therefore could not be cheat flags.

Disproof:
- static initializer `0x515F10` invokes `0x5162A0` on `0x877540`;
- `0x5162A0` is an ordered-tree constructor with a 16-byte object header, allocated 0x24-byte sentinel node, self-referential tree links, and size/bookkeeping fields;
- its matching destructor `0x515F50` destroys tree nodes;
- the streambuf/stringbuf RTTI belongs to a separate routine family beginning around `0x5166A0`.

Conclusion:
- `0x877540..0x87754F` is a tree container;
- `0x877550..` are independent globals and may legitimately be command/cheat state;
- the earlier stream-based rejection of all `0x515FF0..0x5160E0` getters is superseded.

Status:
- definitively superseded by constructor-level evidence.


## Superseded correction: treating 0x877540 itself as std::basic_istringstream

Earlier conclusion:
- global `0x877540` was identified as a `std::basic_istringstream`;
- therefore bytes `0x877550..` were treated as stream/internal state and the nearby getters were rejected as cheat/option accessors.

Disproof:
- static constructor `0x515F10 -> 0x5162A0` initializes `0x877540` as a 16-byte non-polymorphic ordered-tree/container header;
- `0x5162A0` allocates a 0x24-byte self-linked sentinel/tree node and writes no stream vtable to the object;
- destructor `0x515F50` clears/frees the tree structure;
- the real basic_istream/basic_istringstream/basic_stringbuf vtables occur in the separate routine family beginning around `0x516370`, operating on a larger object through unrelated offsets.

Conclusion:
- `0x877540` is not itself the istringstream object claimed by the earlier RTTI interpretation;
- bytes `0x877550..` must be treated as adjacent independent globals;
- exact cheat literal mappings still require parser evidence and must not be inferred solely from adjacency.

Status:
- earlier istringstream-global conclusion superseded.


## Treat game/session +0x694 as live chairman budget storage

Reason it looked plausible:
- the pointer is heavily used in finance/business code;
- it points to a small 0x7C-byte object with multiple integer fields.

Disproof:
- the object is allocated at `0x425BCA`;
- `0x5DE530`, tied to named season-ticket events, reads its +0x04 field;
- nearby season-ticket calculations populate +0x08/+0x0C;
- `0x618Cxx..0x618EFF` iterate its +0x14..+0x78 entries as business/selection state.

Conclusion:
- this is season-ticket/business state, not the authoritative chairman transfer-budget object.

Status:
- ruled out as live transfer-budget storage.


## Treat EAMChairmanRefusesExpenditureM as live budget storage

Why it looked promising:
- the event is generated from the same insufficient-funds transfer branches used by the cash-affordability checks;
- its name explicitly refers to chairman refusal of expenditure.

Disproof:
- constructor `0x56E480` stores only two small identifier/context arguments at +0x3C/+0x40;
- transfer-path callers populate these with club/index/manager-like identifiers rather than the rejected monetary amount or a budget scalar;
- formatter `0x56E540` selects localized refusal text but does not expose live budget fields.

Conclusion:
- this class is a notification/event object, not authoritative transfer-budget state.

Status:
- ruled out as live budget storage.


## Treat game/session +0x5B4 as a hidden chairman-budget controller

Why it looked promising:
- chairman extra-transfer formatters and multiple finance routines repeatedly dereference game/session +0x5B4 and read fields such as +0x04/+0x40.

Disproof:
- initializer `0x4258D0` receives a pointer argument and stores that exact pointer directly to game/session +0x5B4 at `0x4258F2`;
- the pointer is used throughout broad club/team gameplay code, not as a finance-only owned object;
- the small fields used in chairman messages behave as club/manager identity context.

Conclusion:
- game/session +0x5B4 is current club/team context, not a separate live budget storage/controller object.

Status:
- ruled out as a distinct budget store.


## Treat Balance +0x50 / ChairmanPercentBudgetMiss as transfer-budget enforcement

Why it looked promising:
- `ChairmanPercentBudgetMiss` is an explicit chairman/budget tuning key with a live gameplay read;
- routine `0x5E1D90` compares Balance state against current cash.

Disproof:
- the compared value is Balance +0x50 inside the serialized financial-state block;
- the percentage calculation is exactly `target * ChairmanPercentBudgetMiss * 0.01`;
- the two generated events are RTTI-identified as `EAMManagerObjectiveContinuedSuccess` and `EAMManagerFailedObjective`.

Conclusion:
- this is the manager/chairman financial-objective tolerance system, not the seven spending-budget buckets or transfer-budget affordability.

Status:
- ruled out as authoritative transfer-budget storage/check.


## Interpret EAMchairextratransfersuccess +0x40 as a seven-budget-category selector

Why it looked plausible:
- the formatter has a seven-way 1..7 dispatch;
- the chairman system elsewhere exposes seven budget-related values;
- selector 7 was excluded from the random 1..6 default path.

Disproof:
- direct inspection of `ENGLIS2.STR` shows every formatter variant is a different chairman message/circumstance for **increasing the transfer budget**;
- the event itself is `EAMchairextratransfersuccess`;
- a separate `EAMchairextraforallbudgets` event handles increases across all budgets.

Correct interpretation:
- +0x3C = transfer-budget increase amount;
- +0x40 = success wording/reason variant selector;
- +0x44 = club/team ID.

Status:
- superseded and corrected.


## Treat DBRClub +0x21C..+0x234 as the chairman budget block

Why it looked promising:
- club-state copy code moves a consecutive group of dwords in this region;
- the size/shape initially resembled a persistent multi-budget structure.

Disproof/current evidence:
- broader xref inspection shows these offsets are used in unrelated club/runtime operations;
- accesses include mixed pointer/index/byte-style behavior inconsistent with a dedicated seven-budget monetary array;
- no budget formatter, warning calculation, or chairman-budget event has yet been tied to this region.

Conclusion:
- do not identify DBRClub +0x21C..+0x234 as live budget storage without new independent evidence.

Status:
- rejected as current budget candidate.


## Treat the six Balance +0x30..+0x80 records as possible chairman budget buckets

Why it remained plausible:
- the six 16-byte value/range records are persistent and serialized;
- only Balance +0x50 had previously been semantically identified, leaving the other five open.

Disproof:
- periodic routine 0x5E12C0 is called with ECX = Balance+0x30 and directly processes this whole block;
- it constructs RTTI-named EAMManagerWarnedObjective and EAMMonthlyFinancialTargets events;
- EAMMonthlyFinancialTargets formatter explicitly labels values BALANCEA, BALANCEB, PROFITA, PROFITB and TARGET;
- adjacent routines on the same block emit EAMManagerObjectiveGoodWork and manager-objective success/failure events.

Conclusion:
- the six serialized records form financial-objective/target/forecast state, not the chairman spending-budget reserve array.

Status:
- definitively rejected as live transfer-budget storage.


## Treat game/session +0x698 as possible chairman budget storage

Why it looked promising:
- persistent/save-serialized 0x108-byte object;
- constructor initializes several finance-value records and tuning-driven child objects;
- it sits adjacent to other finance/business state.

Disproof:
- constructor tuning inputs resolve directly to Bank1/Bank2/Bank3 loan limits, repayment terms and APR values;
- dedicated save/load routines preserve this loan state.

Conclusion:
- game/session +0x698 is the bank-loan subsystem, not chairman transfer-budget storage.

Status:
- definitively rejected as live transfer-budget storage.


## Interpret `push 0x44C` in Balance.cpp as allocation of EAMchairbudgetwarning

Why it looked promising:
- `EAMchairbudgetwarning` is 0x44C bytes;
- several Balance.cpp sites contain `push 0x44C`;
- some occur near finance aggregation.

Disproof:
- the following instruction flow passes 0x44C directly as a category argument to ledger routines rather than to operator new;
- Stadium Manager/Groundsman expenditure paths use the same 0x44C value while constructing category-tagged finance postings and then debit Balance;
- Finance Overview independently queries the same category through its aggregation helper.

Conclusion:
- these are accounting category **1100** references, not event allocations.
- event size and category value happen to be numerically identical.

Status:
- rejected before being used as producer evidence.


## Treat game/session +0x690 as chairman budget storage

Why it looked promising:
- persistent save-state object;
- large 0xB50 allocation;
- eight repeated 0x168-byte records suggested per-manager/per-club state.

Disproof:
- its periodic timing globals are explicitly loaded from `FCConcessionOfferMinWait` and `FCConcessionOfferMaxWait`;
- nearby tuning keys are concession-specific;
- routine `0x5E5640` iterates active records and credits their financial value to current cash through Balance `0x5DC510`;
- record layout includes large text buffers consistent with commercial/concession offers.

Conclusion:
- game/session +0x690 is the concession-offer subsystem, not chairman transfer-budget storage.

Status:
- ruled out.


## Treat game/session +0x69C as chairman budget storage

Why it looked plausible:
- persistent save-state object adjacent to other finance/business objects;
- runtime periodic logic.

Disproof:
- the object's update path consumes globals loaded from `FSNoSponsorMinWait`, `FSNoSponsorMaxWait`, `FSHaveSponsorMinWait`, and `FSHaveSponsorMaxWait`;
- the same tuning family continues with `FSOfferMinLifeTime`.

Conclusion:
- game/session +0x69C is sponsor-offer/sponsor-state scheduling, not chairman transfer-budget storage.

Status:
- ruled out.


## Treat EAMChairmanNotEnoughFunds as the transfer-budget reserve check

Why it looked promising:
- distinct chairman-specific event name;
- emitted from a real gameplay financial path rather than pure UI registration.

Disproof:
- immediately before construction at `0x4EECA0`, the requested monetary value is passed through `0x404AE0`;
- `0x404AE0` is independently proven as the current-cash affordability helper;
- the event is taken only on that cash-test failure branch.

Conclusion:
- `EAMChairmanNotEnoughFunds` reports insufficient current cash, not exhaustion of the separate chairman transfer-budget reserve.

Status:
- ruled out as transfer-budget storage/check.


## Treat game/session +0x6B0 as possible chairman budget state

Why it looked plausible:
- very large persistent object;
- contributes values to monthly finance history;
- contained multiple arrays and an internal list object.

Disproof:
- internal vtable RTTI identifies `CEntriesList`;
- club setup passes the stadium/map asset into `0x65D5B0` on this object;
- load failure formats EA's explicit `Unable to load stadium ... building screens, and ticketing will not work!` message.

Conclusion:
- game/session +0x6B0 is stadium/entry/building/ticketing state, not chairman budget storage.

Status:
- ruled out.


## Treat DBRUser +0x588..+0x5A8 as the five chairman operating budgets

Why it looked promising:
- exactly five consecutive qword financial values;
- chairman has five quarterly operating-budget categories.

Disproof:
- initializer `0x4268C0` sources the values from tuning globals explicitly named `LRADIO_MAX/RES`, `NRADIO_MAX/RES`, `LTV_MAX/RES`, `NTV_MAX/RES`, and `EUROPEAN_MAX/RES`.

Conclusion:
- the block is media-rights/reserve state, not chairman operating-budget state.

Status:
- ruled out.
