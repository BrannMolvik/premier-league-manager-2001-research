# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. It is intentionally short. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 2 - Finish the startup RNG chain**

Gate 1 (repository stabilization) is complete. See `../ROADMAP.md` for gate definitions and completion criteria.

## Porting mission

The project is now explicitly a **Windows 11 modernization/port**, not a strict clean-room-only replacement.

The project owner has confirmed that the supplied FM2001 archive/disc contents are authorized for project use. Future work should therefore preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical. Modern code should replace the incompatible runtime/game logic while keeping the original player-visible experience as intact as possible.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Latest reverse-engineering checkpoint before stabilization: `1014b042a19fc851b8d87e653ee1e5d807816630` - **Advance startup RNG boundary before TeamSelect click**
- Latest reconstruction-suite validation: `c5d040f36e5ff20e13ee962b3df5ea2c854a8582` - **309 tests passed**
- Latest repository asset-policy validation: `17ee2f299a2a0d87f959b9480df9b48d194de6aa` - **passed**
- Commits after `1014b042...` are repository-management, documentation, verification/CI hardening, and the Windows 11 port/authorized-asset policy transition. They do not supersede the latest reverse-engineering address/path findings.

## Gate 2 objective

Close the remaining mandatory new-game RNG path before the first Premier League schedule shuffle.

The reconstruction already has:

- the exact MSVC CRT RNG primitive;
- DBRPlayer constructor/startup draws on the shared CRT stream;
- generated-name and per-user youth RNG helpers;
- recovered competition/schedule RNG consumers;
- exact schedule bucket head insertion;
- descending Fisher-Yates shuffle;
- fixed Premier League fixture source/insertion order;
- Premier League schedule-container selection.

What remains is to prove which mandatory RNG consumers can occur **before** the already bounded TeamSelect click-to-new-game path and survive into the first Premier League shuffle state.

## Last verified technical boundary

The concrete TeamSelect Start/Continue click path consumes **zero CRT RNG draws** before `0x4C41C0`.

Inside the subsequent new-game path:

- the TeamSelect prefix through `0x4C42EE` is zero-draw;
- `0x413830` is the recovered generated-name / per-user youth RNG block;
- the path after `0x413830` through `0x4F7C00` is zero-draw;
- RNG-active competition/schedule work beneath `0x4F7C00` is separately mapped.

Therefore the remaining uncertainty has been pushed backward to the TeamSelect panel lifetime/activation path before the user presses Start/Continue.

## Exact next task

The Loader444 side effect is implemented/tested, and a false startup lead has been removed:

- `0x432190` is a later route that requires an existing current user;
- the ordinary front end can create PStartMenu through generic screen factory `0x47AEC0`;
- **screen ID `0x323` -> `0x47C928 -> 0x4C3280` PStartMenu**.

Continue Gate 2 on the actual first-start chain:

1. trace post-intro front-end initialization/navigation into screen ID `0x323`;
2. audit any RNG-bearing functions concretely reachable before the user selects New Game;
3. connect that to the already-proven PStartMenu ID-2 -> `0x50D630` -> DBTPlayers path;
4. if no other mandatory consumers exist, assemble the complete seed-to-competition startup RNG ledger.

Do not count RNG from later current-user/calendar routes unless concrete first-start reachability is proven.

Commit each verified boundary and checkpoint unresolved traces after roughly ten minutes.

## Gate 2 completion criteria

Gate 2 is complete when:

- [ ] TeamSelect lifetime/activation path is bounded.
- [ ] Mandatory RNG consumers before schedule initialization are enumerated, or any residual boundary is precisely stated.
- [ ] The RNG state entering competition/schedule initialization can be described from a known seed for the standard new-game path.
- [ ] The resulting findings/implementation consequences are committed and reviewed against `FINDINGS.md`.

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
