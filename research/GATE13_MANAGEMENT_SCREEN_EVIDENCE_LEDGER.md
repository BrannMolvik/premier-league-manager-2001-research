# Gate 13 Management-Screen Evidence Ledger

_Date: 1 October 2026 KST_

## Purpose

Gate 13 cannot close while "manager home" and "remaining screens" are only
generic placeholders. This ledger enumerates the presentation evidence already
persisted in the repository, separates actual panel/screen identity from backend
or event identity, and records the exact source-catalog query to run when
private byte execution becomes usable again. Recovery 120 supplied that
execution path and completed the first catalog-to-executable correlation.

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
| Main menu / TeamSelect | **Proven.** PStartMenu screen ID `0x323`, vtable `0x7C64E0`; `PMain@TeamSelect` vtable `0x7C7650` | PStartMenu/TeamSelect constructors, event IDs, action rectangles, original English STR/IDX menu labels, native Button atlas-state mapping, Zurich caption placement/color and exact first-slice source paths are recorded | **Partial.** The strict ten-resource audit/import and PStartMenu native-caption live-view integration are complete. TeamSelect hierarchy content/interaction and the real Windows graphical validation remain open |
| Manager home | **No persisted original panel identity** | Read-only bridge can expose controlled-club original name/short name and current game date | **Open.** No original manager-home screen class, screen ID, exact resource path, layout, controls or navigation edge has been correlated |
| Squad | **Proven: `PSquadScreen`.** TypeDescriptor `0x819D48`, vtable `0x7C5CA4`, setup `0x4B5720` | Ordered live roster contract plus exact `squad_but_anim.444` binding; controls 3/4/5 at `(37,92)`, `(113,92)`, `(189,92)` bind English.idx 2490/2491/2492: `1ST & RES`, `1ST FORM`, `RES. FORM` | **Partial.** Distinct panel identity, atlas, control IDs and captions are proven/imported. Frame-state semantics, roster columns/icons/sort and navigation remain unknown |
| Tactics / team selection | **Partially proven.** `PFormation2k`; `PTeamOrders2K`; `PSquadPitch`; `FormationText` | `PFormation2k` vtable `0x7C1AB4`; exact `squad_bars.444` and `squad_form_anim.444` consumers in `FormationText`; five native formation records; Team Orders source path `Applications\\FootballManager\\SquadPan.cpp` | **Partial.** The two formation resources are proven/imported, but their caller-supplied geometry, remaining controls, gestures and navigation are unresolved |
| Fixtures / results | **No persisted original panel identity** | `DBTRealFixtures` / `DBRRealFixture` / `DBTRounds` construction and source insertion order are recovered; executable retains `Season.cpp` source-path metadata | **Open.** Original screen comparator/order, graphics, geometry, controls and navigation remain unknown |
| League table | **No persisted original panel identity** | Native League comparator `0x4F45E0` and its six-field ordering contract are recovered | **Open.** Original table panel class, header/row artwork, geometry, controls and navigation remain unknown |
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
`Manager_Home` path literal, while finding exact source paths in the other
families (including all four Squad candidates and both Scouting candidates).
That negative result does not prove that Manager Home lacks resources; it
prevents a filename-only import and makes panel/factory recovery the next
required step for that screen.

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

The four-candidate Squad correlation is complete. It proves the distinct
`PSquadScreen` owner for `squad_but_anim.444`, the `FormationText` ownership of
`squad_bars.444` and `squad_form_anim.444`, and the negative boundary that
shared `blue_toggle.444` has no `PSquadScreen` consumer. All four are imported
and fail-closed by deterministic hash/header/owner tests. Full evidence is in
`research/GATE13_SQUAD_RESOURCE_CORRELATION.md`.

Next, expand outward from `PSquadScreen::0x4B5720` to recover the three button
bindings/captions and surrounding roster presentation without splitting the
73x575 atlas by arithmetic guesswork. Trace the callers that provide
`FormationText` geometry separately. The real Windows PStartMenu/TeamSelect
graphical audit and remaining management-screen correlations are still
required before Gate 13 can close.
