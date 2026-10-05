# Gate 14 real-Windows startup-media acceptance audit

_Status: audit harness added; private Windows 11 client receipt still required._

## Purpose

PR #454 established the normal Windows runtime path for the exact original
startup movies:

1. validate `FMV/easp.tgq` and `FMV/premintro.tgq` against their canonical
   source identities;
2. create or revalidate the private per-user H.264/AAC derivative cache;
3. preserve the source-proven two-item order;
4. play each verified derivative synchronously through the built-in Windows MCI
   backend.

Hosted Windows package CI proves that this code can be packaged and constructed.
It cannot prove that an actual Windows 11 client workstation visibly displayed
the movies or produced audible output.

`reconstruction/gate14_windows_startup_media_audit.py` supplies that missing
acceptance boundary without promoting unresolved original behavior.

## Strict platform boundary

The audit refuses:

- non-Windows platforms;
- GitHub Actions;
- Windows Server/product types other than client workstation;
- Windows builds below 22000.

This prevents a hosted Windows Server runner from being misrepresented as the
required external Windows 11 client evidence.

## Runtime path reused

The audit calls the same runtime components as normal launch:

- `prepare_runtime_startup_media()`;
- `WindowsMciStartupMediaBackend`;
- `play_verified_startup_sequence()`.

The preparer therefore performs the exact TGQ identity checks and derivative
cache verification already required by the normal runtime. The playback seam
again enforces the canonical two-item source order and synchronous completion.

An arbitrary injected player cannot produce a passing audit. The backend must be
the exact `WindowsMciStartupMediaBackend` class.

## Human acceptance

Only after both playback calls have completed does the audit ask the operator to
type exactly:

`YES-BOTH`

That token means all three of these observations were personally made:

- both startup videos were visibly displayed;
- both contained audible audio;
- they appeared in source order: `easp.tgq`, then `premintro.tgq`.

Any other response fails closed and produces no success receipt.

## Private receipt

A passing schema-1 receipt records:

- Windows 11 client build/product-type evidence;
- exact source path/hash/size and source media geometry for both TGQs;
- converted derivative filename/hash/size and codec profile;
- playback completion for both items;
- exact backend class;
- explicit human visibility and audibility confirmation;
- `startup_media_real_windows_verified = true`.

The receipt must be written outside Git and cannot overwrite earlier evidence.

## Deliberate limits

A passing receipt still sets these false:

- `normal_application_launch_invoked`;
- `skip_input_recovered`;
- `transition_timing_recovered`;
- `exact_display_treatment_recovered`;
- `gate14_complete`.

This distinction is important. The audit replays the exact runtime components
used by the normal application, but it does not itself launch the complete
application wrapper. Repository tests already prove that the ordinary Windows
path selects those components. A later acceptance run of the packaged
application may add stronger end-to-end launch evidence.

The original bit-0 playback flag remains neutral metadata and is not renamed to
a skip semantic.

## Example

On the actual Windows 11 client workstation, with the canonical installed game
folder and the packaged application root:

```text
python reconstruction/gate14_windows_startup_media_audit.py ^
  --game-dir "C:\Games\FM2001" ^
  --application-root "C:\Path\To\FM2001-Windows11" ^
  --output-receipt "C:\private\gate14-startup-media-windows.json"
```

Do not commit the receipt, converted movies, original TGQs, or runtime cache.
