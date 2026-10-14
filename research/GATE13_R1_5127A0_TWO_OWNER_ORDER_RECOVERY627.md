# Gate13 Recovery627: ordered original 0x5127A0 both-owner match transaction integration plan

**14 October 2026 KST, after verified PR726.** Canonical main `cde3f9b69eecbd5275331b9ab8cef5115be511a7`; PR726 exact-head focused Gate13 1,767 tests/142 skips, full reconstruction 4,288 tests/146 skips, repository asset policy successful. Source provenance is the private original 4,714,541-byte `footballmanager.exe`, SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original has only been statically inspected; source-preserving models and tests do not constitute native original runtime verification.

## Ordered world integration dependencies

The persistent native-world building blocks now on main are **bounded** rather than the original whole-game transaction. The next implementation must preserve the original **two EBX side passes**, without moving post-row availability or conflating manager/club identities:

| Native original stage | Existing source contract | Required before source-faithful live NEXT |
| --- | --- | --- |
| Each side: +0x294 roster traversal, 0x419490 | `original_native_419490_suspension_return_source.py` | Player count and per-player post-call state, possible dated pending 0x613EC0 event, unknown recipient callback must fail closed |
| Per-side 0x615D10 calendar search | Previous v3C original linked owner source models | Carry actual source lookup pointer **including NULL**, original registry mutations and vtable effects without replacing with arbitrary fixture |
| Each active row 0x4197C0 | `original_native_5127a0_row_incident_source.py`, `original_native_41a250_uefa_producer.py`, `original_native_4085d0_world_branch.py` and source 41A490 | Preserve row+0x48/+0x49/+0x4A, optional 0x41A5B0, 0x4085D0 status/role/club writes, original 0x64D540 RNG order and conditional event producers; existing restricted arg2=0 branch is not a substitute |
| After active rows 0x419680 on each side roster | `original_native_419680_availability.py` merged in PR726 | Re-read **post-row** player state and reuse same possibly-NULL 0x615D10 pointer; do not run once before rows or for wrong owner |
| After both owner passes late side selectors | 0x408030 composite +0xCC+2×+0xCE; 0x4080A0 +0xCA | Native owner +0xE8 masks, +0xF4/+0xF6 and +0x102/+0x104 conditional write order and team ownership |
| Event queue and delivery | Pending 0x613EC0 double-linked wrapper / 0x613EE0 dated trigger / 0x5CFA20 / 0x413020 manager dispatch | Prove subtype recipient and pending→delivered semantics, maintain distinct original calendar/event registries, never fabricate Inbox |
| Original normal player journey | Earlier R1 screen/navigation stubs | Actual NEXT → PPreMatch modes 0/1/2/3 → PResults → management return with persisted league/calendar/club world, user-visible controls and original graphics |

## Atomicity and blockers

Existing `GameState.native_player_discipline` and `GameState.native_status_world` remain source-owned, distinct from generic player fields. The original roster transaction must validate all reached source bytes, owners, row callbacks, calendar results and mutating event paths before committing a coherent world, not run partial source projections independently and then advance PResults.

**Immediate implementable source-backed slice**: build a deterministic two-owner *ordering/ownership guard* that consumes per-side roster IDs, row receipts, and qualified 419680 outcomes only if they were obtained after the corresponding earlier original 419490/4197C0 stage. Reject incomplete/extra per-player callbacks, incorrect team pointer, duplicate side/index or moved post-row availability. Keep it immutable and assert no live match advance. Only after the guard tests are verified connect the fully qualified mutating world to GameState. The original function owner/dates/events require further native source audit; never manufacture missing callbacks or claim gate completion.

**Still open:** Gate 13 player-facing all-modes original match parity, pending manager event world and original full calendar, other original shipped countries/leagues and multiple human managers; Gates14–17 and real Windows 11 graphical test/release acceptance. A useful code checkpoint is not a gate audit.
