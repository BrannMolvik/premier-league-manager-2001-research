# Gate 8 - Internal Save/Load

> **27 September 2026 startup-wage RNG correction:** deterministic RNG states,
> schedule orders, audit hashes and later gameplay outcomes in this file that
> conflict with `research/STARTUP_WAGE_RNG_CORRECTION.md` are superseded by
> that correction. The gate's functional conclusion remains valid.


_Status: implementation and canonical equivalence verified 27 September 2026_

Gate 8 adds a versioned **internal save format for the modern Windows 11 port**.
It is deliberately separate from original FM2001 save-file compatibility.

## Format

Implementation: `reconstruction/internal_save.py`.

- logical format: deterministic JSON;
- file format: gzip-compressed JSON by default;
- prototype extension: `.fm2k`;
- current schema: **2**;
- no pickle or live Python-object serialization;
- incompatible schema versions fail explicitly;
- a structural source SHA-256 binds a save to the FM2001 database definitions
  it expects.

Immutable player identity/biographical/source fields are reloaded from the
verified game database rather than duplicated into every save. Mutable and
startup-randomized runtime fields are persisted. Schema 2 uses a documented
positional player record to avoid repeating large JSON key strings for roughly
30,000 players; zero training-modifier arrays are stored sparsely as null.

The source fingerprint covers immutable player source identity/development
inputs plus club, manager, competition and fixture definitions. Live skill
changes do not alter the source signature.

## Persisted runtime state

The internal snapshot includes:

- calendar date and monthly-update counter;
- complete runtime-player mutable state:
  - current skills;
  - randomized development baseline and peak ages;
  - training modifiers;
  - club/shirt state;
  - XI/substitute flags and assigned match position state;
  - Condition and Form;
  - injury/suspension/selection availability state and dates;
  - discipline counters;
  - Non-EU runtime state;
  - morale and startup-randomized month span;
- club roster order;
- Premier League result state and recovered round dates/order;
- team tactics;
- Pitch Wear;
- prepared match environments;
- recovered Premier League scheduler order;
- shared `GameState.rng` state;
- human club, formation, XI/bench and Team Orders;
- human controller `match_rng` state;
- pending human fixture;
- already-completed and still-pending same-day fixture state, including detailed
  prior `NormalMatchResult` event/possession records.

Current club/manager/competition definitions themselves are immutable in the
implemented gameplay runtime, so they are reloaded from the source database and
verified through the source fingerprint rather than copied into the save.
Future gates that make those definitions mutable must extend/bump the schema.

## Automated regression

`reconstruction/test_internal_save.py` verifies:

- JSON round-trip from a mid-matchday pending-human-fixture state;
- gzip file save/load;
- source-database mismatch rejection;
- source fingerprint stability across live skill changes;
- source fingerprint rejection when immutable player source identity changes;
- unknown schema rejection;
- save/reload branch equivalence through three full later matchdays, including
  detailed match results, tables, runtime snapshots and RNG state.

At the compact-schema checkpoint `ea5a8545f08822a542f4800c0d38ac609a40fc1b`:

- reconstruction GitHub Actions: **413 tests passed**;
- repository asset-policy workflow: **passed**.

## Save-size checkpoint

Canonical Arsenal game, saved mid-matchday on 26 August 2000 after seven
earlier same-day AI fixtures but before Arsenal's fixture:

- schema-2 deterministic JSON: **6,535,498 bytes**;
- gzip file: **998,022 bytes**;
- gzip / raw ratio: about **15.3%**;
- deterministic JSON SHA-256:
  `0eac6a1c5ddd248c76f153b2a274d334240fd0ec72cdc494331cb543e37838f6`;
- source signature SHA-256:
  `6ba4b9c3bce385f084053d7b0ef13595652e3335ac7ea04991637281785668cc`.

The earlier uncompressed schema-1 experiment was about 34.9 MB, so schema 2
removes most duplicated source data before gzip compression.

## Canonical shipped-data continuation audit

Runner: `reconstruction/canonical_internal_save_audit.py`.

The audit uses the same canonical shipped files and human-control path proven in
Gate 7.

Sequence:

1. start a canonical new game and control Arsenal (club ID 0);
2. play the 19 August and 23 August 2000 league fixtures normally;
3. advance to 26 August;
4. execute the **seven AI fixtures scheduled before Arsenal** on that date;
5. stop with Arsenal's fixture ID **20** pending and fixture IDs **22** and
   **29** still after it;
6. serialize schema 2;
7. create a fresh `FM2001Database` and coefficient-matrix set;
8. restore the save into a fresh runtime;
9. require exact snapshot equality immediately;
10. continue original and restored branches through four human fixtures and
    require equal matchday outcomes, runtime snapshots and RNG after each.

The continued fixtures were:

| Date | Fixture ID | Score | Stored PL results | Match RNG after |
| --- | ---: | --- | ---: | --- |
| 26 Aug 2000 | 20 | Arsenal 2-1 Charlton Athletic | 30 | `0x1047CB35` |
| 2 Sep 2000 | 34 | Chelsea 3-1 Arsenal | 40 | `0xCF9BCBFF` |
| 16 Sep 2000 | 40 | Bradford City 1-3 Arsenal | 50 | `0x30A76146` |
| 23 Sep 2000 | 50 | Arsenal 1-1 Coventry City | 60 | `0xBE52A1F6` |

The restored branch remained exactly equal to the uninterrupted branch through
the full Gate-7 six-fixture span. Arsenal ended 4-1-1 on 13 points, matching the
Gate-7 canonical baseline.

Canonical Gate-8 audit SHA-256:

```text
69a91dbce914be2fe5babdf8a8c71ad77bad5653c9cac09468520330f7c7b413
```

## Prototype integration

The Tkinter Play tab now exposes **Save Game** and **Load Game**. Loading
restores the human club, formation, XI/bench, tactics, table, current date and
pending fixture state.

## Gate 8 criteria

- [x] Calendar, current runtime players, source-bound club/manager/competition
      definitions, fixture/results, injuries, suspensions, tactics and relevant
      RNG state survive save/reload.
- [x] Save -> reload -> continue produces equivalent state.
- [x] Multi-week games can be resumed.
- [x] Original PLM2001 save compatibility remains explicitly separate and
      incomplete.

Original save compatibility therefore remains a later fidelity task rather than
being implied by this internal port format.
