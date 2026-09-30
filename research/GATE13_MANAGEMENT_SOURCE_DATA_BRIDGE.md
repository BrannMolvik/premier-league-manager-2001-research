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
