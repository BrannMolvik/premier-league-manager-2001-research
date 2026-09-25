# Fidelity Gaps

This file tracks **known differences or unresolved fidelity boundaries** between the clean-room reconstruction and the analyzed FM2001 release.

Historical uncertainty that has since been resolved should be moved to the resolved section rather than left as a live gap.

## Active gaps

| Gap | Current reconstruction behavior | Original status | Planned gate |
| --- | --- | --- | --- |
| Startup RNG before first PL shuffle | Shared MSVC CRT stream covers the mapped player-startup block and recovered startup helpers, but the full mandatory pre-shuffle path is not yet closed | Remaining TeamSelect lifetime/activation caller path is under investigation | 2-3 |
| Same-day Premier League execution order | Deterministic fixture-ID order unless an explicit scheduler order is supplied | Head insertion, PL source order, container, and Fisher-Yates are recovered; exact entering RNG state remains | 4 |
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

### Runtime-player startup Python RNG mismatch

**Resolved for the currently mapped DBRPlayer startup block.**

Older audit text identified Python `random.Random` use for peak/development draws. `GameState.from_database` now uses `MsvcCrtRng` for the recovered startup sequence and retains the same RNG object for later autonomous simulation unless a caller explicitly supplies another RNG.

This does **not** mean the entire startup RNG timeline is solved. The remaining gap is the set/order of other mandatory consumers before schedule finalization, tracked separately above.

### Missing authoritative AI match-day initialization

**Superseded as the principal blocker.**

The autonomous Premier League path now includes strategy/formation, lineup/bench selection, runtime role state, participant collection, environment generation, MatchCalculator simulation, persistence, and result/table storage. Remaining user-controlled setup is a separate Gate 7 concern.

## Fidelity rule

A deterministic fallback is allowed while a subsystem is being reconstructed, but it must:

1. be named as a fallback in code/docs;
2. have a corresponding entry here if it can change observable game behavior;
3. be removed or explicitly accepted before Gate 17.
