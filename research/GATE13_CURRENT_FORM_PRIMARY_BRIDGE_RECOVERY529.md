# Recovery529 — bounded original Current Form primary GameState source bridge

**11 October 2026 KST; Gate 13 OPEN; Codex R1 protected.** Original private PE evidence preserved in Recovery 518–528 (SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`). This branch does not launch the original game, copy binary assets or touch Codex's pending NEXT/match lifecycle.

## Original source and port defect

Native `0x4F4970` scans the selected primary/secondary `ScheduleContainer` per DBRClub +0x74 and native source League owner, uses strict `0x615ED0` bit5/wrapper/bit6 gates and native `LeagueMatch::0x513F70` signed score words. A still-unplayed 0–0 on the eligible date can count as a draw. `0x4F3B70` selects the secondary calendar for root source competition class2/3; `0x510380` writes each native Match +0x0C bit0 from actual selected ScheduleContainer.

The reconstruction retains `GameState.primary_schedule_shadow` and `LiveProceduralLeagueState` fixtures/results separately, **not validated original secondary day buckets**. In the current main, `record_procedural_league_result` records in the live league owner; no direct `retain_ordinary_completion` call exists in that method. Whether the broader NEXT flow synchronizes both must be separately established, not assumed. A results-only or last-six API would be a wrong Current Form source.

## Source-backed implementation boundary

`reconstruction/original_league_tables_current_form_game_state.py` is a **read-only, non-presenter** adapter. It requires a real root original League class with native primary schedule, matching full live membership, original byte98 club calendar code1 and native CP1252 name bytes, exact Shadow LeagueMatch tokens and Side cache, known flags/link states, full procedural fixture registry, source day and schedule horizon, and agreement between original bit0 and live result registry. It never derives bit0 from scores or treats unknown scores as a played draw. The original Current Form kernel alone produces the six W/D/L cells and source sort.

It **rejects** category2/3 clubs, source secondary competition containers, foreign/missing member references, unknown or duplicate tokens, unknown native flags, unqualified linked state, missing schedule horizon and score/completion discrepancies. Tests include actual original eligible-unplayed 0–0 conditional, played win/loss, both flag divergences, source membership/Side mismatch, secondary rejection, unknown links and no mutations. These are source-scoped synthetic tests, **not Windows visual/original process acceptance**.

## Still incomplete and exact next steps

1. Independent review/CI of this PR at exact head; fix tests or reject scope if source contradiction is found. Do not touch Codex R1.
2. Investigate why/where procedural result paths update original shadow +0x44 bit0, including post-ponement. The adapter intentionally refuses a live result whose original shadow bit0 is still clear. Do not patch match lifecycle on the protected R1 branch.
3. Source-recover secondary calendar persistence, first/second season dynamic club+0x74 mode, actual native Current Form alternate 0x2B0 row widget coordinates/font and radio WM_LBUTTON ownership. Only then join player-visible PLeagueTables in a disjoint reviewed worker PR.
4. Gate13, Gates14–17, complete original-country/league feature scope and physical Windows11 release remain OPEN; this bridge alone is not a feature restoration or a passed gate.

## Recovery530 source-owner follow-up (no new native executable execution)

The original League Tables base source owner is a **root League** in the corresponding source country, as already required by `original_league_tables_live_source.py` (native `0x4F4940` and DBRCompetition parent/country fields). Recovery529's initial bridge validated type and container but not root parent/country, which could accept an unrelated child-context League with a colliding context-zero fixture owner. The bridge now rejects nonroot competitions, missing original country identity, or any source club whose country does not equal selected root country. Three new independent negative cases cover wrong parent, foreign club and missing country. Still no visible UI or broad secondary history claim.
