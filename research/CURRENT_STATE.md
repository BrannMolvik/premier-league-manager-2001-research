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
  Historical Gate-8 checkpoint used schema 2; current Gate-9 transfer runtime
  uses schema **4**, gzip `.fm2k` files.
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
4. **Completed:** selling-club core decision at `0x4EF940`: protected
   under-30/top-11 players reject below 60% value as Too Cheap; clubs with
   fewer than 17 `0x405080` count reject as Too Small Squad; otherwise
   Offer Accepted. Exact RTTI reason events are mapped and the pure decision
   is implemented/tested.
5. **Completed:** `0x4205A0/0x4205F0` player valuation is reconstructed and
   bound to live source-backed GameState tables. **Completed:** `0x405080`
   excludes transfer-listed, injured, loaned-out and suspended players; both
   formerly-unknown bits are proven and schema-4 saves persist them.
6. **Completed:** ordinary cash-only proposal setup uses +0x14/+0x15 = 0/0;
   canonical 0x4EFA20 then equals the cash fee exactly. A live cash bid now
   creates proposal/deal/bid-log state first and evaluates the seller decision
   from current valuation/age/squad inputs.
7. **Partially completed:** exact 0x4EDB10/0x4EE180 player counter-offer
   transform is implemented and tested: 110% tolerance, anchor midpoint/current
   wage floor, same-club signing-fee skip, and RNG(3) -> 24/36/48 months.
   Response code 1 is proven Counter Offer; code 2 is proven Player Accepts.
8. Promote the live 0x420180 wage expectation and 0x4202A0 signing-fee
   expectation helpers from AccessSkillFinancialValues/current club context,
   then reconstruct the remaining ordinary 0x422470 accept/counter/refuse
   policy needed to drive those response codes from live state.
9. **Completed for ordinary cash conclusion handoff:** code-2 acceptance
   reaches Player Accepts -> Confirm Conclude/Deal Concluded -> shared
   0x4EF600(proposal,0), which schedules MPMTransferPlayer for +1 day.
   Ordinary cash does not require an invented CDealInProgress 0->1 promotion;
   0x422920/0x50E760 belongs to swap/try-execute paths.
10. Implement the normal MPMTransferPlayer completion slice over the modern
    runtime: persisted +1-day scheduled transfer, exact contract application,
    safe club-roster movement, join-date/signing-bit reset and movement history.
    Keep the unresolved Gate-10 cash/budget posting as an explicit external
    affordability dependency rather than inventing finance state.
11. Then add AI transfer progression and synthetic/canonical regressions before
    re-auditing every Gate-9 criterion.

## Gate 9 completion criteria

- [x] Initial player weekly wage and contract expiry are represented and saved.
- [x] Full negotiated contract terms / proposal/deal/bid-log/movement state are represented and saved.
- [x] Ordinary cash-only bids can be submitted and evaluated end-to-end from live runtime inputs.
- [x] Core clubs accept/refuse decision/reason logic is reconstructed and tested.
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
