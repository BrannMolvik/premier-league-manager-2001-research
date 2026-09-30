# Current State

_Last reconciled: 30 September 2026_

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

## Porting mission

This is a **Windows 11 modernization/port**. The supplied FM2001 archive/disc
contents are authorized for project use. Original FM2001 resources and
recoverable original behavior are the default source of truth. Use them
directly, convert them, or wrap them as needed; do not replace or redesign them
for convenience. Authorized original resources belong under
`original_assets/` with provenance tracked according to
`research/ASSET_POLICY.md`.

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

See `research/FIDELITY_GAPS.md`. The two existing secondary-schedule
assertions, original save compatibility, residual transfer/finance branches,
special both-controlled-participants Cup revenue, and presentation/audio
fidelity remain explicit later work. Do not promote historical synthetic
tooling verification as original-screen visual fidelity.
