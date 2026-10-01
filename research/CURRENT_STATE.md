# Current State

_Last reconciled: 2 October 2026 KST_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.

## Current gate

**Gate 13 - Restore original management presentation**

Gates 1 through 12 are complete. Gate 12 closed on 30 September 2026 after a
canonical real-data season reached the complete annual qualification snapshot
and atomically regenerated the year-two primary world.

Evidence:

- `research/GATE12_COMPLETION_AUDIT.md`
- `research/GATE12_ENGLISH_DOMESTIC_CUPS.md`
- `research/GATE12_EUROPEAN_COMPETITIONS.md`
- `research/GATE12_ENGLISH_DIVISIONS.md`
- `research/GATE12_ENGLISH_SEASON_TRANSITION.md`
- `research/GATE12_NEXT_SEASON_REGENERATION.md`

## Live resume summary

- **Recovery 158 PMatchInfo text producers merged:** PR #89 merged as `5603f96fddee9de4b02d40c0a199fe66eea415ca`; Gate-13 run `36934794672` passed **357 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36934794463` passed. All six bounded Zurich text producer chains, the DBTPositions player-strip source, Attendance/Ref./Mom popup lines, and bounded incident wrapper-selection predicates are canonical. The separate decimal remains only source-proven as `event_record+0x00` formatted with `%d`.
- **Recovery 158 PMatchInfo tabs/exit merged:** PR #90 merged as `ab39fd753e94c6ccfcea13ebbcd1d9576133efdb`; Gate-13 run `36935848636` passed **360 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36935848660` passed. MATCH INFO / TEAM INFO / FINANCIAL tabs, concrete embedded subpanels, default MATCH INFO selection, eCSubPanel rewiring, and the shared fmCrossButton/Escape `PostMessageA(WM_USER,7,0)` path are canonical.
- **Recovery 159 final Match Report consumer checkpoint:** exhaustive canonical-PE reference analysis proves `name_block_1..4` and `poss_back/poss_blue/poss_yellow` are loaded original resources but have **no source-proven runtime presentation consumer**. Every raw/wrapper literal xref is confined to static load/setup/teardown and the two family-wide lifetime sweeps; no PMatchInfo, Team Info, Finance or other runtime UI method references those objects or their wrapper fields. The reconstruction now fails closed instead of assigning them by filename.
- **Exact Gate-13 next boundary:** validate/merge Recovery 159, then move from PMatchInfo source recovery into intentional asset staging/import and reconstructed presentation integration for only source-proven consumers. Follow that with corrected real-Windows validation and a Gate-13 coverage audit; keep the WM_USER/wParam=7 receiver name and `event_record+0x00` gameplay meaning neutral unless separately proven.

- **Recovery 155 PMatchInfo navigation merged:** PR #85 merged as `a5c0de8aff324aa6ea8481da24da725d8921ebd4`; Gate-13 run `36924435622` passed **333 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36924435665` passed. Populated League Fixtures cells conditionally open the exact 760x500 `PMatchInfo` dialog through `0x488C80 -> 0x487580`; unresolved linked context remains a source no-op.
- **Recovery 156 PMatchInfo resource checkpoint:** the authorized 511,121,336-byte Library ZIP was freshly rematerialized and rehashed to canonical `677dcbc...a8a4`; both shipped executables reverified at `833bf95e...cc3`. The canonical executable's contiguous `Match_report` loader family now binds **20 exact original .444 resources** with firsthand SHA-256/byte-size/geometry and raw/wrapper handles. `PMatchInfoSubPanelBase` and `PMatchInfoSubPanel` RTTI are source-bound; 13 resources have direct per-control consumers mapped, while the four name blocks and three possession strips deliberately retain no invented final widget binding. Evidence: `research/GATE13_PMATCHINFO_RESOURCES.md` and `reconstruction/original_pmatchinfo_resources.py` on the active branch.
- **Exact Gate-13 next boundary:** validate/merge the Recovery-156 PMatchInfo resource checkpoint, then continue PMatchInfo control geometry/text/font/event binding for the already-owned resources. Do not infer the seven still-unmapped final consumers from filenames. Original binary asset import and integrated Windows validation remain open.

- **Recovery 154 League Fixtures selectors merged:** PR #84 merged as `501707f396aa2af7ca66dffcd7a5ecf8189c4df7`; Gate-13 run `36923762250` passed **330 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36923762398` passed. The exact eight-country `fmRadioTextSm` order/events, six RTTI-cast League controls/captions and current-club default selection are canonical on `main`.
- **Recovery 155 populated-cell PMatchInfo checkpoint:** `PLeagueGrid::0x46D390` passes a non-null matrix fixture directly to `0x488C80`. That target resolves a secondary linked context from the fixture-derived object `+0x40`; if absent it returns without opening. When resolved, it allocates `0x1828` bytes and calls `0x487580`, whose final vtable `0x7C41D4` / TypeDescriptor `0x81D058` is **`PMatchInfo`**, derived from `PExplodingDialog`. Constructor contexts are retained at `+0x70/+0x74`; dialog geometry is exact 760x500 with dynamic source-clamped origin. Evidence and fail-closed action contract are on the active branch in `research/GATE13_LEAGUE_FIXTURES_RESOURCES.md` and `reconstruction/original_league_fixtures_resources.py`.
- **Exact Gate-13 next boundary:** validate/merge the Recovery-155 PMatchInfo navigation checkpoint, then continue either `PMatchInfo` internal presentation/resource recovery or the remaining League Fixtures non-selector controls, whichever yields the stronger source-backed closure. Fixture status bit `0x20`, binary asset import and corrected real-Windows/Tk validation remain open.
- **Recovery 153 League Fixtures matrix/navigation merged:** PR #83 merged as `7381efcf9ca912d684406effc5ff3b4da1f2d1d8`; focused Gate-13 run `36922149326` passed **323 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36922149239` passed. The same-club red diagonal, 373-head fixture scan/filtering, `N*N` repeat layers, 12-club paging and 29x14 pointer navigation are canonical on `main`.
- **Recovery 154 League Fixtures selector checkpoint:** `PLeagueFixtures` source-binds eight `fmRadioTextSm` country controls and six `fmRadioTextSm` League controls. Exact country order is England (26), Germany (33), Italy (40), Spain (73), Scotland (66), France (31), Holland (24), Belgium (9), with events 1..8. `0x46D840` dynamically casts country `LeagueBase*` entries to concrete `League` through RTTI before exposing at most six source League captions from `League+0x14`; League events are 9..14. Current-club country/League identity initializes active country `+0x64` and that country's selected League index `+0x68+4*i`. Evidence and fail-closed helpers are on the active branch in `research/GATE13_LEAGUE_FIXTURES_RESOURCES.md` and `reconstruction/original_league_fixtures_resources.py`.
- **Exact Gate-13 next boundary:** validate/merge the Recovery-154 selector checkpoint, then continue only the still-open League Fixtures surrounding non-selector controls or independently identify non-null cell action target `0x488C80`. Fixture status bit `0x20` remains neutrally named. Corrected real-Windows/Tk validation and binary asset-import transport remain open.
- **Recovery 144 management-shell route merged:** PR #75 merged as `3adf75e713c70dd3a3cddf9f5df9db6e34e19b5d`. TeamSelect Start constructs `PMenu` (vtable `0x7C3DE8`, ctor `0x482830`); fresh user route state `+0x10E8=0` selects panel code `0xCE` / `PSquadScreen`, while state 1 selects `0x25A` / `PLeagueTables` and is then cleared. Gate-13 run `36907084180` passed **280 tests with 21 expected source-gated skips and zero failures**; asset-policy run `36907084140` passed.
- **Recovery 145 PMenu row-chrome checkpoint merged:** PR #76 merged as `addd82b7a8a5efddd83abb698f08d08c71ebcaf9`. It binds `PTitleMenuRow` / `PChildMenuRow` to four exact original menu-popup assets, preserves the nine-root static tree and 29-pixel row geometry, and fails closed on labels that had not yet been loader-correlated. Gate-13 run `36911756061` passed **288 tests with 21 expected source-gated skips and zero failures**; asset-policy run `36911756170` passed.
- **Recovery 146 PMenu labels/font/background-state checkpoint merged:** PR #77 merged as `2f59e163e873051a9bc691f6d6c04033f678ad20`. It resolves every modeled PMenu caption through the complete 2,714-entry English loader, binds runtime font wrapper `0x87BEA0` to imported `Fonts/Zurich_BdXCn_BT_16pixel.fnt`, preserves exact black/white row component triples and source-binds `MenuBackgroundToggle::0x47AC00` neutral bit-to-row arithmetic. Gate-13 run `36914325613` and asset-policy run `36914325533` passed on PR head `f0cb6a0b55955f2b99d79687c80734b85b5ec61b`.
- **Recovery 148 PMenu arrow-state checkpoint:** shared animation state selection is now traced through `0x652AE0/0x652780/0x6527F0`. Child `menu_anim.444` partitions exactly as 11 + 11 + 1 frames across neutral states 0/1/2. `MenuTitleArrow` overrides frame count/source offsets: `menu_arrow_anim.444` is 11 native **30x58** frames, not 22 independent 29px rows; state 0 animates frames 0..10, state 1 fixes physical frame 10 and state 2 fixes frame 0. `PMenu::0x47AB40` directly owns the embedded `CMenuList` setup but references no dedicated original resource handle in the bounded PMenu method range, so no shell-specific background image is invented. Evidence and exact arithmetic are on the active branch in `research/GATE13_PMENU_CHROME_TRACE.md` and `reconstruction/original_pmenu_chrome.py`.
- **Recovery 148 PMenu arrow-state checkpoint merged:** PR #78 merged as `f61146fa5dd644ecebbf032effda10dab60d7299` after repaired Gate-13 run `36915849517` passed **298 tests with 21 expected source-gated skips and zero failures** and asset-policy run `36915849434` passed. The first run exposed one incorrect test expectation; implementation remained aligned with the recovered same-tick transition/retreat sequence.
- **Recovery 149 Calendar/Tables/fixtures identity checkpoint:** PMenu IDs `0x259/0x25A/0x25B/0x25C` now resolve through factory `0x47AEC0` and RTTI to `PCalendar2k`, `PLeagueTables`, `PCupTable2000`, and `PLeagueFixtures` respectively. This closes the previous League Fixtures panel-identity gap but not resource/layout/result/navigation fidelity. Evidence: `research/GATE13_CALENDAR_FIXTURES_NAVIGATION.md` and `reconstruction/original_management_navigation.py` on the active branch.
- **Recovery 149 Calendar/Tables/fixtures identity merged:** PR #80 merged as `9da4c89f67aaba7b263354591497d596ca50edd1`; Gate-13 run `36916343766` passed **303 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36916343760` passed.
- **Recovery 150 League Fixtures resources merged:** PR #81 merged as `4420e2d12386b749653cbc4202cd2d3f190c1ebe`. All six exact `FM2001_Art/Generic/league_fixtures/*.444` resources are source-bound and privately hash/geometry-verified; `PLeagueFixtures::0x46AA70` places 12 vertical-grid controls at `(378+29n,98)` and 24 horizontal-grid controls at `(241,235+14n)`. Gate-13 run `36917169429` passed **309 tests with 21 expected source-gated skips and zero failures**; asset-policy run `36917169401` passed.
- **Recovery 151/152 League Fixtures cell-state/text checkpoint merged:** PR #82 merged as `cac2e5e92a6a195bf1a271e517ed90b5535f9908`. Populated fixtures use `date_fixtures_box.444` while fixture `+0x44 bit 0` is clear and `played_fixtures_box.444` once set; completed cells show exact score `"%i:%i"`, scheduled cells exact `"%02i.%02i"`, and selected row/column overlays use `toggled_fixtures_box.444`. Final focused CI/asset-policy evidence is recorded in `project_status.json`.
- **Recovery 153 League Fixtures matrix/navigation checkpoint:** the former neutral red predicate is now source-proven as the same-club self-fixture diagonal. Both 12-column and 24-row header families are RTTI-proven `ClubText` arrays; setter `0x5D5490` stores the supplied club pointer at `+0x48`, and the empty-cell branches compare those two club identities directly. Equality selects `red_fixtures_box.444`. Matrix builder `0x46D950` preserves prepared competition-member order, scans exactly 373 global fixture-chain heads, accepts only kind-code 1 fixtures for the selected competition with status bit `0x20` clear and both clubs resolvable, and stacks repeated club pairs in first-free `N*N` layers. Grid paging is exact 12-club columns; pointer mapping is exact 29x14 cell reduction. Evidence and regressions are on the active branch in `research/GATE13_LEAGUE_FIXTURES_RESOURCES.md` and `reconstruction/original_league_fixtures_resources.py`.
- **Exact Gate-13 next boundary:** validate/merge the Recovery-153 matrix/navigation checkpoint, then continue the remaining League Fixtures surrounding category/header controls and the higher-level meaning of action target `0x488C80` only if source evidence permits. Fixture status bit `0x20` stays neutrally named as a matrix-exclusion bit. Corrected real-Windows/Tk validation and binary asset-import transport remain open.
- **Recovery 143/144 TeamSelect selection closure:** the authorized 511,121,336-byte source archive was rematerialized successfully and both shipped `footballmanager.exe` copies reverified at canonical SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. The bounded `0x4D8E90` / `0x4D9240` trace resolves the former payload contradiction: the private 0x30-byte record stores displaced-manager rollback state, while the clicked row/control supplies the club directly to user creation. `0x413BB0 -> 0x4258D0` binds that club at user `+0x5B4`; deselection removes the user and restores the prior manager state. Multiple selected clubs/users are source-proven, with `0x4DA4D0` enforcing a hard global cap of six plus a manager-availability condition. Start consumes the already-created user list and does not translate the private record into a club ID. Evidence: `research/GATE13_TEAMSELECT_USER_SELECTION_TRACE.md`.
- **PR #74 TeamSelect selection closure merged:** `38b8daedcc85ba5f875aca075ad6c9ea852bcd7a`. Final Gate-13 run `36905637324` passed **276 tests with 21 expected source-gated skips and zero failures**; asset-policy run `36905637224` passed. The corrected real-Windows graphical audit remains open because Recovery 138 predates this behavior.
- **Earliest incomplete validation gate:** Gate 13.
- **Recovery 142 private execution boundary:** this recovery initially restored one trivial shell process, then successfully rematerialized the canonical 511,121,336-byte Library source ZIP. Every subsequent shell launch, the independent Python execution path, and a later trivial shell reprobe failed before process start with `caas.internal.errors.ClientError`. No new original-byte hash, TeamSelect payload behavior, or upgraded Windows graphical result is claimed from Recovery 142. The exact private next action remains the bounded `0x4D8E90` / `0x4D9240` selection-record and Start-resolution re-trace, followed by the upgraded real-Windows audit.
- **Recovery 142 Gate-14 work-ahead:** PR #71 merged as `ea1e7c6bb25c35243a992c4a33d02038ddb3abc3`. The original startup-media contract now also defines deterministic, non-overwriting FFmpeg conversion plans and strict FFprobe validation for MP4/H.264/AAC derivatives while retaining the exact TGQ source hashes, 320x480 geometry, 25 fps timing, decoded frame counts, and 22,050 Hz stereo audio. Full reconstruction run `36897544475` passed **1,149 tests with 22 expected source-gated skips and zero failures**; asset-policy run `36897544592` passed. This closes only the repository-side conversion contract: no actual TGQ conversion, playback, skip-key, fade, scaling/interlace treatment, or Gate-14 completion is claimed.
- Local Codex recovery on 2 October closed the source-critical TeamSelect
  hierarchy implementation: exact root-league filtering and stable ordering,
  raw-name club ordering, all league/team native frame transforms and Zurich
  18/16 row captions are integrated. Four exact resources were imported through
  the verified inventory path. The interrupted trace's claim that
  `DBRClub+0x40` is a canonical club ID conflicts with earlier verified
  evidence mapping that field to manager ID/reference, so club-row ACTIVE/toggle
  state is retained but gameplay club selection remains fail-closed pending a
  bounded payload re-trace.
