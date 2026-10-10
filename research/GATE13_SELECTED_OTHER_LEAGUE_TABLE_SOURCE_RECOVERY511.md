# Recovery511: source-selected original League Tables data

11 October 2026 KST. Independent of Recovery510's PLeagueFixtures stateful presenter branch, based on post-#575 main `49841fb13889f7178b1550170e6cb3b506096807`. **Gate13 OPEN**.

## Verified owner separation

Original `PLeagueTables` at `0x448640 / 0x448C40` has eight country fmRadioTextSm controls (events1..8) country IDs `26,33,40,73,66,31,24,9`; **five** dynamically rebuilt DIVISION radios (events9..13), not the six used by `PLeagueFixtures`. Original panel `+0x64` contains active country index, `+0x68` a **single** division index, `+0x8C` selected competition identity, `+0x98` sort mode. Original event14/15 choose League Position mode0 / Current Form mode1, with default0. Source `0x448E60` rebuilds country roots filtered by DummyLeague RTTI; current-human country's own League is selected where present. Canonical source evidence: `research/GATE13_LEAGUE_TABLES_RESOURCES.md` Recoveries161–162 and `research/GATE13_LEAGUE_TABLES_MANAGER_DIVISION_AND_SORT_WRONG_PANEL_AUDIT_RECOVERY486.md`, but that old wrong-manager finding was fixed on main by PR569.

## Implemented independent data slice

`original_league_tables_selector_context.py` provides an immutable native event 1..15 candidate state with exact original country order, up-to-five country-specific root-League slots (excludes DummyLeague, cups, children), single selected division index, source human division default and explicit sort mode. Event handling is **non-pointer** and makes no native click acceptance claim.

`ManagementSourceDataBridge.original_league_tables_selection_context()` obtains original source identities from the true manager's DBRClub+0x10 and country. `source_selected_nonpl_league_table_rows(context)` reauthenticates the complete source candidates/manager, refuses tampering, unconstructed radios, sort state1 Current Form (original `0x4F4A10` unimplemented), and Premier League0's distinct fixed-source route; for a selected real nonPL root League, it reuses Recovery508's original `0x4F4940 / 0x4F45E0` comparator and source-live context0 data with no fake manager/membership. Projection is the already-established original League Position row dataclass. Default current-manager League Tables path is unchanged.

Five focused tests exercise Southport349 Conference7 original fifth selection, England Division1 League2 foreign selection (Alpha/Beta 3:1 and 3/0 points), five-option limit, switching countries, distinct sort14/15 states and strict Current Form/PL0/unauthenticated source rejection. CI checks at the exact PR head required before merge. No original proprietary bytes added.

## Still incomplete

The normal League Tables presenter is not yet wired to this selected-data owner; original fmRadioTextSm screen-pointer ownership, captions/art, selected other-League PMenu table screen GUI, `0x4F4A10` Current Form ranking and full normal Win11 player walk remain open. Do NOT treat this branch as Gate13 acceptance or authorize a fabricated Current Form or unrelated Premier League standings.
