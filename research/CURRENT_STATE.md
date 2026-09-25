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
- Latest reconstruction-suite validation: `1ee98449980c872de33ecdb377124701f3766149` - **326 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 3 correction objective

The hidden shared MSVC CRT state entering primary `0x615BE0` is now corrected.

Canonical primary competition totals are:

- 27 primary Cups;
- 115 primary Cup rounds;
- 80 NormalRound / 32 TwoLegRound / 3 MiniLeagueRound;
- 1,737 mandatory Cup participant-shuffle calls;
- 2 Europe-root selector calls;
- **1,739 total competition-stage CRT calls before `0x615BE0`**.

For the existing synthetic post-youth checkpoint `0x2797444C`, the corrected competition-stage state is `0x986E4579`.

Gate 3 remains open only because exact bounded-call **ordering and resulting Cup pairings** must still be materialized. That output is required by Gate 4 to know the complete global schedule bucket contents.

## Last verified technical boundary

The startup path through TeamSelect and pre-competition initialization is bounded.

The corrected primary Cup scheduler state is also quantified and implemented:

- all 115 primary Cup rounds contribute their mandatory participant Fisher-Yates;
- total Cup pairing RNG cost is 1,737 calls;
- the two Europe selectors add two more calls;
- hidden CRT state after all 1,739 competition-stage calls is reproducible exactly;
- canonical invariants are enforced by `reconstruction/verify.py`.

Gate-4 groundwork remains valid and committed:

- exact primary bucket coordinate system;
- exact ordinary LeagueMatch conflict-placement search;
- first Premier League target bucket = 54;
- complete target-54 bucket = 142 LeagueMatch nodes;
- PL fixture IDs occupy pre-shuffle slots 96..105 in order 9..0.

The remaining blocker is not RNG call count; it is exact Cup bounded-call order/pairing output so Cup-generated matches can be placed into the global schedule before the bucket shuffle.

## Exact next task

The exact primary competition **bounded-call order** is now materialized:

- 117 RNG-bearing events;
- 115 Cup-round Fisher-Yates events;
- two Europe selector events at canonical event indices 99 and 108;
- 1,739 total bounded calls;
- canonical ordered-bound SHA-256:
  `baef6479394ffee84e7a9aec58d74f1c5418ccaeaad7f617d9ed0f77e95fd8df`;
- corrected synthetic state entering primary `0x615BE0` remains `0x986E4579`.

Continue Gate 3 at the participant-record layer:

1. recover the 16-byte Cup participant record types/fields and the allocation instructions that create them;
2. reproduce the participant source order entering each round;
3. finish comparator `0x4F67D0` and the qsort that runs after each round's mandatory Fisher-Yates;
4. materialize exact club/winner-reference pairings and generated Cup matches;
5. then resume Gate 4 with those Cup schedule nodes inserted into the already-recovered global bucket placement/shuffle.

Commit each participant/allocation/pairing boundary separately.

## Gate 3 completion criteria (reopened)

- [x] One shared MSVC CRT RNG stream covers the mapped pre-competition startup phases.
- [x] Fixed-seed intermediate checkpoints exist for those phases.
- [x] Python-RNG startup fallbacks are isolated/removed.
- [x] Cup round scheduler RNG call count before primary `0x615BE0` is fully included.
- [x] Corrected hidden CRT state entering primary `0x615BE0` is reproducible and canonically verified.
- [x] Exact bounded-call ordering is materialized and canonically verified.
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

- exact Cup participant-shuffle ordering/pairing output before primary `0x615BE0` is still being materialized;
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
