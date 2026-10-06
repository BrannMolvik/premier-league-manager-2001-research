# Recovery 347 continuation — PR #497 merged; Windows manifest EOL regression repair active

_Updated 6 October 2026._

Canonical `main` is now `a881d628449e4ea05e9b31952aee3cdc3abb93b2`,
which merges PR #497's source-closed special Non-EU/frame-12 Squad lifecycle.
**Gate 13 / issue #482 remains the earliest incomplete validation gate** and
still requires Daniel's normal Windows 11 playability/visual acceptance.

PR #497 exact-head validation passed before merge:

- full reconstruction run `37473657785`: success;
- Gate-13 presentation run `37473657873`: success;
- repository asset-policy run `37473657782`: success.

Issue #482 now has a newer external packaged-build blocker from Daniel's
Windows test. The packaged
`original_assets/converted/pstartmenu-v1/manifest.json` was checked out with a
CRLF final newline, changing its exact byte hash from pinned
`cc541cac0e844abdb7539627ea68a982288c0ba735a6bf91c84d3c502961877e`
to `cfd3d38126769b732c5f0215872f8574b589988c733649e7f81d0799785d5b7d`.
The runtime correctly failed closed with
`PStartMenuDerivativeError: Derivative manifest identity differs from the pinned receipt`.

Active cloud-safe repair is PR #498,
`recovery347-package-manifest-eol`, currently refreshed onto this main at
`f49657133e288527db8c1b54f3b5bd8115b81665`. It:

- forces LF for the exact-byte PStartMenu manifest via a narrow
  `.gitattributes` rule and marks the XZ payload binary;
- makes frozen `--package-smoke` fully verify the staged PStartMenu derivative
  with the existing pinned hash/provenance contract;
- adds a CRLF regression proving the fail-closed receipt check fires;
- adds that smoke test to the Windows package workflow.

Exact next task: require PR #498's refreshed-head Gate-13, reconstruction,
asset-policy, and especially Windows package/frozen-smoke workflows to pass.
Merge only if green, then use the resulting Windows artifact for the next
external #482 run.

The private mode-1 Cup-Tied trace remains separately deferred by the current
execution sandbox. The authorized 511,121,336-byte Library archive
rematerializes successfully, but shell/Python process execution is unavailable.
When a functioning sandbox returns, resume exactly at
`0x422E7E -> CPlayerTransferHistory::0x4EBF60` and then trace
`0x8755E8/0x8755EC/0x8755F0`; do not infer those semantics.

---

# Recovery 347 continuation — frame 12 candidate green; Cup-Tied transfer-history trace blocked only by execution sandbox

_Updated 6 October 2026._

Canonical `main` remains `3c17eaa1dc5a9491699d92ec99489bb796660753`.
**Gate 13 / issue #482 remains the earliest incomplete validation gate** and
still requires Daniel's normal Windows 11 playability/visual acceptance.

PR #497 branch `recovery342-gate13-status-lifecycle` now contains the
source-closed special Non-EU/frame-12 implementation at
`45c5c0e09c9fec420160e9e60eedf304423fcfd9`. Exact-head validation is green:

- full reconstruction run `37467142990`: success;
- Gate-13 presentation run `37467143159`: success;
- repository asset-policy run `37467143070`: success.

That candidate now publishes frame 12 only when DBRPlayer bit 11 is active and
the synchronized registration/contract cutoff is expired, preserves the exact
higher-priority alternate On-loan frame 13, allows a lower positive Cup-Tied
result when an active bit-11 cutoff is still current, and applies the
source-proven sticky post-transfer bit-11 set transition. Internal save already
persists both the bit and contract expiry, so no save-schema change is required.

Recovery 346 continued the canonical executable trace and identified the
remaining mode-1 Cup-Tied embedded state more precisely:

- DBRPlayer `+0x198` is an embedded `CPlayerTransferHistory` object;
- DBRPlayer `+0x1A0` is that object's `+0x08` club-table index/club ID;
- embedded `+0x18` is a transfer/join-history date, initialized from the
  normalized current-club join date at DBRPlayer `+0x158`.

The exact unresolved source step is to finish the `0x422E7E` call into
`CPlayerTransferHistory::0x4EBF60` so every argument/update is identified,
then trace the producers and semantic meaning of globals
`0x8755E8/0x8755EC/0x8755F0`. Until that is complete, the negative mode-1
Cup-Tied fallback remains fail-closed.

Recovery 347 successfully rematerialized the authorized 511,121,336-byte
Library source archive, but the current execution allocation cannot launch even
a trivial shell or Python process: container execution returns
`caas.internal.errors.ClientError`, while Python returns a
`TooManyRequestsError`. This is an execution-sandbox blocker only, not a
source-availability blocker. The archive remains available at the canonical
Library location recorded in `research/ORIGINAL_SOURCE_LOCATOR.md`.

Under the deferred-blocker policy, finish integrating the already-green PR #497
candidate, then continue independent cloud-safe Gate-13/Gate-14 work while
preserving the exact native-trace step above for the next functioning execution
sandbox. Do not infer the unresolved cutoff globals.

---

# Recovery 342 continuation — native Squad status lifecycle narrowed

_Updated 6 October 2026._

Canonical `main` is `3c17eaa1dc5a9491699d92ec99489bb796660753`, including merged PR #496. **Gate 13 /
issue #482 remains the earliest incomplete validation gate** and still requires
Daniel's normal Windows 11 playability/visual acceptance.

Recovery 342 restored the authorized original-source path and independently
re-extracted canonical `footballmanager.exe` from the supplied MODE1/2352
disc image. The executable again hashes exactly to
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

First-hand disassembly now closes more of the two remaining Squad-status
boundaries without publishing an unsafe frame:

- `0x421760`, already represented by `derive_non_eu_status()`, is the exact
  native eligibility predicate used by the loaded-player initialization pass;
- `0x421CE0 -> 0x417A20` sets DBRPlayer `+0x14` bit 11 and creates the
  registration record for qualifying players;
- registration record `+0x14` is copied from DBRPlayer `+0x154`, now
  source-closed as contract expiry, and `0x4E9BE0` tests
  `current_date <= cutoff`; frame 12 occurs only after that cutoff;
- renewal/finalizer paths keep the record cutoff synchronized to live contract
  expiry, while full reset `0x41AFE0` clears bit 11 and removes the record;
- ordinary transfer `0x422F70` preserves an already-active bit through the
  contract finalizer; the only two `0x4EF600` callers are the native
  `TransferDealConcluded` and `FreeTransferDealConcluded` handlers, where a
  positive `0x421760` result sets bit 11 and a negative result does not clear
  it; `0x41B4D0` lazily creates a missing registration record when needed;
- mode-1 Cup-Tied fallback helper `0x419350` returns embedded
  `DBRPlayer+0x198+0x18` when `+0x1A0 > -1`; it is not a first-list-element
  lookup. Its producer semantics and global cutoffs remain unresolved.

Durable evidence is in
`research/GATE13_SQUAD_STATUS_LIFECYCLE.md`. No proprietary executable,
archive, disc image or raw disassembly entered Git.

Exact next task: trace the producer semantics of embedded
`+0x198/+0x18`, gate `+0x1A0`, and globals `0x8755E8/EC/F0`. The
ordinary-transfer bit-11 transition is now source-closed as sticky until the
full reset/removal lifecycle. Keep frame 12 and the mode-1 negative Cup-Tied
fallback fail-closed until the remaining source semantics are reconciled with
the clean runtime.
---

# Recovery 341 continuation — PR #495 merged; Gate 13 external acceptance still open

_Updated 6 October 2026._

Canonical `main` is now `0a91c088f14f5988ab96430de5dc9239b24457cf`.
PR #495 merged the source-qualified Squad Cup-Tied / alternate On-loan status
slice after the complete candidate validation set passed. **Active gate remains
Gate 13 / issue #482.**

Exact merged-candidate evidence:

- Gate 13 presentation run `37424300671`: success;
- repository asset-policy run `37424300703`: success;
- Windows package/smoke run `37424300615`: success;
- full reconstruction run `37424300721`: success;
- Windows candidate artifact `11394291084`,
  `FM2001-Windows11-94a620839624f293c0d4343f7e42c9ddfb31d549`,
  Actions digest
  `sha256:8fb7c6359a42a78a30f5c5ea91940789214725bf6d76818353adb2f13f9afb62`.

The live Squad status path now preserves native priority for direct frames
0/1/2, exact alternate On-loan frame 13, and positively proven current-day
Cup-Tied frame 3. A true Non-EU state still blocks lower publication because
its separate registration-expiry lifecycle is unresolved. The mode-1 negative
Cup-Tied transfer-history cutoff and club-relative assignment also remain
source-evidence blockers.

Gate 13 is **not complete**. Daniel's normal Windows 11 #482 acceptance remains
mandatory and must verify startup presentation, responsiveness, the usable
Southport Squad landing, and ordinary management navigation.

Independent cloud-safe next task: repair the stale Gate-14 startup-media
external acceptance audit. It still mandates the obsolete MCI transport even
though normal Windows launch now uses `WindowsWpfStartupMediaBackend` bound as
a child HWND of the game-owned 800x600 host. The acceptance tool must exercise
the production WPF child-window path before any future startup-media receipt is
trusted.

---

# Recovery 341 continuation — source-qualified Squad Cup/loan status candidate

_Updated 6 October 2026._

Canonical `main` remains `3eeb5b92605f338499a6dcbc132e1187856508c9`.
Recovery branch `recovery340-squad-cup-tied-resolver` now carries the next
Gate-13 candidate. **Active gate remains Gate 13 / issue #482.**

Recovery 340 source analysis closed the safe positive boundary around
`0x418480`: the current club must have a match on the global current date,
that match competition resolves through the Cup root predicate, and a positive
`0x4F8E40 -> 0x4E9710` collection result returns Cup-Tied immediately even
for restriction mode 1. The branch also retains packed competition +0x24 and
projects exact Cup runtime +0x34 modes 0/1/2.

The live presenter is now wired, not merely helper-complete:

- native direct frames 0/1/2 retain highest priority;
- exact alternate On-loan state publishes frame 13;
- `RuntimePlayer.non_eu == true` still blocks lower publication because the
  registration-expiry lifecycle is not yet complete;
- frame 3 publishes only from a positive Cup-Tied lookup for a pending primary
  entry that is still present in the recovered scheduler order for the current
  date;
- every unsupported lower/negative path remains fail-closed.

Focused resolver, presenter and source-bridge tests now cover the priority and
current-day context boundary. Next: validate this candidate through the normal
PR reconstruction/presentation/package/asset checks, merge only if green, then
continue source-closing the mode-1 transfer-history cutoff / Non-EU lifecycle
or the next independent source-backed Gate-13 fidelity slice. The mandatory
normal Windows 11 #482 acceptance remains external evidence and Gate 13 must
not close before it passes.

---

# Recovery 338 continuation — Cup-Tied runtime state candidate

_Updated 6 October 2026._

Canonical `main` is `7e1597e51e508188a827e4709813c5f7d6d6e975`.
PR #493 merged override-safe native Squad status frames 0/1/2.
**Active gate remains Gate 13 / issue #482.**

The current candidate is PR #494 on branch
`recovery338-cup-tied-state`. Fresh analysis of the hash-verified canonical
executable closes the separate Cup-Tied state path:

- `0x41B7E0 -> 0x4F8E20 -> 0x4E9690` records a player's ID and current club
  only after the player actually appeared in a qualifying match.
- The record is owned by the root competition selected through `0x4F3DC0`;
  root virtual +0x18 is true for Cup/DummyLeague and false for ordinary League.
- `0x4E9690` is idempotent by player ID, so the first qualifying club remains
  authoritative.
- `0x4F8E40 -> 0x4E9710` returns true only after that player is now queried
  with a different club.

The clean runtime now materializes those root-scoped collections at the existing
`0x404CE0`-equivalent shared post-match seam, including procedural League
children under Cup roots. Internal save schema 45 persists the collections and
fails closed on duplicate player records. Focused collection/GameState/save
round-trip tests are included. PR-head repository asset-policy validation has
passed; the full reconstruction suite is still the gating candidate check.

Do **not** render PSCF frame 3 solely from the collection yet. The exact
`0x418360` priority still evaluates alternate On-loan frame 13 and special
Non-EU frame 12 first, and `0x418480` itself contains current-calendar
competition-context/date logic around the Cup-Tied lookup. Next, after PR #494
is green and merged, source-close that remaining `0x418480` context/date
predicate and expose frame 3 only where the complete resolver is equivalent.
Club-relative assignment remains unresolved. The mandatory normal Windows 11
#482 acceptance remains external evidence and Gate 13 must not close before it
passes.

---

# Recovery 336 continuation — direct Squad statuses active

_Updated 6 October 2026._

Canonical `main` is `0b9cd9b53cd525c3b4af2a27f8c1ddbf6a101a93`.
PR #492 merged the exact original Squad status atlas/source-table contract.
**Active gate remains Gate 13 / issue #482.**

The current branch is `recovery336-squad-direct-status`. Canonical executable
analysis now closes the `0x401DE0 -> 0x418330 -> 0x418360` priority boundary.
In PSCFRow context, status-table indices 0/1/2 are the only scan results that
return before the later override helper, and the recovered Static.dat table
identifies them exactly as Injured, Banned and International. Bit 2 is therefore
no longer merely a neutral selection-exclusion label.

The implementation decodes the already pinned byte-identical
`FM2001_Art/Generic/status.png` and renders only those three override-safe
frames at native PSCFRow geometry `(1,1,18,14)`; the first visible first-roster
icon lands at screen `(277,234)`. Every lower-priority status remains
fail-closed.

The remaining native override chain is bounded: alternate On-loan frame 13,
special Non-EU frame 12, separate Cup-Tied frame 3, bit-15 frame 10, bit-12
frame 6, then fallback. The clean runtime still lacks the exact competition
Cup-Tied collection and the separate Non-EU registration-record date state.

Next: validate this branch through the focused/full reconstruction, Windows
package/smoke and asset-policy workflows, merge only if green, then materialize
the exact Cup-Tied runtime state from its proven producer/lookup path before
expanding lower-priority status rendering. Club-relative assignment remains
unresolved. The mandatory normal Windows 11 #482 acceptance remains external
evidence and Gate 13 must not close before it passes.

---

# Recovery 335 continuation — Squad status atlas/source table pinned

_Updated 6 October 2026._

Canonical `main` is `c51353a75c9360cdc1e45b8ee4fe1c3c5be2f07d`.
PR #491 merged the source-backed PSCFRow Condition, recent-form and
current-role-rating controls after all four candidate validations passed.
**Active gate remains Gate 13 / issue #482.**

The exact current branch is `recovery335-squad-status-icon`. Recovery 335 has
now imported and provenance-pinned the byte-identical original
`FM2001_Art/Generic/status.png` (4,015 bytes; SHA-256
`59cd053c93ea789a010d813f46f650c2e4c16ea46163c63ae01209f69e4f5b1b`).
Canonical initializer `0x603940` slices the 18x196 RGB image into fourteen
vertical 18x14 entries stored from `0x87BBF0` in 0x20-byte steps.

The serialized player-status definition table at Static.dat `0x26F2` is also
source-closed: twelve ordinary definitions in order are Injured, Banned,
International, Cup Tied, First Team, source-spelled "Subsitute", On loan,
Out of contract, Transfer listed, Bid in, Wanted, and Non EU. Frames 0..11
correspond to that ordinary source order; frames 12 and 13 are later native
alternate Non-EU and On-loan frames.

The implementation currently validates only the exact atlas/frame contract.
It deliberately does **not** render the status column yet. Native resolver
`0x418330` / override helper `0x418360` can replace fallback statuses using
state the clean runtime does not yet represent exactly, most importantly the
separate Cup-Tied collection and a special Non-EU registration branch.
Rendering a fallback icon before those priorities are closed could therefore
show a wrong status and remains fail-closed. Club-relative assignment is still
unresolved as well.

Next: source-close the remaining `0x418330` priority/override predicates and
map only exact represented runtime state. If the missing Cup-Tied source state
must be materialized first, do that as the next backend-safe slice before
drawing status pixels. Then run focused/full CI, Windows package/smoke and
asset-policy validation before merge. The mandatory normal Windows 11 #482
acceptance remains external evidence and Gate 13 must not close before it
passes.

---

# Recovery 334 continuation — PSCFRow numeric controls active

_Updated 6 October 2026._

Canonical `main` is `7ecdb33e060ed751288e76ed8cbdf71c9876aba9`.
PR #490 merged the source-bound assigned-role abbreviation renderer after all
four candidate validations passed. **Active gate remains Gate 13 / issue #482.**

The exact current branch is `recovery334-squad-scf-numeric`. Fresh canonical
executable analysis has now source-closed the paired `PSCFRow` numeric
presentation: `CSquadSCFList` local x=239, Condition/recent-form/role-rating
controls at x=24/47/70 with 19x14 geometry, raw text flags `0x24`, exact
`Zurich_XCn_BT_18pixel.fnt`, whole-number `%N` formatting for Condition and
rating, one-decimal `%.N` formatting for form, and the strict source
Condition threshold `>75`. Fresh-state colors are white above 75, RGB
`(0,45,255)` at/below 75, and white for recent form/rating.

The implementation renders only these three resolved fields on the fresh
combined Squad viewport. The native status icon and club-relative assignment
remain fail-closed, as do reserve/post-transition semantics not yet recovered.

Next: run focused/full CI plus Windows package/asset-policy validation on this
branch, merge only if green, then continue the next independent source-backed
Squad fidelity slice. The mandatory normal Windows 11 #482 acceptance remains
external evidence and Gate 13 must not close before it passes.

---

# Recovery 332 continuation — Squad names merged; assigned-role abbreviation active

_Updated 6 October 2026._

Canonical `main` is `1a24b456f763a8f8899b2eb940a8316bf35aef2b`.
PR #489 merged the source-bound first-roster player-name renderer after all four
candidate validations passed: reconstruction `37399160903`, Gate-13
presentation `37399160894`, Windows package `37399160807`, and repository
asset policy `37399160815`.

The merged row path now preserves native initial+surname formatting, the exact
18px Zurich font, first-team active/substitute source colors, and fail-closed
withholding when the unmodeled reserve-selection pair would be needed to choose
a color.

**Active gate remains Gate 13 / issue #482.** The current source-backed follow-up
is the ordinary assigned-role control. Fresh canonical executable analysis
proves `PSquadPlayerRow::0x489530` reads the current role's runtime Position
record `+0x0C`; the Position reader stores localized name at `+0x08` and
localized abbreviation at `+0x0C`, matching the clean-room Static.dat
`Position(name, abbreviation, lineup_order, lineup_group)` parse. Therefore
the visible role label is the original `Position.abbreviation`.

Recovery branch `recovery332-squad-role-abbreviation` projects that source
abbreviation from `state.positions`, fails closed when it is unavailable, and
rasterizes it in native first-roster control `(28,1,38,14)` with raw text
flags `0x24`. The already recovered `0x4EA3F0` predicate selects source RGB
`(255,255,255)` for a preferred-role match and `(0,0,125)` otherwise.
Runtime packed-16 mask identity remains a separate unresolved display receipt;
no RGB565/RGB555 assumption is introduced.

After this slice is verified and merged, continue the next source-backed Squad
fidelity work that does not invent reserve/status semantics. The mandatory
normal Windows 11 #482 acceptance remains deferred external evidence and Gate 13
must not close before it passes.

---

# Recovery 330 continuation — startup FMV candidate merged; continue Squad fidelity

_Updated 6 October 2026._

Canonical `main` is now
`421a3e1c34e007c1e9550aea892678fa95dde261` plus the immediately following
Recovery-330 research reconciliation checkpoint.

PR #487 is merged and closes the repository-side startup-FMV geometry/window
repair candidate for issue #482:

- exact coded TGQ geometry remains 320x480;
- startup wrapper flag `0x40` selects the doubled 16-bpp TQI writer;
- the ordinary game display initializes BPP `0x8547A8 = 0x10` at
  `0x615256`;
- ordinary writer `0x69DC20` emits 0x20 bytes per 16 coded horizontal samples,
  while startup writer `0x69DCC0` emits 0x40;
- lookup helper `0x69C1A0` mirrors packed channel bits into the upper 16 bits,
  so each startup DWORD is two identical packed16 pixels;
- compatibility media now bakes the recovered exact horizontal 2x duplication
  as `scale=640:480:flags=neighbor`;
- the final original presentation remains a 1:1 640x480 blit at (80,60) in the
  ordinary 800x600 game mode;
- the Windows WPF MediaElement transport is now hosted as a child HWND of the
  realized fullscreen FM2001 Tk window instead of creating a separate
  maximized top-level window.

PR-head reconstruction, Gate-13 presentation, asset-policy and Windows package
workflows were all green before merge. A fresh merged-head CI run and
human-visible/audible Windows 11 acceptance are still required before this
criterion can be called closed.

**Active gate remains Gate 13 / issue #482.** The highest-priority independent
cloud-safe task is now the ordinary Squad player-row fidelity blocker: recover
enough of helpers `0x4EA3F0` and `0x5D6C50` to source-bind display names and
row colors/styling for the already closed geometry/data/font path, without
inventing visual semantics. Continue that trace while Windows startup/media,
responsiveness, TeamSelect and first-management/Squad acceptance remain
deferred external checks.

Do not close Gate 13 until bundled Windows 11 acceptance passes.

---

# Current State

_Last reconciled: 6 October 2026 KST_

This is the **canonical live resume point**. Historical chronology belongs in
`PROGRESS.md`; established technical evidence belongs in `FINDINGS.md` and
topic-specific research files.


## Recovery 329 continuation — PStartMenu cold-start derivative canonical; Gate 13 still open

Canonical `main` is now `32f02fc86f0eb404c0f410cbceb131f56f0ddaf0`.

PR #486 is merged and closes the repository-side PStartMenu cold-conversion
repair for issue #482:

- the exact canonical EA444 decoder inputs were re-extracted from the authorized
  root `footballmanager.exe` and provenance-tracked as the 0x420-byte TQIA
  block SHA-256
  `c62a13efbb812fb2157c067aaa3eae8afbbb52283dc5dc3eaf6cb86c5a11e8da`
  and 0x100-byte quantization block SHA-256
  `6fb2af66cb6a51e4b3fa7da9bacab417fa40f180aa0c18c85adb2550c04c89eb`;
- Gate-13 CI regenerated the PStartMenu derivative twice from tracked original
  sources and compared the results byte-for-byte before staging them;
- the canonical derivative manifest SHA-256 is
  `cc541cac0e844abdb7539627ea68a982288c0ba735a6bf91c84d3c502961877e`;
- the tracked XZ payload is 718,884 bytes, SHA-256
  `2428510481442c5334bbdce806bd9c9919ce1a59f1d321c536432d5501199697`;
  its decoded 2,315,939-byte render payload is SHA-256
  `a73badbb141334441ed0893114238d9fedc75de0580588bddb2f894e986c3f55`;
- normal repository/packaged startup now loads only that independently pinned
  derivative for PStartMenu and fails closed on manifest/payload/provenance
  drift. Explicit custom source-root research calls retain the original cold
  source-decoder path. There is no silent fallback from normal runtime to the
  previously measured 26.301-second conversion;
