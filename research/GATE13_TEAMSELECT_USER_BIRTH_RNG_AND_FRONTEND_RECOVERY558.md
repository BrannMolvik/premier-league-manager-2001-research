# Recovery558: original TeamSelect performs immediate user birth before Continue

**Active scope:** Gate13 PStartMenu -> TeamSelect selected first/next human -> native DBRUser initialization -> six original staff -> seven-row PSupportStart modal -> Apply/Cancel -> TeamSelect -> Continue -> competitions. **Original source**, not the incomplete reconstruction, defines the player journey.

**Source identification:** private authorized original footballmanager.exe (4,714,541 bytes) independently SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Original Master.dat (3391446, SHA `183dd457d09ce616f99a664636727668ec15eab3f65b9057ef0953e76548b6b8`), Static.dat (86929, SHA `e0ff7c10a5f5f973a87cf6cd2d3770e623071899a0b30378debd0e7d13edb9d8`), Core.str (351695, SHA `b0800475769fa087e69de989388569e5b29f495e5abe5d62687c2acb1d339e06`) verified. The original process was never launched. This is static source proof, NOT original GUI observation or Windows11 acceptance.

## 1. The original click performs actual user construction immediately

Native selected-club event `0x4D8E90`, on new human branch, invokes:
1. `0x4D8EF3 -> 0x413BB0` original user registration, not a deferred club-ID-only toggle.
2. `0x413C54 -> 0x4258D0` attaches selected user club at `DBRUser+0x5B4` and **unconditionally** calls `0x42C400` at `0x4258F8`, before staff creation.
3. `0x4D8F29..0x4D8F4E` clears original selected human staff-list anchors.
4. `0x4D8F75 -> 0x4C9CD0` calls six native `0x4C9B30` constructors in exact type order 1,2,3,4,5,13.
5. `0x4D8F7F -> 0x4DA4F0` transfers actual initialized staff pointers to seven selector records. Later original TeamSelect `0x4D91C0 -> 0x450BB0` opens original PSupportStart.
6. PSupportStart Cancel(0) and Apply(1) have different native state effects; verify return and rollback before adopting UI hit/commit behavior.

Source pointers are tied to actual selected DBRClub and runtime DBRUser/linked lists. Replacing the event with a deferred `selected_club_ids` set does not reproduce this original transition.

## 2. Additional original shared-CRT calls BEFORE six staff births

`0x42C400` invokes `0x421C00` directly exactly nine unrolled times (0x42C422, 0x42C43B, 0x42C454, 0x42C46D, 0x42C486, 0x42C49F, 0x42C4B8, 0x42C4D1, 0x42C4EA), then FOUR more times at 0x42C505 in `0x42C4F5..0x42C50E` loop. Total **13 pairs = 26 bounded CRT calls per successful native 0x42C400** before any staff. Name input is selected club+0x14 nationality/country; actual `0x421C00` draws two independently selected source PLAYER positions via original `0x421BA0`. The routine uses no first-name '-' retry (unlike `0x4CA660` SupportStaff), so sentinel source strings can be retained.

Original DBRUser destination offsets for the first/surname pointers are nine sequential pairs +0x520/+0x524 .. +0x560/+0x564, followed by four staggered pairs +0x568/+0x578, +0x56C/+0x57C, +0x570/+0x580, +0x574/+0x584.

This makes **at least 26 + 6*12 = 98 direct calls** per original first-human creation in the ordinary source before PSupportStart, with variable 1–3 associations per staff, name retries, and other indirect constructor side effects potentially adding further draws. This is a LOWER BOUND, NOT permission to skip or inject 98 synthetic calls.

## 3. Existing clean-room normal Windows UI and CRT startup divergence

Current main `reconstruction/front_end_session.py`:
- `FrontEndSession.toggle_club_selection` (lines ~176–189) **only** updates `selected_club_ids` and selected count. No native DBRUser+staff constructor transaction or modal.
- `FrontEndSession.dispatch` (lines ~228–254) obtains a parsed catalog on New Game, but explicitly DEFERS gameplay backend until TeamSelect Start/Continue; line ~256+ creates the backend only at Start, and multiple selected humans fail closed.
- `reconstruction/original_game_host.py` (~3040–3049) handles the club row via front-end presenter/row updates, then Start/Continue enters recovered PMenu; **no full PSupportStart seven-row modal** is entered on club selection.
- `reconstruction/game_state.py GameState.from_database` (~386+) creates a NEW local MSVC CRT seeded with time/argument and materializes runtime players at GameState creation, which is currently delayed until Start in the canonical GUI. The source original DBTPlayers and Loader444 CRT consumption already happened BEFORE human selection; later runtime source user and six staff births occur before original Continue.
- `reconstruction/startup_rng.replay_precompetition_startup_rng` consumes Loader444, DBTPlayers, team-name and youth blocks in one helper, **omitting original TeamSelect DBRUser name-pair initialization and all six support staff births**. Historical `research/STARTUP_RNG_LEDGER.md` paragraph saying TeamSelect consumes zero original CRT before Continue is superseded for the player journey, and historical fixed raw-draw checkpoints are partial-only.

