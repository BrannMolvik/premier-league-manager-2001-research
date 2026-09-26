# Current State

_Last reconciled: 27 September 2026_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 9 - Transfers and contracts**

Gates 1 through 8 are complete. Gate 8 closed after the modern port gained a
versioned internal save format, exact save/reload continuation through a
mid-matchday human fixture boundary, multi-week canonical equivalence, and
Save/Load controls in the temporary playable UI.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Preserve and reuse original data,
music, sounds, interface graphics, strings, and other resources wherever
technically practical while replacing incompatible legacy runtime/game logic.

Authorized original resources belong under `original_assets/` with provenance
tracked according to `ASSET_POLICY.md`.

## Verified repository state

- Gate-8 evidence: `research/GATE8_INTERNAL_SAVE.md`.
- Gate-8 canonical audit runner:
  `reconstruction/canonical_internal_save_audit.py`.
- Internal save implementation: `reconstruction/internal_save.py`.
  Historical Gate-8 checkpoint used schema 2; current Gate-9 contract runtime
  uses schema **3**, gzip `.fm2k` files.
- Reconstruction GitHub Actions at
  `72c21e8f07bf9bf57f6dc3cbaba83809cdd06414`: **413 tests passed**.
- Repository asset-policy workflow at that checkpoint: **passed**.
- Canonical executable SHA-256:
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

## Stable startup / scheduler checkpoint

A Gate-9 contract trace exposed one previously omitted unconditional weekly-wage
RNG call per DBRPlayer inside `0x418B90 -> 0x423A50`. The full correction and
Gate-3-through-Gate-8 re-baseline are in
`research/STARTUP_WAGE_RNG_CORRECTION.md`.

Corrected canonical path through primary schedule finalization:

- DBTPlayers startup RNG: **180,384 calls** for 30,064 players;
- synthetic post-youth state: **`0x4B68DE28`**;
- actual-count primary competition RNG: **5,836 calls**;
- state entering primary `0x615BE0`: **`0x4F5CF274`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0xD25DFFE6`**;
- first PL fixture order: **0, 6, 8, 5, 1, 9, 3, 2, 4, 7**.

Gate-4 historical evidence remains in `research/GATE4_SCHEDULE_ORDER.md`;
corrected deterministic values are authoritative in the correction note.

## Stable autonomous and human gameplay checkpoints

Gate 6 completed three deterministic canonical 38-round / 380-fixture Premier
League seasons.

Gate 7 completed a canonical six-fixture Arsenal human-manager run from
19 August through 23 September 2000, with all surrounding PL fixtures continuing
in recovered scheduler order.

Evidence:
- `research/GATE6_FULL_SEASON.md`
- `research/GATE7_HUMAN_GAMEPLAY.md`

## Gate-8 internal save checkpoint

Schema 2 persists the Gate-7 gameplay state, including calendar/scheduler
state, runtime player development and availability, Condition/Form,
injuries/suspensions, tactics, PL results, Pitch Wear, human XI/bench and Team
Orders, both relevant CRT RNG streams, and pending same-day match state.

Canonical mid-matchday save:

- save date: **26 August 2000**;
- seven earlier same-day AI fixtures already complete;
- Arsenal fixture ID **20** pending;
- later same-day fixtures **22** and **29** pending;
- raw deterministic JSON: **6,535,498 bytes**;
- gzip save: **998,022 bytes**;
- source signature:
  `6ba4b9c3bce385f084053d7b0ef13595652e3335ac7ea04991637281785668cc`;
- raw save SHA-256:
  `0eac6a1c5ddd248c76f153b2a274d334240fd0ec72cdc494331cb543e37838f6`.

After the startup-wage correction, the 26 August scheduler puts Arsenal's
fixture first on the date, so the save now has **0 prior** and **9 later**
same-day AI fixtures. A fresh database/runtime still remains exactly equal to
the uninterrupted branch through 23 September / 60 PL results.

Corrected Gate-8 final match RNG: **`0xC0009A67`**.

Corrected Gate-8 audit SHA-256:

`25d5a461cf0c7eb4e05ad718d81a81815407deb15c25784eff514842e28d0b03`

Original FM2001 save compatibility is **not** claimed; it remains a separate
fidelity task.

## Gate-9 goal

Make squad building part of the playable season.

Completion requires:

- contract state represented in the modern runtime;
- human bids and club accept/refuse evaluation;
- player wage/duration negotiation;
- completed transfers moving players safely between rosters;
- transfer state surviving Gate-8 save/reload;
- AI transfer activity during calendar progression.

## Exact next task

1. **Completed:** authentic starting weekly wage from
   `DBTAccessSkillFinancialValues` + country multiplier, plus exact initial
   12/24/36/48/60-month contract expiry.
2. **Completed:** current internal save schema **3** persists weekly wage and
   contract expiry.
3. **Completed:** persistent proposal/deal/bid-log/movement state is attached
   to GameState and round-trips through schema-3 saves. CI at `8f7936d9`:
   **424 tests passed**.
4. Recover the selling-club accept/refuse decision/reason-code path without
   approximating known decline reasons.
5. Implement the smallest end-to-end human transfer path: bid -> club decision
   -> player negotiation -> completion -> roster movement.
6. Add AI transfer progression only after the human path/state model is stable.
7. Build synthetic and canonical regressions and re-audit every Gate-9 criterion.

## Gate 9 completion criteria

- [x] Initial player weekly wage and contract expiry are represented and saved.
- [x] Full negotiated contract terms / proposal/deal/bid-log/movement state are represented and saved.
- [ ] Bids can be made and evaluated.
- [ ] Clubs accept/refuse according to reconstructed logic where known.
- [ ] Player negotiations, wages, duration, and transfer completion work.
- [ ] Player movement updates squads safely.
- [ ] AI transfer activity can occur during calendar progression.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. Most relevant now:

- transfers/contracts are researched more deeply than currently implemented;
- Gate 10 finance/budget state is not yet a full runtime subsystem, so Gate 9
  must avoid silently inventing later finance behavior;
- original FM2001 save compatibility remains separate;
- exact final league-table tie fallback remains unresolved;
- persistent-injury availability helper `0x405080` retains an approximation;
- broader competitions, original front-end fidelity and FastView/3D remain later
  gates.

## Do not work on yet

Unless required to unblock Gate 9, defer:

- full finance/board implementation;
- broader competition season-transition behavior;
- original save-file compatibility;
- full original UI fidelity;
- FastView/3D.

Record useful side leads in `BACKLOG.md` instead.
