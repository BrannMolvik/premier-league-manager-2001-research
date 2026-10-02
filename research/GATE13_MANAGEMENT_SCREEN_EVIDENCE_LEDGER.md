# Gate 13 Management-Screen Evidence Ledger

_Date: 1 October 2026 KST_

## Purpose

Gate 13 cannot close while normal-management surfaces are only generic
placeholders. This ledger enumerates the presentation evidence already persisted
in the repository, separates actual panel/screen identity from backend or event
identity, and records exact source-catalog queries for unresolved surfaces.

Recovery 143/144 corrected two earlier placeholders: TeamSelect club identity is
now source-bound, and the assumed standalone "Manager Home" fresh-game panel is
superseded by the executable-proven PMenu management shell routing a fresh user
directly to PSquadScreen.

This is an evidence inventory, not a claim that the listed screens have been
visually reconstructed.

## Evidence classes

- **Panel identity proven**: persisted RTTI/class or screen-factory evidence
  identifies an original presentation class.
- **Backend/event identity only**: source behavior is recovered, but no
  persisted evidence identifies the original presentation panel.
- **Feature-family lead only**: a source-path/string/model family exists, but it
  must not be promoted to a screen without further executable correlation.

## Roadmap screen ledger

| Roadmap surface | Persisted presentation identity | Strongest source-backed evidence | Original resource/layout/navigation status |
| --- | --- | --- | --- |
| Main menu / TeamSelect | **Proven.** PStartMenu screen ID `0x323`, vtable `0x7C64E0`; `PMain@TeamSelect` vtable `0x7C7650` | PStartMenu/TeamSelect constructors, event IDs, action rectangles, English country order, 16 hierarchy + 24 club control layouts, exact root-league/club filtering and stable ordering, native row-state transforms, original Zurich captions/fonts, source paths, clicked-club user binding, rollback-record semantics and six-user cap are recorded | **Integrated and Windows-verified for this bounded path.** The base first-screen resources plus four TeamSelect row/font resources are provenance-imported and live presentation is integrated. Recovery 164's corrected Windows 11 audit passed with Python 3.13.15 / Tk 8.6.15. |
| Management shell / former "Manager home" placeholder | **Proven shell: `PMenu`.** TypeDescriptor `0x81CE80`, vtable `0x7C3DE8`, constructor `0x482830`, route method `0x482960`; concrete `CMenuList`, `PTitleMenuRow` and `PChildMenuRow` families are source-bound | Fresh state `+0x10E8=0` routes to `PSquadScreen`; state 1 routes code `0x25A` to `PLeagueTables`. Recovery 145 proves the nine-root static tree, 29-pixel row geometry and four title/child menu-popup resources. Recovery 146 closes every modeled root/child caption through the complete 2,714-entry English loader, binds the already-imported Zurich 16px font, preserves exact black/white row component tuples, and source-locks `MenuBackgroundToggle::0x47AC00` neutral bit-to-row selection. | **Partial.** Shell/navigation, modeled captions, font identity, background-row selection and title/child arrow frame mapping are source-bound. All four exact `.444` menu-popup assets are provenance-imported. Remaining exact clipping/origin behavior, shell background and complete downstream visual composition/navigation remain open. |
| Squad | **Proven: `PSquadScreen`.** TypeDescriptor `0x819D48`, vtable `0x7C5CA4`, setup `0x4B5720`; embedded `CBasePlayerList` and `PSquadPitch` identities proven | Exact `squad_but_anim.444` controls 3/4/5 and captions; two roster rectangles and pitch rectangle; exact first+reserve / first+pitch / reserve+pitch transitions; concrete 20-row player-list hierarchy/columns/status filters; all 22 paired `FormationText` rectangles/IDs and exact group/state-to-source-row transform | **Partial.** Core panel/view geometry, roster bindings/status semantics and FormationText state selection are source-bound and guarded. Broader visual/icon semantics, unresolved selection/sort/navigation behavior and final integrated composition remain open |
| Tactics / team selection | **Partially proven.** `PFormation2k`; `PTeamOrders2K`; `PSquadPitch`; `FormationText` | `PFormation2k` vtable `0x7C1AB4`; exact `squad_bars.444` and `squad_form_anim.444` consumers; five native formation records; all 22 FormationText paired rectangles/control IDs and exact state-to-source-row transform; Team Orders source path `Applications\\FootballManager\\SquadPan.cpp` | **Partial.** The two formation resources, FormationText geometry and state selection are proven/imported. Surrounding controls, gestures, broader team-order presentation and navigation remain unresolved |
| Fixtures / results | **Proven League Fixtures panel: `PLeagueFixtures`.** Menu ID `0x25C`, direct factory case `0x47C724`, constructor `0x46D470`, TypeDescriptor `0x81C550`, vtable `0x7C24B8`; embedded `PLeagueGrid`, `ClubText` axes and `fmRadioTextSm` country/League selectors are RTTI-proven | Six exact original graphics, exact 12x24 grid placements, date/played/toggled cell states, DD.MM vs score A:B text, same-club red self-fixture diagonal, competition-member-order matrix population, 373-head fixture scan/filtering, first-free `N*N` repeat layers, 12-club paging, 29x14 pointer reduction, eight exact country selectors and six RTTI-cast League controls with source captions/events are source-bound. | **Partial.** Core grid and country/League selector presentation/navigation are proven. Status bit `0x20` remains neutral. Populated-cell action `0x488C80` is now source-bound to a conditional `PMatchInfo` dialog (constructor `0x487580`, vtable `0x7C41D4`, 760x500) that no-ops if its secondary linked context cannot be resolved. PMatchInfo now has 20 exact source Match_report graphics with firsthand hashes/dimensions/static handles, plus RTTI-proven subpanel classes and 13 directly mapped resource consumers. PMatchInfo now additionally has nine exact local resource rectangles, six Zurich-16 text rectangles, source clipping/negative-origin behavior, and an RTTI-proven eCDBitmap callback target distinct from typography. The shared PScriptRow1/PScriptRow2 14x14 incident control, its resource slot, all seven switched wrappers, all six bounded Zurich text producer chains, and the bounded incident-wrapper selection predicates are source-bound. The player-strip line is RTTI-bound to DBTPositions; popup lines are source-bound to Attendance, Ref. and Mom. The event-row decimal remains only event_record+0x00 formatted with %d. PMatchInfo now also has exact MATCH INFO / TEAM INFO / FINANCIAL tab controls, concrete embedded subpanel targets, source-default MATCH INFO selection, and a shared fmCrossButton/Escape PostMessageA(WM_USER,7,0) path. The four name-block and three possession resources have now been exhaustively audited and are loaded-but-unconsumed in the canonical executable, so no final widget binding is claimed. Remaining non-selector controls, intentional source-proven asset import/integration, and integrated Windows validation remain open. |
| League table | **Proven: `PLeagueTables` and `PCupTable2000`.** League menu ID `0x25A`, TypeDescriptor `0x81B458`, vtable `0x7C00C8`, constructor `0x448640`; Cup Tables ID `0x25B`, TypeDescriptor `0x81BA30`, vtable `0x7C0A78`, constructor `0x44EC80`; body is `CLeagueTableList` and entries are `PLeagueTableRow`. | Recovery 161 source-binds all 15 selector events and Country/DIVISION/Sort By plus exact `P / W / D / L / F / A / Pts` headers. Recovery 162 closes the 477x384 list body, 24-row/16px native layout, rank/name/seven-stat row rectangles, direct P/W/D/L/F/A source fields and `Pts = 3*W + D`; all 15 original `league_tables/*.444` row-grid/icon/bar assets are fresh raw-disc hash/geometry/handle proven. Recovery 164 resolves the seven `0x449090` targets as eCText stat headings and closes their exact active-state transform. | **Partial.** Core League Tables presentation contract, presenter integration and original artwork ownership are source-closed; all 15 exact binaries are provenance-imported and validated. Current Form row ordering and integrated Windows validation remain open. |
| Player profile | **No persisted original panel identity** | `DBTPlayers` / `DBRPlayer` runtime identity and current-skill vector boundary are recovered | **Open.** Original profile panel, visible field/column mapping, icons, resource/layout and visibility rules remain unknown |
| Transfers | **Panel-family name proven: `PTransfer2K`** | Original transfer event/action families, deal-state families and executable source-path family `TransPan.cpp` are persisted | **Open.** Original screen sort, unresolved caption bindings, controls, art, geometry and navigation remain unknown |
| Finances | **Panel-family names proven: `PFinanceOverview`, `PTickets`** | Finance Overview category-1000 aggregate path; `PTickets` update routine `0x45FF10`, ticket object and section-state semantics; `Balance.cpp` source-path metadata | **Open.** Exact visible account labels, resource paths, widget bindings, layout and navigation remain unknown |
| Messages / news | **No original inbox panel identity proven** | `MPMEAMail` is a recovered mail wrapper/queue family with several proven message/action subclasses | **Open.** `MPMEAMail` is not evidence of an inbox screen class. Cross-family interleave/order, resources, layout, controls and navigation remain unknown |
| Training | **No persisted original panel identity** | Executable source-path family `Training.cpp`; recovered training record/method/update contract | **Open.** Original training panel class, resources, visible bindings, geometry and navigation remain unknown |
| Scouting | **Proven: `PScouting2K`** | TypeDescriptor `0x81C9C0`, COL `0x7E3D20`, vtable `0x7C2E6C`, setup method `0x4AB150`, event handler `0x4ADB50`, search event 31 and six native result-sort modes | **Partial.** Two exact original graphics are provenance-imported and a deterministic fail-closed composition fragment now enforces their recovered dimensions/placements. Captions, the surrounding background, remaining controls and navigation still need recovery |