**CONFIRMED code absence** versus original source: whole user creation transaction is missing at native click. Current controls/visuals/selection set do not establish original multi-user setup or true shared CRT continuity. This is P0 for original new-career fidelity, and independent from original GUI/Windows acceptance still missing.

## 4. Source-bounded new components, not yet integrated or accepted

On the EXISTING unopened SupportStart feature branch (no unnecessary PR/CI), newly staged:
- `reconstruction/original_supportstart_user_creation_rng.py`: explicit 13 original name-pair records / 26 bounded draws on caller-owned shared RNG, unique original source player-pool position, CP1252 + exact native field offsets, **no '-' retry**.
- `reconstruction/test_original_supportstart_user_creation_rng.py`: 26-draw ordering/field offsets, no-sentinel-retry, original-group use, negative guards.
- `reconstruction/original_supportstart_teamselect_staff_rng.py`: one normal 0x4C9B30 staff's source DIRECT RNG call receipt, preserving both full-pair retries, vft+0x2C twice, +0x30 RNG30 and +0x58 1–3 native club assignments; uses same passed original shared RNG, no independent seed.
- `reconstruction/test_original_supportstart_teamselect_staff_rng.py`: 1/3 associations, retry and invalid-context tests.
- Existing `original_supportstart_teamselect_staff_clubs.py`, `original_supportstart_player_name_source.py` and their regressions support the original club/name sources. Neither source component mutates GameState, starts a user, creates a playable modal or claims false exact seed.

**Tests on the exact active branch not executed:** GitHub remote cannot be cloned from local shell due DNS (the secure GitHub connector remains writable). A reviewable feature milestone must undergo actual exact-head targeted/full tests and asset privacy policy CI. Do not mistake private original-executable static disassembly for execution, tests or game GUI acceptance.

## 5. Highest-impact continuation

1. Audit original first-user `0x413BB0` constructor callees `0x424CA0`, `0x4258D0`, `0x426090` and the source seed-to-TeamSelect boundary for any additional CRT, name/text producer and later rollback. Verify the true shared CRT at first source 0x42C400 and 0x4C9B30, for 1–6 humans and actual selected country/root league.
2. Integrate an **atomic genuine TeamSelect club click -> DBRUser+13 pairs -> six full staff -> 7 selectors -> PSupportStart Apply/Cancel/return** transaction using already authenticated original name and club data, source assets and exact GUI control/hit owner. Be careful that Cancel and removal/reselect must not corrupt original shared RNG or user linked lists; source-proof them first.
3. Share the process CRT across Loader444, database, TeamSelect and subsequent competition initialization rather than seeding a new independent RNG at Start. Re-audit previous Gate2–4 seed and fixture equivalence claims against actual original user selection events.
4. At coherent player-visible integration, create one reviewable PR with source-proven tests, privacy/asset checks, exact-head required CI and a real user Windows11 GUI acceptance. Then continue Inbox, R1 four modes/PResults, complete leagues/countries/2–6 humans, Gates 13–17 Windows11 release audit.

Do not mark Gate13 or any later gate passed from static original disassembly or synthetic tests. Continue from GitHub, not the conversation.


## Recovery558 independent original executable static assertions PASS

A fresh deterministic local script, inspecting the SHA-confirmed original PE with Intel objdump, asserted all of the following without executing the original process:

| Native owner | Assertion | Result |
| --- | --- | --- |
| 0x42C400..0x42C514 | exactly 10 textual callsites to 0x421C00, of which 9 are unrolled and last at 0x42C505 sits inside native four-iteration loop | PASS |
| 0x4C9CD0..0x4C9D12 | exactly 6 source calls to 0x4C9B30 before post-staff linkage | PASS |
| 0x4CB0F0..0x4CB2B0 | exactly four DIRECT bounded RNG call instructions, 0x4CB16D/0x4CB1A1/0x4CB1CE/0x4CB1D7 (the latter three run once per chosen assignment) | PASS |
| 0x4CA660..0x4CA6CF | original source compare branch at 0x4CA6B6 loops back to 0x4CA66B, i.e. both name choices repeat on first-name "-" | PASS |

