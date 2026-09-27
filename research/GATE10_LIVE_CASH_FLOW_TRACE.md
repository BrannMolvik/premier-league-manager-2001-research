# Gate 10 Live Cash-Flow Trace

_Last reconciled: 28 September 2026_

This note records the exact implementation boundary for the Gate-10 task:
recover ordinary live income/cost producers without inventing finance behavior.

Baseline when this trace was reconciled:

```text
c67c7db6ccb2e16e461d53855be413ec73260599
Advance Gate 10 after verified payroll integration
```

The last code checkpoint remains `5dc29a072d6e4f91744b882251df16f980c82f55`,
where the reconstruction suite passed 497 tests and the asset-policy workflow
passed.

## Already integrated

The modern runtime currently has:

- explicit Balance/current cash;
- persisted finance ledger state;
- transfer buyer debit and seller credit through category 1000;
- controlled-club transfer affordability against live current cash;
- recovered Saturday player payroll through category 101;
- the first-of-month support-staff category/cadence recovered as category 102,
  with concrete amounts deliberately deferred because CSupportStaff cost state
  is not materialized.

## Concession payout path: exact but dormant on the ordinary fresh-game path

Fresh instruction-level recovery against the canonical executable
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`
corrects the earlier description of concessions as an ordinary recurring
producer.

The payout path itself is exact:

`0x42A9FD -> 0x5E5640 -> 0x5E56F0 -> Balance 0x5DC510`

### Exact amount, category, and cadence

`0x5E56F0` computes the selected 0x168-byte record address and returns the
qword at record `+0x160` as a floating-point value.

`0x5E5640`:

- exits when the concession object's active-record count at `+0x00` is zero;
- decodes the current serial date through `0x64CCD0`;
- continues only when decoded day-of-month is **1**;
- loops records `0 .. count-1`;
- wraps each record's `+0x160` value through `0x5E43B0` with accounting
  category **0x12C = 300** and conversion flag 0;
- credits the active Balance through `0x5DC510`.

Thus the exact dormant posting is:

`first day of month -> each active record's +0x160 double -> category 300 -> Balance credit`.

### Why this is not an ordinary fresh-game income source

The same executable also proves that the ordinary new-game path does not
activate those records:

- concession-object construction initializes active count `+0x00 = 0`;
- each record initializes `+0x160/+0x164` to the all-ones sentinel;
- `0x5E5330`, the only periodic offer generator called from the DBRUser path,
  builds a complete 0x168-byte candidate record **on the stack**;
- that candidate receives its generated financial offer at record `+0x158`
  and an expiry/date value at `+0x164`;
- the routine never copies the candidate into the persistent +0x690 object and
  never increments its active-record count;
- the separate `0x5E5710` pass likewise walks active records and decodes dates
  without mutating the active set;
- a complete direct-reference scan of DBRUser `+0x690` found construction,
  save/load, the periodic payout/generator calls, and the date pass, but no
  ordinary record-activation writer.

Persisted save data can still contain nonzero records because save/load
serializes the count and active records. The executable therefore contains a
valid payout mechanism for such state, but the currently recovered fresh-game
path does not create that state.

Do **not** integrate category-300 concession income into normal calendar
progression as though fresh games generate it. Treat this as a dormant/legacy
payout path unless a genuine activation writer is later recovered.

## Match-day gate-receipt producer recovered

A complete Balance-credit call-site scan found the actual live match-day
producer outside the earlier monthly/history address family:

`0x513252 -> 0x5DA2F0 -> Balance 0x5DC510`.

The earlier `0x429904/0x429BB4/0x42A111/0x42A5D2/0x42C1F2`
family remains relevant to business/history reporting, but it is not the
primary gate-receipt posting path.

### Accounting categories and ticket-price inputs

Inside `0x5DA2F0`, the active controlled user's DBRUser `+0x694`
ticket/section state supplies the two dword ticket prices at `+0x08` and
`+0x0C`. They are converted to floating point and combined with two pairs of
attendance/count values.

The first posting has the exact shape:

`double(price_08) * count_A0 + double(price_0C) * count_A1`

and is credited as accounting category **1** at `0x5DB456`.

The second posting has the same two-price shape with a second attendance/count
pair:

`double(price_08) * count_B0 + double(price_0C) * count_B1`

and is credited as accounting category **2** at `0x5DB4B9`.

Equivalent controlled-club posting branches occur at
`0x5DB58D/0x5DB5F0` and `0x5DB692/0x5DB6F5`.

The exact user-facing distinction between categories 1 and 2, and between the
two `+0x08/+0x0C` price types, is not yet named. Their role as live
match-ticket receipts is independently locked by the ledger family below.

### Gate-receipt ledger family

Balance aggregate helper `0x5DC890` expands high-level accounting category
**0** into the exact sum of subcategories **1, 2, and 3**. Finance Overview
queries that high-level category-0 aggregate.

Category **3** is independently produced by the ticket/season-ticket path at
`0x5D0FF4` and `0x5D1684`: it multiplies a selected ticket quantity by
its selected ticket price, passes category 3 through the normal finance-value
constructor, and credits Balance.

