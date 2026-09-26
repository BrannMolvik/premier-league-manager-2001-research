# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| League-table final tie fallback | Club ID after points / GD / goals scored | Exact original fallback after the first three keys is unresolved | 15 or earlier if standings behavior requires it |
| Persistent-injury availability count | Approximation around the inputs to helper `0x405080` | Injury generation/persistence is substantially recovered, but this availability helper is not exact | 15 |
| Original FM2001 save compatibility | Modern port now has a complete internal schema-2 save/reload path | Original PLM2001 save format is not yet supported | 15 or later fidelity work |
| Transfers/contracts | Research substantially ahead of implementation | Not yet a complete playable system | 9 |
| Finance/board | Research substantially ahead of implementation | Not yet a complete playable system | 10 |
| Broader competitions | Core structures known, full behavior incomplete | Premier League is the strongest reconstructed competition | 12 |
| Original front-end presentation | Temporary Tk prototype now has a functional Play tab, but it is intentionally not the original FM2001 presentation | Authorized original screen/audio resources should be inventoried, reused, and converted where needed | 13-14 |
| UI fidelity | Minimum human gameplay controls exist; original FM2001 screen structure/workflow is still unreconstructed | Original screen/workflow restoration incomplete | 13 |
| FastView/3D | Largely unreconstructed | Intentionally low priority until gameplay is stable | 14 |

## Resolved or superseded gaps

### Internal modern-port save/load

**Resolved for Gate 8.** Schema-2 source-bound JSON saves persist the live
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
