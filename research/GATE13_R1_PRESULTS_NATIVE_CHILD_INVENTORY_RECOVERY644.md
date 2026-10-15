# Recovery644: original PResults complete initial five-child inventory, static source

15 October 2026 KST. Starting canonical main after reviewed/merged PR753: `d3db81d86029873ac63ab525f1050cdf64b072c6`. Active WIP branch `worker/gate13-r1-original-normal-player-644`, intentionally **no PR/remote CI yet** because complete normal player-visible match route remains unresolved. Active Gate13 reopened; Gates14–17 and actual Windows11 user GUI/release acceptance **OPEN**.

## Original authority, not synthetic imitation

Private user-authorized **shipped** `footballmanager.exe` 4,714,541 bytes, SHA256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, read-only `objdump -D -M intel --start-address=0x4a6e45 --stop-address=0x4a6fbe`. The original executable was **not run**. The original `FM2001_Art/Generic/Waiting/waiting_back_2.444` was independently retrieved as **46,448 bytes SHA256 `289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5`** from the private extracted original Drive tree, specifically exact non-shared file ID `1MlTY24WId0hnynvkAk5chJLFhG3Acy8t`. Original graphic is not uploaded into GitHub by this branch. Original user-provided extracted disc source, not the Windows reconstruction RC, supplied the bytes.

### Native child factory and positions

The PResults initialization at original `0x4A6E50` checks already-initialized +0x5C and only constructs once. `4A6E61 PUSH 0x14` allocates five 4-byte child-array slots. `4A6E74` writes native child count 5 at owner+0x38. The initial registered children are, in their actual native index order:

| index | embedded PResults offset | source (x,y) | source (w,h) | initial control ID | constructor |
|---|---|---|---|---|---|
| 0 | +0x16C | (0,513) | (800,87) | **0** | 0x651BA0 / wrapper 0x946630 original waiting_back_2.444 |
| 1 | +0x1A0 | (0,518) | (800,38) | **0** | 0x6503F0 |
| 2 | +0x1E0 | (0,556) | (800,18) | **0** | 0x6503F0 |
| 3 | +0x220 | (0,579) | derived from original global 0x946604/0x946608, **not a fixed known size** | **0** | 0x64F380 |
| 4 | +0x270 | (0,581) | copied from original embedded progress-owner +0x250 bounds, **not a fixed known size** | **0** | 0x64F380 |

Child0 bitmap source/position original `4A6E98..4A6EA6`. Children1/2 exact (y=0x206/0x22C,w=0x320,h=0x26/0x12) at `4A6EC0..4A6EDD` and `4A6EF7..4A6F17`. Child3 origin y=0x243 and initial dynamic bounds through 0x64F380 at `4A6F31..4A6F53`. Native **+0x250** control is constructed at `4A6F63..4A6F76`, but **is not an additional index 5 in the five-pointer initial child array**; child4 gets its width/height from +0x250 at `4A6F90–4A6FA9` with y=0x245. Native 0x4A7190 later adjusts actual progress width from event counters, not match-result cardinality.

All five initial child IDs are zero because `4A6E54 XOR EBP,EBP`, the five parent registration sites each push EBP as ID, and bitmap control +0x6C 0x64F7A0 does **not** emit a parent return event with ID zero. Do not bind a modern click on the 800×87 bottom waiting strip to PMenu. See existing `research/GATE13_PRESULTS_ORIGINAL_BACKGROUND_RETURN_NEGATIVE_AUDIT_RECOVERY443.md`.

New source inventory `reconstruction/original_presults_child_inventory.py` is strict about the unknown dynamic sizes and source-reused original Waiting art identity, declares static display facts with no player return/control behavior; three local tests **PASS** against the actual private original PE and actual private graphics, including **17 original native opcode signatures**, changed-byte/size asset counterexamples, and five child/callback geometry/scope checks. Tests registered on focused Gate13 workflow in WIP branch, no GitHub Actions dispatched before a meaningful integration boundary.

### Whole original user journey remains missing

This source receipt is not a renderer, no original PResults progress event queue is executed, and no original-game GUI or release validation is claimed. Main code `original_game_host.py` currently keeps a Tk spinner/retained PPreMatch frame during calculated Quick3; `human_gameplay.play_original_user_primary_match` has a Quick-only calculation while source-different modes0/1/2 raise without mutating the pending match. Original expected PResults 0x431F70->4A83F0 actual dated work + original 0x4A71F0 event ticks, and original normal return 0x432505+, are **not** modeled by this control inventory.

