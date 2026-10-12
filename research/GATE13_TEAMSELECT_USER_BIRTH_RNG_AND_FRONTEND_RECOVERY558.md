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
