# Recovery654 — original 510D60 readiness AL, four 407770 gates, and 511120 wrapper

15 October 2026 KST. Baseline main `6ad944c7d1ee21cf3cb6623623f3b94620cb08ca`. Gate 13 remains OPEN, Gates 14–17 OPEN. Original authorized private `footballmanager.exe` was retrieved byte-for-byte from the recorded private Google Drive direct access file, verified **4,714,541 bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3**, and **statically disassembled only** using local PEi386 objdump. Never launched, patched, committed or shared original executable bytes.

## Actual native branch source

Entry virtual+0x34 `510D60` caches raw global `877530` into processing context+D3C at 510D95/510D9B, resets arrays, computes source context counters D0C/D10/D14/D18 and sets initial D24/D28/D2C defaults (already recorded in Recovery634). This does **not** prove the full match context is initialized. The previous source prefix ended before the important native eligibility branch and left the AL outcome unknown.

The new bounded static trace covers the *actual reached* original call sequence:

| Call | First party object | Argument | If original EAX == 0 |
|---|---|---:|---|
| `510EE5 -> 407770` | context+0 source team | 0 | `510EEC -> 511106` sets context+5A4/B54 zero and returns AL=0 at 511115 |
| `510EF9 -> 407770` | context+5B0 source team | 0 | `510F00 -> 511106` same zero/return |
| `510FFA -> 407770` | context+0 team | 1 | `511001 -> 5110EE` zeros context+5A4/B54 and returns AL=0 at 5110FF |
| `51100F -> 407770` | context+5B0 team | 1 | `511016 -> 5110EE` same zero/return |

The **first zero result short-circuits**; later native calls are not reached. Only **four nonzero** EAX values from the actual reached native calls proceed through the subsequent optional original human/registration/408170 +D48 callback branches to `5110E7: mov al,1`, returning AL=1. Original `510F06->5111A0`, `40D860`, `405890`, `421BA0`, `510A20`, `6314E0`, `631630`, `4139E0`, `4080F0`, `4037B0`, `403850`, `408170`, and earlier registration/date helpers have *other side effects/unknown outcomes*: the four-gate outcome alone is not a full processing context, nor proof native callbacks were executed by the port. The first early checks are **407770(0)**; the later checks are **407770(1)**, not two retries of the same predicate. Do not map them to a reconstructed human fixture from first principles without source qualification.

Original `511120` calls `510D60` at `51112A`, saves AL in BL, then independently obtains virtual+28 kind. For *kind 5*, regardless of saved AL, source `513E80` writes context+D28 and `513E70` writes context+D2C. **Only if** the base AL was nonzero does the wrapper store match+50 to context+D24. It returns the cached base AL at `511166`, not a newly computed result. Six original literal virtual+28 kinds are source-verified; exceptional `7C4CE4/668766` diagnostic kind remains unqualified and is rejected.

## Implemented source boundary

`reconstruction/original_leaguematch_native_process_owners.py` now contains `source_original_510d60_four_readiness_gate_return`. It requires the actual class vtable and precisely *only* the original reached 407770 EAX nonzero flags; later unvisited flags must remain None. It returns an immutable branch receipt with exact native source call-site sequence, AL, failure epilogue, and context+5A4/+B54 zero write intentions; for wrapper vtables it reuses the preexisting source-proven `source_original_wrapped_prepare_511120_post_base`, including the required kind5 results. It does **not** invoke native callbacks, source actual side effects, live GameState, Save/Load, results, modes, or calendar.

`reconstruction/test_original_leaguematch_native_process_owners.py` extends existing CI-listed focused tests for all four first-failure positions and the all-success path; six literal native class vtables and kind5 post-base behavior; fail-closed unknown diagnostic vtable, optional branch statuses and extra/unreached callbacks; and 19 exact source opcode checks when `FM2001_ORIGINAL_EXE` is supplied privately. The local original PE opcode sites were verified independently; exact branch head Python CI and full suite still need review before integration. Do **not** count this as an original GUI runtime test.

## Next highest priority and integration stop

Source-qualify actual native **407770(0)/(1)** meaning/owners and intermediate `5111A0`, `40DA30`, `40D860`, `6314E0/631630`, human condition branches and `+D48` state, and determine whether source-owned original LeagueMatch/fixture structures can be represented in durable portable GameState while preserving original v38/v3c callback world, calendar writes and Save/Load. Do not infer true/false AL just from reconstructed XI or map the v34-false `512D80` random fallback to every modern Quick3 fixture. Continue original four match mode player route and original event production on an independently source-backed context, then physical Windows 11 GUI comparison; all original leagues and 2–6-human careers and release Gate17 remain open. High-risk PR739 continues separate/unmerged.