**Next player-visible integration work**:
1. Prove native PResults +0x250/+0x270 actual dynamic extents and underlying original colors/Font/Resource sources, plus original 0x4A83F0 initialization/0x4A7190 progress update, and render source-qualified PResults child layers in the **ordinary** Tk host (not a separate inspector). Event-driven progress can only come from actual qualified original dated-event callbacks, not synthetic time or match count.
2. Continue normal original `513010→513252→5DA2F0→v38/v3c` first/second side score/event state and original modes 0,1,2,3 with presentation wrapper branch semantics; implement atomic saved live GameState lifecycle, preserve unknown/rejected branches. PResults should release management based on original 0x432505+ route, not guessed click events.
3. Verify physical normal Windows 11 GUI against original behaviors and all shipped countries/leagues and human managers before Gate13 closure and subsequent Gate14–17 audits.

This WIP does not merge PR739 or rewrite canonical main CURRENT_STATE until coherent integration.


## Recovery644 continuation: original progress backing/fill SOURCE-RESOLVED, not unknown geometry

The earlier table's child3 and child4 `None` unknown width/height
are **superseded** by independently traced original initialization.

The original executable string pointers at `0x835980` and
`0x8359AC`, verified directly as the shipped NUL-terminated
paths, are:

- `FM2001_Art/Generic/Waiting/loading_back.444`:
  authenticated directly from the **private extracted disc source**
  Google Drive file `1PISSgK8dwFbUwPlJZQUrho1QgwnPWtO5`,
  **25,944 bytes**, SHA256
  `397e6a91e041575a897605274c6cc6d0711d462ef15bedfe7d9d383f370e37d2`,
  authentic 444 header width=800, height=14.
- `FM2001_Art/Generic/Waiting/loading_fill.444`:
  private Drive file `10Ks8RyM7B8HtcGUR8i5-6W58t1wxMey7`,
  **17,204 bytes**, SHA256
  `9ba312d886fbb1898ad1f63b5e3c985972c22da09b7915b13d06a374e8c32070`,
  authentic 444 header width=800, height=10.

Original `5F43D0→64D750` loads the backing asset into
`0x946610`. Original `5F4420` passes the **exact**
`0x946610` bitmap handle, original x=0, y=0, width=800,
height=14, two native option DWORDs and 0x100 to original
`64E500` owner **0x9465F0**; its native `64E58F/592`
stores these width/height fields at object+14/+18. In
`PResults::4A6E50`, the source `4A6F31/36` retrieves
**0x9465F0+18 = 14** and **+14=800** for PResults child3
`+0x220` at (0,579), giving **initial 800×14**.

Similarly `5F4460→64D750` loads `loading_fill.444` into
`0x9465D0`; original `4A6F58–4A6F76` passes native
width=0, height=10, x=0,y=0 into `64E500` for the embedded
**PResults+0x250** bar. Its `+14/+18` become **0/10**;
child4 `+0x270` copies them at `4A6F90–4A6FA9`
and begins at (0,581) with initial **0×10** rectangle.
Original event tick `4A71F0` calls `4A7190`, which
computes quantized width **10 × floor(80 × processed / total)**
within the nonnegative, non-overflow source domain (total0
=> width0) and changes `PResults+0x264` then the
control's right edge `PResults+0x280`, followed by
`64F600` child4 refresh. This **does not** mean a clock
or fixture-result count may generate the progress ticks.

The new original-source `source_original_presults_bar_rects_from_dated_callbacks`
accepts ONLY typed, ordered native `6168C0` two-pass
event-progress callback receipts and caller-supplied authentic
`4A7210` eligible-event total and prior processed count.
It yields event-by-event rectangle geometry `(0,581,width,10)`.
It refuses arbitrary/fake tick records, missing or invalid
native virtual+10 callbacks, unqualified signed count
overrun, and cannot claim native execution or GUI rendering.
Source loader identity checker independently validates the
three original assets and rejects changed/malformed data,
without checking those private bytes into Git.

**New local test evidence:** six focused tests PASS against the
hash-verified original private executable and ALL THREE original
bitmap files, including negative asset corruption, dynamic
progress callbacks and initial rects. Event receipt tests use
the same pure dataclass schema as the repository's
`original_presults_native_event_work`; actual complete suite
and CI have not yet been run on this WIP branch.

