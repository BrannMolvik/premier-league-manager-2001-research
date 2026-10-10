# Recovery485 — original League Fixtures current-manager selector vs hardcoded Premier League

_10 October 2026 KST; STRICT AUDIT ONLY, following the new original-reference and complete-playability protocol. Original source is from previously hash-verified Recovery154; no fresh original process, original Windows playtest, game implementation, tests or CI in this checkpoint._

## Original identity and complete user journey

The authorized original `footballmanager.exe` has 4,714,541 bytes and canonical SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Independent first-hand original source report: `research/GATE13_LEAGUE_FIXTURES_RESOURCES.md`, “Recovery 154 country and League selector closure” (~lines446–584). The resource/matrix source was previously recovered; it does **not** count as running the original game today.

Entry is PMenu **League Fixtures child 0x25C**, factory `0x47C724→0x46D470`, native `PLeagueFixtures` vtable `0x7C24B8`. Its source constructor `0x46AA70` creates **eight `fmRadioTextSm` country controls** and **six League controls** (0x4C stride). Country order and events are exact: England26/event1, Germany33/2, Italy40/3, Spain73/4, Scotland66/5, France31/6, Holland24/7, Belgium9/8. League radio events are9–14.

The **current selected manager's club** supplies `DBRClub+0x14` country ID, selecting panel country index `+0x64`. The club's League ID at `DBRClub+0x10` resolves via `0x4056F0→0x4F3B10`, then `0x410FF0` finds its identity in the selected country's League list and stores the **per-country selected-League index** at `PLeagueFixtures+0x68+4*country_index`. `0x46D840` filters LeagueBase pointers with native RTTI cast to actual League, binds up to six native `League+0x14` captions and hides absent radio entries.

Original `PLeagueFixtures::0x46E040` country events1–8 update country, rebuild League list via `0x46D840`, rebuild **that selected competition's** fixture matrix via `0x46D950` and refresh via `0x46DCD0`. League events9–14 change the corresponding per-country index and rebuild matrix/refresh. The fixture/member source is the selected competition's `0x4F4940` prepared list with a per-fixture competition identity filter. Selector state for a different country occupies a separate slot. Original keyboard handling, actual panel return under every nested modal, save persistence for radio selection, visible frames and multiuser transitions remain UNKNOWN. Do not invent any of those behaviors.

## Present merged reconstruction — confirmed wrong content owner

Current code was inspected at post-PR562 `main` (application files unchanged through audit start `8ceec58a72e0eeade3841ee0fb1be6f1af84dfd8`); Codex branch `e166ae4d70c32b41f8dcef86b3d3d42b19a24262`.

- `reconstruction/original_management_presenter.py::build_management_panel_snapshot` ~210–225 handles normal PMenu 0x25C by **`bridge.league_fixtures_grid_source()`**, then `build_league_fixtures_snapshot`. It does not pass current manager's country/League.
- `reconstruction/gate13_management_source_data.py::league_fixtures_grid_source` ~2149–2230, blob `4181db2efc218f5bf5c026767b111b3394b7789f`, always loads **`state.premier_league`** members/table, **`state.competitions.get(0)`** and explicitly returns `competition_id=0`. Its `fixture_rows()` ~2074 always uses Premier League fixtures, results and round dates. This method never calls `_human_club_id()`; it cannot represent a current non-PL club's League.
- `reconstruction/original_league_fixtures_presenter.py::build_league_fixtures_snapshot`, blob `b1d6d3f7c06aec6c8d68c2bab36e919da4a1162b`, consumes the already fixed PL source and cannot recover missing chosen competition data.
- The original selector functions **already exist** under `reconstruction/original_league_fixtures_resources.py`, blob `7d182f0c08eb8397dcf44089b45256b50a4f5688`: `league_fixtures_country_selector_for_club_country`, `league_fixtures_selected_league_index`, `league_fixtures_league_selectors`, `league_fixtures_selector_event` (~lines352–467). They are source-derived but not connected to the live panel. Do not re-reverse-engineer them.

