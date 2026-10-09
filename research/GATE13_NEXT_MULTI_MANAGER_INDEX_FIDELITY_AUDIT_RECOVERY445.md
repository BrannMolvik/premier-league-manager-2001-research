# Recovery 445 — original NEXT/PResults multi-manager selection, scheduling and index restoration

_9 October 2026 KST. Continued high-priority Gate-13 original-core-game audit under `research/CURRENT_STATE.md`. **AUDIT ONLY**; Codex owns implementation. Latest source audit starts at main `deac39e271d8b9b2c935b8553617cc797c9773d2`, implementation reference `codex/gate13-windows-playability-recovery` at `8702eded049643220bf4b590d8d45c2197cfd42a`._

## Provenance, exact source identity

The authorized original `footballmanager.exe` in the private workspace is 4,714,541 bytes and was **SHA-256 reverified** in this recovery as:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

The source statements below are from independent bounded `objdump -d -M intel` disassembly against that hash. Reproduction targets are `0x4139D0..0x4139DD`, `0x413B10..0x413B35`, `0x413C4F..0x413C83`, `0x431F70..0x431FCB`, `0x43215E..0x43218D`, `0x43261F..0x43267D` and `0x4A83F0..0x4A8520`. Original raw PE/data remain outside Git; no original game process was run.

## A. Critical field correction: `0x8755D4/0x8755E4` are player-manager selection/count, NOT calendar position/count

**Original manager container base address:** `0x874C10`. The observed absolute data addresses have these exact source-relative offsets:

| Source address | Containing owner offset | Independently observed producer/consumer | Classification |
| --- | --- | --- | --- |
| **`0x8755D4`** | **`+0x9C4`** | `0x4139D0` reads this as list index and passes it to indexed user getter `0x413B10`; `0x413C6A` writes new user index | **EXACT current selected manager/user index** |
| `0x8755DC` | `+0x9CC` | `0x413B10` starts an original singly linked user list, walks by node `+0x04` until index and returns node `+0x00` actual user | **EXACT linked user collection head** |
| **`0x8755E4`** | **`+0x9D4`** | `0x413C60` reads current size; `0x413C70..0x413C71` increments size after user creation; `0x4138C9` resets it to zero on container reset | **EXACT registered manager/user count** |

At `0x413C4F..0x413C71`, the original new-user creation flow first binds the user to the selected club/state (`0x4258D0`, `0x426090`), writes **old count to selected user index `+0x9C4`**, then increments count `+0x9D4`. This is not a date/round progression structure. The manager getter `0x4139D0` and indexed traversal `0x413B10` form the decisive original producer-consumer proof.

**Historical correction:** Recovery442/444 intentionally retained the neutral symbols `0x8755D4` and `0x8755E4`; any shorthand characterizing the expression `(0x8755D4+1)%0x8755E4` as a calendar-position or round modulo is now **WRONG**. The original is **`(selected_manager_index+1) modulo manager_count`**, with guard/active-state conditions at `0x43261F`. Game-date value remains the distinct global **`0x9847FC`**.

## B. NEXT original source conditional user rotation

At `PBg::0x432190` continuation **`0x43261F..0x432639`**:

- Tests original local source state **equals 2**, not an unconditional operation on every press;
- increments current selected manager index `0x8755D4`, runs **signed `idiv`** by `0x8755E4` (manager count), and writes signed remainder back into selected manager index;
- checks/destroys prior PMenu owner/panel stack as needed and calls **`0x4C2FB0`** at `0x432675` to reconstruct management after this state-specific rotation.

The clean model must retain the index and source-state guard before switching manager/club context, and **must not** interpret the modulo as incrementing time. The whole other original NEXT branching family, including match processing, PResults, direct Squad, and PStartMenu, remains condition-dependent.

## C. Original PResults scans all registered managers, then restores the prior selection

**Explicit source-state preservation across simulated work:**