- The upgraded real-Windows audit is ready and now checks the 13-row English
  default, 20 Premier League clubs, country clear, league repopulation and
  club ACTIVE/toggle state without promoting the unresolved payload into the
  gameplay backend. Rerun it with the same Tcl/Tk-capable Windows Python used
  by Recovery 138; the interrupted Codex attempt happened to use a bundled
  Python lacking a usable `init.tcl`.
- Recovery 141 hardened the unresolved TeamSelect identity boundary in PR #69,
  merged as `74f5b626f07f6da5d15fd6c4795a1a37f5a56411`. The native
  presentation model now names its provisional value
  `selected_club_record_index`, while the gameplay session alone owns
  `selected_club_id`; the developer-only explicit backend picker no longer
  synchronizes those values by numeric coincidence. Focused Gate-13 run
  `36889927015` passed 273 tests with 21 expected source-gated skips and zero
  failures; asset-policy run `36889927306` passed.
- Recovery 141 successfully materialized the pinned source and persisted runtime
  ZIPs, but both the next shell launch and the independent Python execution path
  then failed before process start with `caas.internal.errors.ClientError`.
  No private TeamSelect payload behavior or upgraded Windows graphical result is
  claimed from this allocation. The exact private next action remains the
  bounded `0x4D8E90` / `0x4D9240` selection-record and Start-resolution
  re-trace, followed by the upgraded Windows audit.
- Recovery 141 also removed the last synthetic secondary bucket geometry from
  the Gate-15 startup RNG checkpoint. PR #70 merged as
  `cb0df0d50b7e1348e9c75b2dfa452f533dd26bed`: the proven 262 secondary
  nodes / 45 nonempty buckets now advance the MSVC hidden state through an
  aggregate-only `217`-draw checkpoint, with impossible aggregate shapes
  rejected and no invented per-date bucket vector. Full reconstruction run
  `36890779450` passed 1,146 tests with 22 expected source-gated skips and zero
  failures; asset-policy run `36890778875` passed. Exact per-date mode-1 bucket
  contents and the complete equal-key native qsort permutation remain open
  source questions rather than test fixtures.
- Recovery 141 reconciled the Gate-13 resource coverage, management-screen
  evidence ledger and presentation-separation audit after the TeamSelect/Squad
  source work (`d8f13f97f9cd8f25aeb8c9120e8ec0c6a9dfbaa5`,
  `f5f07ff43d132673072b7fabd87cb15a925116a7`,
  `5e6e7901cc1004ec55e3a776814b4619b9e4b14a`). They now explicitly mark
  the 20-row Squad bindings and FormationText state mapping as complete, and
  narrow TeamSelect to the selection-record/Start identity plus upgraded
  Windows audit. Older instructions to re-recover those completed slices are
  superseded.
- Local Codex recovery at `4537f9b150cab8e2282c5d33a30c13a43cfb50c3`
  completed the concrete Squad player-list hierarchy, 20-row/column/status
  bindings and exact `FormationText` state-to-source-row transform. Do not
  repeat that private trace unless a regression or evidence dispute requires it.
- Gate 13 still requires the upgraded **real Windows PStartMenu/TeamSelect
  graphical audit** and broader normal-management presentation/resource/
  layout/navigation work.
- The Windows first-screen audit harness is merged at
  `0a871b5fbc9c546ad67c335bc6db009d3a023627`; a hosted harness pass is not a
  substitute for the real Windows receipt.
- Cloud-safe Gate 14 groundwork began at `e54cc8591df91bbc949856ed241fcffcedd5fe97` and now includes the verified conversion contract merged at `ea1e7c6bb25c35243a992c4a33d02038ddb3abc3`. The source-backed startup-media contract, deterministic conversion/probe boundary, and read-only match-presentation event feed are foundations only; Gate 14 is not complete.
- Cloud-safe Gate 16 work-ahead now includes the 30-rollover destructive annual
  regeneration soak (`abe0876f240cdac1f3b135869a2f5b11b9c0d953`), six-seed
  complete-season stress (`f08a014bc73c8ca4a7e11e3f10ef79e42ca13e62`), three
  consecutive fully played synthetic seasons (`3d6037d71365a2ddce53d2e6b40eda9baa02cf93`),
  five exact save/reload round-trips across those seasons
  (`73ca421609cc6e929156c72f5b021b02a6efca3b`), a five-year autonomous
  transfer-churn/state-growth stress (`71676cb9a5b5b89b60b037c8f4426dc72a58e682`),
  and the mixed shared-primary scheduler stress merged at
  `24447d846b96fe68d2eba7c17d0053de638e43ef`. The mixed stress executes 33
  retained-order entries across Premier League, domestic Cup, European Cup,
  qualification Cup and procedural League owners in one long synthetic
  calendar. Its first CI run exposed an invalid two-club stress fixture rather
  than a production defect; the repaired 20-club fixture passed full
  reconstruction run `36846018068`: 1,132 tests, 22 expected source-gated
  skips, zero failures. Asset-policy run `36846018016` passed. The production
  fail-closed dynamic FA Cup replay insertion boundary remains unchanged.
  The annual replacement path is also now combined with 12 exact internal
  save/reload round-trips in PR #59, merged as
  `a9ec833173a92a4b8b3c2238d91943c159f7fa92`. Final reconstruction run
  `36847418060` passed 1,133 tests with 22 expected source-gated skips and
  asset-policy run `36847418038` passed. Across all 12 cycles, replaced
  season-owned structures retain one stable shape and compact JSON payload size
  stays within a 4 KiB max-minus-min corruption guard. Canonical real-data
  multi-season evidence, more seed coverage and remaining state-growth risks
  stay open.
- The five-year autonomous-transfer churn now also survives yearly internal
  game-state round-trips at weeks 52/104/156/208/260. PR #60 merged as
  `c640e5cb7dad46926e67a35caa34b83deb99c2cf`; final reconstruction run
  `36849081411` passed 1,134 tests with 22 expected source-gated skips and
  asset-policy run `36849081409` passed. The periodically reloaded run matches
  a never-reloaded run from the same seed across the full movement history,
  rosters, counters, RNG state and final date.
- **Exact next task:** Gate 16's present roadmap criteria are now prevalidated
  by the synthetic stress suite plus two passing canonical shipped-data
  three-rollover seeds. Do not mark Gate 16 complete before earlier gates close.
  The secondary startup checkpoint is now honestly aggregate-only with no
  invented bucket vector. The remaining Gate-15 task is to recover the exact
  equal-key permutation and mode-1 per-date bucket shape from the canonical
  executable/real input when sustained private execution returns; do not infer
  those details from the aggregate checkpoint.
- **Recovery 133 execution blocker:** the fresh allocation launched one trivial
  shell process successfully, but direct `git clone` could not resolve
  `github.com`. The GitHub connector remained healthy and the canonical
  511,121,336-byte Library disc archive was materialized into the execution
  workspace. Immediately afterward every further shell launch and the
  independent Python execution path failed before process start with
  `caas.internal.errors.ClientError`. No canonical season was executed in this
  recovery, no source hash was re-claimed from the failed process path, and no
  new original-behavior assertion is promoted.
- **Recovery 134 runner/bootstrap checkpoint:** the fresh allocation failed
  before its first shell process with `caas.internal.errors.ClientError`, so
  the canonical private run still could not execute. Cloud-safe work produced
  `reconstruction/canonical_multiseason_audit.py`, merged through PR #63 as
  `c12df0dde85bb477392c25b97f8b9ca3254b2837`. It repeats the proven annual
  qualification boundary on one live controller and fails closed on incomplete
  PL state, invalid roster/membership references, RNG or membership commit
  drift, dropped played qualification Leagues, duplicate/missing scheduler
  fixtures, or growth in the fresh season-owned structural shape. Full CI run
  `36857099351` passed **1,138 tests with 22 expected source-gated skips and
  zero failures**; asset-policy run `36857099441` passed.
