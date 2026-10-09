# Original-File Fidelity Ledger

This ledger is the worker's primary queue while the original-file fidelity sweep is active.

## Urgent order — Daniel's core-functionality priority (9 Oct 2026)

Follow `research/GATE13_CORE_MENU_FUNCTIONALITY_AUDIT_PRIORITY_2026-10-09.md` **ahead of the general P0/P1/P2 ordering below**. The next audit is not another isolated row-bitmap/font trace; it is the original **menu-to-function graph** and end-to-end playability path. This changes **work ordering only**, not the evidence/status claims in historical research or the independent Codex implementation ownership.

| Order | Audit target | Minimum result before moving down | Current status |
| --- | --- | --- | --- |
| **P0-A** | PMenu roots/children, selection, visual state, dispatch and back/return | Complete source-addressed per-item action map; identify supported, accepted-but-not-integrated, and unresolved routes; audit actual selection/pathing | PARTIAL — three integrated presenter routes; other original action kinds must be classified |
| **P0-B** | EAMail / inbox | Trace native PEAMail/CMessageList list ownership, order, controls and callbacks through visible usable inbox; compare clean-room | PARTIAL — original constructor verified, clean-room inbox absent |
| **P0-C** | Main first-team / Squad controls including 1ST, RES, formations and interaction | Control-by-control original/port/working-Codex comparison across 2 clubs/states, functionality not just pixels | PARTIAL — rendering repairs exist; several tabs/selection semantics incomplete |
| **P0-D** | Core menu-to-gameplay loop including NEXT/MATCH, fixtures, table, calendar, Save/Load | Trace original route → actual state/destination → return, identify blockers and whether clean-room normal original-look path works | UNKNOWN/PARTIAL — standalone development playtest is not original navigation |
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
| P0 | EAMail PMenu child / native inbox panel | club with source messages; empty and populated mailbox | native 0x65 dispatch case, PEAMail/CMessageList owner, native message flow and input | PARTIAL | Original factory and class proven, but reconstruction has no functional EAMail presenter, message aggregation/geometry unverified | `research/ORIGINAL_FIDELITY_SWEEP_NATIVE_GATE13_RECHECK_2026-10-09.md` |
| P0 | Management header | multiple clubs and date/match states | club name/date/match lines, fonts, layout, conditional selector | PARTIAL | recent source-backed repairs require end-to-end audit | |
| P0 | Startup FMV | EA + Premier League intros | source decode, 320x480->640x480 transform, 640x480 field, (80,60), timing/input/audio | PARTIAL | external build content misframed; transport receipt still required | |
| P0 | Fullscreen/window/input | startup + menu + management | original-visible behavior vs compatibility-only mechanism | PARTIAL | Escape original semantics unresolved | |
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
| P2 | Competition/schedule mapping | league/cup/multi-country | owner fields, participant/order/progression rules | NOT AUDITED | | |
| P2 | RNG/startup mappings | startup through scheduling | original consumers/order/state | NOT AUDITED | previously strong evidence, but not yet sweep-reviewed | |

## Rules for using this ledger

1. Work highest-priority NOT AUDITED/PARTIAL/WRONG rows before expanding new functionality.
2. Update a row only after writing/referencing the underlying reproducible evidence.
3. If an audit finds a wrong mapping, treat correction as higher priority than continuing the sweep elsewhere unless blocked.
4. Cross-check shared UI paths on more than one club/state where applicable.
5. Add rows when an implemented surface is discovered that is not represented here.
6. Do not mark the sweep complete while any currently implemented player-visible Gate-13 surface remains NOT AUDITED, WRONG, or unexplained PARTIAL.