## Additional normal-play / feature-family leads

These persisted source facts prove feature families, not additional screen
classes:

- `CSupportStaff` model RTTI is adjacent to
  `Applications\\FootballManager\\Manager\\Support.cpp`.
  This establishes a support-staff subsystem, not a Support Staff screen.
- The executable retains source-path strings for `Youth.cpp`,
  `MatchFrontEnd.cpp`, `Scouting.cpp`, `Training.cpp`, `TransPan.cpp`
  and `Season.cpp`. A source-module name alone does not establish a panel,
  screen ID or navigation edge.
- Original `English.idx` / `English.str` prove front-end labels including
  `Save Game`, `Settings`, `Virtual Managers`, `Main Menu`,
  `Team Selection` and `Match View`. Those strings prove original feature
  vocabulary, not their final control binding or resource layout.

Accordingly, "remaining screens" is not allowed to collapse into an assumed
modern feature list. It closes only after executable navigation/panel evidence
and exact original resources are correlated.

## Reproducible source-catalog query plan

The existing source inventory/query tools already support a whole-disc path
catalog. Once the materialized private ZIP can be read by an execution tool,
generate or refresh a deep report and keep it outside Git unless intentionally
reduced to research metadata.

Example source inventory:

```text
python reconstruction/gate13_source_inventory.py <authorized-source.zip> --deep --hash-source --output gate13-source.json
```

