# Windows playtest feedback — 12 October 2026

Baseline: PR650 `d4f96dc18c0dfac4a4e190fc72c538ced8111588`, based on main
`8d81c44d27463ee52a287e98d2db60b919c64877`. Gate13 is not accepted by this note.
SupportStart/staff, the separate performance branch, simulation/RNG, saves,
original files, Windows security and agent-runtime are unchanged.

## Demonstrated package defect and correction

The downloaded frozen build opened PStartMenu, but New Game raised
FileNotFoundError in gate13_ea444_staged_rasters._load_bundle. The path was
`FMTest-d4f96dc1/original_assets/converted/gate13-rasters-v1/manifest.json`;
the verified artifact actually contains it under `_internal/original_assets`.
Resolving a frozen module's grandparent incorrectly escaped the runtime root.
This failure is distinct from Smart App Control denying an unsigned executable.

Use the existing runtime_layout.bundled_original_assets_root, which already
handles source, PyInstaller _MEIPASS and legacy frozen layouts. No conversion,
pixels, original-source checks, manifest pins or fallback semantics change.
Extend package_smoke_report to assert that the actual management-raster decoder
uses that root, then verify its pinned manifest, compressed payload and decoded
images. The old smoke only constructed PStartMenu and missed the New Game path.

The regression executes the actual decoder module with simulated onedir,
onefile and legacy layouts and decodes through its default bundle argument.
All three fail before the fix and pass afterward. Additional smoke tests reject
the wrong runtime root and a missing payload, without weakening verification.

## Reported gameplay defects remain open

- **Invisible drag cursor:** the host retains a drag/drop transaction but has
  no integrated source-qualified name-cursor transport. The bounded original
  content/packing contract in GATE13_SQUAD_NAME_CURSOR.md does not establish a
  live pixel-format receipt or a faithful output adapter. Do not add a guessed
  RGBA cursor or claim that the gesture is visibly accepted.
- **Players moving upward / lower-right targets:** native sorting and ownership
  are not free placement in a spreadsheet. A fresh real-data Southport fixture
  contains all30 players. An independent bounded execution of4B7500/4B6FE0
  matches the port's40 slot results, with declared fixture predicate leaves.
  Right rows14..16 have null-player owners; rows17..19 share the actual empty
  owner. This is not native full-pointer/cursor execution or adjudication of
  Daniel's exact gesture. Keep the visible drop complaint open; do not guess
  new hit rectangles or change original membership sorting to satisfy a grid.
- **Form tabs:** source hover animation exists, but actual first/reserve
  formation activation/rendering is unfinished. The current host does not
  connect these clicks to complete source-backed pitch/role/shape producers.
  Enabling a button to an empty panel would not fix the reported functionality.
- **Inbox:** the real fresh Southport session has zero delivered messages.
  Current integration provides the list, selection/scrolling and Received
  header, not all filter columns, message preview or actions. The source-playtest
  log contains no thrown Inbox exception; that does not prove its visible
  screen is correct. Keep the broken-screen report open. PR638/shared CRT
  ownership remains blocked; no fabricated mail or guessed RNG state is added.
- **Menu:** popup art/navigation acceptance is separate from panel integration.
  Only Squad, Inbox, League Fixtures and League Tables have integrated panel
  snapshots. Other recovered menu entries fail closed instead of implementing
  their screens; their apparent inactivity is a genuine playability limitation.
- **Sound:** the diagnostic launch explicitly skipped intro media. First-screen
  press audio excludes management events. The local canonical menus.bnk passes
  its159324-byte/SHA256 identity check, but that is not audible-device evidence.
  Neither the device/mixer nor live playback was tested in the background.

Canonical executable reverified for data-only source checks:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Private original/emulation receipts and player data are not committed.

## Validation and next acceptance

The user subsequently requested no popups or interruption. Since that request,
all work used an isolated source/assets copy: no game/Tk window, audio, native
original process, security prompt or user-save write. New source tests are not
a claim that the rebuilt frozen executable or full gameplay works.

Focused regression:161 tests PASS,3 expected skips. Runtime-root/raster group:
11 tests PASS. Broader non-interactive regression and asset-policy results are
recorded in the PR. The two stock-WPF tests that spawn PowerShell without a
hidden-window flag are deferred, as is opt-in real media/Tk playback.

After reviewing the code, rebuild the package and re-run its frozen smoke.
Only when hands-on testing is authorized: launch the exact rebuilt artifact,
enter Southport, confirm New Game no longer fails resource lookup, then capture
the reported drag/drop, form-tab, Inbox and inactive-menu cases separately.
Do not describe this packaging correction as full playability acceptance.