- `PResults` outer routine `0x431F70` saves **original `0x8755D4` selected index** into stack slot `[esp+0x0C]` at `0x431FB5..0x431FC7`, before starting the PResults simulation pass;
- at `0x4A83F0`, `PResults+0x64` processed count is zeroed, and **selected manager index `0x8755D4=0`** is reset at `0x4A8435`;
- inside `0x4A843B..0x4A8488`, `0x4139D0` retrieves the *currently indexed manager/user* via the real container list, uses that user's `+0x5B4` source schedule owner to query candidates via `0x615D10`, then chooses one candidate based on a source dword `candidate+0x10`: if two candidates are present, **the lower `+0x10` value wins** (`0x4A8467..0x4A8471`). After each indexed user query, it computes **`(index+1) % manager_count`**, writing the remainder back to `0x8755D4` until it reaches 0;
- if a candidate is chosen, `0x510A20` derives a source value used to bound the date horizon; if no candidate exists the routine uses `0x616A30` fallback. That value is further limited by `current_date (0x9847FC) + 0x87753C` before original event simulation `0x4A83D0` runs across the bounded date interval. The precise meaning of `candidate+0x10`, the competing candidate classes, `0x87753C` and the user-facing time-range policy remain **UNKNOWN**.
- after `0x431F70` finishes its progress processing and source per-manager follow-up work, **`0x432171..0x43217B` restores the saved selected-user index into `0x8755D4`**, then returns to NEXT caller `0x432505`. Thus a normal results pass does **not** permanently switch the player's current manager merely because simulation checked all managers.

This directly qualifies earlier partial descriptions: `0x8755D4` is not an independent date cursor, a match simulation loop counter or a calendar-position field. It is the same source manager-selection field read by normal current-user helper `0x4139D0`, temporarily rotated during multi-user event processing and restored afterward. Conversely, the *separate guarded NEXT branch* at `0x43261F` intentionally changes current manager index for PMenu reentry.

**Classification: EXACT** at native address/instruction and linked user-record identity; **PARTIAL/UNKNOWN** for calendar candidate `+0x10` semantic label, specific match/gameplay branch predicates, direct PResults `+0x10 -> 0x4A87E0` event producer, original visual/input timing and full Windows acceptance.

## D. Original PResults callback remains source-unresolved, negative result respected

An exhaustive **raw `CALL rel32` scan** of `.text` found **no direct `CALL 0x4A87E0`**. The only 4-byte absolute literal pointer to `0x4A87E0` in the canonical PE is its original vtable slot. This supports *virtual dispatch* as the likely caller class but **does not establish which runtime event, if any, reaches it**. Specifically, the shared `waiting_back_2.444` image at PResults `+0x16C` is registered with native control ID0, and native `0x64F7A0` skips parent-action dispatch for control ID0 (Recovery443). There is **still no proof** of a click-to-close control. Do not substitute a guessed bottom-strip click in production.

## E. Current clean-room mismatch and minimum Codex implementation handoff

Main and current Codex still do not integrate the original native-look NEXT control's accepted press → real `0x432190`-equivalent game-state pathway, real `PResults` owner, or ordinary PResults → conditional main/menu transitions. Codex has source art, caption and hover but not end-to-end native gameplay activation. A developer-only simulation control is not an equivalent original NEXT route.

**Priority for implementation owner (Codex; no code implementation by this audit worker):** model original **selected manager index and manager count as independent of calendar time**, source-qualify the `0x43261F` manager-switch branch; preserve and restore selected manager context around `PResults` event processing; select earliest eligible source candidate among all registered managers, retaining original compare rule and the bounded time/date horizon after independent semantic typing; integrate real normal management NEXT → native PResults → conditional Squad/PMenu/PStartMenu return. Regression tests should cover at least **two managers/clubs with different source-schedule candidate ordering and a subsequent saved/loaded active-manager selection**, not Southport only. Existing original bitmap zero-ID gate must remain respected.

No native process launch, Windows 11 UI acceptance, game code, Codex branch, assets, saves, CI, merge or gate closure. Gate 13 remains OPEN, Gates 14–17 and full original-country Windows 11 release INCOMPLETE.
