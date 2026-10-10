# Recovery486 — normal League Tables uses Premier League instead of the human's original division

_10 October 2026 KST. Strict audit only, following the original whole-journey protocol. Current main at audit start: `0da0f5ea961dae90672f4d038d8cd288c5b3fb6d`, Codex branch `e166ae4d70c32b41f8dcef86b3d3d42b19a24262`. No game-code, tests, CI, source assets, merges, original-game process or Windows UI work._

## Bounded original proof and player entry

Canonical authorized original `footballmanager.exe`, 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, was previously hash verified. Original `PLeagueTables` TypeDescriptor `0x81B458`, vft `0x7C00C8`, constructor `0x448640`, setup `0x446F00`, native events `0x448C40`. Prior first-hand original PE disassembly `research/GATE13_LEAGUE_TABLES_RESOURCES.md` Recoveries161–162 proves an eight-country selection family at panel+0x1D4/+0x23C (country IDs `26,33,40,73,66,31,24,9`; native event IDs1–8; selected country index panel+0x64). Five **DIVISION** `fmRadioTextSm` controls at +0x4E4 (events9–13) rebuild via `0x448E60`: the active country's LeagueBase entries are inspected, DummyLeague is filtered using native RTTI, live non-DummyLeague league identity and caption retained; selecting a division stores chosen index at +0x68 and original competition identity at +0x8C, not always Premier League0.

The original **initial** division is source-sensitive: when current human club's country agrees with the currently selected country, the club's competition identity is matched into that country's division list, with source `0xFFFF` fallback to index0. Two **Sort By** controls are at +0x6A8, native events14/15: **League Position** mode0 (default) and **Current Form** mode1; source event `0x449090` updates table presentation, not the identity of the selected club. The original row owner is `CLeagueTableList` with `PLeagueTableRow` children, whose projections are investigated in the same Recovery162 report. This is a **distinct** source contract from PLeagueFixtures (eight countries and six League controls, native events1–14); do not copy its six-League selector count into PLeagueTables.

## Actual merged player-facing route

Normal PMenu child `0x25A` runs `reconstruction/original_management_presenter.py::build_management_panel_snapshot`, around lines227–240. It calls `bridge.league_table_rows()` with **no current-club, country, division or sort input** and passes the result to `build_league_tables_snapshot` without any source-choice action.

In `reconstruction/gate13_management_source_data.py::ManagementSourceDataBridge.league_table_rows` (lines2261–2286; blob `4181db2efc218f5bf5c026767b111b3394b7789f`), the entire table comes unconditionally from `state.premier_league_table()`. The returned rows have no source competition/selector owner; the method does not consult human club or active country. `reconstruction/original_league_tables_presenter.py::build_league_tables_snapshot` (blob `detailed current source on main`) defaults `sort_state=0` and **explicitly rejects source mode1 (Current Form)**. Its snapshot does not contain original country/division selection and cannot repair an upstream wrong competition. `reconstruction/original_league_tables_resources.py` already holds source-derived country order and events1–15; normal Tk pointer events currently do not bind those controls to the panel. This is not merely a missing sorting label or different artwork.

## Concrete falsifiable football impact

A qualified non-Premier-League human (the canonical source probe's Southport club349 in competition27 is a real example) selecting normal PMenu League Tables should receive the initial table belonging to that selected human club's original country/division, subject to the original source `0xFFFF` fallback. The integrated screen instead returns Premier League's 20 clubs and standings **unconditionally**. This is a **CONFIRMED WRONG player-facing competition context** for source-qualified non-PL clubs, as distinct from actual Windows screenshot observation. For PL humans, a correct initial table's rows may appear, but there is no working 8-country/5-DIVISION navigation or Current Form sort. The source sort default0 is correctly represented, so do not treat the entire table column presenter as wrong or replace with a modern generic select widget.

| Source-backed journey stage | Reconstructed owner | Classification |
|---|---|---|
| PMenu League Tables child0x25A opens original class | Integrated `PLeagueTables` snapshot | PARTIAL |
| Country from user/country selection; country events1–8 | Static original-derived helper constants but no live user/current-country binding | MISSING |
| Five eligible non-DummyLeague DIVISION entries, events9–13, source-selected club's own League | Fixed global `premier_league_table()` | **WRONG** for non-PL user; MISSING radio actions |
| Sort default League Position (event14) | Table presenter sort0 | SOURCE-COMPATIBLE within PL subset |
| Current Form mode1 (event15) | Presenter explicitly refuses | MISSING, fail-closed is safer than fabricated order |
| Real source input/navigation, save/return, 2–6 human manager rotation | No actual original runtime/Windows11 acceptance here | UNKNOWN / NOT VISIBLE-ACCEPTED |

## Codex-only next implementation acceptance

1. Reuse existing original selector/resource functions and native per-country/dynamic division identity from `GATE13_LEAGUE_TABLES_RESOURCES.md`; initialize from selected human's club and its live competition and country, with source class predicate; no PL0 fallback for a known non-PL club.
2. Render source-selected League's **actual** standings/results and row membership in source order. When a supported division's data is not source-qualified, **fail closed**, not silently show an unrelated league. Do not claim Cup ranking identical to a League table.
3. Wire actual eight country radios, **five** division radios and sort actions14/15 with their original enabled/hidden and table rebuild/return semantics. Keep sort mode1 explicitly incomplete until native `0x4F4A10` ranking inputs are proven.
4. Acceptance in normal Windows11 player input: (a) PL human→Tables belongs to PL; (b) Southport349→Tables belongs to its real non-PL division, not PL; (c) country26→33 and eligible divisions/disabled slots; (d) League Position vs Current Form with exact source order; (e) return/reopen/pointer coordinates, fixture/table consistency, save/reload, and later manager switch in a source-equivalent two-human session. Validate at both original 1x and compatible scaled display.
5. Preserve Recovery485's **separate** League Fixtures owner audit; no renaming/merging their UI classes. Complete core Inbox, PPreMatch/results/Save, squad formations and full original scope as earlier priorities.

**Evidence grade:** original source class/selector events and table rebuild **SOURCE-VERIFIED from prior independently hashed PE**; current unconditional PL table and missing selector actions **CODE-CONFIRMED**; running shipped original process today **NOT OBSERVED**; real Windows11 integrated click/visual **NOT VISIBLE-ACCEPTED**. No source/asset/game modifications by this audit worker; Gate13 OPEN, Gates14–17 and full original-scope Win11 release incomplete.
