# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 4 - Resolve exact Premier League matchday ordering**

Gates 1, 2, and 3 are complete. Gate 3 was reopened when previously missed procedural-League RNG and later actual-runtime Cup participant counts changed the pre-`0x615BE0` state. The corrected actual-count competition materializer is now canonical and digest-locked. Gate 4 resumes from that state.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc contents are authorized for project use. Preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Latest verified code baseline before the Gate-3 transition: `b4264affbdbbf1e69d18a9293c2e46833ca4b76e` - **Relabel packed Cup RNG helpers as diagnostics**.
- Reconstruction GitHub Actions at that head: **392 tests passed**.
- Repository asset-policy GitHub Actions at that head: **passed**.
- Gate-3 transition is recorded in `ROADMAP.md` and `project_status.json`.
- Canonical executable hash: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Gate-3 canonical actual-count checkpoint

The executable Cup schedulers `0x4F64D0` / `0x4F6820` shuffle runtime round `+0x0C` actual ClubRef count after allocation/propagation. They do **not** use packed Static.dat team capacity as the final shuffle length.

Canonical primary competition RNG before the first primary `0x615BE0` therefore contains:

- **39 procedural League runtime instances**;
- **4,302 procedural-League bounded calls**;
- **1,728 actual-count Cup participant-shuffle calls**;
- **124 DummyLeague lazy-ranking calls**;
- **2 Europe-root selector calls**;
- **6,156 bounded calls total**;
- **167 RNG-bearing events** plus one explicit zero-draw fixed-League traversal marker = **168 traversal events**.

For synthetic post-youth state `0x2797444C`:

```text
0x2797444C
  + canonical actual-count competition replay
= 0x0E556598
```

Canonical ordered-bound SHA-256:

```text
1ed67d7402f1fb749d963f8978a242a6833a1f4410434b61165c906b943a710d
```

Europe selectors remain clubs **1137** and **1159**. In the integrated traversal list their indices are **138** and **159**.

The older **6,165 calls / 1,737 Cup calls / `0x0DD3ACA3` / `3e7acc...`** values are retained only as the historical packed-capacity diagnostic and must not be used as the state entering `0x615BE0`.

## Canonical competition materialization digests

Canonical shipped-data run from `0x2797444C`:

```text
Cup participant SHA-256
f9282d4c236e14f9ccb56a8ecf90dc42095278e94471624f7248eb005e3daa4e

Cup pairing/group SHA-256
e2f34fe736db27a011c274d8be0b0df26ed7547062c80a8b34b7d56620c63e45

Cup schedule-node SHA-256
30b06c3e420ebb5bbead56a14b00340a532d12dcc5bdffba715e4f84eca5ca89

Complete primary schedule-node SHA-256
0a22c9f0c1fa20de770a7d679583b6b4e4bdbd9363a5bda07194bfe8919cc35a
```

Counts:

- 27 primary Cups / 115 Cup rounds;
- 1,226 Cup schedule nodes;
- 9,346 complete primary schedule nodes before bucket placement/shuffle;
- 3 allocation refs dropped after destination capacity was exhausted;
- 24 Champions-League-to-UEFA type-2 transfer refs.

Canonical UEFA Cup runtime participant counts across rounds 210..217 are:

```text
80, 95, 47, 31, 15, 7, 3, 1
```

The original odd-count quirk is preserved: knockout scheduling pairs `floor(count/2)` entries and leaves the final sorted ClubRef unpaired rather than inventing a bye.

## Gate-3 participant/source fixes that must not be regressed

- League-parent playoff children 97 / 157 / 169 use `League::Initialize 0x4F5150 -> 0x4F4FD0` to expand destination allocation types 4/1 into exact type-2 source-position ClubRefs.
- Cup type-3 source enumeration is exact: Cup virtual count = 2 and index getter exposes constructor fields `Cup+0x40/+0x44`, parsed as `enumerated_club_reference_0/1`.
- Allocation type 3 and type 5 both preserve executable source-exhaustion underfill behavior instead of raising.
- `startup_sequence.py` now composes precompetition RNG directly into `materialize_primary_rng_driven_schedule()` on the same MSVC CRT object.
- Legacy packed-capacity helpers remain only as explicitly labeled regression diagnostics.

