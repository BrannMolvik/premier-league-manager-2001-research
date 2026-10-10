# Recovery 456 — original normal NEXT/MATCH roster eligibility chain and live click-path omission

_10 October 2026 KST; strict AUDIT ONLY per research/CURRENT_STATE.md, continuing Recovery455. Do not modify Codex's implementation, licensed original assets, saves, CI, release, gates or other source code. No Windows11 original executable executed._

## Source checkpoint and original executable

- Live starting `main`: **`866e6b59de16c920cd4623d7b211fb26b4e2c1de`**, `codex/gate13-windows-playability-recovery`: **`0ae745d1b56f45cade460f03cd893849a2f53b45`** (unchanged). `research/CURRENT_STATE.md` and runtime state establish **audit_only**, **implementation_allowed=false**. Earliest incomplete Gate13; Gates14–17 and Windows11 release incomplete.
- Rehashed private original PE **`/mnt/data/fm2001_private/footballmanager.exe`**, 4,714,541 bytes, SHA-256 **`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`**; no binary/graphics/disassembly committed.
- Reproduce using GNU `objdump -d -M intel` ranges **`0x432190..0x432310`**, **`0x432310..0x43250A`**, **`0x43250A..0x432688`**, **`0x407FE0..0x40802B`**, **`0x407770..0x407895`**, **`0x407C00..0x407CD8`**, **`0x407350..0x4073F8`**, **`0x407CE0..0x407D80`**, **`0x651E20..0x651E26`**, **`0x432690..0x432707`**. Original vtable owner in PBg covered by Recoveries441–442.

## A. Source branch: ordinary native header control ID3 invokes 0x432190, not a date-only shortcut

Native **`PBg::0x432690`** reads the actual child control event object's ID at `+0x20`; **case ID3 `0x4326A4` pushes 0 and invokes `0x432190`**. Case ID1 separately creates `PEAMail` via `0x482BF0(0x65)`, and ID2 handles PMenu stack state.

Within `0x432190`, a source control-state adjustment at `0x4321D5..0x4321E1` calls native header control virtual+0x70 (its exact effects are not named); then current manager lookup `0x4139D0`, user schedule/selector `+0x5B4`, `0x4079D0`, and eligible event query `0x615D10` occur **before** any state transition. The query uses native global date `0x9847FC`. If an eligible candidate exists and a source comparison involving its `0x510A20` computed date succeeds, `0x432241..0x432280` considers match preparation. The exact upper comparison operand is a stack local altered by the preceding control call; the mere fact it uses a date comparison **does not prove** it equals only the visible header's caption date. Event polymorphism and original payload flags were audited Recoveries446–449.

**The native NEXT action is conditional**, may involve match preparation, results processing or other control-flow branches, and must not be implemented as `current_date += 1`, `show_report`, or `rotate_manager` unconditionally.

## B. Exact eligibility subchain 0x407FE0, with 11-player count tested inside first gate

Native **`0x407FE0`** is called from source **`0x432270`** with contextual event-derived payload or null, and is **a conjunction of four ordered tests** on original source list/roster owner `ECX` (`0x407FE0` preserves it in ESI):

| Step | Exact original instruction/call | Source contract and stop condition |
| --- | --- | --- |
| 1 | `0x407FE3 push 1; 0x407FE5 call 0x407770` | `0x407770` result must be nonzero or `0x407FEE` returns false |
| 2 | `0x407FF4 push 0; 0x407FF8 call 0x407C00` | `0x407C00` result must be nonzero or `0x408001` returns false |
| 3 | `0x408007..0x40800E` pushes caller's event/competition argument and invokes `0x407350` | Must return nonzero or `0x408017` returns false |
| 4 | `0x40801B..0x408027` invokes `0x407CE0` | Returns **true iff `0x407CE0` result != 0** |