- Recovery 134 also removed the in-container Git/DNS transport dependency. The
  successful Recovery-132 Actions artifact was downloaded and persisted in the
  user Library as
  `/FM2001/Working Runtime/FM2001-reconstruction-runtime-120400bd.zip`
  (688,773 bytes; Actions artifact digest
  `sha256:9167302c608882161954109d617824422671d2999d69006bff5d662adeb2c4d6`).
  Its `reconstruction/` contents are from merge-base
  `120400bd1ce25e449897e927e00dfa9f945076eb`; comparison through Recovery-133
  main showed only research/status changes before PR #63, so the engine code is
  the current pre-runner runtime. The ZIP does not contain the newly merged
  multi-season runner itself.
- **Next executable action:** keep the canonical shipped-data multi-season
  Gate-16 audit as the next task. On the next healthy sustained execution
  allocation, materialize both the pinned canonical disc archive and the
  Library runtime ZIP before launching a shell, extract them outside Git, add
  the now-canonical `canonical_multiseason_audit.py` from current `main` (or
  invoke its equivalent temporary orchestration against that runtime), recheck
  the pinned canonical source hashes, and run at least three consecutive
  qualification/regeneration cycles. Persist the JSON evidence and convert any
  discovered failure into a regression before continuing.
- **Recovery 134 final execution boundary:** after the runner/bootstrap
  checkpoint, Files successfully materialized both persistent inputs into the
  workspace (`fm2001-source.zip`, 511,121,336 bytes; `fm2001-runtime.zip`,
  688,773 bytes). An independent user-visible Python execution path then also
  failed before process start with `caas.internal.errors.ClientError`. Together
  with the first shell failure, every available process-execution route in this
  allocation is unusable. The blocker is therefore execution infrastructure,
  not source availability, runtime transport, GitHub access, or missing audit
  code. No canonical multi-season result is claimed.
- **Recovery 135 canonical execution:** the fresh allocation restored sustained
  shell/Python execution. The authorized source ZIP and persisted runtime ZIP
  materialized, all 268,549 raw MODE1/2352 sectors validated, the four pinned
  canonical data/string SHA-256 values matched, and the current multi-season
  runner blob matched GitHub. The seed-1 three-rollover run then failed closed
  on cycle 2 after about 22 minutes: fresh shape
  `(380,380,5735,9344,291,371,311,13)` became
  `(380,380,5737,9346,291,373,311,13)`. The isolated +2 change is in European
  Cup nodes and their corresponding shared-primary/shadow entries; Premier,
  domestic Cup, qualification Cup and procedural-League counts stayed stable.
  This is now a real Gate-16 investigation, not an infrastructure blocker.
- **Recovery 137 canonical seed-1 pass:** PR #65's corrected current-regeneration
  projection guard passed asset-policy run `36867367968` and full reconstruction
  run `36867368043`, then merged as
  `7f3f83eb98b9f29039b691197505dbe74c8b0851`. The exact authorized shipped-data
  seed-1 audit completed three consecutive annual qualification/regeneration
  cycles with exit code 0 in 1,617.49 seconds, ending 2003-06-02. All three
  cycles completed 380 Premier League fixtures and passed roster, membership,
  RNG, scheduler and current-regeneration projection invariants. The legitimate
  cycle-2 UEFA Cup shape variation remained bounded rather than accumulating.
  Machine-readable evidence is
  `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED1_RECOVERY137.json`.
  Recovery 137 has started the same three-rollover canonical audit with player
  seed 2 for additional real-data seed coverage.
- **Recovery 137 canonical seed-2 pass and Gate-16 readiness:** the second
  shipped-data player seed also completed three consecutive annual cycles with
  exit code 0 in 1,440.49 seconds, ending 2003-06-02. Its fresh European-Cup
  node counts (367, 371, 371) differed from seed 1 but every installed schedule
  projected exactly from that cycle's regeneration; no stale accumulation was
  observed. Evidence is
  `research/evidence/GATE16_CANONICAL_MULTISEASON_SEED2_RECOVERY137.json`.
  `research/GATE16_READINESS_AUDIT.md` now records all four Gate-16 completion
  criteria as prevalidated by work-ahead. Gate 16 remains formally incomplete
  until earlier gates close and the then-current runtime is re-audited.
- Gate 17 release-readiness evidence is now fail-closed and machine-checkable at
  `9e7cb18be721ea2ae89b074991e120d3e60e4c68`; it intentionally cannot pass
  without real clean-Windows receipts, a release archive and final limitations.
- If Windows/private execution is unavailable, preserve those Gate-13 blockers
  and continue the highest-priority independent cloud-safe work. Do not mark a
  blocked criterion or later gate complete merely because work-ahead exists.

**Resume rule:** this live summary and the current `agent-runtime` marker
supersede historical "exact next task" wording in older recovery sections below.

## Historical local recovery: Squad resource ownership correlated

- Resumed clean canonical main
  `cad50f8d9fa45f57608971db3eff5f2bbc817d47`. The authorized ZIP and private
  executable re-verified at their pinned SHA-256 values before analysis.
- The saved whole-disc catalog's four exact Squad candidates were traced
  through exact path literals, `0x64D750` resource handles, `0x64E500`
  wrappers, consumers and RTTI-backed presentation owners.
- Distinct general panel identity is now proven: `PSquadScreen` TypeDescriptor
  `0x819D48`, vtable `0x7C5CA4`, setup method `0x4B5720`.
  `squad_but_anim.444` is used at exact origins `(37,92)`, `(113,92)` and
  `(189,92)`.
- `squad_bars.444` and `squad_form_anim.444` belong to `FormationText`, a type
  embedded by `PSquadPitch`. `blue_toggle.444` is shared by `PFormation2k`,
  `PSCFTitle`, `PTraining` and `PYouthTeam`; it is not `PSquadScreen` evidence.
- All four exact resources are provenance-imported. A fail-closed contract and
  tests lock hashes, native header sizes, owner boundaries and recovered Squad
  button origins. See `research/GATE13_SQUAD_RESOURCE_CORRELATION.md`.
- The three top controls are now source-bound end-to-end: IDs 3/4/5, object
  offsets `+0x37A4/+0x37F8/+0x384C`, origins `(37,92)/(113,92)/(189,92)`,
  label globals `0x982110/0x98210C/0x982108`, and English.idx entries
  2490/2491/2492 resolving exactly to `1ST & RES`, `1ST FORM`, `RES. FORM`.
- The surrounding view transition is now exact. Embedded `CBasePlayerList`
  panels are `(37,0,228,520)` and `(418,0,228,520)`; `PSquadPitch` is
  `(388,92,412,432)`. Events 3/4/5 switch first+reserve / first+pitch /
  reserve+pitch by rebinding the left list, toggling native mask 1 on the
  second-list and pitch containers, and selecting pitch team index 0 or 1.
- `PSquadPitch::0x4B3C80` supplies all 22 `FormationText` rows: paired 23x16
  form cells at x=279 and 81x16 bars at x=303, y=`25+17*i`, control IDs
  12..55. Wrapper initializers independently prove both frame sizes.
- **Superseded next-task note:** the player-list row/column/status bindings and
  `FormationText` state/frame selection were later completed by local recovery
  at `4537f9b150cab8e2282c5d33a30c13a43cfb50c3`. The remaining Gate-13 boundary
  is the real Windows PStartMenu/TeamSelect graphical audit, TeamSelect
  hierarchy input/state recovery and broader management-screen fidelity.

## Recovery 127: fresh worker cannot launch first private process

- Resumed canonical `main` at
  `9fc09f2327d4bf1a18c2690bfa97c4756d3616a2`. The only commit after Recovery
  126 is the v0.4.1 auto-continue detector hardening; it does not supersede or
  alter the active Gate-13 Squad source task.
- This fresh worker attempted the required execution path immediately. The
  **first** shell process failed before process start with
  `caas.internal.errors.ClientError`; unlike Recovery 126, this allocation
  never reached a usable Python/Git process.
- The canonical private source location, executable hash, prepared
  `reconstruction/gate13_squad_source_trace.py`, and all previously proven
  Squad ownership/caption/geometry/transition evidence remain unchanged. No
  `CBasePlayerList` row/column/status semantics and no `FormationText`
  state-to-frame semantics are promoted from this recovery.
- Safe repository-only fallback work for this exact subtask is exhausted: the
  missing facts require private canonical-executable control/data-flow
  adjudication, and committed evidence explicitly forbids inferring them from
  resource dimensions, filenames, or visual guesses.
- Exact next action: in the next allocation that can launch sustained private
  processes, synchronize to canonical `main`, recover/verify the canonical
  executable SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
  run the existing Squad trace, and manually adjudicate the two
  `CBasePlayerList` bindings plus `FormationText` value-to-frame transform.
  Only then promote source-backed bindings and continue to the mandatory real
  Windows PStartMenu/TeamSelect graphical audit and remaining management
  screens. Gate 13 remains active.

## Recovery 126: private source recovered; sandbox failed after first process

- Resumed canonical main `14a7b47b3328475f8218350c0fc03e7786e4537b`.
  A direct Git tree read confirmed that SHA as the current `main` tree, and the
  `agent-runtime` handoff still names the same unresolved Gate-13 task.
- The canonical private source ZIP was resolved again at Library file
  `file_00000000010c8209961739423e78473b`, size **511,121,336 bytes**, and
  materialized successfully in the fresh worker workspace. This is therefore
  not a source-availability failure.
- The fresh execution allocation initially launched one trivial shell process
  successfully (`Python 3.13.5`, `git 2.47.3`). Every later shell and Python
  process then failed before process start with
  `caas.internal.errors.ClientError`.
- Because sustained private execution was unavailable, this recovery could not
  safely synchronize a local clone, extract/verify the canonical executable,
  run `reconstruction/gate13_squad_source_trace.py`, or adjudicate native
  control/data flow. No new `CBasePlayerList` row/column/status meaning or
  `FormationText` frame/state meaning is claimed.
- Exact next action remains unchanged: on the next execution allocation that
  can sustain private processes, use the first working process to synchronize
  canonical main and run the prepared Squad trace against the independently
  verified executable, then manually adjudicate the two player-list bindings
  and FormationText value-to-frame transform before promoting anything.
  Afterward perform the mandatory real Windows PStartMenu/TeamSelect graphical
  audit and continue remaining management-screen correlations. Gate 13 remains
  active.

## Recovery 125: fail-closed Squad native trace prepared; cloud execution blocked

- Reconciled canonical main after the worker-recovery hardening commit
  `0599c15b7064865a239614db213d0873a3460a93`; that commit changed only the
  auto-continue sandbox-failure handling and did not supersede the active
  Gate-13 Squad source task.
- The canonical 511,121,336-byte private source ZIP was resolved at the durable
  Library identity and materialized successfully in this recovery.
- Both trivial shell execution and Python execution then failed before process
  start with `caas.internal.errors.ClientError`. No new original executable
  bytes, disassembly, row bindings, status semantics or frame meanings are
  claimed from this worker.
- PR #48 added `reconstruction/gate13_squad_source_trace.py`, a checksum-gated
  private trace pinned only to the already-proven `CBasePlayerList`,
  `FormationText`, `PSquadPitch` and `PSquadScreen` anchors, plus synthetic
  regression coverage and `research/GATE13_SQUAD_SOURCE_TRACE_PROCEDURE.md`.
  The tool explicitly leaves row/column/status meanings and state-to-frame
  semantics unresolved until manual native control/data-flow adjudication.
- PR #48 Gate-13 run `36822999900` and repository asset-policy run
  `36822999889` both passed. It squash-merged to main as
  `cf2b5c18a18a2b05f061d41e2c39a5363a8f643b`.
