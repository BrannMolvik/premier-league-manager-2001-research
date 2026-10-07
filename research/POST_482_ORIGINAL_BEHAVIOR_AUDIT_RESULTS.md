# Post-#482 Original-Behavior Retrospective Audit Results

_Date: 7 October 2026 KST._  
_Audit snapshot: `main@e4a60f0a40ed7bfe9664f899c6f13f8796fdbd41`._  
_Reopen base (excluded): `e2770be0649853e00d1e849ffd377ea3a115d237`._

## Result

The retrospective audit is complete for the snapshot above. An explicit
first-parent walk reaches the reopen base after **128 in-scope main commits**.
The earlier runtime handoff count of 99 was stale and is superseded by this
inventory.

The audit does **not** close Gate 13. It separates source-correct component
work from player-visible acceptance and reconciles Daniel's four external
contradictions without treating green CI as stronger evidence than the normal
Windows run.

Classification codes in the table:

- **O — ORIGINAL-PROVEN**: player/runtime behavior is backed by reproducible
  original executable/resource/data evidence.
- **C — COMPATIBILITY-EQUIVALENT**: the mechanism is modern, but its bounded
  effect preserves the source-proven behavior or exact bytes.
- **R — RESEARCH/INFRASTRUCTURE-ONLY**: no new normal player behavior.
- **D — DEFERRED-MODERNIZATION**: intentional non-original feature, preserved
  only outside the original-default path.
- **I — INCONCLUSIVE**: source component evidence exists, but the active
  player-visible equivalence is not established or is contradicted externally.
- **U — UNSUPPORTED**: active behavior has no acceptable original/equivalence
  basis. No in-scope snapshot commit is left classified U after isolation;
  one pre-scope fullscreen-key behavior is handled separately below.

## Evidence anchors

The behavior classifications below are grounded in these reproducible
repository evidence sets, not in commit titles alone:

- **PSTART** — `research/GATE13_PSTARTMENU_DERIVATIVE.md`, pinned source
  identities, canonical manifest SHA-256 and exact decoded payload hashes.
- **FMV** — `research/GATE13_STARTUP_FMV_PRESENTATION_SOURCE_TRACE.md` and
  `research/STARTUP_FMV_PIXEL_PIPELINE.md`: canonical EXE/TGQ identities,
  flag `0x40`, doubled 16-bpp writer, 640x480 movie surface, 1:1 final blit,
  ordinary 800x600 destination `(80,60)-(720,540)`.
- **WPF** — `research/GATE13_ISSUE482_WPF_STARTUP_DIAGNOSIS.md`: controlled
  blocked/pumped child-HWND observations and unchanged production WPF script.
- **SQUAD** — `research/GATE13_SQUAD_RESOURCE_CORRELATION.md`,
  `research/GATE13_SQUAD_PRESENTATION_CONTRACT.md`, and
  `research/GATE13_SQUAD_STATUS_LIFECYCLE.md`: canonical executable
  addresses/RTTI, exact assets, roster ordering, fields, status priority and
  lifecycle.
- **CUP** — `research/GATE13_CUP_TIED_RUNTIME.md` plus Recovery 357 in
  `research/GATE13_SQUAD_STATUS_LIFECYCLE.md`: root ownership, collection
  semantics, transfer-history date, DBRGame selector and +60/+207-day cutoffs.
- **PREMATCH** — `research/GATE14_PREMATCH_PANEL.md` and
  `research/GATE14_FASTVIEW_DIRECT_HEADER_TEXT.md`: canonical executable
  addresses, original resources/hashes, child order, geometry, text and rating
  mechanics. Management-to-match launch remains fail-closed.
- **EXT** — Daniel's normal Windows observations that reopened Gate 13 and the
  four contradictions named by the mandatory audit: startup framing, Escape
  input, transition latency, and incomplete fresh Southport Squad landing.
- **DIFF** — the item changes only research/status/tests/workflows/provenance or
  a fail-closed research tracer and does not alter normal player behavior.

## Complete first-parent inventory

Every in-scope first-parent commit appears exactly once below.