**First subgate `0x407770` explicitly inspects roster-owner `+0x294` count against **`0x0B=11`** at `0x40777B..0x407784`. If count is below 11 it takes **a separate path `0x407846`**; it does **not** universally return false from that single compare. If count is >=11 and caller argument1 is nonzero, it additionally invokes `0x403640`, performs a source comparison of a record's first byte to `0x21`, uses source `0x407EC0`, `0x407220` or default count11, and requires `0x406BE0(...)` to return 1 with a further count/availability comparison before returning true. The caller argument0 path checks source player-record eligibility `0x4EA300` against global bound `0x874B64`, with its own early-fail rules. These are original roster/eligibility checks; they should **not** be glossed as “always at least 11 healthy starters” or a single field.

**Second subgate `0x407C00`** is also roster-sensitive. It compares original `0x407060(5,0)` to `0x407220(5,source 0x407EC0)` at `0x407C1D..0x407C2F`, then iterates selected source player indexes from the owner's **`+0x244`** array, resolves source player record table `0x875640`, calls `0x41FAB0` with literal source argument5/-1/current club and further `0x418050` predicate, comparing native `0x408500` result to a prior computed count. Exact meaning of all integer subcategories remains unknown; the source uses more than “11 selected”.

**Third and fourth subgates** invoke further club/player and source-ref lookups (`0x407350` iterates the same roster IDs, `0x417F50`, `0x418050` etc.; `0x407CE0` uses `0x41B490` and `0x41FAB0` with source params4/5). Do not invent user-facing validation popup captions or classify these flags without their producers.

**Source branch asymmetry matters:** in `0x432275..0x432280` the caller **inverts** `0x407FE0` return, stores the inverted result into a local byte, and performs an additional original global **`0x875680`** predicate before entering the conditional `0x404A80→0x404A70→0x409C90→0x405A20` path. A false “eligibility” result is not synonymous with instant match launch, match loss, or return to main; it triggers source-specific following logic. Values named here are source addresses, not speculation about the playable event.

## C. Small but important constant-source closure: 0x651E20 is always 1

The direct original **`0x43220E call 0x651E20`** is a separate getter/check in the NEXT body. `0x651E20` consists of **`mov eax,1; ret`** (original bytes `B8 01 00 00 00 C3`). Thus `0x432219` always stores 1 in its local from that call in this shipped build. The `0x4322F1..0x432306` branch checking that value against zero **does not derive a runtime 'no fixture' state in this exact executable**. Other byte flags and source queries still vary; don't claim the entire NEXT body is unconditional or infer dead paths not covered by this exact call.

This qualifies Recovery442's broad treatment of `0x4322ED..0x432340` as generic “returned pointer/byte flags”: the `0x651E20` return is **constant**, whereas the roster-validity local (and earlier eligible event lookup) remains variable. It is an important fail-closed constraint for clean implementation and test design.

## D. Concrete source outcomes and multi-manager context preserved

Prior Recoveries442/445 already prove, and original `0x4324FE..0x432688` re-disassembly reconfirms:
- guarded **`0x431F70` original PResults processing** at `0x4324FE`, not every normal NEXT press;
- calendar/UI date recomputation `0x64CCD0→0x64CE30` at `0x432505..0x432522`;
- conditional **`PStartMenu::0x4C3280`** after predicates including original human manager count **`0x8755E4<=1`** at `0x4325DF`;
- distinct multi-manager state case `0x43261F..0x432639` rotates **selected user/manager index `0x8755D4=(index+1)%0x8755E4`**, *not* current game date, then reconstructs management shell `0x4C2FB0`.

Do not restart the previous calendar/PResults/event-classes audits; these remain exact source findings with unknown Windows GUI acceptance.

## D2. Second independently verified roster gate: native 0x407F40 and guarded forced Squad return

This source path is **different from `0x407FE0`** above. The original `0x43245F..0x4324FC` branch explicitly fetches the current manager `0x4139D0`, gets that user's `+0x5B4` roster/selector, invokes **`0x407F40`**, and then conditionally performs a source modal and **Squad-screen** transition.

Original `0x407F40` performs an **effective eleven-entry threshold**, not merely the raw roster count gate in `0x407770`:

1. Iterates `roster_owner+0x294` entries selected by 16-bit player IDs in the array beginning `roster_owner+0x244`; resolves original player records from global **`0x875640`** using original **0x250-byte per-record stride** (the disassembly computes `((37 * id) << 4)=592=0x250`).
2. Calls player method **`0x418050`** with original roster-owner `+0x04` and `0x407EC0` context, and increments a tally only when that callback returns **false** (see `0x407F88..0x407F95`). What the original callback's football meaning is remains UNKNOWN.
3. Obtains **`0x407060(11,0)`**, calls **`0x407DF0`**, calculates **`max(0, result_of_407060 - result_of_407DF0)`**, **subtracts this quantity** from the earlier tally, and returns true iff the adjusted tally is **at least 11** (`0x407FBB..0x407FD7`).
4. Therefore **`0x407F40` is NOT equivalent to `roster_owner+0x294 >= 11`**, and also is not equivalent to the earlier composite readiness `0x407FE0`. It is an independently source-defined *adjusted eligible-player tally*. Avoid naming player exclusion flags beyond their own producer evidence.

**What the original NEXT function does with it:** at **`0x43246F`**, if `0x407F40` returns nonzero, it builds original roster feedback text via **`0x407410`**, invokes native modal/choice via **`0x668995`**. If that modal returns **zero**, the code calls **`0x482BF0(0xCE)`** to construct the original **Squad** panel and **`0x5ED2A0`** to push it, and calls **`user::0x42C6C0(2)`** before common date/UI post-processing. If the modal returns **nonzero**, it bypasses that Squad construction (source branch `0x4324B7→0x432505`). If `0x407F40` itself returns zero, it skips the modal/Squad subpath and reaches the user state2 setter via `0x4324E9`. Exact prompted text, accepted choice semantics and all input states are **UNKNOWN**. It would be wrong to read `0x407F40` result alone as a universal match-failure / success or to unconditionally open Squad on every NEXT click.

**Concrete Codex regression cases:** verify `0x407FE0` roster readiness separately from the later `0x407F40` adjusted tally; create source-backed fixtures for adjusted count below/equal/above11, a modal accepted/refused path, a route back to native Squad, and a route continuing without Squad — all after an *actual NEXT ID3 pointer event* and within original selected-manager context. Exact source behavior and Windows11 receipts are not already implemented by the existence of an isolated match simulator.

## E. Verified main/Codex normal-click comparison and Codex-only handoff