Then query path families without importing anything:

```text
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(manager|home|overview|club|calendar)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(squad|roster|team|player|injur|suspend)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(formation|tactic|team.?order|set.?piece)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(fixture|result|season|calendar|match)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(league|table|stand)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(player|profile|history|stat)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(trans|transfer|contract|offer|bid|negotiat)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(finance|balance|ticket|stadium|ground|cash|budget)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(mail|message|news|inbox)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(train|scout)"
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(support|staff|youth)"
```

A broad cross-check can use:

```text
python reconstruction/gate13_catalog_query.py gate13-source.json --regex "(manager|home|squad|formation|tactic|fixture|result|league|table|player|profile|transfer|finance|balance|ticket|mail|message|news|training|scout|support|youth|stadium|ground|match)"
```

These are discovery queries only. A matching filename is not a binding.

## Correlation rule before import

For every candidate screen family:

1. establish the original panel/navigation identity from the canonical
   executable where possible;
2. establish the exact original source path from the source catalog;
3. stage only explicit paths with
   `--only-explicit --require-all-explicit`;
4. record size and SHA-256 and inspect the native format;
5. connect the resource to executable/control/layout evidence;
6. only then provenance-import the minimum required original bytes.

The existing `gate13_asset_import.py` and manifest policy remain the import
guard. Resource-name similarity alone is never sufficient.

## Recovery 120 catalog execution and first proven correlation

The canonical source inventory was audited against all management-screen query
families on 1 October 2026. Candidate counts were: main-menu reference 293,
manager home 80, squad 4, tactics 27, fixtures/results 39, league table 30,
player profile 8, transfers 5, finances 484, messages/news 28, training 11,
scouting 2, and support/youth 38. These counts remain discovery evidence only.

