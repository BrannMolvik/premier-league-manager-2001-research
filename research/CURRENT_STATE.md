# Current State

_Last reconciled: 26 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in `PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and topic-specific research files.

## Current gate

**Gate 3 - Build an executable startup RNG ledger (REOPENED)**

Gates 1 and 2 are complete. Gate 3 was reopened after mandatory competition-startup RNG was found before primary `0x615BE0`. The corrected complete competition RNG replay is now integrated and verified. Gate-4 scheduler groundwork remains valid but is paused until the complete startup schedule-node set is materialized.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc contents are authorized for project use. Preserve and reuse original data, music, sounds, interface graphics, strings, and other resources wherever technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Current verified integration checkpoint: `fba3babd72859d4c932c1aadffc81f6b54e339a0` - **Integrate complete primary competition RNG replay**.
- Reconstruction GitHub Actions at that head: **365 tests passed**.
- Repository asset-policy GitHub Actions at that head: **passed**.
- Canonical executable hash: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Corrected complete primary competition RNG replay

The previously mapped Cup/DummyLeague/Europe-selector stream remains valid, but it is only a subset.

Complete canonical primary competition replay before primary `0x615BE0` now contains:

- **39 procedural League runtime instances**;
- **4,302 procedural-League bounded calls**;
- **1,737 Cup participant-shuffle calls**;
- **124 DummyLeague lazy-ranking calls**;
- **2 Europe-root selector calls**;
- **6,165 bounded calls total**;
- **167 high-level RNG events**.

For the synthetic post-youth checkpoint `0x2797444C`:

```text
0x2797444C
  + complete primary competition replay
= 0x0DD3ACA3
```

The complete ordered-bound SHA-256 is:

```text
3e7accfdf108a48a53902bb32a782fb23c64c7e5ce54eff101e0f869f6c3629c
```

Europe-selector event indices in the complete replay are **137** and **158**. With the synthetic starting state they select clubs **1137** and **1159** respectively.

Filtering procedural-League events out of the complete stream reproduces the older mapped subset exactly:

- 128 events;
- 1,863 calls;
- selector indices 110 / 119;
- ordered-bound digest `a6675e77b8256fcb8d5834efa6a9d006182078c12f27887c8228a14eca889711`;
- subset-only state `0xAECA9FA5`.

Therefore `0xAECA9FA5` must never again be described as the final state entering `0x615BE0`.

## Last verified technical boundary

The startup path through TeamSelect and pre-competition initialization is bounded. The procedural League RNG generator is translated and integrated:

```text
League::Initialize 0x4F5150
 -> procedural builder 0x6170F0
 -> round-robin solver 0x616F20
 -> 0x616EA0
 -> randomized/backtracking selector 0x616CE0
 -> bounded RNG 0x64D540