Both branches include a `reconstruction/original_management_next.py` source-backed bitmap/caption and hit helper `native_next_at_point(x,y)` for native rect **(700,0,100,95)**. Latest Codex host **`reconstruction/original_game_host.py` blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`** uses `native_next_at_point` in its **`on_fixtures_pager_motion` hover** and changes `management_next_flags`. But its actual ordinary **`on_click`** block (**around lines2320–2420**) recognizes PMenu opener, Squad row, Fixtures pager, PMenu tree and Fixtures grid, **with no NEXT/MATCH hit-to-action dispatch**; if no PMenu row or fixture grid it sets a status string and returns. The main host also has no NEXT action in its management `on_click`.

**Exact missing P0 functionality:** even when original art, match dates and backend scheduling are correctly drawn, an actual ordinary mouse click on the native NEXT/MATCH rectangle does **not invoke gameplay advancement** in either version. This is independently verified from host control flow and does not depend on guessing what the NEXT button should do after accepted click. Native `PBg::0x432690` has a concrete ID3 action calling `0x432190`.

**Codex-only handoff / acceptance:**
1. Add actual *source-accepted* native NEXT ID3 click dispatch without bypassing modal PMenu state, normal source flags, per-manager current user or already modeled fixture/event filters; do not turn mouse hover into state mutation.
2. Preserve ordered eligibility `0x407FE0` gates and source fallback, rather than making a generic one-day progression or a universal pre-match 11-starter modal.
3. Exercise at least **(a)** current manager has no qualifying immediate fixture; **(b)** current manager has an eligible match with source roster gates; **(c)** roster gate fails; **(d)** two human managers with different next eligible events; **(e)** return from source PResults and reenter current PMenu/Squad; **(f)** serialized manager/date after save and reloading.
4. Test **normal pointer input and on-screen match readiness** at both Southport and an unrelated original club on Windows11, not only direct calls to a gameplay controller. Original match-watch/3D visual presentation is still separately incomplete under Gate14 and must not be claimed done.

## F. Subsequent source-backed cross-branch contrast: Codex already owns a bounded backend NEXT, but cannot reach it from the game

This audit checked actual newest code, rather than inferring that the match engine is unimplemented from the visible unresponsive button.

| Exact checked artifact | Main | Latest Codex implementation branch | Audit outcome |
| --- | --- | --- | --- |
| `reconstruction/original_management_advance.py` | **Not present** as standalone module at main | Blob `6343fe0a23112d32d8023243b0e9a7b83d2eaf9b`, `original_management_advance_target(...)` | Codex **already has** fail-closed source-bounded turn target arithmetic, requiring `selector_source_qualified=True`; do not recreate it without reason |
| `reconstruction/human_gameplay.py` | Blob `682056ed0667bce69025bea38a71045c7293495a`, prototype `advance_to_next_user_fixture`, no native bounded turn method | Blob `980f9af731ae2aa5ee2ed14694c8b60fb22c37d7`, **`HumanGameplayController.advance_original_management_turn` at ~line1571** | Codex has a structured **non-UI** calendar processing method, with original native source gap documentation |
| `reconstruction/original_game_host.py` | Blob `76820796c9bbf4a51b6972fd9f88099b734c1a91`, no normal NEXT press dispatch | Blob `14c4436d600aa2a397779d6fe22cdc74b742bf26`, hover `native_next_at_point` around lines1765–1767, **no caller of `advance_original_management_turn`** | Confirmed missing **UI→source state→backend integration**, not proof no match engine exists |
| `reconstruction/original_management_presenter.py` | Blob `2c23adf12a3378a53793e5a8036d3dc950034dad` | Blob `8cee4bca0686475b4b0a41922b9600afe70879ed` | Neither exposes `advance_original_management_turn`, `original_management_advance_target` or the NEXT user action |

**Codex existing method's explicit constraints** (read from actual source): `advance_original_management_turn(next_match_date,selector_source_qualified,container_end_date,turn_length)` rejects absent human user and unqualified native selector; refuses a calendar's annual-end transition instead of inventing one; preserves source bounded turn date, processes each day through shared `_process_current_primary_day(native_primary_order=True)`, invalidates unmodeled wrapper-links, stops at pending human fixture, and checks the current roster only when the source next human fixture is tomorrow. The last behavior is a current Codex *implementation assumption* justified in its docstring, not proof that every source `0x407FE0` return and dialog path is already reproduced.

**Precise implementation consequence:** **do not ask Codex to build the match simulation from scratch or copy the source target helper onto `main` now.** The immediate actionable integration task is to source-qualify the retained original selector/candidate, preserve window/modals and manager context, dispatch the native **PBg ID3** accepted `on_click` to the *existing* Codex controller entry point, then implement missing source branches and visual destinations. Reject an unqualified selector and leave unknown game states fail closed. A direct call to the controller in a backend test does not validate the ordinary Windows game.

**Verification boundary:** This is an exact code-level coverage assessment against the named current branch blobs. It does not assert the backend has full original multi-manager progression, EAMail event dispatch, graphical match watch, original saves or Win11 playable parity. The source native roster gates audited above remain partially unmapped.

**Audited status**: EXACT source call chains, roster count branch, 0x651E20 constant, original manager switching and host missing input; PARTIAL original field semantics and dynamic consequences; UNKNOWN native Win11 GUI behavior and game parity. No implementation, CI, binary build, original game runtime or gate closure by this audit worker. **Gate13 OPEN; Gates14–17/full verified Windows11 release INCOMPLETE.**