The helper is a static x86/source receipt only; no current GitHub branch code was checked out in the local shell, so **new Python tests and full suite were not run** and no GitHub Actions claim is made. Source code/asset privacy unchanged.

### Immediate integration impediments, source-specific

Canonical main FrontEndSession currently preserves team selection only as IDs while the source event constructs an actual linked DBRUser, resolves 13 generated name pairs, creates six Staff objects, and enters editor BEFORE its start transition. Canonical main GameState.from_database currently creates a new CRT at backend materialization, which is deferred to Start/Continue. Correct replacement must avoid silently shifting all later seed/fixture states. Source selected user initialization 0x413BB0 also calls DBRUser constructor 0x424CA0 (whose visible four array element initializer 0x424F70 is RNG-free) and 0x426090 current-manager binding with indirect nontrivial subcalls. The complete seed-to-first-user branch, including 0x426090 indirect runtime effects and modal Apply/Cancel/rollback, remains to be audited. Do not declare an *exact* pre-staff LCG checkpoint from the >=98 direct calls alone.

The source itself is accessible; the outstanding limitation is exact-head code test execution/graphical acceptance (local shell cannot resolve github.com for a clone), not unavailable original bytes. Continue branch-staged source modeling and native event mapping, then combine into one full feature PR with its required exact-head CI rather than triggering CI for every trace.


## Recovery559: composed first-click CRT transaction and modal ownership

The already-verified original user+staff draw components are now composed, **without an independent seed or GUI side effects**, in `reconstruction/original_supportstart_teamselect_user_birth.py`. The source-only `replay_original_teamselect_user_birth_direct_rng` requires the actual clicked `Club.index`, its selected native root-league definition from TeamSelect row+0x4C, the clicked club's original country-dependent name route, original source-ordered Player/Club tables, and a caller-owned RNG already at the correct first-click checkpoint. It preflights source contexts before drawing, consumes 13 original user pairs (26 calls) and then six original staff in exact type order on the **same RNG object**, returning a receipt that distinguishes names, RNG draw counts and club associations. No CSupportStaff registration or DBRUser native linked-list mutation is claimed. Its unit tests `reconstruction/test_original_supportstart_teamselect_user_birth.py` cover the minimum 98 direct draws, correct first-versus-next user club-group RNG bound, six exact staff types, source context mismatch rejection with zero advance, and no silent per-user reseed/rewind. Tests remain **unexecuted on the exact branch** until available CI or isolated verified checkout.

### Original editor is a separate guarded TeamSelect input callback

A fresh static trace of the original (SHA256 `833bf95e...`) distinguishes the new-human creation callback `0x4D8E90` from the **later separate editor-opening callback `0x4D91C0`**. Native `0x4D91C0` first calls base owner event `0x64F960` with its incoming event arguments and requires its return to be nonzero; it then checks original control bit15 via `0x652F80` and returns without modal if false. Only after BOTH gates does it locate the corresponding selected-human slot through `0x4D9240`, select current native user via `0x413B80`, and invoke `0x450BB0` with slot index and two actual original entry-name/state pointers. This is not proven to be a generic click on arbitrary 326×37 visual row bounds.

`0x450BB0` itself constructs the PSupportStart object `0x4CF0F0`, lays it out from original screen position, runs modal `0x5EB540 -> 0x532650`, then reads **source result BYTE `PSupportStart+0x1DE4`** into BL at `0x450CBF`; cleanup via `0x5EB920` returns the same result as `AL`. Thus **the modal itself distinguishes Cancel=0 from Apply=1**. Crucially its TeamSelect editor-event caller **`0x4D91C0` at `0x4D922C` overwrites `EAX` with its earlier base event acceptance result held in EBX**, discarding `0x450BB0`'s AL before returning. This means Cancel can still count as a handled click at the OUTER TeamSelect event layer; do not equate the handler's return with Apply.

Original `0x450BB0` sets modal width/height `0x2F8×0x1F4=760×500` and uses source global 0x8779C0/0x8779C4 for placement (clamped by native bounds), with additional x/y controls from source `0x653320`. Do not substitute a centered invented Tk dialog or assume mouse-hit regions from underlying visual row rectangles. The exact source hit owner/hotspots still need explicit reconstruction.

### Native pre-staff call graph constraints