```

The solver reproduces candidate-list setup, cursor behavior, forced-slot movement, recursive perfect-matching construction, candidate-vector swaps, backtracking, row propagation, and the complete one-cycle round-robin. Backtracking can consume more calls than the number of unique pairings.

Cup schedule-node construction already has direct executable evidence:

- NormalRound scheduler `0x4F64D0`: one `CupMatch` per pairing through `0x510520`, inserted through `0x615950` at the round primary week/day.
- TwoLegRound `0x4F6820`: first leg via `0x510640` at `+0x20/+0x24`; second leg via `0x510680` at `+0x28/+0x2C`; propagated winner ClubRef references the second-leg object.
- MiniLeagueRound `0x4F6B10`: distributes participants into child League objects; those child procedural Leagues emit the group-stage LeagueMatch nodes.
- Generic conflict virtuals `0x510A80` / `0x510A40` use ClubRef identity resolver `0x4F2830`. Resolved refs conflict only on the same resolved club pointer. Two unresolved symbolic refs conflict only when type, referenced runtime object pointer, and selector all match. Direct-vs-symbolic does not conflict.

Gate-4 groundwork remains useful:

- primary schedule container = 373 buckets;
- exact ordinary LeagueMatch conflict-placement search is recovered;
- first Premier League target bucket = 54;
- prior LeagueMatch-only reconstruction found 142 nodes in bucket 54;
- PL fixture IDs occupied pre-shuffle slots 96..105 in order 9..0.

The bucket-54 population/order must be re-audited after Cup and procedural child-League schedule nodes are integrated.

## Exact next task

Continue Gate 3 from the schedule-node layer:

1. Finish direct tracing of **procedural League schedule-node emission in `0x6170F0`**, including:
   - reuse of the randomized one-cycle pairing matrix across `scheduled_matchday_count`;
   - home/away direction and alternating-cycle behavior;
   - exact date selection;
   - LeagueMatch construction and insertion order through `0x615950`.
2. Resolve the conditional parent-vector shuffle around `0x617245..0x617290` for child Leagues whose parent is a Cup/DummyLeague. Confirm whether any canonical startup path consumes additional draws there; do not assume the historical count-one observation without rechecking the actual child contexts.
3. Implement schedule-node descriptors for:
   - NormalRound CupMatch;
   - TwoLeg first/second-leg matches;
   - MiniLeague child LeagueMatch nodes;
   - generic symbolic ClubRef conflict identity.
4. Integrate all schedule nodes into the **actual primary competition initialization order**, sharing the already-correct complete RNG stream.
5. Execute the complete materializer against canonical `Master.dat` / `Static.dat` / STR data and lock:
   - participant digest;
   - pairing digest;
   - schedule-node digest;
   - counts per Cup/round and any dropped refs;
   - confirmation that the complete 6,165-call replay/state/digest is unchanged.
6. Audit Gate-3 completion criteria. If complete, update `ROADMAP.md`, `CURRENT_STATE.md`, `project_status.json`, and `PROGRESS.md`, commit the gate transition, then resume Gate 4.

## Gate 3 completion criteria (reopened)

- [x] One shared MSVC CRT RNG stream covers the mapped pre-competition startup phases.
- [x] Fixed-seed intermediate checkpoints exist for those phases.
- [x] Python-RNG startup fallbacks are isolated/removed.
- [x] Cup round scheduler RNG is included.
- [x] Procedural-League round-robin RNG is translated and integrated for every primary runtime instance.
- [x] Final hidden CRT state entering primary `0x615BE0` is reproducible for the complete mapped competition replay.
- [x] Exact bounded-call ordering, including DummyLeague lazy sorts and Europe selectors, is canonically verified.
- [ ] Complete canonical Cup/League participant, pairing, and schedule-node outputs are materialized and digest-locked for global schedule reconstruction.

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
- startup/schedule RNG primitives;
- exact legacy CRT qsort behavior;
- Cup allocation, participant, pairing, and cross-Cup transfer materialization;
- procedural League round-robin RNG generation.

## Known live fidelity boundaries

See `FIDELITY_GAPS.md` for the canonical list. Most relevant now:

- complete startup schedule-node emission is not yet materialized;
- MiniLeague child procedural-League match emission still needs the final direct trace/implementation;
- exact inter-bucket RNG consumption/order inside primary `0x615BE0` is Gate-4 work paused behind Gate 3;
- deterministic fixture-ID same-day fallback;
- unresolved final league-table tie fallback;
- approximation around persistent-injury availability helper `0x405080`;
- absence of real-data full-matchday/full-season automated integration;
- incomplete human management, transfers/contracts, finance/board, broader competitions, save compatibility, faithful UI, and FastView/3D.

## Do not work on yet

Unless required to unblock Gate 3, defer:

- transfers/contracts implementation;
- finance/board implementation;
- broader competitions;
- UI fidelity;
- FastView/3D;
- original save compatibility.

Record useful side leads in `BACKLOG.md` instead.
