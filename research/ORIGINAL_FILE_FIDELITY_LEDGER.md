# Original-File Fidelity Ledger

This ledger is the worker's primary queue while the original-file fidelity sweep is active.

## Urgent order — Daniel's core-functionality priority (9 Oct 2026)

Follow `research/GATE13_CORE_MENU_FUNCTIONALITY_AUDIT_PRIORITY_2026-10-09.md` **ahead of the general P0/P1/P2 ordering below**. The next audit is not another isolated row-bitmap/font trace; it is the original **menu-to-function graph** and end-to-end playability path. This changes **work ordering only**, not the evidence/status claims in historical research or the independent Codex implementation ownership.

| Order | Audit target | Minimum result before moving down | Current status |
| --- | --- | --- | --- |
| **P0-A** | PMenu roots/children, selection, visual state, dispatch and back/return | Complete source-addressed per-item action map; identify supported, accepted-but-not-integrated, and unresolved routes; audit actual selection/pathing | PARTIAL — all 28 native factory cases and 9 roots independently mapped in `research/GATE13_PMENU_ALL_28_NATIVE_DISPATCH_AUDIT_2026-10-09.md`; only 3 integrated; action kind / exact return and live timing still incomplete |
| **P0-B** | EAMail / inbox | Native PEAMail/CMessageList rows, original input/result routing and view closure | PARTIAL — original Escape→PostMessageA(WM_USER,16)→MyWindow vft7CB294+0→532B80 returns wParam16→471270 result16→5EB920 detail remove verified in canonical executable; original list scroll restoration verified; complete original inbox data/assets, row physical input/actions and Windows GUI receipts still missing; original PBg control1 provides a second direct inbox entry (`research/GATE13_MANAGEMENT_PBG_MAIL_MENU_NEXT_DISPATCH_AUDIT_RECOVERY441.md`). `research/GATE13_EAMAIL_ESCAPE_MODAL_RESULT_CHAIN_RECOVERY441.md` |
| **P0-C** | Main first-team / Squad controls including 1ST, RES, formations and interaction | Original interactive tab owner/hit-test plus 2 clubs and accurate view state | PARTIAL — native actual control input now traced: 73×25 `0x7BE814 +0x6C→0x652CF0→0x64F7A0` with flag gates, parent `PSquadScreen +0x0C` true and `+0x10→0x4B8E70` reads child IDs 3/4/5; main and Codex still lack normal Tk press routing and 4/5 source view rendering. Cross-club/physical Win11 acceptance missing. `research/GATE13_SQUAD_TAB_NATIVE_POINTER_OWNER_AUDIT_RECOVERY441.md` |
| **P0-D** | Original NEXT/MATCH → all-user event scheduling, PResults, manager return and Save/Load | Reconstruct genuine native input and polymorphic match selection | PARTIAL — actual original `PBg` NEXT control/action, manager rotation, two calendar families, Event/Match/PostponedEvent object construction, conditional PResults and return previously traced. Recovery447 newly verifies **ordinary `0x615D10→0x615C50` NEXT event eligibility**: payload `+0x44 & 0x61==0` for that caller, Event `+0x08==0`, manager reference selector via Match virtual `+0x04=0x510A40` testing both participant reference objects `+0x14/+0x28` with structured comparator `0x4F2830`, wrapper PostponedEvent `0x5140D0` delegates matching and source `0x514520` updates/rechecks prior to return. original `PBg::0x432760` header initialization from PMenu ctor `0x4C3046` and PResults follow-on `0x4A80D4` calls *mutable* `0x615DA0`, which can invoke native `0x510BA0` to create PostponedEvent at relative slot+7 when `LeagueMatch/CupMatch` virtual+0x64 predicate `0x510B20` accepts. Do not confuse source lifecycle refresh with every repaint. Codex's fixed-league shadow is intentionally bounded but not this complete dynamic filter; neither main nor Codex wires normal native-look NEXT→gameplay. No multi-club Win11 receipt, original results-input producer still UNKNOWN. See `research/GATE13_NEXT_ORIGINAL_EVENT_QUERY_FILTER_AUDIT_RECOVERY447.md` and Recoveries442–446 source reports. |
| **P0-E** | Menu/input responsiveness | Map swallowed clicks and repeated redraw/snapshot work to original input contract; measure on Windows when available | PARTIAL — code-level repeated-work defects known; complete latency unverified |

Only after those is it appropriate to resume isolated bitmap-color, other UI styling, and Gate-14 audits except when directly necessary to prove these paths.


Status values:
- **EXACT**
- **COMPATIBILITY-EQUIVALENT**
- **PARTIAL**
- **WRONG**
- **UNKNOWN**
- **NOT AUDITED**

A row cannot be promoted to EXACT from reconstruction tests alone. Record reproducible original evidence.

