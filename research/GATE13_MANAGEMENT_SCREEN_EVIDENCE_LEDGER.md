# Gate 13 Management-Screen Evidence Ledger

_Date: 1 October 2026 KST_

## Purpose

Gate 13 cannot close while "manager home" and "remaining screens" are only
generic placeholders. This ledger enumerates the presentation evidence already
persisted in the repository, separates actual panel/screen identity from backend
or event identity, and records the exact source-catalog query to run when
private byte execution becomes usable again.

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
| Main menu / TeamSelect | **Proven.** PStartMenu screen ID `0x323`, vtable `0x7C64E0`; `PMain@TeamSelect` vtable `0x7C7650` | PStartMenu/TeamSelect constructors, event IDs, action rectangles, original English STR/IDX menu labels and exact first-slice source paths are already recorded | **Partial.** Native Button atlas-state mapping, Zurich caption placement/color, hierarchy behavior, strict ten-resource audit/import and Windows graphical validation remain open |
| Manager home | **No persisted original panel identity** | Read-only bridge can expose controlled-club original name/short name and current game date | **Open.** No original manager-home screen class, screen ID, exact resource path, layout, controls or navigation edge has been correlated |
| Squad | **No distinct original Squad panel identity proven** | Ordered live team roster at `+0x244` / count `+0x294`; participant collector `0x510CD0`; DBRPlayer active/substitute flags and setters are now contract-locked | **Open.** Do not treat `PTeamOrders2K` as proof of the general Squad screen. Original squad graphics, columns, status icons, sort, geometry and navigation remain unknown |
| Tactics / team selection | **Partially proven.** `PFormation2k`; `PTeamOrders2K` | `PFormation2k` vtable `0x7C1AB4`; five native formation records; Team Orders RTTI neighborhood and source path `Applications\\FootballManager\\SquadPan.cpp`; four ordered set-piece/captain categories | **Open.** Original resource bindings, slot geometry, widget IDs, gestures and navigation remain uncorrelated |
| Fixtures / results | **No persisted original panel identity** | `DBTRealFixtures` / `DBRRealFixture` / `DBTRounds` construction and source insertion order are recovered; executable retains `Season.cpp` source-path metadata | **Open.** Original screen comparator/order, graphics, geometry, controls and navigation remain unknown |
| League table | **No persisted original panel identity** | Native League comparator `0x4F45E0` and its six-field ordering contract are recovered | **Open.** Original table panel class, header/row artwork, geometry, controls and navigation remain unknown |
| Player profile | **No persisted original panel identity** | `DBTPlayers` / `DBRPlayer` runtime identity and current-skill vector boundary are recovered | **Open.** Original profile panel, visible field/column mapping, icons, resource/layout and visibility rules remain unknown |
| Transfers | **Panel-family name proven: `PTransfer2K`** | Original transfer event/action families, deal-state families and executable source-path family `TransPan.cpp` are persisted | **Open.** Original screen sort, unresolved caption bindings, controls, art, geometry and navigation remain unknown |
| Finances | **Panel-family names proven: `PFinanceOverview`, `PTickets`** | Finance Overview category-1000 aggregate path; `PTickets` update routine `0x45FF10`, ticket object and section-state semantics; `Balance.cpp` source-path metadata | **Open.** Exact visible account labels, resource paths, widget bindings, layout and navigation remain unknown |
| Messages / news | **No original inbox panel identity proven** | `MPMEAMail` is a recovered mail wrapper/queue family with several proven message/action subclasses | **Open.** `MPMEAMail` is not evidence of an inbox screen class. Cross-family interleave/order, resources, layout, controls and navigation remain unknown |
| Training | **No persisted original panel identity** | Executable source-path family `Training.cpp`; recovered training record/method/update contract | **Open.** Original training panel class, resources, visible bindings, geometry and navigation remain unknown |
| Scouting | **Proven: `PScouting2K`** | TypeDescriptor `0x81C9C0`, COL `0x7E3D20`, vtable `0x7C2E6C`, event handler `0x4ADB50`, search event 31, six native result-sort modes; adjacent `MenuPan.cpp` source path | **Open.** Original captions for neutral controls, graphics, layout, control geometry and navigation remain unknown |

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

## Current blocker and exact next action

Recovery 104 successfully re-listed and materialized the canonical
511,121,336-byte authorized source ZIP, proving that the source exists.
Subsequent shell and private-Python access returned `ClientError`.

Therefore the immediate missing evidence is execution access, not another
source upload. When execution recovers, the first action remains the higher
priority first-screen canary and Button/Zurich/ten-resource path. The catalog
queries above then provide the screen-by-screen expansion path from first-screen
fidelity into manager home and normal management play.

Until those correlations are performed, this ledger must remain an inventory of
known evidence and explicit unknowns, not a Gate-13 completion claim.
