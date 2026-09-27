# Gate 9 - Transfers and Contracts

**Completed: 27 September 2026**

Gate 9 makes squad building part of the modern runtime. The implementation
reuses the authorized FM2001 data/executable evidence and deliberately leaves
finance posting to Gate 10 rather than inventing a budget system early.

## Canonical source

The authorized disc image was re-materialized during the final Gate-9 audit.
The extracted executable reverified as:

```text
FOOTBAL.EXE
SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

Raw disc images and temporary extraction files were kept outside Git.

## Implemented transfer state

The modern runtime now represents and persists:

- player weekly wage and contract-expiry date;
- promotion bonus, appearance fee, contract clauses, house and car benefits;
- 0x50-byte proposal-equivalent state;
- CDealInProgress-equivalent state;
- player bid-log entries;
- scheduled MPMTransferPlayer mode 0/1 objects;
- completed CPlayerMovement-equivalent history;
- transfer-listed, loaned and signed-for-another-club status required by the
  reconstructed decision/completion paths.

Internal save schema **8** preserves the Gate-9 transfer state and the neutral
runtime inputs used by the weekly AI acquisition path.

## Human cash-transfer path

The ordinary cash-only human path is reconstructed from the recovered
executable flow rather than from an invented transfer model.

### Selling club

`submit_live_cash_bid` creates proposal/deal/bid-log state before the
seller response, matching the original lifecycle. For the canonical ordinary
cash mode, proposal value equals the cash fee.

The seller decision reproduces the mapped `0x4EF940` behavior:

- protected under-30/top-11 players reject bids below 60% of live player value;
- selling squads with fewer than 17 eligible players reject as too small;
- otherwise the offer is accepted.

Player value is resolved from live AccessSkillFinancialValue, position, age,
competition and country inputs.

### Player terms

The reconstructed ordinary money path includes:

- live wage and signing-fee floor/expectation helpers;
- direct acceptance for sufficiently strong terms;
- low-wage rejection;
- already-signed and recently-joined rejection states;
- the exact counter-offer transform from `0x4EDB10 -> 0x4EE180`;
- 110% tolerance;
- repeated-offer anchor midpoint/current-wage floor;
- 24/36/48-month counter-offer duration draw;
- exact code-1 Counter Offer and code-2 Player Accepts branches where proven.

Two broader response branches remain explicitly deferred rather than guessed;
see `research/FIDELITY_GAPS.md`.

### Transfer conclusion and movement

Accepted ordinary cash terms reach the recovered
`0x4EF600 -> MPMTransferPlayer` handoff.

The modern runtime reproduces:

- mode 0 scheduled for current date +1;
- mode 1 scheduled for +7 days;
- 40-player buyer roster reschedule from mode 0 to mode 1;
- final 40-player mode-1 block;
- controlled-buyer current-cash dependency exposed as an explicit callback
  until Gate 10 supplies live finances;
- safe seller-roster removal and buyer-roster insertion;
- current-club join-date update;
- transfer/signed/loan status cleanup;
- negotiated contract application;
- movement-history recording;
- proposal/deal cleanup after completion.

`HumanGameplayController` now exposes the complete callable Gate-9 sequence:

1. `submit_cash_bid`;
2. `offer_player_contract`;
3. accepted terms schedule the +1-day transfer;
4. normal calendar advance executes the due transfer using the explicit
   affordability callback.

This gives Gate 10 a stable transfer interface to connect to real club cash
without redesigning the transfer subsystem.

## Autonomous AI acquisition

The final Gate-9 criterion is backed by the recurring original path:

```text
0x40DD70 weekly club maintenance
  -> 0x40DC90(buyer)
    -> 0x40DBB0(seller)
      -> 0x41EFB0(target, buyer)
```

The weekly phase is Saturday in the 2000/01 calendar.

Implemented evidence-backed behavior includes:

- BigClubFanBase threshold 21;
- BigClubBuyChance 50;
- user-controlled club suppression;
- active-manager, country/window and club-status gates;
- startup-roster-count capacity predicate;
- big-club-filtered random seller selection;
- three related-club IDs and their directional RNG suppression;
- AccessFanBase.field_48 - 4 seller retained-roster threshold;
- exact seller spare-roster discounting;
- exact positional coverage-equivalence/minimum tables;
- >26-week seller target tenure;
- >=12-week direct-acquisition defensive guard;
- recovered valuation-based transfer-fee construction;
- autonomous wage generation through the existing financial-value machinery;
- decoded age/category autonomous contract-month table;
- direct safe movement through the same roster/contract core used by ordinary
  transfer completion.

A Friday-to-Saturday GameState regression proves that calendar progression can
produce an AI player movement.

## Verification

The final Gate-9 code checkpoint is:

```text
c8b6d4e71fa9464e4d7f002c69213aad2f5ff196
Verify human transfer completion on calendar advance
```

GitHub Actions at that checkpoint:

- reconstruction suite: **486 tests passed**;
- repository asset-policy workflow: **passed**.

The feature branch remains a fast-forward descendant of the pre-implementation
main checkpoint `4f174fcf`.

## Bounded fidelity gaps

Gate 9 is complete for the roadmap criteria, but completion does not mean every
transfer branch is claimed exact. The live gap tracker retains:

- the unmapped broader player-response helper `0x422803` and invalid-duration
  `0x423340` revision branch;
- exact same-day ordering of a due MPMTransferPlayer relative to fixtures;
- later transfer-window boundary toggling;
- exact `0x4FA510` autonomous contract-category source;
- exact autonomous buy-counter reset/update lifecycle;
- finance posting and controlled-club affordability, which are Gate 10 work.

These boundaries are explicit and do not require invented behavior to satisfy
the Gate-9 completion criteria.