- Exact next action: on the next working private/local execution path, run the
  new Squad trace against the independently verified canonical executable,
  adjudicate `CBasePlayerList` row/column/status reads and `FormationText`
  value-to-frame selection, then promote only directly proven bindings into the
  Squad contract/tests. After that, perform the mandatory real Windows
  PStartMenu/TeamSelect graphical audit and continue remaining management
  screens. Gate 13 remains active.

## Recovery 123: native menu captions + Scouting composition verified

- PR #47 was squash-merged as
  `757e8fec77f688bab893e155fee0bb82eaa97b6f`.
- The developer first-screen view now draws the recovered PStartMenu Zurich
  glyph alpha at the exact native line origins. Manual source-frame inspection
  uses the recovered source-frame -> Button group mapping, so caption color
  follows the proven native endpoint value for that group.
- The live debug conversion remains deliberately narrow: only native
  `0x0000` (all bits off) and `0xFFFF` (all bits on) are mapped to modern
  black/white RGBA endpoints. No generic 16-bit color-channel layout is
  invented.
- Added a fail-closed `PScouting2K` source-resource composition module.
  `background_alpha_1.444` is independently checked as **571x16** and placed
  at x=207 for 20 rows y=192..515 in 17-pixel steps; `background_2.444` is
  **295x45** at (206,543). The module composes only that proven transparent
  fragment and does not invent the unknown surrounding Scouting screen,
  captions, controls, result text, navigation or row semantics.
- Hosted focused Gate-13 run `36814179046` passed **249 tests with 20
  expected original-source-gated skips and zero failures** on PR head
  `2ba43f19ed29e16a609f20d03eeacef6790cf342`. Repository asset-policy run
  `36814179303` passed.
- A fresh cloud shell/Python process probe still returned `ClientError`
  before process start. The four exact private Squad catalog candidates were
  deliberately not persisted, so their panel ownership cannot be inferred
  safely from filenames in this environment.
- Exact next Gate-13 work: on the next working private/local execution path,
  correlate **one Squad resource to its actual panel owner** from the saved
  whole-disc catalog + canonical executable, then expand that evidence outward
  without guessing. In parallel/afterward, run the real Windows graphical
  PStartMenu/TeamSelect audit using the now-integrated native captions and
  source-backed controls. Gate 13 remains active; Gates 14-17 and the verified
  Windows 11 release remain mandatory afterward.

## Recovery 120: canonical Button/Zurich trace and ten-resource import complete

- Local Windows execution resumed from clean canonical main
  `c36b7047dbcfc1f99a916a9997debb706ec08eb0` after fetching and
  fast-forwarding the local clone without discarding user work.
