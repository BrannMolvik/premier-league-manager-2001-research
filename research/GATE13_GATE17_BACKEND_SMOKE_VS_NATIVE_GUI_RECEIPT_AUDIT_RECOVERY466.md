# Recovery 466 — backend smoke receipts versus original Windows 11 GUI acceptance

_10 October 2026 KST. Audit-only continuation from Recovery465; no game implementation or original assets, saves, CI, merge, release or Windows acceptance._

## Verified checkpoint and source

- At start: `main 80c0d3c7e242029e468cf099645d3151c5f96878`, Codex implementation branch `0ae745d1b56f45cade460f03cd893849a2f53b45` (unchanged since 9 October). `ROADMAP.md` explicitly reopens Gate13 due to the real Windows11 regression on **6 October**; GitHub issue [#482](https://github.com/BrannMolvik/premier-league-manager-2001-research/issues/482) remains open. `CURRENT_STATE.md` and agent-runtime assign this worker **audit_only**, `implementation_allowed=false`.
- Original privately authorized `footballmanager.exe`: **4,714,541 bytes**, independently rehashed SHA256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**. No original executable executed or uploaded.
- Codex `reconstruction/gate17_windows_gameplay_receipts.py` verified blob `399d1ea831c8edb3edff509e4e98c2790f87ca2b`; `reconstruction/original_game_host.py` blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`.

## A. Precise coverage of the three existing Windows gameplay receipts

1. **`new_game_management_loop`**: `audit_new_game_management_loop` directly creates a `HumanGameplayController`, selects the **first Premier League club**, autofills XI and five substitutes, calls **`advance_to_next_user_fixture()`** and **`play_user_fixture()`**, and verifies league result insertion. This does NOT construct `OriginalGameHost`, exercise ordinary NEXT/MATCH click ID3, use `advance_original_management_turn`, or test PResults/correct header caption.
2. **`save_reload`**: `audit_save_reload` uses the same prototype backend advancement and `save_human_gameplay` to write a temporary `gate17-smoke.fm2k` and compare `snapshot_human_gameplay` after `load_human_gameplay`. It does NOT exercise original PMenu child0x321, native `PSaveGame`, or source numeric `games/%d.sav` slot actions (Recovery454).
3. **`season_progression`**: `audit_season_progression` runs `run_canonical_annual_rollover_audit`, a valuable canonical backend season test, NOT a normal on-screen repeated NEXT/fixture/formation interaction test.

The runner correctly requires an **external Windows11 workstation** and hashes an actual release archive. Keep these positive constraints. Yet a backend CLI run on Windows does not prove the original-like GUI or match-watch display works: current `on_click` in Codex handles PMenu, Squad row and Fixtures but **not PBg ID3 NEXT**. These claims do not contradict successful controller-only receipts; the layers are separate.

## B. Existing final release gate is stricter — no false bypass claim

`reconstruction/gate17_release_readiness.py` requires **five** distinct external receipts for the exact release commit/archive: clean installation, management-loop backend smoke, season progression, save/reload and **full_original_scope**. That last receipt includes every original selectable country/League, human career and original subsystems, scope save/reload and **multi-human management**; `research/GATE17_FULL_SCOPE_EVIDENCE.md` notes that no complete producer exists while secondary-owner and six-human runtime remain incomplete. Final gate also checks prerequisite roadmap gates and release integrity. **This audit does NOT claim the final release gate can pass from the three backend receipts.** It distinguishes backend proof from user-visible Windows mouse/keyboard acceptance.

## C. Correct historical status contradiction

The `research/GATE17_RELEASE_READINESS.md` report still said “Gate13 is complete; Gate14 earliest incomplete” because it was authored **5 October**. Actual `ROADMAP.md` records Gate13 **reopened 6 October after #482**. The current-status/prerequisite prose and new source-scope note are corrected in this checkpoint; historic completed groundwork and checkbox states are untouched.

## D. Codex-only action and evidence

Prioritize existing issue [#482](https://github.com/BrannMolvik/premier-league-manager-2001-research/issues/482): source-qualified PBg ID3 click → selector ownership and atomic bounded NEXT controller → actual pending human match and PResults return; original Squad 3/4/5, EAMail header/inbox, PSaveGame/Return Menu and 2–6 human managers. Then test **real Windows 11 GUI pointer input** from TeamSelect/Southport, a second club, replay/save/reload and the original on-screen match watch; do not substitute `advance_to_next_user_fixture` API results for that. External original Windows GUI acceptance remains UNKNOWN.

**Gate13 OPEN; Gates14–17 and verified full original-scope Windows11 release incomplete. Audit only; no code/CI/binary/gate modification.**
