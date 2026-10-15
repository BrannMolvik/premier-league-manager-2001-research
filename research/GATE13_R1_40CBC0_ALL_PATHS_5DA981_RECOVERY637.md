# Gate 13 R1 Recovery637: complete original 40CBC0 eight-branch QWORD coefficient and 5DA981 source gate

Canonical original private `footballmanager.exe` is 4,714,541 bytes SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Only static x86 disassembly/raw-byte validation; original executable never run and never committed to GitHub. Base main after verified/merged PR #746: `d48008e519f860fdc1aca6ba9205bfc74d936197`, exact-head Gate13 CI `38657210985` 1,983 tests/169 expected skips and asset `38657211008` both PASS. Gate13–17 **OPEN**.

## Exact original eight jump-target source state and fallthrough

Original `0x40CBC0` uses first-side club+0x14 selector and original 50-byte/8-DWORD jump tables previously recovered in PR #746. The key source trap is that **only two exceptional cases return directly after a category-dependent QWORD pair**; all other source exceptional jumps fall through into later case routines, overwriting prior QWORD writes. A conventional `switch` that assumes each jump target is independent will produce different original match numbers.

| Native case target / club+14 | Original category calls if reached | Stores and final result |
|---|---:|---|
| `0x40CBF2` /26 | 1 | category0..4: first=[30,20,16,12,9]; second=first*0.75, then RET. Outside0..4 both QWORDs untouched |
| `0x40CCC9` /33 | 1 | category0..2: first=[20,15,10]; second=first*0.75, then RET. Category3,4,>4 **no-write**, then return |
| `0x40CD5D` /40 | 6 | optional category0/1 store [25,17], fallthrough CDB3→CE09→CE83→CEDA→CF31 |
| `0x40CDB3` /73 | 5 | optional category0/1 store [16,12], fallthrough CE09→CE83→CEDA→CF31 |
| `0x40CE09` /66 | 4 | category0..4 store [20,16,12,9,9], fallthrough CE83→CEDA→CF31 |
| `0x40CE83` /24 | 3 | optional category0/1 store [15,10], fallthrough CEDA→CF31 |
| `0x40CEDA` /31 | 2 | optional category0/1 store [17,12], fallthrough CF31 |
| `0x40CF31` /default | 1 | category0..4: final first=[15,10,8,6,4.5]; second=first*0.75; category unsigned>4 **no-write** |

Intermediate case `0x40CE09` uses the original five-DWORD jump table at `0x40D008` targets `[0x40CE37,0x40CE44,0x40CE56,0x40CE69,0x40CE69]`, so category3 AND category4 both write the same intermediate source constant 9. For all paths that fall through to CF31, the final category0..4 writes **replace** previous source QWORD outputs with the default five coefficients, though the intermediate source writes still matter as original instruction effects. Every intermediate store copies original exact source QWORD doubles or x87 `FMUL 0.75` from `0x7BD558`. Original private constants `0x822040–0x822170`, original eight-branch write instruction sites and case jump table independently checked. All source values are integers or exact binary halves; products 0.5 and 0.75 are exactly representable, so these **particular numeric results** do not require inventing the original x87 control-word semantics.

New `original_native_40cbc0_all_paths.py` projects source branch entry, **every ordered intermediate QWORD store**, actual final first and second QWORD bytes and true no-write paths from a source-qualified original club→4056D0→4F3B10→4FA510→4FA520 category receipt (merged PR746). For every native 4FA520 reached during fallthrough, callers **must provide the same independently observed original native category** as the first; missing/changed values fail closed instead of presuming that repeated query calls read immutable state. No 40CBC0/native 4FA520 or actual GameState execution is claimed. New `test_original_native_40cbc0_all_paths.py` tests 8 ×6 category/outside cases, exact category call counts and intermediate source store order, native QWORD bytes, unmatched/no-write, forged category drift, invalid output owners and independently original PE opcode sites.

## First player-match integration boundary: original 5DA967 output-owner stack and 5DA981 zero guard

The source at `0x5DA8D9` takes a pointer to pre-push stack `[ESP+0x98]`, at `0x5DA8E0` a pointer to pre-push `[ESP+0x90]`, pushes the two pointers (first `ECX`, then `EDX`) and sets `ECX=ESI` at `0x5DA8E9`. Thus **at the actual call site** `0x5DA967`, first `40CBC0` output pointer `EBP+8` is `ESP+0x98`, and second `EBP+0xC` is `ESP+0xA0`; the selected club in native ESI/40CBC0 ECX must be the **same original first-side owner**, not the match processing object or current human. Original four DWORD zeros at `0x5DA93B/946/951/95C` initialize those two QWORD output slots to +0.0. After `0x5DA967`, original `0x5DA96C` reads the **second** output `[ESP+0xA0]`; `0x5DA973` FCOMP against original `0x7BD5F8 = 0.0`; and `0x5DA981` branches to `0x5DAC05` when equal (x87 C3 zero flag in AH bit0x40).

New `original_native_5da967_coeff_guard.py` source-joins verified first-side club owner, entire original 40CBC0 source coefficient result, both exact source stack addresses, both source zero-initialized QWORDs, and the resulting **no-write/zero vs nonzero** comparison branch. All eight dispatches category0..4 produce positive second QWORD except category3/4 in case33, which writes **nothing**, leaving original zero and taking the skip. Any category >4 likewise no-writes and takes 5DAC05. For nonzero branch, later genuine 5DA2F0 player/roster/event scoring is still missing. It reports true source instruction effects, not an original-runtime execution.

### Remaining implementation and audit

None of this establishes real native 5DA2F0 gameplay or the later private original player accumulators/RNG/injury source state. Original 5DA981 branch outcomes and QWORD values are now source-projected for exact inputs, but actual original manager/club memory, roster getters, score and event pipeline are not connected to live GameState. The original `5DA967→5DAC05` alternate path and `5DA981→5DA987` normal scoring branches require source-joined player state/callbacks; then v38/v3c and original PPreMatch modes0–3, PResults, management return and Save/Load. All original selectable leagues/countries, 1–6 human managers and genuine Windows 11 physical GUI installer/whole-career Gate13–17 acceptance remain pending. High-risk PR #739 is still unmerged pending independent GameState/schema48 and native event future-identity review.

**Work status:** WIP feature branch `worker/gate13-r1-40cbc0-all-paths-637`, source and regressions persisted. No PR or hosted CI for this NEW all-path segment until a coherent review/audit; original private binary stays outside repository. Do not mark Gate13 or Gate17 complete from these source tests.