Original `0x413BB0` first checks whether an existing user for the same club is already linked, and can return zero without allocating a fresh DBRUser. **The 26+six-staff transaction is ONLY for successful native new-user creation**, not every TeamSelect click. The normal new-user branch calls `0x424CA0` constructor, `0x4258D0` (which calls `0x42C400`) and `0x426090` manager slot/name binding before staff. An original static scan of direct callees `0x424CA0` and `0x426090` finds no direct call to `0x64D540`/CRT random, but **indirect helpers/vtable actions and source transition calls remain unqualified**; the source-only transaction must not present itself as the complete original seed-to-staff stream. The click path also invokes `0x412EF0` after registration but before staff creation, whose nested source graph remains to be audited for RNG and rollback side effects. Do not advance a fixed 98 calls or assume no intervening RNG without proving those callees.

Reproduce static original:
```bash
objdump -D -Mintel --start-address=0x4D8E90 --stop-address=0x4D90A0 footballmanager.exe
objdump -D -Mintel --start-address=0x4D91C0 --stop-address=0x4D9240 footballmanager.exe
objdump -D -Mintel --start-address=0x450BB0 --stop-address=0x450CE9 footballmanager.exe
objdump -D -Mintel --start-address=0x413BB0 --stop-address=0x413C86 footballmanager.exe
objdump -D -Mintel --start-address=0x4258D0 --stop-address=0x425A10 footballmanager.exe
objdump -D -Mintel --start-address=0x426090 --stop-address=0x42621E footballmanager.exe
```

**Next work:** establish mandatory intermediate `0x412EF0` and `0x426090` hidden-CRT effects and actual first-click game-CRT state; source-bind distinct original new-human and editor-button callbacks and their Cancel/Apply linked-list semantics into Windows host. The source transaction is staged for integration but has no fake user creation, private assets, or GUI. Gate13–17 still open.


## Recovery559: exact six-list staff order and initial seven row transfer

Static disassembly of the same authenticated original further resolves the source list staging that occurs **before** PSupportStart opens:

- Native `0x4C9CD0` creates six CSupportStaff in type order 1,2,3,4,5,13. Every successful `0x4C9B30` appends its newly allocated staff-node **to the TAIL** of current user's `DBRUser+0x5D0` list through `0x4C9CA6 -> 0x617D70`. Original `0x617D70` uses current list last-node at +0x08 and updates its +0x04 successor; thus original staff-list order equals original constructor order (it is not reversed by head insertion).
- Original `0x4D8F7F -> 0x4DA4F0` initializes selector index `EBP=6` and iterates in descending order **6,5,4,3,2,1,0**. Its list lookup starts at user `+0x5D4` and advances exactly EBP successor links. Six entries mean index6 is empty; index5 resolves type13, index4 type5, ... index0 type1. Thus seven original starting rows are staff types **(1,2,3,4,5,13,NULL)**, but the *native list-transfer execution order* is **(13,5,4,3,2,1)**.
- At `0x4DA537` on each nonempty row, `0x4CA070` appends source staff to the current user's **type-specific inactive list**, `DBRUser+0x5B8` for types1..5, `+0x5C4` for types6..16. At `0x4DA561`, original `0x4D1880` removes its original node from current user `+0x5D0`. A separate branch at `0x4DA566..0x4DA58D` conditionally removes the staff from global `0x875600` if it is found there. These are original mutable list operations **before** the editor's native Apply or Cancel events.
- The later PSupportStart Apply routine `0x4D0830` starts by resetting the three original user staff list anchors and conditionally reattaches selected staff by the original source flags, so its effects differ from simple display-row staging. **Cancel(0) does not invoke that Apply routine, but that alone is NOT proof that premodal staging side effects are undone or retained after cleanup.** Trace the modal destructor, TeamSelect caller, and subsequent user-return paths before asserting cancellation rollback semantics.
- The stage-only port source component `reconstruction/original_supportstart_initial_modal_rows.py` projects the six **final (second-pass)** names and original row owner offsets, with an empty seventh row. Its `source_supportstart_native_staging_transfers` produces an ordered **unexecuted native list-change plan** for the six transfers (13,5,4,3,2,1), identifying current user+0x5D0 source, type-specific +0x5B8/+0x5C4 target and conditional global removal. It never mutates GameState or invents actual Cancel rollback. Dedicated focused regressions are staged but **NOT exact-head executed**.

Reproduce: `objdump` 0x4C9C7E..0x4C9CAB, 0x617D70..0x617DA5, 0x4DA4F0..0x4DA59B, 0x4CA070..0x4CA0CF, 0x4D0830..0x4D093B. Original process not launched and no Windows GUI acceptance. This source stage closes initial name-and-slot ordering but does not close full modal lifecycle, linked-list persistence, exact shared CRT seed or Gate13.
