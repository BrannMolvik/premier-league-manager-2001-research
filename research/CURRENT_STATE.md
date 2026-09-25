# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. It is intentionally short. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 4 - Resolve exact Premier League matchday ordering**

Gates 1, 2 and 3 are complete. See `../ROADMAP.md` for gate definitions and completion criteria.

## Porting mission

The project is now explicitly a **Windows 11 modernization/port**, not a strict clean-room-only replacement.

The project owner has confirmed that the supplied FM2001 archive/disc contents are authorized for project use. Future work should therefore preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical. Modern code should replace the incompatible runtime/game logic while keeping the original player-visible experience as intact as possible.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Latest reverse-engineering checkpoint before stabilization: `1014b042a19fc851b8d87e653ee1e5d807816630` - **Advance startup RNG boundary before TeamSelect click**
- Latest reconstruction-suite validation: `52d5b4c2eaa9535a67a73b484e712fe0043306b5` - **312 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 4 objective

Replace the deterministic fixture-ID same-day fallback with the original primary schedule-container ordering.

The exact shared MSVC CRT state entering primary `0x615BE0` is now reproducible. Gate 4 must carry that state through the schedule buckets in their original order and recover the exact linked-list order for Premier League matchdays.

Canonical startup evidence: `STARTUP_RNG_LEDGER.md`.

## Last verified technical boundary

The concrete TeamSelect Start/Continue click path consumes **zero CRT RNG draws** before `0x4C41C0`.

Inside the subsequent new-game path:

- the TeamSelect prefix through `0x4C42EE` is zero-draw;
- `0x413830` is the recovered generated-name / per-user youth RNG block;
- the path after `0x413830` through `0x4F7C00` is zero-draw;
- RNG-active competition/schedule work beneath `0x4F7C00` is separately mapped.

Therefore the remaining uncertainty has been pushed backward to the TeamSelect panel lifetime/activation path before the user presses Start/Continue.

## Exact next task

Gate 4 now has the exact nominal bucket coordinate system:

- primary container has 373 buckets and `0x615BE0` traverses indices 0..372;
- League round target offset is `7*scheduled_week + (scheduled_weekday-1)`;
- first Premier League round targets bucket 54;
- `0x615950` can move individual nodes from their nominal target through `0x615890` conflict resolution.

Continue by:

1. resolve the `0x615790/0x615890` conflict predicates and outward search rules;
2. reconstruct final primary bucket placement in original competition/insertion order;
3. enumerate bucket sizes/order for indices before and including first PL target 54;
4. propagate the Gate-3 CRT state through those bucket shuffles and derive exact first-PL-matchday order;
5. extend to later PL matchdays and regression tests.

Commit each verified scheduler boundary separately.

## Gate 4 completion criteria

- [ ] Premier League source fixture insertion order is preserved.
- [ ] Schedule bucket/container selection is reproduced.
- [ ] Shuffle input RNG state is reproduced through all preceding buckets.
- [ ] Same-day Premier League extraction/execution order is reproduced.
- [ ] Regression tests cover the first several real matchdays.


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

- exact inter-bucket RNG consumption/order inside primary `0x615BE0` is still being completed;
- deterministic fixture-ID same-day fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- absence of real-data full-matchday/full-season automated integration;
- incomplete human management, transfers/contracts, finance/board, broader competitions, save compatibility, faithful UI, and FastView/3D.

## Do not work on yet

Unless required to unblock Gate 4, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competitions;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