| # | Commit | Item | Class | Evidence / disposition |
|---:|---|---|:---:|---|
| 1 | `e4a60f0a` | State: block implementation pending post-482 source audit | R | DIFF; retain |
| 2 | `0ccb9192` | Require retrospective source validation | R | DIFF; audit specification |
| 3 | `087ea771` | Prioritize original Gate 13 behavior | R | DIFF; retain |
| 4 | `e6dd1cfb` | Autoworker source-first freeze | R | DIFF; retain |
| 5 | `cf4a1861` | Continuation source-first rules | R | DIFF; retain |
| 6 | `f6a4cf3a` | Roadmap modernization freeze | R | DIFF; retain |
| 7 | `2da9782a` | Original-behavior-first policy | R | DIFF; retain |
| 8 | `f2772868` | PR #538 Gate-17 material checkpoint reconciliation | R | Gate-17 status only; freeze |
| 9 | `edf24e71` | PR #537 redistribution material bundle | R | Packaging/audit tooling only; freeze |
| 10 | `0e1abef6` | PR #536 exact FFmpeg source snapshot | R | Packaging provenance only; freeze |
| 11 | `513afeff` | PR #535 contributor license material | R | Packaging provenance only; freeze |
| 12 | `85f1534e` | PR #534 static-contributor source bundle | R | Packaging provenance only; freeze |
| 13 | `5cb72c97` | PR #533 Settings/acceptance reconciliation | R | Status claims superseded by this audit |
| 14 | `2ccec2ce` | PR #532 source-styled Settings surface | D | Intentional modernization; isolate from default |
| 15 | `1a580ea7` | PR #531 link-map proof / Settings pivot | R | Status/toolchain evidence only |
| 16 | `5edc4764` | PR #530 archive-member contribution proof | R | Toolchain audit only |
| 17 | `21eb5031` | Roadmap adds Settings/graphics options | R | Documentation; modernization requirement superseded |
| 18 | `84437800` | PR #529 link-input ownership reconciliation | R | Toolchain status only |
| 19 | `0f1739c2` | PR #528 package owners of link inputs | R | Toolchain audit only |
| 20 | `c73e07e5` | PR #527 link-input state reconciliation | R | Status only |
| 21 | `1bdbb2d9` | PR #526 resolved minimal FFmpeg link inputs | R | Toolchain audit only |
| 22 | `2583ff73` | PR #525 source-contract CI hardening | R | CI/toolchain only |
| 23 | `eb5fe6a4` | PR #524 build package environment lock | R | Toolchain provenance only |
| 24 | `aadaf484` | PR #523 critical source-family tarballs | R | Toolchain provenance only |
| 25 | `073099c7` | PR #522 source-material plan | R | Toolchain provenance only |
| 26 | `12544b6f` | Gate-14 trigger / tracer status | R | Status only |
| 27 | `79695509` | PR #520 progress receipt | R | Progress only |
| 28 | `100f7544` | Caller-tracer state receipt | R | State only |
| 29 | `a117df66` | PR #520 candidate-only match-entry caller tracer | R | Fail-closed research tracer; no normal route |
| 30 | `3b88bc67` | Gate-13 candidate status | R | Status only |
| 31 | `bb7734f4` | PR #519 package/progress receipt | R | Progress only |
| 32 | `855a4d9b` | Package/tracer boundary state | R | State only |
| 33 | `c28c9984` | PR #519 host source Match Detail dispatch | O | PREMATCH; only after source-accepted selection |
| 34 | `581a3d2d` | WPF repair progress | R | Progress only |
| 35 | `27143dd0` | WPF repair status | R | Status only |
| 36 | `532833a8` | WPF startup-fix state | R | State only |
| 37 | `bfe95f25` | PR #521 embedded WPF owner pumping | C | WPF; modern message pump preserves bounded source sequence |
| 38 | `f7b17cca` | PR #518 Match Detail presentation dispatch | O | PREMATCH; exact mode branches, launch remains closed |
| 39 | `bf91dc03` | PPreMatch compositor progress | R | Progress only |
| 40 | `d1268e62` | PPreMatch compositor state | R | State only |
| 41 | `37b709ef` | PR #517 PPreMatch native compositor | O | PREMATCH; source child order/layers |
| 42 | `b1544807` | PPreMatch progress | R | Progress only |
| 43 | `43809408` | PPreMatch state | R | State only |
| 44 | `77120385` | PR #516 PPreMatch supplied raster state | O | PREMATCH; source-bounded supplied state |
| 45 | `9e4d2377` | PR #515 PPreMatch team badges | O | PREMATCH; exact source family/geometry |
| 46 | `17f49fa3` | PR #514 PPreMatch row selector state | O | PREMATCH; source-bounded state |
| 47 | `8a6dddec` | PR #513 PPreMatch markers | O | PREMATCH; source markers/formation path |
| 48 | `6a6627b5` | PR #512 Gate-15 ledger doc reconcile | R | Documentation only |
| 49 | `b142892a` | PR #511 PPreMatch coverage | O | PREMATCH; structural coverage, no launch |
| 50 | `e58caf33` | PR #510 PPreMatch text surface | O | PREMATCH; exact text-control contract |
| 51 | `aee48673` | Pre-match row progress | R | Progress only |
| 52 | `91bcac71` | Pre-match row state | R | State only |
| 53 | `29a79930` | PR #509 PPreMatch rows | O | PREMATCH; source row geometry/content boundary |
| 54 | `065eeb83` | PR #508 PPreMatch identity | O | PREMATCH; source identity contract |
| 55 | `222a6bd8` | Recovery 367 project status | R | Status only |
| 56 | `7cae8004` | Recovery 365-367 progress | R | Progress only |
| 57 | `6c2bd690` | PPreMatch rating state | R | State only |
| 58 | `58bf939e` | PR #507 native PPreMatch rating widths | O | PREMATCH; exact XI/rating functions |
| 59 | `f84b0ca5` | PR #506 staged PPreMatch presentation surface | O | PREMATCH; exact consumed assets, fail-closed gaps |
| 60 | `c754fd46` | Pre-match correction progress | R | Progress only |
| 61 | `c25e4c1c` | Pre-match correction state | R | State only |
| 62 | `adff9a96` | PR #505 live background/rating correction | O | PREMATCH; supersedes false prematch_bground assumption |
| 63 | `d83ce244` | Pre-match progress | R | Progress only |
| 64 | `4d43313f` | Pre-match integration state | R | State only |
| 65 | `4080cfb6` | PR #504 source-backed PPreMatchPanel model | O | PREMATCH; exact panel/event contract |
| 66 | `f85e3ddf` | Correct selector atlas binding | R | Research correction only |
| 67 | `b3680c6c` | Document PPreMatch layout | R | Research only |
| 68 | `1f1402c8` | Match Detail project status | R | Status only |
| 69 | `cfaa6227` | Match Detail progress | R | Progress only |
| 70 | `2f34b6aa` | Match Detail integration checkpoint | R | State only |
| 71 | `531266d1` | PR #503 source-backed Match Detail selection | O | PREMATCH; exact selectable modes, sentinel fail-closed |
| 72 | `c643e777` | FastView activation trace state | R | Research state only |
| 73 | `26836742` | Cup-Tied project status | R | Status only |
| 74 | `1b3e8af7` | Cup-Tied progress | R | Progress only |
| 75 | `4453b20b` | Cup-Tied state | R | State only |
| 76 | `3719f7a9` | PR #502 mode-1 Cup-Tied fallback integration | O | CUP; final code reflects Recovery-357 date semantics |
| 77 | `9a32ddf7` | Model source-closed Cup-Tied date window | O | CUP; DBRGame selector/cutoffs |
| 78 | `a00dbefd` | DBRGame date-semantics checkpoint | R | Research/state only |
| 79 | `ce3b45fd` | Cup-Tied producer trace checkpoint | R | Research/state only |
| 80 | `a6711b09` | PR #501 minimal FFmpeg toolchain provenance | R | Gate-17 tooling only |
| 81 | `ae578fc1` | Transfer-history appearance-semantics correction | R | Research false lead; superseded by Recovery 357 before final integration |
| 82 | `8d670a72` | Source/TGQ proof checkpoint | R | Research state only |
| 83 | `52d2cb84` | PR #500 exact original TGQ proof helper | R | Gate-17 verification only |
| 84 | `f71b56c5` | Synthetic FFmpeg roundtrip checkpoint | R | Status only |
| 85 | `d918d621` | PR #499 minimal FFmpeg synthetic roundtrip | R | Gate-17 verification only |
| 86 | `c624387f` | Minimal FFmpeg build checkpoint | R | Status only |
| 87 | `b150555f` | PR #479 minimal FFmpeg pinned-source build | R | Gate-17 verification only |
| 88 | `6b9bf4dc` | PR #475 minimal FFmpeg source contract | R | Gate-17 verification only |
| 89 | `7fe07ab3` | Package-repair checkpoint | R | State only |
| 90 | `e24485b5` | PR #498 preserve exact PStartMenu bytes on Windows | C | PSTART; packaging preserves exact pinned source-derived bytes |
| 91 | `03c5783d` | PR #497/package blocker state | R | State/progress only |
| 92 | `a881d628` | PR #497 Non-EU Squad status lifecycle | O | SQUAD; exact override/lifecycle evidence |
| 93 | `3c17eaa1` | PR #496 WPF startup acceptance audit | R | Audit tooling/docs only; not human acceptance |
| 94 | `f9723879` | PR #495 validation progress | R | Progress only |
| 95 | `378dd847` | PR #495 state reconciliation | R | State only |
| 96 | `0a91c088` | PR #495 Squad Cup-Tied resolver integration | O | SQUAD+CUP; source-qualified positive path/fail-closed gaps |
| 97 | `3eeb5b92` | PR #494 exact Cup-Tied runtime state | O | CUP; root collection producer/lookup |
| 98 | `7e1597e5` | PR #493 override-safe native Squad statuses | O | SQUAD; exact priority, unresolved states fail closed |
| 99 | `0b9cd9b5` | PR #492 native Squad status atlas contract | O | SQUAD; exact asset/hash/frame contract |
| 100 | `c51353a7` | PR #491 Squad PSCF numeric fields | O | SQUAD; source-bound numeric controls |
| 101 | `7ecdb33e` | PR #490 Squad role abbreviations | O | SQUAD; source-bound role/text contract |
| 102 | `1a24b456` | PR #489 Squad player names | O | SQUAD; source-bound display-name path |
| 103 | `1301a333` | FMV integration progress | R | Progress only |
| 104 | `4856f6ad` | FMV integration state | R | State only |
| 105 | `beb256a2` | Correct doubled-pixel-writer research | R | FMV research correction |
| 106 | `421a3e1c` | PR #487 native startup FMV presentation | I | FMV source transform proven; EXT contradicts final Windows framing |
| 107 | `0266ad13` | FMV display-integration state | R | State only |
| 108 | `322bca92` | FMV stretch-path progress | R | Progress only |
| 109 | `3226956a` | Exact startup FMV pixel-pipeline research | R | FMV research |
| 110 | `b6e8f23f` | PStartMenu repair status | R | Status only |
| 111 | `d0f2e34d` | PStartMenu derivative progress | R | Progress only |
| 112 | `87868d39` | PStartMenu derivative state | R | State only |
| 113 | `32f02fc8` | Stage/use verified PStartMenu derivative | C | PSTART; exact deterministic source result, timing-only mechanism change |
| 114 | `1ff263f2` | #482 route/TeamSelect latency progress | R | Progress only |
| 115 | `6fa06557` | #482 latency state | R | State only |
| 116 | `3c325a5d` | Defer canonical world build until TeamSelect Start | C | Source lifecycle-compatible removal of reconstruction overhead; EXT says latency still open |
| 117 | `4c045b0b` | Scope management resources to active route | C | Compatibility resource-lifetime optimization; EXT says latency still open |
| 118 | `b8fab87b` | Bound ordinary Squad row helper traces | R | Research tracer only |
| 119 | `e9635ee0` | Native startup FMV geometry status | R | Status only |
| 120 | `a630a34e` | Native startup FMV geometry progress | R | Progress only |
| 121 | `2b33de0a` | Native FMV/private-source state | R | State only |
| 122 | `40e99eaa` | Executable movie-surface/blit trace | R | FMV research |
| 123 | `f4d23116` | Native startup FMV display geometry | R | FMV research |
| 124 | `b669b253` | Reopen Gate 13 on regression #482 | R | Status only |
| 125 | `6252923c` | Regression-audit progress | R | Progress only |
| 126 | `193d29f7` | Mark prior Gate-13 closure superseded | R | Documentation only |
| 127 | `af75dabc` | Promote external playability regression | R | Fidelity/status only |
| 128 | `ac0e4077` | Prioritize external regression #482 | R | State only |