- exact local XZ decompression was roughly 29 ms median in the recovery
  environment. This demonstrates removal of the expensive conversion class but
  is **not** a substitute for Daniel's Windows 11 timing acceptance;
- final PR-head checks all passed: Gate-13 `37386883275`, Windows package
  `37386882889`, repository asset policy `37386883101`, and full
  reconstruction `37386883155`.

Gate 13 remains open. The next independent #482 blockers are:

1. recover enough of the ordinary Squad player-row color/display-name helpers
   (`0x4EA3F0`, `0x5D6C50`) to render the already source-closed row
   geometry/data/fonts without inventing styling;
2. repair startup FMV presentation from the separate maximized WPF player to
   the source-proven game-owned 640x480 presentation rectangle centered at
   (80,60) in 800x600 mode. The TGQ `pIQT` header is directly confirmed as
   320x480, so the precise legacy horizontal expansion path still needs a
   source-backed explanation before implementation;
3. after those repairs, perform Daniel's meaningful normal Windows 11
   acceptance run, including the new `startup.presenter_build` and
   `teamselect.catalog_build` timings.

Private/static-source execution is healthy again in this recovery. Do not
reopen the old decoder-input blocker.

**Exact next task:** continue the private-source FMV decode/display trace far
enough to explain the 320x480 `pIQT` frame's relationship to the real 640x480
movie surface, focusing on actual display bit depth/pixel packing and the
state-4 writer path. Do not guess interpolation. If that remains unresolved,
continue the independent Squad helper trace rather than blocking all useful
work.


## Recovery 326 continuation — route/New-Game latency slices canonical; Gate 13 still open

Canonical `main` is now `3c325a5d1d81b44d1f43da6dc53d4d1e33f988f1`.

Issue #482 Phase 1 and Phase 2 are both merged and verified:

- PR #483 merged as `4c045b0b75fc4d6061e06e23d8089c2a08a5c475`.
  Fresh MANAGEMENT is route-scoped: Squad loads only PMenu, Squad top controls,
  management background and management header; Fixtures/PMatchInfo and League
  Tables load only on their first route entry, remain off the Tk thread, fail
  closed on errors and are cached thereafter. Fresh post-base checks passed:
  reconstruction `37372720405`, Gate-13 `37372720352`, asset policy
  `37372720354` and Windows package `37372720390`.
- PR #485 merged as `3c325a5d1d81b44d1f43da6dc53d4d1e33f988f1`.
  Canonical New Game now verifies/parses the canonical database into a
  TeamSelect catalog but does **not** construct GameState, the primary schedule
  or the full gameplay world. TeamSelect renders from countries/competitions/
  clubs in that catalog; Start materializes `HumanGameplayController` from the
  same parsed database, so it does not parse canonical files a second time.
  Deferred world-build failures keep TeamSelect retryable. The final head
  `b8efab946ad8a834fabd3b3286f6a64e4efd0dae` passed Gate-13 run
  `37376279197`, repository asset policy `37376279127`, and full
  reconstruction run `37376279059`. The Windows package workflow is
  path-filtered away from these files; no package-pass claim is inferred from
  non-triggering.
- The catalog boundary deliberately still uses the existing eager
  `FM2001Database` parser. It removes the heavier world/schedule construction
  from New Game without introducing a second parser. The new
  `teamselect.catalog_build` timing should be measured on Daniel's next normal
  Windows run before deciding whether a narrower catalog parser is warranted.

Gate 13 is **not** closed. The remaining #482 acceptance blockers are:

1. The fresh Squad landing still lacks the ordinary player-row renderer. Exact
   role/name geometry and fonts are source-closed, but the player-row packed
   color branch (`0x4EA3F0`) and display-name helper (`0x5D6C50`) remain
   insufficiently traced. Do not substitute white or a modern palette.
2. Cold `startup.presenter_build` previously measured 26.301 seconds. A
   deterministic staged first-screen derivative is the preferred fix, but the
   exact EA444 decoder inputs needed for package-independent generation are not
   yet available as a clean-room public constant set. The authorized private
   executable remains the source of truth.
3. Startup FMV presentation must move from the separate top-level WPF player to
   the source-proven game-owned 640x480 movie rectangle centered at (80,60) in
   800x600 mode. Exact 320x480 -> 640x480 pixel expansion/interlace treatment
   remains evidence-open.
4. Daniel must perform a meaningful normal Windows 11 acceptance run after these
   repairs. #482 and Gate 13 cannot close from CI alone.

Private/source execution is again infrastructure-blocked: trivial container,
notebook Python and visible Python process starts currently raise
`caas.internal.errors.ClientError`. The authorized disc/archive and retained
trace remain available through connected Files, but missing executable helper
semantics must not be invented.

**Exact next task:** continue the highest-priority independent Gate-13 repair
that does not require guessed private semantics. Prefer source-safe cold-start
derivative infrastructure/provenance work that can be completed without the
missing decoder bytes, while periodically retrying private execution to close
the Squad helper and decoder-input evidence. Do not start external Windows
acceptance until the renderer/startup regressions have a meaningful candidate.

## Recovery 322 continuation — external Windows playability regression #482 reopens Gate 13

Daniel's real Windows 11 hands-on run supersedes the prior Gate-13 external
acceptance interpretation. Current `main` at the start of this audit was
`6030cbae46d8a15386d6b6114a11bcd35e8984dc`. Issue #482 is now the priority
regression and Gate 13 is again the earliest incomplete validation gate.

The audit separates the observed problem into source-backed implementation
boundaries rather than one generic performance complaint:

- The first-screen caching work from `72aedde11690ecaa2d9290482b477eb1440f44a7`
  is still present. The remaining measured `startup.presenter_build = 26.301s`
  is cold source conversion: executable table/quantization derivation, EA444
  background/button decode, font/language parsing and final source-identity
  verification.
- Start New Game still constructs the full canonical gameplay world and primary
  schedule synchronously inside `FrontEndSession.dispatch()` before TeamSelect
  appears. Daniel's measured first pointer transaction was **3.355s**.
- The first management transition still waits for one broad loader containing
  PMenu, fixtures, League Tables, PMatchInfo, Squad, background, header and text.
  The prior external aggregate was **16.724s**. Fixtures/Tables/PMatchInfo are
  unrelated to the fresh Squad landing and must not gate it.
- The management presenter already materializes up to **20 source-backed Squad
  rows**, with recovered 17-pixel row cadence, player/side-column geometry and
  source font identities. The Tk host nevertheless renders only the three
  Squad top buttons. Daniel's sparse Southport screenshot is therefore a real
  renderer omission, not missing backend roster data.
- Some Squad side-column native color transforms, status icons and
  club-relative-assignment styling remain unresolved. Those exact details stay
  fail-closed, but they do not justify omitting the already-recovered row
  geometry/data/font subset.
- The current startup-video backend deliberately creates a separate maximized
  topmost WPF/PowerShell window with `MediaElement.Stretch=Uniform`. Recovery
  322 private-source analysis now proves this geometry is wrong: native
  `0x461900` creates a 640x480 movie surface and `0x461CD0` blits its full
  640x480 rectangle 1:1 into the game-owned display, centered at `(80,60)` in
  800x600 mode or `(0,0)` in 640x480 mode. The exact encoded 320x480 ->
  640x480 pixel interpolation/interlace treatment is still unresolved.

A fresh authorized-source recovery also materially cleared the prior private
execution blocker. The 511,121,336-byte Library ZIP materialized again; the
container shell path still raises `caas.internal.errors.ClientError`, but the
notebook execution path successfully opened the ZIP, extracted the
631,627,248-byte MODE1/2352 track, enumerated the Joliet level-3 filesystem,
and re-extracted the root `footballmanager.exe`. Its SHA-256 reverified as
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
This is sufficient for private static executable analysis even while the shell
path remains unavailable.

A detailed worker directive with these boundaries is persisted on issue #482
(comment 6001127354). Gate-17 FFmpeg work-ahead #475/#479 remains suspended
until this regression is repaired and externally accepted.

**Exact next task:** repair the highest-confidence cloud-safe slice first:
split management resources by route so a fresh Squad landing loads only its
shell/background/header/Squad requirements, and add regression tests proving
Fixtures, League Tables and PMatchInfo resources are not loaded for that first
draw. In the same worker branch, render the already source-closed ordinary
Squad row subset that can be drawn without inventing unresolved status/color
semantics. Verify focused tests and then the relevant full/package CI before
moving to startup/New-Game latency. Keep startup-FMV display-treatment work
evidence-led and require Daniel's normal Windows 11 acceptance before #482 or
Gate 13 can close.

## Recovery 321 continuation — minimal FFmpeg contract needs explicit D3D11VA

Recovery 321 resumed from canonical main `a57ba974c051ef2db29dfe17ec867acb6aaf40bb` and reconciled the older Gate-17 work-ahead PRs against the current repository state.

- PR #475 (`Gate 17: pin minimal FFmpeg source contract`) and stacked PR #479 (`Gate 17: build minimal FFmpeg from pinned source`) are both still open and non-mergeable against current `main` because their branches predate later canonical Gate-14 work.
- #475's earlier reconstruction, Windows-package and asset-policy workflows passed, but that is no longer sufficient evidence for its proposed configure contract. #479's exact-source build run `37352166679` failed deterministically in `libavcodec/mfenc.c` while compiling the pinned FFmpeg commit `46d8f462eeb87ee1f704d8c44a0ee24fca471ad1`.
- The compile errors are missing `ID3D11DeviceContext`, `AVD3D11VADeviceContext`, `ID3D11Texture2D` and `IID_ID3D11Texture2D`. The pinned FFmpeg source includes `libavutil/hwcontext_d3d11va.h` only under `CONFIG_D3D11VA`, while the Media Foundation encoder context uses those D3D11 types. FFmpeg configure exposes D3D11VA as an autodetected capability; the proposed minimal contract uses `--disable-autodetect` and restores Media Foundation but not D3D11VA.
- Therefore #475's minimal-helper source contract is incomplete as written. Do not merge #475 or retry #479 unchanged. The production helper remains unchanged and every minimal-helper promotion flag remains false.
- Durable review directives were posted on #475 and #479 with this diagnosis. This is a source-backed contract correction, not a reason to weaken the fail-closed provenance/import guards or to claim legal compliance.

**Exact next task:** have the implementation worker cleanly reconcile #475 onto current `main`, explicitly restore the D3D11VA capability required by the pinned `h264_mf` source path, and update the source-contract audit/tests/documentation accordingly. Re-run its focused/full/package validation. Only after that corrected contract is canonical should #479 be rebased/recreated and its exact-source Windows build proof rerun. Keep Gate 14 as the earliest incomplete validation gate and keep the real Windows 11 visible/audible WPF startup-media retest deferred until Daniel can perform it.

## Recovery 320 continuation — WPF startup-media transport canonical; external acceptance open

Main advanced through the hands-on gameplay blocker fixes before this checkpoint:

- PR #476 merged as `9bda514e673fff97621110f49b4bf506ecf15fdb`, mirroring the
  recovered source-backed generic seasonal management-background fallback so
  Southport/non-Premiership clubs do not fail on an unstaged club-specific
  background.
- PR #477 merged as `282d9fd1b1b09c772306575d811f47704185682a`, optimizing
  source-faithful EA444 decode reuse and exposing front-end latency stages.
  Its verified full suite passed **2,613 tests / 23 expected skips**.
- PR #480 merged as `8195eedac48a5d361b9dac8f116c0baa6b9ec00d`, adding
  per-family timing inside the previously measured
  `management.resources.load_all` aggregate without changing resource
  semantics. Reconstruction run `37352814705` passed **2,613 tests / 23
  expected skips**; its Windows package, Gate-13 and asset-policy workflows
  also passed.

Issue #437 was then isolated on Daniel's real Windows 11 client. The exact
source-verified startup cache is reached, but the built-in MCI transport fails
at **open**, before playback, with status 277:
`A problem occurred in initializing MCI.` The verified derivative is
`%LOCALAPPDATA%\\FM2001-Windows11\\startup-media\\easp.mp4`; this is a
transport regression, not evidence against the TGQ extraction/conversion/cache
contract.

PR #481 merged as `cb69cc583e367e4ff5d7b65c960eae56e8b81d21` from head
`c59ffc049bfdc813434da54b53a8a0d8eb297e32`. It replaces normal automatic
Windows MCI playback with a stock-Windows WPF `MediaElement` transport hosted
by a synchronous hidden Windows PowerShell STA process. The verified derivative
path is passed through a child-process environment variable rather than
interpolated into PowerShell. The transport uses a borderless maximized black
window with uniform scaling, starts after WPF content rendering, waits for
`MediaEnded`, surfaces `MediaFailed` detail, and bounds a stuck player by the
source-proven decoded clip duration plus 30 seconds of initialization headroom.
The explicit developer external-player override and
`--skip-startup-media` bypass remain intact. The legacy MCI adapter remains
only as a regression/diagnostic seam.

PR #481 final-head validation:
- reconstruction run `37353925792`: **2,619 tests / 24 expected skips**;
- Windows package run `37353925786`: passed exact candidate staging, the
  package-specific tests including a real Windows
  `PresentationFramework`/`MediaElement` instantiation smoke, PyInstaller
  freeze, frozen executable smoke, deterministic archive build and upload;
- focused Gate-13 run `37353925825`: passed;
- repository asset-policy run `37353926007`: passed.

PR #480 changed only `reconstruction/original_game_host.py`; PR #481 changed
`app.py`, `startup_media_windows_backend.py` and their tests, so the two
canonical changes are textually non-overlapping. Their full/package checks
passed independently. The repository intentionally does not auto-run these
manual/PR-only workflows on main pushes.

**Gate-14 boundary remains open.** Hosted Windows CI proves the stock WPF
runtime is present, not that Daniel's real Windows 11 client visibly and
audibly plays both verified startup clips. Do not close issue #437, claim
startup-media Windows acceptance, or mark Gate 14 complete until a normal
external launch confirms both clips. Native skip input, fades/transition timing
and exact original display treatment also remain unrecovered.