Together, these instruction paths establish:

- high-level category **0** = the gate/ticket-receipt family;
- categories **1 and 2** = live match-day ticket receipt components;
- category **3** = the separate pre-match/season-ticket sales component.

This is stronger evidence than the separate `EAMbcmonthlyincome` label
`GATE`, although that presentation label is consistent with it.

### Stadium/section dependency is also confirmed

The producer directly consumes the state previously identified as the missing
runtime dependency:

- DBRUser `+0x694`: ticket prices plus 26 section-state dwords at
  `+0x14..+0x78`;
- DBRUser `+0x6B0`: the loaded stadium/entry model.

In particular, helper `0x618E00` loops the 26 section entries, filters them by
section selector 0 or 1, and sums capacity-like stadium-entry dimensions after
conversion through `0x4290A0`. `0x5DA2F0` also calls stadium helpers
including `0x65D920`, `0x65DA60`, and `0x65D9B0`.

Therefore the modern runtime still cannot faithfully post gate receipts merely
from a club stadium string or unmapped `DBTAccessFanBase` fields. The
original ticket-section/stadium state must be materialized or equivalently
reconstructed from the authorized stadium data.

### Applicability boundary: cup/knockout branch confirmed

The ordinary branch credits categories 1 and 2 when the primary club is
user-controlled. The special flag set at `0x5DA705` is now tied directly to
the cup/knockout attendance branch rather than an unnamed generic match flag.

The branch at `0x5DA5CF..0x5DA744` consumes the executable's explicit
attendance tuning globals:

- `ATTCupFianlBoost` -> `0x821088` (spelling preserved from the binary);
- `ATTCupSemiFinalBoost` -> `0x82108C`;
- `ATTCupQuarterFinalBoot` -> `0x821090` (spelling preserved);
- `ATTCupDiv` -> `0x821094`.

It selects the final/semi-final/quarter-final factor from the cup round
relationship and then normalizes by `ATTCupDiv`. In this same branch the
special posting flag is set to 1. Later posting logic can independently credit
categories 1 and 2 to both controlled participants, each using that user's own
ticket prices.

This proves the special branch is a **cup/knockout attendance path**. It does
not, by itself, prove a user-facing policy label such as "revenue sharing" or
"neutral-ground receipts", so those labels remain deliberately unassigned.

### Ticket-state header refinement

The ticket object at DBRUser `+0x694` now has a stronger header map:

- `+0x00` = season-ticket quantity;
- `+0x04` = season-ticket price;
- `+0x08` and `+0x0C` = the two ordinary match-day ticket prices;
- `+0x14..+0x78` = 26 per-section allocation/classification dwords.

The category-3 producer at `0x5D0E20..0x5D0FF4` obtains a season-ticket
quantity, stores it at `+0x00`, stores the chosen season-ticket price at
`+0x04`, and credits exactly:

`double(+0x00 quantity * +0x04 price)`

as category **3**.

Helper `0x618820`, called from the same season-ticket workflow, marks selected
stadium sections with state **2** until the required season-ticket capacity is
covered. Therefore section state 2 is the season-ticket-reserved allocation,
while states 0 and 1 are the two ordinary match-day section classes.

The shipped English string table independently contains the exact finance/help
labels "Year to date home fan ticket sales", "Year to date visiting fan ticket
sales", "Year to date season ticket sales", "Terraces", "Recommended terrace
ticket price", "Seating places available", and "Recommended seat ticket price".
These are strong semantic leads, but the exact mapping of category 1 versus 2
and `+0x08` versus `+0x0C` is still being instruction-locked rather than
assigned from string order alone.


### Home/visiting split and section-state allocation

The supporter-side split is now instruction-locked strongly enough to name the
two accounting subcategories.

At the end of `0x5DA2F0`:

- category **1** uses the count pair later stored as the non-season-ticket
  supporter group;
- category **2** uses the second count pair;
- after both match-day postings are complete, the controlled primary club's
  season-ticket quantity from `DBRUser +0x694 +0x00` is added **only** to the
  category-2 count group before attendance output is written;
- output `+0xD84` receives the combined attendance total;
- output `+0xD8C` receives the category-2/home-side attendance group,
  including season-ticket holders;
- output `+0xD90` receives the category-1/visiting-side attendance group.

This cleanly separates revenue from attendance: category 2 is ordinary **home
supporter match-day ticket sales**, category 1 is ordinary **visiting supporter
match-day ticket sales**, and category 3 remains season-ticket sales. Season
tickets increase the home attendance count but are not double-counted in the
category-2 revenue posting.

The section allocator independently supports the same home/visiting split.
`0x618A20` first clears every section state 1 back to 0, skips unavailable
and season-ticket-reserved (state 2) sections, and then marks sections state 1
until accumulated ordinary capacity reaches:

`10 * floor(club_stadium_capacity / 100)`

places. `0x618B60(ticket_state, 1)` enforces the same minimum when the user
tries to reassign sections in the ticket screen. State **1** is therefore the
mandatory visiting/away-supporter allocation; state **0** is the remaining
ordinary home-supporter allocation; state **2** is the already-proven
season-ticket allocation; `-1` is unavailable/disabled section state.

