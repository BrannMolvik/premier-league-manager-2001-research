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

### Exact four-way attendance demand and stochastic integerization

The body of the gate-receipt attendance calculation is now instruction-locked.
The function maintains four ordinary-supporter capacities, one for each
supporter side and physical ticket class:

- home seating;
- visiting seating;
- home terrace;
- visiting terrace.

For a controlled club those capacities are derived from the original 26-section
allocation through `0x618E00` and the stadium helpers. For the direct stadium
path the same four values correspond to state-0/state-1 splits of stadium-entry
`+0x28` seating and `+0x1C` terrace. This independently agrees with the
resolved ticket-class mapping.

#### Reference ticket prices and price response

`0x40CBC0` selects the competition/division reference ticket price. Its first
output is the seating reference; its second output is exactly 75% of that
amount, the terrace reference. Controlled clubs compare their live ticket
prices with those converted references:

- seating delta = `ticket +0x0C - seating_reference`;
- terrace delta = `ticket +0x08 - terrace_reference`.

Price-response helper `0x5DA250(delta, reference)` is piecewise. With
`a = delta` and `b = reference`:

```text
if a > b:             p = 0.1
else if a > 0:        p = max(0.1, 1 - a / b)
else if a > -0.5*b:   p = 1 - a / (2*b)
else if a > -b:       p = 1.5 - a / (4*b)
else:                  p = 2.0
```

The threshold discontinuities are preserved as executable behavior rather than
smoothed into a modern pricing curve.

#### Demand body and caps

Club field `+0x70` indexes the 84-byte AccessFanBase runtime table. Entry
`+0x08` supplies the raw fan-base scalar used by this calculation. A separate
indexed factor selects one of `0.9, 0.8, 0.7, 0.6, 0.5` (with later/default
cases also 0.5). Its higher-level semantic label remains deliberately open.
Call that selected value `tier_factor` and the side-specific upstream
attendance value `side_modifier`.

Before capping, each of the four class/side demands has the common shape:

```text
weighted_fan_base = fan_base_raw * tier_factor

demand = weighted_fan_base
       * (2.0 - tier_factor)
       * side_modifier
       * price_response
```

For a controlled club, `0x42B0E0` additionally multiplies this by the exact
stadium/facility attendance factor. That helper starts at 0.9 and adds the
recovered Hotel, Club House and Parking attendance bonuses when those club
buildings are present.

The demand is then capped in this order:

1. outside the special cup/knockout branch, no higher than
   `fan_base_raw`;
2. always no higher than the allocated capacity for that exact
   home/visiting × terrace/seating cell.

Thus the four floating outputs are home seating, visiting seating, home terrace
and visiting terrace demand. No generic replacement attendance model is needed
for this body.

#### Exact conversion and random subtraction

Helper `0x668350` changes the x87 control word to round toward zero and uses
`fistp`; its conversions are therefore **truncation toward zero**, not ordinary
round-to-nearest.

The RNG used by `0x64D540` is the game's MSVC-style 15-bit stream:

```text
seed = seed * 0x343FD + 0x269EC3
rand15 = (seed >> 16) & 0x7FFF
```

For positive integer `n`, `0x64D540(n)` returns exactly:

```text
floor(rand15 * n / 32768)
```

For every one of the four capped floating demands, the executable derives the
random-subtraction span from the already-computed price response `p`:

```text
if p > 1.0:
    span_float = demand / (100 + 1000 * (p - 1))
else:
    span_float = demand * 0.01

span = max(1, trunc_toward_zero(span_float))
base_count = trunc_toward_zero(demand)
count = base_count - floor(rand15 * span / 32768)
```

The four integer counts are then summed as:

- ordinary home attendance = home terrace + home seating;
- visiting attendance = visiting terrace + visiting seating.

Season-ticket quantity is added to the home attendance only after ordinary
home ticket revenue has been calculated, preserving the already-proven category
2/category 3 separation.

The class-demand body and its exact stochastic integerization are therefore
closed. The remaining attendance-formula dependency is upstream: translate the
side-modifier producers `0x5DBA60` (ordinary competition path) and
`0x5DBCD0` (the alternate type-6 paired path) sufficiently to reproduce their
inputs without semantic invention.

### Upstream side modifiers resolved

The two remaining attendance modifiers are now translated instruction-for-
instruction. This closes the formula dependency that remained above the
four-cell home/visiting × terrace/seating demand body.

#### Ordinary league path: `0x5DBA60(club, match)`

The match supplies its league/competition object at `match +0x4C`. The helper
first sorts/refreshes the league table as required and finds the supplied club's
current league-table index.

The following components are then calculated.

**League-importance factor.** `0x4FA670` resolves the league's country/region
object and returns:

```text
league_importance = 1.0 - signed_integer_division(
    country_competition_list[0].order_value - league.order_value,
    country_competition_count
)
```

The referenced order field is runtime competition `+0x18`; the country list is
at `+0x48` with count at `+0x4C`. The integer division occurs before the
conversion to floating point.

**League-position factor.** For the selected table row:

```text
games_played    = row +0x10
games_remaining = league +0x5C - games_played

if games_remaining < 4 or games_played < 5:
    league_position = 1.0
else:
    league_position = 1.0 - table_index / league_team_count
```

Thus position is deliberately neutral during the first four played matches and
again for the final three remaining matches.

**End-of-season opportunity factor.** This begins at 0. It is considered only
when:

```text
games_remaining < ATTLeagueEndPlay
```

(default 5).

`0x4F8C50` derives five flag/gap pairs from the current sorted table. Points are
exactly `3*wins + draws`. Its four competition-boundary counts correspond to
direct promotion, promotion playoff, direct relegation, and relegation playoff.
The five candidate gaps are, in order:

1. win/title gap when no direct-promotion boundary exists;
2. direct-promotion gap;
3. promotion-playoff gap;
4. direct-relegation/safety gap;
5. relegation-playoff/safety gap.

A candidate is accepted only when its flag is present, its points gap is
positive, and:

```text
gap / games_remaining <= 3.0
```

The first accepted candidate supplies:

```text
win/title          -> 1.0
direct promotion   -> ATTLeagueEndPlayCanGoUp        / ATTLeagueEndPlayCanWin
promotion playoff  -> ATTLeagueEndPlayCanPlayOffUp   / ATTLeagueEndPlayCanWin
direct relegation  -> ATTLeagueEndPlayCanGoDw        / ATTLeagueEndPlayCanWin
relegation playoff -> ATTLeagueEndPlayCanPlayOffDw   / ATTLeagueEndPlayCanWin
```

With shipped defaults these are respectively `1.0, 0.8, 0.6, 0.3, 0.2`.

**Starting-XI rating factor.** When the club roster is present, the helper walks
exactly the first 11 player IDs at club `+0x244`. For each player,
`0x41E1D0` returns the maximum overall rating across the player's three
preferred-role entries. The 11 values are summed and scaled by the exact double
constant `0.00125`:

```text
xi_rating = sum(first_11_overall_ratings) * 0.00125
          = sum(first_11_overall_ratings) / 800
```

Finally `0x5DBA60` returns the weighted average:

```text
numerator = ATTPrestigeBoost        * xi_rating
          + ATTLeagueEndPlayBoost  * end_play_factor
          + ATTLeaguePosBoost      * league_position
          + ATTLeagueImportanceBoost * league_importance

denominator = ATTPrestigeBoost
            + ATTLeagueEndPlayBoost
            + ATTLeaguePosBoost
            + ATTLeagueImportanceBoost

side_modifier = numerator / denominator
```

The shipped defaults are 10 for all four weights.

#### Alternate type-6 path: `0x5DBCD0(primary_club, other_club)`

This path has no league-position/end-play/importance terms. It computes the same
11-player `sum/800` rating factor for each club and returns:

```text
side_modifier = 0.2 * (
    ATTPrestigeBoost      * primary_xi_rating
  + ATTOtherPrestigeBoost * other_xi_rating
) / (ATTPrestigeBoost + ATTOtherPrestigeBoost)
```

The shipped defaults are `ATTPrestigeBoost=10` and
`ATTOtherPrestigeBoost=5`, so the primary side is weighted 2:1 over its
opponent before the final exact `0.2` multiplier. The caller invokes this
helper in both argument orders to obtain one modifier per side.

#### Tuning identities used by the side-modifier path

The executable's named tuning loader maps the relevant globals exactly:

- `ATTLeagueImportanceBoost = 10`;
- `ATTLeaguePosBoost = 10`;
- `ATTLeagueEndPlayBoost = 10`;
- `ATTPrestigeBoost = 10`;
- `ATTOtherPrestigeBoost = 5`;
- `ATTLeagueEndPlay = 5`;
- `ATTLeagueEndPlayCanWin = 10`;
- `ATTLeagueEndPlayCanGoUp = 8`;
- `ATTLeagueEndPlayCanPlayOffUp = 6`;
- `ATTLeagueEndPlayCanGoDw = 3`;
- `ATTLeagueEndPlayCanPlayOffDw = 2`.

The live attendance producer is therefore formula-complete at the instruction
level. The next Gate-10 dependency is no longer attendance algebra; it is
materializing the minimum original-compatible ticket/section and stadium state
needed to feed that formula in the modern runtime.



### Fresh ordinary ticket-price initialization resolved

The final fresh-state ambiguity for ordinary terrace/seating prices is resolved
at `0x5DE160`.