## Behavior adjudication

### Exact PStartMenu derivative — C

**Expected original behavior.** The menu is the exact recovered 800x600
composition using the source background, 23-frame Button@ease atlas, Zurich
font and English strings.

**Modern difference.** The port precomputes immutable render inputs rather than
re-decoding them from the canonical executable/resources on every launch.

**Equivalence evidence.** PSTART pins the canonical EXE-derived decoder slices,
six exact source identities, manifest SHA-256 and component/payload hashes; CI
generated the derivative twice and compared bytes.

**Why original-first.** The optimization starts from the proven source render
and changes only when that deterministic work is performed.

**Mismatch risk.** Hash/schema drift. It fails closed on mismatch.

**Action.** Retain. It does not prove the remaining menu-transition latency is
acceptable.

### TeamSelect/world-build and route-scoped resource loading — C

**Expected original behavior.** New Game enters TeamSelect; selected users are
created from clicked club rows and Start continues from the selected user list.

**Modern difference.** The clean port delays its expensive reconstructed
GameState/schedule materialization until Start and decodes management resource
families only when needed.

**Equivalence evidence.** The TeamSelect navigation/user-selection traces
source-close the New Game/Start boundary and user ownership. These changes do
not invent a selection or gameplay rule and retain fail-closed multi-user
limits.

