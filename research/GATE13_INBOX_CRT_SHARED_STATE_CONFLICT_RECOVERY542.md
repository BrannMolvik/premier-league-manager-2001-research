# Recovery542: BLOCKED native Inbox first-click shared CRT reconciliation

## Original evidence

Original authorized `footballmanager.exe` 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original native Inbox first selection `0x471B80` calls EAMPlayerAskTransferListsub virtual +0x1C argument0, branch `0x56FD65`; when native record+0x3C reason = -1 it uses `0x66951C` CRT rand15, original 7-way nonuniform `max(1,(rand15*7)//32767)`, stores reason and invokes typed text formatting. Native `0x66951C→0x66D553` reads/writes **the CRT thread-local data seed+0x14** (TLS via original 0x7BD1C8/0x7BD184). One source-thread's CRT draws cannot safely be split into arbitrary separately seeded per-subsystem modern streams. Native shared seed for true first-click after all original startup and daily/background events has not yet been observed or established.

## Critical reconstructed integration counterexample

The existing normal reconstruction has **two separately initialized MSVC CRT objects**, not a proven one-native-thread stream:
- `reconstruction/game_state.py::GameState.from_database`, original startup player and following gameplay state, creates `rng=MsvcCrtRng(int(seed))` and stores `state.rng`. `GameState._resolve_rng` defaults many daily/training/AI and simulation routines to this RNG. Actual player startup consumes it.
- `reconstruction/human_gameplay.py::HumanGameplayController.from_verified_canonical_database` reconstructs primary schedule and separately passes `MsvcCrtRng(primary_schedule.state_after)` as `controller.match_rng`. Several reconstructed match contexts explicitly consume `controller.match_rng` while many original gameplay actions use `state.rng`.
- `reconstruction/internal_save.py` persists **both** `game_state.rng_state` and `control.match_rng_state` independently. There is no native source proof here that the two represent separate original TLS threads or how to unify existing saves without replay divergence.
- The source-path `original_game_host.py::_press_original_eamail_row` proposed in PR638 currently blindly uses `game.match_rng` at accepted first click, not `state.rng` and not a proven reconciled CRT TLS seed. For an ordinary game that can consume the wrong RNG stream even though `rand15` arithmetic and modern data persistence are internally correct. A synthetic test deliberately seeded `match_rng` separately and did **not** establish original gameplay seed/ordering.

**Classification: source semantics verified, reconstructed full gameplay first-click integration DISPUTED/UNACCEPTED.** External Windows gameplay acceptance remains nonexistent, and Gates13–17 OPEN.

## Containment and exact next action

PR [#638](https://github.com/BrannMolvik/premier-league-manager-2001-research/pull/638), head `21b65927fa829436be2b44308a3b0576303a9e45`, is kept **DRAFT/BLOCKED** and must **NOT be merged** until independent shared-state proof and cross-system high-risk review. Its tests and implementation are only experimental candidate work on worker branch, not main. Even green exact-head Gate13/full/package/asset CI does NOT remove the divergence risk.

Next for this exact task: reconstruct original CRT TLS creation/identity across fresh startup/player and scheduler state checkpoints, daily timer/transfer draw order, human first Inbox click and selected-user rotation; compare with both `state.rng` and `controller.match_rng` in current normal game. Establish a single qualified per-original-thread ownership and save/restore migration strategy or retain fail-closed separation if impossible. Run original-derived fixed-seed sequence tests spanning startup, first press and subsequent simulation, check no second-click re-roll, multi-human switching and full career save/resume, obtain independent supervisor review. Then only integrate first-click raw reason mutation to main. Independently continue original manager/player dynamic rich-tag text renderer/preview source without relying on the disputed RNG.

No unapproved original EXE execution or native GUI acceptance.
