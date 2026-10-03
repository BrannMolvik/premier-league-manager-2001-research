# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| Secondary startup exact tie permutation and bucket shape | The startup-staff CRT boundary replays the independently recorded 262 total secondary schedule nodes / 45 nonempty buckets / 217 shuffle draws through an **aggregate-only MSVC checkpoint with no invented bucket vector**; tests enforce the proven World Cup-before-European Championship ordering without pretending to know every equal-key root permutation | Original reverse qsorted country-root traversal and post-secondary CRT state are documented, but the exact per-date mode-1 bucket vector and full equal-key native qsort order have NOT been independently source-locked; resolve from the canonical executable/real input before asserting pixel-calendar-level fidelity | 15 |
| Exact fully indistinguishable PL league-table native qsort ties | PL display now uses the previously recovered numeric and CP1252 short-name source comparator when original club short names are available; if two clubs have identical complete source keys, it explicitly falls back to deterministic display and refuses to publish an "exact" ranking | All comparator fields are recovered, but native qsort's relative order for truly identical complete source keys has not been independently locked; lightweight synthetic clubs missing valid CP1252 names also receive documented display-only fallback | 15 |
| Original FM2001 save compatibility | Modern port now has a versioned internal schema-35 save/reload path | Original PLM2001 save format is not yet supported | 15 or later fidelity work |
| Player negotiation residual branches | The proven ordinary money path handles accepted, low-wage, counter-offer, already-signed and recently-joined outcomes; unresolved 0x422803 / invalid-duration 0x423340 branches return explicit deferred states | Remaining refusal/status and duration-revision policy is not guessed | 15 or earlier if a broader negotiation case blocks play |
| Due-transfer same-day ordering | Scheduled MPMTransferPlayer objects execute in reconstructed day maintenance after the date's fixture block | Persisted evidence proves 0x613EE0 is first inside 0x4A8070, but does not preserve the missing outer call relationship between 0x4A8070's dated-process queue and same-day match execution. Fresh disassembly is currently blocked by the worker's process-start ClientError, so fixture ordering remains fail-closed rather than inferred. | 15 or earlier if same-day transfer availability matters |
| Match-day / recurring commercial income | Normal Premier League gate income is integrated. English Cup gate RNG/policy inputs are integrated, and the source-proven special posting tail now has an accounting helper that can independently credit both controlled participants' category-1/category-2 receipts using each participant's own ticket prices. Full live Cup receipt attachment remains pending. | The Cup/knockout applicability flag and controlled-participant posting mechanics are instruction-bounded; no narrower business-policy label such as revenue sharing is claimed. Fresh-game concession income remains disabled because its generator does not activate records. | 15 |
| Finance/board residuals | Gate-10 ordinary Premier League finance and recovered board/job-security behavior are integrated; the legacy chairman budget-event family is already proven irrelevant to the ordinary shipped fresh-game path | Remaining live items are support-staff amount materialization, broader cup/facility integration, and unresolved EA-facing category labels | 15 or owning later system |
| Original front-end / management presentation | Fixed 800x600 host preserves #177 original seasonal base/header. Ordinary fixture report gesture is source-proven WM_RBUTTONDOWN, with a read-only cell/link adapter and uncaptured-fixture no-op. PR #183 closes native participant/script/possession snapshot codecs and skill flags | Complete live calculator/completion report inputs and report owner/save integration remain absent. See `GATE13_FIXTURE_REPORT_CAPTURE_TRACE.md`; codec fragments and scores/completion never imply a context. Normal-play/timing criteria await the real calculated-report route. Other club backdrop families remain fail-closed | 13 |
| UI fidelity | Real Windows schema-8 original-art/navigation path passes, including the native right-press no-op; base-image generator 0x5D3560 is already integrated by #177 | Receipt success is not ordinary successful captured-report opening or a human recognizability judgment. Full report production is the next implementation blocker; unproven Squad/post-transition and owner-local popup pixels remain withheld, without expanding the closure scope to obscure secondary screens | 13 |
| FastView/3D | Reconstructed match events project through source-backed FastView semantic routes; the exact PossessionDiagram FastView source paths, four byte-identical staged EA444 assets, 294x78 base-pitch/overlay geometry, private one-call territory transition, and PossessionFigures percentage text rectangles are now source-closed | Original update cadence/lifecycle reset, user-team side orientation, three 82x16 possession-bar placement/binding, audio bindings, commentary, and SCI/3D choreography remain open; unresolved behavior stays fail-closed | 14 |

