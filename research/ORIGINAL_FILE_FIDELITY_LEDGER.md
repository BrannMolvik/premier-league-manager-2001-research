# Original-File Fidelity Ledger

This ledger is the worker's primary queue while the original-file fidelity sweep is active.

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
| P0 | Shared management shell / PMenu | Southport + at least one additional club | shared background/header/sidebar/menu ownership and geometry | PARTIAL | external build showed missing content; likely shared-path defect | |
| P0 | Squad screen | Southport + at least one additional club | row ownership/order, names, role/status/value fields, fonts/colors/icons/state | PARTIAL | external build materially incomplete | |
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
