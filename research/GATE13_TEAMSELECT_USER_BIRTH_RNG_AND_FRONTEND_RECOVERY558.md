> **RECOVERY561 MATERIAL SOURCE CORRECTION, 12 OCTOBER 2026:** Prior Recovery560 claim that the `0x5EB920` cleanup indirect `+0x74` necessarily dispatches `PSupportStart::0x5D4860` is **WRONG**. The object at `0x5EB962` comes from `0x5EB8F0 -> 0x6555D0`, where the global *rendering/device service* `0x947590` is called through its virtual+0x18 to obtain a different graphics object, not the original PSupportStart pointer. The same graphics `+0x74` operation occurs on **modal opening** at `0x5EB5D6`, establishing this is a generic rendering setup/teardown edge, NOT standalone evidence of original staff-list Cancel effects. **The actual PSupportStart destructor is called later at `0x5EBAA0: call [edi->vft+0]`**, with `EDI` carrying the original modal pointer; the real PSupportStart deleting destructor is `0x4CF790 -> 0x4CF7B0`. Correction detailed at end. Do not use the old `+0x74` association for input/Cancel semantics.

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


## Recovery559 continuation: original row first/second text semantics, localized type label origin

Authenticated original x86 `0x4D06B0..0x4D07C9` corrects the initial row visual semantics, independently of source name-generator output:
- The original PSupportStart row **FIRST** buffer `+0x70+0x80*i` receives a **localized staff role caption**. The code obtains each staff type from native CSupportStaff vft+0x14, passes it to `0x4CDCD0`, then copies that returned role string into the first buffer. It is **NOT the staff member's first name**.
- The row **SECOND** buffer `+0x4F0+0x80*i` receives the staff's **complete combined name** from CSupportStaff vft+0x08, not its surname alone. Thus splitting the final source first/surname pair over both buffers would render source-wrong text.
- If a source slot has no staff pointer, `0x4D07B0` copies original empty literal `0x874BA0` into both buffers and handles the selector state separately.
- `0x4CDCD0` dispatches original staff types 1..16 through its actual jump table at `0x4CDD84`; types 1..12 use original localized data pointer slots `0x982AA4` down through `0x982A78`. **Type13 specifically reads `0x9821E4` instead of sequential `0x982A74`; types 14/15/16 use `0x982A70`, `0x982A64` and `0x982A60`. Do not assume a simple continuous 16-role-index lookup** based only on a similar-looking English.str list.
- Source language loader `0x6458B0..0x645AF9` reads 2-byte string reference IDs from its selected original language index and calls `0x64E320` to produce pointers in the role-owner slots. `0x64E320` is just a 16-bit table index into its language resource owner pointer array; it does not independently establish every original role ID or every supported language.

Authenticated original private `English.str` 369,644 bytes, SHA-256 `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`, and `English.idx` 5,428 bytes, SHA-256 `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1`, were additionally targeted and raw-byte retrieved from the owner's private extracted Google Drive folder. Original English.str string IDs 21207..21222 contain candidate staff role terms, and English.idx positions 1877..1892 map to those source IDs in order. **But no proof yet establishes the reader's precise index-offset when populating these 16 role global pointers, nor the exception type13**, so a full source-complete type->role-label table is NOT currently authorized. Keep captions unresolved rather than embed guessed strings. No private proprietary binary bytes were committed.

The updated `reconstruction/original_supportstart_initial_modal_rows.py` exposes `source_staff_full_name` as a combined string on the second text owner and `source_role_label=None` on first (pending true localized source resolution); its regression cases assert correct owner offsets and absence of invented captions. Still no live GTK/Tk mouse behavior, original process execution, exact-head Python tests or Win11 GUI acceptance.

Reproduce via original static disassembly:
```
objdump -D -Mintel --start-address=0x4D06B0 --stop-address=0x4D07C9 footballmanager.exe
objdump -D -Mintel --start-address=0x4CDCD0 --stop-address=0x4CDD82 footballmanager.exe
objdump -D -Mintel --start-address=0x6458B0 --stop-address=0x645B00 footballmanager.exe
objdump -D -Mintel --start-address=0x64E320 --stop-address=0x64E339 footballmanager.exe
```

**NEXT:** source-resolve localization pointer index offset and special type13 label; trace actual modal Cancel cleanup/restoration and input-owner hit/selection callbacks. Then integrate selected native human/staff birth and GUI on one true CRT. Gates13–17 and original/Win11 GUI acceptance remain OPEN.

## Recovery560: reuse Recovery551 SOURCE-CLOSED staff role localization, do not rediscover

**Correction to the late Recovery559 paragraph above:** role-label provenance was NOT unresolved in the canonical repository. Already-merged `research/GATE13_PSUPPORTSTART_STAFF_LOCALIZATION_RECOVERY551.md` and `reconstruction/original_supportstart_staff_labels.py` source-qualified ALL SIX ordinary starting staff labels and all sixteen supported role cases, including special type13. The actual CSupportStaff constructor stores type at +0x04, verified vft+0x14 `0x42CB40` returns that same type, and PSupportStart `0x4D0725` forwards it to native `0x4CDCD0`. The original language initializer `0x64A312` separately populates 0x9821E4 from `English.idx` position2437, resolving type13 **Physiotherapist**. This predates Recovery559; no new localized-data inference is needed.

Independently reopened the unchanged private original 369,644-byte English.str SHA256 `aa594a55...` and English.idx 5,428-byte SHA256 `98fcbe9e...`. Parsed their real uint32-offset string table and uint16 string index IDs directly: native cases (1,2,3,4,5,13) return exactly:
```
ASSISTANT MANAGER
STADIUM MANAGER
YOUTH TEAM MANAGER
BUSINESS CONSULTANT
CHIEF SCOUT
Physiotherapist
```
The type13 entry is English.idx slot2437, NOT the neighboring slot1889 MASSEUR. Original staff role mapping in existing `support_staff.py` main is already corrected: ASSISTANT_MANAGER_TYPE=1, not the old wrong2. No new fix needed there.

Updated branch `reconstruction/original_supportstart_initial_modal_rows.py` to optionally accept BOTH existing `EAStringTable` and `EAStringIndex` and use the existing `original_supportstart_native_staff_label` resolver for the original **first** text buffer `+0x70+0x80*i`. The original **second** buffer `+0x4F0+0x80*i` still holds the complete source staff name and the seventh row remains empty. With no original language pair, first-buffer role is intentionally unresolved (None); incomplete or invalid language inputs fail closed rather than inventing a string. Extended existing source rows tests to assert all six authentic labels and the special Physiotherapist role using the actual repository original assets. **Private source bytes reverified in shell; new GitHub Python tests not yet executed on exact feature head.**

