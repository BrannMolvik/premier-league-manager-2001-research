# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| League-table final tie fallback | Club ID after points / GD / goals scored | Exact original fallback after the first three keys is unresolved | 15 or earlier if standings behavior requires it |
| Persistent-injury availability count | Approximation around the inputs to helper `0x405080` | Injury generation/persistence is substantially recovered, but this availability helper is not exact | 15 |
| Real-data season integration | Unit/regression suite is broad, but season progression tests are mostly synthetic | Canonical raw data invariants are known; full 10-match / 380-match automated integration remains | 5-6 |
| Human-controlled match setup | Autonomous AI path is much further ahead | User-control initialization/workflow is incomplete | 7 |
| Save/load | No complete internal/original save workflow | Individual serialization findings exist | 8 |
| Transfers/contracts | Research substantially ahead of implementation | Not yet a complete playable system | 9 |
| Finance/board | Research substantially ahead of implementation | Not yet a complete playable system | 10 |
| Broader competitions | Core structures known, full behavior incomplete | Premier League is the strongest reconstructed competition | 12 |
| Original front-end presentation | Tk/data-browser prototype; original UI/music resources not yet integrated into the modern runtime | Authorized original screen/audio resources should be inventoried, reused, and converted where needed | 13-14 |
| UI fidelity | Tk/data-browser prototype rather than FM2001 interface | Original screen/workflow restoration incomplete | 13 |
| FastView/3D | Largely unreconstructed | Intentionally low priority until gameplay is stable | 14 |

## Resolved or superseded gaps

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