**Remaining normal player barrier:** this constructs an exact
source-defined three-sprite bottom PResults visual component,
not an 800x600 finished original screen. Original PResults
actual tick producer, original child1/child2 dynamic captions
and source mouse/keyboard lifecycle must be connected to the
real retained pending match, with native 0–3 mode execution,
GameState SaveLoad and PBg 0x432505+ return. No fake click to
return or fabricated progress timing. Gate13 stays reopened;
no physical Win11 proof. Do not PR/CI until coherent player
feature or otherwise independently useful safely reviewed
integration milestone.


## Recovery645: original PResults bottom graphics entered the ordinary Tk NEXT worker

**This entry supersedes the earlier "not a renderer" state above.** A
meaningful **partial real player-visible integration** has now been
implemented on the new main-based branch:
`worker/gate13-r1-original-normal-player-644`.

Three byte-identical source assets were imported under
`original_assets/source/FM2001_Art/Generic/waiting/`,
not into `reconstruction/` and not as a duplicate archive.
`original_assets/MANIFEST.md` records full original Drive
provenance, original SHA256, size, unchanged binary form, runtime
native purpose, and Git blob identity. Imported art:

- `waiting_back_2.444`, original source byte count 46448,
  SHA `289b6929...`, initial original PResults x0 y513
  800x87, **static initial control ID0, never a return control**.
- `loading_back.444`, 25944,
  SHA `397e6a91...`, PResults x0 y579 800x14.
- `loading_fill.444`, 17204,
  SHA `9ba312d8...`, actual decoded 800x10 sprite initially
  x0 y581 width0; clipped left-to-right only from original
  6168C0→4A71F0 qualified event ticks/4A7210 independent total.

`original_presults_bottom_surface.py` now validates all
three actual original .444 bytes and headers **before**
decoding with the repository's existing original
TQIA/quantization EA444 pipeline. It yields exact
source XY, pixel-aligned RGBA imagery for children
`+0x16C/+0x220`, and optional clipped original
`+0x270` bitmap **only** when the caller supplies the
typed actual source `OriginalPResultsDatedEventReceipt`
with independent original eligible-work denominator.
There is no invented animation, progress time, score, upper
screen, input semantics, or return button.

`original_game_host.py` now injects a lazy
`presults_resource_loader` from the ordinary
`run_original_game_ui` entry. It decodes original bitmaps
**off the Tk thread** inside the transactional NEXT or
Quick3 match worker, publishes only a typed
`presults_art` queue receipt, and paints the verified
partial source PResults bottom while the original
results owner holds management input. The upper
0–512 pixel rows are intentionally empty/black
rather than made-up PResults typography. Original
gameplay transaction is only published **after** the
worker returns an `ok` or `match_ok` receipt.
A source art failure aborts the transaction and leaves
prior saved state alone. Each NEXT resets previous
dated-event progress so no stale progress bar is shown.

A new host method
`apply_source_original_presults_dated_callbacks`
accepts the actual typed dated-event callback receipt
**only during an active results owner** and validates the
source quantized bar layout before changing any
Tk pixels or stored graphical receipt. No synthetic
worker sends events yet, because the actual original
dated-event producer is not source-integrated into
modern `GameState`. Consequently normal NEXT/Quick3
shows only original static source bottom imagery and
cannot falsely display "100%" based on match count.

New test modules:
`test_original_presults_bottom_surface.py`
and `test_original_presults_host_surface.py`,
plus original child resource tests, covering import
hashes, three source placements, exact RGBA source
cropping, two-pass validated events, typed fail-closed
triggers, stale progress reset, source resource error
atomicity and real ordinary NEXT worker receipt order.
All are registered in the focused Gate13 source
workflow. **No green exact-head CI or independent
native Windows11 player playtest exists yet at
authoring of this entry**; complete applicable PR
checks and review are required before merge.

**Whole-feature audit:** This is a **PARTIAL** implementation
and not completed PResults, Gate13 or original normal
player journey. Upper PResults children 1/2 contents,
native event count/producer, source 432505+ post-results
manager branch and conditional Start/Menu/Squad,
original score calculation `513252→5DA2F0→v38/v3c`,
mode 0/1 3D and mode 2 FastView wrapper,
true saved GameState, multiple humans and shipped
competitions/leagues, and actual Windows11 GUI
verification are still OPEN. Do not fake these missing
behaviors or mark any gate passed.

**Next highest impact after exact-head tests:** integrate
the actual source `4A7210` eligible event work and
`6168C0` ordered user match+event callback stream
into `HumanGameplayController` / live event-driven
`PResults` UI rather than a dummy timer; recover
and paint remaining original PResults children and
source-return trigger. Continue original mode-specific
full player match and source saved state.
