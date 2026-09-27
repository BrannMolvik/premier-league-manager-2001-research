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

## Confirmed ordinary income producer: concessions

The original executable already provides one verified recurring commercial cash
producer:

`0x42A9FD -> 0x5E5640 -> 0x5E56F0 -> Balance 0x5DC510`

`0x5E5640` iterates active records from the concession subsystem at
`DBRUser +0x690`. The subsystem is a 0xB50-byte object containing eight
0x168-byte concession-offer records and is controlled by tuning including
`FCConcessionOfferMinWait` and `FCConcessionOfferMaxWait`.

The path obtains a financial value from each active record through `0x5E56F0`
and credits the active Balance through `0x5DC510`.

This is enough to prove that concession income is a real live current-cash
producer. It is **not yet enough to integrate it faithfully** because the
repository does not preserve:

- the accounting category attached to the concession posting;
- the exact meaning/source of the amount returned from the offer record;
- the complete offer-state transitions required to decide when a record pays.

Do not invent any of those values.

## Match-day / attendance income dependency boundary

Match-day gate/attendance receipts remain the preferred next income target, but
the modern data model is missing a required original dependency.

The original side has two relevant persistent owners.

### DBRUser +0x694: stadium-section / attendance state

This is a 0x7C-byte persistent object. Its tail contains exactly 26 dwords,
one per stadium-section state entry. Live helpers include:

- `0x6187E0`;
- `0x618A20`;
- `0x618B60`;
- `0x618C10`.

The section calculations resolve entries from the stadium model and combine
them with capacity-derived values.

Downstream monthly/business routines include:

- `0x429904`;
- `0x429BB4`;
- `0x42A111`;
- `0x42A5D2`;
- `0x42C1F2`.

They use stadium capacity helpers including `0x65DA60` and `0x65D9B0`.

### DBRUser +0x6B0: stadium model/state

This is the 0x1BC4-byte stadium model constructed by `0x65CB20`. It contains
the stadium entries used by the ticketing/section logic. The original error
path explicitly states that if the stadium cannot be loaded, building screens
and ticketing will not work.

### What the reconstruction currently has

The clean-room database/runtime already exposes:

- each club's stadium string/identifier;
- each club's `fan_base_index`;
- the 42-row `DBTAccessFanBase` table from Static.dat as 19 packed dwords per
  row;
- one proven AccessFanBase field semantic, runtime `+0x48`, used by the
  transfer subsystem as a retained-roster threshold input.

It does **not** currently materialize the original 26-section stadium state or
the `+0x6B0` stadium capacity/entries model.

Therefore the presence of `AccessFanBase` is not evidence for a gate-receipt
formula, and its unmapped fields must not be relabeled as attendance values.

No original stadium binary assets are currently imported under
`original_assets/`.

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

When the authorized executable/disc is available to the active worker, do **not**
restart the broader finance investigation. Continue from these exact targets:

1. Trace `0x429904`, `0x429BB4`, `0x42A111`, `0x42A5D2`, and
   `0x42C1F2` through their stadium/section inputs and any call that reaches
   Balance credit `0x5DC510`.
2. Identify the actual match-day/gate receipt producer, including:
   - invocation cadence;
   - home/away applicability;
   - attendance/capacity input fields;
   - ticket-price input;
   - accounting category;
   - exact money conversion/rounding.
3. In parallel, `0x5E56F0` is the shortest known route to making concession
   income implementable. Recover its source fields and posting category.
4. Materialize only the required original stadium data/asset format if the
   gate-receipt formula genuinely depends on it. Any intentionally imported
   authorized asset belongs under `original_assets/` with manifest provenance.
5. Add deterministic finance regressions before wiring the producer into normal
   calendar/matchday progression.

Until those details are recovered, the correct reconstruction behavior is to
leave gate/concession income unimplemented rather than inventing a plausible
formula.
