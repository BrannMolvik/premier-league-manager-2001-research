# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. It is intentionally short. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 3 - Build an executable startup RNG ledger (REOPENED)**

Gates 1 and 2 are complete. Gate 3 was previously marked complete but has been reopened after discovering mandatory Cup round scheduler RNG before primary `0x615BE0`. Gate-4 scheduler groundwork remains valid but is paused.

## Porting mission

The project is now explicitly a **Windows 11 modernization/port**, not a strict clean-room-only replacement.

The project owner has confirmed that the supplied FM2001 archive/disc contents are authorized for project use. Future work should therefore preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical. Modern code should replace the incompatible runtime/game logic while keeping the original player-visible experience as intact as possible.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Latest reverse-engineering checkpoint before stabilization: `1014b042a19fc851b8d87e653ee1e5d807816630` - **Advance startup RNG boundary before TeamSelect click**
- Latest reconstruction-suite validation: `8b52d20a3e363430c33257b1954763a377aa0b06` - **358 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 3 correction objective

The hidden shared MSVC CRT state entering primary `0x615BE0` is now corrected.

Canonical primary competition totals are:

- 27 primary Cups;
- 115 primary Cup rounds;
- 80 NormalRound / 32 TwoLegRound / 3 MiniLeagueRound;
- 1,737 mandatory Cup participant-shuffle calls;
- 124 mandatory DummyLeague lazy-ranking calls reached through type-5 Cup allocation;
- 2 Europe-root selector calls;
- **1,863 total competition-stage CRT calls before `0x615BE0`**.

For the existing synthetic post-youth checkpoint `0x2797444C`, the corrected competition-stage state is `0xAECA9FA5`.

Gate 3 remains open only because exact bounded-call **ordering and resulting Cup pairings** must still be materialized. That output is required by Gate 4 to know the complete global schedule bucket contents.

## Last verified technical boundary

The startup path through TeamSelect and pre-competition initialization is bounded.

The corrected primary Cup scheduler state is also quantified and implemented:

- all 115 primary Cup rounds contribute their mandatory participant Fisher-Yates;
- total Cup pairing RNG cost is 1,737 calls;
- first type-5 access to 11 unique DummyLeague sources adds 124 ranking calls;
- the two Europe selectors add two more calls;
- hidden CRT state after all 1,863 competition-stage calls is reproducible exactly;
- canonical invariants are enforced by `reconstruction/verify.py`.

Gate-4 groundwork remains valid and committed:

- exact primary bucket coordinate system;
- exact ordinary LeagueMatch conflict-placement search;
- first Premier League target bucket = 54;
- complete target-54 bucket = 142 LeagueMatch nodes;
- PL fixture IDs occupy pre-shuffle slots 96..105 in order 9..0.

The remaining blocker is not RNG call count; it is exact Cup bounded-call order/pairing output so Cup-generated matches can be placed into the global schedule before the bucket shuffle.

## Exact next task

Gate 3 now has executable Cup runtime materialization, not only RNG accounting:

- corrected primary pre-`0x615BE0` ledger remains **1,863 calls** / state `0xAECA9FA5`;
- type-5 DummyLeague ranking RNG is integrated;
- exact legacy CRT `qsort` behavior is implemented;
- standard allocation types 1/3/4/5 expand into semantic ClubRefs;
- silent entrant-capacity overflow is reproduced;
- both Champions-League-to-UEFA type-2 transfer branches are represented as exact semantic ClubRefs;
- NormalRound/TwoLegRound shuffle -> qsort -> split-half pairing is implemented;
- MiniLeague shuffle/distribution/qualification propagation is implemented;
- Cup runtime rounds now materialize participant arrays, pairings, and propagated winner/group-position refs;
- the conditional auxiliary Cup shuffle is proven zero-draw at startup;
- `reconstruction/cup_runtime.py` now composes all primary Cups on one shared RNG stream, including lazy DummyLeague ranking, UEFA type-2 transfer injection, allocation, Europe selectors, round materialization, and stable participant/pairing digests;
- cross-Cup synthetic integration is locked by CI at **358 tests passed**.

Continue Gate 3 by:

1. trace the exact NormalRound / TwoLegRound / MiniLeague schedule-node construction and insertion semantics so materialized Cup pairings can become primary-container nodes without approximation;
2. wire those recovered node rules into the all-primary-Cup driver;
3. execute the driver against the authorized canonical Master.dat / Static.dat / STR set when those files are available to the execution environment, verifying all 27 Cups / 115 rounds, both UEFA type-2 injections, the 1,863-call bound digest/state, and participant/pairing digests;
4. lock those canonical digests/checkpoints in verification;
5. close Gate 3 and resume Gate 4 with the emitted Cup schedule nodes.

The canonical game binaries were not available in the current ChatGPT file library or connected Dropbox during the 358-test checkpoint, so no unexecuted participant/pairing digest is being claimed as canonical.

Commit every verified canonical materialization boundary separately.

## Gate 3 completion criteria (reopened)

- [x] One shared MSVC CRT RNG stream covers the mapped pre-competition startup phases.
- [x] Fixed-seed intermediate checkpoints exist for those phases.
- [x] Python-RNG startup fallbacks are isolated/removed.
- [x] Cup round scheduler RNG call count before primary `0x615BE0` is fully included.
- [x] Corrected hidden CRT state entering primary `0x615BE0` is reproducible and canonically verified.
- [x] Exact bounded-call ordering, including type-5 DummyLeague lazy sorts, is materialized and canonically verified.
- [ ] Cup participant records and final pairing output are materialized for schedule reconstruction.


## Current implementation state

Already implemented and tested at a substantial level:

- canonical Master.dat / Static.dat / STR parsing for the core shipped database;
- mutable runtime player state;
- player aging/development/training;
- Premier League real fixtures, dates, results, and table;
- AI formation, lineup, substitutes, roles, and Non-EU handling;
- MatchCalculator normal-time simulation;
- set pieces, possession, Condition decay, injuries, discipline, and substitutions;
- post-match Form/Condition, persistent injury, and discipline state;
- fixture -> match -> result -> table integration;
- startup/schedule RNG primitives and several mapped startup consumers.

## Known live fidelity boundaries

See `FIDELITY_GAPS.md` for the canonical list. The most relevant current gaps are:

- the all-Cup orchestration exists and is integration-tested, but its canonical participant/pairing digests still require execution against the authorized shipped data;
- exact Cup schedule-node construction/insertion semantics are still being traced before primary `0x615BE0`;
- exact inter-bucket RNG consumption/order inside primary `0x615BE0` is Gate-4 work paused behind that correction;
- deterministic fixture-ID same-day fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- absence of real-data full-matchday/full-season automated integration;
- incomplete human management, transfers/contracts, finance/board, broader competitions, save compatibility, faithful UI, and FastView/3D.

## Do not work on yet

Unless required to unblock the reopened Gate 3, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competitions;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
