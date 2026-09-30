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

The source paths and hashes are documented, and executable research already proves PStartMenu action rectangles, labels, IDs and core TeamSelect navigation anchors. However:

- the strict physical ten-resource audit has not been rerun in the current blocked execution environment;
- native Button state-to-atlas mapping remains unresolved;
- Zurich caption placement/color remains unresolved;
- TeamSelect hierarchy interaction/layout semantics remain incomplete;
- the ten pinned resources have not yet been intentionally provenance-imported as the finished first-screen set.

The existing `original_assets/MANIFEST.md` contains three imported original assets only: one reused menu Windows-buttons PNG plus two tiny EA444 scroll-end decoder fixtures. These are useful provenance examples/fixtures, but they are not equivalent to completed PStartMenu/TeamSelect resource import.

## Management-screen coverage matrix

| Roadmap screen | Source-faithful presentation data seam | Original resource/layout/navigation status |
| --- | --- | --- |
| Main menu / TeamSelect | Yes | **Partial.** Strongest source-backed screen family, but native atlas-state, text placement, hierarchy behavior, strict source audit and final import are still open. |
| Manager home | Controlled-club identity/date available | **Open.** No completed original screen resource/layout/navigation correlation. |
| Squad | Source-order roster and recovered player state available | **Open.** No completed original squad graphics, columns, icons, geometry, controls or sorting/navigation proof. |
| Tactics/team selection | Formation, XI/bench and tactical state available; PFormation2k five-record family and PTeamOrders2K captain/penalty/corner/free-kick order semantics now have a verified presentation contract | **Open.** Original control IDs/bindings, graphics, player-slot geometry, gestures and navigation remain unresolved. |
| Fixtures/results | Source fixture insertion order, dates and results available | **Open.** Original screen row ordering/comparator, resources, geometry and navigation are not yet recovered. |
| League table | Native League comparator-aware rows available | **Open.** Original table artwork/layout/navigation remains unrecovered. |
| Player profile | Source/runtime profile projection available | **Open.** Original field-to-column/icon mapping, resource/layout and visibility rules remain unresolved. |
| Transfers | Proposal/deal/contract runtime records available | **Open.** Original screen sort, captions for unresolved negotiation bytes, resource/layout and navigation remain unresolved. |
| Finances | Cash, ledger and objective runtime state available; PTickets exact ticket object / terrace-seating / section-state presentation contract now verified | **Open.** PFinanceOverview account/category labels plus Finance/PTickets screen resources, control bindings, layout and navigation remain unresolved. |
| Messages/news | Verified presentation contract now preserves MPMEAMail plus ordinary/Bosman renewal and player-transfer-request identities/actions | **Open.** Complete inbox family coverage, cross-family interleave/order and original screen resources/layout/navigation remain incomplete. |
| Training/scouting | Training arrays and mapped scouting results available; PScouting2K event 31 and six native result-sort modes now have a verified presentation contract | **Open.** Proprietary graphics, layout, visible captions, control geometry and navigation remain unresolved. |
| Remaining screens | Not a single complete inventory | **Open.** Must be enumerated and correlated before Gate 13 can close. |

The read-only bridge is important architecture and data work, but it must not be counted as original visual/presentation completion.

## Current infrastructure result

Recovery generation 101 re-resolved the canonical private Library ZIP at the durable ID/path and the file service materialized the expected 511,121,336-byte archive into the execution workspace. Immediately afterward:

- trivial `container.exec` failed with `ClientError`;
- trivial Python execution failed with `ClientError`.

Therefore the source is present, but byte execution remains blocked. No new executable disassembly, ten-resource physical audit, source import or original-pixel claim is made by this audit.

## Exact closure work for this criterion

When byte execution returns:

1. re-hash the materialized canonical ZIP and extract the exact canonical executable;
2. complete the TeamSelect RTTI canary, Button draw/update state mapping and Zurich render trace;
3. run the strict ten-resource source audit and provenance-import the verified first-screen assets;
4. regenerate/save the full disc catalog if needed;
5. for each remaining Gate 13 screen family, correlate executable/layout/navigation evidence to exact original source paths before importing anything;
6. preserve original strings/fonts/art where usable, documenting only genuinely incompatible/inaccessible replacements;
7. maintain an explicit per-screen resource/layout/navigation evidence table until every normal-play presentation area is covered;
8. run native Windows graphical/integration smoke tests before marking the resource criterion satisfied.

Until those steps are complete, this criterion must remain unchecked in `ROADMAP.md`.