## Resolved or superseded gaps

### Autonomous monthly purchase-counter lifecycle

**Resolved in Gate 15.** The transfer-stat object at club `+0x1E0` carries
monthly and season transfer bytes. Permanent player arrival reaches
`0x422F70 -> 0x405190 -> 0x4F3290`, which increments monthly arrivals at
club `+0x1ED` and the adjacent season-arrivals byte at `+0x1EE`. The modern
persisted `ai_transfer_buy_counter` now represents the exact monthly
`+0x1ED` byte and is incremented by the shared permanent-transfer completion
path, so human and autonomous purchases count identically.

Month start is also source-ordered. Late daily path
`0x4A81A0 -> 0x40BB10 -> 0x4042E0 -> 0x4F3320` clears the monthly
sold/bought bytes only after same-date Saturday autonomous transfer maintenance
and payroll. The reconstruction therefore resets `+0x1ED` only after weekly
transfer work on day 1, not through the earlier generic monthly hooks.

The shipped buyer predicate has a deliberate quirk: `0x403E70` reads the
same monthly byte `+0x1ED` for both `MaxPlayersBuyMonthly = 3` and
`MaxPlayersBuySeason = 8`. The adjacent season byte exists, but this buyer
gate does not read it; the port preserves that behavior instead of substituting
a more plausible season counter.

### Autonomous contract category helper

**Resolved in Gate 15.** `0x4FA510` calls `0x4F8FF0` to resolve the
competition's country and `0x410FF0` to return the competition's zero-based
index in `DBRCountry +0x48/+0x4C`, not its packed valuation category.
Country construction puts only root League (kind 1) and DummyLeague (kind 3)
objects into this subset and qsorts it through `0x4F79D0`: League roots
precede DummyLeague roots, and each kind is ordered by ascending packed
`initialization_order_value`.

Canonical England therefore stores
Premier League / Division 1 / Division 2 / Division 3 / Conference /
Conference 2 at subset indices 0..5. The five playable League indices map
exactly to the five rows in `0x423340`; the trailing DummyLeague index 5 is
outside that table. The modern autonomous contract-duration path now resolves
this exact subset index and fails closed outside rows 0..4 instead of clamping
a guessed valuation category.

This trace also supersedes the old Gate-10 all-root FanFactor interpretation:
`0x5DA2F0` indexes the host club's registered League/DummyLeague subset entry.
Premier League is index 0 and therefore uses **FanFactor1 = 0.9**; the Cup gate
adapter now uses the host club's league index rather than the Cup competition.

### Contract calendar-month normalization

**Resolved in Gate 15.** Direct disassembly of shared date helper `0x64CDD0`
shows that the original does not preserve or clamp the source day. It first
writes decomposed day = 1, then advances the year/month pair by the requested
month span. Contract callers including `0x418FED`, `0x4191AF`,
`0x4192CE` and youth/date caller `0x61E65B` serialize that normalized
date through `0x64CE30`. The modern shared
`contract_expiry_from_month_span()` now returns the first day of the target
month exactly, including for a zero-month span.

### Autonomous transfer-window lifecycle

**Resolved in Gate 15.** Canonical `Static.dat` country bytes `+28..+35` are
the four `(week, weekday)` transfer-window boundary pairs copied into runtime
`DBRCountry +0x24..+0x2B`. Fresh construction sets country gate `+0x54 = 1`.
`0x411020 -> 0x64D500` materializes each enabled boundary from the primary
season Monday anchor as `anchor + 7*(week-1) + (weekday-1)`. Daily
`0x411850 -> 0x411190 -> 0x4112D0 -> 0x411380` compares every enabled
boundary with the current date and XOR-toggles `+0x54` once for each match.
The country pass runs before the later Saturday autonomous-transfer maintenance.

The modern runtime now parses all four source pairs and applies the exact
daily toggle before `run_weekly_ai_transfer_maintenance()`. The existing
persisted gate boolean remains sufficient for save/reload, so internal save
schema 34 does not change. England's canonical pairs close the gate on
30 March 2001 and reopen it on 31 May 2001.

### Chairman legacy budget-event family

