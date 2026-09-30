# Gate 13 management source-data bridge

_Date: 1 October 2026 KST_

## Purpose

Gate 13 needs the original FM2001 management presentation to sit on top of the
already reconstructed simulation rather than duplicating league, squad,
fixture or player-state logic inside widgets.

`reconstruction/gate13_management_source_data.py` introduces a deliberately
read-only boundary for that work. It does **not** claim original screen layout,
screen IDs, navigation events, fonts, colors, column labels, fixture-screen
sort order or widget behavior. Those remain original-resource/native-executable
research.

The bridge only projects already recovered runtime/source data into immutable
rows that a future original-resource renderer can consume.

## Source-backed ordering/field rules

### Controlled-club header

The bridge exposes the current human club's original database `name` and
`short_name` plus the reconstructed game calendar date. Missing source names
fail closed; the bridge does not synthesize display labels.

### Squad

`HumanGameplayController.squad()` delegates to
`GameState.ordered_club_roster()`, which is the live controlled-club roster
order already used by the reconstructed backend. The bridge preserves that
order exactly and records each row's source-roster index.

Projected fields are already recovered runtime state only:

- player ID and source first/surname;
- original three-position tuple;
- shirt number;
- condition, form-state and morale values;
- injury/suspension;
- out-of-contract, transfer-list, loan-list and Wanted states.

No positional label names, status icons, colors, sorting or screen-specific
visibility rules are assigned here.

### Source-backed formation / Team Orders presentation contract

Existing canonical-executable, RTTI and MatchCalculator research now supplies a
bounded tactics-facing presentation contract without inventing the original
screen surface.

For `PFormation2k`, the proven vtable `0x7C1AB4` owns the exact persisted
DBRUser formation region at `+0x70C`, magic `0x074A3216`, with five
`0x1F4` records beginning at `+0x714`. Those records hold formation /
team-sheet names plus current-club player IDs and assigned-role data.

For `PTeamOrders2K`, existing RTTI/source analysis identifies the screen
family in `Applications\\FootballManager\\SquadPan.cpp`, with recorded RTTI
anchors around vtable `0x7C6FE0` / TypeDescriptor `0x81DE68`. Independent
MatchCalculator selectors prove the four ordered categories:

- 0 = captaincy order;
- 1 = penalty-taker order;
- 2 = corner-kick order;
- 3 = free-kick order.

Original English resources independently corroborate those semantics with
`Captains`, `Penalty Takers`, corner-left/right and free-kick-left/right
string families. These strings are corroborating source evidence, **not**
claimed control bindings or screen coordinates.

The immutable contract exposes none of the still-unrecovered original control
IDs, geometry, artwork paths, click/drag behavior or navigation. See
`research/GATE13_TACTICS_PRESENTATION_CONTRACT.md`.

### Tactics/team selection

The bridge also exposes the controlled user's already persisted
`HumanManagerState` selection plus the reconstructed team tactical state:

- formation ID;
- exact starter/substitute player-ID tuples in stored order;
- runtime `TeamTacticalState` fields at the recovered team offsets:
  Play style, Without Ball, With Ball, Aggression;
- the four exact `TeamOrderPriorities` lists: Captain, Penalty,
  Corner and Free Kick.

These are source-backed numeric/runtime values. The bridge deliberately
does **not** assign original tactics-screen control IDs, button captions,
formations graphics, player-slot coordinates, style labels, colors or drag/drop
behavior. Missing tactical state, lineup tuple or one of the four Team Orders
lists fails closed instead of silently injecting modern defaults.

### PTickets source-backed presentation contract and runtime state

The original ticket/stadium research is sufficiently instruction-locked to
expose a bounded Finance-adjacent presentation seam without recreating the
screen.

The immutable contract preserves:

- panel family `PTickets` and update routine `0x45FF10`;
- DBRUser ticket object at `+0x694`, exact size `0x7C`;
- `+0x00` season-ticket quantity, `+0x04` season-ticket price,
  `+0x08` terrace price and `+0x0C` seating price;
- 26 section-state dwords at `+0x14`, with native states
  -1 unavailable / 0 home / 1 visiting / 2 season-ticket reserved;