The 0x7C ticket object is created with both ordinary price fields zero. The
original runtime initializes them lazily from a match/business path rather than
hard-coding them in the object constructor. `0x5DE160` obtains the already-
recovered competition reference prices through `0x40CBC0`:

- first output = seating reference;
- second output = exact `0.75 * seating` terrace reference.

Both values pass through the normal finance/money conversion path
`0x5E43B0 -> 0x5E48D0`. The routine then ranks the club's `DBRClub +0x70`
fan-base/access index against the other clubs in its league. Helper `0x4F40E0`
returns the count of league clubs whose own `+0x70` value is less than or equal
to the target club's value. With league team count `N` and this count `r`, the
reference price multiplier is exactly:

```text
if r <= floor(N / 2):
    multiplier = 0.90
elif r < N - 5:
    multiplier = 0.95
else:
    multiplier = 1.00
```

The constants are literal doubles in the executable: 90.0 / 95.0 multiplied by
0.01 on the discounted branches.

After the multiplier, x87 helper `0x668350` performs the already-proven
truncation toward zero. The routine writes:

- seating result -> ticket `+0x0C` **only if +0x0C is zero**;
- terrace result -> ticket `+0x08` **only if +0x08 is zero**.

Existing nonzero prices therefore survive later calls unchanged. This closes
the fresh ordinary ticket-price state needed by the Gate-10 producer.



### Premier League FanFactor resolved

The previously neutral `tier_factor` is selected from the named
`FanFactor1..FanFactor5` tuning family by the competition's index in its
country/region root-competition array. `0x410FF0` returns that stored-array
index; indices 0..3 select 0.9/0.8/0.7/0.6, while index 4 and later/default use
0.5.

England's recovered root order places Premier League competition 0 at index 6,
so normal Premier League gate demand uses exact `tier_factor = 0.5`.

### Normal Premier League integration closed

The minimum normal Premier League gate path is now integrated and regression
tested.

Additional instruction-level inputs closed during integration:

- `EPBase` loads as exact double **30.0**. For Premier League competition 0,
  `0x40CBC0` therefore supplies **30.0 seating** and exact **22.5 terrace**
  reference prices.
- Controlled-club facility helper `0x42B0E0` begins at **0.90** and adds:
  - `0.08 * (hotel_level + 1)` when Hotel exists;
  - `0.04 * (club_house_level + 1)` when Club House exists;
  - `0.05 * (parking_level + 1)` when Parking exists.
  The fresh `DBRUser +0x65C` facility collection starts empty, so a fresh
  controlled club uses exactly **0.90** until later building gameplay creates
  those facilities.
- `0x513252 -> 0x5DA2F0` executes after MatchCalculator has finished and
  before LeagueMatch virtual `+0x3C -> 0x5132E0 -> 0x511370`, which reaches
  `0x5127A0` incident persistence and the later Form pass. Thus the four gate
  RNG draws occur **after match calculation but before red-card, persistent
  injury, and Form RNG**.
- That call is part of the normal LeagueMatch path itself. Every ordinary league
  fixture consumes the four gate draws even when no controlled Balance receives
  a category-1/2 posting.

The modern Premier League path now snapshots the table/selected-XI inputs before
the result mutates league state, simulates the match, consumes four 15-bit draws
in exact home-seating / visiting-seating / home-terrace / visiting-terrace
order, then performs any materialized category-1/2 posting before incident/Form
persistence.

GitHub Actions at `0d3010df0dbbb60ab147d40dedd1ad83ff533965` passed
**531 reconstruction tests** and the repository asset-policy workflow.

For normal Premier League play, the remaining Gate-10 work is therefore no
longer gate-receipt algebra or RNG placement. Broader finance fidelity remains,
including Balance credit's secondary category-1600 debit and later facility
upgrades beyond the exact fresh-game 0.90 baseline.

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

## Balance-credit category-1600 secondary debit resolved

The original `Balance::credit` path at `0x5DC510` constructs a second
finance posting for every incoming credit.

Instruction order is exact:

1. convert the incoming finance value to a double through `0x5E48D0` with
   conversion argument 0;
2. add the full incoming amount to Balance current cash;
3. multiply that same double by literal `0.01`;
4. multiply by literal `0.2`;
5. construct a second finance value from that floating result through
   `0x5E43B0` with conversion flags zero;
6. invoke `Balance::debit 0x5DC650` with accounting category **1600** and
   flag **1**;
7. append the original primary-credit transaction.

Thus the exact secondary amount is:

```text
incoming_amount * 0.01 * 0.2
= incoming_amount * 0.002
```

There is **no integer conversion or x87 `0x668350` truncation** before this
secondary debit. A primary credit of `1.0` therefore generates a
category-1600 debit of `0.002`, not zero.