- The authorized 511,121,336-byte ZIP matched canonical SHA-256
  `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
  The privately extracted `footballmanager.exe` matched
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
- Capstone 5.0.9 ran privately outside Git. The fail-closed TeamSelect RTTI
  canary recovered TypeDescriptor `0x81EC10` and vftable `0x7C7650`.
  Constructor writes then corroborated the sole `Button@ease_2001` candidate:
  TypeDescriptor `0x81AD90`, COL `0x7E0B90`, CHD `0x7E0B80`, vftable
  `0x7BF4CC`.
- Native Button mapping is implemented and tested: enabled/mask-4-clear group
  0 uses frames `0..10`, enabled/mask-4-set group 1 uses `11..21`, and disabled
  group 2 uses frame `22`. Pointer-inside mask `0x8` advances the group
  subframe; outside retreats it. The mask-4 group's user-facing name remains
  deliberately unresolved rather than guessed as pressed.
- Zurich Button captions are source-bound: style `0x2000`, centered native
  21-pixel line, zero offsets, `0xFFFF` for groups 0/2 and `0x0000` for group
  1. PStartMenu line origins are `(234,480)`, `(33,480)`, `(399,480)` and
  `(205,510)` for Continue, Start New Game, Load Game and Quit to Windows.
- The strict exact ten-resource selection and firsthand source audit passed.
  All ten files are imported individually under `original_assets/source/`
  with canonical hashes and provenance. The post-import readiness and
  repository asset-policy guards pass. No archive, executable, disc image,
  private raw report or uncontrolled dump entered Git.
- Durable evidence: `research/GATE13_BUTTON_NATIVE_TRACE.md`.
- The whole-disc management catalog audit also ran. `PScouting2K` setup method
  `0x4AB150` now proves the exact ownership and geometry of
  `background_2.444` and `background_alpha_1.444`; both resources are imported
  with provenance. The private exhaustive correlation reports remain outside
  Git. See `research/GATE13_MANAGEMENT_SCREEN_EVIDENCE_LEDGER.md`.
- Exact next Gate-13 work: integrate the native first-screen captions, decode
  and test the proven Scouting composition, correlate a Squad resource to its
  panel owner, then perform the real Windows graphical first-screen and
  normal-play audit. Gate 13 remains active; Gates 14-17 and the verified
  Windows 11 release remain mandatory afterward.

## Recovery 104: verified Squad contract; source present, byte execution still blocked

- Fresh fallback recovery resumed canonical main
  `da23cf50e3a250dbe3c43a5c97533fd7f2537741`.
- The canonical private 511,121,336-byte authorized source ZIP was re-listed at
  the exact durable Library location and successfully materialized into the
  current workspace. Source availability is therefore independently confirmed
  in this recovery.
- Execution did **not** become reliably usable. One initial trivial shell probe
  succeeded, but the repository clone/file-access command, subsequent trivial
  shell probes and private Python execution all returned `ClientError`.
  Therefore no new Button RTTI, Zurich render, ten-resource physical audit,
  executable disassembly, pixel inspection or source import is claimed.
- PR #45 was merged at
  `de3091f7102d178aafb5604b3eeca2561bf04a97`. The read-only Gate-13
  presentation seam now preserves only already-proven Squad backend state:
  ordered team roster IDs at `+0x244` / count `+0x294`, participant
  collector `0x510CD0`, active/substitute predicates
  `0x417F50` / `0x417F60`, DBRPlayer `+0x14` flags
  `0x10` / `0x20`, setters `0x4182F0` / `0x4182C0`,
  removal helper `0x4181B0`, and preservation of live roster iteration
  order. It deliberately claims no original Squad screen class, row sort,
  columns, geometry, artwork, controls or navigation.
- Verification on PR head
  `db7c463dcfb482bdea938798ba9e545888a53bf4`:
  - focused Gate-13 run `36780212525`: **238 tests, 19 expected
    original-source-gated skips, zero failures**;
  - full reconstruction run `36780212535`: **1,074 tests, 21 expected
    original-source-gated skips, zero failures**;
  - repository asset-policy run `36780212608`: passed.
- The manager-home / remaining-screen fallback inventory is now complete in
  `research/GATE13_MANAGEMENT_SCREEN_EVIDENCE_LEDGER.md`. It records the
  evidence level for every named roadmap surface and proves an important
  negative boundary: Manager Home has no persisted original panel identity,
  while several other areas have backend/event identities but not screen
  identities. Source-module names and filename hits are not promoted to
  screens.
- PR #46 was merged at
  `ca7f6cfd9c5fae01ac9c454ad14603076979262b`. The new
  `gate13_management_catalog_audit.py` makes the ledger's whole-disc path
  queries repeatable and marks every candidate `binding_proven = false`.
  Focused Gate-13 run `36781127596` passed **243 tests with 19 expected
  source-gated skips and zero failures**; asset-policy run `36781127819`
  passed. The full reconstruction workflow was intentionally not triggered for
  this isolated catalog/reporting tool; PR #45 remains the latest full baseline
  at **1,074 tests / 21 expected skips / zero failures**.
- A fresh post-merge shell probe still returned `ClientError` before it could
  even `stat` the already materialized private ZIP. The safe source-backed
  fallback work identified by the prior handoff is therefore exhausted.
- Exact next Gate-13 action: when private execution works, run the canonical
  TeamSelect RTTI canary -> native Button state/23-frame trace -> Zurich
  placement/color trace -> strict ten-resource source audit/import, then run
  the saved management catalog through the verified screen-family audit and
  correlate exact resources/layout/navigation outward through normal play.
  Until execution or Windows graphical access returns, do not invent further
  presentation semantics. Gate 13 remains active; Gates 14-17 and the clean
  Windows 11 release remain mandatory afterward.

## Recovery 101: Gate 13 resource-coverage audit and execution blocker

- Resumed from canonical main `9bb117f9403821982c112d649305cb0121cd1c4d`.
- Reconciled the newer PR #33 full hosted integration baseline: run
  `36760160986` passed **1,050 tests with 21 expected original-source-gated
  skips and zero failures** on `818e91033ba0cb7f2c912c67badf58f06f38f098`.
- The presentation/simulation separation criterion is already independently
  audited and checked in `ROADMAP.md`.
- Re-resolved and materialized the canonical private 511,121,336-byte source
  ZIP from the durable Library location. The source is present, but both a
  trivial shell command and a trivial Python command still fail with
  `ClientError`; no new original-byte execution is claimed.
- Added `research/GATE13_RESOURCE_COVERAGE_AUDIT.md`. It confirms that the
  resource criterion remains OPEN: first-screen source evidence is strong, but
  the ten pinned first-screen files are not yet a completed provenance import,
  and manager-home through remaining screens still lack completed original
  resource/layout/navigation correlation.
- Exact next task remains the canonical original-byte Button/Zurich/ten-resource
  path as soon as execution works. While it does not, only source-backed
  Gate-13 audits/data/presentation preparation may continue; do not invent
  screen semantics. Gates 14-17 and the clean Windows 11 release remain
  mandatory after Gate 13 closes.

### Verified PScouting2K presentation contract

PR #35 was merged at `5a4224e651b4b4a7051eb3afe1e5f4b8d8aff44e`.
It promotes only prior firsthand canonical-executable evidence into the
read-only Gate-13 presentation seam: `PScouting2K` RTTI/vtable identity,
search event **31**, the deterministic panel-state reseed path, and all six
native result-sort comparator modes/directions. It deliberately defines no
original on-screen captions, screen/control IDs, rectangles, artwork, font
placement or navigation that have not been recovered.

Verification on the PR head `96cf4c7fbf95cb86af261f4e0289104493db7b85`:

- focused Gate-13 run `36767384902`: **219 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36767384882`: **1,055 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36767384938`: passed.

This narrows Scouting interaction/sort fidelity but does not close Gate 13's
resource, first-screen fidelity, or normal-play visual criteria.

### Verified first-screen provenance readiness guard

PR #36 was merged at `947fc7d26e6383a7da15113994baf858a44dd609`.
The new fail-closed end-state audit requires all ten pinned first-screen source
originals to be present at their canonical `original_assets/source/` paths,
manifested as byte-identical originals with the independent source SHA-256, and
still hashing to those same bytes.

Focused Gate-13 run `36768095800` passed **226 tests with 19 expected
original-source-gated skips and zero failures**. Repository asset-policy run
`36768095889` passed. The immediately preceding full integration baseline
remains run `36767384882`: **1,055 tests, 21 expected source-gated skips,
zero failures**.

The actual current repository is intentionally **not** declared first-screen
provenance-ready: the private-byte execution blocker still prevents the strict
physical ten-resource audit/import, and the manifest is therefore incomplete
for this guard.

### Verified tactics / Team Orders presentation contract

PR #37 was merged at `c43ce7d308c187ea9ee82698abba1c82e7af5896`.
The read-only Gate-13 presentation seam now retains the already-proven
`PFormation2k` five-record formation family and the `PTeamOrders2K`
captaincy / penalty / corner / free-kick priority categories with original
English-string corroboration. Team Orders RTTI addresses that were recorded as
neighborhood anchors remain explicitly non-canary anchors until private PE
execution returns.

Verification on PR head `eaf5bb05578eed482ba353ce3924f2fb7d89ed4a`:

- focused Gate-13 run `36768744626`: **227 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36768744640`: **1,063 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36768744578`: passed.

No original tactics control IDs, geometry, art paths, gestures or navigation
are claimed. The tactics visual/resource part of Gate 13 remains open.

### Verified PTickets presentation contract

PR #38 was merged at `cca08a22f33aebfab230afd6ced70e28bf552c10`.
The read-only Gate-13 presentation seam now preserves the already instruction-
locked `PTickets` state identity, exact ticket-object layout, terrace/seating
price attribution, recommendation helpers/comparison sites, and all 26 native
section-state values. The controlled club's existing `TicketRuntimeState`
is exposed through a fail-closed read-only view.

Verification on PR head `92d9d0322fd2ff0a9403a66190591438d025527f`:

- focused Gate-13 run `36769405085`: **230 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36769405053`: **1,066 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36769404960`: passed.

No original PTickets widget IDs, visible caption bindings, geometry, artwork,
font/color rules or navigation are claimed. The visual/resource part of the
screen remains open.

### Verified Messages / News presentation contract

PR #40 was merged at `ab51a607f9576f68179ea7c0c531d594c6b411ee`.
The read-only Gate-13 presentation seam now preserves the recovered
`MPMEAMail` family and three proven manager-mail identities/actions:
ordinary renewal suggestion, Bosman renewal suggestion, and low-morale
transfer-list request. The contract explicitly records that global inbox
interleave/sorting remains unproven.

Verification on PR head `3076119018c8bdd5ca23a82e73c499f5b5ec8588`:

- focused Gate-13 run `36772292710`: **233 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36772292682`: **1,069 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36772292765`: passed.

No Messages/News screen ID, global row order, geometry, artwork, typography or
navigation is claimed. The visual/resource part of the screen remains open.

### Verified Training presentation contract

PR #41 was merged at `22254782bf396f192c9db38b1b518628177ece65`.
The Gate-13 presentation seam now preserves the recovered `Training.cpp`
record layout, fresh defaults, seven exact method/profile identities and the
daily/weekly update chain. Because no original Training screen RTTI class is
independently pinned in persisted evidence, the contract explicitly leaves the
screen class unknown rather than inventing one.

Verification on PR head `0b3e0bc3090dd763e2a8a889ee391419a7ba4c81`:

- focused Gate-13 run `36772718356`: **234 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36772718243`: **1,070 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36772718259`: passed.

Original Training controls, visible bindings, geometry, artwork and navigation
remain open.

### Verified League-table presentation contract

PR #42 was merged at `bffa017331788958344b598ea44f3f6b5e002477`.
The Gate-13 presentation seam now explicitly preserves the recovered native
`League::0x4F45E0` six-field ranking contract, including strict original
DBRClub short-name CP1252 bytes on numeric ties and the unresolved relative
order of fully equal CRT-qsort keys.

Verification on PR head `ebb84f8ab7539b5654d488153aeace0153caf523`:

- focused Gate-13 run `36773050542`: **235 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36773050532`: **1,071 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36773050761`: passed.

No original League-table screen class, artwork, header/column geometry, controls
or navigation is claimed.

### Verified Fixtures / Results presentation contract

PR #43 was merged at `a346762f0fcfc54cdb17fbd0d1787a539dfa8fd7`.
The Gate-13 presentation seam now preserves the recovered
`DBTRealFixtures` / `DBRRealFixture` and `DBTRounds` backend identities,
the shipped 380-fixture table and fixed source-order construction path. The
contract explicitly keeps the original Fixtures/Results **screen sort** unknown
rather than promoting backend source order into a UI claim.

Verification on PR head `8551d9774353f1b44af8c8c2e62da07b89cfd088`:

- focused Gate-13 run `36773557317`: **236 tests, 19 expected
  original-source-gated skips, zero failures**;
- full reconstruction run `36773557140`: **1,072 tests, 21 expected
  original-source-gated skips, zero failures**;
- repository asset-policy run `36773557226`: passed.

Original fixture-screen class/sort, artwork, geometry, controls and navigation
remain open.

### Verified Player Profile presentation contract

PR #44 was merged at `0e2d9e03b61f691be5f63ebbb7b57018cbfdbf45`.
The Gate-13 seam now preserves DBTPlayers/DBRPlayer runtime identity, keeps
historically approximate RTTI/accessor addresses explicitly as anchors, and
locks the current-skill versus development-target vector boundary without
claiming that development targets were visible on the original profile screen.

Verification on PR head `133facd4e8cdd6973d19affda7b6abf5b13e5dd7`:

- focused Gate-13 run `36773922844`: **237 tests, 19 expected skips, zero failures**;
- full reconstruction run `36773922864`: **1,073 tests, 21 expected skips, zero failures**;
- repository asset-policy run `36773922713`: passed.

A fresh trivial shell retry after CI still returned `ClientError`; the native
Button/Zurich path remains blocked. Original Player Profile class, columns,
icons, art, geometry and navigation remain open.

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Original FM2001 resources and
recoverable original behavior are the default source of truth. Use them
directly, convert them, or wrap them as needed; do not replace or redesign them
for convenience. Authorized original resources belong under
`original_assets/` with provenance tracked according to
`research/ASSET_POLICY.md`.

## Recovery 99 source-backed management presentation data bridge

- Direct native execution was re-probed at recovery start and
  `container.exec` still returned `ClientError`; the authorized
  canonical original ZIP remains retained in the private Library.
  Therefore the critical original PE32 Button RTTI/Zurich/pixel path is
  still NOT executed, and no native visual claim follows from the work below.
- PR #27, squash `0ecf3258c21f66806741807d2056008b7743c190`,
  adds `reconstruction/gate13_management_source_data.py`, a strictly
  read-only presentation seam over already recovered runtime/source data.
  It preserves controlled-club source names/date, live source roster order,
  PremierLeagueState fixture source insertion order/dates/results, and
  `GameState.premier_league_table()` output without re-sorting the native
  comparator result. Missing source identity/order fails closed. Focused
  Gate13 run `36754613939` passed **199 tests**; asset policy
  `36754613931` passed.
- PR #28, squash `278916e4479fc5ec53d12126d31a4b1894c20b4f`,
  extends that seam with persisted human formation, starter/substitute source
  IDs, the four recovered `TeamTacticalState` numeric fields and all four
  exact `TeamOrderPriorities` lists. It intentionally does NOT name or draw
  original tactics controls/slots. Focused run `36754954095` passed
  **201 tests**; asset policy `36754954127` passed.
- PR #29, squash `1d2bce7a1b22c9112b3a19b2e4e454c771557992`,
  adds a player-profile source/runtime projection: source identity, body/DOB,
  three-position tuple, live 17-byte current skill vector, condition/form/
  morale, wage/contract and recovered player status fields. Development target
  bytes are explicitly excluded because their original profile visibility is
  unproven. Focused run `36755334639` passed **203 tests**; asset policy
  `36755334392` passed.
- PR #30, squash `6c0abb541bc7b8badec9793a10c687f710897e50`,
  adds read-only Finance and active Transfer runtime projections. Balance
  ledger append order and numeric category IDs remain neutral; financial
  objective state is preserved. TransferProposal/DealInProgress/ContractTerms
  fields plus unambiguous scheduled-transfer metadata are exposed without
  assigning guessed UI names to unresolved negotiation bytes or claiming
  dictionary insertion order is original screen sorting. Focused run
  `36755982345` passed **206 tests**; asset policy
  `36755982172` passed.
- Exact architecture/evidence rules are in
  `research/GATE13_MANAGEMENT_SOURCE_DATA_BRIDGE.md`.
  These merges advance Gate13's required presentation/simulation separation
  and supply source-faithful data for the eventual original screens, but
  **do not** close any missing original artwork, control IDs, layouts,
  navigation, typography, animation state, messages-screen behavior,
  training/scouting UI, native Windows graphical smoke test or Gate13 audit.
- The current verified FULL hosted suite remains run `36751321715`
  from PR #26: **1029 tests with 21 expected original-source-gated skips**.
  Recovery-99 changes have focused Gate13 + asset-policy verification only;
  do not silently promote focused counts to a new full-suite result.

## Most recent Gate13 native-trace safeguards and source-backed League management data

- PR #24, squash `5b1bd361a922f1696e6c0fba963e9082a2e8fe55`,
  corrects a concrete original-Button RTTI CLI validation gap. The
  existing private opt-in test required recovered canonical
  TeamSelect TypeDescriptor `0x81EC10` and vftable
  `0x7C7650`, but the tool itself previously still emitted
  uncalibrated Button table candidates. It now FAILS CLOSED,
  writes no misleading private report and passes no candidate
  slots into direct-branch scans on known-positive failure. Hosted
  focused Gate13 CI `36750381283` and asset-policy check
  `36750381374` passed. A positive match against the
  original licensed executable remains NOT YET RUN.
- PR #25, squash `b7d30e557f5411aad4bd62431998d5ffd390faf7`,
  wires the ALREADY firsthand-recovered original
  `League::0x4F45E0` comparator into `PremierLeagueState`
  and `GameState.premier_league_table()`: points DESC,
  played ASC, goal difference DESC, goals for DESC, goals
  against ASC, original short-name CP1252 bytes ASC.
  Numeric ties without original names retain clearly documented
  deterministic display fallback, while a full-key native qsort
  tie does not pretend to have a proven source order. The
  original proprietary League TABLE artwork and UI remain
  unrecovered, so this is correct *management data* feeding the
  eventual original screen, not Gate13 visual fidelity.
  The first hosted full-suite PR run `36750875054` exposed
  4 synthetic finance test-stub incompatibilities (1026 tests,
  21 expected source-gated skips); those were FIXED and
  the second run `36751032575` passed 1027 tests
  with 21 expected gated skips, asset policy `36751032716`
  passed. Exact evidence in
  `research/GATE13_SOURCE_LEAGUE_COMPARATOR.md`.
- PR #26, squash `71d235e9c4478ad08c04127d949351339a013a87`,
  closes a real downstream integration gap: the match-result
  publisher had still failed to supply original CP1252 name
  bytes to the now source-aware `publish_exact_ranking()`,
  which could withhold genuinely provable complete-season
  classification on numeric ties. It now reuses the SAME strict
  source-name helper for publishing and display. Incomplete
  tables, missing/non-CP1252 names and genuinely
  indistinguishable full original keys remain fail-closed.
  Full hosted reconstruction run `36751321715` passed
  **1029 tests, 21 original-source-gated skips, zero
  failures**; asset-policy run `36751321748` passed.
  This is the current verified FULL HOSTED suite result.
- The critical native Gate13 source analysis was re-probed
  in this recovery: trivial `container.exec`,
  `python.exec`, alternate root-directory shell, and
  visible Python execution ALL returned `ClientError`.
  The exact canonical 511121336-byte original ZIP was
  independently re-listed in the private Library
  `/FM2001/Original Source/`, and is NOT lost.
  As a result no new original executable RTTI canary,
  native Button draw/update or atlas-frame state mapping,
  Zurich caption placement, original ten-file pixel audit,
  Windows 11 graphical test or Gate13 completion is claimed.
  The exact next ORIGINAL-BYTE step remains below;
  continue all remaining Gate13 screens and the Gate14-17
  release mission only after appropriate source-backed audits.

## Independent release-readiness progress while licensed byte execution is blocked

- PR #23, squash `3ed8661faee4a73496ffb3674a7f97d0ddb24fa6`,
  retired two **unsupported historical secondary-scheduler test
  assumptions** without inventing a native fixture order or per-date
  bucket distribution. The exact executable research supports the
  reverse traversal of each qsorted country-root array and World
  Cup 174 before European Championship 171; it does NOT independently
  pin the equal-key relative ordering of roots 170/181. Existing
  Gate11 original-source evidence supports **262 total secondary nodes
  in 45 nonempty buckets**, hence 217 raw CRT shuffle draws from
  `0xCAB0B953` to `0x61D6DFA2`, but the old handwritten 45-bucket
  test vector mistakenly summed to 280 and was NOT original-verified
  per bucket. Tests now assert only independently established
  navigation/RNG aggregates with an EXPLICIT synthetic bucket
  partition. The **remaining actual secondary per-date distribution
  and exact equal-key original qsort permutation stay open** in
  `research/FIDELITY_GAPS.md`; refer to
  `research/SECONDARY_SCHEDULE_TEST_CONTRACT_AUDIT.md`.
- The earlier full reconstruction GitHub Actions run `36747022836`
  passed **1,019 tests with 21 expected original-source-gated skips**
  on verified PR #23 HEAD `18fa7120e489fd191675f12d0e5899a928352c12`.
  Asset-policy run `36747022951` passed.
  The previous source-doc'd 899-test run with exactly two legacy
  failures is historical; DO NOT report it as the current full-suite
  outcome. This newly passing hosted test suite is important but
  **does not** execute original licensed-byte audits, native Button
  interaction tests or an actual Windows 11 installable release.
- Gate13 ORIGINAL presentation and native executable analysis remain
  the current active critical path. This secondary test repair is
  preparation for the later Gate15/17 fidelity and full-suite audits,
  not advancement past the incomplete Gate13 audit.

## Latest Gate 13 source-grounded Button RTTI work and limits

- PR #21, squash `6e2e67564486d9578f109106f28bb22f05a7049c`,
  adds a tightly bounded **MSVC 32-bit RTTI class-vftable candidate
  locator** for the pre-existing firsthand `Button@ease_2001` type.
  From the exact canonical executable PE sections it tests the decorated
  class string, possible TypeDescriptor, COL, CHD and vftable[-1] pointer
  chain, preserving separate multiple-inheritance subobject candidates.
  It expands the private binary trace CLI; optional direct-call scanning
  can also target candidate vftable code-pointer slots. These remain
  UNVERIFIED byte-pattern leads, not recovered Button virtual methods
  or 23-frame animation states. Gate13 focused CI `36745808069`
  and asset-policy check `36745808627` both passed.
- PR #22, squash `9931c289cce45e957a5b1dd178f06acae01576b7`,
  calibrates the same RTTI parser against the ALREADY firsthand-proven
  exact TeamSelect MSVC TypeDescriptor `0x81EC10` and class vftable
  `0x7C7650`. Its real-original opt-in test now REQUIRES that
  known-positive calibration before trusting new candidate output.
  Synthetic positive, incorrect-address and tampered-hierarchy
  regressions passed alongside the full Gate13 focused
  `36746061863` (191 tests, hosted synthetic; optional tests
  skip without licensed original bytes); asset policy
  `36746061738` passed. See
  `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