- terrace recommendation helper `0x461340`, its exact 0.75 reference factor,
  and comparison site `0x4605AD`;
- seating recommendation helper `0x4615B0` and comparison site
  `0x460753`;
- stadium capacity fields `+0x1C` terrace and `+0x28` seating.

`ticket_state_view()` reads the controlled club's already materialized
`TicketRuntimeState` only. Missing state, wrong vector length or an unmapped
section-state value fails closed.

No original PTickets widget IDs, visible captions, coordinates, artwork,
font/color rules or navigation are assigned. See
`research/GATE13_TICKETS_PRESENTATION_CONTRACT.md`.

### Source-backed Finance Overview and Transfer interaction contracts

The bridge now exposes two immutable presentation-facing contracts from
already-persisted canonical-executable research.

For `PFinanceOverview`, the contract retains only the proven Balance/accounting
path for transfer category **1000**:

- credit aggregate `0x5DC890`, called at `0x43E08B`;
- debit aggregate `0x5DD650`, called at `0x43E0DB`;
- net helper `0x43F1E0`, called at `0x43E115`;
- resulting transfer aggregate stored around panel-state anchor `+0xAC0`.

The `+0xAC0` value is deliberately named an **anchor**, because the prior
research says "around +0xAC0" rather than proving an exact C++ member offset.
No localized Finance row caption is guessed. The contract also preserves the
negative result that the dormant chairman budget-event family has no recovered
ordinary fresh-game Finance/Transfer consumer; presentation must not invent a
live budget widget from those legacy messages.

For `PTransfer2K`, the contract retains source-proven EA event identities for
End Negotiations, conclusion, counter-offer, acceptance, rejection, deadline
and insufficient-offer paths, plus the proven CDealInProgress state families
0/3 pending, 1/4 cleared for execution, and 2/5 player-rejected terms. Where
the existing research did not pin an exact vtable (the counter-offer event),
the contract stores no vtable rather than fabricating one.

Neither contract assigns original screen sorting, control IDs, widget
rectangles, art resources, visible caption bindings or navigation. See
`research/GATE13_FINANCE_TRANSFER_PRESENTATION_CONTRACTS.md`.

### Finances and transfer runtime data

The bridge now exposes the already recovered user-owned `Balance` slice
without assigning unresolved EA-facing finance labels:

- current cash;
- ledger postings **in runtime append order**;
- each posting's signed amount, numeric category ID and posting date;
- the three recovered financial-objective candidates plus selected objective,
  start/target values, dates and proven progression fields.

Category IDs stay numeric because several original Finance screen labels are
still unresolved. The bridge does not turn category 1600 or any other account
into a guessed human-facing caption.

For active transfer negotiations, the bridge preserves `TransferRuntimeState`
proposal dictionary insertion order as a **runtime order only**, not a claim
about the original Transfers screen sort. Each row exposes the recovered
proposal/deal structures:

- target player plus buying/selling clubs using source names;
- cash fee and three exchange-player slots;
- still-neutral negotiation bytes `+0x14/+0x15` and prior offer values;
- exact reconstructed contract-term fields/clauses;
- raw DealInProgress state, base state, swap-variant flag and creation date;
- one scheduled MPMTransferPlayer due date/mode when present.

The neutral negotiation bytes remain neutral. Missing DealInProgress identity
or multiple schedule records for the same active proposal fail closed rather
than being silently normalized into a modern UI state.

### Player profile source/runtime projection

The bridge can now project one runtime player into a profile data record using
only already reconstructed fields:

- source first/surname and player/club/nationality IDs;
- date of birth, shirt number, height and weight;
- original three-position tuple;
- the live **17-byte current skill vector** loaded into DBRPlayer/runtime state;
- condition, form state and morale;
- weekly wage and contract-expiry date;
- injury/suspension plus Out of Contract, Transfer Listed, Loan Listed and
  Wanted runtime states;
- current loan-club ID when present.

The backend also carries development-target bytes, peak/development state and
other internal values. Those are intentionally **not** exposed here merely
because they exist in memory: no claim has been made that the original
player-profile UI showed them. Likewise the bridge does not assign the 17 raw
skill bytes to visual columns/icons until original player-profile presentation
evidence establishes that mapping.