**Mismatch risk.** Loading/input timing is player-visible. Daniel's later
normal run still reports extremely slow transitions.

**Action.** Retain the bounded optimizations but withdraw any claim that issue
#482 latency is fixed. Continue source-lifecycle profiling after this audit.

### Startup FMV — I

**Expected original behavior.** Canonical TGQ frames are coded 320x480; startup
flag 0x40 selects an exact two-identical-pixel horizontal writer to 640x480.
The original game then presents that 640x480 surface 1:1 at (80,60) inside its
ordinary 800x600 display.

**Modern difference.** The port bakes the proven horizontal duplication into a
640x480 MP4 and presents it in a child WPF HWND inside a desktop-sized
compatibility Tk host.

**Equivalence evidence.** The decode/derivative geometry itself is
source-proven. The WPF child mechanism passes controlled Windows tests.

**Contradiction.** Daniel's normal Windows run still shows the intro offset or
misframed inside the movie field. That external observation overrides the
earlier implication that the complete visible transport was equivalent.

**Action.** Retain the exact derivative transform; downgrade final Windows
placement/transform to INCONCLUSIVE. No Gate-13 acceptance claim until the
desktop/Tk/child-HWND coordinate/DPI transform is diagnosed on the normal
package.

### WPF owner pumping — C