**Exact next task:** treat the external WPF playback retest as a deferred
specific user-action blocker and continue independent cloud-safe critical-path
work. Prioritize the Gate-17 minimal upstream FFmpeg helper/source-provenance
route (#475/#479) while keeping Gate 14 as the earliest incomplete validation
gate. Before promoting those older stacked branches, reconcile them against
current main and preserve the fail-closed production-migration boundary.

## Recovery 319 continuation — matching FFprobe/output contract canonical

PR #473 merged as `18a2266507eec2a1b5663e047e89671e20a713a5`
from head `6dd7cdfd31a5ee84a4f4eef40b39a82c46239c5b`.
The clean rebased PR contained only the three FFprobe/output-contract files.
Current-head reconstruction runs `37345064573` and `37345270284` both
passed **2,609 tests / 23 expected skips**. Windows package run
`37345270265` and repository asset-policy run `37345270184` passed.

The pinned LGPL migration candidate now requires both `ffmpeg.exe` and
`ffprobe.exe` from the same immutable BtbN archive and the same FFmpeg source
revision `n9.0.2-22-g46d8f462ee`. The verified FFprobe executable SHA-256 is
`46a86ca9eb512c2989354ebe68eb1562fcb73b16d8041d54d54b5f4b244f958c`
(size 134,300,160 bytes). The synthetic Windows proof uses the real private
converter's `-fps_mode passthrough` option and then requires FFprobe to report
H.264/yuv420p 320x480 @ 25 fps plus AAC 22,050 Hz stereo in MP4 before
independent video/audio decode checks pass.

This does **not** migrate production packaging. Exact original
`easp.tgq` / `premintro.tgq` conversion remains unexecuted in Recovery 319
because the materialized private archive still cannot be opened by either the
container or notebook execution path. The current production default remains
`libx264` under the #468 fail-closed release-material boundary.

**Exact next task:** retry the authorized private archive at this persistence
boundary. If execution is healthy, run both exact source-verified TGQs through
the pinned LGPL `h264_mf` + matching FFprobe path and preserve an outside-Git
receipt. If execution remains blocked, do not spin on the same infrastructure
failure; continue the independent Gate-17 minimal-upstream-helper/source
provenance route while keeping Gate 14 as the earliest incomplete validation
gate.

## Recovery 319 continuation — h264_mf private-audit path canonical

PR #470 merged as `bb32e74cff669b2fdd489058f118a8476f207ad1`
from head `97463a335da3f9f2440abe745807aad0ba2dca84`.
Reconstruction run `37343527426` passed **2,607 tests / 23 expected
skips**. Windows package run `37343527442` passed the pinned candidate
probe, package-focused tests, PyInstaller freeze, frozen-executable smoke,
deterministic candidate archive and artifact upload. Repository asset-policy
run `37343527679` passed.

The startup-media conversion layer now has a named candidate-only
`h264_mf` profile while preserving `libx264` as the normal production
default. The private Gate-14 converter accepts
`--video-encoder h264_mf`; runtime startup-cache creation, cache reuse and
receipts are profile-bound as well as FFmpeg-SHA-bound, so a prior
`libx264` derivative cache cannot be reused as evidence for the candidate
profile. The exact outside-Git command for the private original-TGQ audit is
recorded in `research/GATE17_FFMPEG_LGPL_MIGRATION.md`.

A fresh Recovery-319 retry materialized the authorized 511,121,336-byte source
archive, but both the container execution path and an independent notebook
Python probe failed with `caas.internal.errors.ClientError` before real
archive access. Therefore no exact original TGQ was converted in this
checkpoint and production packaging remains unchanged.

PR #471 is the current cloud-safe follow-up. Its Windows run
`37344094021` has already passed the same pinned LGPL archive with both
`ffmpeg.exe` and `ffprobe.exe`, the production converter's
`-fps_mode passthrough`, exact H.264/yuv420p/AAC/MP4 synthetic probing,
frozen packaging and smoke testing. Its full reconstruction run
`37344093250` is still pending completion and PR #471 must not be merged
until that run is green.

**Exact next task:** finish #471 verification and merge only if the full
reconstruction suite passes. Then retry private archive execution and, if
healthy, run both exact original startup TGQs through the pinned LGPL
`h264_mf` + matching FFprobe path. Until that private receipt exists, keep
`libx264` as production default and keep the #468 third-party release
boundary fail-closed.

## Recovery 318 continuation — LGPL FFmpeg candidate probe canonical

PR #469 merged as `4f0443ffe40ff93ad48fd93b4d196dbb5ab394e4`
from head `e21159de5508f187ab154f53dbe9463be38a862d`.
Reconstruction run `37339029246` passed **2,604 tests / 23 expected
skips**. Windows package run `37339029237` and repository asset-policy run
`37339029157` passed on the same head.

The pinned BtbN Windows x64 LGPL candidate is
`ffmpeg-n9.0.2-22-g46d8f462ee-win64-lgpl-9.0.zip`, release tag
`autobuild-2026-10-03-18-14`, archive SHA-256
`3fc85bae9f9643a03d15c2d2de12fb017dcd9fdabe819bfb1a94f54fea108714`.
The verified executable SHA-256 is
`c15ef2e38620f3efb81355c2b25afe054e93a69ce7300a35e640508e92954aa8`;
its packaged LICENSE SHA-256 is
`da7eabb7bafdf7d3ae5e9f223aa5bdc1eece45ac569dc21b3b037520b4464768`.
The candidate reports FFmpeg revision `n9.0.2-22-g46d8f462ee`, contains the
EA TGQ decoder plus `h264_mf` and native AAC encoders, and omits the
current GPL/nonfree/libx264/libx265 enable flags. A real Windows CI synthetic
roundtrip at 320x480, 25 fps, 22,050 Hz stereo successfully encoded H.264/AAC
MP4 with `h264_mf` and decoded both streams again.

This is still a **candidate-only** result. Production packaging remains on the
#468 imageio-ffmpeg/Gyan helper. No exact original TGQ has yet been converted
through this candidate in canonical evidence, no external Windows 11
visibility/audibility receipt exists for candidate-produced derivatives, and no
legal-compliance claim is made.

**Exact next task:** retry the authorized private archive and run both exact
startup TGQs through the verified LGPL candidate with `h264_mf`, preserving
the existing source hashes, frame-count checks, audio decode checks and private
receipt boundary. Only after that private conversion succeeds should the
production conversion profile/package provider be migrated. In parallel, keep
the #468 final-release third-party material guard fail-closed until exact
license/source/build-script distribution material is staged and hash-bound.

## Recovery 318 continuation — FFmpeg redistribution boundary canonical

PR #468 merged as `fabbe1971d7c8667dc7a347498b64f7970bc1970`
from head `03cb83e2d9fda998eb5ec265eb198fde7723f24c`.
Reconstruction run `37336912015` passed **2,599 tests / 23 expected
skips**. Windows release-candidate package run `37336911662` passed the
new exact-provider install, FFmpeg identity/attestation step, focused package
tests, PyInstaller freeze, frozen executable smoke, deterministic archive build
and artifact upload. Repository asset-policy run `37336911707` also passed.

The Windows packaging workflow now pins `imageio-ffmpeg==0.6.0` and checks
the staged executable against the exact previously observed FFmpeg 7.1
`essentials_build-www.gyan.dev` identity. Repository provenance records the
observed Gyan build, compiler, GPL/version-3/static configuration, required
configuration flags, FFmpeg library versions and upstream reference URLs. Each
Windows package emits a SHA-bound `runtime_tools/ffmpeg.provenance.json`
attestation for the exact executable and repository provenance.

Gate 17 now fails closed on third-party release material. A final release audit
requires the same release ZIP to contain the attested FFmpeg binary, matching
repository provenance, and every declared FFmpeg license/source-distribution
material with exact SHA-256 identities. The canonical provenance deliberately
keeps `release_ready=false`, `license_material_complete=false` and
`source_material_complete=false`; therefore this checkpoint does **not**
claim that redistribution requirements are satisfied and does not make a legal
compliance conclusion.

A fresh private-execution retry in this recovery failed even for a trivial
shell/Python probe with `caas.internal.errors.ClientError`. The private
TeamTable six-base-control trace around `0x524EC0` therefore remains
unexecuted and Gate 14 remains the earliest incomplete validation gate.

**Exact next task:** audit whether the Windows 11 release can avoid redistributing
the current static GPL-enabled FFmpeg binary while retaining the source-backed
startup-media path. Prefer a technically sound dependency strategy that removes
or sharply narrows the redistribution obligation; if no compatible route is
available, preserve the #468 fail-closed boundary and document the exact
third-party source/license material still required. Do not weaken startup-media
fidelity, silently rely on a developer-installed executable, or mark the
current FFmpeg material complete without exact evidence. Retry the private
Gate-14 source route again at the next normal persistence boundary.

## Recovery 318 continuation — release disclosure guard canonical; private source still blocked

PR #467 merged as `93991be9f3a147f7d8764b46792b9685091b1ddd` from head
`61a1690f05ff4b79b6193425354d90c1d43c9be8`. Reconstruction run
`37331984582` passed **2,593 tests / 23 expected skips** and repository
asset-policy run `37331984552` passed on that same head.

The final Gate-17 release audit now reuses the canonical Gate-15 fidelity audit,
requires Gate 15 to be explicitly declared complete/release-ready, and requires
every final `accepted_documented` Gate-15 gap title to appear verbatim in
`research/RELEASE_LIMITATIONS.md`. The final audit receipt records the
Gate-15 ledger SHA-256 and accepted-disclosure list. Fixed or
`proven_irrelevant` rows are not treated as release limitations. This is an
omission guard only; Gates 14-17 remain incomplete.

Recovery 318 also retried the exact authorized source archive. The
511,121,336-byte Library archive materialized successfully, but the first real
Python `zipfile.ZipFile(...)` access failed with
`caas.internal.errors.ClientError`. Real private source access therefore
remains unavailable; the TeamTable six-base-control trace around `0x524EC0`
remains deferred and no new source semantics were promoted.

The top-level `project_status.json.source_execution_blocker` has been
reconciled to this current Recovery-318 failure. Historical Recovery-194 fields
remain historical evidence only and must not be interpreted as current
availability.

**Exact next task:** while private Gate-14 source access remains blocked, audit
the bundled Windows FFmpeg release dependency. The package workflow copies the
`imageio-ffmpeg 0.6.x` Windows executable into `runtime_tools/ffmpeg.exe`;
the existing backlog records the observed binary as an FFmpeg 7.1 Gyan
essentials GPL-enabled build. Add a fail-closed third-party provenance/license
boundary for Gate 17 so a final release cannot silently ship that binary without
the required source/license/provenance material. Do not make a legal-compliance
claim from repository inference alone; preserve exact upstream/version/build
evidence and fail closed where source-distribution obligations are not yet
satisfied.

## Recovery 317 continuation — Gate-15 ledger canonical; Gate 14 still active

### Recovery 317 support-staff fidelity tracer merged

PR #466 merged as `5a324004d92ac80e0d74ecbaa4010f6c638f3bc2` from verified head
`7b4027602d311be76583ee882ef47ba38a4a18db`. Reconstruction run
`37329789390` passed **2,591 tests / 23 expected skips** and repository
asset-policy run `37329789327` passed on that same head. Stale Recovery-316
PR #465 was closed as superseded.

The merged support-staff tracer resolves only checksum-gated private
`CSupportStaff` vtable targets and bounded source windows for the already-known
day-1 category-102 path. It deliberately keeps the `+0x24` returned-value
semantics, backing field, initialization, mutation/persistence and runtime amount
materialization unresolved. The Finance/board fidelity row remains active and
Gate 15 remains incomplete.

The current Gate-17 release audit also has one independent cloud-safe hardening
opportunity: it validates that `RELEASE_LIMITATIONS.md` is substantive and no
longer marked pre-release, but does not yet machine-check that every final
Gate-15 `accepted_documented` item appears in that release disclosure. This is
the next independent critical-path task while private archive access is blocked.


PR #464 merged as `79d4457f38112f57fe5cfbc57f0e6a02baac64cd`.
Its head `c5103024e163e5473e8a8a431e993bebeefb82cd` passed the full
reconstruction suite in run `37324348013` with **2,586 tests / 23 expected
skips**, and repository asset-policy run `37324348957` also passed.

The merged Gate-15 schema-1 fidelity ledger now covers all 11 live
`research/FIDELITY_GAPS.md` rows exactly once. Ten rows remain Gate-15-owned
or deferred; the `FastView/3D and original audio/match presentation` row
remains an explicit Gate-14 prerequisite. The audit rejects missing, duplicate
or extra rows, Planned-gate drift, fallback-as-original claims, accepted
limitations without release disclosure, relabeling the Gate-14 prerequisite as
a Gate-15 acceptance, and any Gate-15 completion declaration before Gate 14 is
closed and every Gate-15-owned row has a terminal disposition.

This checkpoint is omission-proofing only. It does **not** adjudicate any
remaining fidelity gap and does **not** complete Gate 15. Gate 14 remains the
earliest incomplete validation gate.

Recovery 317 retried the private source path at this checkpoint. A trivial shell
launch and Python version probe succeeded, and the exact authorized
511,121,336-byte Library archive materialized again. However, the first real
source-access command (`unzip -l`) failed with
`caas.internal.errors.ClientError`, and an independent notebook `zipfile`
open of the same materialized archive failed with the same error. The canonical
private next step remains the already-prepared TeamTable six-base-control trace
around `0x524EC0`; it has **not** been run or adjudicated in Recovery 317.

**Exact next task:** while private executable/archive access remains unavailable, harden the Gate-17 final release audit so every Gate-15 `accepted_documented` fidelity item is machine-linked to the final `RELEASE_LIMITATIONS.md`. Keep Gate 14 as the earliest incomplete validation gate. Revisit the TeamTable base-control private trace when real archive access, not merely process startup, succeeds. Do not infer unresolved FastView geometry/order, broader AudioHooks semantics, procedural-secondary ownership, six-user runtime semantics, or non-PL objective progression by analogy.

## Recovery 315 continuation — acceptance tooling and later-gate handoff canonical

Canonical main has advanced through three verified Recovery-315 checkpoints:

- PR #462 merged as `774629a983780bf35e4d4736968d4cca20fd0c0e`.
  It adds one transactional external Windows 11 coordinator for the already
  canonical startup-media and bounded first-screen audio acceptance audits.
  The two human-confirmed receipts remain distinct and hash-bound; no files are
  written unless both independent audits pass. Reconstruction run
  `37320506035` and asset-policy run `37320506527` passed.
- PR #461 merged as `53b8ad95389fc1c9226d47a5a07863e8ca875507`.
  Gate-14 readiness now records acceptance-tool presence separately from
  actual external Windows evidence for both startup media and bounded
  first-screen audio. Both real-Windows verification flags remain false.
  Corrected reconstruction run `37320843836` and asset-policy run
  `37320843885` passed.
- PR #463 merged as `7eccca00151672e7933ed33d482c5adddf7e8615`
  after reconstruction run `37322157361` passed. Gate 13 is now consistently
  treated as complete across Gate-15/16/17 readiness and the pre-release
  limitations ledger. Gate 14 is the earliest incomplete validation gate.
  Gate-13 secondary/pixel-perfect residuals are Gate-15 fidelity backlog items,
  not an excuse to reopen Gate 13.

The external acceptance tooling above is **not** evidence that either Windows
transaction ran. No private startup-media receipt and no private bounded-audio
receipt is canonical. Broad AudioHooks semantics/login-menu integration and a
recognizable original match workflow remain open.

The authorized 511,121,336-byte private source archive still materializes
successfully, but Recovery 315 has now failed on both a trivial shell/container
probe and the notebook Python execution path with
`caas.internal.errors.ClientError`. No executable-byte or semantic source
claim may be inferred until a process execution route is healthy.

Gate 15 work-ahead is now focused on an omission-proof fidelity ledger. PR #464
is building a one-to-one machine audit between the live **Active gaps** table in
`research/FIDELITY_GAPS.md` and an explicit Gate-15 adjudication ledger. It
must keep the still-open Gate-14 presentation row as an earlier-gate
prerequisite, reject fallback-as-original claims, and refuse Gate-15 completion
until Gate 14 is complete and every Gate-15-owned row has a terminal
fixed/irrelevant/accepted-documented disposition.

**Exact next task:** finish current-head CI and review for PR #464, merge only if
the full reconstruction and asset-policy checks pass, then reconcile the
canonical Gate-15 ledger checkpoint. After that, retry private execution at a
normal persistence boundary and resume the highest-priority source-backed
Gate-14 closure item if execution has recovered. If it has not, continue only
independent cloud-safe critical-path work; do not infer FastView geometry/order,
broader AudioHooks sender semantics, procedural-secondary ownership, six-user
runtime semantics, or non-PL objective progression by analogy.

## Recovery 315 continuation — #460 canonical; private execution still blocked

PR #460 merged as `1882ce3e36b1ded7919230319c6d7c73538a9b85`. It adds the
fail-closed external **Windows 11 client** acceptance transaction for the
already-integrated production-host first-screen press-audio route. The audit
drives a real Tk **Start New Game** click, requires the canonical `menus.bnk`
identity and exact source-backed `AudioHooks (10,0) -> slot 2` delivery through
`WindowsMemoryWaveMenuPcmBackend`, and requires explicit human
`YES-HEARD` confirmation before a private receipt may mark this bounded route
audible. Ordinary launches remain unchanged and audio failure still delegates
gameplay.

PR #460's head `a5148bba1527ecf8ded85ec221998cc6949fae59` passed the
reconstruction suite (run 37315028568), Windows release-candidate package
(run 37315028421), Gate-13 presentation regression (run 37315028868), and
repository asset policy (run 37315028543). No private Windows receipt exists,
so canonical human-heard bound-audio acceptance remains false. Broad semantic
AudioHooks binding, sample meaning, hover audio, full login/menu audio
integration, startup-media acceptance, recognizable match workflow and Gate 14
completion also remain false.

Recovery 315 re-resolved the exact authorized Library source at
`/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`
and materialized the 511,121,336-byte archive into the current private
workspace. Immediately afterward, a trivial shell/Python execution probe failed
with `caas.internal.errors.ClientError`. Therefore the private source bytes are
recoverable, but this execution allocation still cannot inspect or hash them.
No new executable-byte, disassembly, archive-SHA or source-semantic claim is
made from this recovery.

Gate 14 remains the earliest incomplete validation gate. Real Windows client
evidence is still required for #436 launch-time acceptance, #437 startup-media
and bounded-audio acceptance, and #438 Southport Start Game acceptance. Private
execution is still required for the unresolved FastView geometry/order,
broader AudioHooks sender semantics, source FastView navigation, and other
byte-level source questions. The already-prevalidated Gate-16 stress work does
not need speculative duplication. Gate-17 secondary-owner, six-user
multi-human, and non-PL sporting-objective progression remain explicitly
source-locked and must not be implemented by analogy while private execution is
unavailable.

**Exact next task:** keep Gate 14 fail-closed and continue only independent
cloud-safe critical-path work whose source contract is already established.
First reconcile the current-base Gate-14 readiness/status after #460 and audit
the existing Gate-17 full-scope blockers for any implementation step that does
not depend on unresolved private-source semantics. Revisit the materialized
private source immediately when process execution becomes healthy; do not route
procedural-secondary owners through the primary engine, duplicate the
single-human runtime six times, or generalize non-PL objective progression
without the required source proof.

## Recovery 314 continuation — current-base acceptance/readiness checkpoint

PR #458 merged as `3465043767cffb40a822df15b01a6fb20dd37747`. It adds a
strict **external Windows 11 client** startup-FMV acceptance audit that reuses
the exact runtime TGQ cache, source-proven startup order and Windows MCI backend.
A passing private receipt requires explicit human confirmation that both videos
were visible, both audio tracks were audible and order was correct. No receipt
exists yet, so canonical real-Windows startup-media acceptance remains false.
Reconstruction run 37309256252 and asset-policy run 37309256060 passed.

PR #459 merged as `9c0e22c63c5c9c17953648ae4eb2619c6d9569c2` after
reconstruction run 37313356333 and asset-policy run 37313356314 passed. The
current-base readiness model now records three already-canonical bounded facts:
first-screen press audio is bound, normal Windows startup media is integrated,
and the resolved-only FastView preview has an operator-visible surface. It
continues to keep broad semantic/application-wide audio binding, human-heard
Windows output, full login/menu audio integration, a source FastView navigation
trigger, complete FastView fidelity and recognizable-original-workflow
verification false. Diverged #456 and its obsolete #457 predecessor were closed
in favor of current-base #459/#458 rather than merging stacked history.

Gate 14 therefore remains open. The private executable/container execution
failure still blocks source-byte closure for remaining FastView geometry/order
and broader AudioHooks sender semantics. Real Windows client evidence also
remains required for the player-facing #436 launch-time check, #437 startup and
bound-audio acceptance, and #438 Southport Start Game route; hosted CI cannot
close those issues.

**Exact next Gate-14 task:** add a fail-closed external Windows 11 acceptance
harness for the **already integrated normal-application first-screen press audio
path**. It must exercise a real Tk bound first-screen action through the
production host, require the exact canonical menus bank and source-backed
(10,0)->slot-2 delivery summary, require explicit human confirmation that the
sound was heard, reject hosted/server CI, and keep the receipt private outside
Git. This must not promote broad semantic event/sample meaning, hover audio,
full login/menu audio integration, or Gate-14 completion. After that verified
cloud-safe tooling lands, continue the next source-backed task or preserve the
private/real-Windows blockers and advance only independent later-gate work.

## Recovery 313 continuation — resolved FastView surface merged

PR #455 merged as `6ad4416be3fc91dcac7ff3e007fcaa7cb04c8ad9`.
The source-backed host can now open an operator-visible native 800x600 child
window for an already-built `HumanFastViewResolvedPresentation`. The child
draws the bundle's canonical resolved-preview PNG unchanged; unresolved overlap
pixels remain transparent. The host method creates no match state and is not
called from ordinary clicks, PMenu actions, gameplay, or front-end navigation,
so no unrecovered source trigger has been invented.

Fresh validation after correcting a prose-sensitive test guard passed:
reconstruction run 37307918883, Windows package run 37307919062, Gate-13
presentation regression run 37307919034, and asset-policy run 37307918885.

The private executable/container path remains unavailable in this worker:
a fresh trivial shell probe still returns `caas.internal.errors.ClientError`.
Therefore complete TeamTable/score pixels, GoalFlash absolute placement,
ScoreCompositeMain/embedded-control geometry and other byte-level source
questions remain deferred rather than guessed.

Two cloud-safe Gate-14 follow-ups are active:

- #456 reconciles machine-readable readiness with the now-canonical bounded
  first-screen audio, automatic startup-media path and operator-visible FastView
  surface while keeping broad audio and recognizable-workflow criteria false.
- #457 adds a strict external Windows 11 client startup-FMV acceptance receipt
  that rejects hosted/server CI and requires explicit human confirmation of
  visible video plus audible audio for both source-proven startup clips.

**Exact next Gate-14 task:** verify and merge #456/#457 on the current main
without promoting any external acceptance flag until a real receipt exists.
After those land, continue the highest-priority cloud-safe Gate-14 work; if no
independent presentation work remains, preserve the exact private-source and
real-Windows blockers and advance only independent later-gate work under the
deferred-blocker policy.

## Recovery 313 — automatic startup FMVs merged; live FastView surface is next

PR #454 merged as `7b2c8d4eb32bd82e01570d3ed09b30a1b057f5ba`.
Normal Windows source-backed launch now revalidates the exact original
`FMV/easp.tgq` and `FMV/premintro.tgq`, converts them once into a private
per-user H.264/AAC cache, verifies exact source-backed decoded frame counts plus
audio decode, rehashes cached derivatives, and plays them through the built-in
synchronous Windows MCI transport. The Windows candidate bundles FFmpeg and
package smoke requires it. The explicit receipt/external-player path remains a
developer override. Current-base CI passed: reconstruction run 37305008796,
Windows package run 37305008767, Gate-13 regression run 37305008731, and asset
policy run 37305008736.

This closes the repository-side *absence* of the startup FMV path, but it does
not prove real Windows visibility/audibility, native skip input, fades, or exact
display treatment. Issue #437 therefore remains an acceptance/fidelity item
rather than being closed from hosted CI. Likewise #436 launch-time acceptance
and #438 England -> Conference -> Southport -> Start Game acceptance remain
real-Windows checks.

The Gate-14 audio readiness contract must also remain fail-closed: first-screen
press routing is source-bound and live on Windows, but no current canonical
receipt proves the bound application path was audibly heard. Broad login/menu
audio integration therefore remains false.

A fresh live-host audit found a separate actionable integration gap:
`OriginalGameTkHost` has no FastView/completed-match rendering references at
all. PR #452 already carries every currently verified optional FastView plane
through the completed-human frame/resolved adapters, but those verified pixels
are not yet exposed on an operator-visible runtime surface.

**Exact next Gate-14 task:** add a presentation-only Windows/Tk FastView surface
that consumes the existing completed-human resolved presentation bundle,
without duplicating simulation state or inventing unrecovered z-order/blend,
omitted controls, audio, or 3D choreography. Keep the surface explicitly
partial/fail-closed and regression-lock that the displayed bytes come from the
canonical resolved preview. If a source-backed runtime trigger cannot yet be
proven, expose only a bounded presentation seam rather than inventing a
management navigation command. After that, continue the next FastView/audio
closure item while private source execution remains unstable.

## Recovery 312 — verified FastView integration landed; startup-FMV branch under final regression

PR #452 merged as `f896ecf9302dc20b953866054237013811146144`.
The completed-human FastView frame/resolved adapters now carry every already
source-verified optional plane supported by the canonical component compositor:
surfaced match background/badges, ClockControl text, direct header text,
LeagueScores phase planes/runtime phase text, LeagueTable, and the complete
retained PlayerRows raster. Frame-integrity hashes are derived from canonical
component order, so a caller-provided verified plane cannot be silently omitted.
No unresolved z-order, native blend, audio, omitted-control pixels, or 3D
semantics were promoted. Reconstruction CI run 37303703674 and asset-policy run
37303703640 both passed.

Issue #437's repository-side default startup-media fix is now PR #453. Its
Windows package path successfully stages bundled FFmpeg, freezes the onedir
candidate, and passes package smoke on run 37303921886. The first full-suite
attempt exposed only a Linux package-smoke fixture that had not created the new
required `runtime_tools/ffmpeg.exe`; the fixture was corrected on PR head
`15f733d043c664d8b4e7a53a9763333349aac876` without weakening the package
guard. Do not merge #453 until the new full reconstruction run also passes.

Recovery 312 re-resolved and materialized the exact authorized
511,121,336-byte Library ZIP through `ORIGINAL_SOURCE_LOCATOR.md`. A trivial
container/Python probe worked before materialization, but immediately afterward
the execution sandbox again returned `caas.internal.errors.ClientError` even
for `ls`, `sha256sum`, and a trivial Python call. Therefore the private
source is available but private execution is not sustained; no new TeamTable
adjudication or source-byte claim is made from this recovery.

**Exact next Gate-14 task:** finish PR #453's full regression, merge it only if
all required CI is green, and keep Windows FMV visibility/audibility, native
skip/fade behavior, #436 launch timing, and #438 Southport Start acceptance
open until real Windows evidence exists. If #453 lands, continue the next
independent cloud-safe FastView/audio closure item while the private execution
sandbox remains unstable.

## Recovery 311 — gameplay-test fixes canonical; Gate 14 remains active

Current `main` includes the two repository-side fixes prepared from Daniel's
5 October Windows 11 playtest:

- #450 / `520b8202` integrates the source-backed first-screen press-audio route
  on the current fullscreen host. It verifies the canonical installed
  `DATA/AUDIO/SFXS/menus.bnk`, uses the Windows in-memory WAV backend and
  remains presentation-fail-soft. All repository, presentation, reconstruction
  and Windows-package CI passed.
- #451 / `fb3c770e` moves only the pure management resource decode bundle off
  the Tk Start Game callback, keeps the TeamSelect frame visible while loading,
  polls the worker result back on Tk, ignores premature management clicks and
  surfaces worker exceptions. All four CI workflows passed. This is the
  repository-side fix candidate for issue #438; the exact
  England -> Conference -> Southport -> Start Game route still requires a real
  Windows acceptance run before issue #438 may close.

Issue #437 is now split cleanly. First-screen press audio is integrated, but the
startup FMVs are still absent on a normal launch because `app.py` creates a
startup-media backend only when both `--startup-media-receipt` and
`--startup-media-player` are supplied; `play_configured_startup_media()`
returns immediately when both are absent. The packaged/default launcher supplies
neither. The verified original `easp.tgq` / `premintro.tgq` source evidence
and conversion/playback modules remain canonical.

The authorized 511,121,336-byte Library ZIP was successfully resolved and
materialized during Recovery 311, but both the container and Python execution
sandboxes then failed even on trivial execution with
`caas.internal.errors.ClientError`. Therefore no new extraction, hash,
conversion or startup-media derivative claim was made. No existing private
startup derivative/receipt was found in `/FM2001`.

Issue #436's TeamSelect/startup decode deferral is already canonical from #445,
but its actual Windows launch-time acceptance remains unverified. Do not close
#436 or #438 from CI alone.

**Exact next Gate-14 task:** continue issue #437 toward an automatic,
provenance-tracked default startup-FMV runtime/package path as soon as sustained
private execution is healthy. While that execution blocker persists, continue
independent cloud-safe Gate-14 FastView/audio work; do not invent TGQ bytes,
skip/fade semantics or Windows audibility.

## Gate 13 CLOSED — advance to Gate 14 (5 October 2026 KST)

Gate 13 now passes all four ROADMAP criteria. The final fixed slice integrates
the source-qualified application-owned `back_4_anim/back_4` management header,
exact MENU caption/Zurich 24px font, and source-rasterized ordinary League
Tables row text/data on top of the already-closed Button timing, PMenu,
Fixtures arrows, report/save/reload and PMatchInfo route.

Final pre-closure-doc code head `1a3009042d547b9043235bdca2b09d87f4f024da`
passes the Gate-13 source suite, full reconstruction suite, Windows candidate
package and repository asset policy. Exact run IDs and private receipt hashes
are in `GATE13_CLOSURE_AUDIT.md` and `GATE13_FINAL_MANAGEMENT_TEXT.md`.

The earliest incomplete validation gate is now **Gate 14 — Original audio and
match presentation**. Do not reopen Gate-13 capacity/report/paging/header/text
work unless a later regression proves a concrete criterion failure. Secondary
management pixels, Squad dynamic colors/status icons, held-repeat/thumb/shirt
states and similar exact-fidelity refinements are Gate-15 items.

## Daniel approved the decisive native capacity probe (5 October 2026 KST)

### Fixed closure boundary: live Button implementation checkpoint

Canonical base `186ed2970c9803284280005b97a26e47d37e1eaf` preserves the
worker's disjoint Gate14/15 work. On `codex/gate13-fixed-closure`, the ordinary
Button owner/cadence is now source-qualified: `531B40 -> 5329D0 -> 6541E0 ->
6538F0 -> child vtable+68 (6527F0)`. This is a serialized available UI pass,
not a fixed millisecond timer. The Tk host advances the recovered eleven-step
state once per idle pass, stops stable redraws and retreats on pointer leave.
Focused tests: **38 tests /1 expected licensed-source skip PASS**. Real
Windows/Tk8.6.12 hover qualification passes all eleven source frames and retreat;
fresh real Windows schema8 also PASS (receipt131866c4...e8cc9, exact hash below).
Final full regression/package and closure validation remain pending. Evidence and exact
private receipt hashes: `GATE13_FIXED_CLOSURE_SLICE.md`.

The only other accepted implementation blocker is required management
`back_4/back_4_anim` dynamic header art/text and ordinary data/text rendering.
Then audit the four ROADMAP criteria. Non-blocking pixels/secondary states/
obscure refinements belong to Gate15; do not reopen paging, capacity, report,
save/reload or PMatchInfo. Gate13 remains open pending this fixed slice and
final validation. No original execution, ownership or agent-runtime change.

Daniel requested wrap-up at the usage limit. No further source work is running.
Final reconciliation preserves current-main `47039febe5318c9109f71e90b88789ca39833b90`
and the worker's disjoint #405/#406 changes; none are modified by this branch.
Reconciled focused regression plus the worker's changed tracer module passes
**43 tests /1 expected skip**, using the existing private Capstone dependency.
Header source/asset handoff is in the fixed-slice evidence file: verified private
back_4/back_4_anim extraction, compound child origins/geometry and24pixel Zurich
caption producer. These are not yet integrated. Resume ONLY that accepted
management item, then final four-criterion audit; no new fidelity blockers.

### Current result: selected read reached with uninterrupted watch coverage

**Subsequent executable milestone:** the canonical human-away fixture now
publishes a strict complete report, saves to schema **44**, reloads in a new
process, and opens the exact rendered PMatchInfo via real Windows/Tk right-click.
This succeeds both with the explicitly observed allocation and, separately,
with **automatic Windows-produced allocation bytes**, without replaying the
probe's zero values or injecting report/scalar/link state. Automatic-route
receipt SHA-256:
`20c3ab1422244a312d64db53da55cb1f86b58955ab03c7ea65c7580bb34ae9d5`.

Allocator closure and exact integration details are in
`GATE13_UNCONTROLLED_ALLOCATION_PRODUCTION.md`. Actual Win32 allocation bytes
are retained, not a zero default; the port's heap history is not claimed to
replay the original process. Field mapping and known-zero native RNG skips
are source-corrected. Focused capacity/gate/save tests: **71 passed**.

**Ordinary paging milestone (5 October):** exact `toogle_arrow_left/right.444`
resources are imported and the +D30/+D60 controls now use events39/40, original
four-frame draw state, accepted press/release/hover and zero-origin transform.
`0xF` is a capability mask, NOT15frames. A real visual-tail check exposed the
permanent PMenu overlay hiding the entire right arrow; source-qualified popup
stack/event2/dismissal behavior now fixes that without invented z-order.
The genuine automatic human-away save reloads in a fresh Tk process and uses
real bidirectional arrow clicks, no explicit paging seam, then ordinary
right-click opens the correct rendered PMatchInfo. Receipt SHA-256:
`d22de98fa7b130df69331366073256e8e62a6ecaa67ea77f3a26004fbd159125`.
Exact source/asset/route evidence: `GATE13_FIXTURES_PAGING_TRACE.md`.

Final code checkpoint `daa1622f8e5c2a64698e013f1f14fdb9edad3dd3`, based on
current-main `7aac77afcb22931eb8cf6d17725df2e7b24daf1e` with the worker's
disjoint Gate14 #363 preserved: **2,283 tests /23 expected skips**, **44 focused
host/pager/popup/Windows-audit tests**, asset policy and fresh real Windows11/Tk
schema8 PASS. Correct Windows receipt SHA-256:
`131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aa7aae2e8cc9`.
Windows candidate package CI **PASS**, including frozen smoke:
https://github.com/BrannMolvik/premier-league-manager-2001-research/actions/runs/37227429547
This is not Daniel-machine frozen-package acceptance or Gate17 certification.
Verified implementation/research is on PR **#365**,
`codex/gate13-fixtures-paging-closure`; original/proprietary reports and save
remain private. `agent-runtime` and ownership are unchanged.
Latest reconciliation preserves canonical `07eb4f7bc21bac3f0c2f6f1952c579fb9131dde1`
(including the worker's Gate14 PRs through #400) at code head
`a8e0eaed7a2c45b0ce5e170f812f88448aa9cb0c`. A fresh genuine automatic
human-away calculation/save and separate Windows/Tk process repeat again pass
with ordinary arrows and no paging seam; private receipt SHA-256:
`6ee68869cd9fdcb997f00ce3045b8e441ba629b15e13b81136299eee323111d4`.
Full regression at the preceding reconciled `fafd2882` passes **2,395 tests /
23 expected skips**; the final disjoint #400 module separately passes4 tests,
and final focused Gate13 tests44 PASS. The fresh schema8 receipt retains the
correct identity above; asset policy and patch hygiene pass.
No original game was executed and no Gate14 file differs
from this reconciled main. Weekly usage reached the final validation reserve;
do not substitute guessed timing or renderers to claim closure.
Final reconciliation also preserves the newer disjoint worker PR #364 at
`a99f1e029036c8cb37d66f36641c6093214d883a`; its changed-module regression
passes7 tests. This introduces no new Gate13 source/runtime discrepancy.

**Historical PR365 criterion review (superseded by the fixed-slice checkpoint
above):** Gate13 remained OPEN. The next actual blocker was
live first-screen Button hover/update timing: the host still draws fixed
`build_original_debug_frame(view,0)`, not the recovered 11-step live state.
Qualify its original update owner/cadence and integrate it without inventing a
timer. Then complete normal-play recognizability review of the recovered
management header/ordinary data/text presentation. Header popup input is now
qualified, but `back_4/back_4_anim` dynamic art/text is not yet rendered.
No capacity/report/save/PMatchInfo retracing, Gate14 changes or new original
launch is required by these findings. Previous milestone regression passed
**2,267 tests / 23 expected skips** after canonical-main reconciliation,
plus **134 focused tests** and asset policy (pre-reconciliation: 2,248 tests).
Fresh real Windows 11/Tk schema-8 passes; receipt SHA-256:
`131866c416673c306c932a11899dc4bfe3810c60ee683fd87e82aa7aae2e8cc9`.
This validates existing host contracts, not every timing/
recognizability criterion. Both original-probe attempts and consent are spent;
no further original launch is authorized by those receipts. Gate14 work and
ownership are unchanged. See the current criterion table in
`GATE13_CLOSURE_AUDIT.md`; earlier probe next-actions below are historical.

Reconciled canonical main for this milestone:
`e76f9c5b766bbfecec7b5a4f8cf50dbd87b668cd`; the continuous worker's newer
disjoint Gate14 changes are preserved. Merged PR353 is not reopened; subsequent
producer/persistence work is on `codex/gate13-uncontrolled-producer-20261005`.
Reconciled real Windows11/Tk schema8 passes with the same deterministic receipt
identity above. Existing Windows package CI passes at code head `84fa8d79`,
including frozen executable smoke and uploaded candidate archive:
https://github.com/BrannMolvik/premier-league-manager-2001-research/actions/runs/37223803377
This is CI packaging evidence, not Daniel-machine frozen-executable acceptance
or Gate17 certification; earlier local App Control denials are not bypassed.

The second/final separately approved follow-up succeeded: **41.812 seconds /
1,673 debugger events**, stopping **before** selected `5DA538` on imported
DBRClub ID 5 (Coventry City). The ledger verifies **1,156 consecutive events /
1,155 continuations** with both WOW64 and native AMD64 DR0/DR1/DR7 read-back
on every live user thread; four new threads were armed before continuation.
No watch write occurred. The exact receiver retained allocation bytes
`0000000000000000` at `+13C/+140` through construction/import/this read.

Classification: **unchanged allocation bytes for this exact lifecycle**, NOT
a universal zero initializer/default. Kernel/external-writer coverage is not
claimed. The original executable remains unchanged. All other desktop checks
remain mandatory; manual audio and the sole topmost shim are unchanged.

The preceding guarded attempts failed closed because one newly created thread
lost its debug registers during startup in both context views. Initial arming
now sets DEBUG_REGISTERS only in both architectures, selecting no native
control/game state; subsequent loss still terminates without repair/bypass.
The successful run is not a claim that the earlier graphics fault was fixed.
Both approved follow-ups are spent; no further original launch is authorized
by their expiry receipt.

Private successful receipt SHA-256:
`132a3ed0c4553a031b7d84e3357837f650a67e1b785f9ea8db108a1e080856c9`;
adjudication SHA-256:
`3a9bbf15cfbd6d62418c924bf409be090327c29aaba9b31fcd25f0ec2cefd944`.
**Next:** retain source-qualified uncontrolled allocation state explicitly,
without turning this observation into a global zero default; connect the
uncontrolled attendance inputs and prove the genuine human-away calculated
report/save/fresh-reload/right-click/rendered-PMatchInfo chain. Gate 13 remains
OPEN. Current focused probe/display tests: **63 passed**. Gate 14 and ownership
protocol remain untouched. Earlier next-action paragraphs below are historical.

### Executed on current main: startup fault, not a capacity conclusion

**Follow-up, separately approved idle surface diagnostic:** Daniel approved a
single <=60-second run with the same safeguards and no additional shim. It ran
from the PR #353 branch with newly isolated observational Lock-return probes
at `5EE232` / `5EE252`, not capacity watches or GUI inputs. Fresh consent was
generated at `2026-10-04T16:44:35.385300+00:00`, expiring 10 minutes later.
It intentionally stopped on the 60-second time bound (60.031 seconds including
cleanup / 515 debugger events), **not** an exception. All **120** returns
(60 per surface) were zero; all retained descriptors were 108 bytes,
800x600, pitch 1600, with non-null surface buffers. No access violation or
unhandled native exception occurred. Original terminated; disk hash unchanged.
Other desktop checks remained intact; only approved foreground/focus was seen.

This is a successful **idle** diagnostic, not proof that the prior graphics
fault is fixed, and not a capacity/report route or a new DXGI qualification.
Daniel reports he alt-tabbed to another game during the prior crash run, but
also recalls an earlier crash without interaction. Focus loss is a candidate,
not a proven sole cause. No automatic additional original launch is authorized
by the now-executed single diagnostic approval.

Private diagnostic receipt SHA-256
`96f6e93c26e86d0b732604087773dbc7857edd7e21c4155e10750379719bfb5e`;
consent SHA-256
`a2a5ed2e07ed34217ce3a9f305fc86f056a36b34dfda993adca079d7a6115ab5`;
offline adjudication SHA-256
`b80f832b0cd299da16a17a9bc2d61f555981c67c05bc470157800d0510bde4f0`.

**Updated next action:** reproduce the ordinary startup/interaction boundary
in a separately scoped bounded guarded native observation, retaining actual
surface HRESULT/descriptors and adjacent focus/foreground state. Do not
manufacture surface recovery or blame alt-tab from user recollection alone.
The isolated diagnostic helper is fixed at 60 seconds / 4096 events, continuously
re-arms its two probes and terminates before copying on nonzero HRESULT or a
null/malformed descriptor. Ordinary capacity mode is unchanged. Resume the
all-user-thread allocation-to-selected-read proof only after this startup
dependency is closed; human-away report and final Gate-13 closure remain pending.
Focused current-code watcher/display checks now pass **56 tests**; asset policy
passes. No broad/full-suite/Windows closure repetition was needed for this
observational milestone.

The approved single run executed from canonical `781f90a1` using the hardened
watcher. Fresh consent was generated immediately before execution at
`2026-10-04T16:27:24.529140+00:00`, expiring 20 minutes later. Exact executable,
wrapper and config identities were rechecked; the sole topmost shim read-back
was 8 -> 0, every other argument unchanged. No capacity/report/registry/simulation
values were injected.

The run ended after **58.031 seconds / 273 debugger events** with an unhandled
native `0xC0000005` at **`0x5EE19B`**, a word graphics-copy store to invalid
address **`0x00009312`**. This was **not** an intentional attendance/time/event
stop. The debugger terminated the failed owned process after the unhandled
exception; no original remains running, and its on-disk SHA-256 is unchanged.

Allocation/import/selected `0x5DA538` were not reached. The all-user-thread
watch ledger never started (0 checks). Thus this receipt proves **neither** a
capacity writer nor unchanged allocation bytes, and authorizes no capacity
value/default or human-away report. Gate 13 remains **OPEN**.

Offline exact-source adjudication identifies `mov word ptr [eax], si` at
`5EE19B`, called from `5EE34E -> 5EE180`. The caller obtains two surface locks
at `5EE22F` / `5EE24F` and does not branch on their HRESULTs before copying.
The retained first caller descriptor has a null surface pointer, but actual
lock HRESULTs were not observed. Do not claim a specific lock failure,
lost-surface cause, or debugger/wrapper causality from this evidence alone.

Private receipts (outside Git):
- `gate13-native-decisive-20261005-capacity.json`, SHA-256
  `df539e660f6c04e57ee2797d4df6cde8b6c10622a9c1a93bd9b8d87a0f062546`;
- renewed consent SHA-256
  `863850e0d613bf68335d3e8ac1985b29bf5e465de6fba9374f5784e208cacc80`;
- offline adjudication SHA-256
  `8e0936b2284dd6cae2fbe6730f5e5f7004b836283a576949660eb5ce51c16894`.

**Next action at the failed capacity checkpoint (superseded above):** a separately scoped bounded observation of actual
surface-lock HRESULT/descriptor returns at `5EE232` / `5EE252`, stopping before
unsafe copying and never replacing pointers/returns or adding compatibility
shims. The one approved capacity run has now executed; its live expiry is not
authorization for automatic retries or an additional diagnostic run. No repeat
approval of the already-executed run is requested. Once safe startup is restored,
resume the unchanged all-user-thread capacity proof and genuine human-away
report -> disk save -> fresh reload -> ordinary right-click -> rendered PMatchInfo
chain. No broad static scans, Gate-14 work or ownership changes are required.

Current-code focused watcher/display checks: **49 tests passed**. No new full
reconstruction, Windows/Tk closure or playable-release pass is claimed by this
failed native probe. Prior CI results below remain historical verified results.

At approximately **2026-10-05 01:12 KST**, Daniel explicitly approved the exact
bounded probe below: one supervised human-operated original-game run, maximum
300 seconds / 4096 debugger events, selected array index 5 / qualified DBRClub
ID 5, existing topmost-only presentation shim, manual Windows Volume Mixer
audio, no injected capacity/report/registry/simulation values, and stop before
executing the selected `0x5DA538` read.

The user-approval blocker is therefore cleared for **this one probe**. The
temporary ChatGPT takeover session receiving the approval has no Windows
desktop/computer/shell execution surface, so it did **not** launch
`FOOTBAL.EXE` and no native receipt is claimed.

The existing safety contract still requires a live UTC consent expiry covering
the exact five-minute execution. A Windows-capable continuation should use this
recorded approval to create the renewed private consent receipt immediately
before execution with a live <=1-hour UTC expiry covering the 300-second bound,
revalidate the exact qualified private stage, and call
`observe_supervised(..., club_index=5)`. Do not weaken or bypass that expiry
check.

No additional static/source analysis is required before the probe. Its receipt
is now the decisive next evidence:
- a `+13C/+140` hardware trap => adjudicate the writer and receiver;
- selected `0x5DA538` with uninterrupted all-user-thread coverage and no
  write => classify only the actual receiver bytes as unchanged allocation
  bytes for this exact lifecycle, never as a general zero initializer/default.

## Gate-13 takeover reconciliation / exact next probe (5 October 2026 KST)

Temporary Gate-13 closure work is now reconciled onto current-main-based PR #346;
the preserved stale checkpoint remains separately recoverable. PR #346 head
`b23bd281a666dea3ee48d6dba394932e2a21854a` contains all verified PR #309
Gate-13 implementation/evidence plus Worker-1's disjoint Gate-14+ main work.
`agent-runtime` is untouched.

The native capacity watcher now verifies DR0/DR1/DR7 on every live target thread
before every target-process continuation from `40BC14` allocation through the
selected `5DA538` stop, including arming/read-back on `CREATE_THREAD_DEBUG_EVENT`
before that new thread can resume. It can therefore produce a fresh receipt
proving uninterrupted user-thread coverage; it deliberately does not claim
kernel/external-writer coverage.

Canonical source adjudication also closes the known producer candidates:
`405A40` constructor and `403660` import do not write `+13C/+140`;
HeapAlloc uses flags 0, so allocation-time 0/0 is not a zero-fill/default
contract; `40BD10 -> 40BE30` copies those fields only into the separate
`!Spare` object; and the real writer `618C10` is confined by its three direct
call sites to the recovered user/stadium setup path. No zero default has been
promoted.

**Original launch remains prohibited until Daniel explicitly approves it.**
The only remaining next action for this lifecycle is one supervised,
human-operated native observation using the already source-qualified path:
maximum 300 seconds / 4096 debugger events, selected array index 5 / qualified
DBRClub ID 5, with the existing exact non-topmost presentation shim and manual
Volume Mixer audio. The probe must stop before executing the selected
`0x5DA538` read, retain all-thread watch checkpoints and actual receiver
`+13C/+140` bytes, and either capture an authoritative write or prove the
run reached that read with uninterrupted user-thread write-watch coverage and
no write. No capacity value, report input, registry value, simulation result or
additional compatibility behavior may be injected.

If the no-write case is proven and the receiver again contains 0/0, classify
that only as the observed allocation bytes remaining unchanged in this exact
lifecycle, never as a general initializer/default. Then integrate only the
resulting source-proven behavior and continue the required human-controlled
**away** calculated fixture -> complete report -> disk save -> fresh process/
reload -> ordinary Fixtures right-click -> correct PMatchInfo route.

Reconciled verification before this documentation checkpoint: focused Gate-13
CI **643 tests / 22 expected skips**; full reconstruction CI **2,210 tests /
23 expected skips**; repository asset policy and Windows release-candidate
package job all passed. Gate 13 remains OPEN.

## Supervised allocation-to-attendance milestone (4 October 2026 KST)

**Daniel explicitly stopped further original-game launches while playing an
esport match. Do not launch again until he explicitly says it is fine.**
The proposed14:05UTC extension was NOT approved. Offline analysis/tests/docs
may continue; no desktop interaction, policy/audio work or ownership change.

PR #309 advances beyond startup: Daniel selected Southport (canonical club 349)
and advanced normal play. The first supervised run deliberately stopped at its
512-event ceiling after 42.25 seconds, not a native crash. The separately approved
five-minute plan now uses the existing 4096-event ceiling; ordinary CLI remains
bounded to 60 seconds. No further compatibility adaptation was added.

The next run reached fresh allocation/construction/import of watched DBRClub
ID 5 (Coventry City), then its actual uncontrolled attendance read at `0x5DA538`.
It deliberately terminated there after **77.719 seconds / 1270 events**, before
executing the stopped instruction. Exact selected receiver identity is retained;
this is not merely an attendance read belonging to another club. No hardware
write was recorded, and `+0x13C/+0x140` still read 0/0. **Neither observation proves
initialization, a zero default, or continuous all-thread watch coverage.**
The receipt does not retain DR0/DR1/DR7 read-back; support tooling now retains
that witness and actual attendance-receiver identity/fields in future runs.
These additions have synthetic contracts, not a new native execution receipt.
Do not manufacture a producer or promote this snapshot into report inputs.

Private `gate13-native-capacity-supervised-20261004-r2.json` SHA-256:
`abcfa7ea4af09a8cc60f63f67409d3cda8daf27cc64727d8a8190873f0a6d42f`.
Daniel reports Southport's first fixture was a HOME 1-1 against Dagenham;
it is not proof of a human-away fixture/report. All non-activation desktop
checks passed. Original terminated; no native process remains from the probe.

Daniel explicitly renewed foreground/focus approval until **2026-10-04
13:40 UTC / 22:40 KST** for the supervised five-minute probe. The new private
consent receipt preserves prior physical display evidence unchanged and does
not claim a new DXGI observation. Consent receipt SHA-256:
`0350a81816b2fbee95dfcbbe8b8d028d30c7fefa1f64f9704a220c2aff44a40f`.
After expiry, no original launch is authorized by this historical consent.
Any new supervised run needs a new explicit agreed foreground window; all
other display safeguards and Daniel's manual audio condition remain mandatory.

**Exact next action:** verify debug-register/watch coverage from allocation
through this source-qualified attendance receiver; adjudicate the absence or
presence of an authoritative write/copy/alias lifecycle without inferring zero.
Then integrate only proven semantics and prove human-away complete report ->
save -> fresh reload -> ordinary Fixtures right-click -> rendered PMatchInfo.
Gate13 stays OPEN; no new closure/Windows schema8 pass is claimed. Gate14 and
ownership unchanged. Broader regression results are recorded below/by checkpoint.

Final offline validation: **2082 reconstruction tests / 23 expected skips**
pass on the final code (292.054 seconds), along with **46 focused probe-safety
tests**, repository asset policy, JSON and diff checks. No new Windows/Tk
closure audit is claimed for debugger-only changes.

## Exact-callsite shim and activation trace (historical prerequisite)

Daniel accepted 3c7a17ef and authorized only a probe-local dwExStyle adaptation
at canonical CreateWindowExA call 6A6363. The checksum-qualified instruction and
all twelve stack arguments are checked; only WS_EX_TOPMOST is cleared iff present.
Read-back verifies all other style bits and eleven arguments unchanged. Disk code,
fullscreen/game globals, registry, capacity and simulation state are not adapted.
This is compatibility evidence, NEVER original-game semantic evidence.

The bounded shim display run proves exstyle **8 -> 0**, XOR 8, unchanged other
arguments and on-disk executable. It stopped at **0.516 seconds / 109 events**
on foreground takeover, before native graphics success. Its game window was not
topmost and had no capture; desktop stayed 2560x1440 / 32 bpp / 165 Hz and no
unrelated geometry violation was reported. Original terminated; display did not
qualify. Private `gate13-native-windowed-shim-qualification-20261004.json` SHA-256:
`34a65dadf22f17ee463ae41a7b07150e47c42fd86e03b2a720768720903498e1`.

Daniel then permitted temporary foreground observation for the next hour. A
separate ten-second/256-event activation trace (no added shim) reached the window
creation return at **6A6369**, then stopped BEFORE **6A6016 SetForegroundWindow**
with that same HWND. It ended at **0.563 seconds / 111 events**, with no display
violations and unchanged disk executable. Private `gate13-native-activation-boundary-20261004.json`
SHA-256 `6977ad4ca72f6d384849b75bfd4ae03d10b6479bf82695a490c945d6f9240d45`.
That explicit request is now runtime/source-qualified; this observation-only
receipt does not qualify normal runtime or capacity execution. Native visible
creation has source style 90000000 (853230 initialized WS_VISIBLE, OR WS_POPUP).
No extra activation call was suppressed or return fabricated. The first failure
alone did not distinguish implicit creation activation from the later call.

Daniel explicitly approved executing the original startup foreground call and
temporarily accepting foreground/focus during qualification/capacity probes until
**2026-10-04 13:22 UTC / 22:22 KST**. This is an expiring human-managed condition,
not another compatibility patch or an unsafe override. Every other check is strict.

**Display now qualified within that consent window.** The ten-second exact-stage
run reaches native graphics-success 6153A0; topmost-only shim read-back and actual
wrapper load pass. Loss-free Microsoft-Windows-DXGI events report Windowed=true
for the actual returned game HWND and its 800x600 swap chain. Stable visible HWND
samples independently bind that HWND. Desktop remains 2560x1440/32bpp/165Hz;
no topmost/capture/unrelated geometry violation. The native captionless WS_POPUP
is qualified by actual DXGI state, never by appearance or assumed fullscreen mode.
Private `gate13-native-windowed-dxgi-20261004-r2.qualified.json` SHA-256
`0e96f4e83d804b7068a0fbd8e72f24289203e8d22be80b5e1eb4f9487603ab82`;
ETL SHA-256 `fc52bcaeb5a00376b8cc1c4585d884ae92eb6c0fe7230af39569ca2b7472c1d3`.
Zero events lost; no observed exclusive-fullscreen request. Schema-4 reader
re-adjudicates exact PID/HWND DXGI rows and rejects expired approval or any
non-activation safety problem. The original is terminated after each bound.

**Capacity watch resumed successfully after display qualification.** The narrowed
60-second r6 run reaches fresh-world50D630, allocation40BC14, construction40BC43
and import40BA2C of qualified DBRClub ID5 (array count1246). Hardware watches are
armed before construction. No +13C/+140 write or uncontrolled read was observed;
zero snapshots do NOT prove initialization and cannot supply report inputs.
Private `gate13-native-capacity-qualified-20261004-r6.json` SHA-256
`5d7e0e6839788bfbb805d7e20c9083287384ac7ada622878e8444088b74134ca`.
Desktop checks remain satisfied under expiring foreground/focus consent; original
terminated and disk hash unchanged. First root redraw53120A->53120F and its
renderer call/return both complete; actual target belongs to exact private
DDraw.dll. This is NOT a permanent renderer-stall finding or reason for another
compatibility patch. Startup movies return normally. Repeated first-chance C++
ThrowInfo8375592 source-resolves to eEPanelDeleted, not a guessed missing-file
error; no exception/return was bypassed.

Historical next action, superseded by the supervised milestone above: continue the armed fresh receiver's native write/
copy/alias lifecycle through an actual uncontrolled-home attendance read, then
adjudicate the producer, integrate only proven semantics and verify human-away
report/save/fresh-reload/right-click/PMatchInfo. Automated inspection of the
elevated original did not reliably show its surface (helper reports integrity
limitation); no blind input was sent. Daniel has been asked about supervised
native interaction. No extra presentation/game-state patch is authorized.
After13:22UTC, this receipt/consent cannot authorize another native launch; arrange
a new foreground window before any supervised probe. Audio remains manual.

Audio remains accepted user-managed Volume Mixer; Azure/signing/custom mute work
is stopped. Gate13 stays OPEN; Gate14/ownership unchanged. That prerequisite
checkpoint passed44focused tests; latest validation is recorded above. No fresh
Windows closure audit is claimed for debugger-only work.

## Historical pre-shim display checkpoint (3c7a17ef; superseded above)

**Daniel has stopped Azure CLI / Artifact Signing / custom mute-helper work.**
Audio is an accepted user-managed Windows Volume Mixer condition, not a Gate-13
prerequisite. Do not resume signing, discovery, paid infrastructure or automated
silence qualification. Historical receipts remain evidence only.

PR #309 preserves the proven installer-selector repair and earlier fresh-club
allocation/import. Neither establishes the `DBRClub +13C/+140` producer.
The newly authorized smallest display-only original probe loaded the exact
private dgVoodoo 2.87.5 wrapper but stopped after **1.969 seconds / 106 debug
events** on `probe_window_always_on_top`. Desktop mode stayed **2560x1440,
32 bpp, 165 Hz** before/after; no unrelated-window geometry or foreground
violation was reported. The child was terminated and no original remains running.
Non-exclusive desktop safety is **NOT qualified**. Private receipt:
`work/gate13-native-windowed-qualification-20261004.json`, SHA-256
`ce3733c202181e9ffda2d75a573dd3982b8790fa866d376a17eb5ccc47dff23a`.
This receipt lacks the offending window's class/pre-termination snapshot, so
its exact runtime owner is not established. Future monitoring retains both.

Canonical static source explains a concrete unsafe native request:
`615260 -> 615262` explicitly sets bit 0 in `8547AC`; the renderer routes
that bit through `6AFFD6 -> 6B96B0 -> 6A5060` into `A9115D`.
`6A6230`'s nonzero-mode branch sets `WS_POPUP` and `WS_EX_TOPMOST=8`
before `CreateWindowExA` at `6A6363`. This is not an inferred command-line
option or a capacity producer. Prepared forced-windowed config alone did not
prevent the observed topmost window; do not repeat that unchanged launch or
patch this native flag. The debugger now stops **before** a topmost window API
request while the debug event still suspends execution. Graphics acceptance is
checked at the actual successful return `6153A0`, not the unrelated software
renderer query `6151B5`.

**Exact next action:** source/vendor-qualify a presentation-only compatibility
method that removes the native topmost request without changing game logic,
capacity state or desktop mode. Then qualify that exact stage with the bounded
display-only probe (manual Volume Mixer audio), and require its successful
schema-2 receipt before allocation/write-watch. No unsafe override exists.
If the only evidence-valid route requires desktop disruption, ask Daniel before
executing it. No repeated original launch is authorized by an offline config pass.

After display qualification, resume the existing fresh uncontrolled allocation/
import hardware-watch through the attendance read, adjudicate writes/copies/
aliases, integrate only source-proven values, and prove the genuine human-away
report -> save -> fresh reload -> Fixtures right-click -> PMatchInfo route.
Continue remaining required Gate-13 closure work. Gate 13 stays OPEN; capacities
and the human-away report remain fail-closed. Ownership/Gate-14 work are unchanged.
This environment/debugger checkpoint does not claim a new full-suite or real
Windows schema-8 closure audit. **33 focused tests**, repository asset policy,
state JSON and diff checks pass; no test launches the original.

## Gate-13 installer prerequisite advanced (4 October 2026 KST)

PR #309 remains on `codex/gate13-uncontrolled-capacity-lifecycle`. Latest fetched
main is `8b4969e01d3168a77f4f1caab45e944efea0698e`; merge `51762b6d` preserves
its disjoint worker commits without changing Gate-14 implementation or the
Gate-13 lock. Prior broader validation through `29781e92` remains historical.

Daniel's explicitly approved missing-only repair is now source-qualified and
verified. The authorized original INS 3.00.077 writes each component's exact
selection byte as REG_DWORD: 1 selected / 0 unselected. The original full-component
configuration was applied only to missing art / stadia / fmv / matchengine in
the existing 32-bit installation key, after export. Install Dir / CD Drive,
Settings and all game files were left unchanged. Private source/before/after
receipts and the rollback are in `GATE13_INSTALLER_RESOURCE_SELECTORS.md`.
Actual original startup now accepts all four type-4 / size-4 / value-1 selectors
and returns setup AL=1. No capacity/report value follows from this success.

Exact original DLL staging has now removed the null driver call (`6151EB` ->
`A911EC`): ThrashSoftware loads and graphics initialization returns success.
The following run with verified original data reaches fresh-world allocation,
construction and import of qualified DBRClub ID 5. No capacity writes or
uncontrolled read were observed within the bound; zero snapshots are explicitly
not initializer proof. After qualifying the non-exclusive probe environment
above, complete the private original startup resource dependencies, continue the
real allocation-to-uncontrolled-read watch and
adjudicate the actual +13C/+140 writer/copy lifecycle. No source-proven initialized
capacity or human-away complete report is claimed. Ten debugger
checks pass; gameplay/presentation code is unchanged, so prior full/Windows
receipts below remain historical evidence, not a new closure claim. Gate 13
remains OPEN. Do not touch Gate 14 or the ownership protocol.

## Historical local Gate-13 closure result (base `29781e92`; live action above)

Codex started a fresh `codex/gate13-uncontrolled-capacity-lifecycle` branch
from fetched canonical main `3a3f60d1e89c7f44e7f12ca70fef3f263fe73a9b`.
It subsequently preserved the worker's disjoint commits through
`29781e9278c4a50ca0921723fa7614314f793b0d` by merge `c9c64fa0`.
The exclusive Gate-13 ownership lock and disjoint Gate-14 work are unchanged.
Existing report production/persistence/rows/arrows were not retraced or changed.

A checksum-gated bounded WOW64 debugger now calibrates against the original
entry point **and actual known CRT dword writes**, and can arm exact fresh-array capacity write watches before club
construction. It did **not** reach allocation: non-admin install-key open
returns 5; Daniel-approved elevation changes that result to 0, but the native
mandatory `art` DWORD query returns 2 and setup exits. No installation key,
executable file, capacity or report input was altered to bypass this guard.
See `GATE13_NATIVE_CAPACITY_WATCH.md` for exact probes, receipts and limitations.

The three pending native scroll assets have been extracted from the rehashed
authorized archive, strictly receipt-validated and provenance-imported. All
five scroll loader-family identities now verify. The original thumb rectangle,
range and `0.49900001287460327` conversion contracts are retained without
inventing pixels/input. Twenty-six focused checks and asset policy pass.
Fresh **current-main-based Windows 11/Tk schema-8 passes**, as does the genuine
controlled-home calculated fixture -> save -> fresh reload -> ordinary
right-click -> rendered PMatchInfo regression. The repeated human-away probe
still publishes no report/link. Fresh criterion-by-criterion results and private
receipt hashes are in `GATE13_CLOSURE_AUDIT.md`; timing/normal-play closure
does not pass. Full starting-base regression: 2,004 tests / 23 expected skips;
final post-merge regression: **2,011 tests / 23 expected skips, no failures or
errors**. The subsequent calibration-mode guard is separately included in the
26 passing focused checks; native entry/hardware calibration also passes.

Gate 13 remains **OPEN**. Exact capacity next action: source-qualify original
installer resource-location selectors and obtain approval before repairing
the existing installation keys, then observe actual allocation-to-uncontrolled
read and adjudicate the writer/copy lifecycle. Do not infer zero or inject
controlled-home values. Continue independently source-backed report-scroll
geometry/input and required normal-play closure work while this native startup
prerequisite is unresolved. `Setup/English/SETUP.INS` and its exact component/
registry text are staged privately and hashed; component names alone do not
authorize DWORD flag values. Administrator-debugger approval did **not**
authorize modifying installation keys. No raw dump/executable/archive/save
entered Git, and no full-original-functionality scope reduction is made.

## Recovery 255 Gate-13 League Fixtures grid-selector checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN.

PR #291 merged as canonical main `02b5d5c8` after **1,960 tests / 23 expected skips**, **594 Gate-13 tests / 22 expected skips**, repository asset policy, and the Windows release-candidate package workflow all passed. The live management presenter/host now accepts only the exact source-proven `PLeagueGrid` left-press boundary: half-open screen rectangle `(378,235,348,336)`, 29x14 point reduction, visible column selector `0..11`, visible row selector `0..23`, and only materialized source cells. PMenu retains priority where screen regions overlap; PMatchInfo remains on its separately recovered right-press/context route.

A source-evidence re-check during PR #291 **removed** the provisional single-cell visual-selection interpretation before merge. `0x46D300` dispatches the column and row selector indices separately, while the older `+0x109B0/+0x109B4` toggled-box trace describes a 24-entry selected-index update. The repository now explicitly records that this does not prove one clicked `(column,row)` maps to one toggled cell. Exact selector-band composition remains fail-closed until the `0x46CF90` / `0x46D140` data flow into those selected-index fields is source-closed.

Private execution briefly recovered enough to launch one trivial process. The authorized **511,121,336-byte** source ZIP and **688,773-byte** persisted runtime ZIP were then successfully materialized to the workspace. Every subsequent shell launch, a minimal independent shell reprobe, and the separate Python execution path failed before process start with `caas.internal.errors.ClientError`. No source hash, PMatchInfo scroll extraction, remaining-setup trace, selector data-flow result, or new Windows receipt is claimed. Source/runtime availability is not the blocker; sustained process startup is.

Exact private actions when sustained execution returns remain: (1) run the PMatchInfo scroll exact-path inventory with `--deep --hash-source --only-explicit --require-all-explicit`, validate the private staging receipt and import only verified assets; (2) run the bounded remaining-setup trace for fresh uncontrolled club `+0x13C/+0x140` and manually adjudicate authoritative writes/lifecycle; (3) source-close `0x46CF90` / `0x46D140` -> `+0x109B0/+0x109B4` before rendering any toggled selector bands; and (4) rerun the current-main real-Windows graphical audit.

Next cloud-safe action: do **not** infer the PLeagueFixtures country/League runtime list from generic `state.competitions` ordering. Audit and expose a fail-closed source-data contract for the already-recovered eight country selector identities/events and the dynamic League selector input requirements, so later integration cannot silently substitute modern/dictionary ordering for the original DBRCountry competition-array order.

## Recovery 255 Gate-13 League Fixtures paging checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN.

PR #289 merged as canonical main `b28c4697` after **1,951 tests / 23 expected skips**, **585 Gate-13 tests / 22 expected skips**, and repository asset policy passed. The integrated `OriginalManagementPresenter` now carries the already-recovered `PLeagueFixtures+0xA4` 12-club column window and exposes a source-accepted non-pointer paging seam. For the canonical 20-club shape the exact recovered transition is 0 -> 8, clamps at 8, and returns 8 -> 0. Fresh panel navigation resets to source offset 0. No page-button rectangle, caption, keyboard binding, hover state or pointer-event equivalence is claimed.

PR #290 merged as canonical main `0ebdd839` after a test-fixture correction and final verification of **1,953 tests / 23 expected skips**, **587 Gate-13 tests / 22 expected skips**, repository asset policy, and the Windows release-candidate package workflow. `OriginalGameTkHost` now exposes the same source-accepted League Fixtures paging seam at the live host boundary, redraws only after that accepted transition, and remains fail-closed outside MANAGEMENT. The ordinary Tk `<Button-1>` handler is deliberately unchanged, so this does not invent the missing page-button input mapping.

Private PMatchInfo scroll extraction/capacity lifecycle work remains infrastructure-blocked exactly as recorded below. The next cloud-safe Gate-13 action is to integrate the already source-proven League Fixtures **grid** pointer-selection path, whose exact control rectangle is `(378,235,348,336)` and whose recovered point reduction is 29x14, while keeping paging-button geometry and any unrecovered selector-control geometry fail-closed. Reuse the existing source-backed selected-cell/toggled-box projection; do not infer new visual semantics.

## Recovery 254 Gate-13 PMatchInfo scroll staging checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN.

PR #287 merged as `eb44dd11` after **1,944 tests / 23 expected skips**, **578 Gate-13 tests / 22 expected skips**, and repository asset policy passed. The three pending PMatchInfo vertical-scroll resources are now bound to one exact source-relative staging set for the existing fail-closed source inventory: `scroller_bar_vert.444`, `scroller_blue_bar.444`, and `vscroll_blue_bar.444`. No unknown checksum, byte size, geometry or behavior is assigned before extraction.

PR #288 merged as `14ef3211` after **1,948 tests / 23 expected skips**, **582 Gate-13 tests / 22 expected skips**, and repository asset policy passed. A private-only staging receipt validator now requires one complete exact-path extraction report with `only_explicit=true`, no unresolved paths, a real source SHA-256, exactly one extracted candidate per required path, and byte-for-byte size/hash agreement with the staged files. It records raw EA444 header dimensions only and keeps `native_scroll_behavior_recovered=false` and `renderer_geometry_recovered=false`. Its output must remain outside Git.

Private execution was reprobed after these checkpoints and still fails before process start with `caas.internal.errors.ClientError`. The authorized source/runtime archives are already materialized from earlier Recovery-254 work, but no new extraction, source hash, asset identity, renderer behavior, or canonical executable result is claimed.

Exact next private action when execution recovers: run the exact-path source inventory with `--deep --hash-source --only-explicit --require-all-explicit`, validate the resulting staging directory/report with `gate13_pmatchinfo_scroll_stage_receipt.py`, then import only verified assets with provenance. This closes byte identity only; native thumb/bar geometry and interaction still require separate source adjudication.

Next cloud-safe Gate-13 action: integrate the already recovered PLeagueFixtures 12-club paging offset into the stateful management presenter through a source-accepted non-pointer seam. Do not invent page-button hitboxes or claim ordinary user navigation until those controls are source-qualified.

## Recovery 254 Gate-13 PMatchInfo scroll-resource checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN.

PR #286 merged as canonical main `df098e6d` after **1,942 tests / 23 expected skips**, **576 Gate-13 tests / 22 expected skips**, and repository asset policy passed. The repository now has a fail-closed PMatchInfo vertical-scroll readiness inventory for the already source-identified loader family. It verifies the two currently staged identities (`scroller_vert.444` and `vscroll_end.444`) and explicitly reports `scroller_bar_vert.444`, `scroller_blue_bar.444`, and `vscroll_blue_bar.444` as missing/pending. Native thumb/bar geometry, composite blits, x87 page/range arithmetic, hover, six-tick held-repeat, wheel and drag behavior remain unrecovered and are hard-coded false rather than inferred.

PR #287 is the current follow-up. It binds exactly those three pending assets to a durable source-relative path file consumable by the existing `gate13_source_inventory.py --extract-path-file --only-explicit --require-all-explicit` flow. It does not assign hashes, byte sizes, geometry or behavior before authorized bytes are actually extracted and verified. Focused Gate-13 CI and asset policy are green on the current PR head; full reconstruction CI is still running.

Private execution remains infrastructure-blocked in this allocation. The authorized source and persisted runtime archives were materialized successfully earlier in Recovery 254, but subsequent shell and independent Python process startup failed with `caas.internal.errors.ClientError`. No extraction or private-native scroll result is claimed.

Exact next action after PR #287 verification: if sustained private execution is healthy, run the exact-path staging pass against the authorized source with source hashing and retain the private selection report; otherwise add a fail-closed private staging-receipt validator that requires all three candidates to come from one complete hashed exact-path inventory before any import. Do not infer renderer behavior from asset identity.

## Recovery 254 Gate-13 bounded setup-access checkpoint

PR #284 merged as canonical main `88a3d38a` after **1,937 tests / 23 expected skips**, **571 Gate-13 tests / 22 expected skips**, and repository asset policy passed. The remaining-setup private trace can now optionally classify exact unresolved displacement operands only inside the seven source-qualified `REMAINING_SETUP_WINDOWS`. It reuses `REMAINING_GATE13_FIELDS`, records Capstone read/write/read-write direction plus base/index register and window/instruction identity, and labels every hit `bounded_linear_candidate_not_cfg_or_object_proof`. The classifier refuses to run outside `--remaining-setup-only`; it does not prove object identity, reachability, writer ownership, initialization semantics, a capacity value, or Gate-13 closure.

Recovery 254 briefly restored one shell process and successfully rematerialized the authorized 511,121,336-byte source archive plus the persisted reconstruction-runtime ZIP from the Library. The next shell launch failed before process start with `caas.internal.errors.ClientError`. No canonical executable scan, new source hash, writer identity, or runtime result is claimed from this recovery.

Exact private action when sustained execution returns: run the canonical executable with `--remaining-setup-only --classify-remaining-field-accesses`, then manually adjudicate the emitted candidates through CFG/data-flow from fresh club allocation to the uncontrolled `+0x13C/+0x140` read. Do not promote any candidate solely from displacement/access metadata.

Until that private path is healthy, continue independent Gate-13 work that is already source-backed and does not depend on the unresolved capacity lifecycle. Preserve current PMatchInfo remaining blockers: native thumb/bar/hover/held-repeat behavior, remaining required shirt/color contexts, current-main real-Windows rerun, and final timing/normal-play recognizability.

## Recovery 253 Gate-13 remaining-setup trace checkpoint

PR #283 merged as `7cfcad7c` after **1,935 tests / 23 expected skips**, **571 Gate-13 tests / 22 expected skips**, and repository asset policy passed. The current live-report private trace now has a checksum-gated `--remaining-setup-only` scope containing only seven already-known lifecycle neighborhoods around fresh club `+0x130/+0x13C/+0x140`, DBRClub construction, D48, player selection/assignment, and attendance/capacity. Its evidence contract remains explicitly fail-closed: `remaining_setup_trace_complete=false` and `legacy_capacity_writer_identified=false`.

Private execution is still infrastructure-blocked after the authorized source/runtime files were materialized: both shell and independent Python process startup fail with `caas.internal.errors.ClientError`. No new original-byte hash, writer identity, capacity value or Windows result is claimed.

Exact next private action when sustained execution returns: run the canonical executable through the bounded remaining-setup trace, follow allocation-to-uncontrolled-read data flow and identify the authoritative write/lifecycle for `+13C/+140`. Do not substitute zero, a controlled-stadium value or a guessed percentage.

Until then, the next cloud-safe Gate-13 aid is to classify exact `+0x130/+0x13C/+0x140/+0x76` memory-operand candidates **inside those seven bounded windows only**, retaining read/write access and register context while explicitly refusing to infer object type or semantics. This should prioritize private CFG review without repeating the existing whole-.text displacement scan.

## Recovery 253 Gate-13 PMatchInfo row reconciliation checkpoint

PR #282 reconciled the verified PR #242 native report-row milestone onto current canonical main as `ac9a417d` without overwriting newer project/status ledgers. The transplant used exact Git blob identities for 31 files that had not changed on main since PR #242's base: the native packed-script row implementation/tests, original PMatchInfo host/resource changes, provenance manifest, twenty original Premiership primary custom-shirt atlases, the original vertical scroller atlas, and Gate-13 evidence documents.

Fresh hosted validation on the reconciled current code passed **1,933 tests / 23 expected skips**, **571 Gate-13 presentation tests / 22 expected skips**, repository asset policy, and Windows release-candidate package build/smoke. The older private genuine calculated-fixture route receipt and real Windows schema-8 receipt remain valid historical evidence for the byte-identical Gate-13 milestone files, but Recovery 253 did **not** rerun that private real-Windows route on `ac9a417d`; current-main graphical rerun remains pending.

The older "required PMatchInfo script rows remain blank/withheld" wording below is superseded. Controlled-home report rows now render source labels/minutes, player abbreviations/selection colors, icons, primary numbered custom shirts, blank slots and source single-press arrow traversal; both retained eight-entry lists were previously exercised through actual Tk press/release. Gate 13 remains OPEN. Fresh uncontrolled club `+13C/+140` still has no authoritative initializer/lifecycle value and the genuine human-away/uncontrolled-home probe publishes no complete report. Native thumb/bar/hover/held-repeat behavior, remaining required shirt/color contexts, current-main real-Windows rerun, and final timing/normal-play recognizability remain open.

Exact next Gate-13 action: recover the existing fail-closed remaining-setup trace harness from stale PR #210 only if it still composes with the current evolved live-report trace, then use it on a sustained private execution allocation to observe the allocation-to-read/write lifecycle for `+13C/+140`. Do not infer zero from HeapAlloc flags or substitute controlled-stadium values.

## Recovery 253 Gate-17 final-audit preflight checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #280 merged as `c8ab34e6` after **1,915 tests / 23 expected skips**, repository asset policy, and Windows release-candidate packaging passed. The external Windows validation transaction now refuses to create its work root or immutable release receipts unless the canonical repository-side full-scope implementation preflight is green for the same player seed and day bound.

PR #281 merged as `e522672a` after **1,917 tests / 23 expected skips**, repository asset policy, and Windows release-candidate packaging passed. Direct `run_final_release_audit()` now independently re-runs that same canonical full-scope implementation preflight, records the green preflight payload in the final receipt, and cannot be used to bypass human-scope, runtime-owner, per-scope save/reload, six-user multi-human, or completed-state progression blockers by supplying plausible external JSON.

Recovery 253 briefly regained local shell execution and successfully materialized both persistent private inputs: the authorized 511,121,336-byte source archive and the persisted reconstruction runtime ZIP. Subsequent shell launches failed before process start with `caas.internal.errors.ClientError`, so no new private source hash, Gate-13 behavior, or canonical preflight execution is claimed.

Exact next action: Gate 13 remains the highest-value validation gate. PR #242 contains a verified source-backed PMatchInfo script-row/arrow milestone from an older base and overlaps current main in only four status/research files; reconcile its disjoint technical/resource changes onto current main rather than reimplementing them. Preserve the four newer canonical status files and manually merge only still-valid Gate-13 evidence wording. Gate 13 remains OPEN after that milestone; the unresolved fresh +13C/+140 capacity lifecycle and remaining native scroll/kit/color/timing criteria stay fail-closed.

## Recovery 252 Gate-17 canonical preflight checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #278 merged as canonical main `9fc7c2e5` after **1,911 tests / 23 expected skips** plus repository asset policy. The repository now has one diagnostic canonical full-scope preflight coordinator that assembles the human-scope, runtime-owner, per-scope save/reload, multi-human and live progression audits from a verified game directory. The live progression leg uses one deterministic controller and remains read-only; missing allocation-plan state fails closed. PR #279 separately reconciled the full-scope evidence wording as `46a29d7f`, removing the stale Premier-League-only handoff claim while preserving secondary, multi-human, objective/progression and Windows blockers.

Private canonical execution remains infrastructure-blocked in this recovery: the authorized 511,121,336-byte source archive was successfully materialized from the Library, but both the local shell and Python execution paths failed before process start with `caas.internal.errors.ClientError`. No private preflight result is claimed.

Exact next cloud-safe action: bind the final external Gate-17 Windows release transaction to the canonical full-scope implementation preflight. External validation must refuse to create any release work root or receipts while repository-side full-scope capability is known incomplete, instead of relying only on a separately supplied external full-scope receipt.

## Recovery 252 Gate-17 canonical preflight checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #278 merged as canonical main `9fc7c2e5` after **1,911 tests / 23 expected skips** plus repository asset policy. The repository now has one diagnostic canonical full-scope preflight coordinator that assembles the human-scope, runtime-owner, per-scope save/reload, multi-human and live progression audits from a verified game directory. The live progression leg uses one deterministic controller and remains read-only; missing allocation-plan state fails closed. PR #279 separately reconciled the full-scope evidence wording as `46a29d7f`, removing the stale Premier-League-only handoff claim while preserving secondary, multi-human, objective/progression and Windows blockers.

Private canonical execution remains infrastructure-blocked in this recovery: the authorized 511,121,336-byte source archive was successfully materialized from the Library, but local process execution failed before startup. No private preflight result is claimed.

Exact next cloud-safe action: bind the final external Gate-17 Windows release transaction to the canonical full-scope implementation preflight. External validation must refuse to create any release work root or receipts while repository-side full-scope capability is known incomplete, instead of relying only on a separately supplied external full-scope receipt.

## Recovery 252 Gate-17 save-scope preflight checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #277 merged as canonical main `ed997a0a`. Full-scope implementation preflight now includes an independent, catalog-ordered per-scope save/reload capability audit. Runtime ownership can no longer imply persistence readiness: serialization and post-load continuation are required separately for each exact TeamSelect scope and owner class. Fixed-primary and procedural-primary scopes use the existing dedicated continuation surfaces; procedural-secondary scopes remain explicitly blocked on missing serialization and continuation. Hosted verification passed **1,909 tests / 23 expected skips** plus repository asset policy. No private canonical primary-container execution or secondary persistence implementation is claimed.

Exact next cloud-safe action: add one canonical full-scope preflight runner that assembles the existing human-scope, runtime-owner, save-scope, multi-human and live progression audits from a single verified game directory/controller state. The runner must remain diagnostic and fail-closed; it should expose the exact current blocker set without mutating progression or manufacturing missing secondary/multi-human capability.

## Recovery 251 Gate-17 multi-human readiness checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #276 merged as canonical main `fc985fab`. Gate-17 full-scope implementation preflight now requires an independent multi-human capability audit tied to the source-proven hard maximum of exactly six simultaneous TeamSelect users. The six-user requirement cannot be lowered by callers or forged audit objects. Current canonical capability remains deliberately blocked: TeamSelect selection capacity is 6, but gameplay capacity is 1, multi-human Start is unavailable, one shared multi-human runtime is unavailable, and multi-human save/reload is unavailable. Hosted verification passed **1,900 tests / 23 expected skips** plus repository asset policy. No multi-human gameplay implementation is claimed.

The remaining Gate-17 runtime blockers are unchanged: secondary procedural Leagues still lack a distinct live runtime container/human route; multi-human gameplay/shared-runtime/save continuity are absent; RNG-bearing non-PL fresh chairman-objective branches still need exact caller CRT state; non-PL season-end sporting-objective progression is not source-closed; and final full-scope Windows receipts remain external blockers.

Exact next cloud-safe action: add an independent catalog-ordered save/reload capability audit to the full-scope preflight. Runtime-owner completeness must not imply persistence completeness. Fixed-primary and procedural-primary scopes already have source-backed continuation harnesses; every procedural-secondary scope must remain blocked until its own live state, serialization and post-load continuation path exist. Do not infer secondary persistence from primary-container saves.

## Recovery 251 Gate-17 primary-container save checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #275 merged as canonical main `636f4204`. Canonical save tooling now aggregates every source-backed TeamSelect **primary-container** scope in exact runtime-ownership-plan order: the fixed Premier League uses the established mid-matchday save/reload route, every procedural-primary League uses the all-scope continuation audit, and the aggregate is bound to the same TeamSelect catalog SHA-256. Every procedural-secondary TeamSelect scope is emitted explicitly as unverified; no secondary owner is routed through the primary engine. Hosted verification passed **1,893 tests / 23 expected skips** plus repository asset policy. No authorized private `--primary-container-all` execution receipt is claimed.

The remaining Gate-17 runtime blockers are explicit: secondary procedural Leagues still lack a distinct live runtime container/human route; the gameplay backend still has only one `HumanManagerState` even though TeamSelect source tracing proves up to six simultaneous users; RNG-bearing non-PL fresh chairman-objective branches still need the exact `0x5DF670` caller CRT state; non-PL season-end sporting-objective classification/progression is not source-closed; and final full-scope Windows receipts remain external blockers.

Exact next cloud-safe action: close a readiness-audit gap around the source-proven six-user requirement. The current full-scope implementation preflight measures selection/runtime ownership/progression but does not independently include multi-human backend capability, so it must not be able to report ready while the clean-room controller is still single-manager. Add a fail-closed multi-human capability input to that preflight without claiming the missing gameplay implementation.

## Recovery 251 Gate-17 primary-save catalog checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. No later-gate work below closes or bypasses its private/source-dependent criteria.

PR #274 merged as canonical main `748b4782`. The all-procedural-primary canonical save sweep is now bound to the exact hash-verified TeamSelect scope catalog: every audited competition maps to its exact ordered `<country_id>:<competition_id>` ID and the aggregate records the canonical catalog SHA-256. Missing or duplicate catalog competition identities fail closed. Hosted verification passed **1,891 tests / 23 expected skips** plus repository asset policy. This is still audit tooling only; no authorized private `--procedural-primary-all` execution receipt is claimed.

The remaining Gate-17 runtime blockers are unchanged: secondary procedural Leagues still lack a distinct live runtime container/human route; RNG-bearing non-PL fresh chairman-objective branches still need the exact `0x5DF670` caller CRT state; non-PL season-end sporting-objective classification/progression is not source-closed; and the canonical full-scope Windows receipts remain external blockers. The older Premier-League-only save receipt cannot substitute for full-catalog save continuity.

Exact next cloud-safe action: extend the canonical save audit from procedural-primary-only coverage to the complete **primary-container** TeamSelect scope using the already source-backed runtime-ownership plan, while continuing to report secondary-container scopes as unverified rather than routing them through the primary engine. Do not infer secondary-container semantics.

## Recovery 250 Gate-17 work-ahead checkpoint

Gate 13 remains the earliest incomplete validation gate and stays OPEN. Private/source-dependent Gate-13 work must not be inferred from later-gate progress.

Independent Gate-17 cloud-safe work through canonical main `053dc98f` is now:

- PR #269 / `1a4f5eea`: fresh chairman-objective setup and season-end sporting-objective progression are tracked as separate capabilities; non-PL sporting progression remains fail-closed.
- PR #270 / `06c935b7`: internal save schema 43 preserves playable primary procedural IDs, playable club IDs and the full-country allocation plan across reload.
- PR #271 / `efb9eb7b`: canonical audit tooling can source-select a live non-PL procedural-primary TeamSelect club, save with its first procedural League entry pending, reload from fresh source objects and require exact controller-policy/state/result/RNG continuation. Hosted verification passed **1,885 tests / 23 expected skips** plus asset policy. This is an audit harness; no private canonical `--procedural-primary` receipt is claimed.
- PR #272 / `053dc98f`: final full-scope Windows evidence now separately requires save/reload proof for every exact canonical TeamSelect scope ID, exact full scope count/order, and empty save/reload missing/failed lists. Hosted verification passed **1,886 tests / 23 expected skips** plus asset policy.

The remaining Gate-17 runtime blockers are explicit: no secondary procedural League runtime container/human route; RNG-bearing non-PL fresh-objective branches still need the exact `0x5DF670` caller CRT state; non-PL season-end sporting-objective classification/progression is not source-closed; and the new non-PL canonical save audit still needs its authorized private execution receipt. The older PL-centered `save_reload.json` cannot substitute for full-scope save continuity.

Exact next cloud-safe action: do not generalize any of those source-sensitive paths by analogy. If private execution is unavailable, audit the next independent release/runtime invariant or later-gate work that can be proven from existing repository evidence; preserve every source blocker explicitly. Final Gate 17 external Windows 11 evidence remains impossible until Gates 13-16 are formally closed and the full original scope is implemented.

## Current gate

**Gate 13 - Restore original management presentation**

Continuation from PR #211 head `689c91dd`: corrected scanner discovery past
undecodable bytes (still candidate-only), traced controlled capacity writer
`618C10`, and integrated original possession-percent controls, complete
Attendance/caption buffer and native-aligned name/score header. +13C/+140
fresh uncontrolled state remains unknown: the proven writer uses an existing
user-owned stadium, not fresh AI setup. Required script rows remain withheld
pending native lazy reader `60B1E0 -> 633BD0/633C50`, concrete list
`487B80 -> 4872C0`, row factory `486EC0 -> 485B30` and source clipping.
The reader exposed and now verifies a corrected native chance-family encoder
tag mapping (kinds1..4 -> tags2/3/1/0), not a second decoded-kind remapping.
Do not replay completed
report assembly/save/owner/calculator work. Gate13 remains OPEN; main,
later-gate files and ownership protocol are unchanged.

Final changed-code milestone: **1,722 full tests / 23 expected skips**;
99 focused tests / 5 expected licensed-source skips, asset policy and fresh
real Windows schema8 pass. Genuine calculated fixture2 again publishes,
saves/reloads and opens correct PMatchInfo with header/summary/pitch/possession.
Required script rows remain blank. Exact receipts and encoder discrepancy
evidence are in `GATE13_LEGACY_CLUB_REPORT_STATE.md`. No final closure or
package/release success is inferred. The first full run lacked Capstone;
the final run with the existing private runtime passes.

Latest PR #211 continuation from reconciled `70c8af0a`: the top-four D48
producer now performs the exact second full-roster Condition/RNG pass before
participant snapshots. Human club selection automatically loads the original
club stadium map/building setup, without resetting existing ticket state.
The genuine Coventry calculated fixture again publishes a complete report,
saves/reloads and opens matching PMatchInfo through real Windows right-click.
The original summary font now renders Attendance/Referee/Mom, and the default
nested pitch uses its recovered parent translation and two-row source clip.
These are partial visible contents, not complete nested report rendering.
Evidence and private receipt hashes: `GATE13_LEGACY_CLUB_REPORT_STATE.md`.
Final milestone validation: **1,713 full tests / 23 expected skips**, 91
focused report/host/save tests, asset policy, JSON/diff checks, fresh real
Windows schema 8 and repeated genuine changed-route probe pass. No frozen
package/release launch or complete nested report rendering is claimed.

Gate 13 remains **OPEN**. +13C/+140's fresh club allocation has HeapAlloc
flags 0, not a zero-fill contract; no authoritative fresh capacity value is
established. Next presentation step is default PMatchInfo score/script-row
owners, text producers and clipping, followed by the complete genuine route
and final timing/recognizability judgment. Secondary/loan shirts remain
fail-closed, not a reason to expand the minimum slice without audit evidence.
Main, Gate-14 work and ownership protocol are untouched.

Recovery-223's checksum-gated remaining-field scanner is also preserved as
support tooling. Its earlier +0x130/D48 status is superseded by the PR #211
producer proof above; the scanner remains useful for candidate discovery and
manual CFG/data-flow review of the still-open fresh +0x13C/+0x140 capacity
lifecycle and secondary/loan +0x76 selector. Candidate hits are not semantics.

Previous local Gate-13 milestone, based on canonical `6207dbe0`: native
attendance bit-9/count lifecycle and exact zero-based human-rank D48 guards
are integrated and persist in schema 42. A genuinely calculated Coventry
home fixture publishes all eleven scalars and a complete report. Disk save,
fresh reload and real Windows ordinary Fixtures right-click open the correct
PMatchInfo context (fixture 2, owner 0), without injected fragments. Fresh
Windows schema-8 audit passes. Evidence: `GATE13_LEGACY_CLUB_REPORT_STATE.md`.
Final local validation: **1,695 full tests / 23 expected skips**, 135 focused
tests, asset-policy/JSON/diff checks, fresh Windows schema 8 and the final-code
genuine reload/right-click probe all pass. Frozen-package launch is not claimed.

At that earlier checkpoint Gate 13 remained **OPEN**. Its next source task was to establish the fresh native
allocation/write lifecycle of uncontrolled visiting capacities +13C/+140;
do not assume zero. Complete the top-four D48 roster-Condition/RNG branch
without a numeric substitute. Secondary/loan shirts stay unknown. The
ordinary host still needs source-qualified stadium setup materialization;
PMatchInfo nested report rendering and final timing/normal-play judgment
are not certified by a correct stored context. Preserve all shipped-country
scope; Gate-14 work and agent-runtime ownership are untouched. Work is on
`codex/gate13-legacy-setup`, not main; no branch reconciliation was performed.

Earlier checkpoints below are historical and do not negate the new genuine
calculated-report/context proof.

PR #199 continuation from `f8bbdd9c`: B68 constructor and original-order
FE0/FE4 draws, explicit tactics, primary-shirt/normalized flag metadata and
gate scalar retention are connected at production to the existing strict
assembler. A genuine canonical calculated fixture retains six of eleven
scalars but stays fail-closed: uncontrolled-home gate inputs are unavailable.
The remaining setup boundary is legacy visiting capacities +13C/+140 and
human-opponent D48's attendance-counter/rank guard (plus secondary-shirt
contexts). Exact evidence and next action: `GATE13_LIVE_CAPTURE_INPUTS.md`.
Gate 13 remains OPEN; no genuine reload/right-click/PMatchInfo success or
final timing/Windows closure is claimed. No main reconciliation or Gate-14/
agent-runtime ownership change was made in this continuation.
Verified code checkpoint `a9388465`: **1,675 full reconstruction tests,
23 expected licensed-source skips**, plus 116 focused tests and asset-policy
checks pass. The first full run had three sandbox/private-Capstone import
errors; the access-corrected full rerun passes. No Windows/packaging success
is inferred from these results.

Local complete-report owner milestone, based on `41df3ac` and reconciled with
`050085a8`: exact source caption/context/venue/weather setup fragments and initial
normalized-history/booking bits are retained at production. Strict complete
assembly, atomic ordered GameState owner/fixture links and schema-39 save/load
are implemented. Synthetic complete-contract reload/context tests pass; no
genuine ordinary calculated-report opening is claimed. Mandatory setup scalar
and participant metadata still withholds ordinary publication. Gate 13 remains
OPEN; final timing/recognizability audit is pending the genuine route. See
`GATE13_LIVE_CAPTURE_INPUTS.md` for the exact remaining production boundary.
Parallel RNG work is preserved and agent-runtime ownership is unchanged.
Verification of this milestone: local full reconstruction suite **1,664 tests,
23 expected licensed-source skips**, asset policy and diff checks pass. No
successful real-fixture PMatchInfo/Windows claim or final closure audit is made.

PR #194 follow-on from `cfab7abc`: live calculator completion now retains
the native calendar tuple and D4C/D50 score accumulators, independently of the
semantic score property, through pending-result save/reload (internal schema
37). Metadata-only canonical-executable evidence resolves the caption binding
(English IDX 2713), venue selection, initial participant-history bit and
referee/setup selection. These are not yet a complete live report producer.
Required setup fields, adjusted initial history and caption/context inputs
remain absent from the ordinary runtime capture; no partial report/link is
published. The successful calculated fixture -> reload -> native right-click
-> PMatchInfo route remains unverified, and Gate 13 remains OPEN.

Latest `origin/main` `50b70390197ecace3297231eef5d227820a22478` was reconciled.
The parallel worker's history retention and per-side target/trajectory ordering
are preserved; Gate-13 statistics are collected from that same finalization,
not by replaying rating RNG. Reconciled focused tests: 156 passed. No new broad
closure audit, full suite, Windows schema-8 run or package claim was made for
this input-only continuation. The previous 1,644-test milestone remains a
historical result, not verification of this new merge. Agent-runtime ownership
was not changed. Exact next producer boundary: `GATE13_LIVE_CAPTURE_INPUTS.md`.

PR #194 continuation (3 October): native compact pruning/spacing/boundary
correction/stable ordering and explicit live FullTime payloads are implemented.
Ordinary calculated fixtures retain constructor-written script fields and
survive pending-matchday save/reload with identical packed scripts (schema 36).
Live statistics pack without fabricated memory/tail padding; finalized goal
fields and selected-player output are source-backed. Complete report assembly,
ordered GameState owner/link and successful reload/right-click/PMatchInfo
remain unfinished: missing native participant history/flag and helper/scalar
metadata must not be filled with defaults. Next: retain those outputs at the
calculator/completion producer, assemble only a complete report, persist owner
and fixture links together, then verify the genuine normal route. Gate 13 is
OPEN. Gate-14 files and agent-runtime ownership are untouched. No broad closure
or repeated intermediate Windows audit was performed for this continuation.
See `GATE13_LIVE_CAPTURE_INPUTS.md` for the current executable milestone.
Milestone suite: 1,644 tests / 23 expected skips, plus 179 focused checks and
80 final targeted assertions; asset policy passes. Current reconciled main is
`d0dadf1f`. Complete report/owner persistence and successful PMatchInfo opening
are explicitly not claimed by those passing tests.

Earlier local continuation (3 October, after PR #183 merged): live AI/human performance
finalization now retains ordered participant ratings/skill flags and persistent
player identities as transient report inputs. Actual calculator possession is
retained at completion and survives the already-saved pending matchday results
through internal schema 35. No partial input creates a report/link. Full live
compact-event and remaining helper/scalar output retention, complete report
owner/save integration and successful normal right-click remain the blocker.
See `GATE13_LIVE_CAPTURE_INPUTS.md`. Gate 13 remains OPEN; Gate-14 worker,
runtime ownership and full-original-functionality scope are unchanged.
Fresh native production tracing additionally proves that capture needs the
`0x62F7C0 -> 0x62FBF0` pruning/time/order finalizer and FullTime's explicit
`0x62AE00` outcome payload, not an encoding of the present semantic event list.
These inputs must be retained at production; no post-score reconstruction.
Final code `f8b9f4ba` passes 1,625 tests with 23 expected skips and 134 focused
checks; fresh Windows schema 8 passes with ordinary successful opening still
false. Continuation PR #194 reconciles main `d0dadf1f`; no runtime ownership
change or Gate-13 closure is claimed.

Local Gate-13 branch update (3 October): management base lookup at `0x5D3560`
is now recovered and integrated, including the month variant, exact source
club/country art fields and the application-owned competition header. All 97
selected assets pass provenance/hash/geometry checks; a new real Windows
schema-8 receipt passes with the base/header live. See
`GATE13_MANAGEMENT_BACKGROUND_RECOVERY.md`. Gate 13 remains OPEN.
Successive fixture tracing recovered the exact (378,235) grid origin and
the successful-capture report-list/link writer `0x60BF10`. A played fixture
cannot substitute for that captured report. Native capture eligibility, ordered
owner save/load/clear, eleven scalar copies and the WM_RBUTTONDOWN acceptance
chain are now recovered. The real host has the read-only right-press/cell/link
adapter; an uncaptured fixture remains a no-op, not a fabricated report.
See `GATE13_FIXTURE_REPORT_CAPTURE_TRACE.md`. Single next implementation
blocker: materialize/persist the complete completion-time report from native
participant/statistics/script and calculator/post-match state, then verify a
calculated fixture -> save/reload -> correct PMatchInfo context on Windows.
PR #183 continuation source-closes and tests the participant bit packing,
eight native skill flags, all sixteen script families/six tactical subcommands,
four additional scalar copies and exact two/four-group captured possession.
These snapshot codecs do not supply a complete report or assign a link.
Continue at the live calculator/completion boundary, not by retracing codecs:
retain the remaining native participant/goal metadata, complete compact-event list and
calculator/post-match scalars, then assemble/persist the complete owner.
The Premier League AI/human completion paths now retain actual gate receipts
as transient inputs; this alone does not create or persist a report/link.
Application Control blocked the preceding new package's smoke-test startup;
the final rebuilt package smoke remains deferred. See
`GATE13_CLOSURE_AUDIT.md`; no security bypass was attempted.
Normal-play/timing criteria must be assessed on that real route, not the
explicit popup seam. Parallel later-gate work and `agent-runtime` ownership
are unchanged.

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

- **Recovery 196 FastView possession assets / text geometry is canonical:** PR #162 squash-merged as `1e68dca68395c97cc8ea8498f1ec212e0273659b` after reconstruction run `37079435396`, Windows package run `37079435467`, and asset-policy run `37079435346` all passed. Four source-closed PossessionDiagram EA444 files are staged byte-identically; exact diagram rectangles and PossessionFigures percentage rectangles are guarded. User-side orientation and diagram cadence remain unclaimed.
- **Recovery 198 bar-ownership correction is canonical:** PR #164 squash-merged as `25ad2622aec612e8eddaf452e53ae7b717369a05`; reconstruction run `37081838582` passed **1,483 tests with 22 expected skips** and asset-policy run `37081838607` passed. The 82x16 team/blank bars are source-bound to `FastViewTeam/TeamTable`, not `PossessionFigures`.
- **Recovery 198 PossessionDiagram receiver lifecycle is canonical:** PR #165 squash-merged as `46d3cb57a1d7ad0fdd5141f911b00dabda35cc4e`; reconstruction run `37082560833` passed **1,487 tests with 22 expected skips** and asset-policy run `37082560879` passed.
- **Recovery 198 EventPossession cadence is canonical:** PR #166 squash-merged as `6277e385cff41216f6842bce4b49daea41e366e6`; reconstruction run `37083068477` passed **1,489 tests with 22 expected skips** and asset-policy run `37083068484` passed. MatchIterator emits one EventPossession opportunity every fifth EventGlobalTick while its exact source gates hold.
- **Recovery 199 GlobalTick timing is canonical:** PR #167 squash-merged as `78e305ca0e0fc7e5c22ed91649c2d9c5b163162f`; reconstruction run `37083625545` passed **1,492 tests with 22 expected skips** and asset-policy run `37083625478` passed. FastView uses GetTickCount thresholds 1000/500/250 ms, default index 1, Space cycling and one MatchController step per due host update with no catch-up loop.
- **Recovery 199 clock/art bridge is canonical:** PR #168 squash-merged as `49cb46ece578a6d93105febf49968aed6cf4b694`; reconstruction run `37085827416` passed **1,500 tests with 22 expected skips** and asset-policy run `37085827389` passed. ClockControl shares the EventGlobalTick numeric value, source lookup uses `tick // 5`, the semantic shell rejects non-five-minute possession segments, and the four staged PossessionDiagram assets now have an exact decoded-pixel seam without claiming a complete FastView frame.
- **Recovery 200 PossessionFigures typography is canonical:** PR #169 squash-merged as `c75ce5b07dc9d8c7467ed8dc4826854443ffd4a2`; reconstruction run `37086870371` passed **1,504 tests with 22 expected skips** and asset-policy run `37086870329` passed. The exact 18px Zurich font, white native color, left/top flags and bounded percentage text-art seam are source-closed.
- **Recovery 202/203 orientation/background boundary is canonical:** PR #170 squash-merged as `608e4f9168939c08ddffd90f5d6fb112b5d2724e`; reconstruction run `37088996337` passed **1,509 tests with 22 expected skips** and asset-policy run `37088996360` passed. Side 0 = home/right and side 1 = away/left for PossessionFigures; the loose 800x600 `FastView/background.444` path is explicitly unbound and must not be rendered.
- **Recovery 204 direct FastView chrome is canonical:** PR #172 squash-merged as `9b554eb6f9a5eae5c0b6f31205d9ed07aefaa658`; reconstruction run `37090449064` passed **1,514 tests with 22 expected skips** and asset-policy run `37090449112` passed. `top_bar.444` and `ticker.444` are direct FastViewPanel PictureControl children with exact source identities/rectangles. Their byte-identical binary import remains a deterministic transport follow-up and is not replaced by approximate art.
- **Recovery 205 FastView current-fixture score grids are canonical:** PR #175 squash-merged as `29a55fdeed4192010940f9f3806f87cfea2dc5f5`; reconstruction run `37092578763` passed **1,523 tests with 22 expected skips** and asset-policy run `37092578747` passed. `current_fix_grid_1.444` belongs to `FastViewLeagueScores`, while `current_fix_grid_2.444` belongs to `ScoreCompositeNormal`; their distinct source identities, grid-1 strips and typed receiver families are locked.
- **Recovery 205 ScoreCompositeNormal row geometry is canonical:** PR #176 squash-merged as `8ea49594b827542196a4b5e94137ea4cecc5d176`; reconstruction run `37093081527` passed **1,526 tests with 22 expected skips** and asset-policy run `37093081545` passed. Final score-composite page origins, grid-2 placement and four generic text rectangles are source-closed while their user-facing labels remain fail-closed.
- **Recovery 206 LeagueTableComposite current-table family is canonical:** PR #178 squash-merged as `642c004eb9e9b542a21e2a7c4401eb233c58b531`; reconstruction run `37094555752` passed **1,532 tests with 22 expected skips** and asset-policy run `37094555803` passed. Heading/row resource ownership, exact geometry, source-count transform and EventScore->refresh->EventLeagueTableUpdate lifecycle are source-closed while column labels remain fail-closed.
- **Recovery 207 ScoreComposite phase presentation is canonical:** PR #179 squash-merged as `9041cb9aff25e6982af6d9c80fccc0bac693f852`; reconstruction run `37095142860` passed **1,543 tests with 22 expected skips** and asset-policy run `37095142854` passed. Typed half/full/extra-time/penalties icons and shared phase icon/text geometry are source-closed; localized label strings remain fail-closed.
- **Recovery 208 FastViewTeam/TeamTable rows are canonical:** PR #180 squash-merged as `745c1576c337c94dcea86f996bf347af641c77c2`; reconstruction run `37095885928` passed **1,549 tests with 22 expected skips** and asset-policy run `37095885981` passed. Side-specific name grids/bars, exact row/text geometry, 17-pixel step and the row-11 primary-to-alternate grid transition are source-closed.
- **Recovery 209 PlayerRow energy bars are canonical:** PR #182 squash-merged as `66c0886a49581ac3461e0c242fb5e333bf73ac8c`; reconstruction run `37096841596` passed **1,553 tests with 22 expected skips** and asset-policy run `37096841613` passed. PlayerRow energy uses exact 58/99 anchors and the mirrored 82-pixel team/blank bar treatment.
- **Recovery 209 PlayerRow typed text events are canonical:** PR #184 squash-merged as `88e8b3554ece25ca609e38a41f159b5473900065`; reconstruction run `37097264888` passed **1,557 tests with 22 expected skips** and asset-policy run `37097264890` passed. Text cell 6 is EventPlayerUpdateForm `%u`, cell 4 is the EventPlayerGoal counter `(%u)`, and cell 5 is the EventPlayerOwnGoal counter `(%u)`. Own-goal color-channel semantics remain fail-closed.
- **Recovery 210 PlayerRow position is canonical:** PR #185 squash-merged as `25aac6bdce57e1ae06f395da6f058209cd746794`; reconstruction run `37099424476` passed **1,559 tests with 22 expected skips** and asset-policy run `37099424477` passed. Cell 2 is the localized Position* field via `0x635EC0` / table `0x849930`.
- **Recovery 210 PlayerRow name is canonical:** PR #186 squash-merged as `cdfc5b88c67d05b4eb58fc3c42f879e9fe95146e`; reconstruction run `37099943167` passed **1,560 tests with 22 expected skips** and asset-policy run `37099943164` passed. Cell 3 is the source player display name: surname-only for the `'-'` prefix sentinel, otherwise first-name initial plus surname.
- **Recovery 211 PlayerRow shirt number in progress:** builder caller `0x533370` invokes DBRPlayer accessor `0x41E3D0` at `0x5333EC`; that accessor returns the proven shirt/squad-number byte from runtime `+0x70` for matching team context or alternate `+0x76`, and `0x5333F3` stores AL into the 72-byte display record at exactly `+0x47`. Shared producer `0x525BD0` later formats that byte as `%u` in cell 1. This is a derived presentation field, not a direct DBRPlayer offset alias.
- **Recovery 211 complete PlayerRow snapshot staged on child branch:** `gate14_fastview_playerrow_snapshot.py` composes the already source-closed shirt number, position key, display name, form, energy bar and optional event-written goal/own-goal counters. `HumanMatchPresentation` and the semantic FastView shell preserve explicitly retained snapshot objects only; they do not derive or rerun match state. Goal controls remain absent until a caller supplies evidence that the typed callback has written the counter.
- **Recovery 211-216 PlayerProxy live-history/RNG path is source-backed through the Premier League finalizer:** canonical main `50b70390197ecace3297231eef5d227820a22478` already retains exact source-timed raw Condition prefixes and completed 24-sample FastView form histories through internal-save schema 35. PR #196 verified one persistent MatchEngine ran1 stream (`0x981BF0`) across weather, AI Condition, MatchCalculator, low-rating target lift and form trajectory, with the complete shuffle state saved separately from the shared MSVC CRT. Reconstruction run `37111511192` passed **1,620 tests with 23 expected skips** and asset-policy run `37111511208` passed. The combined Gate-13/Gate-14 integration advances the strict internal format to schema 38. FastView energy still requires later presentation RNG(6) consumption from retained post-finalizer state. Human-vs-AI `MatchCalculator+0xD48` remains fail-closed on unresolved legacy `DBRClub+0x130`.
- **Recovery 182 bounded Squad view transition is canonical:** PR #126
  squash-merged as `9b31feb05f4c6e239eb4c96288375217165a484e`.
  `OriginalManagementPresenter` now carries the exact source-proven
  PSquadScreen control 3/4/5 container state: control 3 first+reserve, control
  4 first+formation with pitch team index 0, and control 5 reserve+formation
  with pitch team index 1. The clean host exposes this only through an explicit
  source-accepted seam. Ordinary modern pointer equivalence is still false.
- **Fail-closed post-transition pixels:** only control 3's fresh selected/normal
  top-button state was previously source-closed. After source-accepted controls
  4/5, the host withholds unproven top-button/formation/player pixels instead
  of reusing or inventing them. The schema-8 audit exercises control 4 through
  the explicit seam, verifies the exact container transition, then restores
  control 3 before continuing the representative loop.
- **Current verification:** PR #126 Gate-13 run `37015082865` passed
  **485 tests with 21 expected skips**; full reconstruction run
  `37015083315` passed **1,387 tests with 22 expected skips**; repository
  asset-policy run `37015082578` passed.
- **Gate 13 validation boundary:** actual Windows 11/Tk schema **8** passed,
  including a fresh post-fix run with source-proven TeamSelect action captions
  and corrected space rendering. Private receipt hashes and source corrections
  are in `GATE13_WINDOWS_PLAYTEST_CORRECTIONS.md`. The existing explicit
  Squad/Fixtures/PMatchInfo/Tables bitmap loop passed; this does not close the
  ordinary navigation or broader graphical-fidelity boundaries below.
- **Remaining fail-closed boundaries:** ordinary Squad top-control pointer
  equivalence remains unproven; real captured-report production/persistence is
  missing despite the now source-closed native right-press/cell/link adapter;
  unproven owner-local popup children remain withheld. #177's management
  background is integrated, not an active retrace task. Keyboard equivalence
  remains unclaimed and is not itself a closure prerequisite.
- **Exact next Gate-13 task:** materialize and persist the complete native
  completion-time report. PR #183 now closes `0x60BCB0` participant packing,
  `0x630C4F/0x630DE0` skill flags, `0x633610` script extraction and the
  `0x631270/0x631290` possession aggregation codecs. Retain their complete
  remaining source-backed inputs at live calculation/completion, including
  the complete compact records / native list finalizer, FullTime outcome and
  remaining participant/goal/helper metadata. Rating/skill outputs plus player
  IDs and gate-receipt output are already retained; do not retrace them.
  Do not default missing fields
  or reconstruct report ownership from scores. Then verify real
  calculation/save/reload/right-press context and
  assess normal-play/timing against the roadmap. The parallel cloud worker
  continues its existing Gate-14 task independently; runtime ownership is
  unchanged. Gate 13 is not complete merely because schema 8 passed.

- **Recovery 186 Gate-15 injury gap closed:** `DBRClub::0x405080`
  availability is now shared exactly by persistent-injury and transfer
  consumers; PR #138 merged as `1a274e5f...` after 1,413 tests / 22 expected
  skips.
- **Recovery 186 Gate-15 legacy chairman-budget disposition:** persisted
  executable evidence proves the A0/A1/settings/warning budget-message family
  irrelevant to the ordinary shipped fresh-game path. Ordinary Finance
  Overview/transfers use Balance/accounting, so the port keeps no invented live
  budget scalar. Legacy persistence compatibility remains bounded.
- **Recovery 186 Gate-15 transfer-window lifecycle is canonical:** PR #140
  squash-merged as `833f1fedd7ce3c645c428ba20a09392d6bf994b3` after
  **1,417 tests / 22 expected skips** plus asset-policy success. Canonical
  `Static.dat +28..+35` supplies four transfer boundary pairs; England closes
  autonomous acquisition on 30 March 2001 and reopens it on 31 May 2001.
- **Recovery 186 contract month normalization is canonical:** PR #141
  squash-merged as `6a31e62e92c6c74fe097940dbd5b9bdea92b6b75` after
  **1,416 tests / 22 expected skips** plus asset-policy success. Shared
  `0x64CDD0` resets day to 1 before advancing the requested calendar-month
  span.
- **Recovery 186 contract category/FanFactor correction is canonical:** PR #142
  squash-merged as `948aa5193ab9a1003a7a640e93eca91b1dfee126` after
  **1,418 tests / 22 expected skips** plus asset-policy success. Autonomous
  contract duration now uses the exact country League/DummyLeague root index;
  Premier League attendance uses exact **FanFactor1 = 0.9**, and Cup attendance
  derives FanFactor from the host club's league rather than the Cup root.
- **Recovery 186/187 permanent-arrival lifecycle is canonical:** PR #143
  merged as `3b9fc3741a8d614a14389d90db99285b9aa49a69` after
  **1,420 tests / 22 expected skips** plus asset-policy success. DBRClub
  `+0x1ED` is the monthly permanent-arrival byte shared by human/autonomous
  transfers; day-1 reset runs after same-date Saturday transfer/payroll work.
- **Recovery 187 due-transfer ordering blocker:** persisted evidence proves
  `0x613EE0` is first inside `0x4A8070`, but the repository does not retain
  the missing outer relation between that dated-process queue and same-day match
  execution. The current worker cannot start a shell process
  (`caas.internal.errors.ClientError`), so fresh disassembly is unavailable.
  The reconstruction therefore keeps due transfers after fixtures as an
  explicit approximation rather than promoting it to original behavior.
- **Recovery 187 Gate-15 Cup accounting work-ahead is canonical:** PR #146
  merged as `57e59f6374f8c278cabbe054b8767638a69e5a26` after
  **1,424 tests / 22 expected skips** plus asset-policy success. The exact
  controlled-participant category-1/category-2 posting helper and neutral
  `0x5DBCD0` paired-XI numeric primitive are materialized; the direct
  match-family caller/applicability remains fail-closed and no invented
  "revenue sharing" label is used.
- **Recovery 187 Gate-15 readiness audit is canonical:** PR #147 merged as
  `04b2a65d864939f219d5800bef03eb8144833b00`. It classifies remaining
  fidelity items under Gate 15's fixed / proven-irrelevant /
  explicitly-documented rule without closing Gate 15 or bypassing Gates 13-14.
- **Recovery 188 Gate-17 prerequisite guard is canonical:** PR #149
  squash-merged as `ba6cabb692a1884be9e5bec8115d41f8bcad60c4` after
  **1,428 tests / 22 expected skips** plus asset-policy success. The final audit
  now requires every Gate 1-16 roadmap criterion and four distinct external
  Windows receipts before Gate 17 can pass.
- **Recovery 188/189 Gate-17 artifact binding and packaging are canonical:**
  gameplay receipt producers are bound to one release version, commit and
  archive SHA-256, and main `d571f86de06fbe09a7e5d74f848ffc36c05e2f59`
  has the reproducible Windows candidate package. Full reconstruction workflow
  `37063389249` passed **1,448 tests / 22 expected skips**; Gate-13 and
  asset-policy workflows passed; Windows package workflow `37063389258`
  froze and smoke-tested the PyInstaller executable and produced candidate
  archive SHA-256
  `79116b1aece63c68bfdf7b2fc541f1697f49bea79c87ccc2260144dd24139075`
  (13,626,308 bytes), artifact `11251855235`.
- **Recovery 190 clean-install producer is canonical:** PR #154 merged as
  `49c2c1099ba546c1ce6d9f809d91425c62bc5a43` after full reconstruction,
  asset-policy, and Windows package/freeze/smoke verification. The separate
  `clean_windows_install.json` producer extracts the exact release archive
  into a fresh directory outside Git, validates every installed payload file
  against `PACKAGE-MANIFEST.json`, runs the frozen executable's
  `--package-smoke` from the installed location, and never overwrites prior
  receipt evidence.
- **Recovery 190 release-evidence assembler is canonical:** stale-base PR #155
  was closed without merge; rebased PR #157 squash-merged as
  `8ec4dec9f32a98362f29fccaecec6176e1fef5a8` after full reconstruction and
  asset-policy success. It deterministically hashes/prevalidates the exact
  archive and four distinct external receipt files before constructing the
  final Gate-17 evidence contract.
- **Recovery 191 shared external-workstation guard is canonical:** PR #158
  squash-merged as `9fe93ea5c87e87b6e2db866205f8289e0bac83c6` after
  **1,464 tests / 22 expected skips**, Windows package/freeze/smoke success,
  and asset-policy success. Final audit, gameplay receipts, and clean-install
  receipts now all require a Windows client workstation
  (`VER_NT_WORKSTATION/product_type == 1`) and explicitly reject GitHub
  Actions; a modern Windows build number alone is insufficient.
- **Recovery 192 receipt-host metadata validation is canonical:** PR #159
  squash-merged as `fe73236559e61939e972324f0c61e391f29a1a0f` after
  **1,465 tests / 22 expected skips**, Windows package/freeze/smoke success,
  and asset-policy success. The final evidence validator independently requires
  every external receipt to record `windows_11 = true`, build >= 22000, and
  workstation product type 1, preventing old/copied/hand-edited evidence from
  bypassing host provenance checks.
- **Recovery 194 Gate-17 transactional coordinator is canonical:** PR #160
  squash-merged as `6b33a5fab9651866021a1e28be4bc72877303dda`.
  Full reconstruction run `37070962823` passed **1,470 tests with 22
  expected skips**; Windows package run `37070962855` passed package tests,
  PyInstaller freeze, packaged executable smoke and candidate build; asset
  policy run `37070962826` passed. The coordinator remains work-ahead only:
  Gate 17 still requires the real external workstation run and Gates 13-16
  actually closed.
- **Recovery 194 private source revalidation:** the canonical 511,121,336-byte
  disc-image ZIP was rematerialized, the 631,627,248-byte MODE1/2352 image was
  decoded, and a fresh independent Joliet scan reproduced exactly **2,456
  files / 211 folders**. The root executable rehashed to canonical SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
  The older process-start blocker is not current.
- **Recovery 194 Gate-14 FastView source closure in progress:** the canonical
  executable embeds all seven bounded `PossessionFigures` /
  `PossessionDiagram` full paths. This resolves the real
  `pitch_normal.444` basename collision in favor of the explicit FastView
  path without directory guessing. The bounded `PossessionDiagram` constructor
  is now traced to exact pitch rectangle **(253,139)-(547,217)**, overlay x
  offsets **[0,98,169]**, initial middle state, and a source-exact one-call
  territory transition using the private MSVC-style presentation RNG. Update
  cadence and side-0/user orientation remain fail-closed. See
  `research/GATE14_FASTVIEW_POSSESSION_SOURCE_TRACE.md`.
- **Exact Gate-14 work-ahead after this checkpoint:** verify the exact-path and
  PossessionDiagram primitives through full CI, then deliberately stage only
  the four source-closed diagram assets and connect their proven geometry to a
  player-visible presentation surface without inventing timing/orientation.
  Continue the independent `PossessionFigures` bar/text placement trace.
- **Independent cloud-safe reconciliation:** Gate 16 already has two passing
  canonical three-cycle receipts and a readiness audit, so the stale Gate 17
  limitations text that still described canonical multi-season evidence as
  missing is being reconciled without changing any gate-completion claim.

- **Recovery 179 live PMenu pixels are canonical:** PR #114 squash-merged as
  `57e334208dbad69127d5a173caf23d511971066e`. The default clean MANAGEMENT
  host now composes the four checksum-gated original PMenu row atlases with the
  exact recovered title/child Zurich fonts, line origins, clipping, static
  background/arrow state and black/white label endpoints. It does not fill the
  unresolved surrounding management background. Gate-13 run `36998507566`
  passed **453 tests with 21 expected skips**, full reconstruction run
  `36998507518` passed **1,363 tests with 22 expected skips**, and asset
  policy `36998507581` passed.
- **Recovery 179 PMenu static row-state propagation closed:** the canonical
  row factory maps node bit 0 through vtable `+0x4C` and inverted node bit 1
  through `+0x58`. Enabled title backgrounds stay `0x8002`/white while their
  arrows carry expansion; child backgrounds are `0x0002`/black when
  unselected and `0x8002`/white when selected. Presenter rows now carry the
  exact arrow/background bits and native endpoint color. The next task remains
  composing the already imported row resources/fonts into the live canvas.
  Focused PMenu/canvas verification passes **32 tests**.
- **Recovery 177 exact PMenu row text geometry recovered:** private canonical
  executable tracing followed the concrete title/child constructors through
  `0x651E30 -> 0x6520C0 -> 0x657280/0x6570F0`. Title rows use exact
  `Zurich_XCn_BT_25pixel.fnt` at local line origin **(30,1)**; child rows use
  exact `Zurich_XCn_BT_16pixel.fnt` at **(30,17)**. Both clip to the
  half-open **(30,0)-(198,29)** background control. The two checksum-gated
  authorized fonts are now imported, and the presenter carries per-row font,
  line-origin and clip geometry. Focused PMenu/canvas verification passes
  **31 tests**. The next task is live row pixel composition, followed by the
  unresolved application-owned management background and broader management
  screen fidelity.
- **Recovery 177 real Windows schema-7 audit passed:** the private receipt
  (SHA-256 `6e1a43e01a43ccbf7bfe92c3088ee446c40a92d51add3ba9660f20cb76f0bef2`)
  records Windows 11 build 26200, Python 3.12.14 and Tk 8.6.12. The real Tk
  route passes TeamSelect and PMenu Calendar -> League Fixtures -> TABLES ->
  League Tables pointer presses with zero guessed management PhotoImages. The
  receipt remains outside Git and correctly records `gate13_complete: false`.
  The Windows pointer-audit blocker is closed. Recovery 177 subsequently
  closed exact PMenu label origin/clipping; live row composition, surrounding
  management pixels, keyboard equivalence and the recognizable management
  canvas remain open.
- **Recovery 176 PMenu pointer-press boundary integrated locally:** the
  canonical ZIP/executable hashes were reverified. Both concrete title/child
  SelectBmp vtables place `0x64F7A0` at input slot `+0x6C`; their exact control
  is the half-open 201x29 whole-row rectangle, both row `+0x0C` acceptance
  predicates resolve to constant-true `0x42DE00`, and accepted input reaches
  the already proven row `+0x10` actions. Tk `<Button-1>` is a press event, so
  ordinary contained PMenu presses now use the recovered action seam. The
  unknown child node bit 1 and keyboard equivalence remain fail-closed.
  Focused host/PMenu/presenter verification passes **31 tests**. A fresh
  schema-updated real-Windows receipt is still required.
- **Recovery 175 source-accepted PMenu seam merged:** PR #111 passed Gate-13
  presentation CI (`36986776362`), the full reconstruction suite
  (`36986776403`), and asset policy (`36986776562`), then squash-merged as
  `9e8f7a18368b8ce7076126a55b2e99563197659a`. The clean-room management
  presenter now preserves source-proven title expansion independently from the
  selected child panel and exposes an explicit post-source-acceptance PMenu
  action seam. Only currently visible recovered rows may dispatch; supported
  child actions route transactionally into Squad, League Fixtures and League
  Tables. Recovery 176 subsequently closed the concrete pointer-press boundary.
- **Superseded worker blocker:** the earlier ChatGPT process-start failure is
  historical. Recovery 179 has working container execution and successfully
  recovered/rehashed the authorized source. Do not treat the old ClientError
  note as a current blocker.
- **Recovery 175 schema-6 Windows audit contract merged:** PR #112
  squash-merged as `f6995c0e6b90c9e06a7d6309c7ffb2e49f26f376`.
  Gate-13 run `36987669876` passed **442 tests with 21 expected skips**
  and asset-policy run `36987669896` passed. The real-Windows harness now
  requires ordinary Tk PMenu clicks to remain candidate-only while
  separately exercising the explicit source-accepted callback seam through
  Calendar root -> League Fixtures -> TABLES root -> League Tables. It
  records that Tk-event equivalence is **not** claimed and still requires
  zero guessed management PhotoImages.
- **Real Windows validation boundary:** the schema-6 contract is
  repository-verified only. A fresh real Windows 11 schema-6 receipt is
  still pending; the Recovery-164 schema-3 receipt remains valid only for
  the earlier corrected first-screen path.
- **Exact next task:** compose the exact PMenu row resources and newly recovered
  native label geometry in the live management canvas, then close
  application-owned background ownership. Continue the smallest
  source-backed Squad -> League Fixtures/PMatchInfo -> League Tables visual
  loop without inventing pixels. Gate 13 remains active.

- **Recovery 175 source-accepted PMenu integration merged:** PR #111
  squash-merged as `9e8f7a18368b8ce7076126a55b2e99563197659a` after
  Gate-13 run `36986776362` passed **440 tests with 21 expected skips**,
  full reconstruction run `36986776403` passed **1,350 tests with 22
  expected skips**, and asset-policy run `36986776562` passed.
  `OriginalManagementPresenter` now keeps the currently expanded source root
  separate from the selected management panel, applies the recovered
  post-acceptance title/child callback contract only to a currently visible
  row, and transactionally routes supported child actions into Squad, League
  Fixtures and League Tables. `OriginalGameTkHost` exposes the same explicit
  source-accepted seam, but ordinary Tk pointer clicks remain candidate-only.
- **Recovery 175 private-trace blocker reverified:** a fresh trivial shell
  probe still fails before process start with `caas.internal.errors.ClientError`.
  The blocker is now narrower than the old row-action uncertainty: exact PMenu
  label origin/clipping, any still-missing application-owned management
  pixels, and the original control-acceptance -> modern Tk-event equivalence
  remain unavailable for fresh private tracing. This is not a user-action
  blocker.
- **Exact next task:** extend the real-Windows Gate-13 audit contract so it
  separately proves (a) ordinary Tk PMenu hits remain non-activating and
  (b) the explicit source-accepted seam can execute the already-proven
  post-acceptance root/child actions and supported panel transitions without
  inventing event equivalence. Then resume the private text-origin/control-
  acceptance trace as soon as process execution recovers; a fresh real
  Windows 11 receipt remains pending.

- **Recovery 173 private execution recovered:** the authorized
  **511,121,336-byte** source ZIP rehashed to canonical
  `677dcbc...a8a4`, and both extracted shipped executables rehashed to
  canonical `833bf95e...b7cc3`. The previous process-start infrastructure
  blocker is no longer active for static tracing.
- **Recovery 173 PMenu action ownership is source-closed:** concrete row action
  vtable slot `+0x10` resolves to title `0x47AC60` and child
  `0x47AD60`; the generic accepted-control path calls the parent-row action
  at `0x64FF21`. Title action mutates the exact root open bit. Child action
  reads node `+0x0C` and calls management panel factory
  `0x47AEC0(menu_id, 0)`, gated by neutral node-state bits 0/1.
  `original_pmenu_activation.py` preserves this contract without equating a
  modern Tk click to the original accepted event.
- **Gate-14 startup-media work-ahead verified and merged:** PR #109 passed
  Gate-13 presentation CI, the full reconstruction suite, and asset policy,
  then squash-merged as
  `94d9702c0e4fce3fd215ec4741755cf8630751b3`. The clean host can now run
  an explicitly configured verified startup derivative sequence before Tk.
- **Gate 13 remains active:** exact PMenu label origin/clipping and any
  application-owned surrounding management pixels remain unresolved; the
  source control-acceptance boundary is not yet mapped far enough to promote
  Tk rectangle containment into native event equivalence; the clean-host
  Squad -> Fixtures/PMatchInfo -> League Tables loop still needs live
  activation; and a real Windows 11 schema-5 receipt is pending.
- **Exact next task:** continue the now-unblocked private PMenu trace through
  label origin/clipping and accepted-control event semantics, then integrate
  only the proven row activation route into the clean host and update the
  Windows audit contract.


- **Recovery 172 default clean-host Windows audit merged:** PR #107 merged as
  `a79edc86e0333fb856539274e12113d85de868c8`. The real Windows/Tk harness is
  now schema **5** and exercises both the developer viewer and the default
  `OriginalGameTkHost` with a fresh session through New Game -> native club
  click -> TeamSelect Start -> MANAGEMENT. It requires the fixed **800x600**
  host, PMenu **(599,96,201,504)**, fresh PSquadScreen
  **(0,79,800,520)** / code **0xCE**, zero guessed management PhotoImages,
  and candidate PMenu hit feedback that dispatches no navigation. Gate-13 run
  `36975636316` passed **427 tests with 21 expected skips**; asset-policy
  run `36975636285` passed. A new real Windows 11 schema-5 receipt is still
  pending.
- **Recovery 172 normal-host PMenu hit integration merged:** PR #106 merged as
  `45844074b4ad7128903fd3ed7b9a840dc82dbc74`. The default clean host now
  reports the geometry-proven PMenu candidate row under a management click,
  while keeping PSquadScreen selected and dispatching no navigation.
- **Recovery 172 diagnostic PMenu hit integration merged:** PR #105 merged as
  `8b36c566ababdf52a8574d5c8753f92aad641fc4`. The developer viewer and the
  Windows audit exercise the same non-activating candidate-row boundary.
- **Recovery 172 closure audit refreshed:** `GATE13_CLOSURE_AUDIT.md` now
  reflects that the generic ttk notebook is no longer the normal launch path.
  Gate 13 remains active because the management canvas is intentionally blank,
  exact PMenu text/background pixels are unresolved, native row activation is
  unproven, and the Squad -> Fixtures/PMatchInfo -> League Tables loop is not
  yet live in the clean host.
- **Current infrastructure blocker:** a fresh trivial process probe still fails
  before start with `caas.internal.errors.ClientError`. Repository evidence
  contains no persisted native PMenu activation/event trace sufficient to
  promote candidate containment into navigation. Fresh private executable
  tracing remains required for PMenu label origin/clipping, any missing
  application-owned background layer, and row-event ownership.
- **Exact next task:** if private execution recovers, trace PMenu
  text-origin/clipping plus row activation/event ownership first. Otherwise
  continue only source-backed cloud-safe management composition/audit work that
  does not invent those semantics. Run the schema-5 audit on the real local
  Windows 11 path when available.


- **Recovery 172 Windows-management audit harness merged:** PR #104 merged as
  `c0b2fd2465952d2f5134837054622c2706abda71`. The real Windows/Tk Gate-13
  audit now preserves all prior first-screen checks, then re-enters New Game,
  clicks a source-backed native club row, drives TeamSelect Start through the
  real Tk binding, and requires the recovered **MANAGEMENT/PMenu** host. The
  schema-4 contract verifies the exact **800x600** canvas, PMenu
  **(599,96,201,504)**, fresh PSquadScreen **(0,79,800,520)**, panel code
  **0xCE**, and PSquadScreen identity. It also requires **zero management
  PhotoImages** and keeps surrounding background, exact PMenu label placement,
  and native PMenu row activation explicitly unresolved. Gate-13 run
  `36974932379` passed **427 tests with 21 expected skips and zero failures**;
  asset-policy run `36974932407` passed.
- **Validation boundary:** the upgraded schema-4 harness is repository-verified,
  but its new positive MANAGEMENT path still needs one actual local Windows 11
  execution before that graphical result can be claimed. Hosted Linux CI is not
  a substitute for the real Windows/Tk receipt.
- **Exact next task:** continue the highest-priority independent Gate-13
  presentation slice that does not require unresolved PMenu activation or
  private native pixels. Re-run the schema-4 Windows audit on the local
  Windows path when that execution path is available, then fold the result into
  the Gate-13 closure audit.


- **Recovery 171 PMenu candidate hit-testing merged:** PR #102 merged as
  `25fdf0e8d9cbcf9cea580ca625e548b21612604c`. The presenter can now identify
  the visible PMenu row under a screen-space point using only the exact
  **(599,96)** list origin, **201x504** bounds, **29px** row step and current
  recovered visible ordering. The API deliberately returns a **candidate row**
  only; it does not activate, expand, select or navigate because native PMenu
  event ownership is still unproven in persisted evidence. Gate-13 run
  `36973075568` passed **425 tests with 21 expected skips** on exact head
  `b33b3fc2f32d25dbdb7b55b1c4e283c0d9d69605`; asset-policy run
  `36973075522` passed.
- **Exact next task:** extend the integrated real-Windows/Tk Gate-13 audit so a
  native club selection followed by TeamSelect Start must enter the fixed
  MANAGEMENT/PMenu host with the exact recovered PMenu/Squad parent geometry.
  Keep the audit fail-closed on still-unrendered management background/text and
  do not convert candidate PMenu row containment into activation.


- **Recovery 171 source-backed app host merged:** PR #101 merged as
  `62a1bbcd24bf1dc26e57294e40fef176a4f87036`. Normal `app.py` launch now
  opens the clean fixed **800x600** source-backed FM2001 host, loads
  checksum-gated PStartMenu/TeamSelect resources from
  `original_assets/source` plus the canonical installed `FOOTBAL.EXE`, and
  routes the recovered first-screen flow into the MANAGEMENT/PMenu host. The
  former generic ttk notebook remains available only through explicit
  `--prototype-ui`. Gate-13 run `36972538322` passed **419 tests with 21
  expected skips**; full reconstruction run `36972538328` passed **1,321
  tests with 22 expected skips**; asset-policy run `36972538362` passed.
  After TeamSelect Start the host deliberately clears prior first-screen pixels
  instead of drawing an invented management skin while the management
  background and exact PMenu label placement remain unresolved.
- **Recovery 171 PMenu input boundary:** PR #102 is the current cloud-safe
  checkpoint. It adds only source-bounded screen-coordinate **candidate row**
  hit-testing from the proven PMenu origin/201px width/29px row geometry and
  visible order. It does not activate, expand, select or navigate a row because
  the native row-event ownership is not yet persisted.
- **Exact next task:** verify/merge PR #102, then continue the next independent
  Gate-13 presentation slice. Private executable tracing remains required
  before promoting PMenu pointer containment into native activation semantics or
  claiming exact PMenu text/background pixels.


- **Recovery 171 fixed PMenu management host merged:** PR #100 merged as
  `163071883b932067a5cf33cf12ff3d05a2940cb5`. Successful TeamSelect Start
  now transitions from `TEAM_SELECT` into an explicit source-proven
  `MANAGEMENT` / PMenu state instead of remaining on the first-screen enum.
  The fixed host binds `OriginalManagementPresenter` to the exact **800x600**
  surface, preserves the PMenu rectangle **(599,96,201,504)** over the fresh
  PSquadScreen parent **(0,79,800,520)**, and deliberately reports the
  surrounding management background and exact PMenu label origin/clipping as
  unresolved rather than drawing a substitute skin. The Tk first-screen viewer
  enters this host after Start. Gate-13 run `36971906350` passed **415 tests
  with 21 expected source-gated skips and zero failures** on exact PR head
  `4551e0a5e178a850a8cdf6930beff75cc84bbbc8`; asset-policy run
  `36971906383` passed.
- **Recovery 171 process-sandbox blocker persists:** a fresh trivial
  `container.exec` probe still fails before process start with
  `caas.internal.errors.ClientError`. Private executable tracing for PMenu
  label origin/clipping and any additional application-owned management
  background layer remains deferred infrastructure work, not a user-action
  blocker.
- **Exact next task:** replace the remaining generic ttk ordinary-management
  launch path with the recovered first-screen -> MANAGEMENT host wherever the
  application entrypoint still exposes the prototype Play tab, then integrate
  source-backed PMenu row input/navigation for already-supported Squad,
  League Fixtures and League Tables without inventing unresolved row-event
  semantics.


- **Recovery 170 ordinary-management routing verified on PR #98:** the
  source-bounded management presenter now switches the recovered PMenu between
  fresh **PSquadScreen (0xCE)**, **PLeagueFixtures (0x25C)** and
  **PLeagueTables (0x25A)** without importing simulation code or falling back
  to the generic ttk Play tab. Fixture rows remain in the bridge's recovered
  source order; League Tables reuses its fail-closed original presenter; and
  the PLeagueFixtures -> **PMatchInfo** transition exposes only the already
  recovered two-gate action boundary. Navigation is transactional, so an
  unintegrated PMenu child leaves the previous source-backed panel selected.
  Gate-13 CI run `36968140361` passed **403 tests with 21 expected
  source-gated skips and zero failures** on head
  `30cfc7fdc999d5bc0e005a5a5bc0bc78525aaecd`; asset-policy run
  `36968140362` passed.
- **Recovery 170 private execution blocker:** the authorized
  **511,121,336-byte** Library source ZIP was successfully rematerialized, but
  both the shell/container path and independent Python execution path failed
  before process start with `caas.internal.errors.ClientError`. No new
  original-byte behavior is inferred from that failure. The exact PMenu label
  origin/clipping and application-owned management background trace therefore
  remain deferred infrastructure blockers, not user-action blockers.
- **Exact next task:** merge the verified routing checkpoint, then continue the
  highest-priority cloud-safe Gate-13 integration around the fixed 800x600
  management surface and League Fixtures data/presentation seam while keeping
  the unresolved PMenu text/background pixels fail-closed. Revisit the private
  executable trace as soon as a process sandbox is available.

- **Recovery 166 PMenu/Squad parent placement:** private checksum-gated native
  tracing now closes the application-owned PMenu rectangle at
  **(599,96,201,504)** and the fresh PSquadScreen factory rectangle at
  **(0,79,800,520)**. The right-side overlap is original behavior and the
  clean-room constants/tests now preserve it. The trace still proves no
  PMenu-specific shell background; exact menu label origin/clipping remains
  open, so the finished canvas is not claimed.
- **Recovery 166 TeamSelect -> PMenu/Squad composition seam:** after a valid
  single-user Start, `original_management_presenter.py` now joins the live
  read-only club/roster bridge to the exact fresh Team -> Squad PMenu snapshot
  and the native 20-row Squad viewport. It preserves source roster order,
  reports overflow without inventing scrolling, and has no direct simulation
  imports. The first-screen presenter exposes the seam lazily. Fifteen focused
  integration/front-end/PMenu/Squad tests pass.
- **Exact next task:** render that composed snapshot in the fixed 800x600
  Windows surface with source-backed assets/geometry, then replace the generic
  Play-tab handoff for the fresh management route.
- **Recovery 166 PMenu visible-row closure:** checksum-gated native tracing
  closes the 201x504 / 16-row / 29-pixel list, root-first bit-0 expansion,
  title-versus-child factory split, and fresh Team (`2`) -> Squad (`0xCE`)
  selection. `original_pmenu_presenter.py` now supplies the exact 15 visible
  rows with source-bound resources/font and fails closed outside recovered
  topology; 23 focused tests pass. Raw reports remain outside Git. Exact text
  origin/clipping beyond the recovered row controls remains open.
- **Recovery 166 fresh Gate-13 closure audit:** Gate 13 remains active. The
  source-backed first screens, PMenu contracts and management presenters do not
  yet form one integrated ordinary-management path; the live application still
  hands normal play to the generic ttk prototype. The minimum required closure
  slice is TeamSelect Start -> PMenu -> PSquadScreen, followed by core
  Squad/tactics -> Fixtures/PMatchInfo -> League Tables navigation and a real
  Windows audit. Exact Current Form ordering and secondary-panel pixel fidelity
  are valid Gate-15 deferrals. Evidence:
  `research/GATE13_CLOSURE_AUDIT.md`.
- **Recovery 164 local blockers cleared:** the corrected real Windows audit
  passed on Windows 11 with Python 3.13.15 / Tk 8.6.15. The private schema-3
  receipt remains outside Git. The authorized ZIP rehashed to canonical
  `677dcbc...a8a4`; four PMenu assets, `info_popup.444`, and all 15 League
  Tables assets were exact-path extracted and provenance-imported. Seventy-five
  focused resource tests and the repository asset-policy check pass.
- **Recovery 164 League Tables private trace closed:** the seven controls at
  `+0x7FC..+0x97C` are exact `eCText` P/W/D/L/F/A/Pts headers (TD `0x8198F8`,
  vtable `0x7BE340`). League Position activates all seven through vtable
  `+0x30`; Current Form deactivates them through `+0x34`. The exact bit-state
  transform is integrated and guarded. Current Form row ordering at `0x4F4A10`
  remains deliberately fail-closed.
- **Exact Gate-13 next boundary:** perform the fresh Gate-13 closure audit.
  Classify remaining ordinary-management gaps against the actual ROADMAP
  criteria before starting any broad new reverse engineering.
- **Recovery 160 PMatchInfo presenter merged:** PR #93 merged as `5f76cd8d1187601034424fd6519c29c521b912bc`; Gate-13 run `36943619177` passed **364 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36943619314` passed. The simulation-independent PMatchInfo presenter is canonical, preserving exact staged art geometry/clipping/tabs/text slots and refusing a complete dialog while exact `info_popup.444` remains unavailable through safe binary transport.
- **Recovery 161 League Tables shell merged:** PR #94 merged as `3c19c4fff22cc397fe3728e8f6e21fc7896075e0`. All **15** selector events are source-bound: country events 1..8, dynamic DIVISION events 9..13, and Sort By events 14/15 = League Position / Current Form. Country/DIVISION/Sort By and exact P/W/D/L/F/A/Pts header text/geometry are canonical.
- **Recovery 162 League Tables body/resources merged:** PR #95 merged as `7578e465fbc952a74ee1268b698dde7d26ee2a8b`; Gate-13 run `36949336841` passed **379 tests with 21 expected source-gated skips and zero failures**, and asset-policy run `36949336761` passed. `CLeagueTableList` (TD `0x81B478`, vtable `0x7C011C`) at panel `+0x9BC` has exact local rect **(270,184,477,384)**, native 24-row capacity and 16px row step. Each `PLeagueTableRow` (TD `0x81B378`, vtable `0x7BFEC0`, 0x4A8 bytes) source-binds rank/name plus P/W/D/L/F/A/Pts rectangles; fields come from source offsets `+0x10/+0x14/+0x18/+0x1C/+0x20/+0x24`, with **Pts = 3*W + D**. The complete 15-file `league_tables/*.444` family is source-owned and raw-disc hash/geometry verified.

- **Recovery 164 League Tables presenter merged:** PR #96 merged as `95b566a50d749d17bcf0324b46582c9bc215b65b`; Gate-13 run `36953094233` passed **388 tests with 21 expected source-gated skips and zero failures**, full reconstruction run `36953094137` passed **1,285 tests with 22 expected source-gated skips and zero failures**, and asset-policy run `36953094185` passed. The simulation-independent presenter is now canonical: it preserves the exact 24-row/16px League Tables body contract and P/W/D/L/F/A/Pts projection, removes the unsupported development-only GD substitution, validates `Pts = 3*W + D`, and fails closed on Current Form ordering and unstaged exact art.
- **Recovery 164 presenter reconciliation:** the cloud-safe League Tables presenter and local exact-art/Windows work are both canonical. The former private blockers for downstream headers, 15-file art staging, `info_popup.444`, PMenu popup staging and corrected first-screen validation are closed. Current Form ordering (`0x4F4A10`) remains open and fail-closed.


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


## Recovery 270: AudioHooks numeric routing now reaches canonical decoded menu PCM

- Canonical main reached `48f1f6dc8cb0074d5f0b149ad966b3288d4ed4e8` after verified PRs #334 and #335. Gate 13 is still the earliest incomplete validation gate and remains Codex-owned; this is bounded Gate-14 work-ahead only.
- `AudioHooks::0x5DBFC0` is source-closed as a numeric event/state dispatcher to literal `menus.bnk` sample slots. The canonical FM2001 BNKl v2 parser/decoder is already source-closed for all four core banks, and `audio_sample_decode_ready` remains true.
- New private trace tooling can enumerate decoded direct callers of `0x5DBFC0` and nearby PUSH operands, but caller reachability, calling convention, exact event/state argument positions, and semantic event names remain intentionally unproven until a private canonical-executable run is manually adjudicated.
- The new numeric menu-PCM bridge requires the exact canonical `menus.bnk` SHA/size, preserves no-sound routes, and decodes routed slots to exact mono 22,050 Hz PCM. It does not promote sample names, event meanings, reconstructed UI-event equivalence, Windows device output, or Gate-14 login/menu audio completion.
- Verification: PR #334 ran 2,096 tests with 23 expected skips plus asset-policy success; PR #335 ran 2,101 tests with 23 expected skips plus asset-policy success.

### Exact next Gate-14 work-ahead tasks

1. **Private/source task:** run `reconstruction/gate14_audiohooks_event_source_trace.py` against canonical executable SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`. Manually adjudicate real callers, function/CFG boundaries, calling convention, argument positions, and native sender data-flow before setting any semantic event binding true.
2. **Cloud-safe task while private execution is unavailable:** add a narrow synchronous menu-PCM playback backend seam modeled on the existing verified startup-media backend. It may consume only a verified non-silent `DecodedMenuPcmDispatch`; silent routes must not invoke the backend. Backend success can prove delivery to the platform adapter, but **must not** set audible Windows verification or semantic event/sample flags true.
3. Add a Windows-specific adapter only behind that seam. Python's Windows `winsound.PlaySound` supports an in-memory WAV image synchronously; synthesize only a standard PCM WAV wrapper around the already decoded source samples. Keep actual Windows audible/device verification as a separate deferred receipt before `login_menu_audio_integrated` can become true.
4. After the private caller trace proves native event semantics, bind only those source-proven original UI senders to numeric dispatch. Do not guess modern UI-event equivalence from the sound itself.


## Recovery 270: synchronous menu PCM backend boundary is canonical

- PR #336 is canonical at `4b3f9e0b5d62c699402b580b7dcf4aaf9416a8a4` after reconstruction run `37200017817` passed 2,106 tests / 23 expected skips and asset-policy run `37200017826` passed.
- Verified numeric no-sound routes now bypass platform playback entirely. Verified non-silent decoded menu PCM can be delivered to a caller-supplied synchronous backend, but adapter completion is **not** audible Windows proof and does not change `audio_event_binding_recovered` or `login_menu_audio_integrated`.
- Exact cloud-safe next task: add a Windows-specific in-memory WAV backend with injected playback callable/flag for tests. It must verify the decoded PCM identity before wrapping samples in standard PCM WAV and must return success only when the platform player call returns normally. Keep actual Windows audible verification and semantic sender mapping separate.


## Recovery 271: Windows menu PCM adapter is canonical; real audible receipt remains open

- Canonical main includes PR #337 at `418375e94a90595c121bf4b3ba7dc4071c849f9b`. Reconstruction run `37200338931` passed 2,112 tests / 23 expected skips; asset-policy run `37200338933` passed.
- The full source-backed numeric route now exists as: exact canonical `menus.bnk` -> original numeric AudioHooks event/state switch -> literal slot -> BNKl v2 decoder -> verified PCM identity -> synchronous backend seam -> Windows in-memory WAV adapter.
- This still does **not** prove audible Windows output, semantic event names, human-readable sample names, reconstructed UI-event equivalence, or Gate-14 login/menu audio integration.
- Private caller/source work is currently blocked by execution infrastructure: the authorized 511,121,336-byte Library ZIP resolves/materializes successfully, but both trivial shell and Python execution return `caas.internal.errors.ClientError`. Do not infer caller semantics while this persists.
- Exact cloud-safe next task: create a real-Windows audit harness and fail-closed receipt schema for an explicit numeric event/state pair. It must verify canonical bank identity, run the real Windows adapter, capture OS/Python and routed slot/PCM identity, and require explicit human confirmation of audibility before setting an `audible_windows_verified` receipt field. Semantic event binding must remain separately false.