### Source-backed manager-mail presentation contract

The bridge now exposes an immutable contract for the manager-mail families that
have already been recovered end-to-end from the original executable and
materialized by the clean-room runtime.

The contract preserves the common `MPMEAMail` queue-container family plus:

- ordinary assistant-manager contract-renewal suggestion:
  message ID `0x0E`, key `AssManSuggestPlayerContractRenewalM`,
  event `EAMAssManSuggestPlayerContractRenewalMsub`, accepted action
  `EAMAmendContractsub`;
- Bosman renewal suggestion:
  message ID `0x1B7`, key
  `AssManSuggestBosmanPlayerContractRenewalM`, event
  `EAMAssManSuggestBosmanPlayerContractRenewalMsub`, accepted action
  `EAMAmendContractsub`;
- low-morale player transfer-list request:
  key `PlayerAskTransferList`, event `EAMPlayerAskTransferListsub`,
  accepted action `EAMAcceptTransferRequestsub`, refused action
  `EAMRefuseTransferRequestsub`.

The existing research does not pin an independent numeric message ID for the
transfer-list request, so the contract stores none rather than inferring one.
It also keeps `global_interleave_proven = False`: the runtime's renewal and
transfer-request queues must not be merged into a guessed inbox order.

No inbox screen ID, row sorting, visual caption binding, row geometry, artwork
or navigation is assigned. See
`research/GATE13_MESSAGES_PRESENTATION_CONTRACT.md`.

### Manager-mail source queues

The bridge now exposes the two manager-mail families that the clean-room
runtime has actually materialized, and keeps them as **separate queues** rather
than inventing a global interleave:

- controlled-player assistant-manager contract-renewal suggestions;
- low-morale `PlayerAskTransferList` requests.

For contract-renewal suggestions the event identity is already source-locked:
ordinary message ID `0x0E`, Bosman message ID `0x1B7`, their original
resource keys/event RTTI class names, and the shared
`EAMAmendContractsub` accepted action. Transfer requests retain the exact
`PlayerAskTransferList` original key, `EAMPlayerAskTransferListsub` event
class and mapped accept/refuse action classes. Queue index and dates are
preserved from runtime storage.

Because `GameState` currently stores these two recovered families in separate
lists, the bridge deliberately does **not** sort them together by date or claim
the complete original Messages/News inbox ordering.

### Source-backed Training.cpp presentation contract

The bridge now exposes immutable training-system metadata from the already
recovered original `Training.cpp` and canonical executable paths.

The contract preserves:

- exactly 40 per-user records of `0xC8` bytes;
- player ID at record `+0x08`;
- embedded training object at record `+0x24`;
- method byte `+0x00`, eight-week countdown dword `+0x04`, active-count
  dword `+0x08`;
- 17 per-skill counters from `+0x0C`;
- 17 paired dword states from `+0x20`;
- seven per-method result counters from `+0x64`;
- fresh defaults method 5 / countdown 8 / active count 0;
- method IDs 0..6 as rest/recovery, attacking, midfield, defensive,
  goalkeeper, fitness and technique, tied to their exact seven profile vectors;
- source update chain `0x42AE40 -> 0x61CBA0 -> 0x61C520 -> 0x4EACE0`
  and daily maintenance `0x61CA60`.

The persisted evidence has not pinned a specific original Training screen RTTI
class, so `screen_class_name` is deliberately `None`. No widget IDs,
visible label bindings, player-row geometry, art resources or navigation are
invented. See `research/GATE13_TRAINING_PRESENTATION_CONTRACT.md`.

### Training source/runtime projection

For each controlled-club player, in live roster order, the bridge exposes the
already mapped embedded training state:

- numeric method ID;
- countdown and active-count values;
- the 17-entry persistent per-skill modifier block;
- the 17-entry skill-state block;
- the seven per-method result counters.

These arrays are exact reconstructed runtime structures. The bridge does not
assign proprietary Training-screen graphics, coordinates, control IDs or any
additional labels beyond semantics already independently recovered. Invalid
array shapes fail closed.

### Source-backed PScouting2K interaction contract