Also staged `original_supportstart_modal_result.py` and its synthetic tests: after native `0x64F960` acceptance, `0x652F80` bit15 must be set to open modal; inner event1 Cancel returns0 without `0x4D0830`, event2 Apply returns1 with it; outer `0x4D91C0` returns saved event-acceptance EBX regardless of the inner modal result. This is a source-defined **result projection only**, not a mouse/keyboard controller and not proof of native Cancel linked-list restoration. Confirmed by fresh static original disassembly of `0x4D91C0..0x4D9238`, `0x450BB0..0x450CE8`, and old native `0x4D05E0..0x4D0631`.

**Still unverified:** source modal input owner/hit acceptance, original DbrUser/Staff linked-list post-Cancel lifecycle (native destructor `0x4CF7B0` and `0x5EB920` include indirect GUI owner callbacks, so a bounded absence of direct staff-list calls is not general rollback proof), intervening indirect original CRT from new-user constructor `0x4258D0` and manager binding `0x426090`, exact seed checkpoint, actual live Windows PSupportStart, 2–6 human, release. No original executable launch or genuine Windows GUI acceptance.

**Exact next:** verify any native transient pre-staff callsite random consumption and complete modal close list semantics; then source-wire original TeamSelect immediate DBRUser/13 name pairs/six staff/actual seven-row PSupportStart and original assets using ONE same process CRT with true club context; meaningful milestone PR and exact-head tests/assets/Win11 acceptance. Gate13–17 OPEN.


### Recovery560 targeted native pre-staff RNG callsite audit: bounded, not a global proof

Repeated independent objdump analysis on the SHA256-verified original, inspecting complete explicitly named native ranges, found the following **direct callsite counts** (direct target 0x64D540 bounded RNG, 0x66951C raw CRT rand or 0x66950F reseed):

| Native function/range | Total direct/indirect CALL instructions | Direct RNG/seed calls |
| --- | ---: | ---: |
| new TeamSelect user branch 0x4D8E90–0x4D8F84 | 11 | 0 |
| DBRUser constructor 0x424CA0–0x424F6B | 10 | 0 |
| DBRUser initializer 0x4258D0–0x426090 | 60 | 0 (calls 0x42C400 separately, which contains 13 name-pair consumers) |
| manager binding 0x426090–0x42621E | 6 | 0 |
| selected-user support reset 0x412EF0–0x412FEF | 9 | 0 |
| staff wrapper 0x4C9CD0–0x4C9D35 | 9 | 0 (delegates all staff draws to 0x4C9B30) |

The manager binder 0x426090 calls 0x403E10, 0x4151C0 (itself calls 0x413B10), 0x415870 (which calls 0x405CF0 and 0x50FFC0), plus allocation/free. None is a direct RNG(…) call at the binder. DBRUser initialize reaches indirect `0x614080` global owner; possible virtual callbacks and helpers (`0x5DC400`, `0x5E43B0`, `0x5DED10`) require targeted second-level audits. The original selected-user setup 0x412EF0 has no direct RNG either, but calls 0x614080 and 0x414610 on any existing list entries. These bounded negatives narrow the unresolved branch; they DO NOT establish globally “RNG clean” or a complete exact first-click checkpoint. The 0x42C400 pair draws and 0x4C9B30 six staff draws are still definitely present through callees.

Reproduction without original EXE execution:
```
objdump -D -Mintel --start-address=0x4258d0 --stop-address=0x426090 footballmanager.exe
objdump -D -Mintel --start-address=0x426090 --stop-address=0x42621e footballmanager.exe
objdump -D -Mintel --start-address=0x412ef0 --stop-address=0x412fef footballmanager.exe
objdump -D -Mintel --start-address=0x415870 --stop-address=0x415929 footballmanager.exe
```
**Next precise call-graph step:** qualify 0x614080's dynamic vtable branch for passed global 0x947AA8 and 0x4258D0's original 0x5DC400/0x5E43B0/0x5DED10 helper paths; determine whether they can touch 0x64D540/0x66951C before the normal six-staff creation. Continue UI-modal Cancel list lifecycle through 0x5EB920/vft+0x74 and PSupportStart destructor 0x4CF7B0 before asserting rollback. Gates13–17 remain open.


### Recovery560 modal-close callback qualification, not Cancel rollback proof

Exact original PSupportStart vtable **0x7C6DDC+0x74** contains `0x5D4860`, confirmed from its original .rdata little-endian DWORD (the same vtable has +0x00 `0x4CF790` deleting destructor and +0x4C `0x4D0830` Apply). Generic modal-close routine `0x5EB920` resolves a widget object via `0x5EB8F0` and calls its dynamic **vft+0x74** at `0x5EB962`. This may dispatch `0x5D4860` IF the resolved object is in fact the PSupportStart object; the original type at that callsite still needs independent identification.

`0x5D4860..0x5D48B7` checks a group-control enabled/state bit at +0x18, iterates source registered child controls +0x2C/+0x34 with registration bit0x10, filters through `0x64F570`, then calls eligible children **virtual+0x18**, and finally `0x64F450`. It does not directly invoke `0x4CA070`, `0x4D1880`, `0x617D70`, `0x4D0830` or a DBRUser list. However the indirect child+0x18 actions and the exact object returned by `0x5EB8F0` must be proved before asserting no staff-list mutations at modal close. The native PSupportStart destructor `0x4CF7B0..0x4CFA6E` predominantly calls UI/control destructors `0x64F350`, group destructors `0x5D4600`, and base/resource teardown; no direct source staff-list writes were identified in that bounded range. **Cancel does not execute Apply** is proven; **Cancel restores all staged lists** is NOT.

This preserves the distinction between original modal inner result, outer event acceptance, native staged linked-list moves, and final persisted user staff state. Do not fake Cancel restore or treat zero modal result as a non-click. Actual source close lifecycle remains PARTIAL.


## Recovery561: correct modal cleanup ownership, graphics handle vs PSupportStart

Authenticated original PE SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, static x86 disassembly, no process execution.

The earlier source narrative at Recovery560 conflated **TWO DISTINCT OBJECTS**:

