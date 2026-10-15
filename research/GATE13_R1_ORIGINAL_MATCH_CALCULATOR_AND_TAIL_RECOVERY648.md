# Recovery648: original LeagueMatch 513010 calculator-to-world ordering

15 October 2026 KST. Original owner-authorized footballmanager.exe, 4,714,541 bytes, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Static disassembly only, never executed. Baseline main 73d42e9dab03c90d43bc1d5bd96916801c8bc110; Gate13 and Gates14–17 OPEN.

## Confirmed first-hand source

- 5130C2 calls native Match virtual+34 and tests AL. False calls 512D80 cleanup and jumps to 513294, but STILL invokes native v+38 and v+3C. No 5DA2F0 calculation on this false path.
- True v+34 calls 516080. True 516080 invokes 512D80 but jumps to 513235 then checks match+44 again at 513238. Therefore 516080 true is NOT an unconditional no-calculation branch.
- When 516080 false, 5130F4 tests human flag bit0x10 and complete flag bit0x20. Human/not completed may open PPreMatch, prepare mode, invoke match v+28 and mutate team state. A v+28 return of six jumps to 513238, which is NOT enough to prove that the actual calculator is skipped. Other paths use 632B20.
- Source 513238 reloads match+44 bit0x20 after ALL these callbacks. If clear, source 513252 invokes 5DA2F0 native match calculation. Only afterward at 513257 does source reload match+44 human bit0x10, and when true dispatch original mode0 -> 533D80(0), mode1 -> 533D80(1), mode2 -> 5331C0 FastView, mode3 -> no GUI presentation wrapper.
- Every route then joins 513294 native virtual+38 score latch and 5132A9 native virtual+3C world writeback. Skipping a match calculation is NOT permission to skip post-calc callbacks. Do not replace 3D/FastView with Quick3 or publish provisional score before verified native world changes.

## Implemented on WIP feature branch

reconstruction/original_match_513010_postcalc_phase.py models only source-reached v+34, 516080, post-preparation flags+44, post-calculator flags+44 and reached native mode. It returns the precise common calculator, presentation and mandatory v38/v3c ordering. It neither calculates a score nor mutates an event nor claims native GUI execution. It fails closed for unvisited native values.

test_original_match_513010_postcalc_phase.py covers actual mode0/1/2/3 wrappers, false v+34 still reaching v38/v3c, true 516080 not skipping calculator, bit5 completion, reloaded postcalculator human flag, wrong-source-field rejection. Fifteen exact original PE opcode signatures have been independently verified against canonical PE; optional test also checks five direct CALL targets. No exact-head CI has yet been run on the current WIP branch; no reviewable PR yet.

## Exact next player-visible dependency

Source-map native 5DA2F0 team, seed, match RNG and context writing and compare to the reconstructed GameState match calculation. Determine which original v38/v3c side effects and 533D80/5331C0 mode-specific presentations can be source-backed without fabricating an original match. Then join genuine primary+secondary 4A7210/6168C0 dated event callback producer, original saved 2–6-human state, and 432505 conditional management return. Original full game/physical Windows11 comparison and Gate13–17 audits remain OPEN. High-risk PR739 remains separate/unmerged.

This source finding is a recoverable investigation checkpoint under the user-approved milestone batching policy, not a stand-alone PR or release claim.


## First checked calculator dependency, original 5DA2F0 (not yet implemented)

Local canonical bounded disassembly `5DA2F0..5DA605` confirms:
- Incoming `ECX` is an actual original team-object pointer and stack argument `[EBP+8]` is native match context. At `5DA303`, it reads the context's `+0x28` virtual Side getter before using team objects.
- `5DA31A` invokes original `4037B0` on that team. If the result is false, native jumps to `5DA538` and reads **team+0x140,+0x13C,+0x138,+0x134**, converting the DWORDs to x87 floating-point variables with sign/range checks. These exact fields are source-required original calculation inputs, not inferable from completed score data.
- For true `4037B0`, the original first obtains team via `403850` and repeatedly reads team **+0x694/+0x6B0** (callee `618E00` and `65D920/65DA60/65D9B0`), and invokes `4290A0`, then computes x87 fdivr/fmul ratios. It eventually joins the alternative branch at `5DA5CF`. The different source branches cannot safely be treated as an identical single team-rating getter.
- `5DA5D9` starts a separate match+0x4C owner/pointer branch and may skip at `5DA5F9`. Not yet established how it writes final context scores; this requires continuing the callee source graph rather than inventing native RNG or player ratings.

**Next exact source slice:** analyze `4037B0,403850,4290A0,618E00,65D920,65DA60` callback types and 5DA5CF+ score writes, then map only validated source numeric inputs to the existing reconstructed `HumanGameplayController`. Original 5DA2F0 calculation equivalence, rounding/RNG, 533D80/5331C0 native modal lifecycles and original save state remain UNVERIFIED. Do not model their success as the result of calling modern `play_user_primary_match` alone.