Prior canonical-executable research already identifies the actual scouting panel
class and a bounded interaction/sort contract. Gate 13 now exposes that evidence
as immutable presentation metadata rather than leaving future screen code to
rediscover or guess it:

- class `PScouting2K`, TypeDescriptor `0x81C9C0`, COL
  `0x7E3D20`, vtable `0x7C2E6C`;
- event handler `0x4ADB50`;
- event code **31** dispatches through `0x4AE0FB` into result-vector
  construction at `0x4AE970`;
- panel-state deterministic reseed `0x4AF7F0`;
- exact result-sort comparator modes 0..5 and their native comparator entry
  points.

The contract uses neutral semantic keys such as `history_average` and
`club_display_name` only to identify already recovered comparator inputs.
They are **not** claimed original column captions. No screen ID, control ID,
rectangle, artwork, color, font placement, click target, or navigation edge is
invented. See `research/GATE13_SCOUTING_PRESENTATION_CONTRACT.md`.

### Scouting result projection

The bridge delegates search execution to
`HumanGameplayController.search_scouting_players_mapped()`, the existing
source-backed `PScouting2K` pipeline, instead of reimplementing search logic
inside presentation code.

The caller must still supply the mapped panel state and valuation resolver, and
may supply the same optional source-value resolvers/predicates already accepted
by the backend. Result order is preserved exactly as returned by that pipeline.
Each result exposes source/runtime identity, current 17-byte skill state,
preferred-position tuple, age, exact six-entry-history average, and mapped
Transfer Listed / Out of Contract / Loan Listed state.

An unattached player remains club ID `-1` with **no invented club name**.
The bridge does not manufacture a "Free Agent" club label or substitute a
previous club. Unresolved PScouting2K UI controls remain unresolved rather than
being renamed at the presentation seam.

### Source-backed Fixtures/Results construction contract

The bridge now exposes the recovered fixed-real-fixture backend identity and
construction path as immutable presentation metadata. It records
`DBTRealFixtures` / `DBRRealFixture`, the shipped 380-fixture table at
`Static.dat 0x10057`, the 38-round structure, and the source-order attachment
path through `0x4F72D0`, `0x4F76A4..0x4F770D` and fixed builder
`0x6173D0`.

This contract deliberately separates **backend source order** from the still
unrecovered original Fixtures/Results screen sort. The original screen class,
screen ordering/comparator, row geometry, art and navigation remain unknown.
See `research/GATE13_FIXTURES_PRESENTATION_CONTRACT.md`.

### Fixtures/results

`PremierLeagueState.fixture_source_order` is constructed directly from the
fixture source sequence before the dictionary map is built. The bridge iterates
that exact sequence and exposes each row's source index, reconstructed round
date, clubs and any recorded result.

This is **not a claim that the original Fixtures/Results screen displayed rows
in this exact order**. It is the safest lossless source ordering to hand to the
future original presentation layer until its own comparator/navigation logic is
recovered. The bridge intentionally refuses to substitute an ID/date sort when
`fixture_source_order` is absent.

### Source-backed League-table presentation contract

The bridge now exposes the already recovered native `League::0x4F45E0`
ordering contract as immutable presentation metadata.

The comparator orders rows by:

1. points descending;
2. played ascending;
3. goal difference descending;
4. goals for descending;
5. goals against ascending;
6. original DBRClub short-name **CP1252 bytes** ascending.

The backend `League` vtable anchor is `0x7C9AC0`. The presentation
contract deliberately leaves the actual League-table screen class unknown
because persisted primary evidence identifies the competition backend, not a
specific presentation panel.

Numeric ties require strict source short-name bytes before the bridge may call
the result original ordering. If every recovered comparator field is identical,
the original CRT qsort's relative ordering remains unproven and the contract
records that explicitly instead of inventing a stable tie-breaker.

No original table column geometry, header captions, art resources, control IDs
or navigation are assigned. See
`research/GATE13_LEAGUE_TABLE_PRESENTATION_CONTRACT.md`.

### League table

`GameState.premier_league_table()` now uses the firsthand recovered
`League::0x4F45E0` order whenever all original CP1252 club short-name bytes
are available:

1. points descending;
2. played ascending;
3. goal difference descending;
4. goals for descending;
5. goals against ascending;
6. original short-name bytes ascending.

The bridge **does not sort table rows again**. It preserves the backend result
and only attaches source club names plus one-based display position. Therefore
future original presentation cannot accidentally regress to generic club-ID or
Unicode ordering at this seam.

See `research/GATE13_SOURCE_LEAGUE_COMPARATOR.md` for the comparator evidence
and remaining native equal-key qsort boundary.

## Temporary prototype integration boundary

The existing Tk `reconstruction/app.py` remains a **development prototype**,
not the Gate-13 fidelity target. Its Play tab previously read
`controller.state` and `controller.human` directly for roster/table/tactics
and pending-fixture display, which weakened the presentation/simulation seam
even though the backend logic itself was already separated.

The prototype now routes those presentation reads through
`ManagementSourceDataBridge`:

- controlled-club header/date;
- roster rows and source-backed match-availability/current-position state;
- league table;
- persisted formation/tactics/selection;
- pending fixture source names/date.

Controller calls remain only for intended commands/actions such as selecting a
club, setting lineup/tactics, advancing to a fixture, playing a match, and
save/load orchestration. This does **not** make the Tk prototype an original
FM2001 UI; it prevents that temporary surface from becoming an alternate
simulation reader while the authentic resource-driven presentation is built.

`test_app_presentation_boundary.py` rejects future direct Play-surface reads
through `controller.state`, `controller.human`,
`self.gameplay.state` or `self.gameplay.human`, and focused Gate13 CI also
compiles the prototype after boundary changes.

## Architectural boundary

The bridge never:

- advances the calendar;
- simulates a fixture;
- changes team selection or tactics;
- executes transfers;
- edits player/finance state;
- guesses a management-screen control ID;
- invents original visual geometry or labels.

This is specifically progress toward Gate 13's requirement that simulation
logic stay separated from presentation code.

## Verification

`reconstruction/test_gate13_management_source_data.py` uses a synthetic
backend contract to lock:

`reconstruction/test_app_presentation_boundary.py` separately locks the
temporary Play UI behind this read seam so future prototype changes cannot
silently reintroduce direct simulation-state reads.


- controlled-club source names/date;
- live source-roster ordering;
- exact persisted human formation, starter/bench ordering, four runtime tactical
  bytes and all four original Team Orders priority lists;
- player-profile source identity, current 17-byte runtime skill state,
  contract/status fields, and explicit exclusion of unsupported target values;
- Balance current cash, ledger append order, financial-objective runtime state;
- active TransferProposal/DealInProgress/ContractTerms records and unambiguous
  scheduled-transfer metadata without naming unresolved negotiation bytes;
- exact recovered renewal/transfer-request event identities while preserving
  their separate runtime queues;
- controlled-squad training method/countdown plus exact 17/17/7 state-array
  shapes in roster order;
- mapped PScouting2K result delegation/order and unattached-player neutrality;
- fixture source insertion order even when fixture IDs/dates could tempt a
  modern resort;
- recorded/unplayed result projection;
- preservation of the already-sorted backend league table;
- neutral recovered player-state fields;
- fail-closed behavior when source names, human control or fixture-source order
  are unavailable.

Hosted CI validates only this read-only plumbing. It cannot establish original
screen pixels or native FM2001 management-screen ordering.

## Remaining Gate 13 work

The primary critical path remains unchanged:

1. restore private byte execution;
2. run the hash-gated original Button RTTI trace with the known-positive
   TeamSelect calibration;
3. prove the original action-atlas frame states and Zurich caption rendering;
4. execute the strict ten-resource original-source byte/pixel audit;
5. provenance-import only proven source assets;
6. complete authentic PStartMenu/TeamSelect and then manager-home, squad,
   tactics, fixtures/results, league table, player profile, transfers,
   finances, messages/news, training/scouting and remaining original screens.
   The read-only data seams for these areas do not substitute for recovering
   their original presentation/navigation;
7. audit Gate 13 before advancing to Gate 14.

This bridge supplies source-faithful management data to those future screens;
it does not substitute for them.