- The shell and alternate Python execution mechanisms in this worker
  both failed `ClientError` even for trivial commands. Consequently
  NO actual original executable RTTI scan, real disc ten-asset staging,
  opt-in original-pixel proof, native hover/pressed frame mapping,
  Zurich caption coordinates/color, Windows 11 UI smoke test, or
  Gate13 closure is claimed here. The original 511MB ZIP remains
  preserved in the private Library and verified in previous recoveries.
  The **next source-critical action** is to run the expanded private
  original-executable scanner and validate TeamSelect's known-positive
  RTTI calibration; then MANUALLY corroborate actual Button draw/update
  slots and frame-state data-flow. Complete genuine source-byte
  asset verification and management screens before the Gate13 audit.

## Latest source-backed Gate 13 hierarchy inspection and recovered Button path

- PR #19, squash `b488bf5380b5ef65bc833832b0a8e97acbeb5690`,
  extends the private Tk first-screen developer preview with **two
  independently cyclable, unmodified original TeamSelect hierarchy source
  strips**. Their RGBA8 PNGs appear in the diagnostic sidebar ONLY; no
  speculative screen positions, text labels, animation states or click-to-club
  semantics are drawn on the 800×600 native canvas. Exact source art paths
  and per-frame dimensions were established in prior executable/source
  research. Focused synthetic CI `36742383607` and asset-policy
  `36742383367` passed; an earlier focused attempt caught and repaired
  one mocked-Tk empty-image assertion before the final verified merge.
- Reexamining the **prior first-hand canonical executable research** in
  `research/EXECUTABLE_ANALYSIS.md` revealed a directly documented
  `Button@ease_2001` input and state-control chain that the newer
  native source-trace helper had not yet captured:
  input `0x64F7A0`, setup `0x64F380/0x64F3C0`, state-bit
  toggle `0x64F3E0`, forwarders `0x64F510/0x64F520`,
  state helpers `0x64F710/0x64F750`, TeamSelect owner
  predicate `0x5CFA50` and event handler `0x4DA480`.
  Earlier source research already proves TeamSelect Start embedded
  `Button@ease` has event ID `0x2A` at offset `+0x20`,
  owner pointer `+0x24`, and an absent optional callback at
  `+0x28`; it **does not** prove animation atlas rows or font
  alignment. Do not misread "state bit 1" as "atlas frame 1."
- PR #20, squash `38b6f3a65ed567fd2f33846d6bace7669b62c90c`,
  binds these already verified code anchors into the canonical-SHA
  executable-trace windows and optional direct-call candidate search.
  Its source provenance, click/owner graph, and exact follow-up tracing
  question are consolidated in
  `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
  Focused regression run `36742776548` and asset policy
  `36742776481` both passed.
- No fresh original executable static bytes or licensed original
  source-pixel audit is claimed in this recovery; another direct
  `container.exec` shell probe again failed `ClientError`.
  The original archive remains confirmed in private Library.
  This source-execution blocker must not be mistaken for a need to
  redesign or for permission to promote Gate 13 prematurely.

## Most recent Gate 13 verified native-trace preparation and firsthand-audit boundary

- PR #17, squash commit `4f98316c2be65e0e42925006dbfa045d410483f6`,
  extends the exact-hash-gated original PE trace helper with bounded,
  unverified raw PStartMenu/TeamSelect class-vtable pointer candidates.
  Its optional Capstone stage independently flags LINEAR near direct
  CALL/JMP leads into previously source-established code entry points
  and candidate class-vtable text targets. It explicitly cannot establish
  shared Button@ease vtable identity, executable control-flow reachability,
  native frame transitions, indirect dispatch or glyph alignment.
  Focused run `36739026011` and asset-policy run `36739026154` passed.
  Private command and evidence limitations are recorded in
  `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
- PR #18, squash commit `9682a50d0d670b41eb77dc643a293085be4043b2`,
  adds `reconstruction/gate13_original_source_audit.py`, a strict
  PRIVATE first-hand audit for the already selected ten-resource slice.
  It independently hashes the physical 511,121,336-byte canonical ZIP,
  checks the source receipt/ZIP path and all ten staged SHA-pinned original
  Joliet files, verifies the exact canonical PE32 executable, then loads
  both decoded source-backed opening screens. The audit fails if known
  first-hand RGBA background hashes, all four original Zurich font-mask
  dimensions/digests, both 23-frame action atlases or both original
  TeamSelect hierarchy art resources disagree. It writes only a small
  private JSON result OUTSIDE Git and only after every check succeeds;
  the native button/caption/hierarchy behaviors explicitly remain unset.
  Focused synthetic CI `36739577933` and asset-policy CI
  `36739577928` passed.
- **Important verification limit:** both CI results above are synthetic
  (plus an optional installed Capstone test). The private actual-source
  executable scan and the new first-hand source-byte audit have NOT run
  in this recovery. The original ZIP was verified in the private Library
  by previous workers; it has not been lost. In this recovery, two fresh
  trivial container execution calls also returned `ClientError`. This
  is an execution-infrastructure blocker specifically for NEW original
  binary analysis and original-pixel validation, not evidence of missing
  original source or successful native UI fidelity.

## Current recovery's developer-only live original-pixel inspection

- PR #16, squash commit `7fc92fedd6f660a878348a34a02055027b63c9cb`,
  provides a headless, original-coordinate frame-view model plus an
  opt-in Tk developer inspection surface. It consumes **only the already
  checksum-gated original first-screen resource bundles**, displays
  original 800x600 decoded backgrounds and a **manually chosen numeric
  original button atlas source frame**, and sends clicks to the recovered
  PStartMenu/TeamSelect session boundary. All developer diagnostics,
  source frame controls and explicit numeric club-ID input remain
  **outside native FM2001 UI fidelity**; labels are off-canvas instead
  of being rendered at invented positions.
- Focused Gate-13 synthetic/mocked-Tk CI `36736154217` and repository
  asset-policy CI `36736154071` passed. Actual Windows/Tk startup
  with the canonical licensed executable and disc graphics has **not**
  been run because source byte execution still returns `ClientError`.
  Instructions and limitations were appended to
  `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md`.
- The native Button@ease_2001 state/frame and Zurich placement trace
  remains the primary exact next source-critical task, followed by the
  ten-asset source-byte validation, provenance import, firsthand pixel
  checks and complete original management-screen reconstruction.

## Current recovery's source-exact private pixel diagnostics

- PR #15, squash commit `addc1f2dab50fdccdf7e7517ab22bdf1fbd1a35b`,
  adds `reconstruction/gate13_original_pixel_preview.py`.
  It losslessly exports both original first-screen decoded/background
  RGBA layers as RGBA8 PNGs, the actual menu/TeamSelect/hierarchy atlas
  frames separately in source order, and the authentic Zurich glyph
  alpha as uncolored PGM. Diagnostic JSON records previously
  source-proven control rectangles and string-index associations;
  unknown native interaction states, caption alignment/color and
  timing remain explicitly unset.
- Synthetic pixel-exact PNG/PGM roundtrip, private-directory and
  attribution/regression coverage passed focused GitHub Gate-13 CI
  run `36735502617` and asset-policy run `36735502710`.
  The actual licensed-source exporter remains an opt-in first-hand
  operation pending execution access. The exact private command is
  now recorded in `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md`.
  No complete original visual fidelity claim follows from this
  synthetic evidence.

## Current recovery's canonical original Button executable-trace preparation

- PR #14, squash commit `a42782047e6cfa673ef88f36773b37bf9be63e04`,
  adds `reconstruction/gate13_button_source_trace.py`: a strict canonical-
  hash-gated PE32 i386 VA reader for the *previously recovered* exact
  Button@ease, PStartMenu, TeamSelect and font call-site neighborhoods.
  It reports raw pointer-byte occurrences only as **unvalidated
  candidates**, with optional Capstone linear-disassembly output for
  independent human CFG/vtable adjudication. It refuses private
  original-code reports under the tracked repository.
- Synthetic PE32 address/boundary/candidate regression tests and an opt-in
  original-executable smoke test are in
  `reconstruction/test_gate13_button_source_trace.py`. Focused Gate-13
  run `36735030753` and asset policy `36735030926` both passed.
  The precise original-executable follow-up is in
  `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md`.
- These tests **do not** recover or verify original native frame/state
  mappings. Tracing Button@ease's actual draw/update/hover/down/up
  paths and glyph origin/baseline/color with the original executable
  remains the active source-critical task.

## Current recovery's verified TeamSelect hierarchy-art integration

- Rechecked canonical main at `cb70119caf8421703781e92766f77fd4805ff4c9`.
  The original executable/button-state and ten-asset staging tasks were
  still active; neither original-byte analysis nor Gate 13 gate audit had
  been completed.
- PR #13, squash commit `1edb4deb1063613a92bab08c7aea9153002d76f5`,
  preserves the two already source-correlated TeamSelect hierarchy
  resources `choice_league_but_anim.444` and
  `choice_league_but_bars.444` as checksum-gated, source-order strips.
  It adds their decoded-source interface to the TeamSelect resource
  loader and first-screen presenter while deliberately leaving
  source-frame state, row item mapping and artwork placement unresolved.
  Synthetic focused Gate-13 run `36734520993` and repository asset-policy
  run `36734520580` both passed. Opt-in original-byte hierarchy
  geometry/pixel tests are present but not claimed to have run.
- Both `container.exec` and the alternate visible Python execution
  route returned `ClientError` on trivial tests in this recovery.
  The confirmed original Library ZIP has not been lost; genuinely new
  original-executable disassembly remains dependent on restoring
  byte-execution access.