**Actual graphics object passed through rendering layer**
1. `0x450CCD` passes the actual PSupportStart pointer (in `ESI`) as first stack argument to generic close `0x5EB920`.
2. `0x5EB941: mov edi,[esp+0x48]` stores that original PSupportStart pointer in `EDI`.
3. `0x5EB945..0x5EB953` passes it to `0x5EB8F0`, whose `0x5EB8F4..0x5EB910` calculates the source layout width/height from window fields, fetches **`[0x947590]` graphics/service pointer**, and calls `0x6555D0` with that service and the rectangle parameters.
4. Original `0x6555D0..0x6556BC` builds a graphics request, then at **`0x6556A5: call [render-service-vft+0x18]`** obtains a **different EAX returned graphics object**. It is THIS return value moved to **`EBX`** at `0x5EB956`, and `[ebx->vft+0x74]` is invoked at `0x5EB962`. Thus it is not necessarily the PSupportStart virtual+0x74 function `0x5D4860` (and in the actual concrete operation the object owner/source is a graphics service, not the modal's own virtual table).
5. On original modal **opening**, the same `0x5EB8F0` and `[ebx->vft+0x74]` pair occurs at `0x5EB5AF` and `0x5EB5D6`, confirming it represents generic graphics/front-buffer ownership, not a specially triggered Cancel callback. Its exact drawing/viewport side effects should be audited separately but **cannot establish staff-list rollback**.

**Actual SupportStart lifetime cleanup**
1. After restoring graphics service state and native frame event owner, `0x5EB920` holds original PSupportStart in **`EDI`**, tests it nonnull at `0x5EBA96`, and at `0x5EBA9A..0x5EBAA0` performs `push 1; mov ecx,edi; call [edi->vft+0]`.
2. PSupportStart original vtable base is `0x7C6DDC`, slot+0 is **`0x4CF790`**, deleting destructor. `0x4CF793` directly invokes **`0x4CF7B0`**, then conditionally frees its object when the flag has bit0. That is the true modal/window destructor chain in the close routine.
3. Native `0x4CF7B0` statically destroys large ranges of UI child controls/text/layout resources, mostly through control/base destructors such as `0x64F350` and `0x5D4600`. No direct normal user+0x5D0/+0x5B8/+0x5C4 list restoration or Apply call appears in the bounded destructor disassembly. **Absence of direct calls is not evidence of a full negative result** because its generic child destruction/indirect owner effects are not fully qualified.
4. **Native Apply** still source-verified only on PSupportStart action2 at `0x4D05E0 -> 0x4D0830`; action1 sets modal result0 without Apply. The premodal original `0x4DA4F0` staff list staging remains real and prior to either button. Whether its effects remain on Cancel, or are reversed by later owner logic, is **UNRESOLVED**. Do not assume GUI Cancel restores staff or that it discards the entire human selection/CRT stream.

**Practical correction:** For real original PSupportStart cancellation, examine original `0x4CF7B0` true destructor child owner effects, `0x4D91C0` parent return and any re-entry to `0x4DA4F0` / linked-list repair. **Do not trace generic 0x5D4860 row propagation as modal destructor on the false premise that it was +0x74 called by 0x5EB920.** Other original UI layouts may use 0x5D4860 for legitimate events independent of that incorrect modal ownership.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x5EB8F0 --stop-address=0x5EB919 footballmanager.exe
objdump -D -Mintel --start-address=0x6555D0 --stop-address=0x6556BD footballmanager.exe
objdump -D -Mintel --start-address=0x5EB920 --stop-address=0x5EBAC0 footballmanager.exe
objdump -D -Mintel --start-address=0x5EB540 --stop-address=0x5EB5E0 footballmanager.exe
objdump -D -Mintel --start-address=0x4CF790 --stop-address=0x4CF857 footballmanager.exe
```

**Next specific source task:** inspect direct original PSupportStart destructor `0x4CF7B0` down to every nontrivial owned callback and generic child vtable teardown, then parent `0x4D91C0` post-return and TeamSelect registration/lifecycle; qualify real staged-staff behavior on Cancel. Separately trace original pre-first-human `0x614080` indirect helpers and shared CRT checkpoint. The branch remains source-only; no original process launch, exact-HEAD Python tests, GUI playtest or Gate13–17 release acceptance.


### Recovery561 next verification: PSupportStart row destruction is GUI child destruction, not a direct staff-list restore

Tracing the actual SupportStart deleting destructor `0x4CF790 -> 0x4CF7B0` down one additional level:

- At `0x4CF936..0x4CF94B`, the destructor pushes callback `0x4D89E0`, count 7, stride `0x4C`, and data pointer `this+0x2224` into native vector-destructor helper `0x66820D`. This is **exactly the seven PSupportStart selector-control array**, not an original six-staff DBRUser list.
- Function `0x4D89E0` is a five-byte unconditional jump directly to generic GUI group destructor **`0x5D4600`**. This sets the GUI vtable `0x7D68AC`, loops `group+0x2C` registered control children and invokes each child's **virtual+0x04 deleting destructor**, frees the group's child-control pointer array, then calls base control destructor `0x64F350`.
- `0x64F350` resets generic native input-owner state (clearing globals `0x984814` and `0x984818` if equal to the destroyed widget); it does not touch support-staff linked-list heads. Other direct `0x4CF7B0` callees in the bounded range are the same base controls/destructors and resource cleanup `0x64D780`, whose indirect base resource calls are still unqualified as a complete negative trace.
- This narrows the **seven selector child destructor path** to UI lifetime cleanup. It does not on its own prove that all PSupportStart Cancel paths restore/retain DBRUser+0x5D0/+0x5B8/+0x5C4, because previous `0x4DA4F0` list-transfer and subsequent TeamSelect game-model callbacks are separate. Do not model Cancel as a clean reversal simply from a deleting destructor.

### Recovery561 exact pre-staff event-list dispatch is conditional

`0x412EF0` invokes generic event-queue `0x614080` with `ECX=0x947AA8` before staff list initialization. The actual `0x614080` function checks owner+0x0C: when nonzero, it ONLY writes owner+0x10=1 and returns (**zero direct or indirect RNG calls in this branch**). Otherwise it walks pending nodes through +0x04; if nonempty, it dispatches polymorphic event targets vft+0x04 and +0x18, potentially removing nodes by `0x4EA190`. Therefore a claim of no RNG consumption here requires proving the event queue is empty/short-circuited for the exact first-user click. Simply observing no direct call to RNG in `0x412EF0` is NOT sufficient. This is a concrete runtime-state predicate, not a perpetual generic blocker; target the `0x947AA8` owner initialization and producer at the first TeamSelect event.

Reproduce:
```
objdump -D -Mintel --start-address=0x4CF92A --stop-address=0x4CF9B0 footballmanager.exe
objdump -D -Mintel --start-address=0x4D89E0 --stop-address=0x4D89E5 footballmanager.exe
objdump -D -Mintel --start-address=0x5D4600 --stop-address=0x5D4670 footballmanager.exe
objdump -D -Mintel --start-address=0x64F350 --stop-address=0x64F376 footballmanager.exe
objdump -D -Mintel --start-address=0x614080 --stop-address=0x6140EF footballmanager.exe
objdump -D -Mintel --start-address=0x412EF0 --stop-address=0x412F30 footballmanager.exe
```

**Next source actions:** investigate owner global `0x947AA8` initialization and when it has queued nodes on normal TeamSelect user creation, original `0x4258D0` + `0x426090` virtual subcall reachability, and any post-Apply/Cancel movement in the TeamSelect main model. These must precede a source-exact shared CRT claim. The Windows 11 host currently lacks the immediate source user/event/modal transaction; its original fidelity is still incomplete, and no original GUI acceptance, exact-head new Python test result or Gate13 closure is claimed.


## Recovery561 continued: identify concrete pre-staff queue producer and callbacks

Native queue global `0x947AA8` is NOT an inert reserved pointer. Its enqueue method has been identified:

- `0x613EC0` with ECX pointing to queue owner allocates 0x0C-byte linked-list node through `0x668140`, copies the incoming dynamic event object pointer into its first field, and appends through shared native list helper `0x617D70`. Its owning queue list is at **owner+0x04**. This is source-backed actual queue production, not merely a theoretical indirect dispatch.
- Actual original source producer `0x4044F5..0x404503` pushes the constructed polymorphic object `ESI`, sets `ECX=0x947AA8` and **calls `0x613EC0`**. This gives one real source path that can populate the global list.
- `0x613EE0` sets owner+0x0C=1 during event processing, iterates objects, invokes their virtual+0x10 to check eligibility, conditionally removes via `0x4EA190`, clears owner+0x0C, and invokes `0x614080` recursively if owner+0x10 deferred work is flagged. `0x614080` additionally invokes each queued object's virtual+0x04 and +0x18. These are actual potential indirect source side-effect routes, not a direct RNG call.
- Original `0x425570` is a separate queue query by owner `0x947AA8 -> 0x614230`, searching event objects with virtual+0x14 tags 0x45/0x54 for a matching object member. This supports original queue's dynamic gameplay-event nature, not a locally empty UI placeholder.

**What is NOT proven:** whether `0x4044F5` producer or any other enqueue route executes before normal first-user TeamSelect `0x412EF0`, whether a specific queued object virtual callback uses shared CRT, and whether a call at first-user selection sees queue owner+0x0C set/queue owner+0x04 nonempty. Consequently the prior 26+6-staff direct RNG ledger remains a lower bound, NOT an exact precompetition seed checkpoint. To finish, trace normal launcher -> DB load -> TeamSelect entry event queue state and instantiated event class virtuals on that path.

Reproduction: `0x613EC0..0x613EDD`, `0x613EE0..0x613F4C`, `0x614080..0x6140EF`, `0x4044D3..0x40450C`, `0x425570..0x425581`. All independent original private static disassembly, no original process launched or normal Windows UI playtest.


### Recovery561: one queued object's concrete polymorphic forwarding confirmed

The actual original `0x4044D3..0x404503` event producer assigns vtable **0x7BD564** to the 0x0C-byte wrapper before enqueuing it. Independently reading that original PE `.rdata` vtable gives `+0x04 = 0x40DFB0` and `+0x18 = 0x404610`:
- `0x40DFB0` is exactly `xor eax,eax; ret` (this wrapper's own +0x04 callback is **RNG-free** and returns false).
- `0x404610` loads wrapper+0x08 **underlying event object** and tail-jumps through its **virtual+0x24**. Hence the outer queued wrapper's +0x18 callback can perform underlying object-specific work. Its source object is constructed at `0x4044CA -> 0x555D60`, and its concrete vtable/call graph, runtime reachability before first human and shared CRT impact remain to be established.
- The vtable+0x14 function `0x404600` separately tail-jumps to underlying event object vft+0x40, confirming this wrapper delegates several behaviors rather than implementing static category logic itself.

This is a narrower independently proven indirect dispatch boundary, not a claim that this event is queued when first TeamSelect creates a human. Source execution order and actual queue contents must still be qualified. Reproduce `0x7BD564..0x7BD580`, `0x40DFB0..0x40DFB3`, `0x404600..0x404618`, `0x404450..0x404506`.


### Recovery561 final follow-up: one concrete queued class has RNG-free virtual+0x24

The specific native event created by `0x4044CA -> 0x555D60` and enqueued at `0x4044F5..0x404503` is now closed **for its two event-queue callback slots**, removing one false indirect-RNG suspicion without asserting ALL queue entries are safe.

1. Native constructor `0x555D60..0x555DF2` writes actual underlying event instance's vtable **0x7CE378** at `0x555DC6`.
2. The queue envelope constructed by `0x404450` writes wrapper vtable **0x7BD564** at `0x4044DC`. Original vtable+0x04 is **0x40DFB0** (`xor eax,eax; ret`), which consumes no original CRT.
3. This wrapper's vtable+0x18 is **0x404610** (`mov ecx,[ecx+8]; mov eax,[ecx]; jmp [eax+0x24]`). For this exact constructor's underlying `0x7CE378`, **vtable+0x24 = 0x40DFB0** again, the same zero-return leaf. Thus `0x614080` invoking either wrapper +0x04 or wrapper +0x18 on THIS object alone has **zero shared CRT calls**.
4. This proof is only for the specific `0x555D60/0x7CE378` event class, conditional on no later in-place vtable mutation. Additional queue producers and actual callback types may differ. It does not prove whether any event is queued at the first human click, nor negate the original 13 name pairs and six staff RNG calls.

Original private PE source reproduce:
```
objdump -D -Mintel --start-address=0x555D60 --stop-address=0x555DF2 footballmanager.exe
objdump -s -j .rdata --start-address=0x7CE378 --stop-address=0x7CE3AC footballmanager.exe
objdump -s -j .rdata --start-address=0x7BD564 --stop-address=0x7BD580 footballmanager.exe
objdump -D -Mintel --start-address=0x404600 --stop-address=0x404618 footballmanager.exe
objdump -D -Mintel --start-address=0x40DFB0 --stop-address=0x40DFB3 footballmanager.exe
```
**Next:** inspect the other queue producers and relevant pre-human TeamSelect state, especially those dynamically dispatched through original 0x614080, and the original manager-binder nontrivial callees; establish exact shared CRT boundaries BEFORE changing the live Windows startup stream. All 13–17 gates remain OPEN; no original execution, exact feature-branch Python tests or Win11 GUI acceptance.


### Recovery561 second queue checkpoint inside actual DBRUser initialization

The original `0x4258D0` DBRUser initializer has **a second confirmed queue dispatch location** in the normal user-creation call chain, which must be distinguished from its later TeamSelect reset:

1. `0x4258F8` first calls `0x42C400` for the thirteen DBRUser name-pair selections (26 direct shared-CRT calls).
2. `0x42599E..0x4259B5` then sets **`ECX=0x947AA8`** and invokes the SAME queue's `0x614080`, before staff registration. Thus the first user birth can encounter an event-queue callback **immediately after the 26 draws**, even before the later `0x412EF0 -> 0x614080` which occurs before the six support staff.
3. `0x4259BA` separately invokes `0x5CF830` with selected DBRUser+0x6B4 (this is a forwarding wrapper to `0x42C9F0`, not a direct bounded RNG call). These intermediate constructors and event effects must be source-audited before treating the following staff birth as exactly 26 draws after entry.
4. An original full-text x86 cross-reference search for direct calls to `0x614080` found the normal local callsites `0x4259B5` and `0x412F1F` plus queue's internal deferred recursion at `0x613F40`; thus two explicit source checkpoints lie between first user selected and the six staff factories, **with possible internal reentrancy**. This rules out treating only `0x412EF0` as the single pre-staff queue barrier.

Next: establish original first-TeamSelect queue objects on **both** calls, then original `0x42C9F0` owned manager bindings and whether those effects/other constructors advance CRT. A successful user still requires authentic source 13 name pairs + six staff, but no exact total draw count is established from these direct sites alone. Original static disassembly only, no source process or Windows11 GUI acceptance.

Reproduce:
```
objdump -D -Mintel --start-address=0x4258F1 --stop-address=0x4259C7 footballmanager.exe
objdump -D -Mintel --start-address=0x412F05 --stop-address=0x412F2A footballmanager.exe
objdump -D -Mintel --start-address=0x5CF830 --stop-address=0x5CF83E footballmanager.exe
```


### Recovery561 additional closure: the 0x5CF830 post-name cleanup has no hidden random draw

Original `0x4259BA`, immediately after the FIRST pre-staff event queue drain at `0x4259B5`, calls `0x5CF830` on DBRUser+0x6B4. Its entire body is a one-argument forwarding call `0x42C9F0`. Direct original disassembly `0x42C9F0..0x42CA5C` shows a deterministic singly linked-list cleanup: iterate nodes at +0x04, if owner nonzero reset a vtable pointer to `0x7BD5A8`, free the nested pointer and each node through `0x686FE3`, reset first/last heads to null at exit. The routine has **NO direct bounded RNG, CRT rand/srand, or independent polymorphic callback** in this bounded native path. Thus the `0x5CF830 -> 0x42C9F0` cleanup itself cannot account for extra CRT draws between 13 user-name pairs and six staff. Other calls and the two event-queue drains remain separate unresolved inputs.

Reproduce original `0x42599E..0x4259C7`, `0x5CF830..0x5CF83E`, `0x42C9F0..0x42CA5D`. No original executable was launched, no GUI acceptance, no new feature-branch test execution.


## Recovery562: exhaustive direct enqueue callsite inventory reveals nonconstant event dispatch

**Source:** same SHA256-checked original `footballmanager.exe` (833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3), original `.text` statically disassembled using `objdump -D -Mintel -j .text`; original process NOT launched. This supplements, and **restricts**, Recovery561's statement that the **one** underlying `0x555D60` class is queue-dispatch RNG-free.

### Source direct call counts and reachability boundary

A complete scan of the disassembled original `.text` gives **175 apparent direct `call 0x613EC0` enqueue sites**, **3 direct `call 0x614080` queue-drain sites** (0x412F1F before six staff, 0x4259B5 after 13 user name pairs, 0x613F40 in deferred queue processing), and **5 direct `call 0x613EE0` time-filter queue processing sites** (0x41A364, 0x41A475, 0x43216C, 0x4A8084, 0x5E3335). Counts are static opcode-callsite counts, **not** assertions that every branch executes or every apparent target is active on fresh TeamSelect.

Among the earliest distinct queued-original constructors:

| Enqueue instruction | 0x7BD564 envelope's underlying constructor | Actual underlying vtable set | Actual underlying virtual+0x24 | Bounded interpretation |
| --- | --- | --- | --- | --- |
| 0x404503 | 0x555D60 | 0x7CE378 | **0x40DFB0** | returns zero, direct RNG-free |
| 0x4045C5 | 0x587120 | 0x7D1828 | **0x40DFB0** | returns zero, direct RNG-free |
| 0x4047FE | 0x587580 | 0x7D187C | **0x40DFB0** | returns zero, direct RNG-free |
| 0x404955 | 0x554810 | 0x7CE420 | **0x40DFB0** | returns zero, direct RNG-free |
| 0x404A3D | 0x554B80 | 0x7CE3CC | **0x40DFB0** | returns zero, direct RNG-free |
| **0x409385** | original 0x57F1E0 writes actual vtable **0x7BD6BC**, then same 0x7BD564 envelope | **0x7BD6BC** | **0x5E5810**, NOT a zero-return stub | **dynamic game-object factory on callback, cannot declare RNG-free** |

The outer envelope `0x7BD564+0x04 = 0x40DFB0` returns zero, so `0x614080` normally reaches outer `+0x18 = 0x404610`, which tail-jumps via the underlying event's **actual virtual+0x24**. Sharing the SAME outer envelope **does not** establish that every underlying event is the benign 0x555D60 event.

**Concrete nontrivial source counterexample:** At original **0x409353**, while constructing/enqueuing this sixth example, a bounded CRT call `0x64D540(5)` is made and its selected result contributes to the event order/position field before `0x409385 -> 0x613EC0`. This is a real original RNG consumer in **event production**, independent of whether the event later dispatches during the first-human workflow. Its underlying callback `0x5E5810` has conditional branches for argument0/1 and allocates either a **0x490-byte or 0x494-byte game object**, invoking 0x582300 or 0x57C970 and installing original vtables 0x7CCB50/0x7CCAA0. No direct bounded RNG was observed in this bounded `0x5E5810` method; its child object constructors and later callbacks are not source-qualified as RNG-free. Do NOT flatten it into `0x40DFB0` or assume it cannot affect original game state.

**Subtlety:** 0x613EC0 can enqueue the same envelope with many other source constructors, and some producer functions may themselves draw original RNG before enqueueing. It is insufficient to classify event-queue draws solely by the `0x614080` callback's direct call list, or to treat every unqualified possible event as present during startup.

### What this actually establishes

The two real pre-staff drain checkpoints remain:
- 0x4259B5 after successful DBRUser `0x42C400` generated thirteen two-pick name pairs (26 confirmed bounded CRT draws);
- 0x412F1F before TeamSelect's six normal `0x4C9B30` staff constructors (at least 72 more direct bounded draws, variable by source choices).

Whether a particular event of the nontrivial class is present at either checkpoint depends on the **original launcher/database initialization and active event queue state**. No source observation here certifies a full 98-draw exact checkpoint or the effect of all 175 producers.

Reproduce, on authenticated original bytes, without original-process execution:
```bash
objdump -D -Mintel -j .text footballmanager.exe > /tmp/fm2001-original-x86.txt
grep -c 'call   0x613ec0' /tmp/fm2001-original-x86.txt  # 175
grep -c 'call   0x614080' /tmp/fm2001-original-x86.txt # 3
grep -c 'call   0x613ee0' /tmp/fm2001-original-x86.txt # 5
objdump -D -Mintel --start-address=0x404490 --stop-address=0x404A44 footballmanager.exe
objdump -D -Mintel --start-address=0x409322 --stop-address=0x40938A footballmanager.exe
objdump -s -j .rdata --start-address=0x7BD6BC --stop-address=0x7BD6F0 footballmanager.exe
objdump -D -Mintel --start-address=0x5E5810 --stop-address=0x5E594A footballmanager.exe
```

**NEXT source action:** trace the source normal New Game database/event/calendar pre-TeamSelect setup and actual event queue population (owner 0x947AA8) at BOTH initial user queues; classify only live-reachable event constructors and their virtual+0x24 effects, plus per-human event reentrancy, not every offline callsite indiscriminately. Investigate Cancel staff staging post-close separately. Preserve current source-only first-human CRT/SupportStart scaffolding; do not inject guessed draws, execute original EXE, assert actual Windows 11 GUI acceptance or close Gates13–17.


### Recovery562 queue-drain lifetime distinction: zero versus nonzero delegated callback

The original `0x614080..0x6140EE` control flow adds an important state/lifecycle consequence to the event-class inventory:

1. If `queueOwner+0x0C != 0`, original sets `owner+0x10=1` and returns without examining entries. Else it traverses the queue list at +0x04, snapshots each entry's next node, calls its event object's virtual **+0x04**, then its virtual **+0x18** on the return-zero or return-one path. 
2. For a return-zero original wrapper +0x04, `0x6140AE..0x6140B5` invokes its +0x18; **a nonzero callback return branches to `0x6140E5` and retains the queue node**. A zero return falls through `0x6140D9..0x6140E0` and calls `0x4EA190` to unlink the node. Thus an original queued event with a nontrivial callback can remain scheduled for later.
3. For the `0x404503/0x555D60` underlying event, delegated +0x24 returns zero via 0x40DFB0, so the original drain can unlink it. For the `0x409385/0x7BD6BC` event, delegate +0x24=`0x5E5810` may allocate an underlying object and return a nonzero pointer on supported arguments (argument0/1 source branches); **this can retain that queue entry**. It is not source-proven that either branch executes during first-manager creation.
4. The original queue is therefore an **ongoing gameplay event/retention system**, not merely a list of startup RNG callbacks to consume once. The port must preserve actual event identity, ordering, state, removal and re-entry. A scalar counter like `startup_rng_draws_per_event=0` or a blanket queue-clear operation is source-incompatible.

This behavior is verified from native static control flow. Original runtime event order, actual callback arguments and shared-CRT consumption along indirect constructors remain unknown. Do not mark the two first-user queue drains or fresh startup stream verified on this evidence alone.


### Recovery562 follow-up: exact guard/caller for the nontrivial RNG(5) event producer

Full original `.text` call xref finds **one** direct caller of underlying event producer `0x409240`: `0x41AAF1` in function `0x41AAE0`. At original `0x41AAE3`, the owner first invokes **`0x417360`**, compares the returned byte to exactly 1 (`cmp al,1`, `jne 0x41AAFA`), and only on **the accepted branch** calls `0x409240` at `0x41AAF1`. On the alternate branch, the same method looks up owner data through `0x417270`, increments `+0x1A4/+0x1A0` counters and invokes `0x41A9D0`, with no call to that particular queued event producer. Hence the source `0x409353 RNG(5)` is **conditionally gated by a game-object predicate**, not a mandatory random draw for every manager, match or queue drain. Its exact normal-start reachability still must be established from the object's dynamic owner and `0x417360` state. Do not add it to the mandatory CRT seed prefix or infer that it runs on first click.

Reproduce `objdump -D -Mintel --start-address=0x41AAE0 --stop-address=0x41AB25 footballmanager.exe`; static `.text` direct call xref `call   0x409240` occurs once at `0x41AAF1`, not including unresolved indirect vft targets.


## Recovery563: fully resolve the guarded RNG(5) producer's human-control predicate and distinct simulation call path

Authenticated original `footballmanager.exe` SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`; independently checked on the container's same binary, **statically disassembled only**. This resolves the precise predecessor of the source `0x409353 RNG(5)` discovered in Recovery562 without claiming its runtime execution.

### Exact predicate is a real-human-managed-club lookup, not an arbitrary AI/club flag

At original `0x41AAE3`, code calls `0x417360`; only when `AL == 1` does `0x41AAF1` call `0x409240`, whose producer consumes `RNG(5)` at `0x409353` and enqueues via `0x409385`.

- `0x417360` invokes `0x4172A0`, then tail-jumps to **`0x4037B0`**. `0x4172A0` reads original source object **signed WORD+0x72**, maps it to expanded `DBRClub` in `0x874B90` (0x2A8-byte club stride), or the fallback original club object `0x874B94` if the signed source index is negative.
- `0x4037B0` passes the obtained ClubRef to `0x4139E0` with global **0x874C10 original human-user registry** as `ECX`; this is not a synthetic staff or country list.
- `0x4139E0` extracts the ClubRef's original **club ID +0x04** and passes it into `0x4139F0`. `0x4139F0` walks the original linked list at **`humanRegistry+0x9CC`**, reading each `DBRUser+0x5B4` actual club pointer, comparing **`[originalClub+0x04]`** to the requested club ID and returning BOOL1 exactly on a match, otherwise BOOL0.
- Therefore the producer's actual immediate guard is: **is the club referenced by this object's +0x72 club index currently controlled by an ORIGINAL HUMAN manager?** It does NOT trigger just because a league, club, candidate group or generic event exists.

This is a strong conditional exclusion for states in which the original human-user linked list is genuinely empty. It is **not** proof that later simulation cannot enqueue the event once a human is registered, nor that any other event class is RNG-free.

### The only direct callsite is inside a separately guarded simulation/transfer allocator

Complete original `.text` direct xrefs:
- only direct `call 0x409240` is **0x41AAF1**;
- only direct `call 0x41AAE0` is **0x619F56** in source `0x619EB0`;
- original `0x619B46` and `0x619B57` each invoke `0x619EB0` with separate candidate arrays.

The `0x619EB0` routine has its OWN event-eligibility requirements, even before the human-owned-club test: the dynamic threshold at `0x821614` must not be reached; `0x947BEC` source candidate count must be nonzero; record `+0x1A0 != 5`; name/predicate `0x403E70` must pass; `0x61ABF0` must return a valid selected object; that object's original signed WORD+0x72 must equal signed WORD+0x10; then `0x41AAE0` is invoked. Source `0x619EB0` also shuffles its candidate array with `RNG(remaining_count)` at `0x619EC1` if count>1, so the pipeline can have its **OWN conditional random draws**, independent of the later `RNG(5)`.

**Runtime inference boundary:** There is no proven call from the original first-human TeamSelect input event `0x4D8E90` or DBRUser constructor `0x4258D0` into `0x619EB0`. It is a distinct data-driven allocator that may run at other game stages. The exact normal fresh game's queue contents, prior simulation state, and any pre-TeamSelect producer effects still require evidence. Do not add 0x409353's RNG(5) to a generic 'first-user fixed RNG budget' or omit possible game-season event draws when the corresponding human club predicate and other gates later pass.

### Important similarly named function is a DIFFERENT bootstrap routine

Original startup at **`0x53108D -> 0x50D390`** loads original data, then `0x531098 -> 0x66A767; 0x53109E -> 0x66950F` explicitly seeds original CRT, and at **`0x5310EB` calls `0x619F70`** before entering further application/UI setup `0x5310F0 -> 0x531400`.

**`0x619F70` is NOT `0x619EB0`.** The former builds/precalculates original 0x876CB8/0x947BE0/0x947BDC 11-field candidate/weight arrays, and its `0x619F70..0x61A0D1` disassembly has **no DIRECT RNG, rand or srand call**. The latter is the separate event-eligibility/shuffle routine with RNG and the `0x619F56` guarded producer. Conflating them could falsely assign `RNG(5)` to the first-human startup sequence just because the close-address bootstrap function is invoked before opening the UI.

This isolates a source-qualified original **seed-before-app-interface anchor**, but not the full canonical stream: intervening original functions `0x5327E0`, `0x604160`, `0x531400` and database/TeamSelect objects may consume indirect CRT. Source-first investigation must examine their reachability and two 0x947AA8 drains rather than declaring an exact seed solely from this anchor.

Reproduce source:
```bash
objdump -D -Mintel --start-address=0x4172A0 --stop-address=0x4172C3 footballmanager.exe
objdump -D -Mintel --start-address=0x417360 --stop-address=0x41736C footballmanager.exe
objdump -D -Mintel --start-address=0x4037B0 --stop-address=0x4037BC footballmanager.exe
objdump -D -Mintel --start-address=0x4139E0 --stop-address=0x413A1A footballmanager.exe
objdump -D -Mintel --start-address=0x41AAE0 --stop-address=0x41AB24 footballmanager.exe
objdump -D -Mintel --start-address=0x619EB0 --stop-address=0x619F6E footballmanager.exe
objdump -D -Mintel --start-address=0x53108D --stop-address=0x531105 footballmanager.exe
objdump -D -Mintel --start-address=0x619F70 --stop-address=0x61A0D2 footballmanager.exe
```

**Next source target:** map which original application startup operations between 0x53109E seed and 0x4D8E90 initial click can populate event queue +0x947AA8, which event classes have source virtual+0x24 side effects and how the first human linked-list and Cancel transitions govern simulation; then actual original shared CRT click-state reproduction. Continue independently original SupportStart GUI hit/Cancel linked-list provenance. No original program launched, no new branch tests or GUI acceptance, Gates13–17 remain OPEN.


### Recovery563 critical chronology correction: DBRUser is registered BEFORE the first queue drain

The native `0x413BB0` registration function also establishes a **positive-state hazard** that prevents prematurely declaring the guarded producer unreachable on the first human click:

1. `0x413BCE..0x413BF0` first checks original human list `registry+0x9CC` for a previously managed same-club ID and refuses duplicates.
2. On success `0x413BEF..0x413C15` constructs the DBRUser object with `0x424CA0`.
3. **`0x413C2F..0x413C4A` allocates a list entry and APPENDS the new DBRUser to the global human-user list via `0x617D70` with head pointer `registry+0x9C8` (first user now resides at original `registry+0x9CC`).** This executes BEFORE initializing the user.
4. `0x413C4F..0x413C54` then calls `0x4258D0` with selected club. That initializer generates 13 user-name pairs and invokes FIRST `0x614080` queue drain at `0x4259B5`.
5. On return, `0x413C5B` binds the manager through `0x426090`. Later TeamSelect invokes the SECOND `0x614080` drain at `0x412F1F`, then creates six staff. **The new human is already registered at BOTH drains** (subject to source user allocation success and no intervening list removal).

This means the `0x417360` predicate for source event `0x409353 RNG(5)` *could* pass during the first user's setup IF a queued object references that newly controlled club, the event producer's simulation criteria are met and it runs before/during the drain. It is wrong to argue that “the human list must still be empty throughout initial TeamSelect.” It was initially empty, but `0x413C44` populated it before the first queue callback. Conversely this does not make the event **mandatory** at first click: neither the producer `0x619EB0` nor a live queued event of its concrete class is source-established there.

Original registration sequence is source-proven by direct x86 static disassembly; no proprietary bytes committed or original process launched. Reproduce `0x413BB0..0x413C87`, `0x4258D0..0x4259C1`, `0x412EF0..0x412F26` and `0x417360..0x41736C`.

### Recovery563 exact startup CRT anchor, with source-only native regression check

Original startup directly calls `0x50D390` to initialize original data at `0x53108D`. Subsequently it calls `0x66A767` to obtain the original time/seed and **`0x66950F`** (srand) at `0x53109E`. The startup then calls `0x619F70` at `0x5310EB` before `0x531400` for application setup. **`0x619F70` is an allocation/precalculation routine, distinct from producer-containing `0x619EB0`; the former makes no direct calls to `0x64D540`, `0x66951C`, `0x66950F` within `0x619F70..0x61A0D1`.** This proves a starting seed-owner boundary and excludes one falsely suspected *direct* RNG source, but not any other intervening startup consumer.

A fresh local automated original-binary static audit on authenticated SHA256 bytes reported **PASS** for the direct function chain (0x4172A0 -> 0x417360 -> 0x4037B0 -> 0x4139E0/0x4139F0), the guarded producer `0x41AAE0`, source CRT seed `0x53109E`, and separate initial `0x5310EB` precompute. Source direct-call xref counts independently checked as EXACTLY ONE each: `0x41AAF1: call 0x409240`, `0x619F56: call 0x41AAE0`, `0x5310EB: call 0x619F70`. The audit did **not** execute the original EXE or the feature-branch Python tests.

**Remaining exact blocker:** determine original event class membership and timing when the new DBRUser has already been inserted but the name and six staff constructors have not completed, at `0x4259B5` and `0x412F1F`, including source cross-queue callbacks and manager binding. Then faithfully implement the same CRT lifecycle and actual PSupportStart UI/list Cancel/Apply from original evidence; Gates13–17 remain OPEN.


## Recovery563 next source step: actual global event-queue initial state is empty

Identified the original C++-style global constructor/cleanup registration for the exact queued-event owner `0x947AA8`, independently of any assumptions about a Python port:

- At original `0x6139A0`, initialization helper calls `0x6139B0`. At `0x6139B0`, ECX is loaded with exact original global queue owner **0x947AA8** and execution tail-jumps to `0x613E40`.
- The complete original constructor `0x613E40..0x613E53` writes **owner+0x00=1**, **owner+0x04=0** (first queue-node pointer), **owner+0x08=0** (last pointer), **owner+0x0C=0** (not processing). These are actual four native DWORD writes, not a guessed initial queue class.
- The `0x6139A0` initializer also registers native cleanup `0x6139D0` through `0x6681CC`; that cleanup tail-jumps to `0x613E60` for the SAME owner. `0x613E60` drains/frees remaining original queue entries through `0x4E9830` at process teardown, not during PSupportStart Cancel.
- The original PE `.data` initializer-function pointer table includes **0x6139A0** at virtual address **0x8180D0** (file offset0x4180D0), alongside many similarly registered global constructors. Thus the original queue is designed to begin **EMPTY after its initializer executes**, not as a prepopulated hardcoded list. The exact order of that initializer relative to other global constructors and any source gameplay event producers still requires normal boot call-chain verification.

**Practical narrowing:** all events seen by original first human at `0x4259B5` and `0x412F1F` must originate from subsequent source producer calls after the owner initialization, subject to legitimate lifecycle resets, not from an unexplained nonzero default at the queue's creation. This does NOT establish that the queue remains empty until TeamSelect, because original database/world/event creation contains many possible enqueue sites. No plain unconditional queue-clear or seed skip is justified.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x6139A0 --stop-address=0x6139DB footballmanager.exe
objdump -D -Mintel --start-address=0x613E40 --stop-address=0x613E54 footballmanager.exe
objdump -D -Mintel --start-address=0x613E60 --stop-address=0x613EBB footballmanager.exe
objdump -s -j .data --start-address=0x8180C0 --stop-address=0x8180E0 footballmanager.exe
```

**NEXT:** trace world/new-game/database producer reachability following this exact empty-state initializer and before TeamSelect's **two** queue-drain locations. Filter the 175 original enqueues by real call graph rather than assuming all 175 are active; focus on source actual event types which draw CRT or persist. Then integrate source-consistent user creation/staff/SupportStart Apply/Cancel/return, without premature GUI acceptance or Gate13 closure.


## Recovery564: original TeamSelect CONTINUE drains/destroys remaining global events before competition initialization

**New concrete post-user chronological boundary.** This source-native progression comes from fresh disassembly of the owner's SHA256-authenticated original `footballmanager.exe`, not a simulated Python event queue or original-process launch:

1. Original TeamSelect event callback `0x4DA480` checks its passed selected control `[arg+0x20]`. On event identifier **0x2A (42)**, its branch `0x4DA493..0x4DA4A5` obtains original screen `+0x64/+0x68` selected human/club context and calls actual new-game transition function **`0x4C41C0`**. This is **a distinct later event from the original selected-club/new-user callback `0x4D8E90`** and the editor callback `0x4D91C0`.
2. `0x4C41C0` begins new career/world setup: resets `0x8755D4`, initializes original match/calendar/session context using `0x432A20` and `0x432D20`, then resets the game owner/control lists. Importantly, at **`0x4C4263..0x4C4275`** it obtains original queue owner head **`[0x947AAC]` = `[0x947AA8+0x04]`**, pushes that head pointer and calls **`0x4E9830` with `ECX=0x947AA8`**. This is not the earlier conditional event drain at `0x4259B5/0x412F1F`.
3. Original `0x4E9830..0x4E9893` walks the supplied linked-list node through each node+0x04, and if queue owner+0x00 is nonzero and event+0x00 is nonnull, invokes that event object's **virtual+0x00 deleting destructor with pushed 1**; it frees the entire corresponding queue-node chain via `0x686FE3`, then **clears owner head `+0x04=0` and tail `+0x08=0`** if the passed head is indeed the owning first node. Because `0x4C426E` passes precisely owner+0x04, **this is a full original global-event queue clear at normal Continue**, not merely one event's conditional dispatch.
4. `0x4C42EE` then invokes `0x4E2EB0`, `0x4C42FA` shifts menu status, and at **`0x4C4304` it calls `0x413830`** (previously source-recovered precompetition initialization). Thus the explicitly cleared queue precedes 0x413830 and `0x4C4379 -> 0x4F7380` source competition grouping and source staff/youth/bootstrap `0x4C43A6` etc. The original game expects pending events to be discarded/destroyed on this transition; simply retaining prior PSupportStart/new-human queued events into original season competition setup would be wrong.
5. **A separate source gameplay event allocator `0x6194D0`** (the real upstream owner of guarded `0x619EB0 -> 0x41AAE0 -> 0x409240 -> RNG(5)` event production) has exactly TWO **direct** callsites in the entire original `.text`: `0x4A8103` and `0x4C48B8`. At `0x4A80EE..0x4A8103` the former is behind `(dateIndex+5) mod 7 == 0` weekly-calendar test, NOT initial TeamSelect selected-club callback. The latter at `0x4C48B8` occurs much later **inside the original `0x4C41C0` Continue transition itself**, after `0x413830` and team/world setup and after the explicit precompetition queue clear. Thus a source direct call to this particular `0x6194D0` allocator cannot produce its special RNG(5) event **during the earlier selected-human click before normal Continue**, unless there is as-yet-unidentified indirect/function-pointer invocation. Source direct call evidence does not rule out other enqueuers or indirect calls, nor prove an exact shared CRT first-human seed state.
6. `0x6194D0` accesses actual current human registry `0x8755E4/0x874C10` and generated game/world candidate pools. Its source `0x61955C..0x6195BC` enumerates human users, iterates actual original club object references and calls source `0x417360` human-managed-club predicate, then conditionally `RNG(10)` at `0x6195C0`. That further qualifies this routine as **human/world-session-sensitive allocator**, not unconditional pre-human original database parsing.

**Consequences for source-exact staged transaction:** The source initial user path may still have dynamic queued events at both `0x4259B5` and `0x412F1F`; only their actually reachable producers need to be audited. But by the later event0x2A Continue transition, whatever events survive those drains are explicitly destroyed/cleared before competition setup. Preserve both distinct lifecycle phases. Do not insert the special `0x409353 RNG(5)` as a mandatory first-click staff draw, and do not retain pre-Continue pending events into newly built competitions.

**Still unknown:** concrete queue population from all other source producer classes between global ctor `0x6139A0` and first-human selected click; indirect function-pointer/vft paths to `0x6194D0`; exact CRT checkpoint and native PSupportStart Cancel linked-list outcome, and true original click/host GUI. Source-only evidence, **no original executable process launched**, no exact-head Python tests, CI or physical Windows11 acceptance; Gates13–17 OPEN.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x4DA480 --stop-address=0x4DA4D5 footballmanager.exe
objdump -D -Mintel --start-address=0x4C41C0 --stop-address=0x4C438C footballmanager.exe
objdump -D -Mintel --start-address=0x4E9830 --stop-address=0x4E9894 footballmanager.exe
objdump -D -Mintel --start-address=0x4C4880 --stop-address=0x4C48E0 footballmanager.exe
objdump -D -Mintel --start-address=0x4A80E9 --stop-address=0x4A813B footballmanager.exe
objdump -D -Mintel --start-address=0x6194D0 --stop-address=0x6195C9 footballmanager.exe
```