**Proven irrelevant to the ordinary shipped fresh-game path in Gate 15.**
Static constructor/callsite analysis shows `EAMbcstartseasonmail`,
`EAMbcmonthlybudget`, `EAMchairbudgetsettings` and
`EAMchairbudgetwarning` are persistence-compatible event classes, but the A0/A1
constructors are reached only through the generic event factory used by
persistence readers. The named `*Budget` / `*Budget2K` tuning globals have
loader writes but no recovered ordinary runtime consumer, normal
`PFinanceOverview` is Balance/accounting-ledger driven, and `PTransfer2K` has no
mapped dependency on those budget events/globals. The modern port therefore
correctly **does not invent** a live transfer/wage-budget scalar for ordinary
fresh games. Legacy-save or deliberately materialized event payloads remain a
documented compatibility boundary and are not claimed impossible.

### Persistent-injury availability count

**Resolved in Gate 15 work-ahead.** The non-user persistent-injury guard calls
the same source helper `DBRClub::0x405080` already recovered for the
selling-club transfer decision. The runtime now shares the exact four-state
predicate: transfer-listed, injured, loaned-out and suspended players are
excluded from the available count; a separate modern selection-only exclusion
is not. Tests cover the exact exclusion set, the 14-player boundary, and the
fact that the guard consumes no injury RNG when the exact count falls below 14.

### Source-exact Premier League table comparison for identifiable clubs

**Resolved for source-backed club names, pending native visual presentation.**
The original `0x4F45E0` points-descending, played-ascending, goal-difference-
descending, goals-for-descending, goals-against-ascending, and then raw
CP1252 short-name-byte comparison is now used by `PremierLeagueState`
when its caller provides canonical club short-name bytes. The
`GameState.premier_league_table()` display/management bridge
passes real canonical club names where present, and its match/financial
objective ranking-dependent paths use that same bridge. The standalone
`PremierLeagueState` retains a clearly named deterministic club-ID
display fallback only when caller source names are unavailable.
`exact_ranking()` is withheld on unresolved full-key equal ties;
no unproven native qsort tie permutation is invented. This improves
the backend powering the upcoming original Gate13 league table; it
does **not** claim the original table artwork, fonts, screen navigation,
graphics or Windows visual smoke test has been recreated.


### Broader competitions / connected annual world

**Resolved in Gate 12.** The canonical real-data runtime now connects English
Cups, European groups/knockouts, required English divisions, qualification-only
Cup owners, annual League/DummyLeague qualification, promotion/relegation, and
atomic next-season primary regeneration. The 4 July 2000 -> 4 June 2001 audit
captured every required annual source and produced a fresh 380-fixture year-two
Premier League while retaining all played qualification-source Leagues. See
`research/GATE12_COMPLETION_AUDIT.md`.


### Dynamic FA Cup replay primary order

**Resolved in Gate 12.** Canonical `0x615A60` clamps the candidate to at
least current relative day + 1, probes candidate-1 through candidate+1 through
`0x615890 -> 0x615790`, restarts from conflict day + 2, and when clear
head-inserts the Replay by storing the old bucket head at match `+0x04` and
the Replay as the new bucket head. The clean-room runtime now reproduces the
date displacement and post-shuffle head insertion in both the full-primary
shadow and executable-order primary scheduler.



### Balance credit secondary category 1600 debit

**Resolved in Gate 10.** `Balance::credit 0x5DC510` adds the full primary
credit, computes a secondary floating finance value as
`incoming * 0.01 * 0.2`, debits that value through category 1600 / flag 1,
then appends the primary credit transaction. No integer truncation occurs.
The modern Balance preserves fractional values and schema-10 internal saves
roundtrip them. Finance Overview queries category 1600, but its EA-facing label
remains unresolved.

### Internal modern-port save/load

**Resolved for Gate 8 and evolved since.** The versioned source-bound JSON save path
now uses internal schema **35** and persists the live human-game runtime,
relevant RNG streams, league/result state, player
Condition/Form/injury/suspension/development state, tactics, scheduler order,
and later-gate competition/transfer/finance state. File saves default to gzip.
The original Gate-8 canonical Arsenal branch saved before the 26 August 2000
human fixture and reloaded into a fresh runtime exactly through 23 September /
60 stored PL results; later Gate-12/16 work additionally exercises schema-34
season transitions and repeated save/reload stress. See
`research/GATE8_INTERNAL_SAVE.md` and the current `project_status.json`.