## Most recent Gate 13 two-screen and original-source recovery checkpoint

- PR #10, squash `96cafb5ae60148dfc7e0ba98c2886abaafe8db46`, added
  the exact-source-hash TeamSelect background and action-resource bundle,
  preserving the 16 proven hierarchy-row origins while leaving hierarchy
  item mapping and button source-frame states unresolved. Focused Gate-13
  run `36730496426` and asset-policy run `36730496711` passed.
- PR #11, squash `fccb8c2ad17431b3333d4ccbc8fa69bdf9f8e2b5`, now
  presents both original first-screen bundles through a single
  `original_first_screen_presenter.py` view and the previously verified
  `front_end_session.py`/pointer seam. Source atlas indices are exposed
  explicitly, never guessed as native idle/hover states. Headless end-to-end
  navigation (menu actions → New Game → TeamSelect → explicit club choice
  → Start and Back without implicit reset) passed focused CI
  `36730750307` and asset policy `36730750418`.
- PR #12, squash `4220259d377b8431b371d7c2fe86395406690e13`,
  records a bounded exact ten-resource original-disc extraction plan in
  `research/GATE13_FIRST_SCREEN_EXACT_PATHS.txt`, checks every
  source SHA against the independently verified canonical ZIP and a
  one-per-path original-disc extraction receipt through
  `gate13_first_screen_selection.py`, and documents the precise recovery/
  import commands in `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md`.
  Focused CI `36731158020` and asset policy `36731158181` passed.
- These are synthetic/headless/receipt-validation milestones. No newly
  staged licensed original pixels, native Button@ease frame mapping or
  Windows 11 installable build has been verified by this worker.
- Private Library listing in this recovery again confirmed the canonical
  511,121,336-byte source ZIP at the recorded original Library path and ID.
  Multiple independent trivial `container.exec` commands and one trivial
  `python.exec` command failed with `ClientError` in this session.
  This is an **execution infrastructure blocker**, not a lost source archive.
  Direct executable disassembly and real-disc staging/opt-in tests must
  resume when an execution container is actually available.

## Latest verified original-font and atlas resource integration

- The already committed source-backed original EAUK bitmap-font parser
  (`reconstruction/ea_font.py`) recovers 224 CP1252 glyph records, individual
  metrics, source alpha atlas and signed pair spacing from original font
  loader `0x657650`. The canonical original
  `Fonts/Zurich_BdXCn_BT_20pixel.fnt` exact hash and first-hand original
  menu label masks are pinned in opt-in tests. Its initial source-backed
  verification predates this checkpoint.
- PR #7, squash commit `973e08253997f75f889b8fd35a370e58ecad40c1`,
  binds the recovered exact PStartMenu event/IDX mapping to actual original
  CP1252 font glyph masks without inventing caption positions or colors. It
  also fixes Gate 13 CI to actually execute the already tracked EA font tests.
  Hosted Gate-13 run `36729337643` and asset policy `36729337666` passed.
- PR #8, squash commit `0a999a16d17850613c0c7451b972b44e3d99d987`,
  provides exact-hash-gated source decoding and lossless slicing of
  `button_type_1.444` (169x575/169x25) and
  `choice_start_anim.444` (150x736/150x32) into 23 vertical source frames
  each. This does NOT imply an unproven native hover/pressed frame mapping.
  Hosted Gate-13 run `36729704209` and asset policy `36729704079` passed.
- PR #9, squash commit `0425d80e099c26f80c409c9e0515b26799ec131b`,
  adds a checksum-gated render-ready original English menu source loader
  encompassing canonical executable tables, global/menu backgrounds,
  original font/STR/IDX, and real button frames. Only the previously
  independently measured original 800x600 background composition SHA is
  described as visually verified. It explicitly does not invent native button
  states or caption placement. Hosted Gate-13 run `36730124709` and
  asset policy `36730124841` passed; original-byte integration tests remain
  opt-in because licensed source binaries are not shipped in CI.
- This worker's `container.exec` and `python.exec` both returned
  `ClientError` even for trivial commands, including a renewed shell
  attempt after these milestones. Do not treat this temporary execution
  failure as lost original resources: the canonical private ZIP locator in
  `research/ORIGINAL_SOURCE_LOCATOR.md` remains available. No first-hand
  new executable disassembly or licensed-source local run is claimed here.

## Latest verified Gate 13 integration checkpoints

- PR #5, squash commit `b204d01189dbfa6de5a624f5f4769ffb27ea37f7`,
  repaired the now-obsolete test that treated original PStartMenu event 1 as
  unsupported and added source-backed original layout tests to Gate 13 CI.
  Focused run `36725002444` and the corresponding repository asset-policy
  check passed.
- PR #6, squash commit `bf643d3ac6a7869842770174a6d7b3477689e895`,
  added `original_front_end_input.py`, which translates confirmed first-screen
  unscaled pixel rectangles into recovered menu/TeamSelect event IDs and
  delegates them to `front_end_session.py`. It deliberately does not assign
  events to unrecovered hierarchy controls or claim pixel-accurate hover/
  transparency handling. Dedicated focused run `36725905158` and asset
  policy run `36725904605` passed on PR #6.
- These CI runs cover synthetic/headless regressions. Neither substitutes for
  opt-in original licensed image/executable tests or a full-suite release audit.
  The previously documented two secondary-schedule full-suite failures remain
  an explicit separate fidelity boundary.

## Earlier verified implementation baseline

```text
1cf7af7ebccba34c6f414d1c3df2f82fb2346686
Verify complete ZIP extraction-to-provenance import for opaque UI binary
```

Dedicated GitHub Actions Gate 13 run `36699473176` passed **71/71 focused
tests**. Full reconstruction run `36699473326` ran **899 tests with 2 failures**,
exactly the two long-standing secondary-schedule assertions:

- secondary root-order assertion;
- secondary bucket-count assertion (262 expected vs 280 recovered).

All Gate-13 navigation, source-inventory, MODE1-conversion, native
ISO9660/Joliet inventory/extraction, and provenance-import tests passed.
Repository asset policy passed.

## Gate 12 closure checkpoint

The canonical annual run used the recovered fresh-game date **4 July 2000** and
reached a complete annual qualification snapshot on **4 June 2001**, after 335
simulated days.

It captured:

- played League sources `(0, 17, 21, 27, 31, 40, 50, 54)`;
- all 44 required DummyLeague ranking sources;
- all ten annual Cup sources `(1, 5, 9, 10, 19, 23, 33, 91, 98, 101)`.

The source-derived Champions League child phases 14/167 and WCC group phase 192
all ran live. Recovered League comparator `0x4F45E0` now resolves European
group ties with points, played, goal difference, goals for, goals against, then
CP1252 short-name bytes.

Atomic annual regeneration then:

- applied 28 membership changes;
- generated season year 2001;
- consumed 15,539 annual materialization draws;
- changed controller match RNG from `0xCE9A6E40` to `0x6F763739`;
- produced a fresh 380-fixture Premier League;
- produced 150 year-two primary-order dates;
- retained every played annual qualification-source League.

Internal save schema remains **34**.

## Stable startup / scheduler checkpoint

- DBTPlayers startup RNG: **180,384 calls** for 30,064 players;
- synthetic post-youth state: **`0x4B68DE28`**;
- actual-count primary competition RNG: **5,836 calls**;
- state entering primary `0x615BE0`: **`0x4F5CF274`**;
- complete primary schedule nodes: **9,346**;
- primary buckets: **373**;
- primary bucket-shuffle calls: **9,178**;
- state after primary schedule shuffle: **`0xD25DFFE6`**;
- first PL fixture order: **0, 6, 8, 5, 1, 9, 3, 2, 4, 7**.

## Gate 13 live checkpoint: original source access restored

**Confirmed firsthand 30 September 2026:** the execution container now reads
the actual authorized original archive and raw disc bytes. Earlier container
`ClientError` notes in historical `PROGRESS.md` no longer describe the
current source-access state.

- Authoritative original ZIP is 511,121,336 bytes; directly calculated
  SHA-256: `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
- ZIP contains the original 631,627,248-byte raw `famg2001.bin`
  MODE1/2352 CD track (CUE independently confirms its sector mode).
- All **268,549 physical sectors** were verified with zero invalid sectors.
- The original **Joliet level-3** filesystem was enumerated firsthand:
  **2,456 files, 211 folders, zero case-insensitive path collisions**.
  There are 1,354 `.444` image resources and 1,403
  `FM2001_Art` files. Refer to
  `research/GATE13_REAL_DISC_INVENTORY.md` for detailed counts, exact
  first-slice paths, sizes, independently calculated resource SHA-256 hashes,
  and a reproducible recovery procedure.
- Canonical `FM2001_Art/Generic/bground.444` was directly extracted and
  independently SHA-256-verified against prior research:
  **222,616 bytes, 800×600**, hash
  `9db0d71daf70d77b4f5f2307304bb8c5eac4ee3a07a85f2828b570fbbf3b7fb9`.
- Exact extracted originals also include
  `FM2001_Art/Generic/main_menu/main_menu_bground.444` (532×532),
  `FM2001_Art/Generic/team_choice/background.444` (800×558),
  TeamSelect choice animations, Premiership division graphics, original
  English text/index data, and several related first-slice resources.
  All targeted hashes are recorded in the first-hand inventory note.
- The actual original `footballmanager.exe` and copy under `crack/`
  were extracted independently and have identical SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`,
  matching the prior verified executable used in reverse-engineering.
- Private current execution workspace contains the full derived catalog at
  `/mnt/data/fm2001-work/real_disc_catalog.json`, staged first-slice bytes
  at `/mnt/data/fm2001-work/staging/`, and the full selected hash receipt
  `/mnt/data/fm2001-work/first_slice_receipt.json`. These are **temporary
  workspace paths**. If unavailable in a future chat, regenerate them from
  the canonical private Library ZIP using the repository's native inventory,
  rather than requesting a re-upload. The detailed confirmed research note
  and ZIP SHA are durable in GitHub. An attempted Library backup upload
  of the complete catalog failed with `container_session_expired`, so do
  **not** incorrectly assume that complete report is already persistently
  saved outside this container.

Existing architectural boundary remains verified:

- `front_end_state.py` preserves recovered original controls: PStartMenu
  ID `0x323`, New Game event `2`, TeamSelect Back `0x29`,
  Start/Continue `0x2A`.
- `front_end_session.py` connects that recovered control contract to
  the working Premier League backend without moving simulation logic
  into the presentation layer.
- Prior dedicated Gate-13 CI run `36699473176` passed 71/71 synthetic
  focused tests; full suite run `36699473326` had 899 tests and only
  the two already documented secondary-schedule failures. These tests
  predate the first real-disc inspection and do not independently validate
  the new original `.444` images.

## Latest original EA444 decoder implementation and local evidence

The real-disc catalog and original checksum facts above remain canonical.
Original graphics no longer need to be guessed or rediscovered.

- `ea444_header.py` validates all 1,354 original `.444` headers.
  `ea444_bits.py` implements original little-endian-DWORD,
  most-significant-bit-first compressed bit ordering.
- `ea444_tables.py` reconstructs original coefficient permutation
  and 160-entry Huffman lookup from the exact canonical executable's
  initialized `TQIA_DAT` PE section; its SHA is checked.
- `ea444_coefficients.py` implements the source-backed 8-bit
  scale/DC, variable Huffman run-length, signed AC amplitude, 14-bit
  escape and EOB parsing for one component. All **17** real first-slice
  graphic assets produced valid first component blocks.
- `ea444_quantization.py` reads the 64 original `.rdata`
  quantization seeds at VA `0x7DABF0` and reproduces the x86
  `IMUL/SHL/SHR/ADC` 16.16 scaling and signed low-DWORD
  multiplication. The source 256-byte table SHA is
  `6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb`.