The two match-day price classes are also structurally paired with distinct
stadium-entry capacity fields:

- `DBRUser +0x694 +0x08` is paired with stadium-entry field `+0x1C`
  through the `0x65DA60/0x65DAB0` family;
- `DBRUser +0x694 +0x0C` is paired with stadium-entry field `+0x28`
  through the `0x65D9B0/0x65DA00` family.

The remaining label question is now only which of entry `+0x1C` and
`+0x28` is terrace versus seating. Do not infer that last mapping from UI
layout alone.

### Terrace/seating ticket class resolved

The final physical ticket-class ambiguity is now instruction-locked against the
canonical executable rather than inferred from UI order.

The ticket panel update routine at `0x45FF10` computes two recommended match-day
prices from the same league/division base-price path:

- `0x461340` applies an additional multiply by `0x7BD558 == 0.75` before
  the final rounding path;
- `0x4615B0` uses the same base-price selection without that 25% reduction.

The resulting values are kept separately by the ticket panel. The live ticket
price at `DBRUser +0x694 +0x08` is displayed and compared at `0x460553 /
0x4605AD` against the **0.75-discounted** `0x461340` recommendation. The
price at `+0x0C` is displayed and compared at `0x4606F9 / 0x460753`
against the **undiscounted** `0x4615B0` recommendation.

This identifies the ordinary prices exactly:

- `DBRUser +0x694 +0x08` = **terrace ticket price**;
- `DBRUser +0x694 +0x0C` = **seating ticket price**.

The already-proven receipt/helper pairing therefore resolves the stadium-entry
capacity fields too:

- stadium entry `+0x1C` = **terrace capacity/class**;
- stadium entry `+0x28` = **seating capacity/class**.

This is independently consistent with `0x618C10`, which accumulates each of
those two physical capacity fields separately for section state 0 and state 1.
The section-state dimension is therefore supporter allocation (home/visiting),
while `+0x1C/+0x28` is the terrace/seating dimension.

### Remaining formula work

The producer, supporter-side categories and section ownership are now known,
but implementation remains intentionally blocked until these details are
closed:

1. finish translating the two parallel attendance-demand calculations and their
   caps/randomized rounding;
2. tie stadium-entry fields `+0x1C/+0x28`, and therefore ticket prices
   `+0x08/+0x0C`, exactly to terrace versus seating;
3. preserve the exact integer/floating conversion and rounding path;
4. materialize only the required stadium/section source state and add
   deterministic finance regressions before normal matchday integration.

## Monthly income report is not a producer

`EAMbcmonthlyincome` exposes EA-authored field labels:

- `+0x3C` = GATE
- `+0x40` = MERCH
- `+0x44` = CONC
- `+0x48` = ADVERTS
- `+0x4C` = SPONSOR
- `+0x50` = TELLY
- `+0x54` = TRANSFERFEES

These labels are useful semantic evidence, but the event is a
reporting/presentation object. They do not by themselves establish the
accounting categories or formulas used by the live producers.

## Other recovered recurring-income owners

The following original state is identified but is not yet an implementable
income posting:

- `DBRUser +0x588..+0x5A8`: radio/TV/European media-rights/reserve values,
  initialized from the LRADIO/NRADIO/LTV/NTV/EUROPEAN MAX/RES tuning family;
- `DBRUser +0x69C`: sponsor-offer/sponsor-state scheduling, driven by
  `FSNoSponsorMinWait`, `FSNoSponsorMaxWait`,
  `FSHaveSponsorMinWait`, and `FSHaveSponsorMaxWait`.

Neither path currently has a persisted instruction-level bridge from those
values to an exact Balance posting amount/category.

## Balance-credit fidelity issue to preserve

The original `Balance::credit` path at `0x5DC510` also constructs a
secondary debit with accounting category 1600. The recovered amount is:

```text
incoming_amount * 0.01 * 0.2
= incoming_amount * 0.002
```

The category's user-facing semantic label and the exact integer/conversion
behavior are not yet proven. The clean-room `BalanceRuntimeState.credit()`
currently only records the primary credit.

Do not silently add a guessed rounded/truncated category-1600 debit. Recover the
conversion behavior first, then add a regression that covers an amount where
rounding matters.

## Exact next binary-backed trace

Do not restart the already-closed producer search. Continue inside
`0x5DA2F0` from the current instruction map:

1. finish the two parallel supporter-demand calculations that produce the four
   terrace/seating-by-home/visiting count components;
2. resolve stadium-entry field `+0x1C` versus `+0x28` as terrace versus
   seating and thereby name DBRUser ticket prices `+0x08/+0x0C`;
3. preserve the exact caps, floating-point conversions, `0x668350` rounding
   calls and `0x64D540` randomized subtraction behavior;
4. identify the minimum original stadium source data needed to materialize
   `+0x694/+0x6B0` state in the clean-room runtime;
5. add deterministic finance regressions before normal match-day integration.

Concession generation remains intentionally disabled on fresh games for the
separate dormant-path reason documented above.
