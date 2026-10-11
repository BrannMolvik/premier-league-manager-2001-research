# Recovery527 — preserve native pre-match input after transactional Quick failure

11 October 2026 KST, Gate 13 remains OPEN.

## Existing shipped-source evidence

Original native `PPreMatchPanel` exists as the match mode modal at `0x499C30` with source accepted selectors `0x49AB50` and commit `0x49ABA0`, storing one of 0,1,2,3 into `0x877530`, signaling original owner and closing it. Explicit selector ID1 means **Quick Match (mode3)**. The original `LeagueMatch::0x513010` computes its human match after the necessary choice and returns through the original PResults/NEXT continuation. Established from prior canonical executable evidence: `research/GATE13_R1_MATCH_PHASE_INTEGRATION_2026-10-11.md`, `research/GATE13_PREMATCH_READY_SOURCE_MODULES_VS_MISSING_GUI_HANDOFF_RECOVERY472.md`, `research/GATE13_PRESULTS_REAL_PROGRESS_EVENT_OWNER_AUDIT_RECOVERY444.md`. Canonical original EXE previously hash-proven (now verified in private Drive): `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. No original game process or actual Windows GUI was run for this recovery.

## Confirmed current reconstruction error

The merged R1 Tk path cleared `prematch_surface` *before* starting a speculative staged Quick calculation. A source boundary exception leaves the actual live `pending_primary_entry` unchanged and `_original_match_input_owner() == 'prematch'`, but its native-source modal artwork becomes unavailable, so no button can be clicked and no management input can escape. Issue #600. This is a modern failure-recovery defect, **not** an assertion that the 2001 binary itself handled Python exceptions or user retries.

## Strict technical compatibility repair

Retain the existing source-verified `prematch_surface` across staging, source-gated worker calculation and errors. Under a running worker, source input owner `results` already suppresses repeated pointer actions; retaining the bitmap does not enable an extra action. Only the successful staged `match_ok` publication clears the old modal. On failed/failed-to-start workers, the exact same object, actual pending original match, current manager/calendar/score and accepted original button remain available for retry. No original modal Escape, Cancel, auto-mode, source-default, alternate presentation, scheduled-event progress, or fake match result is added.

Synthetic host regressions exercise one failing attempt followed by the original Quick ID1 selector again, assert no partial live mutation before retry, background input blocking, single successful publication, and rejected thread startup leaving both thread state and modal intact. These tests demonstrate reconstruction correctness, not a physical 2001/Windows11 playthrough.

**Remaining scope:** actual complete PPreMatch children, all original match modes, true PResults dated-event progress / 800×600 screen and original return branches, user 2–6 player careers, original saves, full playable countries/leagues, original Inbox and verified Windows11 release are not yet complete. All Gates 13–17 remain OPEN.
