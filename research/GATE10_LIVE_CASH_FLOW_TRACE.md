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
