# Gate 13 Original Management Resource Coverage Audit

_Date: 1 October 2026 KST_

## Criterion under review

Gate 13 completion criterion:

> Accessible original UI graphics/resources and recoverable screen/layout/navigation data are inventoried and reused or converted; replacements exist only for documented incompatible or inaccessible source material.

**Status: OPEN.** The repository has enough first-hand evidence to prove that a large original presentation corpus exists, but it does not yet have complete screen-by-screen correlation, import, layout/navigation recovery, or Windows presentation validation for normal management play.

This audit exists to keep three different kinds of progress separate:

1. source-disc availability and format recovery;
2. source-faithful management data exposed to presentation;
3. actual original management presentation resources/layout/navigation.

Only the third category can close this criterion.

## Confirmed source availability

First-hand authorized-disc inventory established:

- 2,456 Joliet files and 211 folders;
- 1,403 files under `FM2001_Art`;
- 1,354 original `.444` graphics;
- 18 files under `Fonts`;
- original English STR/IDX resources;
- canonical original executable SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This proves that original presentation material is broadly available. It does **not** by itself establish which resource, layout, control, timing rule or navigation edge belongs to each management screen.

## First-screen evidence

PStartMenu and TeamSelect are the only screen family with a deliberately pinned exact extraction set today:

- `FM2001_Art/Generic/bground.444`
- `FM2001_Art/Generic/main_menu/main_menu_bground.444`
- `FM2001_Art/Generic/team_choice/background.444`
- `FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444`
- `FM2001_Art/Generic/GenericButtonsAndBars/choice_start_anim.444`
- `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_anim.444`
- `FM2001_Art/Generic/GenericButtonsAndBars/choice_league_but_bars.444`
- `Fonts/Zurich_BdXCn_BT_20pixel.fnt`
- `English.str`
- `English.idx`

The strict physical ten-resource audit has now passed. Native Button group and
23-frame selection, pointer-inside animation direction, PStartMenu Zurich line
origins and original 16-bit color values are recovered in
`research/GATE13_BUTTON_NATIVE_TRACE.md`. All ten files are intentionally
provenance-imported and the post-import readiness guard passes. TeamSelect
hierarchy item identity/interaction and broader management-screen presentation
remain incomplete.

## Management-screen coverage matrix

| Roadmap screen | Source-faithful presentation data seam | Original resource/layout/navigation status |
| --- | --- | --- |
| Main menu / TeamSelect | Yes | **Partial.** Button atlas-state, PStartMenu text placement/color endpoints, strict source audit, ten-resource import and live developer-caption integration are complete; TeamSelect hierarchy content/interaction and Windows graphical validation remain open. |
| Manager home | Controlled-club identity/date available | **Open.** No completed original screen resource/layout/navigation correlation. |
| Squad | Source-order roster/player state plus verified ordered-roster contract; distinct `PSquadScreen` RTTI identity, exact `squad_but_anim.444` binding and three setup origins are proven | **Partial.** The atlas is provenance-imported and guarded, but its button meanings/frame partition plus roster columns/icons/sort/navigation remain unresolved. |
| Tactics/team selection | Formation, XI/bench and tactical state; `PFormation2k`, `PTeamOrders2K`, `PSquadPitch` and `FormationText` identities; exact `squad_bars.444` / `squad_form_anim.444` bindings | **Partial.** Both resources are provenance-imported, but caller-supplied geometry, remaining controls, gestures and navigation remain unresolved. |
| Fixtures/results | Verified DBTRealFixtures/DBRRealFixture construction contract plus source fixture dates/results are available | **Open.** Original screen row ordering/comparator, resources, geometry and navigation are not yet recovered. |
| League table | Native League comparator-aware rows plus a verified six-field presentation ordering contract are available | **Open.** Original table artwork/header geometry/controls/navigation remain unrecovered. |
| Player profile | Source/runtime profile projection plus verified DBTPlayers/DBRPlayer identity/vector-boundary contract available | **Open.** Original field-to-column/icon mapping, resource/layout and visibility rules remain unresolved. |
| Transfers | Proposal/deal/contract runtime records available | **Open.** Original screen sort, captions for unresolved negotiation bytes, resource/layout and navigation remain unresolved. |
| Finances | Cash, ledger and objective runtime state available; PTickets exact ticket object / terrace-seating / section-state presentation contract now verified | **Open.** PFinanceOverview account/category labels plus Finance/PTickets screen resources, control bindings, layout and navigation remain unresolved. |
| Messages/news | Verified presentation contract now preserves MPMEAMail plus ordinary/Bosman renewal and player-transfer-request identities/actions | **Open.** Complete inbox family coverage, cross-family interleave/order and original screen resources/layout/navigation remain incomplete. |
| Training/scouting | Training now has a verified Training.cpp method/record contract; PScouting2K event 31 and six native result-sort modes also have a verified presentation contract | **Partial.** Scouting now has two exact provenance-imported graphics and an executable-proven 20-row/footer composition fragment with deterministic tests. Training presentation, Scouting surrounding background/captions/remaining controls, and navigation remain unresolved. |
| Remaining screens | Not a single complete inventory | **Open.** Must be enumerated and correlated before Gate 13 can close. |

The read-only bridge is important architecture and data work, but it must not be counted as original visual/presentation completion.

The more explicit screen-by-screen evidence boundary, including panel identity
versus backend/event-only identity and exact whole-disc query patterns, is now
maintained in `research/GATE13_MANAGEMENT_SCREEN_EVIDENCE_LEDGER.md`. That
ledger confirms in particular that Manager Home currently has **no persisted
original panel identity**, and that feature/source-module names such as
`Support.cpp`, `Youth.cpp` or `MatchFrontEnd.cpp` must not be promoted to
screens without executable/navigation correlation.

## Superseded infrastructure result

Recovery generation 101 re-resolved the canonical private Library ZIP at the durable ID/path and the file service materialized the expected 511,121,336-byte archive into the execution workspace. Immediately afterward:

- trivial `container.exec` failed with `ClientError`;
- trivial Python execution failed with `ClientError`.

That blocker was cleared by the Windows-local recovery documented in
`GATE13_BUTTON_NATIVE_TRACE.md`. This section remains historical context.

## Exact closure work for this criterion

Current remaining work:

1. expand the proven `PSquadScreen::0x4B5720` anchor into source-backed button meanings/captions and roster layout, then continue the same correlation discipline across the other incomplete management screen families;
2. preserve original strings/fonts/art where usable, documenting only genuinely incompatible/inaccessible replacements;
3. recover TeamSelect hierarchy item/interaction semantics rather than inferring them from source art or the secondary screenshot;
4. maintain the explicit per-screen resource/layout/navigation evidence table until every normal-play presentation area is covered;
5. run the native Windows PStartMenu/TeamSelect graphical audit and broader normal-play integration smoke tests before marking the resource criterion satisfied.

Until those steps are complete, this criterion must remain unchecked in `ROADMAP.md`.
