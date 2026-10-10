# Recovery508: source-qualified selected other-League ranking producer

11 October 2026 KST; verified main `db0ebc83cb0de89d494dea7e8b370c83cdfd0c41`. Gate13 remains **OPEN**.

## Original-source rationale

Original authorized root `footballmanager.exe` canonical SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original `PLeagueFixtures::0x46D950` follows the country/League radio's actual selected `League*`, calls `League::0x4F4940→0x4F4720→qsort(0x4F45E0)` and walks 373 original primary calendar heads with a strict selected-competition identity filter. It **does not** require current managed club membership in the League being displayed. Existing reconstruction's `source_qualified_procedural_league_table(human_club_id,...)` had a different, unnecessarily manager-only gate.

## This small source-backed step

Added `source_qualified_selected_procedural_league_table(selected_country_id, competition_id,...)` with exact real-root kind1 and country matching, full roster membership, live context-zero result state, CP1252 names, strict original points/played/GD/GF/GA order, no unresolved CRT ties, no unknown fixture participants and no fake current manager. Existing manager-only `source_qualified_procedural_league_table` preserves its caller identity and country guard, and delegates to the same qualified algorithm. This refactor **does not** create a different selected League in existing GUI. Two extra integration tests demonstrate foreign selection without impersonating a user and fail closed for country or incomplete source members.

Exact-head asset, Gate13 and full reconstruction suite checks are required before merging. No original files imported; no Codex R1 host/NEXT/match/results edits. Next functional vertical slice is selected-context authentication→original 373-head calendar fixture source→`LeagueFixturesGridSourceView`→stateful native radio event (once hit accepted). Prem/other League source pathways must stay separate. Actual normal Windows11 screen clickthrough, Gate13–17, 2–6 managers and full original four match modes **remain open**.
