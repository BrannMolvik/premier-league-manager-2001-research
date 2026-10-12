# Ordinary NEXT pre-match installed-resource root correction

12 October 2026 KST. Based on main `95430476b4e0bcf62c5954ca801b49cb84153058`.

## Confirmed Windows observation

Daniel's manually operated frozen diagnostic completed New Game / England /
Conference / Southport / Start and reached management. At NEXT, the real
`original_game_host.load_prematch_resources` called the existing pre-match
boundary builder with the bundled `original_assets/source` subset. It failed in
`gate14_fastview_surfaced_resource_loader._read_first_existing`:
`FastViewSurfacedResourceLoadError: all source-backed home_badge attempts are absent`.

The process later closed because its explicitly approved external 120-second
watchdog terminated it, not because that exception terminated the process.
The retained receipt has `timed_out=true`, process exit1 and shutdown at120.453s;
both target processes were terminated. No second automated visible run occurred.
The previously reported Play/Start OSError(22) naming the release EXE remains
unreproduced; this is a different, demonstrated NEXT blocker.

## Source evidence and smallest correction

The existing loader requires an original-game resource root, not a distributable
subset. See [original candidate ownership](GATE14_FASTVIEW_SURFACED_PICTURES.md),
[verified loading](GATE14_FASTVIEW_SURFACED_RESOURCE_LOADING.md) and
[pre-match asset identities](GATE14_PREMATCH_PANEL.md).
Its native selector `0x40C850` uses club `badge_2`, then the original generic
badge. This fallback already exists; no new substitute or candidate is added.

Read-only checks on the authorized installation found the exact generic asset
at `FM2001_Art/Generic/Team_badge_stills/generic.444`: 17,508 bytes, SHA256
`956299bae57456a4cf106f388815c5b71fbcf2b5f60fc151081f3601c74a147c`.
The installation executable independently rehashed to canonical
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Neither file was modified or executed.

Change only the host's existing pre-match-loader argument to `Path(game_dir)`.
Bundled management chrome remains unchanged. Reuse all existing hash/geometry/
canonical-table checks and candidate order; missing assets still fail closed.
No Gate14 producer, simulator, RNG, save, resource bytes or worker state changes.

## Verification and bounds

- 166 focused tests pass, zero skips, Python3.12.14, 26.750s. Includes three new
  host-factory regression tests: installed root, missing-resource rejection and
  unresolved-participant rejection; plus existing frontend/host/package/raster,
  surfaced loader, pre-match and fixture-source/presenter tests.
- Non-interactive ordinary host test with the real original data and existing
  fake Tk widgets: eight actual host NEXT clicks/polls reach the first
  Southport/Telford fixture. The bundled-root negative control fails with the
  same badge exception. The live state object and18August date are unchanged,
  no pending match is published, and the failed turn is retryable. Repeating
  the same host click with the corrected actual factory publishes19August,
  the pending fixture and complete pre-match boundary with both original
  generic badges. This distinguishes blocked pre-match from a consumed fixture.
- The same headless host then accepts the real Quick Match selector, completes
  the pending fixture (observed score0:0), clears the modal/pending owners and
  returns to management. No game files or existing saves were written. Other
  match modes and repeated later fixtures have not been checked by this probe.
- This is data/host integration verification, NOT visible acceptance of the
  corrected package, match-mode selection, calculation or post-match return.
  No corrected frozen release was built or launched during this correction.
- Full-suite and exact-head CI are not yet run. The standalone asset checker
  cannot run in the private source snapshot because it lacks `.git`; no assets
  are added or changed by this patch.

## Separate empty Fixtures finding — not repaired here

The same canonical-data probe found Conference competition7 with462 league
fixtures, including42 Southport matches; its first matrix page has252 dated
cell projections. In that reconstructed runtime, NEXT proceeds in seven-day
steps from4July and reaches18August, then the19August pending fixture. These
are reconstruction observations, not independent proof of the native schedule.

However `OriginalGameTkHost._draw_league_fixtures_grid_art` paints only36 grid
bitmaps. `original_league_fixtures_art.py` explicitly excludes fixture boxes,
date/score text and club captions; the GUI does not draw the populated cell
projection. Daniel's report of an empty Fixtures screen therefore identifies
a real missing presentation path, not evidence that fixtures were deleted.

Next source-backed work: qualify and connect actual cell/club text/control
owners, source fonts/colors, clipping and original placement. Do not rewrite
the schedule or invent a modern fixture list. Gate13 stays OPEN.

## Separate direct Inbox and drag findings — not repaired here

All four SHA-verified back_3 strips are only backgrounds: the current host's
single image cannot display an Inbox emblem. Canonical original source
0x431740 constructs three draw children (background+0x38, number+0x3C,
icon+0x40), registers them via0x5D4580 at0x431813..0x431835, and0x431850
sets up all three, not just back_3. The missing icon binds descriptor0x9438D0
at0x431979..0x431982. Loader0x5FAA80 reads original literal0x837BAC,
`fm2001_art\\generic\\GenericButtonsAndBars\\eamail_anim.444`;
0x5FAAD0 binds18x18 source cells. Original0x4316A0 selects animation groups
0/10/20 from its own flags, and0x4316E0 updates its retained frame after
four native update passes. This is bounded static source proof on the same
canonical executable, not a native runtime/visible acceptance receipt.
Full live flag/counter ownership and update wiring are not integrated here.
Do not mistake the existing blank background's draw test for a visible button.

The current host retains name-drag identity and dispatches a bounded native
drop, but has no dragged-player cursor and explicitly declines shirt-number
dragging. A correct lower-level drop test does not prove the user's gesture,
empty-row hit mapping, or visible original behavior. Existing native cursor
and pointer evidence must be used before changing selection/order semantics;
do not replace native role/selection/resort behavior with a generic swap.
