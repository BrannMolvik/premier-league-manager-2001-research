# Recovery652 — real first-allocated CRT TLS seed vs reused live match thread

15 October 2026 KST. Baseline canonical main `e3b3f94f2508586a1c99dae0fdcda1d2bf4422a4`, after verified PR761 shared native 66951C/64D540 first/second bounded score RNG and CURRENT_STATE checkpoint. Source: 4,714,541-byte owner-authorized original `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, **original not executed or committed**. Gate13 and 14–17 remain open.

## 66D553 exact native conditional fresh/reused TLS state

Bounded canonical original source disassembly `66D540..66D5B9` proves a previously unresolved **first allocated thread-local CRT state** initialization but not that every existing game thread has that seed:

1. `66D553` queries the original TLS slot at global `84AD40` via imported TlsGetValue. If the returned record pointer is nonnull, `66D56D JNE→66D5AE` bypasses allocation and **does not reset** the existing RNG seed DWORD+14. An existing thread seed may be 0, 1 or any uint32 from earlier native CRT draws or explicit reseeding; don't assume new process equals freshly allocated thread.
2. If original GetTlsValue is NULL, native `66D56F` passes `0x74,1` to original `673211`, obtaining a new zero-initialized `0x74`-byte calloc CRT object. It calls imported TlsSetValue on global slot `84AD40`. If the source TlsSetValue fails, it branches to `66D5A6` runtime error handler and cannot publish a valid registered state.
3. On success, `66D591→66D540` writes the original pointer constant **0x84D430** to record+**0x50**, then writes **1** to original thread RNG seed DWORD+**0x14** (`66D54B C7 40 14 01 00 00 00`). Subsequent `66D598` imported source callback returns original EAX that is stored into record+0; native `66D59E` sets record+4 to **0xFFFFFFFF**. This is a concrete original default **only for the source-proven newly allocated thread**, not a general formula for live GameState save/load or a completed match.
4. The subsequent native score RNG `66951C` reads the selected thread record+14 and applies the shared authentic CRT `0x343FD/0x269EC3` LCG. For initial seed1, the first `66951C` returns rand15=**41** and updates seed to **0x0029E2C0**. Other reachable tasks, callbacks and matches may already consume one or more thread-local draws before `5DABED` or `5DAE68`.

`reconstruction/original_native_66d553_tls_initial_state.py` source-projects only those two distinct original TLS branches. An existing pointer requires its actual preexisting native record bytes; constructor or synthetic seed1 inputs are forbidden. A fresh null TLS pointer requires actual source 0x74 zeroed allocation, nonzero allocation pointer, successful original TlsSetValue EAX, and independently supplied original reached thread-ID callback EAX. The projected 0x74 record has only original +0,+4,+14,+50 writes, with explicit **no native callback or GameState mutation**. Unknown/failing source fields error rather than permit fabricated RNG. No claim is made about running TLS code on Windows11.

`test_original_native_66d553_tls_initial_state.py` covers fresh seed1 and exact untouched other allocation bytes, existing thread seeds0/1/0xFFFFFFFF/0xDEADBEEF never reset, projecting only a justified first-draw via already merged `source_original_64d540_bounded_tls_match_rng`, invalid/mismatched/failure branches and owner-private actual shipped PE site signatures. Registered focused Gate13 tests, **not yet exact-PR-head CI verified**; WIP preserved on `worker/gate13-r1-crt-tls-first-init-652` under batching policy.

## Actual next source-to-player work (do not stop at this research)

The real reconstruction still does not know **which existing per-thread seed was reached** by the current save/game process, all other original CRT RNG draws across game and match processing, or the x87-returned native bound prior to `5DABCA/5DAE45`. Source `5DA250` has multiple x87 computed branches and the effective original x87 control/precision values are only partly constrained; those must be recovered before replacing the current reconstructed Quick3 score computation with the actual 513010→5DA2F0→v38/v3c original engine. Normal PResults needs actual native 6168C0 first and second date-calendar v+10 callback events and correct 432505 postreturn; 3D mode0/1 and FastView mode2 presenters need real original lifecycle; true 2–6 saved human registry, all shipped leagues and original-vs-port **physical Win11 GUI** acceptance are still blocked. High-risk PR739 injury/schema48 remains unmerged. Gates13,14,15,16,17 are open, Windows11 release **not** verified.

Source-first evidence does not authorize generating match-result values or registering false calendar events; continue actual playable/saved world integration and batch next CI at a coherent source-to-player milestone.


## Recovery653: x87 first/second native match RNG input and safe TLS join

Continuing the exact active branch rather than restarting, canonical private
PE static disassembly from **5DAB0C–5DABFD** and **5DAE12–5DAE7C**
shows the first/second score stages have identical x87 bound computations:
- `5DAB0C` stores original `5DA250` ratio as native `ESP+0x10`.
  An x87 score/ceiling value remains in ST0 after the earlier
  `5DAB67→5DAB90` source compare/condition sequence.
- `5DAB97` (`5DAE12` second side) compares that native ratio against
  **source double 1.0** at original `0x7BD6B0`.
- Ratio **strictly greater than 1.0** executes source
  `5DABA8–5DABBE` (second side `5DAE23–5DAE39`):
  `ST0 = prior_clamped_score / (1000.0 × (ratio−1.0) + 100.0)`,
  with original 1000.0 at `0x7C6828` and 100.0 at `0x7BD6A0`.
- Ratio **less than or equal to 1.0** executes
  `5DABC2–5DABC4` (second `5DAE3D–5DAE3F`):
  `ST0 = prior_clamped_score × original binary64 0.01`
  stored at `0x7BD600`.
- The common `5DABCA`/`5DAE45` then invokes original
  `668350`: x87 control word temporarily selects truncation
  toward zero and FISTP converts to a signed return integer;
  original code sets `EDI=max(1, EAX)` and calls
  `64D540` at `5DABED`/`5DAE68`. That native call
  advances the original **per-thread** CRT 66951C state.
  A separate next `668350` consumes the remaining original
  x87 score value, so this first bound is **not the final score**.

The new `original_match_5dab97_fpu_tls_join.py` requires:
actual original stage ratio QWORD, independently captured previous
x87 score QWORD, the **actual** first 668350 signed result and a
typed original `66D553` freshly initialized OR reused TLS record.
It bridges these source inputs through already merged
`original_match_5dabca_score_rng_join` and the authentic
`64D540` source RNG implementation. It never creates an RNG
seed1 for existing threads, does not claim that native x87 or RNG
callbacks ran, and does not calculate public goals.

Its independent rational check uses the **exact original binary64
constant bits**, not a decimal approximation. Differences in
the native 80-bit x87 register precision can cause a different integer
near a truncation threshold. Such cases are deliberately **refused**
except mathematically exact zero with EAX=0, rather than
silently accepting an arbitrary reported EAX or claiming x87
equivalence. The original fresh-thread first random draw is a
source-derived candidate, not proof the actual original normal
match thread has not already consumed earlier random calls.

Source-proven actual shipped PE assertions: 14 original TLS
initializer opcode sites already independently verified, plus
**19 original first/second FPU bound opcode sites** and the
four exact PE double constants 1.0/1000.0/100.0/0.01 passed
independent local byte checks. The two new Python files were
registered in the focused Gate13 workflow, not yet exact-head CI
certified at the time of this note.

**Actual player gap:** current `HumanGameplayController`
uses modern reconstructed outcome logic rather than the native
513010→5DA2F0 calculator. Its ordinary Quick Match and source
PResults sprite acceptance do NOT prove these x87 values
were reached, nor source equivalence for 2–6 users, modal
mode0/1/2, native v38/v3c save callbacks, original calendar
event producer, or Windows11 GUI comparison. Keep Gate13–17
open. Next implementation should focus on *persisted actual
match state and normal user route* with source-valid reachable
inputs, rather than indefinitely growing disconnected
source-only helpers. Do not infer live x87 score from fixture count.
