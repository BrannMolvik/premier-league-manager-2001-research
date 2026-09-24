# Project Audit — 24 September 2026

## Scope

This audit reviews the current state of the clean-room reverse engineering and reconstruction effort for **The F.A. Premier League Football Manager 2001**.

Canonical analyzed executable:

- `footballmanager.exe` SHA-256: `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The repository documents offsets and behavior for this exact release unless otherwise stated.

## Headline status

Estimated current state:

| Area | Estimate | Meaning |
| --- | ---: | --- |
| Full reverse-engineering knowledge | 59–63% | How much of the original game's important data/mechanics/architecture is understood well enough to document |
| Management-side reverse engineering excluding match/FastView | 75–80% | Data, development, training, contracts, transfers, finance, business, season-facing systems |
| Reconstruction readiness | 35–45% | Portion of the game for which enough behavior is known to begin a faithful clean-room implementation without heavy guessing |
| Actual clean-room implementation | 5–10% | Code already implemented in `reconstruction/`; currently primarily a verified data parser/browser, not gameplay |

The earlier conversational “playable reconstruction” percentage was too ambiguous because it mixed **knowledge recovered** with **code actually implemented**. The repository audit shows the implementation is much less advanced than the research.

## Persistence audit

From continuation checkpoint `a236506b47eb4340df53346a824bc6fd6050bc92` to audit head `2690eddd196c76e65914310a8b0a6ab9063b1682`:

- 108 commits ahead;
- `research/EXECUTABLE_ANALYSIS.md`: +1,690 lines;
- `research/PROGRESS.md`: +471 lines / -7;
- `research/FAILED_APPROACHES.md`: +318 lines;
- `research/FINDINGS.md`: +38 lines.

This is strong persistence discipline. Recent timeout/connection issues have generally cost at most one small live analysis block.

## Reverse-engineering progress by subsystem

| Subsystem | Approx. status | Audit assessment |
| --- | ---: | --- |
| String tables / Master.dat | 90%+ | Core layout, clubs, players, managers, names, dates, skills and links are strongly verified |
| Static.dat | 80–85% | Many typed tables, competitions, positions, fixtures, allocation and manager tables identified; some field semantics remain |
| Player runtime model | 90–95% | Runtime size, current/target skills and important development fields mapped |
| Aging / development | 92–96% | Main monthly formula, peak groups, decline, conversion behavior and baseline fields recovered |
| Training | 88–92% | Per-player records, seven methods, profile vectors, success probability, staff/facility multipliers recovered |
| Contracts | 78–83% | Wage/expiry and most negotiated terms/clauses mapped |
| Transfers | 80–85% | Proposal/deal/movement objects, swaps, free/Bosman cases, execution and cash posting largely mapped |
| Finance / chairman budgets | 85–88% | Cash, ledger, loans, funding requests, objective state, multiple business subsystems and budget events mapped; authoritative transfer-budget source remains unresolved |
| Clubs / managers / DBRUser | 75–80% | Major runtime ownership corrected; many per-user subsystems identified, but substantial fields remain unnamed |
| Competitions / fixtures | 68–75% | Real fixture schedule and many competition/allocation structures known; full season progression not reconstructed |
| Manager objectives / sacking | 60–70% | Financial objective block, tolerance, several outcome events and some manager tables mapped |
| Stadium / commercial systems | 60–70% | Stadium state, concession/sponsor systems, facility cash paths and monthly-history inputs identified |
| Season simulation / AI | 30–40% | Calendar architecture and periodic systems visible; manager/club AI remains shallow |
| Scouting | 25–35% | Architecture/tuning known, detailed mechanics largely pending |
| Youth | 25–35% | Architecture/tuning known, generation and decision logic largely pending |
| Save format | 15–20% | Many individual serializers recognized, but complete .sav format not decoded |
| Match calculation | 15–25% | Major class/event architecture visible; actual match mathematics and decision logic mostly unrecovered |
| FastView / .SCI | 10–20% | Separation from backend confirmed; approximately 252 .SCI files remain essentially undecoded |
| Cheat/debug command system | 45–55% | Literal command table and several runtime effects recovered; complete decoder/mapping remains incomplete |

## Highest-confidence recovered mechanics

The strongest parts of the project are currently player data, development and training.

Player data is grounded in the original loader rather than pattern guesses: 1,246 clubs, 30,064 packed 103-byte player records, 1,612 packed 43-byte manager records, exact string-table handling, player skill ordering and the exact 0–30 display conversion.

Development is recovered at executable level, including baseline/target fields, individualized peak ages, monthly cadence, pre-peak interpolation, peak-period behavior, post-peak decline and integer conversion.

Training is similarly strong: 40 × 200-byte per-club player training records, seven training methods, 17-skill profiles, active-training success probability, support-staff quality modifiers and Training Centre bonus are all documented.

Transfers are also well advanced: proposal, deal and movement structures; up to three exchange players; contract terms; free/Bosman sentinels; player rejection states; execution, club switching, join-date stamping, transfer history and buyer/seller cash movement.

## Finance / DBRUser audit

The largest recent advance is the correction of runtime ownership.

The large object previously described in older notes as “game/session” state is RTTI-confirmed as **DBRUser**. It owns the active manager/user's Balance objects and much of the persistent club-management state.

Confirmed DBRUser-owned or DBRUser-linked systems now include:

- six Balance pointers at +0x670..+0x684;
- manager funding-request state;
- commercial/attendance state;
- concessions;
- season-ticket/business state;
- bank loans;
- sponsors;
- support-staff lists;
- stadium/building/ticketing state;
- training records;
- movement-history state;
- monthly financial history.

Current cash is definitively active Balance +0x10.

The Balance +0x30..+0x80 records are financial-objective/forecast state rather than chairman budgets.

Manager FundRequest acceptance is a repayable cash-funding system and credits current cash.

Transfer-budget success notifications are presentation-only; their underlying transfer-budget mutation occurs earlier in board/finance logic.

EAMchairbudgetsettings +0x58 is the displayed transfer-budget value.

The current unresolved finance question is therefore narrow but important: whether that value is stored directly in another DBRUser field or reconstructed from board rules, financial history and transfer ledger flow.

## Important eliminated false leads

The repository now explicitly records and rejects many tempting but incorrect interpretations, including:

- runtime club +0x3C..+0x54 as a budget array;
- global TransferBudget / TransferBudget2K values as live storage;
- game/DBRUser +0x694 season-ticket state as budget storage;
- +0x5B4 current-club context as a budget controller;
- Balance objective records as chairman spending budgets;
- DBRUser +0x698 bank-loan state as transfer-budget state;
- +0x690 concessions;
- +0x69C sponsors;
- +0x6B0 stadium state;
- DBRUser +0x588/+0x590/+0x598/+0x5A0/+0x5A8 media-rights qwords as the five quarterly operating budgets;
- DBRUser support-staff list headers beginning +0x5B8/+0x5C4/+0x5D0 as grouped budget state;
- EAMChairmanNotEnoughFunds as a transfer-budget hard-cap check;
- the seven EAMchairextratransfersuccess selector values as seven budget categories;
- a false interpretation of 0x877540 as a global istringstream;
- the false WinMain command-line handoff route.

This negative evidence is valuable because it prevents future sessions from repeating expensive dead ends.

## Reconstruction implementation audit

The clean-room code is currently much less advanced than the reverse engineering.

Present files include:

- `reconstruction/fm2001_data.py`
- `reconstruction/verify.py`
- `reconstruction/app.py`
- `reconstruction/RUN_PROTOTYPE.cmd`

The parser currently supports the verified Master.dat/string layouts and Static.dat positions. The Tkinter prototype can browse clubs, players and managers and display current/target skills.

The verification harness checks counts and representative identities such as Arsenal, David Seaman, Nigel Winterburn, Alex Ferguson and Arsène Wenger.

Not yet implemented as gameplay:

- monthly player aging/development;
- training simulation;
- contracts and negotiations;
- transfer logic;
- finance/accounting;
- season simulation;
- AI;
- save compatibility;
- match engine;
- FastView.

This is the largest gap between research progress and construction progress.

## Quality audit

### Strong points

1. Exact release hashes are recorded.
2. Findings are increasingly grounded in original loaders, RTTI, named tuning keys, formatter tokens and concrete call paths.
3. Confirmed / probable / hypothesis distinctions are generally respected.
4. Failed and superseded interpretations are preserved explicitly.
5. Checkpoint cadence is now strong enough that timeouts rarely lose important work.
6. A data-free clean-room boundary is maintained for reconstruction code.

### Weak points / risks

1. The research documentation has grown faster than its canonical summaries; FINDINGS.md has lagged EXECUTABLE_ANALYSIS.md at times.
2. Older notes frequently say “game/session +offset”; these should now be read as DBRUser-relative where applicable.
3. PROGRESS.md became stale during the long finance trace; its active section was refreshed during this audit.
4. The clean-room implementation substantially lags the recovered mechanics.
5. Automated regression tests cover the static data parser but not yet development, training, transfers or finance formulas.
6. Windows Smart App Control blocks meaningful execution of the original executable on the current host, so much executable work is static analysis. A compatible test environment or controlled VM would improve behavioral validation.
7. Save serialization and the match engine remain major uncertainty clusters.

## Recommended next sequence

1. Finish the authoritative transfer-budget derivation/storage trace in DBRUser/board logic.
2. Immediately implement and unit-test the already-recovered player development and training systems in `reconstruction/`.
3. Implement contracts/transfers and Balance cash/accounting behavior with deterministic tests.
4. Expand the clean-room data parser to the Static.dat tables already decoded.
5. Decode enough save serialization to permit state persistence.
6. Deepen season AI, scouting and youth.
7. Make the match calculator the next major reverse-engineering phase.
8. Treat FastView/.SCI as a separate presentation reconstruction after backend match behavior is understood.



## Audit-window additions

Three additional monthly maintenance findings were committed during the audit window and are part of the current canonical state:

- monthly DBRUser routine `0x42AEB0` is a maintenance cash-debit dispatcher, not the chairman quarterly rebudget producer;
- accounting category **601** = stadium-size maintenance selected from `SM_10000..SM_100000`;
- accounting category **602** = major facility/building maintenance for School, Hotel, Hospital, Club, Training, Parking and Merchandising facilities;
- accounting category **603** = pitch-system maintenance for sprinklers, drainage, pitch cover and heating;
- DBRUser `+0x65C` is a facility/building collection used by category-602 maintenance;
- DBRUser `+0x6A8` is pitch/stadium-installation maintenance state used by category-603 maintenance.

These findings further narrow the chairman transfer-budget search by eliminating another monthly/calendar branch that initially looked like possible rebudget logic.

## Current audit conclusion

The reverse engineering is substantive and technically useful, not superficial. The management side is much further along than the playable implementation.

The best description of the project today is:

> **A strong, evidence-backed reverse-engineering corpus with a verified clean-room data prototype, but not yet a reconstructed game.**

The next strategic improvement is to keep reverse engineering moving while beginning to convert already-stable mechanics into tested reconstruction code so implementation does not continue falling behind research.