- `ea444_quantized_block.py` maps raw sparse coefficients to the
  canonical 64-position, pre-inverse-transform component grid,
  rejecting repeated or out-of-range positions.
- Actual menu background first component: scale code **15**, **14**
  signed AC coefficients, **93 consumed bits**, **15** nonzero
  pre-transform fixed-point grid values and packed-grid SHA
  `d074fa03f380438bfccbdf88dc2375f700434891889399e4750fc7bc2c75c2d7`.
  The reproduced DC fixed-point value is **983040**.
- Source-backed local tests: 12/12 across bitstream, original
  executable Huffman tables and sparse coefficients. Original
  quantization and combined-grid measurements independently verified
  using the actual private original executable and menu bytes.
  The newest additional quantization/grid regression files are
  committed, but **no new hosted CI run has yet been claimed**;
  hosted Gate-13 workflow is PR/manual only to conserve CI minutes.
- Research, original entry points and the incomplete 2-pass IDCT
  boundary are in `research/GATE13_EA444_DECODER_TRACE.md`.
  Original PNG and tiny `.444` source fixtures remain provenance-
  tracked in `original_assets/MANIFEST.md`.
- A subsequent attempt to save the complete derived catalog to
  private Library `/FM2001/Research/` again failed with
  `container_session_expired`. The original ZIP is safely retained;
  its metadata/hash research is in GitHub. Do not claim that the
  full derived catalog was backed up to Library.

## Gate 13 exact PStartMenu action checkpoint

Canonical PStartMenu control setup at `0x4C1BA0`, language loader
`0x635F30`, shared button resource initialization `0x5F4500`, and dispatch
`0x4C3770` now close the four primary menu actions:

- event 1 = English.idx 0 **Continue**, rect `(181,478,169,25)`;
- event 2 = English.idx 1 **Start New Game**, rect `(7,478,169,25)`;
- event 3 = English.idx 2 **Load Game**, rect `(355,478,169,25)`;
- event 4 = English.idx 6 **Quit to Windows**, rect `(181,508,169,25)`.

All four use the original
`FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444` atlas. Its
source EA444 dimensions are 169×575; runtime handle `0x946590` is initialized
with exact frame dimensions 169×25. The common label-font handle
`0x9197E0` is independently traced to original
`Fonts/Zurich_BdXCn_BT_20pixel.fnt`.

`original_front_end_layout.py` now records the exact action atlas, language
indices and rectangles. `front_end_state.py` exposes Continue, New Game,
Load Game and Quit as recovered presentation commands; only New Game changes
to TeamSelect, preserving separation from application-side load/quit behavior.
Address-level evidence is in `research/GATE13_PSTARTMENU_LAYOUT.md`.

The exact EA444 inverse-transform hot loop has also been converted from
per-row Fraction allocation to mathematically identical common-denominator
dyadic integer arithmetic. A first-hand 100,000-pair differential check
against the prior exact Fraction formula matched bit-for-bit, the original
main-menu component hash remains unchanged, and source-backed full
main-menu/TeamSelect decode tests now finish in roughly 20 seconds rather than
timing out. This is a performance optimization of recovered arithmetic, not
a visual approximation.

## Gate 13 verified first-screen pointer bridge

The original menu controls and TeamSelect action rectangles can now be
translated into application-level pointer events without importing gameplay
simulation into the presentation geometry. See
`reconstruction/original_front_end_input.py` and its focused tests.

The next fidelity-critical step remains the original
`Fonts/Zurich_BdXCn_BT_20pixel.fnt` glyph/metric recovery and
`Button@ease_2001` atlas-frame-state binding, followed by complete
original graphic composition and TeamSelect hierarchy input recovery. The
pointer bridge only covers the six confirmed first-screen action rectangles;
the remaining screen and rendering details must not be invented.

This worker re-resolved the authorized archive via private Files/Library and
the materialization service returned its expected 511,121,336-byte ZIP path,
but the execution container and Python both failed with `ClientError` on
trivial commands, so no new first-hand original-byte test is claimed here.
Use `research/ORIGINAL_SOURCE_LOCATOR.md` to rematerialize when execution
recovers. Other source-backed GitHub development and focused CI succeeded.

## Exact next task within the full Gate-17 mission

1. Retry one trivial shell or alternate Python execution command. If byte
   execution is restored, rematerialize the exact private original FM2001
   Library ZIP and separately extract its canonical `footballmanager.exe`.
   Independently recheck the executable SHA:
   `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
   Do not ask Daniel to re-upload an archive already preserved in Library.
2. Execute the PRIVATE expanded original Button trace documented in
   `research/GATE13_BUTTON_STATE_TRACE_PROCEDURE.md` against the actual
   verified original executable. Prioritize already source-confirmed
   `Button@ease_2001` input `0x64F7A0`, state bits
   `0x64F3E0/0x64F710/0x64F750`, source atlas init
   `0x5F4500`, shared setup `0x652FD0`, screen control
   constructors `0x4C1BA0` and `0x4D885F`, and TeamSelect
   owner event `0x4DA480`. Trace the **actual native draw/update
   data-flow from control state bits to numbered 23-frame original
   atlas rows**, including idle/hover/down/up/disabled. Independently
   recover Zurich glyph origin, pair spacing, baseline, colors and
   clipping from the font renderer reached by the true draw path.
   A previously proven "state bit 1", raw class-vtable pointer or
   candidate CALL is NOT proof of atlas-frame 1 or native text placement.
3. Run the precise private ten-asset extraction and fail-closed source
   receipt validator in `research/GATE13_FIRST_SCREEN_RESOURCE_PLAN.md`.
   Then execute the newly added `reconstruction/gate13_original_source_audit.py`
   for direct canonical ZIP, executable, decoded first-screen pixels,
   original Zurich masks and original hierarchy art evidence. Keep its
   receipt and source-pixel diagnostic output private and outside Git.
   Do not claim source-byte tests ran based solely on hosted synthetic CI.
4. Once actual source bytes and native frame/caption/hierarchy behavior
   are VERIFIED, intentionally provenance-import only correlated authorized
   first-screen original bytes under `original_assets/`, complete authentic
   PStartMenu and TeamSelect presentation and their Windows graphical
   source-backed smoke tests. No guessed button states or typography.
5. Continue Gate 13 manager home, squad, tactics, fixtures, table,
   profile, transfers, finances, messages/news, training/scouting and
   remaining original screens. Audit all Gate-13 criteria; then proceed
   through Gates 14, 15, 16 and 17. The mission is complete only upon
   a genuinely verified installable Windows 11 release audit.

## Known live fidelity boundaries

See `research/FIDELITY_GAPS.md`. The old secondary test assertions are now bounded to established
aggregate evidence and passed a full hosted suite; exact native
secondary date-bucket composition/equal-key tie order, original save
compatibility, residual transfer/finance branches,
special both-controlled-participants Cup revenue, and presentation/audio
fidelity remain explicit later work. Do not promote historical synthetic
tooling verification as original-screen visual fidelity.
# Local Windows recovery 124: Squad row/state trace closed

The canonical executable was rehashed locally as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3` and the
expanded private Squad trace was regenerated outside Git. Manual data-flow
adjudication now closes the concrete `PSquadList`/`CSquadPlayerList`/
`CSquadSCFList` owner hierarchy, 20-row construction, player and side-column
bindings, neutral status-filter code map, empty-row behavior, and exact
`FormationText` group/state-to-source-row transform. Focused tests pass.

No proprietary executable, archive, or raw trace entered Git. Exact evidence
is in `research/GATE13_SQUAD_RESOURCE_CORRELATION.md`; durable constants and
fail-closed behavior are in `reconstruction/original_squad_resources.py`.

Exact next Gate-13 task: run the real Windows PStartMenu/TeamSelect graphical
audit, then recover remaining TeamSelect hierarchy input/state mappings and
continue management-screen presentation correlation. Gate 13 remains active.

Verification: the two directly affected modules pass 14 tests with one
expected licensed-source-gated skip. The full Gate-13 focused list ran 263
tests locally: 241 passed, 21 expected source-gated skips, and the pre-existing
Linux-oriented duplicate-ZIP-path assertion failed on Windows because
`Panel.dat` and `panel.dat` are the same filesystem entry. No Squad test failed.

## Recovery 128: Windows audit harness merged; GUI deferred; Gate 14 foundation advanced

- Canonical `main` now includes PR #49 as
  `0a871b5fbc9c546ad67c335bc6db009d3a023627`. It adds the fail-closed
  `gate13_windows_first_screen_audit.py` real-Windows/Tk harness plus contract
  tests and procedure documentation. Hosted Gate-13 run `36830496970` and
  asset-policy run `36830496972` passed after the synthetic hierarchy fixture
  was corrected. This verifies the harness, **not** the real Windows GUI run.
- This worker's local/container process launch remains unavailable with
  `caas.internal.errors.ClientError`, and no Windows GUI is exposed. The actual
  PStartMenu/TeamSelect graphical smoke receipt is therefore a deferred Gate-13
  blocker. Run the merged harness against the private canonical executable,
  source staging and verified game directory on the next working Windows path.
- Under the repository's deferred-blocker policy, independent cloud-safe work
  continued without closing Gate 13. PR #50 was squash-merged as
  `e54cc8591df91bbc949856ed241fcffcedd5fe97` after full reconstruction run
  `36831057948` and asset-policy run `36831057947` passed.
- Gate-14 work-ahead now has a checksum/size-gated contract for the already
  verified original `easp.tgq` -> `premintro.tgq` startup sequence and a
  read-only match-presentation feed that consumes existing timed MatchCalculator
  events/possession records without simulation RNG, commentary generation,
  sound mapping or invented animation semantics. Gate 14 is **not** declared
  complete; Gate 13 remains the active validation gate.
- Exact deferred Gate-13 action remains: obtain the real Windows graphical
  receipt, then recover TeamSelect hierarchy item/input/state semantics from
  source evidence and continue remaining management-screen fidelity. Until
  that local path returns, continue the highest-priority independent cloud-safe
  work, next targeting Gate-16 long-duration/destructive audit coverage without
  claiming Gate 16 complete.

## Recovery 138: real Windows first-screen graphical audit passed

- Canonical `main` was reconciled at `70a86dc4033ec51d6dd9ed207405e4275acfd223`
  before the run. The authorized ZIP and canonical executable were rehashed as
  `677dcbc...a8a4` and `833bf95e...cc3`; the four required gameplay files were
  freshly extracted and passed `verify_canonical_files`.
- The merged real-Windows/Tk harness passed on Windows 11 build 26200 with
  Python 3.12.14 and Tk 8.6.12. It verified the live 800x600 canvas, exact
  PhotoImage geometry, PStartMenu frame-0/frame-11 captions and colors, actual
  New Game -> TeamSelect -> Back bindings, inert unresolved hierarchy input,
  and rejection of Start without a club.
- The bounded receipt stays private outside Git; SHA-256 is
  `b61d56dde7fc3ee7d25451cc993f545c28217cb28347a05921d379efe932e9b4`.
  No proprietary raw bytes or screen dump entered the repository.
- Gate 13 remains active. Exact next task is the remaining TeamSelect native
  hierarchy item identity, hit/input, selection-state, caption/content and
  navigation mapping, followed by a second Windows audit with live hierarchy
  behavior and then broader management-screen presentation fidelity.

## Recovery 139: TeamSelect native hierarchy owner graph recovered

- Canonical executable RTTI/disassembly resolves `PMain@TeamSelect` and its
  `LeagueBtnGrp`/`TeamBtnGrp` child families.
- Source-backed geometry, control IDs, and object offsets are now locked for
  all 16 country/competition controls and all 24 club controls, together with
  the canonical English country order.
- Native flow is proven as country expansion -> competition selection -> club
  population -> Start. Exact competition filtering, visual frame states, and
  the final club selection write remain open; the live hierarchy stays inert
  and Gate 13 remains active.
- Evidence: `research/GATE13_TEAMSELECT_HIERARCHY_TRACE.md`.
