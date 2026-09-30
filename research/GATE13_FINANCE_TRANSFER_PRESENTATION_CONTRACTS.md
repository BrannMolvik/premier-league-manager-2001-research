# Gate 13 Finance Overview and Transfer Presentation Contracts

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes already recovered presentation-facing facts for
`PFinanceOverview` and `PTransfer2K` into the same read-only Gate-13 bridge
used by other management screens. It does not reconstruct either screen.

## PFinanceOverview transfer-account path

Canonical executable research proves that Finance Overview directly queries
accounting category **1000** through the Balance aggregate family:

| Role | Finance Overview call site | Helper |
| --- | ---: | ---: |
| credit/income-side aggregate | `0x43E08B` | `0x5DC890` |
| debit/outflow-side aggregate | `0x43E0DB` | `0x5DD650` |
| net aggregate | `0x43E115` | `0x43F1E0` |

The resulting category-1000 values are stored around Finance Overview panel
state `+0xAC0` and rendered through corresponding row widgets. The prior
research explicitly says **around** `+0xAC0`, so the contract records this as
a panel-state anchor, not an exact recovered member offset.

Gate-10 finance work independently proves category 1000 is the live transfer
accounting category.

The exact EA-authored visible row caption remains unresolved. The contract
therefore exposes the numeric category and helper identities, not a guessed
label such as "Transfers".

## Finance budget-event boundary

The executable also contains chairman/Business Consultant budget event families
with formatted Staff, Wage, Maintenance, Building and Transfer budget values.
However, exhaustive fresh-game reachability work found no ordinary static
producer/consumer path that makes those legacy budget events a live mutable
Finance/Transfer screen store. Normal `PFinanceOverview` is Balance/accounting
ledger-driven, and `PTransfer2K` has no references to those dormant tuning
globals/events/formatter keys.

The presentation contract keeps this negative fact explicit:
`dormant_budget_event_live_consumer_proven = False`.

This prevents future UI work from fabricating a modern "transfer budget" widget
that the recovered ordinary shipped path does not support.

## PTransfer2K interaction event identities

Existing RTTI and event-path analysis proves these source identities:

| Semantic role | EA class | Vtable | Player response code |
| --- | --- | ---: | ---: |
| end negotiations | `EAMTPUserEndNegotiationssub` | `0x7C8F50` | - |
| confirm conclude transfer | `EAMConfirmConcludeTransferDealsub` | `0x7C9008` | - |
| transfer deal concluded | `EAMTransferDealConcludedsub` | `0x7C8FAC` | - |
| player counter-offer | `EAMTransferUserPlayerCounterOfferMsub` | unresolved in persisted notes | 1 |
| player accepts terms | `EAMTransferPlayerAcceptsMsub` | `0x7C8EFC` | 2 |
| player rejects terms | `EAMTPUserPlayerRejectsMsub` | `0x7C8AB8` | 3 |
| deadline passed | `EAMEndNegotiationsTransferDeadLinePassed` | `0x7CE3CC` | - |
| offer not enough | `EAMTPUserEndNegotiationsOfferNotEnoughM` | `0x7D5C38` | - |

The counter-offer contract intentionally stores no vtable because the existing
persisted analysis proves the class/response mapping but does not pin an exact
vtable in the canonical notes used for this checkpoint.

## Deal-state families

`MPMTryExecuteTransfer` and the event factory establish three state families:

- **0 / 3**: pending or unresolved;
- **1 / 4**: resolved/cleared for execution;
- **2 / 5**: player rejected/declined contract terms.

The +3 variant marks the swap/player-exchange family.

These are source-backed lifecycle semantics, not modern UI statuses. Future
Transfer presentation may consume them, but must still recover the original
screen ordering, captions, row/control bindings and navigation separately.

## Explicit non-claims

The new contracts contain no:

- original Finance/Transfer screen IDs beyond recovered panel family names;
- localized Finance category-1000 row caption;
- transfer-list sorting claim;
- control/widget IDs;
- row/button rectangles;
- artwork/resource paths;
- font/color/alignment rules;
- navigation edges.

Those remain Gate-13 work.

## Gate 13 consequence

Finance Overview now has one source-proven presentation aggregate path instead
of only generic runtime ledger data, and Transfers now has its proven original
interaction-event/deal-state vocabulary attached to the presentation seam.
Their original visual resources/layout/navigation remain open.
