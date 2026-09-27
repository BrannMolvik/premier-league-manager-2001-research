# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 10 - Finances and board systems**

Gates 1 through 9 are complete.

Gate 9 closed after the modern runtime gained persistent contract/transfer
state, live human cash bids and player terms, safe scheduled transfer
completion, a callable human transfer workflow, and the recovered Saturday AI
acquisition path.

Evidence: `research/GATE9_TRANSFERS_AND_CONTRACTS.md`.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Preserve and reuse original data,
music, sounds, interface graphics, strings, and other resources wherever
technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance
tracked according to `research/ASSET_POLICY.md`.

## Verified repository state

Final Gate-9 code checkpoint:

```text
c8b6d4e71fa9464e4d7f002c69213aad2f5ff196
Verify human transfer completion on calendar advance
```

GitHub Actions at that checkpoint:

- reconstruction suite: **486 tests passed**;
- repository asset-policy workflow: **passed**.

Current internal save schema: **8**.

Canonical executable SHA-256:

```text
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3
```

The authorized disc image was re-materialized during the Gate-9 closure audit
and the extracted executable reverified against that hash. Raw extraction data
remains outside Git.

## Stable startup / scheduler checkpoint

The corrected canonical path through primary schedule finalization remains:

- DBTPlayers startup RNG: **180,384 calls** for 30,064 players;
- synthetic post-youth state: **`0x4B68DE28`**;
- actual-count primary competition RNG: **5,836 calls**;
- state entering primary `0x615BE0`: **`0x4F5CF274`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0xD25DFFE6`**;
- first PL fixture order: **0, 6, 8, 5, 1, 9, 3, 2, 4, 7**.

See `research/STARTUP_WAGE_RNG_CORRECTION.md` and
`research/GATE4_SCHEDULE_ORDER.md`.

## Stable gameplay / save checkpoints

- Gate 6: three deterministic full 38-round / 380-fixture Premier League
  seasons.
- Gate 7: six human-controlled Arsenal fixtures while all surrounding matches
  continued in recovered scheduler order.
- Gate 8: source-bound internal save/reload with exact continuation across a
  mid-matchday boundary.
- Gate 9: human and AI transfer/contract runtime integrated with calendar
  progression.

Evidence:

- `research/GATE6_FULL_SEASON.md`
- `research/GATE7_HUMAN_GAMEPLAY.md`
- `research/GATE8_INTERNAL_SAVE.md`
- `research/GATE9_TRANSFERS_AND_CONTRACTS.md`

## Gate 10 goal

Make money and board constraints materially affect management.

Roadmap completion requires:

- club cash/balance represented;
- wage and transfer budgets represented;
- match and recurring income/cost paths integrated;
- player wages and transfer spending/income persisted;
- board expectations/job-security behavior integrated where recovered;
- remaining approximations explicitly labeled.

## Gate 10 strongest known evidence

Existing reverse engineering already establishes:

- DBRUser owns six Balance pointers at `+0x670..+0x684`;
- current cash is the qword at active Balance `+0x10`;
- transfer buyer debit is `0x404B30 -> 0x5DC650`;
- transfer seller credit is `0x404BB0 -> 0x5DC510`;
- controlled-club affordability check `0x404AE0` compares against the same
  current-cash value;
- transfer postings use accounting category 1000;
- current cash and chairman transfer budget are separate concepts;
- `EAMchairbudgetsettings +0x58` is the displayed transfer-budget value;
- start-season/monthly chairman budget event layouts and default budget globals
  are mapped;
- the authoritative persisted/derived transfer-budget store remains unresolved.

## Exact next task

1. Materialize a clean-room **Balance/current-cash runtime object** from the
   already-proven DBRUser/Balance layout.
2. Replace Gate-9's controlled-buyer affordability callback with that live cash
   state.
3. Post completed transfer purchases/sales through the reconstructed
   buyer-debit / seller-credit paths and persist them in save schema 9.
4. Add deterministic tests proving insufficient cash blocks a controlled
   purchase and successful completion debits buyer / credits seller by the same
   amount.
5. Then resume the existing chairman-budget trace to resolve the authoritative
   live transfer-budget store before modeling the other operating budgets.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. Most relevant now:

- authoritative transfer-budget storage is unresolved;
- broader player-negotiation refusal/duration branches remain explicit deferred
  states;
- exact due-transfer ordering relative to same-day fixtures is not yet
  instruction-locked;
- later AI transfer-window toggling, autonomous contract-category source and
  buy-counter lifecycle remain bounded gaps;
- original FM2001 save compatibility remains separate;
- broader competitions, original front-end fidelity and FastView/3D remain
  later gates.

## Do not work on yet

Unless required to unblock Gate 10, defer:

- broader management systems beyond finance/board dependencies;
- broader competition season-transition behavior;
- original save-file compatibility;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `research/BACKLOG.md` instead.