**Concrete non-PL test context:** original-aware Southport club349 career has a live primary League node `('league_match',27,0,18)` in the canonical source probe (`research/GATE13_NEXT_EVENT_LIFECYCLE_2026-10-10.md`). Original PLeagueFixtures opens on the current user's country/League. In the current normal management menu its source bridge still builds **Premier League competition0**. That is WRONG content for a valid user whose current League is not0. A Premier League club may receive a correct initial PL matrix, but the cross-country and six-League UI still cannot work.

The **different** `ManagementSourceDataBridge.league_table_rows()` also uses `state.premier_league_table()`, but whether original `PLeagueTables` must initially follow exactly the same selector lifecycle has **not** been proven here; audit separately instead of copying this finding into another class.

## Completeness and evidence matrix

| Feature/owner | Original source | Current implementation | Status |
| --- | --- | --- | --- |
| PMenu0x25C → PLeagueFixtures | 0x47C724→0x46D470 | Actual integrated PMenu content case | PARTIAL |
| Current human club's country/League default | DBRClub+0x10/+0x14→0x410FF0, per-country selected index | Always Premier League competition0 | **WRONG** for valid non-PL human |
| Eight country/six League radios, events1–14 | 0x46AA70/0x46D840/0x46E040 | Helpers only; no normal radio action/selection | **MISSING** |
| Selected competition matrix, prepared members/fixture dates | 0x4F4940/0x46D950/0x46DCD0 | Only PL fixture rows and matrix | PARTIAL, WRONG by selected context |
| Native original runtime observation / Windows11 full input | Not executed this turn | Not acceptance tested for this path | NOT OBSERVED / NOT VISIBLE-ACCEPTED |
| Modal/return, multi-human, save of radio indices | Needs full original source/input validation | Single-human/limited screen owner | PARTIAL / UNKNOWN |

**Player impact:** significant Gate13 **P0 wrong integrated screen**, not a cosmetic difference. The game supplies unrelated Premier League fixtures when managing a qualified non-Premier League club. The mismatch follows directly from source vs current code, not from a claimed screenshot or original game runtime observation.

## Codex-only minimal correction and testable journey

1. After normal menu child0x25C, bind source-qualified current selected human club country and League identity using the **already recovered** radio/source helper functions; never silently default unknown current manager's league to PL0. Fail closed if valid original country/League/RTTI cast or fixture source cannot yet be modeled.
2. Prepare selected League's **real members, source order, fixtures and results** and preserve native matrix/scroll/grid art. Never splice an unrelated procedural cup into a League selector, and do not fabricate a generic modern chooser.
3. Wire actual accepted source country events1–8 and League events9–14, per-country selected-index retention, matrix rebuilding and return. Test original entry and conditional/disabled alternatives.
4. Acceptance: TeamSelect PL manager→PMenu0x25C→PL; TeamSelect Southport349→PMenu0x25C→its actual League, **not PL**; change England/Germany or other source-valid country and League, return, revisit, inspect clicked original fixture and PMatchInfo; compare the correct clubs/dates across normal 1x/1.5x Windows11 physical pointer input. Later test manager rotation in one 2–6-user save. Preserve true original Save/Load, Inbox and NEXT→PPreMatch→match→PResults→return as higher-priority playability gates.

**Evidence grade:** original control/selection and matrix **SOURCE-VERIFIED** (previous first-hand PE); reconstruction mismatch **CODE-CONFIRMED**; original-game observation **NOT performed**; normal Windows11 integration/visible acceptance **NOT performed**. Strict `worker_role=audit_only`, `implementation_allowed=false`; no gameplay edit, test, asset, CI, merge or gate closure. **Gate13 OPEN; Gates14–17/full original-scope Windows11 release incomplete.**
