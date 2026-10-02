# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| Secondary startup exact tie permutation and bucket shape | The startup-staff CRT boundary replays the independently recorded 262 total secondary schedule nodes / 45 nonempty buckets / 217 shuffle draws through an **aggregate-only MSVC checkpoint with no invented bucket vector**; tests enforce the proven World Cup-before-European Championship ordering without pretending to know every equal-key root permutation | Original reverse qsorted country-root traversal and post-secondary CRT state are documented, but the exact per-date mode-1 bucket vector and full equal-key native qsort order have NOT been independently source-locked; resolve from the canonical executable/real input before asserting pixel-calendar-level fidelity | 15 |
| Autonomous transfer-window lifecycle | Fresh-game country gates start at the proven enabled value; later dated toggles are not yet driven from source boundary data | Runtime country +0x54 consumer/toggle behavior is known, but the complete source boundary mapping is unresolved | 15 or earlier if season transfer timing requires it |
| Autonomous contract category helper | The exact 0x423340 age/category month table is used; the current port labels a clamped competition valuation category as an approximation for the unresolved 0x4FA510 category source | Exact 0x4FA510 category-source mapping remains unresolved | 15 or earlier if contract-term fidelity requires it |
| Autonomous buy-counter lifecycle | The recovered >28-player buyer gate and 3/8 thresholds are represented with a persisted neutral counter, incremented on AI purchase | Exact club +0x1ED update/reset lifecycle remains unresolved | 15 or earlier if long-season transfer frequency requires it |
| Player negotiation residual branches | The proven ordinary money path handles accepted, low-wage, counter-offer, already-signed and recently-joined outcomes; unresolved 0x422803 / invalid-duration 0x423340 branches return explicit deferred states | Remaining refusal/status and duration-revision policy is not guessed | 15 or earlier if a broader negotiation case blocks play |
| Due-transfer same-day ordering | Scheduled MPMTransferPlayer objects execute in reconstructed day maintenance after the date's fixture block | Exact original ordering relative to a fixture on the same due date is not yet instruction-locked | 15 or earlier if same-day transfer availability matters |
| Chairman legacy budget-event family | Modern port does not invent a live transfer/wage-budget scalar; ordinary play uses proven Balance/accounting paths | A0/A1/settings/warning payloads are persistence-loadable, but no ordinary fresh-game producer or Finance/Transfer UI consumer is mapped in the shipped executable | 15 or earlier if new evidence appears |
| Match-day / recurring commercial income | Normal Premier League gate income is integrated; English Cup gate RNG and policy inputs are integrated but the special both-controlled-participants category-1/category-2 posting branch is not | The Cup/knockout applicability flag and independent controlled-participant posting branches are proven, but the exact business-policy split has not yet been instruction-closed. The authorized canonical executable is accessible again from the ChatGPT Library, so this is now a pending trace rather than a source-access blocker. Do not infer revenue sharing. Fresh-game concession income remains disabled because its generator does not activate records | 15 |
| Finance/board residuals | Gate-10 ordinary Premier League finance and recovered board/job-security behavior are integrated | Remaining items are legacy chairman budget-event fidelity, support-staff amount materialization, broader cup gate/facility behavior, and unresolved EA-facing category labels | 15 or owning later system |
| Original front-end presentation | Normal `app.py` launch now uses the fixed 800x600 source-backed `OriginalGameTkHost`; original PStartMenu/TeamSelect assets and a bounded PMenu/Squad/League Fixtures/PMatchInfo/League Tables management slice are live, while the generic ttk/Play prototype is explicit opt-in only | Repository schema 8 substantially restores the source-backed front-end/management workflow, but the expanded path still needs a fresh real-Windows 11/Tk receipt and re-audit; unrecovered surrounding management pixels, linked-context PMatchInfo details, and other secondary presentation remain fail-closed | 13-14 |
| UI fidelity | A representative original-style management route now exists from PStartMenu -> TeamSelect -> PMenu -> Squad / League Fixtures / source-accepted PMatchInfo / League Tables using recovered geometry and original assets; unresolved actions/pixels are deliberately withheld instead of replaced by generic controls | The representative workflow is only partially source-closed and has not yet passed the current schema-8 real-Windows recognizability audit; ordinary fixture-cell linked context, some Squad pointer equivalence, owner-local popup children, and the wider management shell remain incomplete | 13 |
| FastView/3D | Reconstructed match events now project through source-backed FastView semantic routes into a bounded presentation shell; a seven-target `PossessionFigures`/`PossessionDiagram` basename resolver fails closed until exact private-disc paths are uniquely proved | Original resource paths/placement geometry, side orientation, territory thresholds, audio bindings, commentary, and SCI/3D choreography remain unclosed; no guessed match-view layout is shipped as original behavior | 14 |

## Accepted modernization limitations

These are deliberate, documented differences for the current Windows 11
modernization release scope. They are **not** claims about original FM2001
behavior and can be revisited after the release baseline if stronger source
evidence or a compatibility requirement appears.

### Original FM2001 save-file import

The port does not import or write the original PLM2001 save format. The modern
runtime instead uses the versioned internal schema-34 save/reload path, which is
covered by canonical continuation, season-transition, and repeated save/reload
stress. Backward compatibility with 2000-era save files is not a Gate-17
installation/gameplay criterion or part of the final definition of done, so it
is accepted as a disclosed compatibility limitation rather than an open
behavioral reconstruction blocker.

### Fully indistinguishable Premier League native qsort ties

The source comparator is recovered through every observable key: points,
played, goal difference, goals for, goals against, and raw CP1252 short-name
bytes. When two clubs are identical on that complete key, the original
comparator returns equality and the relative order is an implementation detail
of the legacy native qsort rather than a further football rule. The modern
runtime keeps a deterministic fallback for display/stability and explicitly
withholds an "exact" ranking for that exceptional state. That fallback is
accepted for the modernization release and must never be described as the
original tie order.

### Invalid target-month contract dates

Recovered contract paths apply a source-backed integer number of calendar
months. When the source day does not exist in the target month, the modern
runtime clamps to that month's final valid day. Exact legacy normalization in
`0x64CDD0` is not instruction-locked, so the clamp remains a bounded safety
difference rather than an original-behavior claim. Gate-16 destructive testing
proved the clamp prevents long-duration date overflow without masking broader
state corruption. This bounded normalization is accepted for the modernization
release and must remain disclosed until/unless the legacy helper is later
closed.

## Resolved or superseded gaps

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
now uses internal schema **34** and persists the live human-game runtime,
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