The original is synchronous from the game's perspective. The modern HwndSource
requires the owning Tk thread to service Windows messages before mainloop.
Controlled blocked/pumped tests prove that a bounded Popen/communicate pump
changes the compatibility transport rather than source sequence, media, parent,
geometry or success condition. Hidden menu interaction remains rejected while
the pump runs. Retain.

### Squad component work — O, complete landing still open

The in-scope name, role, numeric/status and Cup-Tied/Non-EU slices use canonical
executable addresses, RTTI, original resources/hashes, ordered roster data and
source-priority rules. They are not guesses and can remain.

That does **not** mean the fresh Squad landing is complete. Daniel's Southport
run showed blank/missing header/name content. The external contradiction is an
integration/completeness failure, not evidence that the source-proven row
contracts are wrong. Gate 13 therefore remains open for a fresh-game live-data
binding audit and Windows visible acceptance.

### Cup-Tied corrections — O final behavior, superseded research retained as R

Recovery 354 temporarily misidentified transfer-history +0x18 as an appearance
count. Recovery 357 re-traced the setter argument order and independently
confirmed +0x18 is a date, identified the owner as DBRGame, and source-closed
the selector plus +60/+207-day cutoff lifecycle. The final integrated code uses
that corrected date model. The false-lead research commit remains historical R;
it is not active behavior.

### Match Detail / PPreMatch work-ahead — O but not a Gate-14 completion claim

The mode values, modal dispatch, resources, geometry, text, marker/rating
mechanics and paint-order slices are backed by canonical executable/resource
evidence. The management action that launches match processing remains
fail-closed and the missing 3D paths are not substituted. These original-proven
modules may remain while Gate 13 is the earlier validation gate.

### Settings — D

The Settings surface explicitly described itself as an intentional
modernization. It was nevertheless wired into the normal production
`build_original_game_presenter()` path and package smoke required it, which
violated the now-canonical original-first policy.

