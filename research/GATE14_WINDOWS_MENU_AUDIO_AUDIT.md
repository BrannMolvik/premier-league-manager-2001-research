# Gate 14 real-Windows numeric menu-audio audible audit

_Status: audit harness added; real private Windows receipt still required._

## Purpose

The repository now has a complete source-backed numeric menu-audio transport:

`canonical menus.bnk -> AudioHooks numeric event/state -> literal slot -> BNKl v2 decode -> verified PCM -> synchronous playback seam -> Windows in-memory WAV adapter`.

Hosted tests can verify every byte-level and adapter contract above, but they
cannot prove that a real Windows 11 audio device produced audible output.

`reconstruction/gate14_windows_menu_audio_audit.py` closes only that final
device/audibility evidence gap for an **explicit numeric route**. It does not
assign semantic event or sample names.

## What the real audit requires

The command:

- refuses non-Windows execution;
- reads a private `menus.bnk` and requires the exact canonical size/SHA-256;
- requires explicit numeric `--event-id` and `--state-value` values;
- rejects numeric routes that intentionally produce no `menus.bnk` sound;
- decodes the exact routed sample through the existing source-backed bridge;
- requires the exact `WindowsMemoryWaveMenuPcmBackend` adapter class, so an
  arbitrary injected test backend cannot produce passing evidence;
- sends it synchronously through that Windows memory-wave adapter;
- verifies the delivery summary still matches the decoded literal sample slot;
- **after playback**, prompts the human operator to type `YES` exactly if the
  sound was personally heard;
- refuses every other response;
- writes a new private JSON receipt outside Git and refuses to overwrite old
  evidence.

The explicit human confirmation happens after the platform call. A synthetic
backend or hosted Linux test may verify the contract, but cannot produce the
real audible receipt.

## Receipt schema 1

A passing private receipt records:

- Windows platform and Python version;
- canonical `menus.bnk` size and SHA-256;
- numeric event ID, numeric state value and routed sample slot;
- decoded sample rate, channel count, sample count and PCM SHA-256;
- exact playback-adapter class and memory flag;
- synchronous adapter delivery completion;
- explicit human audibility confirmation;
- `audible_windows_verified: true`.

It also explicitly keeps these false:

- `semantic_event_binding_recovered`;
- `sample_meaning_recovered`;
- `modern_ui_event_equivalence_recovered`;
- `login_menu_audio_integrated`;
- `gate14_complete`.

Therefore one audible numeric sample does not silently become proof that the
modern UI is correctly bound to the original event system.

## Private Windows example

Use a numeric route already proven to emit a real sample. Event ID 17 with
state value 0 is currently source-backed only as numeric route -> slot 6; it is
**not** given a human-readable meaning here.

```text
python reconstruction/gate14_windows_menu_audio_audit.py ^
  "<private-staging>\menus.bnk" ^
  --event-id 17 ^
  --state-value 0 ^
  --output-receipt "<private-folder-outside-Git>\gate14-menu-audio-audible.json"
```

The canonical bank identity required by the harness is:

- bytes: 159,324
- SHA-256:
  `e3bd385d89ab94f0a97834a0749898c99d10a29ee404c29ebdc708c0daa1fc1d`.

Do not commit the bank, decoded PCM, generated WAV image, or private receipt.

## Evidence boundary after a pass

A real passing receipt is sufficient to promote **one numeric route's**
`audible_windows_verified` evidence. It is still not sufficient to set
Gate-14 `login_menu_audio_integrated` true.

That later promotion still requires:

1. the canonical executable caller trace to source-close semantic event
   sender/calling-convention/argument data-flow;
2. source-backed binding from the reconstructed runtime/UI to the corresponding
   original numeric sender behavior;
3. a real Windows run through that bound application path rather than the
   explicit audit CLI alone.

The private source caller trace remains blocked whenever local container/Python
execution returns `caas.internal.errors.ClientError`. Do not infer event names
from the sound while that blocker exists.


## Strict private-receipt validation and deterministic replay

`reconstruction/gate14_windows_menu_audio_receipt.py` validates an existing
private schema-1 audible receipt against the exact canonical `menus.bnk`
bytes. It is intentionally stricter than merely parsing JSON:

- the top-level and nested schema keys must match exactly;
- the receipt must preserve all bounded true/false evidence fields from the
  original real-Windows audit;
- the bank filename, size and SHA-256 must match the canonical bank supplied
  to the validator;
- the numeric event/state/slot tuple is freshly replayed through the
  source-backed AudioHooks menu dispatcher and BNKl decoder;
- sample rate, channels, sample count and PCM SHA-256 must equal that fresh
  replay exactly;
- the recorded adapter must be `WindowsMemoryWaveMenuPcmBackend` with the
  Windows `SND_MEMORY` flag;
- any attempt to add semantic event/sample meaning, modern UI equivalence,
  login/menu integration or Gate-14 completion fails closed.

The validator does **not** replay a human hearing event. A successful
validation carries forward the previously recorded human audibility evidence
while setting `new_device_audibility_replayed: false`. To obtain new device
audibility evidence, rerun the real Windows audit itself.

Example:

```text
python reconstruction/gate14_windows_menu_audio_receipt.py ^
  "<private-staging>\menus.bnk" ^
  --receipt "<private-folder-outside-Git>\gate14-menu-audio-audible.json" ^
  --output-validation "<private-folder-outside-Git>\gate14-menu-audio-validation.json"
```

Both the original audible receipt and the validation receipt remain private
outside Git.
