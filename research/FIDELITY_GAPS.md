# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| Secondary startup exact tie permutation and bucket shape | The startup-staff CRT boundary replays the independently recorded 262 total secondary schedule nodes / 45 nonempty buckets / 217 shuffle draws through an **aggregate-only MSVC checkpoint with no invented bucket vector**; tests enforce the proven World Cup-before-European Championship ordering without pretending to know every equal-key root permutation | Original reverse qsorted country-root traversal and post-secondary CRT state are documented, but the exact per-date mode-1 bucket vector and full equal-key native qsort order have NOT been independently source-locked; resolve from the canonical executable/real input before asserting pixel-calendar-level fidelity | 15 |
| Exact fully indistinguishable PL league-table native qsort ties | PL display now uses the previously recovered numeric and CP1252 short-name source comparator when original club short names are available; if two clubs have identical complete source keys, it explicitly falls back to deterministic display and refuses to publish an "exact" ranking | All comparator fields are recovered, but native qsort's relative order for truly identical complete source keys has not been independently locked; lightweight synthetic clubs missing valid CP1252 names also receive documented display-only fallback | 15 |
| Persistent-injury availability count | Approximation around the inputs to helper `0x405080` | Injury generation/persistence is substantially recovered, but this availability helper is not exact | 15 |
| Original FM2001 save compatibility | Modern port now has a versioned internal schema-34 save/reload path | Original PLM2001 save format is not yet supported | 15 or later fidelity work |
| Autonomous transfer-window lifecycle | Fresh-game country gates start at the proven enabled value; later dated toggles are not yet driven from source boundary data | Runtime country +0x54 consumer/toggle behavior is known, but the complete source boundary mapping is unresolved | 15 or earlier if season transfer timing requires it |
| Contract month-end normalization | Recovered contract paths advance by the source-backed calendar-month count. When the source day does not exist in the final target month, the modern runtime clamps to that month's final valid day so long-duration play cannot crash | Exact end-of-month normalization in the original date helper (`0x64CDD0` / callers including `0x4192B0`) is not yet instruction-locked. The clamp is a bounded compatibility approximation, not an original-behavior claim | 15 or earlier if private executable tracing becomes available |
| Autonomous contract category helper | The exact 0x423340 age/category month table is used; the current port labels a clamped competition valuation category as an approximation for the unresolved 0x4FA510 category source | Exact 0x4FA510 category-source mapping remains unresolved | 15 or earlier if contract-term fidelity requires it |
| Autonomous buy-counter lifecycle | The recovered >28-player buyer gate and 3/8 thresholds are represented with a persisted neutral counter, incremented on AI purchase | Exact club +0x1ED update/reset lifecycle remains unresolved | 15 or earlier if long-season transfer frequency requires it |
| Player negotiation residual branches | The proven ordinary money path handles accepted, low-wage, counter-offer, already-signed and recently-joined outcomes; unresolved 0x422803 / invalid-duration 0x423340 branches return explicit deferred states | Remaining refusal/status and duration-revision policy is not guessed | 15 or earlier if a broader negotiation case blocks play |
| Due-transfer same-day ordering | Scheduled MPMTransferPlayer objects execute in reconstructed day maintenance after the date's fixture block | Exact original ordering relative to a fixture on the same due date is not yet instruction-locked | 15 or earlier if same-day transfer availability matters |
| Chairman legacy budget-event family | Modern port does not invent a live transfer/wage-budget scalar; ordinary play uses proven Balance/accounting paths | A0/A1/settings/warning payloads are persistence-loadable, but no ordinary fresh-game producer or Finance/Transfer UI consumer is mapped in the shipped executable | 15 or earlier if new evidence appears |
| Match-day / recurring commercial income | Normal Premier League gate income is integrated; English Cup gate RNG and policy inputs are integrated but the special both-controlled-participants category-1/category-2 posting branch is not | The Cup/knockout applicability flag and independent controlled-participant posting branches are proven, but the exact business-policy split has not yet been instruction-closed. The authorized canonical executable is accessible again from the ChatGPT Library, so this is now a pending trace rather than a source-access blocker. Do not infer revenue sharing. Fresh-game concession income remains disabled because its generator does not activate records | 15 |
| Finance/board residuals | Gate-10 ordinary Premier League finance and recovered board/job-security behavior are integrated | Remaining items are legacy chairman budget-event fidelity, support-staff amount materialization, broader cup gate/facility behavior, and unresolved EA-facing category labels | 15 or owning later system |
| Original front-end presentation | Temporary Tk prototype now has a functional Play tab, but it is intentionally not the original FM2001 presentation | Authorized original screen/audio resources should be inventoried, reused, and converted where needed | 13-14 |
| UI fidelity | Minimum human gameplay controls exist; original FM2001 screen structure/workflow is still unreconstructed | Original screen/workflow restoration incomplete | 13 |
| FastView/3D | Largely unreconstructed | Intentionally low priority until gameplay is stable | 14 |

## Resolved or superseded gaps

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

**Resolved for Gate 8.** The source-bound JSON save path now uses schema 10 and persists the live
human-game runtime, both relevant RNG streams, league/result state, player
Condition/Form/injury/suspension/development state, tactics, scheduler order,
and even a pending mid-matchday human fixture. File saves default to gzip and
the temporary Play tab exposes Save Game / Load Game. A canonical Arsenal branch
saved before the 26 August 2000 human fixture and reloaded into a fresh runtime
remained exactly equal through 23 September / 60 stored PL results. See
`research/GATE8_INTERNAL_SAVE.md`.

This does **not** claim compatibility with original FM2001 save files; that is
retained above as a separate fidelity gap.

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