An independent exact-full-path scan of the canonical executable found no
`Manager_Home` path literal. Recovery 144 subsequently closed the missing
panel/factory boundary: the post-TeamSelect shell is `PMenu`, and a fresh
user routes directly to `PSquadScreen`. The old Manager Home filename query is
therefore retained only as historical discovery evidence, not as an outstanding
screen that must be fabricated.

Scouting now has the first complete catalog-to-panel resource correlation:

- `FM2001_Art/business/scouting/background_2.444` (4,452 bytes) is the exact
  literal at `0x838F7C`. Loader thunk `0x5FE824` passes it to resource handle
  `0x941E10` through `0x64D750`; wrapper construction at `0x5FE887` exposes it
  through `0x941DF0`.
- `FM2001_Art/business/scouting/background_alpha_1.444` (7,420 bytes) is the
  exact literal at `0x838FAC`. Loader thunk `0x5FE8C4` passes it to handle
  `0x941DD0`; wrapper construction at `0x5FE927` exposes it through
  `0x941DB0`.
- `PScouting2K` vtable `0x7C2E6C` contains setup method `0x4AB150`. That method
  composes `0x941DB0` at x=`207` for 20 rows, y=`192..515` in 17-pixel steps
  (`0x4AB6AA..0x4ABA20`), and composes `0x941DF0` at `(206, 543)`
  (`0x4ABA51`). This proves screen ownership and exact geometry rather than
  merely correlating similar filenames.

The private exhaustive reports and raw instruction windows remain outside Git.
Only the concise addresses and conclusions required for reproducibility are
preserved here.

## Recovery 123 presentation integration

PR #47 was squash-merged as
`757e8fec77f688bab893e155fee0bb82eaa97b6f`.

- PStartMenu Zurich captions are now part of the private live developer view at
  the recovered native line origins, with Button-group-dependent endpoint
  colors. The implementation refuses any non-endpoint 16-bit color rather than
  guessing a channel layout.
- `reconstruction/original_scouting_resources.py` binds the two already
  provenance-imported Scouting files to their executable-proven composition:
  20 copies of the 571x16 `background_alpha_1.444` at
  x=207/y=192..515 step 17, plus the 295x45 `background_2.444` at
  (206,543). It yields only a transparent composition fragment, not an invented
  full Scouting screen.
- Focused Gate-13 run `36814179046` passed **249 tests / 20 expected skips /
  0 failures**; asset-policy run `36814179303` passed.

## Automated catalog-audit implementation

PR #46 was squash-merged as
`ca7f6cfd9c5fae01ac9c454ad14603076979262b`.

`reconstruction/gate13_management_catalog_audit.py` implements the query
families above against a saved Gate-13 source report. Its output deliberately
marks every group `binding_proven = false`, preserves the source layer and
uses the nested-disc layer by default so the outer ZIP wrapper name
`F.A. Premier League Football Manager 2001` does not create false
manager-home matches.

Verification on PR head
`4cae5ca3821a9a536fab8176720fad2f11debc01`:

- focused Gate-13 run `36781127596`: **243 tests, 19 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36781127819`: passed;
- the full reconstruction workflow was intentionally **not triggered** because
  this isolated catalog/reporting tool is outside its narrow integration path
  filter. PR #45 remains the latest full-integration baseline at **1,074 tests,
  21 expected skips, zero failures**.

## Current blocker and exact next action

TeamSelect selection identity is closed in
`research/GATE13_TEAMSELECT_USER_SELECTION_TRACE.md`. The post-TeamSelect
management-shell/fresh landing route is closed in
`research/GATE13_MANAGEMENT_SHELL_ROUTE.md`.

Recovery 164 reran the required real-Windows first-screen audit against the
corrected TeamSelect semantics; it passed on Windows 11 with Python 3.13.15 and
Tk 8.6.15. The older Recovery-138 receipt remains historical evidence only.

For independent source work, continue from the now-proven PMenu shell and
PSquadScreen fresh landing rather than looking for a generic Manager Home panel.
The first PMenu row-resource binding, modeled caption/font/background-state
mapping, arrow animation mapping and four exact provenance imports are now
closed in `research/GATE13_PMENU_CHROME_TRACE.md`. Recovery 164 also closed the
`PLeagueTables::0x449090` seven-header eCText state trace. Run the fresh Gate-13
closure audit next. Keep Current Form ordering and every filename-only lead
fail-closed until executable ownership is established.