Audit corrective PR #540 removes Settings resources from the default presenter
and changes package smoke to require exactly the four source PStartMenu control
IDs 1,2,3,4. The Settings implementation remains preserved for a later
modernization phase.

### Gate-17 material work — R

The FFmpeg source-contract, link-input, license/source-material and
redistribution work does not switch the normal FM2001 runtime to a new gameplay
or presentation behavior. It remains useful research/infrastructure, but it is
frozen and cannot advance Gate 17 while Gate 13 original behavior is unresolved.

## Unsafe or Unproven Active Behavior

| Surface | Audit finding | Required disposition |
|---|---|---|
| Default Settings control/surface | Deferred modernization leaked into normal baseline through PR #532 | **Isolate**. PR #540 removes default injection and package requirement. |
| F11 / Alt+Enter / Escape fullscreen key interception | Pre-dates the #482 audit range (introduced by pre-scope #428), has no recovered original input basis, and Escape directly contradicts Daniel's startup observation | **Unsupported on original baseline**. PR #540 removes the bindings while preserving helper methods for a future explicit modernization path. |
| Startup FMV final Windows child placement | Exact source movie transform is proven, final desktop/Tk/WPF transform is externally contradicted | **INCONCLUSIVE**. Keep derivative; diagnose compatibility coordinate/DPI mapping before acceptance. |
| Startup skip/Escape semantics | Backend documentation explicitly does not claim the original skip-input behavior | **Fail closed** after PR #540; recover original executable input path before binding a key. |
| Menu transition latency | Prior optimizations are bounded, but Daniel still observes multi-second/very slow transitions | **Open Gate-13 regression**. No resolved claim. |
| Fresh Southport Squad landing | Source row pieces are proven, but normal fresh-game integration is visibly incomplete | **Open Gate-13 regression**. Audit live bridge/header/name binding; no completeness claim. |
| Gate-17/Settings work-ahead | Useful but not part of original baseline | **Frozen/deferred** until earlier original behavior is restored. |

## Reconciliation of Daniel's four external contradictions

1. **Intro video misframed/offset.** Accepted as authoritative negative
   evidence. PR #487 is not treated as complete visible equivalence. Only its
   source-derived frame transform remains proven.
2. **Escape during startup invokes fullscreen behavior.** Confirmed in current
   host code: the root globally bound Escape to `leave_fullscreen`. This was a
   pre-scope modernization convenience, not original evidence. PR #540 removes
   the interception instead of inventing a skip action.
3. **Menu transitions extremely slow.** The derivative, deferred world build
   and route-scoped resource work are retained as compatibility optimizations,
   but their prior "fixed" implication is withdrawn. External performance
   acceptance remains open.
4. **Fresh Southport Squad incomplete.** Exact Squad component contracts remain
   valid, but full fresh-game presentation is not accepted. Gate 13 stays open
   for the live-data/integration repair.

## Audit Exit Criteria

- [x] Every in-scope first-parent commit from the reopen base to the audit
  snapshot is enumerated: **128/128**.
- [x] Every behavior-affecting in-scope item has a primary classification and
  evidence/action.
- [x] Historical false leads that were later corrected are separated from final
  active behavior.
- [x] Daniel's four external contradictions are reconciled without overriding
  them with CI evidence.
- [ ] PR #540 corrective isolation is merged after focused/full/package checks.
- [ ] Canonical `CURRENT_STATE.md`, `project_status.json` and
  `research/PROGRESS.md` are reconciled to the audit result.
- [ ] The exact next source task is activated only after the correction checks
  pass.

The audit therefore remains **implementation-frozen only until the three
unchecked persistence/validation items above are complete**. Gate 13 itself
remains open after audit exit.

## Exact next original-proven Gate-13 source task

After PR #540 and canonical-state reconciliation, trace the **original startup
movie input/skip path** from the canonical executable, starting at the already
proven startup wrapper `0x461E20 -> 0x461900` and its surrounding playback
loop. Determine exactly which keyboard/mouse events, if any, terminate or alter
the two intro clips, with special attention to Escape. Persist the instruction
addresses/control flow and do not bind Escape (or any replacement key) until
that behavior is source-closed.

In parallel only where independent, the next compatibility diagnosis is the
normal-package Tk/WPF coordinate/DPI transform that causes the externally
observed FMV framing mismatch. The source logical target remains fixed at
640x480 at (80,60) in the original 800x600 game coordinate space.