The finance representation must consequently retain fractional double values.
The clean-room Balance slice now does so, inserts the category-1600 debit before
the primary credit in ledger order, and internal save schema 10 preserves those
fractional amounts.

Finance Overview independently queries category 1600 through its normal
credit/debit/net aggregate family, proving this is a real ledger category. A
trustworthy EA-facing human-readable label has still not been recovered, so the
implementation deliberately keeps the neutral category-number name.

GitHub Actions at `3fc54ed8524fabade0f37be7017f84d5e967a279` passed
**533 reconstruction tests** and the repository asset-policy workflow.

## Exact next binary-backed trace

Do not restart the now-closed normal Premier League gate-receipt or
category-1600 traces.

Continue from Balance construction at `0x5DC400` and its fresh-game callers to
recover the authoritative source of initial Balance current cash. The modern
runtime still requires callers to supply starting cash explicitly; do not
invent a default amount.

Concession generation remains intentionally disabled on fresh games for the
separate dormant-path reason documented above.


## Fresh-game starting cash source resolved

The authoritative initial current-cash source is now instruction-locked.

`Balance::Balance` at `0x5DC400` does **not** embed a starting-money constant.
Fresh DBRUser construction creates the active and secondary Balance objects with
zero-valued finance objects. The subsequent DBRUser initialization routine at
`0x425680` resolves the controlled `DBRClub` and then performs:

```text
club +0xD0/+0xD4
  -> 0x5E4410(..., convert_flag=1)
  -> 0x5E48D0(..., convert_flag=0)
  -> active Balance +0x10 current cash
```

The compact-club importer closes the source mapping. Parser `0x4022D0` reads an
8-byte field directly into temporary club `+0xD0`; runtime copier `0x403660`
rep-copies that field unchanged to `DBRClub +0xD0/+0xD4`. Accounting for every
preceding packed read places the source at exact `Master.dat` club record bytes
**+165..+172**.

Those eight bytes are an IEEE-754 little-endian double. Canonical examples are:

- Arsenal: `28,000,000.0`;
- Aston Villa: `19,000,000.0`;
- Liverpool: `25,000,000.0`;
- Manchester United: `34,000,000.0`.

Money helper `0x5E4410` multiplies flag-1 input by the build currency factor at
`0x87AD88`; `0x5E48D0` only divides when its own flag argument is nonzero.
The fresh-user path passes zero to `0x5E48D0`. In the analyzed standard build,
`0x6596A0 == 0` selects currency factor **1.0**, so the packed +165 double is
stored unchanged as active current cash.

This resolves the final Gate-10 starting-cash source. No guessed default is
needed: a controlled club's Balance should be materialized from its parsed
`Master.dat +165` double when that DBRUser-equivalent control state is created.


## Chairman financial objective and job-security path

Gate 10's board/job-security dependency is now separated from the dormant
quarterly budget-message family.

The live financial objective belongs to the active Balance subobject at
`Balance +0x30`. Chairman selection generates three objective IDs. Choosing one:

1. computes an immediate starting-funds amount from the current/base club cash;
2. **replaces active current cash** with that amount;
3. stores a separate formal target;
4. stores a deadline exactly three years from selection.

Objective IDs 1..17 have exact starting-funds / target percentage pairs:

```text
1  155/170   2  135/150   3  100/110
4  135/155   5  125/135   6  100/110
7  125/150   8  125/135   9  100/110
10 200/220   11 190/205   12 180/195
13 170/185   14 165/180   15 145/155
16 150/180   17 100/105
```

(percent of the objective base cash).

At deadline, `0x5E1D90` applies named tuning
`ChairmanPercentBudgetMiss = 95`:

- above target: clear success;
- above 95% but not above target: non-sacking near miss;
- **at or below 95% of target: sacking reason 5**.

Reason 5 produces `EAMManagerSackedFailedBudget`. The remaining source-backed
step is the three-candidate ID generator `0x5DFD30`; do not invent objective
choices before that branch is translated for the Premier League path.


## Premier League chairman-objective candidates resolved

Fresh objective state starts with byte `+0x9C = 0`. For Premier League
competition 0, both hierarchy predicates inside `0x5DFD30` are false and the
League allocation count used by the remaining random branch is zero. Candidate
generation therefore consumes no RNG for a fresh Premier League manager.

The three generated IDs are selected only by the recovered fan-base rank-half
comparison:

```text
rank_count >= team_count / 2 -> 13, 1, 5
rank_count <  team_count / 2 ->  1, 5, 6
```

`rank_count` is exactly `0x4F40E0`: the count of league clubs whose fan-base
index is <= the controlled club's index. Arsenal has rank count 19/20 and thus
gets **13, 1, 5**.

This closes the source-backed candidate dependency for normal Premier League
objective integration. Broader objective-generator branches remain deferred
until broader competitions are in scope.
