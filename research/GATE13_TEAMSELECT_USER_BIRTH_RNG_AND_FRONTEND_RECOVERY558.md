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