This does **not** claim compatibility with original FM2001 save files; that is
retained above as a separate fidelity gap.

Schema 35 adds explicit retention/validation of the actual calculator's
captured-possession output in saved pending matchday results. This does not
close full live captured-report production/ownership/save persistence or
ordinary PMatchInfo opening. Participant rating/skill outputs and identities
are retained transiently at live completion; remaining inputs stay absent.
See `GATE13_LIVE_CAPTURE_INPUTS.md`. Strict schema-34 migration is not claimed.

### Human-controlled minimum gameplay loop

**Resolved for Gate 7.** One human Premier League club now uses the same
reconstructed MatchCalculator, persistence, scheduler, table, injury,
discipline, Form, Condition and Pitch Wear backend as autonomous AI clubs.
The temporary Play tab supports club, formation, XI/bench, tactics, advance,
match simulation, result and table. A canonical Arsenal run completed six
human fixtures from 19 August through 23 September 2000 while all six full
10-match matchdays continued in recovered scheduler order. See
`research/GATE7_HUMAN_GAMEPLAY.md`.

This does not resolve original front-end fidelity, transfers/finance, or
save/load; those remain separate later gates.

### Real-data full-season integration

**Resolved in Gate 6.** Three deterministic canonical 38-round / 380-fixture
Premier League seasons completed with exact recovered scheduler order and
coherent table, lineup, injury/return, suspension/resolution, Form, Condition
and Pitch Wear state. See `research/GATE6_FULL_SEASON.md`.

### Same-day Premier League execution order

**Resolved in Gate 4.** The complete 9,346-node primary schedule is placed
through the recovered 373-bucket `0x615950` path and shuffled from corrected
state `0x0E556598` through `0x615BE0 -> 0x615AE0`. `0x615C10` confirms
head-to-tail traversal after shuffle. The first ten real Premier League
matchdays are regression-locked; see `research/GATE4_SCHEDULE_ORDER.md`.

The standalone matchday API still permits deterministic fixture-ID order when
no reconstructed startup scheduler order is supplied. That is now an explicit
integration fallback for synthetic callers, not an unresolved original-order
question.

### Startup RNG before first PL shuffle

**Resolved in Gate 3.** One MSVC CRT stream spans the mapped precompetition
path and actual-count competition materialization. The canonical competition
phase consumes 6,156 bounded calls and ends at `0x0E556598`; the older
packed-capacity 6,165-call replay is retained only as a historical diagnostic.

### Runtime-player startup Python RNG mismatch

**Resolved for the currently mapped DBRPlayer startup block.**

Older audit text identified Python `random.Random` use for peak/development draws. `GameState.from_database` now uses `MsvcCrtRng` for the recovered startup sequence and retains the same RNG object for later autonomous simulation unless a caller explicitly supplies another RNG.

The mapped startup RNG timeline through primary schedule finalization is now solved through Gates 3 and 4. Gate 5 is the integration boundary: feed the recovered scheduler order into canonical real-data matchday execution.

### Missing authoritative AI match-day initialization

**Superseded as the principal blocker.**

The autonomous Premier League path now includes strategy/formation, lineup/bench selection, runtime role state, participant collection, environment generation, MatchCalculator simulation, persistence, and result/table storage. Remaining user-controlled setup is a separate Gate 7 concern.

## Fidelity rule

A deterministic fallback is allowed while a subsystem is being reconstructed, but it must:

1. be named as a fallback in code/docs;
2. have a corresponding entry here if it can change observable game behavior;
3. be removed or explicitly accepted before Gate 17.


## Financial-objective lifecycle / dismissal side effect

**Resolved for Gate 10.** The fresh Premier League candidate set, selection
cash/target mutation, three-year deadline, sporting `+0x68` progression for
same-PL IDs 13/1/5/6, 95% reason-5 threshold, persistent DBRUser-equivalent
sacking reason, and single-user control exit are integrated and save-persistent.

A separate narrow approximation remains at exact Premier League table ties: the
original equal-points fallback after points/goal difference/goals scored is
still unresolved, so a perfect tie exactly across an objective cutoff can use
the modern deterministic club-ID fallback.
