# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. It is intentionally short. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 3 - Build an executable startup RNG ledger**

Gates 1 and 2 are complete. See `../ROADMAP.md` for gate definitions and completion criteria.

## Porting mission

The project is now explicitly a **Windows 11 modernization/port**, not a strict clean-room-only replacement.

The project owner has confirmed that the supplied FM2001 archive/disc contents are authorized for project use. Future work should therefore preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical. Modern code should replace the incompatible runtime/game logic while keeping the original player-visible experience as intact as possible.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Latest reverse-engineering checkpoint before stabilization: `1014b042a19fc851b8d87e653ee1e5d807816630` - **Advance startup RNG boundary before TeamSelect click**
- Latest reconstruction-suite validation: `52d5b4c2eaa9535a67a73b484e712fe0043306b5` - **312 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 3 objective

Turn the now-closed seed-to-competition RNG research into one executable replay with fixed-seed intermediate checkpoints, then continue that exact shared CRT stream through primary competition initialization to the first Premier League schedule-bucket shuffle.

Canonical pre-competition evidence: `STARTUP_RNG_LEDGER.md`.

## Last verified technical boundary

The concrete TeamSelect Start/Continue click path consumes **zero CRT RNG draws** before `0x4C41C0`.

Inside the subsequent new-game path:

- the TeamSelect prefix through `0x4C42EE` is zero-draw;
- `0x413830` is the recovered generated-name / per-user youth RNG block;
- the path after `0x413830` through `0x4F7C00` is zero-draw;
- RNG-active competition/schedule work beneath `0x4F7C00` is separately mapped.

Therefore the remaining uncertainty has been pushed backward to the TeamSelect panel lifetime/activation path before the user presses Start/Continue.

## Exact next task

The complete pre-competition sequence is now executable on one shared `MsvcCrtRng`, with fixed-seed intermediate checkpoints after Loader444, DBTPlayers, generated names, and youth generation.

Continue Gate 3 at the primary/mode-0 competition boundary:

1. close the residual argument-1 `0x404110` / `0x50EA90` team-setup RNG audit before `0x615BE0`;
2. implement the proven Europe-root competition draws in exact order:
   - Champions League: `RNG(6)`
   - UEFA Cup: `RNG(6)`;
3. add a fixed-seed checkpoint for the exact CRT state entering `0x615BE0`;
4. if no other primary-container consumers remain, complete Gate 3 and hand exact bucket-shuffle ordering to Gate 4.

Commit each verified research/implementation boundary separately.

## Gate 3 completion criteria

- [ ] One shared MSVC CRT RNG stream is used for all mapped mandatory startup draws.
- [ ] Fixed-seed tests verify intermediate state, not only final output.
- [ ] Legacy Python-RNG fallbacks are removed or isolated where original behavior requires CRT RNG.
- [ ] Remaining uncertain competition consumers before the first PL shuffle are explicitly documented or resolved.


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

- incomplete global CRT state before the first PL shuffle;
- deterministic fixture-ID same-day fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- absence of real-data full-matchday/full-season automated integration;
- incomplete human management, transfers/contracts, finance/board, broader competitions, save compatibility, faithful UI, and FastView/3D.

## Do not work on yet

Unless required to unblock Gate 2, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competitions;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
