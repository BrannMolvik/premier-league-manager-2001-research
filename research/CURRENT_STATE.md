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
- Latest reconstruction-suite validation: `52d5b4c2eaa9535a67a73b484e712fe0043306b5` - **312 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 3 correction objective

Restore the exact shared MSVC CRT state entering primary `0x615BE0`.

The earlier replay correctly covers Loader444, DBTPlayers, generated names, per-user youth generation, and the two Europe-root selector draws, but a Gate-4 audit proved that Cup round scheduling runs before `0x615BE0` and performs additional participant-pairing shuffles.

Canonical startup evidence remains `STARTUP_RNG_LEDGER.md`, but its competition tail must now be amended.

## Last verified technical boundary

The concrete TeamSelect Start/Continue click path consumes **zero CRT RNG draws** before `0x4C41C0`.

Inside the subsequent new-game path:

- the TeamSelect prefix through `0x4C42EE` is zero-draw;
- `0x413830` is the recovered generated-name / per-user youth RNG block;
- the path after `0x413830` through `0x4F7C00` is zero-draw;
- RNG-active competition/schedule work beneath `0x4F7C00` is separately mapped.

Therefore the remaining uncertainty has been pushed backward to the TeamSelect panel lifetime/activation path before the user presses Start/Continue.

## Exact next task

Correct the pre-`0x615BE0` competition RNG ledger.

Confirmed correction:

- Cup initialization calls each runtime round's scheduling virtual before final bucket shuffle;
- type 1 `NormalRound 0x4F64D0` and type 2 `TwoLegRound 0x4F6820` each perform a mandatory participant Fisher-Yates of N-1 draws when N>1;
- type 3 `MiniLeagueRound 0x4F6B10` also contains a direct RNG shuffle;
- therefore the old `0x5D07D526` synthetic "state entering primary shuffle" is provisional/incomplete.

Continue by:

1. map runtime round participant-count initialization for NormalRound/TwoLegRound/MiniLeagueRound;
2. enumerate which primary Cup rounds are active at new-game startup and their N values;
3. resolve the scheduler flag passed from `0x4F62B1..0x4F6321` and any extra parent-vector shuffle;
4. update `competition_startup.py` / `startup_sequence.py` and fixed-seed checkpoints;
5. only after the corrected state is exact, resume Gate 4 using the already-implemented bucket placement logic.

Commit every verified boundary separately.

## Gate 3 completion criteria (reopened)

- [x] One shared MSVC CRT RNG stream covers the mapped pre-competition startup phases.
- [x] Fixed-seed intermediate checkpoints exist for those phases.
- [x] Python-RNG startup fallbacks are isolated/removed.
- [ ] Cup round scheduling RNG before primary `0x615BE0` is fully included.
- [ ] A corrected exact state entering primary `0x615BE0` is locked by tests.


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

- mandatory Cup round pairing/scheduling RNG before primary `0x615BE0` is being corrected;
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