## Gate-4 scheduler groundwork already recovered

- primary schedule container = **373 buckets**;
- exact ordinary LeagueMatch conflict-placement search beneath `0x615950` is implemented;
- generic Cup/League ClubRef conflict identity through `0x510A80` / `0x510A40` -> `0x4F2830` is recovered;
- fixed Premier League source fixture insertion order is known;
- first Premier League nominal target bucket = **54**;
- earlier LeagueMatch-only reconstruction found **142 nodes** in bucket 54;
- Premier League fixture IDs occupied pre-shuffle relative slots **96..105** in order **9..0** in that older partial reconstruction.

Those bucket-54 counts/slots are not final. They must now be re-audited using the complete 9,346-node Gate-3 materialization.

## Exact next task

Continue Gate 4 from the corrected state entering primary `0x615BE0`:

1. Feed the complete 9,346-node primary schedule materialization into the recovered **373-bucket placement** path in exact competition/node insertion order.
2. Apply the recovered generic ClubRef conflict identity and `0x615950` outward conflict search to League/Cup nodes as appropriate. Do not reuse the earlier League-only bucket population as final truth.
3. Re-audit bucket **54** and record:
   - complete pre-shuffle node count;
   - exact Premier League fixture-ID relative positions;
   - any Cup/procedural nodes newly sharing or displacing around the first PL matchday.
4. Starting from corrected CRT state **`0x0E556598`**, recover/execute the primary `0x615BE0` bucket-shuffle sequence and lock the first Premier League matchday order.
5. Extend the regression across the first several real matchdays, then audit Gate-4 completion criteria.

## Gate 4 completion criteria

- [ ] Premier League source fixture insertion order is preserved.
- [ ] Schedule bucket/container selection is reproduced for the complete primary node set.
- [ ] Shuffle input RNG state is the corrected actual-count checkpoint `0x0E556598`.
- [ ] Same-day extraction/execution order is reproduced.
- [ ] Regression tests cover the first several real matchdays.

## Current implementation state

Already implemented and tested at a substantial level:

- canonical Master.dat / Static.dat / STR parsing;
- mutable runtime player state;
- player aging/development/training;
- Premier League real fixtures, dates, results, and table;
- AI formation, lineup, substitutes, roles, and Non-EU handling;
- MatchCalculator normal-time simulation;
- set pieces, possession, Condition decay, injuries, discipline, and substitutions;
- post-match Form/Condition, persistent injury, and discipline state;
- fixture -> match -> result -> table integration;
- exact MSVC CRT startup/schedule RNG primitives;
- exact legacy CRT qsort behavior;
- Cup allocation, participant, pairing, MiniLeague, UEFA-transfer, and Cup-source enumeration materialization;
- procedural League round-robin RNG generation;
- Scottish post-split symbolic node generation;
- integrated fixed/procedural/Scottish/Cup primary schedule-node materialization;
- one shared startup CRT stream through the actual-count competition checkpoint.

## Known live fidelity boundaries

See `FIDELITY_GAPS.md` for the canonical list. Most relevant now:

- exact full-node placement and per-bucket shuffle/execution order inside primary `0x615BE0` is Gate-4 work;
- deterministic fixture-ID same-day fallback remains in the playable season path until Gate 4 replaces it;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- absence of real-data full-matchday/full-season automated integration;
- incomplete human management, transfers/contracts, finance/board, broader competition season transitions, save compatibility, faithful UI, and FastView/3D.

## Do not work on yet

Unless required to unblock Gate 4, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competition season-transition behavior;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
