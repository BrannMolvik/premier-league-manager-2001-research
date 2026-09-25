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
- Latest reconstruction-suite validation: `a7785c42f6ceeea31d00ec13dc8f0cc731176758` - **323 tests passed**
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

Materialize the exact primary Cup scheduler RNG order and pairing output.

Continue by:

1. reproduce the canonical country/root competition initialization order used before primary `0x615BE0`;
2. place the Champions League / UEFA Cup selector draws at their exact positions within that order;
3. reproduce each Cup's runtime round ordering;
4. for every NormalRound / TwoLegRound / MiniLeagueRound, execute its exact descending Fisher-Yates bounds rather than merely advancing raw CRT state;
5. materialize the resulting participant pairings/matches needed by the primary schedule;
6. once those Cup schedule nodes are reproducible, return to the already-valid Gate-4 bucket-placement work and propagate the corrected CRT stream through buckets 0..53 into PL bucket 54.

Commit every verified ordering/pairing boundary separately.

## Gate 3 completion criteria (reopened)

- [x] One shared MSVC CRT RNG stream covers the mapped pre-competition startup phases.
- [x] Fixed-seed intermediate checkpoints exist for those phases.
- [x] Python-RNG startup fallbacks are isolated/removed.
- [x] Cup round scheduler RNG call count before primary `0x615BE0` is fully included.
- [x] Corrected hidden CRT state entering primary `0x615BE0` is reproducible and canonically verified.
- [ ] Exact bounded-call ordering and Cup pairing output are materialized for schedule reconstruction.


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