| Priority | Surface / subsystem | Representative scope | Evidence to verify | Status | Discrepancy / blocker | Corrective reference |
| --- | --- | --- | --- | --- | --- | --- |
| P0 | Main menu / PStartMenu | original/default path | controls, resources, positions, order, input/navigation, timing | NOT AUDITED | full post-policy re-audit required | |
| P0 | TeamSelect / New Game | multiple leagues/clubs | screen/control mapping, club/country data mapping, transition lifecycle/timing | NOT AUDITED | full post-policy re-audit required | |
| P0 | Shared management shell / PMenu | Southport + at least one additional club | shared background/header/sidebar/menu ownership and geometry | PARTIAL | external build showed missing content; native EAMail route now traced but screen and popup behavior incomplete | `research/ORIGINAL_FIDELITY_SWEEP_NATIVE_GATE13_RECHECK_2026-10-09.md` |
| P0 | Squad screen | Southport + at least one additional club | row ownership/order, names, role/status/value fields, fonts/colors/icons/state | PARTIAL | external build materially incomplete; static disabled grid repeated; original normal and highlight assets now independently verified | `research/ORIGINAL_FIDELITY_SWEEP_NATIVE_GATE13_RECHECK_2026-10-09.md` |
| P0 | Squad selected-row bitmap/state | first + reserve, multiple clubs and hover/selection states | canonical row RTTI/vtable, three shipped grid resources, exact selected-frame producer | UNKNOWN | Native final row and `highlight_grid.444` identity verified, but actual selection/background draw-state mapping unproven; reconstruction paints static disabled strips | `research/ORIGINAL_FIDELITY_SWEEP_NATIVE_GATE13_RECHECK_2026-10-09.md` |
| P0 | EAMail PMenu child / native inbox panel | club with source messages; empty and populated mailbox | native 0x65 dispatch case, PEAMail/CMessageList owner, native message flow and input | PARTIAL | Original factory and class proven, native filtering/sorting/row selection/scrolling/second-press path now independently verified; reconstruction has no functional EAMail presenter, precise gesture/geometry/persistence unverified | `research/GATE13_EAMAIL_NATIVE_ROW_DETAIL_AUDIT_RECOVERY439.md` |
| P0 | Management header | multiple clubs and date/match states | club name/date/match lines, fonts, layout, conditional selector | PARTIAL | recent source-backed repairs require end-to-end audit | |
| P0 | Startup FMV | EA + Premier League intros | source decode, 320x480->640x480 transform, 640x480 field, (80,60), timing/input/audio | PARTIAL | external build content misframed; transport receipt still required | |
| P0 | Fullscreen/window/input | startup + menu + management | original-visible behavior vs compatibility-only mechanism | PARTIAL | PEAMMessage's context-specific Escape→MyWindow modal result16 and detail stack removal now source-proven; main/Codex have no inbox and globally bind Escape to fullscreen exit. Other screen Escape semantics and actual Windows timing unknown. | `research/GATE13_EAMAIL_ESCAPE_MODAL_RESULT_CHAIN_RECOVERY441.md` |
| P0 | Menu/management transition timing | main->TeamSelect->management | original lifecycle/order vs reconstruction-only synchronous work | UNKNOWN | external build extremely slow | |
| P1 | Tactics/team selection | representative club/state | all controls/assets/text/data/navigation | NOT AUDITED | | |
| P1 | Fixtures/results | league/cup representative states | all controls/assets/text/data/navigation | NOT AUDITED | | |
| P1 | League table | representative league/state | rows/headings/fonts/text/data ordering | NOT AUDITED | | |
| P1 | Player profile | representative player/statuses | controls/assets/text/data/navigation | NOT AUDITED | | |
| P1 | Transfers | bids/negotiation/completion states | UI + data mapping + lifecycle | NOT AUDITED | | |
| P1 | Finances/board | representative club states | UI + data mapping + rules | NOT AUDITED | | |
| P1 | Messages/news | representative messages | UI + source strings + triggers | NOT AUDITED | | |
| P1 | Training/scouting | representative states | UI + data/rules | NOT AUDITED | | |
| P1 | PPreMatch / Match Detail | representative mode/state | child mapping/order/resources/text/state/input | PARTIAL | extensive source work exists; requires systematic re-audit | |
| P1 | FastView | representative match events | controls/fonts/text/resources/event mapping/timing | PARTIAL | source tracing incomplete | |
| P1 | Match audio | music/SFX/chants | resource identity + trigger/timing/channel semantics | PARTIAL | incomplete | |
| P2 | Cup-Tied status | positive/negative cases | exact original producer/field semantics/lifecycle | PARTIAL | prior wrong date interpretation removed; negative rule unresolved | |
| P2 | Save/load mappings | representative multi-week state | original vs internal format semantics where claimed | NOT AUDITED | | |
| P2 | Transfers/contracts backend | representative paths | field ownership, predicates, ordering, lifecycle | NOT AUDITED | | |
| P2 | Finances/board backend | representative paths | field ownership, producers, ordering | NOT AUDITED | | |
| P2 | Competition/schedule mapping | league/cup/multi-country | native eligibility, reference-owner identities and dynamic PostponedEvent scheduling | PARTIAL — original Event/Match/LeagueMatch/CupMatch/PostponedEvent RTTI/constructors, relative-slot insertion, wrapper source delegation, native `0x615C50` payload flag bits0/5/6 and deferred update, `0x510A40` two-ClubRef-like participant comparison independently source-verified. Existing clean-room bounded source schedule/shadow tests preserve startup ordering, but dynamic full manager-qualified lookup/NEXT and multi-club original acceptance remain unresolved. | `research/GATE13_NEXT_ORIGINAL_EVENT_QUERY_FILTER_AUDIT_RECOVERY447.md` |
| P2 | RNG/startup mappings | startup through scheduling | original consumers/order/state | NOT AUDITED | previously strong evidence, but not yet sweep-reviewed | |

## Rules for using this ledger

1. Work highest-priority NOT AUDITED/PARTIAL/WRONG rows before expanding new functionality.
2. Update a row only after writing/referencing the underlying reproducible evidence.
3. If an audit finds a wrong mapping, treat correction as higher priority than continuing the sweep elsewhere unless blocked.
4. Cross-check shared UI paths on more than one club/state where applicable.
5. Add rows when an implemented surface is discovered that is not represented here.
6. Do not mark the sweep complete while any currently implemented player-visible Gate-13 surface remains NOT AUDITED, WRONG, or unexplained PARTIAL.
