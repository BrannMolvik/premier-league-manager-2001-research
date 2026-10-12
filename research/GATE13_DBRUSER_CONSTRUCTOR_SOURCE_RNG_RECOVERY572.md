# Recovery572 — bounded DBRUser constructor before first human RNG

**13 October 2026 KST.** Gate13–17 remain OPEN. The source for this finding is the privately authorized original `footballmanager.exe` (4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`). The EXE was **not launched**, and source code/assembly or any original binary bytes are not committed. Original text disassembly reconstructed privately from GNU objdump, 31 exact original instruction sites and 4 strict callsite-range scans independently **PASSED**.

## Precise source ordering

First TeamSelect selected club goes through `0x413C0E` → `DBRUser::0x424CA0` **before** `0x413C54` → `0x4258D0` → `0x4258F8` → `0x42C400` (original 13 stored name pairs). The original DBRUser C++ constructor is **not** empty: it allocates several native owned arrays and initializes many native owner records before first name pair is chosen.

Within constructor `0x424CA0..0x424F6B`, three exact source bulk initializer sites all invoke the same C++ array construction runtime helper `0x6687C1`:

- `0x424D39` pushes callback **`0x424F70`**, `0x424D3E` pushes count **4**, `0x424D4E` calls the array helper.
- `0x424E6D` pushes callback **`0x424F90`**, `0x424E74` pushes count **`0xC8` (200)**, `0x424E7A` calls the array helper.
- `0x424EDC` pushes callback **`0x61E480`**, `0x424EE1` pushes count **`0x100` (256)**, `0x424EE9` calls the array helper.

### Nested callbacks narrowed

**200-owner callback** `0x424F90` does scalar initialization and calls `0x4EAB80` at `0x424FAE`. `0x4EAB80..0x4EAC38` has exactly four direct call sites: `0x4EB2A0` once (fixed local zero initialization) and `0x64CE30` three times. `0x64CE30..0x64CF05` calls only `0x66A518`, a signed integer DIV/quotient helper whose native `idiv` occurs at `0x66A51F`; it does not call the original shared CRT RNG. These bounded nested functions explain the 200 owner record initializations without inserting a random draw for each record.

**256-owner callback** `0x61E480` allocates an embedded object, invokes `0x4EAB80` at `0x61E4DF`, and calls `0x61E540` with a literal **`0xFFFF`** argument. That subroutine first executes `0x61E7A0`, which tail-jumps to `0x4EAB80`; then source `0x61E54D` compares the provided word to `0xFFFF` and `0x61E552` branches to `0x61E5A0` early, bypassing the ordinary full non-sentinel club/player association path for **this constructor callsite**. `0x5EE970` (at `0x424EA7`) and `0x42C6B0` (at `0x424F45`) have **no direct native call instructions** in their verified tiny bounded bodies.

**Scope limitation:** These findings rule out extra *direct* CRT calls in the enumerated nested initialization/formatting functions on the specified successful path. They do **not** prove the entire constructor globally RNG-free, because other original allocation helpers/indirect callbacks, CRT seed-to-click and actual runtime object states remain to be accounted for. Never insert or subtract 200/256 RNG calls as a guessed hidden-state adjustment, never mark the historic initial-name RNG checkpoint settled.

## Test and implementation boundary

The existing `reconstruction/original_supportstart_teamselect_user_birth.py` correctly retains its **test-only** explicit missing-queue-and-binder acknowledgement. This finding does not weaken that guard. The subsequent two original global queue drains `0x4259B5` and `0x412F1F`, manager binding `0x413C5B`, first click seed-to-CRT and all subsequent per-staff dynamic draws are still unresolved in live GameState. No original GUI event was executed, no Windows11 interactive fidelity acceptance performed. A persistent 31-instruction, four-call-range audit was added to `research/audit_original_teamselect_continue_static.py` and can be rerun only against the authorized private original executable. The meaningful next step is to enumerate the remaining non-leaf ctor/queue producers by **source reachability** and qualify actual original queue head state at each drain, not assume it empty.


## Recovery572 two distinct original queue-empty snapshots (source-only preflight)

Original `0x4259B5` and `0x412F1F` invoke the SAME global `0x947AA8` event owner through `0x614080`, but these are two **different moments** in the native selected-human startup. Original `0x613E40` sets the head null at construction; `0x614097..0x61409C` has a zero-head return with no vft+4/18 calls. A null head at owner creation cannot be projected unobserved through either later queue drain, particularly because `0x4258D0` performs many calls between the two sites. Added fail-closed `preflight_original_first_human_two_empty_queue_drains` requiring independent original native snapshot witnesses with owner identity, exact sites, enabled1, no processing, zero nodes and no outstanding deferred flag. It returns a narrow zero-event-callback result **only for those independently supplied conditions**, with `live_teamselect_startup_authorized=False` regardless of inputs. A Python boolean claiming runtime observation is an external precondition, not actual observation of the original process; this session did **not** execute the original EXE or obtain genuine runtime queue snapshots.

One focused test method (many positive and negative subcases) covers both native queue locations, nonempty second queue, reentrancy, stale deferred owner, wrong addresses and unobserved state. This cannot be used to bypass the separate shared-CRT first-user constructor/manager binder integration guard; source/full branch tests and Windows11 GUI acceptance still pending. Gates13–17 OPEN.


## Recovery572 first-human binder branch0 narrowed

The original first-manager binder `0x426090` has a documented conditional call at `0x4261B3` to `0x415870`; the actual callsite **pushes literal zero** at `0x4261A9`. Native `0x415877` compares the event argument to 1, and `0x41587C` branches straight to `0x4158C3` for literal 0. Therefore the larger direct `0x405CF0` at `0x4158A5` and `0x50FFC0` at `0x4158BE` are **not** reached by this specific first-human binder invocation. The entire 0x4158C3..0x415927 literal-zero suffix has **zero direct CALL instructions**; it still writes original club-ref, manager indices/counters and other fields. In the same binder, `0x403E10..0x403E3D` resolves an existing original club ID with no direct CALL, while `0x4151C0..0x415209` accesses registered human users only via `0x413B10` (one direct call), and `0x413B10..0x413B36` is a no-call linked-list index lookup. This is a **bounded exclusion of particular direct CRT consumers**, not proof the actual binder performs no unrelated side effects or that the original user/club pointer state is qualified. `0x426090` still allocates/frees memory and mutates original manager assignments.

Checked **12 exact original x86 instruction sites and four direct-call interval inventories** independently on the SHA-pinned private original. All PASSED without launching the original executable. The original prior Recovery558 binder note already identified the event0 distinction; this verification extends its precise no-direct-call audit to the registered-user list lookup and the literal-zero suffix. Persistent static audit extended here. The two global queue heads, pre-first-click CRT seed and normal staff/GUI remain unresolved, Gates13–17 OPEN.
