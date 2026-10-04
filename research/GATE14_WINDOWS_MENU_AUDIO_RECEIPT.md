# Gate 14 Windows menu-audio receipt replay validation

_Status: dependent cloud-safe checkpoint; requires the real-Windows audit harness._

## Purpose

A private Windows receipt must not become trusted Gate-14 state merely because
its JSON says `audible_windows_verified: true`.

`reconstruction/gate14_windows_menu_audio_receipt.py` therefore requires both:

1. a schema-1 receipt produced by the real-Windows numeric menu-audio audit; and
2. the exact canonical private `menus.bnk` bytes.

The validator then independently replays every source-derived part of the
receipt before exposing its human audibility evidence.

## Replay checks

Validation requires:

- schema version 1 and every expected pass/evidence boolean with exact bool type;
- `platform_system == "Windows"` plus non-empty platform/Python metadata;
- exact canonical `menus.bnk` size and SHA-256 from the supplied bank bytes;
- matching receipt `source_bank` filename/size/hash;
- integer numeric event/state values and a real sample slot;
- deterministic replay of the original numeric AudioHooks dispatcher;
- exact routed sample-slot equality;
- deterministic BNKl sample decode against the supplied canonical bank;
- exact sample rate, channel count, sample count and decoded PCM SHA-256 equality;
- exact `WindowsMemoryWaveMenuPcmBackend` class and a nonnegative memory flag.

If the replay resolves to an original no-sound route, or any receipt-derived
slot/PCM field differs, validation fails.

The private receipt's human confirmation cannot be cryptographically recreated,
so the validator requires the original receipt fields to remain exact and
binds them to the independently replayed source path. It does not treat a
manually constructed JSON object as equivalent to a genuine Windows run.

## Readiness boundary

`Gate14ReadinessEvidence` now includes a separate
`audible_windows_verified` capability.

`login_menu_audio_integrated` is forbidden unless all of these are already
true:

- audio bank ownership;
- recovered playback entrypoints;
- sample decode readiness;
- semantic audio event binding;
- audible Windows verification.

The official original-audio criterion therefore cannot pass without real
audible Windows evidence.

`gate14_audio_readiness_bridge.py` accepts only an exact
`VerifiedWindowsMenuAudioReceipt` and advances **only**
`audible_windows_verified=True`.

It deliberately preserves:

- `audio_event_binding_recovered`;
- `login_menu_audio_integrated`;
- all FastView/match-presentation capabilities;
- Gate-14 completion state.

One audible numeric sample therefore cannot complete the audio criterion or
Gate 14 by itself.

## Remaining dependency

A real receipt still requires running the Windows audit privately with the
canonical bank and human confirmation. Separately, semantic event binding still
depends on the canonical executable caller trace and cannot be inferred from
the sound.

No private receipt, BNK bytes, decoded PCM, or generated WAV data belongs in
Git.
