# Recovery610: original 0x513659 v38 bit2 tail, reached-only callbacks

**14 October 2026 KST.** Baseline main `f3ef01b854946585aeb5beb90c261848b910609f` after exact-head green PR705 (Gate13 1,549 tests/127 expected skips, asset policy success); original private `footballmanager.exe` 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. **Static disassembly only.**

## Direct original source proof

`0x513570` after source-linked event primary/secondary scoring arrives at `0x513659` **only if either original context DWORD +D0C or +D10 is nonzero**. It checks `match+0x44` bit2. If unset returns without downstream virtual getters or RNG.

If bit2 set:
1. `0x51365F` calls `0x513F00` and `0x51366A` calls `0x513ED0`. The returned EAX DWORDs are compared at `0x51366F`. If unequal return, skipping all later operations. `0x513F00` calls optional linked `match+0x54` virtual+0x48 and self virtual+0x4C, summing returned integers modulo32. `0x513ED0` calls optional linked virtual+0x4C and self virtual+0x48, summing modulo32. Their *virtual getters may have side effects*, so no reconstruction may invent those source return values from simplified team IDs.
2. When the original context DWORD +D14 is **nonzero**, the source dereferences native linked match+54 (must be nonnull), invokes its virtual+0x4C, invokes self virtual+0x4C, compares the reached EAX values, and returns if unequal. When +D14 zero, none of these optional calls occur. This optional condition is **independent of the earlier +D0C/+D10 gate**.
3. If all required equalities passed, source `0x513697` calls original `0x64D540(2)` once. The actual return is tested for nonzero: if nonzero source increments **BYTE match+5A**, otherwise increments **BYTE match+5B**, with normal 8-bit wrap; no further score WORD subtraction. Original `0x64D540` itself invokes original RNG `0x66951C` and floating scaling; its *actual reached return and RNG state* have not been reconstructed.

## Strict safe projection

`reconstruction/original_native_v38_bit2_reached_tail.py` consumes the prior typed pure original v38 score-stage receipt and matching supplied original context. It requires **actual reached** `0x513F00` and `0x513ED0` EAX results, optionally actual linked/self v+0x4C results only on the reached +D14 path, and actual `0x64D540(2)` EAX only if the RNG call was reached. Missing, mistyped, inconsistent or gratuitous callback results fail closed. All unsupported paths remain source-unqualified rather than inventing original virtual getters. This module **does not call original functions, advance RNG, mutate the live game world, or prove native match/gameplay completion**. Tests cover all short circuits, both RNG outcomes, linked owner presence and equality, skip-only extra arguments, null pointer, wrong original context and wrapped flag gate.

**NEXT:** exact-head Gate13 source CI, privacy asset policy and independent PR review before merge. Then verify source return and original virtual+48/+4C native vtable implementations plus original `0x66951C` RNG and real match-event allocation, fold these source callbacks into the original v38→v3C match-process transaction, reconstruct `0x511370/0x5127A0` rescheduler, and genuine 0/1/2 match-mode presentation and native PResults/management return. Gates 13–17 OPEN. No Windows11 GUI acceptance.
