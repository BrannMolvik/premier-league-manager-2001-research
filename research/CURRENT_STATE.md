# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 5 - Real-data matchday integration**

Gates 1 through 4 are complete. Gate 4 closed after the complete 9,346-node
primary schedule was placed and shuffled with the corrected Gate-3 CRT state,
and the first ten canonical Premier League same-day fixture orders were
regression-locked.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Preserve and reuse original data,
music, sounds, interface graphics, strings, and other resources wherever
technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance
tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Gate-4 code/test checkpoint: `c44e72ddae2e7976e8a1685f1662d659dc4a5e4c`
  - **Regress first ten Premier League matchday shuffles**.
- Reconstruction GitHub Actions at that checkpoint: **399 tests passed**.
- Repository asset-policy workflow at that checkpoint: **passed**.
- Gate-4 evidence: `research/GATE4_SCHEDULE_ORDER.md`.
- Canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Gate-3 canonical startup checkpoint

Canonical primary competition RNG before primary `0x615BE0`:

- 39 procedural League runtime instances / **4,302 calls**;
- 115 actual-count Cup round shuffles / **1,728 calls**;
- 11 DummyLeague lazy-ranking events / **124 calls**;
- 2 Europe selectors / **2 calls**;
- **6,156 bounded calls total**;
- **167 RNG-bearing events** plus one zero-draw fixed-League traversal marker.

For synthetic post-youth state `0x2797444C`:

```text
0x2797444C
  + canonical actual-count competition replay
= 0x0E556598
```

Ordered-bound SHA-256:

`1ed67d7402f1fb749d963f8978a242a6833a1f4410434b61165c906b943a710d`

Canonical materialization:

- Cup participant SHA:
  `f9282d4c236e14f9ccb56a8ecf90dc42095278e94471624f7248eb005e3daa4e`;
- Cup pairing/group SHA:
  `e2f34fe736db27a011c274d8be0b0df26ed7547062c80a8b34b7d56620c63e45`;
- Cup schedule-node SHA:
  `30b06c3e420ebb5bbead56a14b00340a532d12dcc5bdffba715e4f84eca5ca89`;
- complete primary schedule-node SHA:
  `0a22c9f0c1fa20de770a7d679583b6b4e4bdbd9363a5bda07194bfe8919cc35a`;
- **1,226 Cup nodes**;
- **9,346 complete primary schedule nodes**.

The older packed-capacity 6,165-call / `0x0DD3ACA3` checkpoint is historical
only and must not be used for scheduler reconstruction.

## Gate-4 canonical primary schedule checkpoint

Recovered primary scheduler path:

```text
0x615670 -> 0x615700   373-bucket primary container
0x615950              nominal date + conflict placement + head insertion
0x615890 -> 0x615790  adjacent conflict probe
0x615BE0 -> 0x615AE0  ascending-bucket Fisher-Yates
0x615C10              head-to-tail execution traversal
```

Canonical full-node placement/shuffle:

- primary buckets: **373**;
- non-empty buckets: **168**;
- largest bucket: **147 nodes**;
- nodes moved from nominal bucket by conflict placement: **38**;
- bucket-count-vector SHA-256:
  `fce6003d6a415813c08d3b55152ae6bf3da3fb9f68eef3bf4c0666e1df67718b`;
- primary bucket-shuffle draws: **9,178**;
- state entering shuffle: **`0x0E556598`**;
- state after all primary bucket shuffles: **`0x839953AA`**.

First Premier League matchday:

- nominal/actual bucket: **54**;
- complete pre-shuffle bucket size: **142**;
- no nodes move into or out of bucket 54;
- PL pre-shuffle slots: **96..105**;
- pre-shuffle fixture IDs: **9..0**;
- exact PL execution order after shuffle:
  **8, 3, 2, 4, 6, 9, 5, 0, 1, 7**.

The first ten canonical PL fixture orders are regression-locked in
`reconstruction/test_primary_schedule.py`.

## Gate-4 implementation that must not be regressed

`reconstruction/primary_schedule.py` now models:

- primary nominal bucket calculation, including the 25-December skip;
- generic ClubRef conflict placement and outward two-day search;
- exact head insertion into all 373 buckets;
- exact `0x615BE0 -> 0x615AE0` bucket shuffle;
- extraction of fixed-League fixture order in `0x615C10` traversal order.

The standalone matchday API may still use deterministic fixture-ID order when
no reconstructed startup scheduler order is supplied. This is now an
integration fallback, not an unknown original behavior.

## Exact next task

Continue Gate 5 against canonical shipped data:

1. Connect the recovered Premier League scheduler order to the real-data
   matchday execution path instead of supplying fixture order manually.
2. Run one complete canonical **10-match Premier League round** through the
   existing AI preparation, match simulation, post-match persistence, result
   storage, and league-table update.
3. Verify all **20 Premier League clubs participate exactly once** in that
   round and that every due fixture executes in the recovered scheduler order.
4. Audit and persist round-level state:
   - 10 results stored exactly once;
   - table played totals reconcile;
   - goals for/against reconcile;
   - discipline, injuries, Form, Condition, and Pitch Wear persist coherently;
   - no invalid player/club IDs or impossible lineups.
5. Extend the integration across several consecutive canonical real rounds.
   When Gate-5 criteria are satisfied, update the roadmap/status and move to
   Gate 6.

## Gate 5 completion criteria

- [ ] Canonical data hashes are checked before integration runs.
- [ ] One complete real 10-match Premier League round runs.
- [ ] All 20 clubs participate exactly once in that round.
- [ ] Results, table, statistics, discipline, injuries, Form, Condition, and
      Pitch Wear persist coherently.
- [ ] Several consecutive real rounds run without invalid state.

## Current implementation state

Already implemented and tested at a substantial level:

- canonical Master.dat / Static.dat / STR parsing;
- exact startup and schedule CRT RNG;
- complete primary Cup/League schedule-node materialization;
- exact primary bucket placement/shuffle and PL same-day ordering;
- mutable runtime player state;
- AI formation, lineup, substitutes, roles, and Non-EU handling;
- MatchCalculator normal-time simulation;
- set pieces, possession, Condition decay, injuries, discipline, substitutions;
- post-match Form/Condition, injury, and discipline persistence;
- fixture -> match -> result -> Premier League table integration;
- daily calendar sequencing and Pitch Wear recovery.

## Known live fidelity boundaries

See `FIDELITY_GAPS.md`. Most relevant now:

- canonical real-data 10-match and multi-round integration is not yet locked;
- standalone callers without startup scheduler state still use an explicit
  deterministic fixture-ID fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- incomplete human management, transfers/contracts, finance/board, broader
  competition season transitions, save compatibility, faithful UI, and
  FastView/3D.

## Do not work on yet

Unless required to unblock Gate 5, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competition season-transition behavior;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
